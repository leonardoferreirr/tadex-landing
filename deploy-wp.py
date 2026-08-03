#!/usr/bin/env python3
"""
Publica as cinco paginas no WordPress pela REST API nativa.

Credenciais em ~/.config/tadex-wp.txt (NUNCA no repositorio, nunca no chat):

    url=https://tadex.com.br
    user=seu-usuario-wp
    pass=xxxx xxxx xxxx xxxx xxxx xxxx

O "pass" e uma Senha de Aplicativo, nao a senha do login. Como gerar:
Usuarios -> Perfil -> Senhas de aplicativo -> nome "claude-deploy" -> Adicionar.
O WordPress mostra a senha UMA vez. Ela pode ser revogada nessa mesma tela a
qualquer momento, sem afetar a sua senha de login.

Uso:
    python3 deploy-wp.py           # simula, nao grava nada
    python3 deploy-wp.py --go      # publica de verdade
    python3 deploy-wp.py --go site # publica so uma pagina
"""
import base64
import json
import pathlib
import sys
import urllib.error
import urllib.request

BASE = pathlib.Path(__file__).parent
CRED = pathlib.Path.home() / ".config" / "tadex-wp.txt"

# chave: (arquivo, titulo, slug, template)
# elementor_canvas       = sem header/rodape/titulo do tema (o bloco traz os seus)
# elementor_header_footer = largura total, mantendo header/rodape do tema
PAGINAS = {
    "site":        ("wp-site.html",        "TADEX Transportes",
                    "home",                     "elementor_canvas"),
    "contato":     ("wp-contato.html",     "Fale Conosco",
                    "fale-conosco",             "elementor_header_footer"),
    "privacidade": ("wp-privacidade.html", "Política de Privacidade",
                    "politica-de-privacidade",  "elementor_header_footer"),
    "termos":      ("wp-termos.html",      "Termos de Uso",
                    "termos-de-uso",            "elementor_header_footer"),
    "coleta":      ("wp-coleta.html",      "Condições para Solicitação de Coleta",
                    "condicoes-de-coleta",      "elementor_header_footer"),
}


def carregar_credenciais():
    if not CRED.exists():
        sys.exit(
            f"Faltando {CRED}\n\n"
            "Crie o arquivo com tres linhas:\n"
            "  url=https://tadex.com.br\n"
            "  user=seu-usuario-wp\n"
            "  pass=senha de aplicativo gerada no perfil do WordPress\n"
        )
    dados = {}
    for linha in CRED.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, v = linha.split("=", 1)
            dados[k.strip()] = v.strip()
    faltando = {"url", "user", "pass"} - dados.keys()
    if faltando:
        sys.exit(f"{CRED} sem: {', '.join(sorted(faltando))}")
    dados["url"] = dados["url"].rstrip("/")
    return dados


def chamar(cred, caminho, metodo="GET", corpo=None):
    url = f"{cred['url']}/wp-json/wp/v2/{caminho}"
    token = base64.b64encode(f"{cred['user']}:{cred['pass']}".encode()).decode()
    req = urllib.request.Request(
        url,
        method=metodo,
        data=json.dumps(corpo).encode("utf-8") if corpo else None,
        headers={
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "User-Agent": "tadex-deploy",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", "replace")[:400]
        sys.exit(f"\nERRO HTTP {e.code} em {metodo} {caminho}\n{detalhe}\n")


def main():
    executar = "--go" in sys.argv
    alvos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if alvos:
        desconhecidas = set(alvos) - PAGINAS.keys()
        if desconhecidas:
            sys.exit(f"pagina desconhecida: {', '.join(desconhecidas)}\n"
                     f"validas: {', '.join(PAGINAS)}")
    else:
        alvos = list(PAGINAS)

    cred = carregar_credenciais()

    if not executar:
        print("MODO SIMULACAO. Nada sera gravado. Use --go para publicar.\n")

    me = chamar(cred, "users/me")
    print(f"conectado como: {me.get('name')} ({', '.join(me.get('roles', []))})")
    print(f"site: {cred['url']}\n")

    for chave in alvos:
        arquivo, titulo, slug, template = PAGINAS[chave]
        caminho = BASE / arquivo
        if not caminho.exists():
            print(f"  {chave}: {arquivo} nao encontrado, pulando")
            continue

        html = caminho.read_text(encoding="utf-8").strip()
        # Envolve num bloco HTML do Gutenberg para o editor preservar o markup cru.
        conteudo = f"<!-- wp:html -->\n{html}\n<!-- /wp:html -->"

        existentes = chamar(cred, f"pages?slug={slug}&status=publish,draft,private")
        payload = {
            "title": titulo,
            "slug": slug,
            "content": conteudo,
            "status": "publish",
            "template": template,
        }

        if existentes:
            pid = existentes[0]["id"]
            acao = f"ATUALIZAR pagina {pid}"
            destino = f"pages/{pid}"
        else:
            acao = "CRIAR pagina nova"
            destino = "pages"

        print(f"  {chave:12} {acao}")
        print(f"  {'':12} titulo   : {titulo}")
        print(f"  {'':12} slug     : /{slug}")
        print(f"  {'':12} template : {template}")
        print(f"  {'':12} conteudo : {len(html)//1024} KB")

        if executar:
            r = chamar(cred, destino, "POST", payload)
            aplicado = r.get("template") or "(default)"
            print(f"  {'':12} -> {r.get('link')}")
            if aplicado != template:
                print(f"  {'':12} AVISO: o tema nao aceitou '{template}', "
                      f"ficou '{aplicado}'. Ajuste o template na mao.")
            # o WP remove <style>/<script> de quem nao tem unfiltered_html
            bruto = r.get("content", {}).get("raw", "")
            if bruto and "<style" not in bruto and "<style" in html:
                print(f"  {'':12} AVISO: o <style> foi removido na gravacao. "
                      f"Seu usuario precisa da permissao unfiltered_html.")
        print()

    if executar:
        print("Pronto. Confira as paginas antes de divulgar.")
    else:
        print("Simulacao encerrada. Rode de novo com --go para publicar.")


if __name__ == "__main__":
    main()
