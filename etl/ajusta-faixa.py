"""Ajusta a faixa para 8 fotos únicas: 2 do blog + 6 do seminário."""
import io
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"


def fig(src, alt):
    return ('<figure class="foto-faixa__item"><img src="%s" alt="%s" loading="lazy" '
            'decoding="async" /></figure>' % (src, alt))


A = [
    ("fotos/blog/blog-02.jpg", "Foto de post do blog Assessoria Jurídica Popular"),
    ("fotos/seminario/seminario-01.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-02.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-03.jpg", "Seminário do IPDMS, 2026"),
]
B = [
    ("fotos/blog/blog-03.jpg", "Imagem de post do blog Assessoria Jurídica Popular"),
    ("fotos/seminario/seminario-04.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-05.jpg", "Seminário do IPDMS, 2026"),
    ("fotos/seminario/seminario-06.jpg", "Seminário do IPDMS, 2026"),
]


def grupo(itens, oculto=False):
    return '<div class="foto-faixa__grupo"%s>%s</div>' % (
        ' aria-hidden="true"' if oculto else "",
        "".join(fig(s, a if not oculto else "") for s, a in itens))


FAIXA = ('<div class="foto-faixa" aria-label="Fotos do acervo e do seminário do IPDMS">\n'
         '          <div class="foto-faixa__linha">\n'
         '            <div class="foto-faixa__trilho foto-faixa__trilho--a">%s%s</div>\n'
         '          </div>\n'
         '          <div class="foto-faixa__linha">\n'
         '            <div class="foto-faixa__trilho foto-faixa__trilho--b">%s%s</div>\n'
         '          </div>\n'
         '          <p class="foto-faixa__nota">Fotos de posts do blog e do seminário do IPDMS, 2026</p>\n'
         '        </div>') % (grupo(A), grupo(A, True), grupo(B), grupo(B, True))

p = RAIZ + r"\index.html"
t = io.open(p, encoding="utf-8").read()
t2, n = re.subn(r'<div class="foto-faixa".*?<p class="foto-faixa__nota">.*?</p>\s*</div>',
                FAIXA, t, count=1, flags=re.S)
if n == 0:
    raise SystemExit("nao achei a faixa")
io.open(p, "w", encoding="utf-8", newline="\n").write(t2)
print("faixa substituida:", t2.count("foto-faixa__item"), "figuras")
