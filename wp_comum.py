"""
Utilitarios compartilhados por gerar-wp.py e gerar-wp-site.py:
escopar um CSS inteiro sob um seletor raiz e absolutizar assets.
"""
import re

CDN = "https://tadex.vercel.app"


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


def prefixar(sel, escopo):
    """Prefixa um seletor com o escopo, tratando os casos globais."""
    s = sel.strip()
    if not s:
        return s
    if s in (":root", "html", "body"):
        return escopo
    if s == "*":
        return f"{escopo} *"
    if s.startswith("*::") or s.startswith("*:"):
        return f"{escopo} {s}"
    for tag in ("body", "html"):
        if s.startswith(tag) and len(s) > len(tag) and s[len(tag)] in ".:[":
            return escopo + s[len(tag):]
    return f"{escopo} {s}"


def escopar_css(css, escopo):
    """Prefixa todos os seletores do CSS com o escopo, preservando at-rules.

    Comentarios sao removidos antes: um comentario entre o fim de uma regra e o
    seletor seguinte entraria no cabecalho e invalidaria a regra inteira.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    saida, i, n = [], 0, len(css)
    while i < n:
        j = i
        while j < n and css[j] not in "{;":
            j += 1
        if j >= n:
            saida.append(css[i:])
            break
        if css[j] == ";":
            saida.append(css[i:j + 1])
            i = j + 1
            continue
        cabecalho = css[i:j].strip()
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
            saida.append(f"{cabecalho}{{{corpo}}}")
        elif low.startswith("@media") or low.startswith("@supports"):
            saida.append(f"{cabecalho}{{{escopar_css(corpo, escopo)}}}")
        else:
            novos = ",".join(prefixar(s, escopo) for s in dividir_seletores(cabecalho))
            saida.append(f"{novos}{{{corpo}}}")
        i = k
    return "".join(saida)


def absolutizar(texto):
    """assets/x.webp -> https://tadex.vercel.app/assets/x.webp"""
    texto = re.sub(r'(src|href)="assets/', rf'\1="{CDN}/assets/', texto)
    texto = re.sub(r'url\((assets/)', rf'url({CDN}/assets/', texto)
    return texto


def reforco_tipografia(escopo, fonte="'TDX Poppins'"):
    """Regras finais que vencem o CSS de temas/plugins do WordPress."""
    return f"""
{escopo} *,{escopo} *::before,{escopo} *::after{{
  font-family:{fonte},system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  box-sizing:border-box}}
{escopo} h1,{escopo} h2,{escopo} h3,{escopo} h4{{text-transform:none;letter-spacing:normal}}
{escopo} ul,{escopo} ol{{margin:0;padding:0}}
{escopo} a{{text-decoration:none}}
{escopo} img{{max-width:100%;height:auto;display:block}}
"""
