"""Gera a imagem de um post avulso (1080x1350, JPEG) a partir do post.json.

Uso (no ambiente dos agentes, não no GitHub Actions):
    python ferramentas/gerar_post.py posts/2026-10-27-chatgpt-fratura

Campos usados do post.json:
    rotulo     texto pequeno em coral acima da manchete (ex.: "ESTUDO NOVO")
    manchete   título grande; o trecho em "destaque" fica em coral
    destaque   parte da manchete a destacar (opcional)
    imagem     arquivo da ilustração ou gráfico, relativo à pasta do post
    tema       "escuro" (padrão) ou "claro"
Precisa do Playwright com Chromium.
"""
import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
LOGO = RAIZ / "marca" / "logo_branco.png"

MODELO = """<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0}}
.p{{width:1080px;height:1350px;box-sizing:border-box;background:{fundo};display:flex;flex-direction:column;font-family:'Inter Display',Inter,Arial,sans-serif}}
.topo{{display:flex;align-items:center;gap:18px;padding:64px 72px 0}}
.topo span{{font-weight:800;font-size:44px;color:#F6F2E9;letter-spacing:-1px}}
.topo b{{color:#F5785A}}
.arte{{flex:1;display:flex;align-items:center;justify-content:center;padding:40px 72px}}
.arte img{{width:936px;border-radius:28px;display:block;outline:3px solid rgba(246,242,233,.18)}}
.base{{background:#1F2933;padding:56px 72px 72px;border-top:8px solid #F5785A}}
.rot{{font-size:34px;font-weight:800;color:#F5785A;letter-spacing:1px;margin-bottom:18px}}
.man{{font-size:{tam}px;font-weight:800;line-height:1.08;color:#F6F2E9;letter-spacing:-1.5px}}
.man em{{font-style:normal;color:#F5785A}}
</style></head><body><div class="p">
<div class="topo"><img src="file://{logo}" style="height:64px"><span>odonto em 5<b>.</b></span></div>
<div class="arte"><img src="file://{arte}"></div>
<div class="base"><div class="rot">{rotulo}</div><div class="man">{manchete}</div></div>
</div></body></html>"""


def main(pasta):
    pasta = Path(pasta).resolve()
    post = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
    manchete = html.escape(post["manchete"])
    if post.get("destaque"):
        d = html.escape(post["destaque"])
        manchete = manchete.replace(d, f"<em>{d}</em>", 1)
    tam = 76 if len(post["manchete"]) <= 70 else 64
    pagina = MODELO.format(
        fundo="#153D46" if post.get("tema", "escuro") == "escuro" else "#F6F2E9",
        logo=LOGO, arte=pasta / post["imagem"], rotulo=html.escape(post["rotulo"]).upper(),
        manchete=manchete, tam=tam)
    tmp = pasta / ".render.html"
    tmp.write_text(pagina, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto(f"file://{tmp}")
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(pasta / "post.jpg"), type="jpeg", quality=92,
                      clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
        b.close()
    tmp.unlink()
    print(f"Imagem gerada: {pasta / 'post.jpg'}")


if __name__ == "__main__":
    main(sys.argv[1])
