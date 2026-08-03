#!/usr/bin/env python3
"""
Gera as versoes WordPress (bloco unico) das paginas institucionais.

Cada bloco leva a pagina INTEIRA da identidade nova: header navy (legal-top),
hero, corpo e rodape completo do site novo. Sao publicadas em Elementor
Canvas, entao nada do tema antigo aparece em volta.

O CSS e o styles.css inteiro do site, escopado em #tdx-legal, com a fonte
renomeada para nao brigar com a Poppins de tema/plugin.

Uso:  python3 gerar-wp.py
"""
import pathlib
import re

from wp_comum import CDN, absolutizar, escopar_css, reforco_tipografia

BASE = pathlib.Path(__file__).parent
ESCOPO = "#tdx-legal"

# Slugs no WordPress. "coleta" mantem o slug antigo do site, que tem link externo.
SLUGS = {
    "privacidade": "/politica-de-privacidade",
    "termos":      "/termos-de-uso",
    "coleta":      "/coleta",
    "contato":     "/fale-conosco",
}

FONTES = f"""@font-face{{font-family:'TDX Poppins';font-style:normal;font-weight:400;font-display:swap;src:url({CDN}/assets/poppins-400.woff2) format('woff2')}}
@font-face{{font-family:'TDX Poppins';font-style:normal;font-weight:700;font-display:swap;src:url({CDN}/assets/poppins-700.woff2) format('woff2')}}"""


def trocar_links(html):
    for arquivo, slug in SLUGS.items():
        html = html.replace(f'href="{arquivo}.html"', f'href="{slug}"')
    html = html.replace('href="index.html#', 'href="/#')
    html = html.replace('href="index.html"', 'href="/"')
    return html


def script_form(html):
    m = re.search(r"<script>\s*\(function\(\).*?</script>", html, re.S)
    return "\n" + m.group(0) if m else ""


css_site = (BASE / "styles.css").read_text(encoding="utf-8")
css_site = absolutizar(css_site).replace("'Poppins'", "'TDX Poppins'")
css_escopado = escopar_css(css_site, ESCOPO) + reforco_tipografia(ESCOPO)

# Cores dos headings: o styles.css confia na heranca do body, mas dentro do WP
# um tema com h1{color:...} vence heranca. Fixa navy no corpo e branco no hero.
css_escopado += f"""
{ESCOPO} h1,{ESCOPO} h2,{ESCOPO} h3,{ESCOPO} h4{{color:var(--navy)}}
{ESCOPO} .legal-hero h1{{color:#fff}}
{ESCOPO} .legal-hero p{{color:rgba(255,255,255,.72)}}
{ESCOPO} .footer h3{{color:#fff}}
{ESCOPO} .legal__body p,{ESCOPO} .legal__body li{{color:#3d4658}}
"""

css_escopado += """
/* Esconde a barra de admin do WP (so aparece para usuario logado).
   Regras globais de proposito: #wpadminbar vive fora do bloco. */
#wpadminbar{display:none !important}
html{margin-top:0 !important}
html.wp-toolbar{padding-top:0 !important}
"""

for nome, slug in SLUGS.items():
    origem = BASE / f"{nome}.html"
    html = origem.read_text(encoding="utf-8")

    corpo = re.search(r"<body>(.*)</body>", html, re.S).group(1)
    js = script_form(corpo)
    corpo = re.sub(r"<script>\s*\(function\(\).*?</script>", "", corpo, flags=re.S)
    corpo = trocar_links(absolutizar(corpo)).strip()

    saida = f"""<!-- ============================================================
     TADEX - {nome.upper()} para WordPress (bloco HTML)
     Pagina completa da identidade nova: header, hero, corpo e rodape.
     Publicar com template Elementor Canvas. CSS escopado em {ESCOPO}.
     Gerado por gerar-wp.py, nao edite este arquivo na mao.
     Edite {nome}.html e rode: python3 gerar-wp.py
     ============================================================ -->
<style id="tdx-legal-css">
{FONTES}
{css_escopado}
</style>

<div id="tdx-legal">
{corpo}
</div>{js}
"""
    destino = BASE / f"wp-{nome}.html"
    destino.write_text(saida, encoding="utf-8")
    print(f"gerado: wp-{nome}.html  ({len(saida)//1024} KB)  ->  slug {slug}")

    if 'href="' + nome + '.html"' in saida:
        print(f"  AVISO: link .html nao convertido em wp-{nome}.html")
