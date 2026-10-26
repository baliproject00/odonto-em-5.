"""Conta os votos da enquete da edição anterior (comentários com A, B, C ou D).

Lê os comentários do post e as respostas ao comentário-enquete, conta um voto por
pessoa e grava resultado_enquete.json na pasta da edição. O resultado entra na
próxima edição, junto com a resposta certa.
"""
import json
import re
from collections import Counter

from comum import RAIZ, env, http, log, modo_teste

VERSAO = env("IG_API_VERSAO", obrigatorio=False, padrao="v23.0")
BASE = f"https://graph.instagram.com/{VERSAO}"
VOTO = re.compile(r"^\s*(?:letra\s*)?([ABCD])\s*(?:[).!:,-].*)?$", re.I | re.S)


def todas(url, token):
    itens = []
    while url:
        r = http("GET", url if "access_token=" in url else f"{url}&access_token={token}")
        itens += r.get("data", [])
        url = r.get("paging", {}).get("next")
    return itens


def main():
    publicadas = sorted(RAIZ.glob("edicoes/*/publicado_instagram.json"))
    pendentes = [p for p in publicadas if not (p.parent / "resultado_enquete.json").exists()
                 and "post_id" in json.loads(p.read_text(encoding="utf-8"))
                 and "enquete" in json.loads((p.parent / "edicao.json").read_text(encoding="utf-8")).get("instagram", {})]
    if not pendentes:
        log("Nenhuma enquete pendente de contagem.")
        return
    alvo = pendentes[-1]
    pub = json.loads(alvo.read_text(encoding="utf-8"))
    edicao = json.loads((alvo.parent / "edicao.json").read_text(encoding="utf-8"))
    if modo_teste():
        log(f"MODO TESTE: contaria os votos do post {pub['post_id']} ({alvo.parent.name}).")
        return

    token = env("IG_ACCESS_TOKEN")
    campos = "fields=id,text,username"
    comentarios = todas(f"{BASE}/{pub['post_id']}/comments?{campos}&limit=50", token)
    if pub.get("comentario_id"):
        comentarios += todas(f"{BASE}/{pub['comentario_id']}/replies?{campos}&limit=50", token)

    votos = {}
    for c in comentarios:
        m = VOTO.match(c.get("text", ""))
        if m and c.get("username"):
            votos.setdefault(c["username"], m.group(1).upper())  # um voto por pessoa: o primeiro vale
    contagem = Counter(votos.values())
    total = sum(contagem.values())
    enquete = edicao["instagram"]["enquete"]
    resultado = {
        "total_votos": total,
        "votos": {op: contagem.get(op, 0) for op in enquete["opcoes"]},
        "percentual": {op: round(100 * contagem.get(op, 0) / total) if total else 0 for op in enquete["opcoes"]},
        "correta": enquete["correta"],
        "explicacao": enquete["explicacao"],
    }
    (alvo.parent / "resultado_enquete.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"Enquete de {alvo.parent.name}: {total} votos, {resultado['percentual']}")


if __name__ == "__main__":
    main()
