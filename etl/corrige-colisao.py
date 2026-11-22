"""Corrige a colisão dos posts homônimos "Assessoria Jurídica Popular".

- remove a página duplicada `assessoria-juridica-popular-4` (mesmo original da -3);
- gera o post da Rocinha (2010-04-26), que ficou sem página, com slug próprio;
- mantém `-2` (2010-01-08) e `-3` (2009-11-25).
"""
import importlib.util
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
STAGING = r"G:\Meu Drive\RENAP-AJP\staging-full\assessoria-juridica-popular-2.json"

spec = importlib.util.spec_from_file_location("mp", os.path.join(RAIZ, "etl", "monta-paginas.py"))
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

indice = json.load(io.open(INDICE, encoding="utf-8"))
antes = len(indice)
indice = [r for r in indice if r.get("slug") != "assessoria-juridica-popular-4"]
duplicado = os.path.join(RAIZ, "assessoria-juridica-popular-4.html")
if os.path.exists(duplicado):
    os.remove(duplicado)

post = json.load(io.open(STAGING, encoding="utf-8"))
if "cidade-segregada-favela-da-rocinha" not in {r.get("slug") for r in indice}:
    post["slug"] = "cidade-segregada-favela-da-rocinha"
    modelo = io.open(os.path.join(RAIZ, "_modelo.html"), encoding="utf-8").read()
    pagina, valores = mp.monta(post, modelo, indice)
    destino = os.path.join(RAIZ, post["slug"] + ".html")
    io.open(destino, "w", encoding="utf-8", newline="\n").write(pagina)
    indice.append({
        "slug": post["slug"],
        "titulo": post.get("titulo"),
        "data": post.get("data"),
        "autor": valores["AUTOR"],
        "resumo": post.get("resumo") or "",
        "temas": post.get("temas") or [],
        "tema": valores["TEMA"],
        "ano": valores["ANO"],
        "tipo": "",
        "tipo_rotulo": "",
        "palavras": [],
        "tema_principal": "",
        "redes": [],
    })
    print("gerado", destino)

indice.sort(key=lambda r: r.get("data") or "", reverse=True)
io.open(INDICE, "w", encoding="utf-8", newline="\n").write(
    json.dumps(indice, ensure_ascii=False, indent=1) + "\n"
)
print("indice:", antes, "->", len(indice))
