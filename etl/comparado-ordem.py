"""Ordem do comparado: direito crítico popular (1), Brasil (2), América Latina (3), mundo (4).

Idempotente: ignora seções repetidas pelo título.
"""
import io
import re

PAGINA = r"X:\DevCoder\assessoriajuridicapopular\assessoria-juridica-popular-no-mundo.html"

with io.open(PAGINA, encoding="utf-8") as f:
    t = f.read()

blocos = re.findall(r'    <section class="secao"[^>]*>.*?\n    </section>\n', t, re.S)
if len(blocos) < 6:
    raise SystemExit("secoes insuficientes: %d" % len(blocos))


def chave(b):
    if 'id="direito-critico"' in b:
        return "dcp"
    if "No Brasil:" in b:
        return "brasil"
    if "América Latina:" in b:
        return "latam"
    if "No mundo:" in b:
        return "mundo"
    if 'id="controle-popular"' in b:
        return "cp"
    if "O que isso muda" in b:
        return "muda"
    if "<h2>Referências</h2>" in b:
        return "refs"
    return None


mapa = {}
extras = []
for b in blocos:
    k = chave(b)
    if k is None:
        extras.append(b)
    elif k not in mapa:
        mapa[k] = b

faltando = [k for k in ("dcp", "brasil", "latam", "mundo", "cp", "muda", "refs") if k not in mapa]
if faltando:
    raise SystemExit("faltou: %s" % faltando)

dcp = mapa["dcp"].replace("1. Direito crítico popular", "1. Direito crítico popular", 1)
brasil = mapa["brasil"].replace("1. No Brasil", "2. No Brasil", 1)
latam = mapa["latam"].replace("2. América Latina", "3. América Latina", 1)
mundo = mapa["mundo"].replace("3. No mundo", "4. No mundo", 1)
cp = mapa["cp"].replace("5. O que existe no Controle Popular", "5. O que existe no Controle Popular", 1)

ordem = [dcp, brasil, latam, mundo, cp, mapa["muda"], mapa["refs"]] + extras

inicio = t.find(blocos[0])
fim = t.rfind(blocos[-1]) + len(blocos[-1])
t = t[:inicio] + "".join(ordem) + t[fim:]

velho = ("O que a literatura diz sobre assessoria jurídica popular, começando pelo Brasil, "
         "passando pela América Latina e chegando ao debate internacional.")
novo = ("O direito crítico popular em quatro perspectivas e, depois, o Brasil, a América Latina "
        "e o debate internacional.")
t = t.replace(velho, novo, 1)

with io.open(PAGINA, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)

print("ordem:")
for b in ordem:
    h = re.search(r"<h2>(.*?)</h2>", b, re.S)
    print(" -", re.sub("<[^>]+>", "", h.group(1)) if h else "?")
