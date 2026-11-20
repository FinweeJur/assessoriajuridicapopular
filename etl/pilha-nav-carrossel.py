"""Home: bento vira pilha no celular, navegação com luz e carrossel 3D nas referências."""
import io
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# ── CSS ────────────────────────────────────────────────────────────────────
p = RAIZ + r"\acervo.css"
css = io.open(p, encoding="utf-8").read()

EXTRA = """
/* ── Pilha de cartões no celular (stacking cards) ─────────────────────── */
@media (max-width: 560px) {
  .inicio { overflow: visible !important; }
  .bento {
    display: block !important;
    grid-template-columns: none !important;
    margin-top: 20px;
  }
  .bento .bento__item {
    position: sticky;
    top: calc(96px + var(--i, 0) * 6px);
    z-index: calc(1 + var(--i, 0));
    margin: 0 0 14px;
    min-height: 136px;
    background: var(--cp-bg);
    box-shadow: 0 -10px 28px rgba(0, 0, 0, .28);
    transform: none !important;
  }
  .bento .bento__item--grande { min-height: 236px; }
  .bento .bento__item:hover,
  .bento .bento__item:focus-visible { transform: translateY(-2px) !important; }
}

/* ── Navegação dinâmica com tubelight ─────────────────────────────────── */
.topo__links { position: relative; }
.topo__pilha,
.topo__tubo {
  position: absolute; left: 0; width: 0; pointer-events: none;
  opacity: 0; transition: left .28s cubic-bezier(.22, 1, .36, 1),
                          width .28s cubic-bezier(.22, 1, .36, 1),
                          opacity .2s;
}
.topo__pilha {
  top: 4px; bottom: 4px; z-index: 0; border-radius: 9px;
  background: color-mix(in srgb, var(--cp-primary) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--cp-primary) 34%, transparent);
}
.topo__tubo {
  bottom: -2px; height: 2px; z-index: 0; border-radius: 2px;
  background: var(--cp-primary);
  box-shadow: 0 0 10px 2px color-mix(in srgb, var(--cp-primary) 70%, transparent);
}
.topo__links > a,
.topo__links .menu__botao { position: relative; z-index: 1; }
@media (max-width: 1200px) {
  .topo__pilha, .topo__tubo { display: none; }
}

/* ── Carrossel 3D das referências ─────────────────────────────────────── */
.carrossel-3d {
  position: relative; display: grid; place-items: center;
  height: 340px; margin-top: 14px; perspective: 1200px;
  overflow: hidden;
}
.carrossel-3d__palco {
  position: relative; width: min(22rem, 78vw); height: 240px;
  transform-style: preserve-3d;
  transform: rotateY(var(--ang, 0deg));
  will-change: transform;
}
.carrossel-3d__item {
  position: absolute; inset: 0; width: 100%; height: 100%;
  display: flex; flex-direction: column; gap: 8px;
  transform: rotateY(calc(var(--i) * 120deg)) translateZ(260px) !important;
  backface-visibility: hidden; overflow: hidden;
}
.carrossel-3d__item h3 { font-size: 1.15rem; line-height: 1.25; }
.carrossel-3d__item p { font-size: .86rem; line-height: 1.45; }
.carrossel-3d__chao {
  position: absolute; left: 50%; bottom: 22px; width: 62%; height: 44px;
  transform: translateX(-50%);
  background: radial-gradient(ellipse at center,
              color-mix(in srgb, var(--cp-primary) 22%, transparent), transparent 70%);
  filter: blur(8px); pointer-events: none;
}
.carrossel-3d__dica {
  position: absolute; bottom: 6px; margin: 0; font-size: .72rem;
  letter-spacing: .08em; text-transform: uppercase; color: var(--cp-text-soft);
}
@media (max-width: 560px) {
  .carrossel-3d { height: 300px; }
  .carrossel-3d__palco { width: 78vw; height: 220px; }
  .carrossel-3d__item { transform: rotateY(calc(var(--i) * 120deg)) translateZ(205px) !important; }
  .carrossel-3d__item h3 { font-size: 1rem; }
  .carrossel-3d__item p { font-size: .8rem; }
}
"""

if "Pilha de cartões no celular" not in css:
    css = css.rstrip() + "\n" + EXTRA
    io.open(p, "w", encoding="utf-8", newline="\n").write(css)
print("css pilha/nav/carrossel:", "Pilha de cartões no celular" in css)

# ── Marca o carrossel nas referências da home ──────────────────────────────
p = RAIZ + r"\index.html"
t = io.open(p, encoding="utf-8").read()

if "carrossel-3d" not in t:
    ref = t.find('<section class="referencias"')
    grade = t.find('<div class="grade-3">', ref)
    fim = t.find("</div>", grade) + len("</div>")
    bloco = t[grade:fim]
    cartoes = re.findall(r'<a class="cartao destaque".*?</a>', bloco, re.S)
    if len(cartoes) == 3:
        itens = []
        for i, c in enumerate(cartoes):
            c = c.replace('class="cartao destaque"',
                          'class="cartao destaque carrossel-3d__item" style="--i:%d"' % i, 1)
            itens.append("        " + c)
        novo = ('<div class="carrossel-3d" data-carrossel>\n'
                '        <div class="carrossel-3d__palco">\n' +
                "\n".join(itens) + "\n"
                '        </div>\n'
                '        <div class="carrossel-3d__chao" aria-hidden="true"></div>\n'
                '        <p class="carrossel-3d__dica">Arraste para girar</p>\n'
                '      </div>')
        t = t[:grade] + novo + t[fim:]
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
        print("carrossel na home: ok")
    else:
        print("carrossel: cartões não encontrados", len(cartoes))
else:
    print("carrossel: já existe")
