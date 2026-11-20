"""Mística do dia no topo da home, centralizada e com respiro."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
CAPA = os.path.join(RAIZ, "index.html")

with io.open(CAPA, encoding="utf-8") as f:
    t = f.read()

# 1. Remove o bloco de onde estiver e recoloca logo depois do <main>
t = re.sub(r'\n?\s*<section class="mistica-dia".*?</section>\n', "\n", t, count=1, flags=re.S)

BLOCO = '''  <section class="mistica-dia" aria-labelledby="mistica-titulo" hidden data-mistica>
    <div class="miolo">
      <div class="mistica-cartao">
        <p class="olho" id="mistica-titulo"><span class="olho__ponto" aria-hidden="true"></span>Mística do dia</p>
        <p class="mistica__data"></p>
        <h2 class="mistica__titulo"></h2>
        <p class="mistica__resumo"></p>
        <p class="mistica__fonte"></p>
      </div>
    </div>
  </section>

'''

m = re.search(r'<main id="conteudo"[^>]*>\s*\n', t)
if not m:
    raise SystemExit("nao achei o main da capa")
t = t[:m.end()] + BLOCO + t[m.end():]

with io.open(CAPA, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)

# 2. JS: preenche os campos, sem apagar a moldura
JS = os.path.join(RAIZ, "mistica-dia.js")
with io.open(JS, encoding="utf-8") as f:
    js = f.read()

js = re.sub(r"      caixa\.innerHTML =.*?caixa\.hidden = false;", """      var cartao = caixa.querySelector('.mistica-cartao');
      cartao.querySelector('.mistica__data').textContent =
        mmdd.split('-').reverse().join('/') + ' · ' + (e.ano || '');
      cartao.querySelector('.mistica__titulo').textContent = e.titulo || '';
      cartao.querySelector('.mistica__resumo').textContent = e.resumo || '';
      cartao.querySelector('.mistica__fonte').textContent = e.autor || '';
      caixa.hidden = false;""", 1, flags=re.S)

with io.open(JS, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)

# 3. CSS
CSS = os.path.join(RAIZ, "acervo.css")
with io.open(CSS, encoding="utf-8") as f:
    css = f.read()

EXTRA = """
/* Mística do dia: no topo, centralizada, com respiro */
.mistica-dia {
  padding: clamp(16px, 3vw, 28px) clamp(16px, 4vw, 40px) 0;
}
.mistica-cartao {
  max-width: var(--largura); margin: 0 auto;
  padding: clamp(18px, 2.4vw, 28px);
  text-align: center;
  border: 1px solid var(--borda); border-radius: var(--raio);
  background: color-mix(in srgb, var(--cp-surface) 40%, transparent);
}
.mistica-dia .olho { justify-content: center; margin-bottom: 8px; }
.mistica__data { margin: 0 0 6px; font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; color: var(--cp-primary); }
.mistica__titulo { font-family: var(--font-display); font-size: clamp(1.05rem, 1.8vw, 1.35rem); line-height: 1.35; margin: 0 auto 8px; max-width: 60ch; }
.mistica__resumo { margin: 0 auto 8px; max-width: 62ch; font-size: .95rem; color: var(--cp-text-soft); }
.mistica__fonte { margin: 0; font-size: .78rem; color: var(--cp-text-soft); }
"""

if "Mística do dia: no topo" not in css:
    css = css.rstrip() + "\n" + EXTRA
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

# 4. versão nova
for nome in os.listdir(RAIZ):
    if nome.endswith(".html"):
        caminho = os.path.join(RAIZ, nome)
        with io.open(caminho, encoding="utf-8") as f:
            html = f.read()
        novo = html.replace("acervo.css?v=27", "acervo.css?v=27")
        if novo != html:
            with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
                f.write(novo)

print("mística:", "mistica-dia" in t, "| js:", "mistica__titulo" in js)
