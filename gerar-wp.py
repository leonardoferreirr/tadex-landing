#!/usr/bin/env python3
"""
Gera as versoes WordPress (bloco unico) das paginas institucionais.

Le os HTMLs standalone (privacidade/termos/coleta/contato), extrai o hero + corpo,
e escreve wp-<nome>.html com o CSS inline e escopado em #tdx-legal.

Cada arquivo gerado e colado num widget HTML do Elementor, numa pagina do WP.
Nao inclui header nem footer: no WordPress esses vem do tema.

Uso:  python3 gerar-wp.py
"""
import re
import pathlib

BASE = pathlib.Path(__file__).parent
CDN = "https://tadex.vercel.app"

# Slug de cada pagina no WordPress. Ajuste aqui se criar a pagina com outro slug.
PAGINAS = {
    "privacidade": "/politica-de-privacidade",
    "termos":      "/termos-de-uso",
    "coleta":      "/condicoes-de-coleta",
    "contato":     "/fale-conosco",
}

CSS = """
#tdx-legal{--o:#f54900;--o6:#d93f00;--o1:#fdede4;--navy:#081027;--hero:#08111d;
  --cream:#faf1ec;--wa:#37b34a;--wa6:#2e9a3f;--gray:#E4E7EC;--r:16px;--rlg:22px;
  --ease:cubic-bezier(.22,.61,.36,1);
  font-family:'TDX Poppins',system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  color:var(--navy);line-height:1.6;-webkit-font-smoothing:antialiased}
/* Forca a fonte e a cor em TODO descendente: temas do WP costumam ter
   regras proprias para h1/h2/h3/a que vencem a simples heranca do container. */
#tdx-legal *,#tdx-legal *::before,#tdx-legal *::after{
  box-sizing:border-box;font-family:'TDX Poppins',system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
#tdx-legal h1,#tdx-legal h2,#tdx-legal h3,#tdx-legal h4{color:var(--navy);font-weight:700;text-transform:none}
#tdx-legal .legal-hero h1,#tdx-legal .legal-hero p{color:#fff}
#tdx-legal h1,#tdx-legal h2,#tdx-legal h3,#tdx-legal p{margin:0}
#tdx-legal img{max-width:100%;display:block}
#tdx-legal a{color:inherit}
#tdx-legal .container{width:100%;max-width:1200px;margin-inline:auto;padding-inline:clamp(20px,5vw,40px)}

#tdx-legal .legal-hero{background:var(--hero);color:#fff;padding-block:clamp(40px,6vw,72px);
  border-bottom:4px solid var(--o);position:relative;overflow:hidden}
#tdx-legal .legal-hero::after{content:"";position:absolute;right:-60px;top:50%;transform:translateY(-50%);
  width:340px;height:340px;border-radius:50%;
  background:radial-gradient(circle,rgba(245,73,0,.20),transparent 68%);pointer-events:none}
#tdx-legal .legal-hero h1{font-size:clamp(1.85rem,4.4vw,3rem);line-height:1.14;
  letter-spacing:-.02em;position:relative;z-index:1;color:#fff}
#tdx-legal .legal-hero p{margin-top:12px;color:rgba(255,255,255,.72) !important;max-width:60ch;position:relative;z-index:1}

#tdx-legal .legal{padding-block:clamp(40px,6vw,72px);background:#fff}
#tdx-legal .legal .container{display:grid;grid-template-columns:230px minmax(0,1fr);
  gap:clamp(32px,5vw,64px);align-items:start}
#tdx-legal .legal--full .container{grid-template-columns:minmax(0,1fr)}
#tdx-legal .legal--full .legal__body{max-width:none}
#tdx-legal .legal__body{max-width:78ch;min-width:0}
#tdx-legal .legal__meta{display:inline-block;background:var(--o1);color:var(--o6);
  font-size:.83rem;font-weight:700;padding:.45em 1em;border-radius:999px;margin-bottom:28px}
#tdx-legal .legal__body h2{font-size:clamp(1.12rem,2.1vw,1.4rem);line-height:1.3;
  margin:38px 0 12px;scroll-margin-top:24px;letter-spacing:-.01em;color:var(--navy)}
#tdx-legal .legal__body h2:first-of-type{margin-top:0}
#tdx-legal .legal__body h3{font-size:1.02rem;margin:26px 0 10px;color:var(--navy);scroll-margin-top:24px}
#tdx-legal .legal__body p{margin-bottom:14px;color:#3d4658}
#tdx-legal .legal__body ul,#tdx-legal .legal__body ol{margin:0 0 18px;padding-left:22px;color:#3d4658}
#tdx-legal .legal__body ul{list-style:disc}
#tdx-legal .legal__body ol{list-style:decimal}
#tdx-legal .legal__body li{margin-bottom:9px;padding-left:4px}
#tdx-legal .legal__body li::marker{color:var(--o);font-weight:700}
#tdx-legal .legal__body strong{color:var(--navy);font-weight:700}
#tdx-legal .legal__body a:not(.btn){color:var(--o6);font-weight:700;text-decoration:underline;
  text-underline-offset:3px;text-decoration-thickness:1.5px}
#tdx-legal .legal__body a:not(.btn):hover{color:var(--o)}

#tdx-legal .legal-toc{position:sticky;top:24px}
#tdx-legal .legal-toc h2{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;
  color:#7a8496;margin-bottom:14px;font-weight:700}
#tdx-legal .legal-toc ol{list-style:none;margin:0;padding:0;border-left:2px solid var(--gray)}
#tdx-legal .legal-toc a{display:block;padding:7px 0 7px 16px;margin-left:-2px;font-size:.88rem;
  color:#5b6478;line-height:1.35;border-left:2px solid transparent;
  text-decoration:none;transition:color .2s,border-color .2s}
#tdx-legal .legal-toc a:hover{color:var(--o6);border-left-color:var(--o)}

#tdx-legal .legal-note{background:var(--cream);border-left:4px solid var(--o);
  border-radius:0 var(--r) var(--r) 0;padding:clamp(20px,3vw,28px);margin:28px 0}
#tdx-legal .legal-note h3{margin-top:0}
#tdx-legal .legal-note p:last-child{margin-bottom:0}
#tdx-legal .legal-alert{background:#fff4ef;border:2px solid var(--o);border-radius:var(--r);
  padding:clamp(18px,2.6vw,24px);margin-bottom:32px}
#tdx-legal .legal-alert p{margin:0;color:var(--navy);font-weight:700}

#tdx-legal .contato-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:22px;margin-bottom:36px}
#tdx-legal .contato-card{background:#fff;border:1px solid var(--gray);border-radius:var(--rlg);
  padding:clamp(22px,3vw,30px);box-shadow:0 2px 8px rgba(8,16,39,.06);
  transition:transform .25s var(--ease),box-shadow .25s var(--ease)}
#tdx-legal .contato-card:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(8,16,39,.10)}
#tdx-legal .contato-card__tag{display:inline-block;background:var(--o1);color:var(--o6);
  font-size:.75rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  padding:.4em .9em;border-radius:999px;margin-bottom:14px}
#tdx-legal .contato-card h3{font-size:1.1rem;margin:0 0 10px}
#tdx-legal .contato-card address{font-style:normal;color:#3d4658;line-height:1.65;margin-bottom:16px}
#tdx-legal .contato-card__list{display:grid;gap:9px;list-style:none;margin:0;padding:0}
#tdx-legal .contato-card__list li{display:flex;align-items:center;gap:.6em;color:#3d4658;font-size:.95rem}
#tdx-legal .contato-card__list svg{width:17px;height:17px;flex:none;color:var(--o)}

#tdx-legal .form-wa{background:var(--cream);border-radius:var(--rlg);padding:clamp(24px,3.4vw,36px)}
#tdx-legal .form-wa h2{margin-top:0}
#tdx-legal .form-wa__grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  gap:16px;margin:16px 0}
#tdx-legal .form-wa__field{display:flex;flex-direction:column;gap:7px}
#tdx-legal .form-wa__field--full{grid-column:1/-1}
#tdx-legal .form-wa label{font-size:.88rem;font-weight:700;color:var(--navy)}
#tdx-legal .form-wa input,#tdx-legal .form-wa textarea,#tdx-legal .form-wa select{
  font-family:inherit;font-size:.97rem;color:var(--navy);background:#fff;
  border:1.5px solid var(--gray);border-radius:12px;padding:.78em 1em;width:100%;
  transition:border-color .2s,box-shadow .2s}
#tdx-legal .form-wa textarea{resize:vertical;min-height:118px}
#tdx-legal .form-wa input:focus,#tdx-legal .form-wa textarea:focus,#tdx-legal .form-wa select:focus{
  outline:none;border-color:var(--o);box-shadow:0 0 0 3px rgba(245,73,0,.13)}
#tdx-legal .form-wa__hint{font-size:.85rem;color:#6b7383;margin-top:14px}
#tdx-legal .btn{display:inline-flex;align-items:center;gap:.55em;font-weight:700;font-size:.98rem;
  padding:.85em 1.6em;border-radius:999px;border:2px solid transparent;cursor:pointer;
  font-family:inherit;text-decoration:none;
  transition:transform .25s var(--ease),background .25s,box-shadow .25s}
#tdx-legal .btn svg{width:1.15em;height:1.15em;flex:none}
#tdx-legal .btn--wa{background:var(--wa);color:#fff;box-shadow:0 8px 20px rgba(55,179,74,.26)}
#tdx-legal .btn--wa:hover{background:var(--wa6);transform:translateY(-2px)}

@media(max-width:900px){
  #tdx-legal .legal .container{grid-template-columns:1fr}
  #tdx-legal .legal-toc{position:static;order:-1;background:var(--cream);border-radius:var(--r);padding:20px 22px}
  #tdx-legal .legal-toc ol{columns:2;column-gap:24px;border-left:0}
  #tdx-legal .legal-toc a{padding-left:0;border-left:0}
}
@media(max-width:560px){#tdx-legal .legal-toc ol{columns:1}}
@media(prefers-reduced-motion:reduce){
  #tdx-legal .contato-card{transition:none}
  #tdx-legal .contato-card:hover{transform:none}
}
"""

