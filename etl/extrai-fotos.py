"""Extrai imagens do blogue a partir dos posts locais e classifica por contexto."""
import html
import io
import json
import os
import re
from collections import Counter

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
SAIDA = r"X:\DevCoder\assessoriajuridicapopular\dados\fotos-blog.json"

PAGINAS_SISTEMA = {
    "index.html", "acervo.html", "blog.html", "autores.html", "biblioteca.html",
    "cultura.html", "formacao.html", "memoria.html", "mistica.html", "rede.html",
    "ia.html", "referencias-citadas.html", "poemas.html", "mapeamento-ajups.html",
    "glossario.html", "linha-do-tempo.html", "colunistas.html", "entidades-parceiras.html",
    "blogues-parceiros.html", "mapeamento.html", "citacoes.html", "indice.html",
    "_modelo.html", "poesia-critica-do-direito.html",
}

idx = json.load(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8"))
meta = {r["slug"] + ".html": r for r in idx}

RE_IMG = re.compile(r'<img[^>]+src="([^"]+)"[^>]*>', re.I)
RE_ALT = re.compile(r'alt="([^"]*)"', re.I)

itens = []
for nome in sorted(os.listdir(RAIZ)):
    if not nome.endswith(".html") or nome in PAGINAS_SISTEMA:
        continue
    reg = meta.get(nome)
    if not reg:
        continue
    try:
        t = io.open(os.path.join(RAIZ, nome), encoding="utf-8").read()
    except Exception:
        continue
    # só o corpo do post
    i = t.find("<main")
    corpo = t[i:] if i > 0 else t
    for m in RE_IMG.finditer(corpo):
        src = html.unescape(m.group(1))
        if not re.search(r"(googleusercontent|bp\.blogspot|blogspot\.com)", src):
            continue
        alt_m = RE_ALT.search(m.group(0))
        alt = html.unescape(alt_m.group(1)) if alt_m else ""
        itens.append({
            "post": nome,
            "titulo": reg.get("titulo"),
            "data": reg.get("data"),
            "tema": reg.get("tema_principal"),
            "tipo": reg.get("tipo"),
            "src": src,
            "alt": alt,
        })

# dedupe por ID do Blogger (parte antes do /sNNN/)
def chave(src):
    m = re.search(r"/(?:s\d+|w\d+|h\d+)[^/]*/([^/]+)$", src)
    if m:
        return m.group(1)
    return src.split("?")[0].rsplit("/", 1)[-1]

vistos = {}
for it in itens:
    k = chave(it["src"])
    if k not in vistos:
        it["chave"] = k
        vistos[k] = it

unicos = list(vistos.values())
json.dump({"total_ocorrencias": len(itens), "unicas": len(unicos), "fotos": unicos},
          io.open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("ocorrências:", len(itens), "| únicas:", len(unicos))
print("por tipo de post:", Counter(u["tipo"] for u in unicos).most_common())
print("por tema:", Counter(u["tema"] for u in unicos).most_common())
eventos = [u for u in unicos if (u["tipo"] or "").lower() in ("evento",)
           or re.search(r"encontro|semin[áa]rio|jornada|oficina|curso|erenaju|erenap|assembleia|marcha|ato\b|festa|mostra|congresso",
                        (u["titulo"] or ""), re.I)]
print("candidatas a evento:", len(eventos))
