"""Publica posts avulsos no Instagram: uma imagem (post.jpg) ou um carrossel ("carrossel" no post.json).

Por padrão, publica os posts de posts/ cuja data "publicar_em" é hoje (horário de Brasília),
que estão com "revisado": true e ainda não foram publicados.
Posts com "publicar_agora": true ou "urgente": true (e revisados) são publicados assim que
entram na branch main, sem esperar o dia agendado. Com a variável POST_ID, publica só esse post, na hora.
Segredos necessários: IG_USER_ID e IG_ACCESS_TOKEN.
"""
import json
import os
from datetime import datetime

from comum import FUSO_BR, RAIZ, env, falhar, http, log, modo_teste, url_publica
from publicar_instagram import BASE, LIMITE_HASHTAGS, LIMITE_LEGENDA, esperar_pronto


def posts_a_publicar():
    alvo = os.environ.get("POST_ID", "").strip()
    hoje = datetime.now(FUSO_BR).strftime("%Y-%m-%d")
    pastas = [RAIZ / "posts" / alvo] if alvo else sorted((RAIZ / "posts").glob("*/"))
    for pasta in pastas:
        arquivo = pasta / "post.json"
        if not arquivo.exists():
            if alvo:
                falhar(f"Post {alvo} não encontrado em posts/.")
            continue
        post = json.loads(arquivo.read_text(encoding="utf-8"))
        if (pasta / "publicado.json").exists():
            if alvo:
                log(f"{pasta.name} já foi publicado. Nada a fazer.")
            continue
        agora = post.get("urgente") or post.get("publicar_agora")
        if not alvo and post.get("publicar_em") != hoje and not agora:
            continue
        if not post.get("revisado"):
            log(f"{pasta.name} ainda não foi revisado; não será publicado.")
            continue
        yield pasta, post


def imagens(pasta, post):
    return post.get("carrossel") or ["post.jpg"]


def validar(pasta, post):
    lista = imagens(pasta, post)
    if len(lista) > 20:
        falhar(f"{pasta.name}: o carrossel pode ter no máximo 20 imagens.")
    for nome in lista:
        if not (pasta / nome).exists():
            falhar(f"{pasta.name}: falta a imagem {nome}.")
        if not nome.lower().endswith((".jpg", ".jpeg")):
            falhar(f"{pasta.name}: {nome} precisa ser JPEG.")
    if len(post["legenda"]) > LIMITE_LEGENDA:
        falhar(f"{pasta.name}: legenda com {len(post['legenda'])} caracteres; o limite é {LIMITE_LEGENDA}.")
    if post["legenda"].count("#") > LIMITE_HASHTAGS:
        falhar(f"{pasta.name}: mais de {LIMITE_HASHTAGS} hashtags.")


def main():
    encontrados = list(posts_a_publicar())
    if not encontrados:
        log("Nenhum post avulso para publicar agora.")
        return
    for pasta, post in encontrados:
        validar(pasta, post)
        urls = [url_publica(f"posts/{pasta.name}/{n}") for n in imagens(pasta, post)]
        if modo_teste():
            log(f"MODO TESTE: publicaria {pasta.name}\n  imagens: {urls}\n  legenda ({len(post['legenda'])} caracteres):\n{post['legenda']}")
            continue
        usuario, token = env("IG_USER_ID"), env("IG_ACCESS_TOKEN")
        if len(urls) == 1:
            midia = http("POST", f"{BASE}/{usuario}/media",
                         dados={"image_url": urls[0], "caption": post["legenda"], "access_token": token})["id"]
        else:
            filhos = [http("POST", f"{BASE}/{usuario}/media",
                           dados={"image_url": u, "is_carousel_item": "true", "access_token": token})["id"] for u in urls]
            for f in filhos:
                esperar_pronto(f, token)
            midia = http("POST", f"{BASE}/{usuario}/media", dados={
                "media_type": "CAROUSEL", "children": ",".join(filhos), "caption": post["legenda"], "access_token": token})["id"]
        esperar_pronto(midia, token)
        publicado = http("POST", f"{BASE}/{usuario}/media_publish",
                         dados={"creation_id": midia, "access_token": token})["id"]
        registro = {"post_id": publicado}
        if post.get("comentario"):
            c = http("POST", f"{BASE}/{publicado}/comments", dados={"message": post["comentario"], "access_token": token})
            registro["comentario_id"] = c.get("id")
        registro["link"] = http("GET", f"{BASE}/{publicado}?fields=permalink&access_token={token}").get("permalink")
        (pasta / "publicado.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"Publicado {pasta.name}: {registro['link']}")


if __name__ == "__main__":
    main()
