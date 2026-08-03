#!/usr/bin/env python3
"""
Empacota os blocos WordPress em arquivos .md, prontos para copiar e colar.

Gera a pasta wp-md/ com um .md por pagina do WP, cada um contendo o HTML
completo dentro de um bloco de codigo, mais o slug e o titulo sugeridos.

Uso:  python3 gerar-md.py
"""
import pathlib

BASE = pathlib.Path(__file__).parent
DEST = BASE / "wp-md"
DEST.mkdir(exist_ok=True)

# ordem, arquivo de origem, nome do .md, titulo da pagina no WP, slug, observacao
# A landing page fica de fora: ja esta publicada e no ar.
PAGINAS = [
    (1, "wp-contato.html", "1-fale-conosco",
     "Fale Conosco", "/fale-conosco",
     "Tem formulario: o bloco inclui um <script> no fim. Cole tudo, inclusive o script."),
    (2, "wp-privacidade.html", "2-politica-de-privacidade",
     "Politica de Privacidade", "/politica-de-privacidade",
     "Este e o link que voce informa no Meta Ads, no Google e nos formularios de lead."),
    (3, "wp-termos.html", "3-termos-de-uso",
     "Termos de Uso", "/termos-de-uso", ""),
    (4, "wp-coleta.html", "4-condicoes-de-coleta",
     "Condicoes para Solicitacao de Coleta", "/condicoes-de-coleta",
     "O site antigo usava /coleta. Se quiser preservar o link antigo, use esse slug."),
]

COMO = """## Como colar no WordPress

1. **Páginas → Adicionar nova**
2. Em **Título**, use o título indicado abaixo
3. Adicione um bloco **HTML personalizado** (ou, no Elementor, o widget **HTML**)
4. Copie **todo** o conteúdo do bloco de código desta página e cole dentro dele
5. Em **Configurações → Link permanente**, ajuste o slug para o indicado
6. Publique

> Cole o bloco inteiro, do primeiro `<!--` até a última linha. O CSS vai junto,
> escopado em `#tdx-legal`, então ele não vaza para o resto do site nem sofre
> interferência do tema.
"""

linhas_indice = []

for ordem, origem, nome_md, titulo, slug, obs in PAGINAS:
    caminho = BASE / origem
    if not caminho.exists():
        print(f"AVISO: {origem} nao encontrado, pulando")
        continue

    html = caminho.read_text(encoding="utf-8")
    kb = len(html.encode("utf-8")) // 1024

    corpo = f"""# {titulo}

| | |
|---|---|
| **Título da página** | {titulo} |
| **Slug** | `{slug}` |
| **Origem** | `{origem}` |
| **Tamanho** | {kb} KB |

"""
    if obs:
        corpo += f"> **Atenção:** {obs}\n\n"

    corpo += COMO + f"""
---

## Conteúdo para colar

```html
{html.rstrip()}
```
"""
    (DEST / f"{nome_md}.md").write_text(corpo, encoding="utf-8")
    linhas_indice.append(f"| {ordem} | [{titulo}]({nome_md}.md) | `{slug}` | {kb} KB |")
    print(f"gerado: wp-md/{nome_md}.md  ({kb} KB)")

indice = f"""# TADEX · páginas institucionais para o WordPress

Quatro páginas novas, uma por arquivo. Abra o `.md`, copie o bloco de código
inteiro e cole num bloco HTML do WordPress.

A landing page não está aqui: ela já está publicada e no ar.

| # | Página | Slug | Tamanho |
|---|---|---|---|
{chr(10).join(linhas_indice)}

{COMO}
---

## Depois de publicar as quatro

Aponte o menu e o rodapé do tema para os novos slugs. Os links **dentro** dos
blocos já estão apontando para eles, então basta os slugs baterem com a tabela
acima. Se você criar alguma página com slug diferente, ajuste o dicionário
`PAGINAS` no topo de `gerar-wp.py` e rode `python3 gerar-wp.py` de novo.

## Para editar o conteúdo depois

Não edite os arquivos `wp-*.html` nem os `.md`: os dois são gerados.
Edite a página normal (`contato.html`, `privacidade.html`, `termos.html`,
`coleta.html`) e rode, nesta ordem:

```bash
python3 gerar-wp.py && python3 gerar-md.py
```
"""
(DEST / "00-INDICE.md").write_text(indice, encoding="utf-8")
print("gerado: wp-md/00-INDICE.md")
