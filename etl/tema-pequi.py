"""Tema pequi padrão em todas as páginas."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
n = 0
for nome in os.listdir(RAIZ):
    if not nome.endswith(".html"):
        continue
    caminho = os.path.join(RAIZ, nome)
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    novo = t.replace('data-theme="pequi"', 'data-theme="pequi"')
    novo = novo.replace('<option value="light" selected>', '<option value="light">')
    if '<option value="pequi" selected>' not in novo:
        novo = novo.replace('<option value="pequi">', '<option value="pequi" selected>', 1)
    if novo != t:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(novo)
        n += 1
print("paginas:", n)
