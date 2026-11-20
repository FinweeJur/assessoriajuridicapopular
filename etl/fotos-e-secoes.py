"""Faixa infinita de fotos abaixo do título da home + seções que caem."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"


def figura(src, alt):
    return ('<figure class="foto-faixa__item"><img src="%s" alt="%s" loading="lazy" '
            'decoding="async" /></figure>' % (src, alt))


linha_a = [
    ("fotos/blog/blog-01.jpg", "Foto de post do blog Assessoria Jurídica Popular"),
    ("fotos/seminario/seminario-01.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-02.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-03.jpg", "Seminário do IPDMS, 2026"),
]
linha_b = [
    ("fotos/seminario/seminario-04.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-05.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-06.jpg", "Seminário do IPDMS, 2026"),
]


def grupo(itens, oculto=False):
    figs = "".join(figura(s, a if not oculto else "") for s, a in itens)
    return '<div class="foto-faixa__grupo"%s>%s</div>' % (
        ' aria-hidden="true"' if oculto else "", figs)


FAIXA = ('<div class="foto-faixa" aria-label="Fotos do acervo e do seminário do IPDMS">\n'
         '          <div class="foto-faixa__linha">\n'
         '            <div class="foto-faixa__trilho foto-faixa__trilho--a">%s%s</div>\n'
         '          </div>\n'
         '          <div class="foto-faixa__linha">\n'
         '            <div class="foto-faixa__trilho foto-faixa__trilho--b">%s%s</div>\n'
         '          </div>\n'
         '          <p class="foto-faixa__nota">Fotos de posts do blog e do seminário do IPDMS, 2026</p>\n'
         '        </div>') % (grupo(linha_a), grupo(linha_a, True),
                            grupo(linha_b), grupo(linha_b, True))

p = RAIZ + r"\index.html"
t = io.open(p, encoding="utf-8").read()
marcador = "<h1 id=\"titulo-acervo\">Assessoria Jurídica Popular</h1>"
if "foto-faixa" not in t and marcador in t:
    t = t.replace(marcador, marcador + "\n        " + FAIXA, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("faixa de fotos:", "foto-faixa" in t)

# CSS
p = RAIZ + r"\acervo.css"
css = io.open(p, encoding="utf-8").read()
EXTRA = """
/* ── Faixa infinita de fotos abaixo do título ─────────────────────────── */
.foto-faixa {
  margin: 18px 0 8px; display: grid; gap: 10px;
  max-width: 100%;
}
.foto-faixa__linha {
  overflow: hidden;
  -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 5%, #000 95%, transparent 100%);
  mask-image: linear-gradient(90deg, transparent 0, #000 5%, #000 95%, transparent 100%);
}
.foto-faixa__trilho {
  display: flex; width: max-content;
  animation: foto-faixa-a 58s linear infinite;
  will-change: transform;
}
.foto-faixa__trilho--b { animation: foto-faixa-b 68s linear infinite; }
.foto-faixa:hover .foto-faixa__trilho,
.foto-faixa:focus-within .foto-faixa__trilho { animation-play-state: paused; }
.foto-faixa__grupo { display: flex; gap: 10px; padding-right: 10px; }
.foto-faixa__item {
  flex: 0 0 clamp(150px, 20vw, 240px); height: clamp(108px, 13vw, 158px);
  margin: 0; border-radius: 12px; overflow: hidden;
  border: 1px solid var(--borda); background: var(--cp-surface);
}
.foto-faixa__item img { width: 100%; height: 100%; object-fit: cover; display: block; }
.foto-faixa__nota {
  margin: 0; font-size: .7rem; letter-spacing: .04em;
  color: var(--cp-text-soft);
}
@keyframes foto-faixa-a { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@keyframes foto-faixa-b { from { transform: translateX(-50%); } to { transform: translateX(0); } }
@media (max-width: 560px) {
  .foto-faixa { margin-top: 14px; gap: 8px; }
  .foto-faixa__item { flex-basis: 150px; height: 108px; }
  .foto-faixa__grupo { gap: 8px; padding-right: 8px; }
}
@media (prefers-reduced-motion: reduce) {
  .foto-faixa__trilho { animation: none; }
}

/* ── Seções caem suavemente ao entrar na tela ─────────────────────────── */
@media (prefers-reduced-motion: no-preference) {
  .cai {
    opacity: 0; transform: translateY(46px) rotateX(-11deg) scale(.985);
    transform-origin: top center;
    transition: opacity .5s ease, transform .8s cubic-bezier(.16, 1, .3, 1);
  }
  .cai[data-caiu="true"] { opacity: 1; transform: none; }
}
"""
if "Faixa infinita de fotos" not in css:
    io.open(p, "w", encoding="utf-8", newline="\n").write(css.rstrip() + "\n" + EXTRA)
print("css fotos/cai:", "Faixa infinita de fotos" in css)
