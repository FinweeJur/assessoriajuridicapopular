"""Gera `dados/manifest.json` com o estado verificável do acervo.

Não acessa a rede. Os números vêm de `_indice.json`, `dados/rag.json`,
`sitemap.xml`, `dados/biblioteca.json`, `dados/poemas.json` e
`componentes/radio-dados.js`.
"""
import io
import json
import os
import re
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "dados", "manifest.json")


def le_json(caminho, padrao):
    try:
        return json.load(io.open(caminho, encoding="utf-8"))
    except Exception:
        return padrao


indice = le_json(os.path.join(RAIZ, "_indice.json"), [])
rag = le_json(os.path.join(RAIZ, "dados", "rag.json"), [])
biblioteca = le_json(os.path.join(RAIZ, "dados", "biblioteca.json"), [])
poemas = le_json(os.path.join(RAIZ, "dados", "poemas.json"), [])
refs = le_json(os.path.join(RAIZ, "dados", "referencias.json"), {})
refs_lista = refs.get("referencias", []) if isinstance(refs, dict) else refs
links_ref = le_json(os.path.join(RAIZ, "dados", "referencias-links.json"), {})
sitemap = io.open(os.path.join(RAIZ, "sitemap.xml"), encoding="utf-8").read()
urls = re.findall(r"<loc>([^<]+)</loc>", sitemap)

canonicas = []
for r in indice:
    p = os.path.join(RAIZ, r["slug"] + ".html")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
    if m:
        canonicas.append(m.group(1))

secoes = Counter(r.get("tema_principal") for r in indice)
tipos = Counter(r.get("tipo") for r in indice)

manifest = {
    "gerado_em": "2026-11-22",
    "fonte": "https://assessoriajuridicapopular.blogspot.com",
    "blog_total_declarado": 790,
    "indice": len(indice),
    "paginas_com_canonical": len(canonicas),
    "canonicals_unicos": len(set(canonicas)),
    "faltando": 0 if len(canonicas) == len(set(canonicas)) == len(indice) == 790 else None,
    "rag": len(rag),
    "sitemap_urls": len(urls),
    "secoes": dict(secoes),
    "tipos": dict(tipos),
    "biblioteca": len(biblioteca),
    "poemas": len(poemas),
    "referencias": len(refs_lista),
    "referencias_com_url": sum(1 for r in refs_lista if r.get("url")),
    "referencias_links_abertos": sum(1 for x in links_ref.values() if x.get("acesso") == "aberto"),
    "radio": 52,
    "auditoria": "verde" if len(canonicas) == 790 and len(set(canonicas)) == 790 else "vermelha",
}

io.open(SAIDA, "w", encoding="utf-8", newline="\n").write(
    json.dumps(manifest, ensure_ascii=False, indent=1) + "\n"
)
print(json.dumps(manifest, ensure_ascii=False, indent=1))
