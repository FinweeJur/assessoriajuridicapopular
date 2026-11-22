"""Monta um índice de recuperação (RAG) a partir dos posts do acervo.

Cada registro guarda título, autor, ano, temas e um trecho de até ~900 caracteres
do corpo do texto. O chatbot usa esse índice para devolver passagens com link,
sem gerar texto livre — o que reduz alucinação.
"""
import html
import io
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
SAIDA = os.path.join(RAIZ, "dados", "rag.json")
LIMITE = 900


def limpa(t):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def corpo(slug):
    p = os.path.join(RAIZ, slug + ".html")
    if not os.path.exists(p):
        return ""
    t = io.open(p, encoding="utf-8").read()
    m = re.search(r"<article[^>]*>(.*?)</article>", t, re.S)
    if not m:
        m = re.search(r"<main[^>]*>(.*?)</main>", t, re.S)
    texto = limpa(m.group(1) if m else t)
    return texto[:LIMITE]


def main():
    registros = json.load(io.open(INDICE, encoding="utf-8"))
    saida = []
    for r in registros:
        trecho = corpo(r["slug"])
        if not trecho:
            continue
        saida.append({
            "slug": r["slug"],
            "titulo": r.get("titulo", ""),
            "autor": r.get("autor", ""),
            "ano": r.get("ano", ""),
            "tema": r.get("tema", ""),
            "temas": r.get("temas", []),
            "texto": trecho,
        })
    json.dump(saida, io.open(SAIDA, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, separators=(",", ":"))
    print("rag:", len(saida), "posts |", os.path.getsize(SAIDA), "bytes")


if __name__ == "__main__":
    main()
