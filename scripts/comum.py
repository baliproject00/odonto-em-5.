"""Funções compartilhadas pelos scripts de publicação do odonto em 5."""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUSO_BR = timezone(timedelta(hours=-3))


def log(msg):
    print(f"[{datetime.now(FUSO_BR):%H:%M:%S}] {msg}", flush=True)


def falhar(msg):
    print(f"::error::{msg}", flush=True)
    sys.exit(1)


def env(nome, obrigatorio=True, padrao=None):
    valor = os.environ.get(nome, padrao)
    if obrigatorio and not valor:
        falhar(f"Variável {nome} não configurada nos segredos do repositório.")
    return valor


def modo_teste():
    """Em modo teste, nada é publicado nem enviado: só mostra o que seria feito."""
    return os.environ.get("MODO_TESTE", "sim").lower() in ("sim", "true", "1", "yes")


def pasta_da_edicao(data=None):
    data = data or os.environ.get("DATA_EDICAO") or datetime.now(FUSO_BR).strftime("%Y-%m-%d")
    pasta = RAIZ / "edicoes" / data
    if not (pasta / "edicao.json").exists():
        return None, data
    return pasta, data


def aprovada(edicao):
    """Edições novas nascem com "aprovado": false. Só o editor-chefe muda para true."""
    return edicao.get("aprovado", True) is True


def ler_edicao(pasta):
    return json.loads((pasta / "edicao.json").read_text(encoding="utf-8"))


def url_publica(caminho_relativo):
    """Endereço público de um arquivo do repositório (o Instagram e o e-mail buscam as imagens daqui)."""
    repo = env("GITHUB_REPOSITORY")
    ref = os.environ.get("GITHUB_SHA", "main")
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{caminho_relativo}"


def http(metodo, url, dados=None, cabecalhos=None, json_body=None, tentativas=3):
    cabecalhos = dict(cabecalhos or {})
    corpo = None
    if json_body is not None:
        corpo = json.dumps(json_body).encode()
        cabecalhos["Content-Type"] = "application/json"
    elif dados is not None:
        corpo = urllib.parse.urlencode(dados).encode()
    for tentativa in range(1, tentativas + 1):
        req = urllib.request.Request(url, data=corpo, headers=cabecalhos, method=metodo)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                texto = resp.read().decode()
                return json.loads(texto) if texto else {}
        except urllib.error.HTTPError as e:
            detalhe = e.read().decode(errors="replace")
            if e.code >= 500 and tentativa < tentativas:
                log(f"Erro {e.code}, tentando de novo em 10 s...")
                time.sleep(10)
                continue
            falhar(f"{metodo} {url.split('?')[0]} respondeu {e.code}: {detalhe[:500]}")
        except urllib.error.URLError as e:
            if tentativa < tentativas:
                time.sleep(10)
                continue
            falhar(f"Sem conexão com {url.split('?')[0]}: {e}")
