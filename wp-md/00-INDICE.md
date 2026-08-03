# TADEX · páginas para o WordPress

O site oficial mais as quatro páginas institucionais, uma por arquivo. Abra o `.md`, copie o bloco de código
inteiro e cole num bloco HTML do WordPress.

A landing page não está aqui: ela já está publicada e no ar.

| # | Página | Slug | Tamanho |
|---|---|---|---|
| 0 | [TADEX Transportes](0-site-oficial.md) | `/` | 55 KB |
| 1 | [Fale Conosco](1-fale-conosco.md) | `/fale-conosco` | 40 KB |
| 2 | [Politica de Privacidade](2-politica-de-privacidade.md) | `/politica-de-privacidade` | 40 KB |
| 3 | [Termos de Uso](3-termos-de-uso.md) | `/termos-de-uso` | 49 KB |
| 4 | [Condicoes Gerais de Prestacao de Servico](4-condicoes-gerais.md) | `/condicoes` | 39 KB |
| 5 | [Condicoes para Solicitacao de Coleta](5-condicoes-de-coleta.md) | `/condicoes-de-coleta` | 41 KB |

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

## Depois de publicar

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
