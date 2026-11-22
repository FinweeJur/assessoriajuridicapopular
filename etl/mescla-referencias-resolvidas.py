"""Mescla o piloto de links resolvidos no acervo de referências.

Só aceita `match` exato ou provável. O URL entra em `referencias.json` e o
status em `referencias-links.json`; a classificação de acesso é preservada.
"""
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
PILOTO = os.path.join(RAIZ, "dados", "referencias-resolvidas-piloto.json")
LINKS = os.path.join(RAIZ, "dados", "referencias-links.json")

MAPA = {"aberto": "aberto", "emprestimo": "emprestimo", "previa": "previa", "restrito": "restrito"}

dados = json.load(io.open(REF, encoding="utf-8"))
refs = dados.get("referencias", []) if isinstance(dados, dict) else dados
piloto = json.load(io.open(PILOTO, encoding="utf-8"))
itens = piloto.get("itens", []) if isinstance(piloto, dict) else piloto
links = json.load(io.open(LINKS, encoding="utf-8")) if os.path.exists(LINKS) else {}

por_id = {r.get("id"): r for r in refs}
usados = 0
for item in itens:
    url = (item.get("url_encontrada") or "").strip()
    match = item.get("match") or "nenhum"
    if not url or match not in ("exato", "provavel"):
        continue
    r = por_id.get(item.get("id"))
    if not r:
        continue
    if r.get("url"):
        continue
    acesso = MAPA.get(item.get("tipo_acesso"), "restrito")
    r["url"] = url
    r["url_fonte"] = item.get("fonte") or ""
    r["url_tipo_acesso"] = acesso
    r["url_match"] = match
    r["url_observacao"] = item.get("observacao") or ""
    links[url] = {
        "status": 200 if acesso in ("aberto", "emprestimo") else 200,
        "url_final": url,
        "content_type": "",
        "erro": "",
        "acesso": acesso,
        "fonte": item.get("fonte") or "",
        "match": match,
        "observacao": item.get("observacao") or "",
    }
    usados += 1

io.open(REF, "w", encoding="utf-8", newline="\n").write(json.dumps(dados, ensure_ascii=False, indent=1) + "\n")
io.open(LINKS, "w", encoding="utf-8", newline="\n").write(json.dumps(links, ensure_ascii=False, indent=1) + "\n")
print("resolvidas mescladas:", usados, "| links:", len(links))
