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

BASE = pathlib.Path(__file__).parent
CDN = "https://tadex.vercel.app"
ESCOPO = "#tdx-site"

# Mesmos slugs de gerar-wp.py. Mantenha os dois em sincronia.
SLUGS = {
    "privacidade": "/politica-de-privacidade",
    "termos":      "/termos-de-uso",
    "coleta":      "/condicoes-de-coleta",
    "contato":     "/fale-conosco",
}


# ----------------------------------------------------------------- CSS

def dividir_seletores(lista):
    """Split por virgula respeitando parenteses de :is(), :not() etc."""
    partes, atual, nivel = [], "", 0
    for ch in lista:
        if ch == "(":
            nivel += 1
        elif ch == ")":
            nivel -= 1
        if ch == "," and nivel == 0:
            partes.append(atual)
            atual = ""
        else:
            atual += ch
    partes.append(atual)
    return [p.strip() for p in partes if p.strip()]


def prefixar(sel):
    """Prefixa um seletor com o escopo, tratando os casos globais."""
    s = sel.strip()
    if not s:
        return s
    if s in (":root", "html", "body"):
        return ESCOPO
    if s == "*":
        return f"{ESCOPO} *"
    if s.startswith("*::") or s.startswith("*:"):
        return f"{ESCOPO} {s}"
    # body.algo / html.algo viram #tdx-site.algo
    for tag in ("body", "html"):
        if s.startswith(tag) and len(s) > len(tag) and s[len(tag)] in ".:[":
            return ESCOPO + s[len(tag):]
    return f"{ESCOPO} {s}"


def escopar_css(css):
    """Percorre o CSS e prefixa os seletores, preservando as at-rules.

    Os comentarios sao removidos antes: se um deles ficar entre o fim de uma
    regra e o seletor seguinte, ele entra no cabecalho e invalida a regra
    inteira ("#tdx-site /* ... */ .footer{...}" nao casa com nada).
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    saida, i, n = [], 0, len(css)
    while i < n:
        # acha o proximo '{' ou ';' de topo
        j = i
        while j < n and css[j] not in "{;":
            j += 1
        if j >= n:
            saida.append(css[i:])
            break

        if css[j] == ";":                    # at-rule sem corpo (@import, @charset)
            saida.append(css[i:j + 1])
            i = j + 1
            continue

        cabecalho = css[i:j].strip()

        # acha o '}' correspondente
        nivel, k = 1, j + 1
        while k < n and nivel:
            if css[k] == "{":
                nivel += 1
            elif css[k] == "}":
                nivel -= 1
            k += 1
        corpo = css[j + 1:k - 1]

        low = cabecalho.lower()
        if low.startswith("@font-face") or low.startswith("@keyframes") or low.startswith("@-"):
            saida.append(f"{cabecalho}{{{corpo}}}")          # preserva intacto
        elif low.startswith("@media") or low.startswith("@supports"):
            saida.append(f"{cabecalho}{{{escopar_css(corpo)}}}")   # recursivo
        else:
            novos = ",".join(prefixar(s) for s in dividir_seletores(cabecalho))
            saida.append(f"{novos}{{{corpo}}}")

        i = k
    return "".join(saida)


# ----------------------------------------------------------------- HTML

def absolutizar(texto):
    """assets/x.webp -> https://tadex.vercel.app/assets/x.webp"""
    texto = re.sub(r'(src|href)="assets/', rf'\1="{CDN}/assets/', texto)
    texto = re.sub(r'url\((assets/)', rf'url({CDN}/assets/', texto)
    return texto


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
css = escopar_css(css)

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
