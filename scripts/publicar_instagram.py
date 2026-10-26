"""Publica o carrossel da edição no Instagram, com legenda, e posta o comentário-enquete.

Usa a API do Instagram com login do Instagram (graph.instagram.com).
Segredos necessários: IG_USER_ID e IG_ACCESS_TOKEN.
"""
import json
import time

from comum import aprovada, env, falhar, http, ler_edicao, log, modo_teste, pasta_da_edicao, url_publica

VERSAO = env("IG_API_VERSAO", obrigatorio=False, padrao="v23.0")
BASE = f"https://graph.instagram.com/{VERSAO}"
LIMITE_LEGENDA = 2200
LIMITE_HASHTAGS = 30


def validar(ig):
    slides = ig["slides"]
    if not 1 <= len(slides) <= 20:
        falhar(f"O post precisa ter de 1 a 20 imagens; a edição tem {len(slides)}.")
    if any(not s.lower().endswith((".jpg", ".jpeg")) for s in slides):
        falhar("O Instagram só aceita JPEG nas imagens do carrossel.")
    legenda = ig["legenda"]
    if len(legenda) > LIMITE_LEGENDA:
        falhar(f"Legenda com {len(legenda)} caracteres; o limite é {LIMITE_LEGENDA}.")
    if legenda.count("#") > LIMITE_HASHTAGS:
        falhar(f"Legenda com mais de {LIMITE_HASHTAGS} hashtags.")


def esperar_pronto(container_id, token):
    for _ in range(30):
        r = http("GET", f"{BASE}/{container_id}?fields=status_code,status&access_token={token}")
        status = r.get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            falhar(f"O Instagram recusou a mídia {container_id}: {r.get('status')}")
        time.sleep(5)
    falhar(f"A mídia {container_id} não ficou pronta a tempo.")


def publicar_quando_pronto(usuario, container, token, tentativas=8):
    """O Instagram às vezes diz 'mídia não está pronta' mesmo com status FINISHED: espera e tenta de novo."""
    import urllib.error, urllib.parse, urllib.request
    dados = urllib.parse.urlencode({"creation_id": container, "access_token": token}).encode()
    for t in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{BASE}/{usuario}/media_publish", data=dados, method="POST"), timeout=60) as r:
                return json.loads(r.read().decode())["id"]
        except urllib.error.HTTPError as e:
            corpo = e.read().decode(errors="replace")
            if "not ready" in corpo or "9007" in corpo:
                log(f"Mídia ainda não pronta (tentativa {t}); esperando 15 s...")
                time.sleep(15)
                continue
            falhar(f"media_publish respondeu {e.code}: {corpo[:500]}")
    falhar("O Instagram não liberou a mídia para publicação a tempo.")


def main():
    pasta, data = pasta_da_edicao()
    if not pasta:
        log(f"Nenhuma edição aprovada para {data}. Nada a publicar.")
        return
    if (pasta / "publicado_instagram.json").exists():
        log("Esta edição já foi publicada no Instagram. Nada a fazer.")
        return
    ig = ler_edicao(pasta)["instagram"]
    validar(ig)
    urls = [url_publica(f"edicoes/{data}/{s}") for s in ig["slides"]]

    if modo_teste():
        log("MODO TESTE: nada será publicado. Isto é o que seria enviado:")
        for u in urls:
            log(f"  imagem: {u}")
        log(f"  legenda ({len(ig['legenda'])} caracteres):\n{ig['legenda']}")
        log(f"  comentário-enquete:\n{ig['comentario_enquete']}")
        return

    if not aprovada(ler_edicao(pasta)):
        log("Edição ainda NÃO aprovada pelo editor-chefe. Nada foi publicado no Instagram.")
        return
    usuario = env("IG_USER_ID")
    token = env("IG_ACCESS_TOKEN")

    if len(urls) == 1:
        r = http("POST", f"{BASE}/{usuario}/media", dados={"image_url": urls[0], "caption": ig["legenda"], "access_token": token})
        carrossel = r["id"]
        esperar_pronto(carrossel, token)
        urls = []
    filhos = []
    for u in urls:
        r = http("POST", f"{BASE}/{usuario}/media", dados={"image_url": u, "is_carousel_item": "true", "access_token": token})
        filhos.append(r["id"])
        log(f"Imagem enviada: {u.rsplit('/', 1)[-1]}")
    for f in filhos:
        esperar_pronto(f, token)

    if filhos:
        r = http("POST", f"{BASE}/{usuario}/media", dados={
            "media_type": "CAROUSEL", "children": ",".join(filhos), "caption": ig["legenda"], "access_token": token})
        carrossel = r["id"]
        esperar_pronto(carrossel, token)

    post = publicar_quando_pronto(usuario, carrossel, token)
    log(f"Carrossel publicado. ID do post: {post}")

    comentario = http("POST", f"{BASE}/{post}/comments", dados={"message": ig["comentario_enquete"], "access_token": token})
    log("Comentário-enquete publicado.")

    link = http("GET", f"{BASE}/{post}?fields=permalink&access_token={token}").get("permalink")
    (pasta / "publicado_instagram.json").write_text(json.dumps(
        {"post_id": post, "comentario_id": comentario.get("id"), "link": link}, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"Pronto: {link}")


if __name__ == "__main__":
    main()
