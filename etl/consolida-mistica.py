"""Consolida a Mística: subnav sem 'Memória e cultura' e antigo endereço vira 301."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

SUBNAV = ('<nav class="subnav" aria-label="Dentro de Mística"><span class="subnav__rotulo">Mística</span>'
          '<a href="mistica.html"%s>%sMística</a>'
          '<a href="cultura.html"%s>%sCultura</a>'
          '<a href="poemas.html"%s>%sPoemas e Caderno</a></nav>')


def monta(atual):
    def m(p):
        return (' aria-current="page"', "") if p == atual else ("", "")
    return SUBNAV % (m("mistica.html") + m("cultura.html") + m("poemas.html"))


for f, atual in (("mistica.html", "mistica.html"),
                 ("cultura.html", "cultura.html"),
                 ("poemas.html", "poemas.html")):
    p = os.path.join(RAIZ, f)
    t = io.open(p, encoding="utf-8").read()
    t2 = re.sub(r'<nav class="subnav" aria-label="Dentro de Mística">.*?</nav>', monta(atual), t, count=1, flags=re.S)
    if t2 == t and 'aria-label="Dentro de Mística"' not in t:
        print("aviso: sem subnav em", f)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
    print("subnav:", f)

# antigo endereço -> âncora na Mística
REDIR = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex" />
  <meta http-equiv="refresh" content="0; url=mistica.html#memoria-e-cultura" />
  <link rel="canonical" href="mistica.html#memoria-e-cultura" />
  <title>Mística — AJP</title>
  <style>body{font-family:system-ui,sans-serif;background:#0d0b08;color:#f7f0e6;padding:2rem;line-height:1.5}a{color:#ff9f1c}</style>
</head>
<body>
  <p>Esta página agora faz parte da <a href="mistica.html#memoria-e-cultura">Mística</a>.</p>
</body>
</html>
"""
io.open(os.path.join(RAIZ, "memoria-e-cultura.html"), "w", encoding="utf-8", newline="\n").write(REDIR)
print("memoria-e-cultura.html -> redireciona para mistica.html#memoria-e-cultura")

# config do gerador de subnavs
g = os.path.join(RAIZ, "etl", "marca-subnavs.py")
t = io.open(g, encoding="utf-8").read()
inicio = t.find('"cultura.html": ("Mística", [')
fim = t.find('"biblioteca.html": ("Biblioteca", [')
if inicio > 0 and fim > inicio:
    novo = '''"cultura.html": ("Mística", [
        ("mistica.html", "← Mística", False),
        ("cultura.html", "Cultura", True),
        ("poemas.html", "Poemas e Caderno", False),
    ]),
    "poemas.html": ("Mística", [
        ("mistica.html", "← Mística", False),
        ("cultura.html", "Cultura", False),
        ("poemas.html", "Poemas e Caderno", True),
    ]),
    "mistica.html": ("Mística", [
        ("mistica.html", "Mística", True),
        ("cultura.html", "Cultura", False),
        ("poemas.html", "Poemas e Caderno", False),
    ]),

    '''
    t = t[:inicio] + novo + t[fim:]
    io.open(g, "w", encoding="utf-8", newline="\n").write(t)
    print("marca-subnavs.py atualizado")
