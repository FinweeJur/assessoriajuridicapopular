"""Preenche o índice do Caderno com o sumário do PDF, sem reproduzir os poemas."""
import glob
import html
import io
import re

from pypdf import PdfReader

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
PAGINA = RAIZ + r"\caderno-de-poesias.html"

pdf = glob.glob(RAIZ + r"\fontes-textos\Poesias*\Poesias*\CADERNO DE POESIAS - CMM.pdf")[0]
leitor = PdfReader(pdf)

partes = []
for i in range(1, 8):
    texto = leitor.pages[i].extract_text() or ""
    texto = texto.replace("Sumário", "", 1).strip()
    partes.append(texto)
sumario = "\n\n".join(partes)

bloco = ('<details class="sumario-caderno">\n'
         '      <summary>Ver o sumário completo do caderno</summary>\n'
         '      <pre>%s</pre>\n'
         '    </details>' % html.escape(sumario))

with io.open(PAGINA, encoding="utf-8") as f:
    t = f.read()

t = re.sub(r'<ul class="indice-poetas"></ul>', bloco, t, count=1)
t = re.sub(r'<details class="sumario-caderno">.*?</details>', bloco, t, count=1, flags=re.S)

with io.open(PAGINA, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)

print("sumario:", len(sumario), "caracteres")
print("detalhes:", t.count('class="sumario-caderno"'))
