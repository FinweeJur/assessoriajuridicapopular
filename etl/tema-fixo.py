"""Aplica o tema salvo antes do CSS carregar, em todas as páginas e geradores."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

CEDO = ("<script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');"
        "if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>")

# 1. Páginas prontas
n = 0
for nome in os.listdir(RAIZ):
    if not nome.endswith(".html"):
        continue
    caminho = os.path.join(RAIZ, nome)
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    if "data-tema-cedo" in t or "<head>" not in t:
        continue
    t = t.replace("<head>", "<head>\n  " + CEDO, 1)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    n += 1
print("html:", n)

# 2. Geradores e modelo, para as próximas reconstruções
alvos = [
    "_modelo.html",
    "etl/monta-secoes.py",
    "etl/monta-autores.py",
    "etl/monta-paginas.py",
    "etl/paginas-extras.py",
    "etl/paginas-caderno-comparado.py",
    "etl/corrige-revisao.py",
    "etl/corrige-e-antologia.py",
    "etl/glossario-linha.py",
    "etl/monta-mistica.py",
    "etl/sitemap-linha.py",
    "etl/menu-e-comparado.py",
]
m = 0
for rel in alvos:
    caminho = os.path.join(RAIZ, rel)
    if not os.path.exists(caminho):
        continue
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    if "data-tema-cedo" in t:
        continue
    if "<head>" in t:
        t = t.replace("<head>", "<head>\n  " + CEDO)
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
        m += 1
print("geradores:", m)