FONTES = f"""@font-face{{font-family:'TDX Poppins';font-style:normal;font-weight:400;font-display:swap;src:url({CDN}/assets/poppins-400.woff2) format('woff2')}}
@font-face{{font-family:'TDX Poppins';font-style:normal;font-weight:700;font-display:swap;src:url({CDN}/assets/poppins-700.woff2) format('woff2')}}"""


def extrair(html):
    """Pega o <section class="legal-hero"> e o <main class="legal">."""
    hero = re.search(r'<section class="legal-hero">.*?</section>', html, re.S)
    main = re.search(r'<main class="legal.*?</main>', html, re.S)
    if not hero or not main:
        raise SystemExit("nao achei hero/main no HTML")
    return hero.group(0) + "\n" + main.group(0)


def reescrever_links(bloco):
    """Troca os caminhos .html pelos slugs do WordPress."""
    bloco = bloco.replace('href="index.html#', 'href="/#')
    bloco = bloco.replace('href="index.html"', 'href="/"')
    for arquivo, slug in PAGINAS.items():
        bloco = bloco.replace(f'href="{arquivo}.html"', f'href="{slug}"')
    return bloco


def script_form(html):
    """Devolve o <script> da pagina, se houver (so a de contato tem)."""
    m = re.search(r'<script>\s*\(function\(\).*?</script>', html, re.S)
    return "\n" + m.group(0) if m else ""


