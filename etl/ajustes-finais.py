"""Últimos ajustes: bento em duas colunas e anos nas recomendações."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# CSS
p = os.path.join(RAIZ, "acervo.css")
css = io.open(p, encoding="utf-8").read()
extra = """
/* Bento em duas colunas na meia janela */
@media (min-width: 561px) and (max-width: 1100px) {
  .bento { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
  .bento .bento__item { grid-column: auto !important; grid-row: auto !important; }
  .bento .bento__item--grande { grid-column: span 2 !important; }
  .bento .bento__item--largo { grid-column: span 2 !important; }
}
"""
if "Bento em duas colunas na meia janela" not in css:
    io.open(p, "w", encoding="utf-8", newline="\n").write(css.rstrip() + "\n" + extra)
print("bento 2 col ok")

# Recomendações
p = os.path.join(RAIZ, "recomendacoes.html")
t = io.open(p, encoding="utf-8").read()
for velho, novo in [
    ("<b>A montanha é mais que uma imensa estepe verde</b>, de Omar Cabezas (Expressão Popular)",
     "<b>A montanha é mais que uma imensa estepe verde</b>, de Omar Cabezas (Expressão Popular, 1982)"),
    ("<b>Mayombe</b>, de Pepetela", "<b>Mayombe</b>, de Pepetela (1980)"),
    ("<b>Torto Arado</b>, de Itamar Vieira Junior", "<b>Torto Arado</b>, de Itamar Vieira Junior (2019)"),
    ("<b>Judas e o Messias Negro</b> (Netflix)", "<b>Judas e o Messias Negro</b> (2021, Netflix)"),
    ("<b>Marighella</b> — resistência à ditadura militar.", "<b>Marighella</b> (2019) — resistência à ditadura militar."),
    ("<b>BaianaSystem</b> — “Sulamericano”.", "<b>BaianaSystem</b> — “Sulamericano” (2019)."),
    ("<b>Calle 13</b> — “Latinoamérica”.", "<b>Calle 13</b> — “Latinoamérica” (2010)."),
    ("<b>Racionais MC’s</b> — “Mil faces de um homem leal”.", "<b>Racionais MC’s</b> — “Mil faces de um homem leal” (2012)."),
]:
    t = t.replace(velho, novo, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("recomendacoes anos:", t.count("1982"), t.count("(2019)"))

# Versão do CSS
n = 0
for nome in os.listdir(RAIZ):
    if not nome.endswith(".html"):
        continue
    caminho = os.path.join(RAIZ, nome)
    t = io.open(caminho, encoding="utf-8").read()
    novo = re.sub(r"acervo\.css\?v=\d+", "acervo.css?v=48", t)
    novo = re.sub(r"reveal\.css\?v=\d+", "reveal.css?v=48", novo)
    if novo != t:
        io.open(caminho, "w", encoding="utf-8", newline="\n").write(novo)
        n += 1
print("v42:", n)
