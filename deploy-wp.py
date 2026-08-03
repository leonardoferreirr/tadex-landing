#!/usr/bin/env python3
"""
Publica as cinco paginas no WordPress pela REST API nativa.

POR QUE NAO ATUALIZA AS PAGINAS QUE JA EXISTEM
As paginas atuais (home 14, fale-conosco 1285, privacidade 1303, termos 1305,
coleta 1797) foram construidas no Elementor. O Elementor guarda o layout num
campo proprio (_elementor_data) e renderiza ELE, ignorando o content do WP.
Escrever no content dessas paginas gravaria sem erro nenhum e nao mudaria nada
na tela. Por isso o fluxo aqui e outro:

  1. a pagina antiga vira rascunho e ganha o sufixo -antiga no slug
  2. uma pagina NOVA e criada, limpa, sem Elementor, com o slug liberado
  3. no caso da home, o WordPress passa a apontar a nova como pagina inicial

Nada e apagado. O conteudo antigo continua no ar como rascunho e volta com
--reverter. O HTML publico de antes esta em backup-wp/.

Credenciais em ~/.config/tadex-wp.txt:
    url=https://www.tadex.com.br
    user=usuario
    pass=senha de aplicativo

Uso:
    python3 deploy-wp.py              # simula, nao grava
    python3 deploy-wp.py --go         # executa
    python3 deploy-wp.py --go coleta  # so uma pagina
    python3 deploy-wp.py --reverter --go   # desfaz, volta as antigas
"""
import base64
import json
import pathlib
import sys
import urllib.error
import urllib.request

BASE = pathlib.Path(__file__).parent
CRED = pathlib.Path.home() / ".config" / "tadex-wp.txt"
ESTADO = BASE / "backup-wp" / "estado-original.json"
FEITO = BASE / "backup-wp" / "paginas-novas.json"

# chave: arquivo, titulo, slug final, template, id da pagina antiga
PAGINAS = {
    "site":        ("wp-site.html",        "TADEX Transportes",
                    "home",                    "elementor_canvas",        14),
    "contato":     ("wp-contato.html",     "Fale Conosco",
                    "fale-conosco",            "elementor_canvas",        1285),
    "privacidade": ("wp-privacidade.html", "Política de Privacidade",
                    "politica-de-privacidade", "elementor_canvas",        1303),
    "termos":      ("wp-termos.html",      "Termos de Uso",
                    "termos-de-uso",           "elementor_canvas",        1305),
    # slug 'coleta': o que o site antigo ja usava, ha links externos apontando
    "coleta":      ("wp-coleta.html",      "Condições para Solicitação de Coleta",
                    "coleta",                  "elementor_canvas",        1797),
}


def credenciais():
    if not CRED.exists():
        sys.exit(f"Faltando {CRED}. Ver o cabecalho deste arquivo.")
    d = {}
    for linha in CRED.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, v = linha.split("=", 1)
            d[k.strip()] = v.strip()
    if {"url", "user", "pass"} - d.keys():
        sys.exit(f"{CRED} incompleto: precisa de url, user e pass.")
    d["url"] = d["url"].rstrip("/")
    return d


