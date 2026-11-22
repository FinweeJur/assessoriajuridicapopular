"""Checa os links explícitos das referências extraídas.

Não baixa conteúdo: faz HEAD (ou GET de 1 byte quando o servidor recusa HEAD)
e guarda status, URL final e content-type. 1,2 s entre requisições; UA
identificado. O resultado é `dados/referencias-links.json`.
"""
import io
import json
import os
import time
import urllib.error
import urllib.request

UA = "finweejur/github artur colito"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
SAIDA = os.path.join(RAIZ, "dados", "referencias-links.json")
ESPERA = 1.2

dados = json.load(io.open(REF, encoding="utf-8"))
refs = dados.get("referencias", dados) if isinstance(dados, dict) else dados
urls = sorted({r.get("url") for r in refs if r.get("url")})
print("URLs únicas:", len(urls))

resultado = {}
for i, url in enumerate(urls, 1):
    if i > 1:
        time.sleep(ESPERA)
    item = {"status": None, "url_final": url, "content_type": "", "erro": ""}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                item["status"] = resp.status
                item["url_final"] = resp.geturl()
                item["content_type"] = resp.headers.get("content-type", "")
                resp.read(1)
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 405, 429):
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Range": "bytes=0-0"})
                with urllib.request.urlopen(req, timeout=25) as resp:
                    item["status"] = resp.status
                    item["url_final"] = resp.geturl()
                    item["content_type"] = resp.headers.get("content-type", "")
                    resp.read(1)
            else:
                item["status"] = exc.code
                item["erro"] = str(exc)
    except Exception as exc:
        item["erro"] = str(exc)[:200]
    status = item["status"]
    item["acesso"] = "aberto" if isinstance(status, int) and 200 <= status < 400 else (
        "restrito" if status in (401, 402, 403) else "morto_ou_instavel")
    resultado[url] = item
    print("%3d/%d %s %s" % (i, len(urls), status, url[:100]))

io.open(SAIDA, "w", encoding="utf-8", newline="\n").write(
    json.dumps(resultado, ensure_ascii=False, indent=1) + "\n"
)
print("salvo", SAIDA)
