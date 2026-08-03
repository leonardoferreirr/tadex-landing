#!/usr/bin/env python3
"""
Gera a versao WordPress (bloco unico) do site oficial, a partir do index.html.

Escopa todo o styles.css em #tdx-site, embute o script.js escopado no mesmo
container, aponta os assets para o Vercel e troca os links das paginas
institucionais pelos slugs do WordPress.

Saida: wp-site.html

Uso:  python3 gerar-wp-site.py
"""
import re
import pathlib

from wp_comum import absolutizar as _abs, escopar_css as _esc

BASE = pathlib.Path(__file__).parent
CDN = "https://tadex.vercel.app"
ESCOPO = "#tdx-site"

# Mesmos slugs de gerar-wp.py. Mantenha os dois em sincronia.
SLUGS = {
    "privacidade": "/politica-de-privacidade",
    "termos":      "/termos-de-uso",
    "coleta":      "/coleta",
    "contato":     "/fale-conosco",
}


# ----------------------------------------------------------------- HTML

def absolutizar(texto):
    return _abs(texto)


def trocar_links(html):
    """Aponta as paginas institucionais para os slugs do WordPress."""
    for arquivo, slug in SLUGS.items():
        html = html.replace(f'href="{arquivo}.html"', f'href="{slug}"')
    # ancoras da propria home continuam sendo ancoras
    html = html.replace('href="index.html#', 'href="#')
    html = html.replace('href="index.html"', 'href="#top"')
    return html


# ----------------------------------------------------------------- montagem

index = (BASE / "index.html").read_text(encoding="utf-8")
css = (BASE / "styles.css").read_text(encoding="utf-8")
js = (BASE / "script.js").read_text(encoding="utf-8")

# corpo: tudo entre <body> e </body>, sem a tag <script src>
corpo = re.search(r"<body>(.*)</body>", index, re.S).group(1)
corpo = re.sub(r'<script src="script\.js"[^>]*></script>', "", corpo)
corpo = trocar_links(absolutizar(corpo)).strip()

# css: escopado, com a fonte renomeada para nao brigar com a do tema
css = absolutizar(css)
css = css.replace("'Poppins'", "'TDX Poppins'")
css = _esc(css, ESCOPO)

# js: as buscas passam a partir do container, nao do document
js = js.replace("document.querySelector(", "ROOT.querySelector(")
js = js.replace("document.querySelectorAll(", "ROOT.querySelectorAll(")
js = js.replace("document.getElementById('navToggle')", "ROOT.querySelector('#navToggle')")
js = js.replace("document.getElementById('nav')", "ROOT.querySelector('#nav')")

# Reforco: temas do WP trazem regras proprias para h1/h2/h3/a/ul/li que vencem
# a heranca do container. Repete o essencial no fim, ja escopado.
REFORCO = f"""
{ESCOPO} *,{ESCOPO} *::before,{ESCOPO} *::after{{
  font-family:'TDX Poppins',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  box-sizing:border-box}}
{ESCOPO} h1,{ESCOPO} h2,{ESCOPO} h3,{ESCOPO} h4{{text-transform:none;letter-spacing:normal}}
{ESCOPO} ul,{ESCOPO} ol{{list-style:none;margin:0;padding:0}}
{ESCOPO} a{{text-decoration:none}}
{ESCOPO} img{{max-width:100%;height:auto;display:block}}
"""
css = css + REFORCO

saida = f"""<!-- ============================================================
     TADEX - SITE OFICIAL para WordPress (widget HTML do Elementor)
     Bloco unico. CSS escopado em {ESCOPO}, JS escopado no mesmo container.
     Imagens e fontes vem de {CDN}.
     Os links do rodape ja apontam para os slugs das paginas institucionais.
     Gerado por gerar-wp-site.py, nao edite este arquivo na mao.
     Edite index.html / styles.css / script.js e rode: python3 gerar-wp-site.py
     ============================================================ -->
<style id="tdx-site-css">
{css}
</style>

<div id="tdx-site">
{corpo}
</div>

<script>
(function(){{
  var ROOT = document.getElementById('tdx-site');
  if(!ROOT) return;
{js}
}})();
</script>
"""

destino = BASE / "wp-site.html"
destino.write_text(saida, encoding="utf-8")
print(f"gerado: wp-site.html ({len(saida)//1024} KB)")

# checagens rapidas
faltando = re.findall(r'(?:src|href)="assets/', saida)
if faltando:
    print(f"AVISO: {len(faltando)} assets ainda relativos")
sobrou = re.findall(r'href="(?:privacidade|termos|coleta|contato)\.html"', saida)
if sobrou:
    print(f"AVISO: {len(sobrou)} links .html nao convertidos")
for slug in SLUGS.values():
    if f'href="{slug}"' not in saida:
        print(f"AVISO: rodape sem link para {slug}")
