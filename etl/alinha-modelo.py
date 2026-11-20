"""Alinha a página de texto (modelo) ao topo e rodapé das seções."""
import importlib.util
import io
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

MODELO = os.path.join(RAIZ, "_modelo.html")
with io.open(MODELO, encoding="utf-8") as f:
    t = f.read()

t = re.sub(r'<header class="topo">.*?</header>', mod.topo("texto"), t, count=1, flags=re.S)
t = re.sub(r'<footer class="rodape">.*?</footer>', mod.rodape(), t, count=1, flags=re.S)

# Ligar o CSS novo e o reveal.
if "acervo.css" in t and "reveal.css" not in t:
    t = t.replace('<link rel="stylesheet" href="acervo.css" />',
                  '<link rel="stylesheet" href="acervo.css" />\n  <link rel="stylesheet" href="reveal.css" />', 1)
if "reveal.js" not in t:
    t = t.replace("</body>", '<script src="reveal.js" defer></script>\n</body>', 1)

with io.open(MODELO, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)

print("modelo: topo", t.count('class="topo"'), "| rodape", t.count('class="rodape"'),
      "| reveal", "reveal.js" in t)
