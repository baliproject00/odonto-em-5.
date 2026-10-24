"""Renova o token de longa duração do Instagram (vale 60 dias) e grava o novo num arquivo temporário.

A rotina mensal usa esse arquivo para atualizar o segredo IG_ACCESS_TOKEN. O token
nunca é impresso no registro da execução.
"""
import os
import sys

from comum import env, http, log

token = env("IG_ACCESS_TOKEN")
r = http("GET", f"https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={token}")
novo = r.get("access_token")
if not novo:
    print("::error::A Meta não devolveu um token novo. Gere um token manualmente.")
    sys.exit(1)
print(f"::add-mask::{novo}")
destino = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "ig_token")
with open(destino, "w") as f:
    f.write(novo)
log(f"Token renovado; validade de {int(r.get('expires_in', 0)) // 86400} dias.")
