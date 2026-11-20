"""Poemas do blog na página de poemas, com o aviso legal resumido no fim."""
import html
import io
import json
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
PAGINA = RAIZ + r"\poemas.html"

with io.open(PAGINA, encoding="utf-8") as f:
    t = f.read()

if 'id="poesia-no-blog"' in t:
    print("poesia do blog ja esta na pagina")
    raise SystemExit(0)

registros = json.loads(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8").read())
poesias = [r for r in registros if r.get("tipo") == "poesia"]
poesias.sort(key=lambda r: r.get("data") or "", reverse=True)

cartoes = []
for r in poesias:
    ano = (r.get("data") or "")[:4]
    cartoes.append('''        <a class="cartao destaque" href="%s.html">
          <span class="etiqueta">Poesia · %s</span>
          <h3>%s</h3>
          <p>%s</p>
        </a>''' % (r["slug"], html.escape(ano), html.escape(r.get("titulo") or ""),
                   html.escape(r.get("autor") or "Sem autoria")))

SECAO = '''    <section class="secao" id="poesia-no-blog" aria-labelledby="poesia-blog">
      <div class="secao__cabeca"><h2 id="poesia-blog">Poesia no blog</h2>
      <p class="secao__nota">%d posts com poemas, versos e textos de poesia</p></div>
      <p>Além do caderno, o blog publicou poemas soltos, odes, cantigas e homenagens.
      Cada cartão abre o texto completo, com autor, data e link para o original.</p>
      <details class="poesia-blog">
        <summary>Ver os %d posts de poesia</summary>
        <div class="grade-3">
%s
        </div>
      </details>
    </section>

''' % (len(poesias), len(poesias), "\n".join(cartoes))

# 1. Remove o aviso longo do topo
t = re.sub(r'\s*<p class="aviso-lote"><b>Critério legal\.</b>.*?</p>\n', "\n", t, count=1, flags=re.S)

# 2. Remove a seção "Quem ficou de fora"
t = re.sub(r'\s*<section class="secao" aria-labelledby="fora">.*?\n    </section>\n', "\n", t, count=1, flags=re.S)

# 3. Insere a poesia do blog antes da Referência
marcador = '    <section class="secao" aria-labelledby="referencia">'
if marcador not in t:
    raise SystemExit("nao achei a referencia")
t = t.replace(marcador, SECAO + marcador, 1)

# 4. Aviso curto no fim, depois do compartilhar
AVISO = '''    <p class="aviso-lote" id="retirada"><b>Critério legal e retirada.</b> Entram os autores
    falecidos até 1955 (Lei 9.610/98, art. 41) e os publicados por autorização do responsável pelo
    site. Poemas de autores com direitos vigentes e traduções protegidas ficam de fora. Em caso de
    retirada, escreva para <a href="mailto:artur.colito@ufvjm.edu.br">artur.colito@ufvjm.edu.br</a>.</p>
'''
t = t.replace("    </section>\n  \n</article>", "    </section>\n\n" + AVISO + "</article>", 1)
if 'id="retirada"' not in t:
    # fallback: antes do fechamento do article
    t = t.replace("</article>", AVISO + "</article>", 1)

# 5. Lead e descrição
t = t.replace(
    "135 poemas transcritos do caderno organizado por Cleber Mori: autores em\n"
    "      domínio público no Brasil e autores publicados por autorização do responsável pelo site.",
    "135 poemas do caderno organizado por Cleber Mori e uma porta para os 42 posts de poesia do\n"
    "      blog: autores em domínio público no Brasil e autores publicados por autorização do\n"
    "      responsável pelo site.")
t = t.replace("Cento e trinta e cinco poemas do Caderno de Poesias",
              "Cento e trinta e cinco poemas do Caderno de Poesias e 42 posts de poesia do blog")

with io.open(PAGINA, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)

print("poesias do blog:", len(poesias))
print("secao:", 'id="poesia-no-blog"' in t, "| aviso curto:", 'id="retirada"' in t)
print("fora removido:", 'aria-labelledby="fora"' not in t)