def api(cred, caminho, metodo="GET", corpo=None):
    token = base64.b64encode(f"{cred['user']}:{cred['pass']}".encode()).decode()
    req = urllib.request.Request(
        f"{cred['url']}/wp-json/wp/v2/{caminho}",
        method=metodo,
        data=json.dumps(corpo).encode("utf-8") if corpo else None,
        headers={"Authorization": f"Basic {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "tadex-deploy"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"\nERRO HTTP {e.code} em {metodo} {caminho}\n"
                 f"{e.read().decode('utf-8', 'replace')[:500]}\n")


def publicar(cred, alvos, executar):
    novas = json.loads(FEITO.read_text()) if FEITO.exists() else {}

    for chave in alvos:
        arquivo, titulo, slug, template, id_antiga = PAGINAS[chave]
        caminho = BASE / arquivo
        if not caminho.exists():
            print(f"  {chave}: {arquivo} nao existe, pulando\n")
            continue

        html = caminho.read_text(encoding="utf-8").strip()
        conteudo = f"<!-- wp:html -->\n{html}\n<!-- /wp:html -->"

        ja_criada = novas.get(chave)
        print(f"  {chave}")
        if ja_criada:
            print(f"    ATUALIZA pagina {ja_criada['id']} ja criada, template {template}, {len(html)//1024} KB")
        else:
            print(f"    1. cria pagina nova, slug '/{slug}', template {template}, {len(html)//1024} KB")
            if chave == "site":
                print(f"    2. define a nova como pagina inicial do site")
            print(f"    {'3' if chave == 'site' else '2'}. pagina antiga {id_antiga} vira rascunho, slug '{slug}-antiga'")

        if not executar:
            print()
            continue

        if ja_criada:
            nova = api(cred, f"pages/{ja_criada['id']}", "POST", {
                "title": titulo, "slug": slug, "content": conteudo,
                "status": "publish", "template": template,
            })
        else:
            # cria primeiro; o slug desejado pode sair com sufixo ate a antiga
            # ser arquivada, entao corrige o slug depois de liberar
            nova = api(cred, "pages", "POST", {
                "title": titulo, "content": conteudo,
                "status": "publish", "template": template,
            })
        novas[chave] = {"id": nova["id"], "link": nova["link"]}
        print(f"    -> criada: {nova['link']}  (id {nova['id']})")

        aplicado = nova.get("template") or "(default)"
        if aplicado != template:
            print(f"    AVISO: template ficou '{aplicado}' em vez de '{template}'")

        bruto = nova.get("content", {}).get("raw", "")
        if "<style" in html and "<style" not in bruto:
            print("    AVISO: o <style> foi removido. Falta unfiltered_html.")

        if not ja_criada:
            # aponta a home ANTES de arquivar a antiga, sem janela sem front page
            if chave == "site":
                token = base64.b64encode(f"{cred['user']}:{cred['pass']}".encode()).decode()
                req = urllib.request.Request(
                    f"{cred['url']}/wp-json/wp/v2/settings", method="POST",
                    data=json.dumps({"show_on_front": "page",
                                     "page_on_front": nova["id"]}).encode(),
                    headers={"Authorization": f"Basic {token}",
                             "Content-Type": "application/json",
                             "User-Agent": "tadex-deploy"})
                urllib.request.urlopen(req, timeout=60)
                print(f"    -> pagina inicial agora e a {nova['id']}")
            # arquiva a antiga e assume o slug definitivo
            api(cred, f"pages/{id_antiga}", "POST",
                {"slug": f"{slug}-antiga", "status": "draft"})
            nova = api(cred, f"pages/{nova['id']}", "POST", {"slug": slug})
            print(f"    -> slug definitivo: /{nova['slug']}")

        print()

    if executar:
        FEITO.parent.mkdir(exist_ok=True)
        FEITO.write_text(json.dumps(novas, ensure_ascii=False, indent=2))


def reverter(cred, executar):
    if not ESTADO.exists():
        sys.exit("backup-wp/estado-original.json nao existe, nao da pra reverter.")
    orig = json.loads(ESTADO.read_text())
    novas = json.loads(FEITO.read_text()) if FEITO.exists() else {}
    mapa = {"site": "home", "contato": "fale-conosco",
            "privacidade": "politica-de-privacidade",
            "termos": "termos-de-uso", "coleta": "coleta"}

    print("REVERTER: as paginas novas viram rascunho e as antigas voltam ao ar.\n")
    for chave, dados in novas.items():
        o = orig[mapa[chave]]
        print(f"  {chave}: nova {dados['id']} -> rascunho | "
              f"antiga {o['id']} -> publish, slug '{o['slug']}'")
        if executar:
            api(cred, f"pages/{dados['id']}", "POST",
                {"status": "draft", "slug": f"{mapa[chave]}-novo"})
            api(cred, f"pages/{o['id']}", "POST",
                {"status": o["status"], "slug": o["slug"]})

    if executar and "site" in novas:
        token = base64.b64encode(f"{cred['user']}:{cred['pass']}".encode()).decode()
        req = urllib.request.Request(
            f"{cred['url']}/wp-json/wp/v2/settings", method="POST",
            data=json.dumps({"page_on_front": orig["home"]["id"]}).encode(),
            headers={"Authorization": f"Basic {token}",
                     "Content-Type": "application/json", "User-Agent": "tadex-deploy"})
        urllib.request.urlopen(req, timeout=60)
        print(f"\n  pagina inicial devolvida para a {orig['home']['id']}")


def main():
    executar = "--go" in sys.argv
    alvos = [a for a in sys.argv[1:] if not a.startswith("--")] or list(PAGINAS)
    if set(alvos) - PAGINAS.keys():
        sys.exit(f"pagina invalida. validas: {', '.join(PAGINAS)}")

    cred = credenciais()
    if not executar:
        print("MODO SIMULACAO. Nada sera gravado. Use --go para executar.\n")

    me = api(cred, "users/me?context=edit")
    caps = me.get("capabilities", {})
    print(f"conectado: {me.get('name')} ({', '.join(me.get('roles', []))})")
    print(f"unfiltered_html: {bool(caps.get('unfiltered_html'))}  "
          f"(precisa ser True para o CSS e o JS passarem)\n")

    if "--reverter" in sys.argv:
        reverter(cred, executar)
    else:
        publicar(cred, alvos, executar)

    print("Simulacao encerrada." if not executar else "Concluido.")


if __name__ == "__main__":
    main()
