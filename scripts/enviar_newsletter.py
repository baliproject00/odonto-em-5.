"""Envia a newsletter da edição pela Brevo (campanha de e-mail para a lista de inscritos).

Segredos necessários: BREVO_API_KEY, BREVO_LISTA_ID, BREVO_REMETENTE_EMAIL.
Opcional: BREVO_REMETENTE_NOME (padrão "odonto em 5") e BREVO_EMAIL_TESTE
(se definido, a campanha é enviada só para esse endereço, como teste).
"""
import json
import os
from datetime import datetime, timezone

from comum import env, http, ler_edicao, log, modo_teste, pasta_da_edicao, url_publica

API = "https://api.brevo.com/v3"


def main():
    pasta, data = pasta_da_edicao()
    if not pasta:
        log(f"Nenhuma edição aprovada para {data}. Nada a enviar.")
        return
    if (pasta / "enviado_email.json").exists():
        log("Esta edição já foi enviada por e-mail. Nada a fazer.")
        return
    edicao = ler_edicao(pasta)
    html = (pasta / edicao["email"]["arquivo"]).read_text(encoding="utf-8")
    html = html.replace("{{BASE}}", url_publica(f"edicoes/{data}"))

    if modo_teste():
        log(f"MODO TESTE: nada será enviado. Assunto: {edicao['email']['assunto']}")
        log(f"HTML com {len(html)} caracteres; imagens em {url_publica(f'edicoes/{data}/imagens')}")
        return

    teste_lista = os.environ.get("TESTE_LISTA", "não").lower() == "sim"
    cab = {"api-key": env("BREVO_API_KEY"), "accept": "application/json"}
    campanha = http("POST", f"{API}/emailCampaigns", cabecalhos=cab, json_body={
        "name": f"odonto em 5 · {data}" + (" · teste" if teste_lista else ""),
        "subject": ("[Teste] " if teste_lista else "") + edicao["email"]["assunto"],
        "sender": {"name": os.environ.get("BREVO_REMETENTE_NOME") or "odonto em 5", "email": env("BREVO_REMETENTE_EMAIL")},
        "htmlContent": html,
        "recipients": {"listIds": [int(env("BREVO_LISTA_ID"))]},
    })
    cid = campanha["id"]
    teste = os.environ.get("BREVO_EMAIL_TESTE")
    if teste:
        http("POST", f"{API}/emailCampaigns/{cid}/sendTest", cabecalhos=cab, json_body={"emailTo": [e.strip() for e in teste.split(",") if e.strip()]})
        log(f"Envio de teste feito para {teste}. A campanha {cid} ficou como rascunho na Brevo.")
        return
    http("POST", f"{API}/emailCampaigns/{cid}/sendNow", cabecalhos=cab)
    if teste_lista:
        log(f"Teste para a lista inteira enviado (campanha {cid}). A edição NÃO foi marcada como enviada.")
        return
    enviado_em = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (pasta / "enviado_email.json").write_text(json.dumps({"campanha_id": cid, "enviado_em": enviado_em}, indent=2), encoding="utf-8")
    log(f"Newsletter enviada. Campanha Brevo {cid}.")


if __name__ == "__main__":
    main()
