"""Acrescenta o card do texto convidado na seção Memória e cultura."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
GERADOR = os.path.join(RAIZ, "etl", "monta-secoes.py")

BLOCO = """    <section class="secao" aria-labelledby="convidados">
      <div class="secao__cabeca"><h2 id="convidados">Texto convidado</h2>
      <p class="secao__nota">Fora do blog, com autoria e fonte</p></div>
      <ul class="lista-acervo">
        <li class="item"><a class="item__link" href="mistica.html">
          <span class="etiqueta">Mística · 2023</span>
          <h3>Mística: acúmulos, aprendizados, saberes e apontamentos iniciais</h3>
          <p>Texto dos movimentos populares, com citação de Ademar Bogo sobre o que a mística é na vida e na luta.</p>
          <span class="item__ficha">Militantes dos movimentos populares · 2023</span></a></li>
      </ul>
    </section>
"""

with io.open(GERADOR, encoding="utf-8") as f:
    g = f.read()

if "mistica.html" not in g:
    g = g.replace("  </div>\n</main>", BLOCO + "  </div>\n</main>", 1)
    with io.open(GERADOR, "w", encoding="utf-8", newline="\n") as f:
        f.write(g)

print("card da mística:", "mistica.html" in g)
