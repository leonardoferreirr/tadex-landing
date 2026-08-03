# TADEX · páginas para o WordPress

Cinco páginas, uma por arquivo. Abra o `.md`, copie o bloco de código inteiro
e cole num bloco HTML do WordPress.

| # | Página | Slug | Tamanho |
|---|---|---|---|
| 1 | [TADEX Transportes](1-site-landing-page.md) | `/` | 28 KB |
| 2 | [Fale Conosco](2-fale-conosco.md) | `/fale-conosco` | 14 KB |
| 3 | [Politica de Privacidade](3-politica-de-privacidade.md) | `/politica-de-privacidade` | 15 KB |
| 4 | [Termos de Uso](4-termos-de-uso.md) | `/termos-de-uso` | 24 KB |
| 5 | [Condicoes para Solicitacao de Coleta](5-condicoes-de-coleta.md) | `/condicoes-de-coleta` | 14 KB |

## Como colar no WordPress

1. **Páginas → Adicionar nova**
2. Em **Título**, use o título indicado abaixo
3. Adicione um bloco **HTML personalizado** (ou, no Elementor, o widget **HTML**)
4. Copie **todo** o conteúdo do bloco de código desta página e cole dentro dele
5. Em **Configurações → Link permanente**, ajuste o slug para o indicado
6. Publique

> Cole o bloco inteiro, do primeiro `<!--` até a última linha. O CSS vai junto,
> escopado em `#tdx-legal`, então ele não vaza para o resto do site nem sofre
> interferência do tema.

---

## Depois de publicar as cinco

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
