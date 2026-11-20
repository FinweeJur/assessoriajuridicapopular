"""Alinha o topo e o rodapé da capa com as seções geradas."""
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "etl"))
sys.path.insert(0, RAIZ)

import importlib.util
spec = importlib.util.spec_from_file_location("monta_secoes", os.path.join(RAIZ, "etl", "monta-secoes.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
topo, rodape = mod.topo, mod.rodape  # noqa: E402

CAPA = os.path.join(RAIZ, "index.html")

with io.open(CAPA, encoding="utf-8") as f:
    t = f.read()

# Topo: troca o bloco <header class="topo">…</header>
t = re.sub(r'<header class="topo">.*?</header>', topo("acervo"), t, count=1, flags=re.S)

# Rodapé: troca de <footer até o fim do arquivo antes do <script>
t = re.sub(r'<footer class="rodape">.*?</footer>(?=\s*\n\s*<script)', rodape(), t, count=1, flags=re.S)

with io.open(CAPA, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)

print("capa: topo", t.count('class="topo"'), "| rodape", t.count('class="rodape"'))
