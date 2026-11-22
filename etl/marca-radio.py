"""Garante o painel de rádio e os scripts em todas as páginas que têm casca.

Algumas páginas de coleção e de autor nasceram sem o bloco do rádio; o menu “+”
aparecia, mas o botão Rádio não tinha o que abrir. Este injetor usa o markup
canônico de `radio-markup.html` e não toca em redirecionamentos.
"""
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKUP = io.open(os.path.join(RAIZ, "radio-markup.html"), encoding="utf-8").read().strip()
CSS = '<link rel="stylesheet" href="componentes/radio.css?v=4" />'
SCRIPTS = (
    '<script src="componentes/radio-dados.js?v=1" defer></script>\n'
    '<script src="componentes/radio.js?v=4" defer></script>'
)


def main():
    mudados = 0
    for nome in sorted(os.listdir(RAIZ)):
        if not nome.endswith(".html") or nome == "radio-markup.html":
            continue
        caminho = os.path.join(RAIZ, nome)
        t = io.open(caminho, encoding="utf-8").read()
        if 'http-equiv="refresh"' in t or "http-equiv='refresh'" in t:
            continue
        original = t
        if "componentes/radio.css" not in t:
            t = t.replace("</head>", CSS + "\n</head>", 1)
        if 'class="radio-flut"' not in t:
            alvo = re.search(r"<script src=", t)
            if alvo:
                t = t[: alvo.start()] + MARKUP + "\n" + t[alvo.start() :]
            else:
                t = t.replace("</body>", MARKUP + "\n</body>", 1)
        if "componentes/radio-dados.js" not in t:
            t = t.replace("</body>", SCRIPTS + "\n</body>", 1)
        if t != original:
            io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)
            mudados += 1
    print("paginas com radio:", mudados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
