"""Completa a checagem de links das referências usando curl.

O urllib ficou preso em URLs antigas; o curl tem --max-time e resolve o restante
sem travar o lote. Retoma de `dados/referencias-links.json`, não repete o que já
foi conferido e grava a cada URL.
"""
import io
import json
import os
import subprocess
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
SAIDA = os.path.join(RAIZ, "dados", "referencias-links.json")
UA = "finweejur/github artur colito"
ESPERA = 0.8

dados = json.load(io.open(REF, encoding="utf-8"))
refs = dados.get("referencias", []) if isinstance(dados, dict) else dados
urls = sorted({r.get("url") for r in refs if r.get("url")})
try:
    links = json.load(io.open(SAIDA, encoding="utf-8"))
except Exception:
    links = {}

pendentes = [u for u in urls if u not in links]
print("URLs:", len(urls), "| já conferidas:", len(links), "| pendentes:", len(pendentes))

for i, url in enumerate(pendentes, 1):
    if i > 1:
        time.sleep(ESPERA)
    cmd = ["curl.exe", "-I", "-L", "--max-time", "8", "-A", UA, "-s", "-o", "NUL", "-w", "%{http_code}", url]
    try:
        status = subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        status = "000"
    if status in ("000", ""):
        cmd = ["curl.exe", "-L", "--max-time", "8", "--range", "0-0", "-A", UA, "-s", "-o", "NUL", "-w", "%{http_code}", url]
        try:
            status = subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
        except Exception:
            status = "000"
    try:
        codigo = int(status)
    except ValueError:
        codigo = None
    if isinstance(codigo, int) and 200 <= codigo < 400:
        acesso = "aberto"
    elif codigo in (401, 402, 403):
        acesso = "restrito"
    else:
        acesso = "morto_ou_instavel"
    links[url] = {"status": codigo, "url_final": url, "content_type": "", "erro": "" if codigo else "sem resposta", "acesso": acesso}
    io.open(SAIDA, "w", encoding="utf-8", newline="\n").write(json.dumps(links, ensure_ascii=False, indent=1) + "\n")
    print("%d/%d %s %s" % (i, len(pendentes), status, url[:110]))

print("total conferido:", len(links))