for nome, slug in PAGINAS.items():
    origem = BASE / f"{nome}.html"
    html = origem.read_text(encoding="utf-8")

    bloco = reescrever_links(extrair(html))
    js = script_form(html)

    # O bloco ja mostra o titulo no hero. Sem isso, o tema imprime o titulo da
    # pagina logo acima e o visitante ve o mesmo texto duas vezes.
    esconde_titulo = """
/* esconde o titulo que o tema imprime: o hero abaixo ja mostra ele */
.entry-title,.page-header,.page-title{display:none !important}"""

    saida = f"""<!-- ============================================================
     TADEX - {nome.upper()} para WordPress (widget HTML do Elementor)
     Bloco unico, CSS inline e escopado em #tdx-legal.
     Slug sugerido da pagina: {slug}
     Gerado por gerar-wp.py, nao edite este arquivo na mao.
     Edite {nome}.html e rode: python3 gerar-wp.py
     ============================================================ -->
<style id="tdx-legal-css">
{FONTES}
{esconde_titulo}
{CSS.strip()}
</style>

<div id="tdx-legal">
{bloco}
</div>{js}
"""
    destino = BASE / f"wp-{nome}.html"
    destino.write_text(saida, encoding="utf-8")
    print(f"gerado: wp-{nome}.html  ({len(saida)//1024} KB)  ->  slug {slug}")
