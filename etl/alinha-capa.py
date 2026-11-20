"""Alinha o topo e o rodapé da home e do acervo com as seções."""
import importlib.util
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

for arquivo, ativo in [("index.html", "texto"), ("acervo.html", "acervo")]:
    caminho = os.path.join(RAIZ, arquivo)
    if not os.path.exists(caminho):
        continue
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    t = re.sub(r'<header class="topo">.*?</header>', ms.topo(ativo), t, count=1, flags=re.S)
    t = re.sub(r'<footer class="rodape">.*?</footer>', ms.rodape(), t, count=1, flags=re.S)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    print(arquivo, "topo", t.count('class="topo"'), "| rodape", t.count('class="rodape"'))
