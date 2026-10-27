"""Envia a edição da semana para quem se inscreveu DEPOIS do envio de segunda.

Roda de hora em hora. Pega a edição normal mais recente já enviada (dos últimos 7 dias),
procura na lista da Brevo os contatos criados depois do envio e manda a edição para eles,
com um aviso no topo. Os IDs dos contatos atendidos (só os números da Brevo, sem e-mail)
ficam em atrasados.json, para ninguém receber duas vezes.

Segredos: BREVO_API_KEY, BREVO_LISTA_ID, BREVO_REMETENTE_EMAIL.
A chave da Brevo precisa poder criar listas e adicionar contatos (permissão de contatos completa).
"""
import json
import os
from datetime import datetime, timedelta, timezone

from comum import RAIZ, env, http, log, modo_teste, url_publica

API = "https://api.brevo.com/v3"
AVISO = ('<tr><td style="padding:20px 32px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
         'style="background:#FFFFFF;border:2px solid #F5785A;border-radius:12px;"><tr><td style="padding:14px 18px;font-size:14px;'
         'line-height:1.5;color:#1F2933;"><b style="color:#B0452A;">Você chegou depois do envio de segunda.</b> Para não ficar de fora, '
         'aqui está a edição desta semana. A próxima chega na segunda, por volta das 6h30.</td></tr></table></td></tr>')


def data_hora(texto):
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def edicao_da_semana():
    agora = datetime.now(timezone.utc)
    for pasta in sorted((RAIZ / "edicoes").glob("*/"), reverse=True):
        enviado, info = pasta / "enviado_email.json", pasta / "edicao.json"
        if not (enviado.exists() and info.exists()):
            continue
        edicao = json.loads(info.read_text(encoding="utf-8"))
        registro = json.loads(enviado.read_text(encoding="utf-8"))
        if edicao.get("especial") or "enviado_em" not in registro:
            continue
        quando = data_hora(registro["enviado_em"])
        if agora - quando > timedelta(days=7):
            return None
        return pasta, edicao, quando
    return None


def novos_contatos(cab, lista, desde):
    contatos, offset = [], 0
    while True:
        r = http("GET", f"{API}/contacts/lists/{lista}/contacts?limit=500&offset={offset}"
                        f"&modifiedSince={desde.strftime('%Y-%m-%dT%H:%M:%S.000Z')}", cabecalhos=cab)
        pagina = r.get("contacts", [])
        contatos += pagina
        if len(pagina) < 500:
            break
        offset += 500
    return [c for c in contatos if data_hora(c["createdAt"]) > desde and not c.get("emailBlacklisted")]


def main():
    achada = edicao_da_semana()
    if not achada:
        log("Nenhuma edição desta semana enviada ainda. Nada a fazer.")
        return
    pasta, edicao, enviado_em = achada
    data = pasta.name
    arquivo = pasta / "atrasados.json"
    atendidos = set(json.loads(arquivo.read_text(encoding="utf-8"))["ids"]) if arquivo.exists() else set()

    cab = {"api-key": env("BREVO_API_KEY"), "accept": "application/json"}
    lista = int(env("BREVO_LISTA_ID"))
    if not modo_teste():
        limpar_listas_antigas(cab)
    novos = [c for c in novos_contatos(cab, lista, enviado_em) if c["id"] not in atendidos]
    if not novos:
        log(f"Ninguém novo desde o envio de {data}.")
        return
    ids = [c["id"] for c in novos]
    log(f"{len(ids)} inscrito(s) novo(s) desde o envio de {data}.")
    if modo_teste():
        log("MODO TESTE: nada será enviado.")
        return

    html = (pasta / edicao["email"]["arquivo"]).read_text(encoding="utf-8").replace("{{BASE}}", url_publica(f"edicoes/{data}"))
    marca = "imagens/cabecalho.png"
    i = html.find(marca)
    fim = html.find("</td></tr>", i) + len("</td></tr>") if i >= 0 else -1
    html = html[:fim] + "\n" + AVISO + html[fim:] if fim > 0 else html

    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    temp = http("POST", f"{API}/contacts/lists", cabecalhos=cab,
                json_body={"name": f"Atrasados {data} ({agora} UTC)", "folderId": pasta_brevo(cab)})["id"]
    try:
        campanha = enviar_para_lista(cab, temp, ids, data, agora, edicao, html)
    except SystemExit:
        http("DELETE", f"{API}/contacts/lists/{temp}", cabecalhos=cab, tentativas=1)
        raise
    atendidos.update(ids)
    arquivo.write_text(json.dumps({"ids": sorted(atendidos)}, indent=2), encoding="utf-8")
    log(f"Edição de {data} enviada para {len(ids)} inscrito(s) novo(s). Campanha {campanha}.")


def enviar_para_lista(cab, temp, ids, data, agora, edicao, html):
    http("POST", f"{API}/contacts/lists/{temp}/contacts/add", cabecalhos=cab, json_body={"ids": ids})
    campanha = http("POST", f"{API}/emailCampaigns", cabecalhos=cab, json_body={
        "name": f"odonto em 5 · {data} · atrasados {agora}",
        "subject": edicao["email"]["assunto"],
        "sender": {"name": os.environ.get("BREVO_REMETENTE_NOME") or "odonto em 5", "email": env("BREVO_REMETENTE_EMAIL")},
        "htmlContent": html,
        "recipients": {"listIds": [temp]},
    })["id"]
    http("POST", f"{API}/emailCampaigns/{campanha}/sendNow", cabecalhos=cab)
    return campanha


def limpar_listas_antigas(cab):
    """Apaga as listas temporárias de atrasados com mais de 1 dia (as campanhas delas já foram enviadas)."""
    import re
    pasta = pasta_brevo(cab)
    r = http("GET", f"{API}/contacts/folders/{pasta}/lists?limit=50", cabecalhos=cab)
    limite = datetime.now(timezone.utc) - timedelta(days=1)
    for lista in r.get("lists", []):
        m = re.search(r"\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\)", lista["name"])
        if m and datetime.strptime(m.group(1), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc) < limite:
            http("DELETE", f"{API}/contacts/lists/{lista['id']}", cabecalhos=cab)
            log(f"Lista temporária antiga apagada: {lista['name']}")


def pasta_brevo(cab):
    """Usa (ou cria) a pasta 'odonto em 5 · atrasados' na Brevo para guardar as listas temporárias."""
    r = http("GET", f"{API}/contacts/folders?limit=50", cabecalhos=cab)
    for p in r.get("folders", []):
        if p["name"] == "odonto em 5 · atrasados":
            return p["id"]
    return http("POST", f"{API}/contacts/folders", cabecalhos=cab, json_body={"name": "odonto em 5 · atrasados"})["id"]


if __name__ == "__main__":
    main()
