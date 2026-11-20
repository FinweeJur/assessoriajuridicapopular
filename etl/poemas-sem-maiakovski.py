"""Remove os poemas de Maiakovski: autor em domínio público, traduções protegidas."""
import io
import json
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

p = RAIZ + r"\poemas.html"
t = io.open(p, encoding="utf-8").read()

t, n = re.subn(r'    <section class="poeta" aria-labelledby="maiakovski">.*?\n    </section>\n',
               "", t, count=1, flags=re.S)
print("secao maiakovski removida:", n)

t = re.sub(r'\s*<li><a href="#maiakovski">.*?</li>', "", t, count=1)
t = t.replace("151 poemas transcritos", "135 poemas transcritos")
t = t.replace("Cento e cinquenta e um poemas", "Cento e trinta e cinco poemas")
t = t.replace("36 poemas em domínio público e 115 por autorização",
              "20 poemas em domínio público e 115 por autorização")

nota = ('<p><b>Domínio público, tradução protegida:</b> Vladimir Maiakovski (1893–1930) está em '
        'domínio público, mas as traduções do caderno são de Haroldo e Augusto de Campos, Boris '
        'Schnaiderman e outros tradutores, com direitos próprios. Sem autorização dos tradutores, '
        'os 16 poemas ficam fora.</p>\n      ')
marcador = "<p><b>Sem data de falecimento no caderno:</b>"
if "Vladimir Maiakovski (1893–1930) está em" not in t:
    t = t.replace(marcador, nota + marcador, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("maiakovski restante:", t.count("Maiakovski"))
print("figuras:", t.count('figure class="cartao citacao"'))

p = RAIZ + r"\dados\poemas.json"
d = json.loads(io.open(p, encoding="utf-8").read())
antes = len(d)
d = [x for x in d if (x.get("autor") or "") != "Vladimir Maiakovski"]
io.open(p, "w", encoding="utf-8", newline="\n").write(
    json.dumps(d, ensure_ascii=False, indent=1))
print("json:", antes, "->", len(d))
