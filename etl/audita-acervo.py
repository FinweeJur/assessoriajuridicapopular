"""Audita a cobertura do acervo em relação ao sitemap do blog.

Lê o sitemap congelado em `docs/blog-sitemap-2026-11-22.xml`; se ele não
existir, baixa uma vez com User-Agent identificado (1,5 s de espera). Também
aceita `--sitemap` para um arquivo local. Serve para responder, em segundos:

- quantos posts o blog declara e quantos têm canonical local;
- quais URLs faltam, por ano;
- quais entradas do índice não têm canonical;
- se algum slug de seção colide com um post.

Uso:
  python etl/audita-acervo.py
  python etl/audita-acervo.py --csv docs/etl-lacunas.csv
  python etl/audita-acervo.py --sitemap docs/outro-sitemap.xml
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import tempfile
import time
import urllib.request
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP_PADRAO = os.path.join(RAIZ, "docs", "blog-sitemap-2026-11-22.xml")
INDICE = os.path.join(RAIZ, "_indice.json")
SECOES_PY = os.path.join(RAIZ, "etl", "monta-secoes.py")
BLOG = "assessoriajuridicapopular.blogspot.com"
UA = "finweejur/github artur colito"


def garante_sitemap(caminho):
    """Usa o sitemap congelado se existir; senão baixa uma vez, com UA."""
    if os.path.exists(caminho):
        return caminho
    print("sitemap local ausente; baixando o sitemap publico...")
    req = urllib.request.Request(
        "https://%s/sitemap.xml" % BLOG, headers={"User-Agent": UA}
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        dados = resp.read()
    destino = os.path.join(tempfile.gettempdir(), "ajp-sitemap.xml")
    io.open(destino, "wb").write(dados)
    time.sleep(1.5)
    return destino


def ano_da_url(url):
    m = re.search(r"/(\d{4})/", url)
    return m.group(1) if m else "?"


def posts_do_sitemap(caminho):
    xml = io.open(caminho, encoding="utf-8").read()
    return [
        u
        for u in re.findall(r"<loc>([^<]+)</loc>", xml)
        if re.search(r"/\d{4}/\d{2}/[^/]+\.html$", u)
    ]


def canonical_da_pagina(slug):
    caminho = os.path.join(RAIZ, slug + ".html")
    if not os.path.exists(caminho):
        return None
    t = io.open(caminho, encoding="utf-8").read()
    m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
    if not m or BLOG not in m.group(1):
        return None
    return m.group(1)


def slugs_de_secao():
    t = io.open(SECOES_PY, encoding="utf-8").read()
    i = t.find("SECOES = [")
    if i < 0:
        return set()
    bloco = t[i : t.find("]", i) + 1]
    return set(re.findall(r'\("([^"]+)"', bloco))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sitemap", default=SITEMAP_PADRAO)
    parser.add_argument("--csv", default="")
    args = parser.parse_args()

    try:
        args.sitemap = garante_sitemap(args.sitemap)
    except Exception as exc:
        print("nao foi possivel obter o sitemap:", exc)
        return 1
    if not os.path.exists(INDICE):
        print("indice nao encontrado:", INDICE)
        return 1

    sitemap = posts_do_sitemap(args.sitemap)
    indice = json.load(io.open(INDICE, encoding="utf-8"))
    canonicas = {}
    sem_canonical = []
    for item in indice:
        slug = item.get("slug", "")
        url = canonical_da_pagina(slug)
        if url:
            canonicas.setdefault(url, []).append(slug)
        else:
            sem_canonical.append(slug)

    faltando = [u for u in sitemap if u not in canonicas]
    repetidas = {u: s for u, s in canonicas.items() if len(s) > 1}
    secoes = slugs_de_secao()
    colisoes = sorted(set(item.get("slug", "") for item in indice) & secoes)

    blog_ano = Counter(ano_da_url(u) for u in sitemap)
    local_ano = Counter(ano_da_url(u) for u in canonicas)
    falta_ano = Counter(ano_da_url(u) for u in faltando)

    print("posts no sitemap :", len(sitemap))
    print("entradas no indice:", len(indice))
    print("paginas canonicas :", sum(len(v) for v in canonicas.values()))
    print("URLs canonicas unicas:", len(canonicas))
    print("faltando           :", len(faltando))
    print()
    print("ano | blog | local | falta")
    for a in sorted(set(blog_ano) | set(local_ano)):
        print("%s | %4d | %4d | %4d" % (a, blog_ano.get(a, 0), local_ano.get(a, 0), falta_ano.get(a, 0)))
    print()
    print("entradas sem canonical:", len(sem_canonical))
    for slug in sem_canonical:
        print("  -", slug)
    print("slugs de secao que colidem com post:", len(colisoes))
    for slug in colisoes:
        print("  !", slug)
    print("canonicals repetidos:", len(repetidas))
    for url, slugs in list(repetidas.items())[:10]:
        print("  !", url, "|", slugs)

    if args.csv:
        with io.open(args.csv, "w", encoding="utf-8", newline="\n") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["ano", "url"])
            for u in faltando:
                w.writerow([ano_da_url(u), u])
        print("csv:", args.csv)

    # Falha de propósito se a base não fecha; é o teste que o ETL precisa ter.
    if faltando or sem_canonical or colisoes or repetidas:
        print("\nRESULTADO: ACERVO INCOMPLETO — corrigir antes de dizer que esta completo.")
        return 2
    print("\nRESULTADO: cobertura completa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
