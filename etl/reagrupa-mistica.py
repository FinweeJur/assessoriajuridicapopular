"""Reagrupa Cultura/Poemas/Memória e cultura dentro da porta Mística."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

SUBNAV = ('<nav class="subnav" aria-label="Dentro de Mística"><span class="subnav__rotulo">Mística</span>'
          '<a href="mistica.html"%s>%sMística</a>'
          '<a href="memoria-e-cultura.html"%s>%sMemória e cultura</a>'
          '<a href="cultura.html"%s>%sCultura</a>'
          '<a href="poemas.html"%s>%sPoemas e Caderno</a></nav>')


def subnav(atual):
    def marca(pagina):
        return (' aria-current="page"', "") if pagina == atual else ("", "")
    return SUBNAV % (marca("mistica.html") + marca("memoria-e-cultura.html")
                     + marca("cultura.html") + marca("poemas.html"))


for f, atual in (("mistica.html", "mistica.html"),
                 ("poemas.html", "poemas.html"),
                 ("cultura.html", "cultura.html"),
                 ("memoria-e-cultura.html", "memoria-e-cultura.html")):
    p = os.path.join(RAIZ, f)
    if not os.path.exists(p):
        print("falta", f)
        continue
    t = io.open(p, encoding="utf-8").read()
    novo = subnav(atual)
    if 'aria-label="Dentro de Cultura"' in t:
        t = re.sub(r'<nav class="subnav" aria-label="Dentro de Cultura">.*?</nav>', novo, t, count=1, flags=re.S)
    elif 'aria-label="Dentro de Mística"' in t:
        t = re.sub(r'<nav class="subnav" aria-label="Dentro de Mística">.*?</nav>', novo, t, count=1, flags=re.S)
    else:
        # insere depois da migalha
        m = re.search(r"</nav>\s*(<article|<section)", t)
        if m:
            t = t[:m.start() + len("</nav>")] + "\n  " + novo + t[m.start() + len("</nav>"):]
        else:
            print("sem ponto de inserção:", f)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("subnav atualizado:", f)

# configuração do gerador
g = os.path.join(RAIZ, "etl", "marca-subnavs.py")
t = io.open(g, encoding="utf-8").read()
novo_cfg = '''"cultura.html": ("Mística", [
        ("mistica.html", "← Mística", False),
        ("memoria-e-cultura.html", "Memória e cultura", False),
        ("cultura.html", "Cultura", True),
        ("poemas.html", "Poemas e Caderno", False),
    ]),
    "poemas.html": ("Mística", [
        ("mistica.html", "← Mística", False),
        ("memoria-e-cultura.html", "Memória e cultura", False),
        ("cultura.html", "Cultura", False),
        ("poemas.html", "Poemas e Caderno", True),
    ]),
    "mistica.html": ("Mística", [
        ("mistica.html", "Mística", True),
        ("memoria-e-cultura.html", "Memória e cultura", False),
        ("cultura.html", "Cultura", False),
        ("poemas.html", "Poemas e Caderno", False),
    ]),
    "memoria-e-cultura.html": ("Mística", [
        ("mistica.html", "← Mística", False),
        ("memoria-e-cultura.html", "Memória e cultura", True),
        ("cultura.html", "Cultura", False),
        ("poemas.html", "Poemas e Caderno", False),
    ]),'''

inicio = t.find('"cultura.html": ("Cultura", [')
fim = t.find('"biblioteca.html": ("Biblioteca", [')
if inicio > 0 and fim > inicio:
    t = t[:inicio] + novo_cfg + "\n    " + t[fim:]
    io.open(g, "w", encoding="utf-8", newline="\n").write(t)
    print("marca-subnavs.py atualizado")
else:
    print("não localizei o bloco no gerador")
