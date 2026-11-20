"""Ordem do comparado (Brasil → América Latina → mundo), 3 colunas e rádio."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
PAGINA = os.path.join(RAIZ, "assessoria-juridica-popular-no-mundo.html")

# ── 1. Reordenar as três seções ────────────────────────────────────────────
with io.open(PAGINA, encoding="utf-8") as f:
    t = f.read()

blocos = re.findall(r'    <section class="secao">.*?</section>\n', t, re.S)
if len(blocos) >= 3:
    achado = lambda chave: next((b for b in blocos if chave in b), None)
    brasil = achado("2. No Brasil")
    latam = achado("3. América Latina")
    mundo = achado("1. No mundo")
    if brasil and latam and mundo:
        # troca os títulos para a nova ordem
        brasil = brasil.replace("2. No Brasil: Constituição forte, cobertura curta",
                                "1. No Brasil: Constituição forte, cobertura curta")
        latam = latam.replace("3. América Latina: ecologia plural, autonomia desigual",
                              "2. América Latina: ecologia plural, autonomia desigual")
        mundo = mundo.replace("1. No mundo: dois modelos e evidência frágil",
                              "3. No mundo: dois modelos e evidência frágil")
        for b in (brasil, latam, mundo):
            t = t.replace(b, "", 1)
        marcador = '    <section class="secao"><div class="secao__cabeca"><h2>O que isso muda para o acervo</h2></div>'
        t = t.replace(marcador, brasil + latam + mundo + marcador, 1)
        with io.open(PAGINA, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
        print("ordem: Brasil, América Latina, mundo")
else:
    print("ordem: nao achei as tres secoes")

# ── 2. Três colunas no máximo, com respiro ─────────────────────────────────
CSS = os.path.join(RAIZ, "acervo.css")
with io.open(CSS, encoding="utf-8") as f:
    css = f.read()

EXTRA = """
/* Lista do acervo: no máximo três colunas, com respiro entre cartões e bordas. */
.lista-acervo {
  gap: clamp(16px, 1.6vw, 26px) !important;
}
@media (min-width: 1100px) {
  .lista-acervo { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }
}
@media (min-width: 760px) and (max-width: 1099px) {
  .lista-acervo { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
}
@media (max-width: 759px) {
  .lista-acervo { grid-template-columns: minmax(0, 1fr) !important; }
}
.lista-acervo .item__link { min-width: 0; }
"""

if "no máximo três colunas" not in css:
    css = css.rstrip() + "\n" + EXTRA
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

# ── 3. Rádio: toggle próprio, para não depender do script antigo ───────────
casca = os.path.join(RAIZ, "casca.js")
with io.open(casca, encoding="utf-8") as f:
    js = f.read()

if "radioFlutuanteCasca" not in js:
    js = js.replace("})();", """
  // ── Rádio: abre e fecha o painel, mesmo se o script antigo falhar ───────
  (function radioFlutuanteCasca() {
    var caixa = document.querySelector('.radio-flut');
    if (!caixa) { return; }
    var botao = caixa.querySelector('.radio-flut__botao');
    var fechar = caixa.querySelector('[data-radio-fechar]');
    if (!botao) { return; }
    // Evita dois toggles no mesmo clique.
    botao.removeAttribute('data-radio-toggle');
    botao.addEventListener('click', function () {
      var aberto = caixa.dataset.aberto === 'true';
      caixa.dataset.aberto = String(!aberto);
      botao.setAttribute('aria-expanded', String(!aberto));
    });
    if (fechar) {
      fechar.addEventListener('click', function () {
        caixa.dataset.aberto = 'false';
        botao.setAttribute('aria-expanded', 'false');
      });
    }
  })();
})();""", 1)
    with io.open(casca, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
    print("radio: toggle proprio")

# ── 4. CSS v8 em todas as páginas ─────────────────────────────────────────
n = 0
for nome in os.listdir(RAIZ):
    if not nome.endswith(".html"):
        continue
    caminho = os.path.join(RAIZ, nome)
    with io.open(caminho, encoding="utf-8") as f:
        html = f.read()
    novo = html.replace("acervo.css?v=36", "acervo.css?v=36").replace("reveal.css?v=36", "reveal.css?v=36")
    if novo != html:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(novo)
        n += 1
print("html v8:", n)
