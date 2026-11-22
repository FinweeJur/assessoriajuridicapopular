"""Adiciona o botão “Referências citadas neste texto” aos posts que têm refs.

O botão fica antes de `</article>` e aponta para o grupo `#fonte-<slug>` da
página `referencias-citadas.html`, onde cada obra tem “Disponível aqui” quando
o link foi confirmado.
"""
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")


def main():
    dados = json.load(io.open(REF, encoding="utf-8"))
    refs = dados.get("referencias", []) if isinstance(dados, dict) else dados
    por_fonte = {}
    for r in refs:
        s = r.get("fonte_slug")
        if s:
            por_fonte[s] = por_fonte.get(s, 0) + 1

    mudados = 0
    for slug, n in sorted(por_fonte.items()):
        caminho = os.path.join(RAIZ, slug + ".html")
        if not os.path.exists(caminho):
            continue
        t = io.open(caminho, encoding="utf-8").read()
        if "referencias-citadas.html#fonte-" in t:
            continue
        pos = t.rfind("</article>")
        if pos < 0:
            continue
        bloco = (
            '\n    <p class="referencias-post">'
            '<a class="botao secundario" href="referencias-citadas.html#fonte-%s">'
            'Referências citadas neste texto (%d)</a></p>\n' % (slug, n)
        )
        t = t[:pos] + bloco + t[pos:]
        io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)
        mudados += 1
    print("posts com botão de referências:", mudados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
