"""Publica posts avulsos (uma imagem + legenda) no Instagram.

Por padrão, publica os posts de posts/ cuja data "publicar_em" é hoje (horário de Brasília),
que estão com "revisado": true e ainda não foram publicados.
Com a variável POST_ID (ex.: 2026-10-27-chatgpt-fratura), publica só esse post, na hora:
é o caminho para notícia urgente.
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
        if not alvo and post.get("publicar_em") != hoje:
            continue
        if not post.get("revisado"):
            log(f"{pasta.name} ainda não foi revisado; não será publicado.")
            continue
        yield pasta, post


def validar(pasta, post):
    if not (pasta / "post.jpg").exists():
        falhar(f"{pasta.name}: falta a imagem post.jpg.")
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
        imagem = url_publica(f"posts/{pasta.name}/post.jpg")
        if modo_teste():
            log(f"MODO TESTE: publicaria {pasta.name}\n  imagem: {imagem}\n  legenda ({len(post['legenda'])} caracteres):\n{post['legenda']}")
            continue
        usuario, token = env("IG_USER_ID"), env("IG_ACCESS_TOKEN")
        midia = http("POST", f"{BASE}/{usuario}/media",
                     dados={"image_url": imagem, "caption": post["legenda"], "access_token": token})["id"]
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
