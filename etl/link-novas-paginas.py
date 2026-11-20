"""Cards das páginas novas na seção Memória e cultura; comparado no menu."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
GERADOR = os.path.join(RAIZ, "etl", "monta-secoes.py")

CARDS = """    <section class="secao" aria-labelledby="convidados">
      <div class="secao__cabeca"><h2 id="convidados">Textos convidados</h2>
      <p class="secao__nota">Fora do blog, com autoria e fonte</p></div>
      <ul class="lista-acervo">
        <li class="item"><a class="item__link" href="mistica.html">
          <span class="etiqueta">Mística · 2023</span>
          <h3>Mística: acúmulos, aprendizados, saberes</h3>
          <p>Texto dos movimentos populares, com citação de Ademar Bogo.</p>
          <span class="item__ficha">Militantes dos movimentos populares · 2023</span></a></li>
        <li class="item"><a class="item__link" href="coracao-sem-medo.html">
          <span class="etiqueta">Literatura · 2025</span>
          <h3>Coração sem medo: trechos escolhidos</h3>
          <p>Dezesseis passagens de Itamar Vieira Junior sobre terra, semente e justiça.</p>
          <span class="item__ficha">Itamar Vieira Junior · 2025</span></a></li>
        <li class="item"><a class="item__link" href="citacoes.html">
          <span class="etiqueta">Citações</span>
          <h3>Gama, Carolina e Brecht</h3>
          <p>Oito frases sobre fome, terra e dignidade.</p>
          <span class="item__ficha">Luís Gama, Carolina Maria de Jesus e Bertolt Brecht</span></a></li>
        <li class="item"><a class="item__link" href="caderno-de-poesias.html">
          <span class="etiqueta">Poesia · 2010</span>
          <h3>Caderno de Poesias: índice</h3>
          <p>O mapa da coletânea de 272 páginas: autores e títulos.</p>
          <span class="item__ficha">Cleber Mori (org.) · 2010</span></a></li>
        <li class="item"><a class="item__link" href="recomendacoes.html">
          <span class="etiqueta">Estante</span>
          <h3>Recomendações: livros, filmes e músicas</h3>
          <p>Uma estante de entrada: revoluções, terra, raça e cultura popular.</p>
          <span class="item__ficha">Acervo AJP</span></a></li>
      </ul>
    </section>
"""

with io.open(GERADOR, encoding="utf-8") as f:
    g = f.read()

# Troca o bloco antigo (um só card) pelo novo
import re
g = re.sub(r'    <section class="secao" aria-labelledby="convidados">.*?</section>\n',
           CARDS, g, count=1, flags=re.S)

# Menu: Comparado aponta para o comparado mundial; o outro fica no rodapé
g = g.replace('<a href="direito-critico-comparado.html">Comparado</a>',
              '<a href="assessoria-juridica-popular-no-mundo.html">Comparado</a>', 1)

with io.open(GERADOR, "w", encoding="utf-8", newline="\n") as f:
    f.write(g)

print("cards:", g.count("coracao-sem-medo.html"), "| menu:", "assessoria-juridica-popular-no-mundo.html" in g)
