"""Preenche os campos da mística sem apagar a moldura, e centraliza."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

JS = os.path.join(RAIZ, "mistica-dia.js")
with io.open(JS, encoding="utf-8") as f:
    js = f.read()

if "mistica__titulo" not in js:
    js = re.sub(
        r"      caixa\.innerHTML =.*?caixa\.hidden = false;",
        """      var cartao = caixa.querySelector('.mistica-cartao');
      cartao.querySelector('.mistica__data').textContent =
        mmdd.split('-').reverse().join('/') + ' · ' + (e.ano || '');
      cartao.querySelector('.mistica__titulo').textContent = e.titulo || '';
      cartao.querySelector('.mistica__resumo').textContent = e.resumo || '';
      cartao.querySelector('.mistica__fonte').textContent = e.autor || '';
      caixa.hidden = false;""",
        js, count=1, flags=re.S)
    with io.open(JS, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
print("js:", "mistica__titulo" in js)

CSS = os.path.join(RAIZ, "acervo.css")
with io.open(CSS, encoding="utf-8") as f:
    css = f.read()

EXTRA = """
/* Mística do dia: no topo, centralizada, com respiro */
.mistica-dia { padding: clamp(16px, 3vw, 28px) clamp(16px, 4vw, 40px) 0; }
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
print("css:", "Mística do dia: no topo" in css)
