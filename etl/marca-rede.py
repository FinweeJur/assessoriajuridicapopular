"""Coloca "Rede" na navegação principal e no rodapé de todas as páginas.

A porta `rede.html` reúne Quem somos, Como postar, Blogues parceiros,
Entidades, Movimentos, Mapeamento, Colunas e Bibliotecas. O link entra depois
de Biblioteca; no celular, o menu hambúrguer lê o mesmo `.topo__links`.
"""
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV = re.compile(r'(<nav class="topo__links"[^>]*>.*?)(</nav>)', re.S)
BIB = '<a href="biblioteca.html"'
RODAPE = re.compile(r'(<li><a href="biblioteca\.html">Biblioteca</a></li>)')


def main():
    mudados = 0
    for nome in sorted(os.listdir(RAIZ)):
        if not nome.endswith(".html") or nome in ("radio-markup.html",):
            continue
        caminho = os.path.join(RAIZ, nome)
        t = io.open(caminho, encoding="utf-8").read()
        original = t
        if 'href="rede.html"' not in t:
            m = NAV.search(t)
            if m:
                bloco = m.group(1)
                if BIB in bloco:
                    extra = '<a href="rede.html"%s>Rede</a>' % (
                        ' aria-current="page"' if nome == "rede.html" else "")
                    # insere depois do fechamento do link da Biblioteca
                    pos = bloco.find("</a>", bloco.find(BIB))
                    if pos > -1:
                        pos += 4
                        bloco = bloco[:pos] + "\n      " + extra + bloco[pos:]
                    t = t[: m.start(1)] + bloco + t[m.end(1) :]
        if 'href="rede.html"' not in t:
            # fallback: páginas com topo em outro formato
            pass
        if RODAPE.search(t) and 'rede.html">Rede e parceiros' not in t:
            t = RODAPE.sub(r'\1\n        <li><a href="rede.html">Rede e parceiros</a></li>', t, count=1)
        if t != original:
            io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)
            mudados += 1
    print("paginas com Rede:", mudados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
