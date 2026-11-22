"""Marca cada post com as redes/organizações citadas: RENAP, IPDMS e RENAJU/AJUPs."""
import html
import io
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
DADOS = os.path.join(RAIZ, "dados")

PADROES = {
    "renap": [
        r"\brenap\b",
        r"rede nacional de advogad[oa]s? e advogad[oa]s? populares",
        r"rede nacional de advogad",
    ],
    "ipdms": [
        r"\bipdms\b",
        r"instituto de pesquisa (?:em )?direito e movimentos sociais",
    ],
    "renaju-ajup": [
        r"\brenaju\b", r"\berenaju\b",
        r"\bajups?\b", r"\bsajus?\b", r"\bsajup\b",
        r"\bnajups?\b", r"\bgajups?\b", r"\bmajup\b", r"\bcoraje\b",
        r"assessoria juridica universitaria",
        r"assessoria juridica popular universitaria",
        r"nucleo de assessoria juridica",
    ],
}


def sem_acento(t):
    return unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode().lower()


def corpo(slug):
    p = os.path.join(RAIZ, slug + ".html")
    if not os.path.exists(p):
        return ""
    t = io.open(p, encoding="utf-8").read()
    m = re.search(r'<div[^>]*class="[^"]*\bcorpo\b[^"]*"[^>]*>(.*?)</div>\s*(?:<section|<footer|</article>)', t, re.S)
    s = m.group(1) if m else t
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<noscript\b.*?</noscript>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<(nav|aside|footer|header)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return sem_acento(html.unescape(s))


def main():
    registros = json.load(io.open(INDICE, encoding="utf-8"))
    contagem = {k: 0 for k in PADROES}
    for r in registros:
        alvo = sem_acento(" ".join([
            r.get("titulo") or "", r.get("resumo") or "",
            " ".join(r.get("temas") or []), corpo(r["slug"]),
        ]))
        redes = []
        for rede, padroes in PADROES.items():
            if any(re.search(p, alvo, re.I) for p in padroes):
                redes.append(rede)
                contagem[rede] += 1
        r["redes"] = redes
    io.open(INDICE, "w", encoding="utf-8", newline="\n").write(
        json.dumps(registros, ensure_ascii=False, indent=1)
    )
    resumo = {r["slug"]: r.get("redes", []) for r in registros}
    io.open(os.path.join(DADOS, "redes.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(resumo, ensure_ascii=False, indent=1)
    )
    print("redes:", contagem)
    print("com alguma rede:", sum(1 for r in registros if r.get("redes")))
    print("com RENAJU/AJUP:", sum(1 for r in registros if "renaju-ajup" in (r.get("redes") or [])))


if __name__ == "__main__":
    main()
