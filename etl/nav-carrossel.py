"""Navegação com pílula/tubelight e carrossel 3D das referências."""
import io

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# ── Navegação dinâmica em todas as páginas ────────────────────────────────
p = RAIZ + r"\casca.js"
js = io.open(p, encoding="utf-8").read()

NAV = """
  // ── Navegação dinâmica: pílula e tubelight seguem o item ativo ─────────
  (function navDinamica() {
    var nav = document.querySelector('.topo__links');
    if (!nav) { return; }
    var pilha = document.createElement('span');
    pilha.className = 'topo__pilha';
    pilha.setAttribute('aria-hidden', 'true');
    var tubo = document.createElement('span');
    tubo.className = 'topo__tubo';
    tubo.setAttribute('aria-hidden', 'true');
    nav.appendChild(pilha);
    nav.appendChild(tubo);

    var ativo = nav.querySelector('a[aria-current="page"]') || nav.querySelector('a');

    function move(el) {
      if (!el) { return; }
      var nr = nav.getBoundingClientRect();
      var r = el.getBoundingClientRect();
      if (r.width < 2) { return; }
      var esq = r.left - nr.left;
      pilha.style.left = esq + 'px';
      pilha.style.width = r.width + 'px';
      pilha.style.opacity = '1';
      tubo.style.left = (esq + 8) + 'px';
      tubo.style.width = Math.max(8, r.width - 16) + 'px';
      tubo.style.opacity = '1';
    }

    Array.prototype.forEach.call(nav.querySelectorAll('a, .menu__botao'), function (el) {
      el.addEventListener('pointerenter', function () { move(el); });
      el.addEventListener('focus', function () { move(el); });
    });
    nav.addEventListener('pointerleave', function () { move(ativo); });
    window.addEventListener('resize', function () { move(ativo); });
    window.addEventListener('load', function () { move(ativo); });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { move(ativo); });
    }
    move(ativo);
  })();
"""

if "navDinamica" not in js:
    i = js.rfind("})();")
    js = js[:i] + NAV + js[i:]
    io.open(p, "w", encoding="utf-8", newline="\n").write(js)
print("nav dinamica:", "navDinamica" in js)

# ── Carrossel 3D na home ──────────────────────────────────────────────────
p = RAIZ + r"\inicio.js"
js = io.open(p, encoding="utf-8").read()

CARROSSEL = """
  // ── Carrossel 3D das referências: órbita, arrasto e momento ────────────
  (function carrossel3d() {
    var caixa = document.querySelector('[data-carrossel]');
    if (!caixa) { return; }
    var palco = caixa.querySelector('.carrossel-3d__palco');
    if (!palco) { return; }

    var ang = 0, vel = 0, arrastando = false, x0 = 0, base = 0, ultimoX = 0, mexeu = false;
    var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var fino = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var auto = !reduz && fino;
    var visivel = true;

    if (window.IntersectionObserver) {
      new IntersectionObserver(function (entradas) {
        visivel = entradas[0].isIntersecting;
      }, { threshold: 0.05 }).observe(caixa);
    }

    function aplica() {
      palco.style.setProperty('--ang', ang.toFixed(2) + 'deg');
    }

    function quadro() {
      if (!arrastando) {
        if (auto && visivel) { ang += 0.16; }
        ang += vel;
        vel *= 0.93;
      }
      aplica();
      requestAnimationFrame(quadro);
    }

    caixa.addEventListener('pointerdown', function (ev) {
      if (ev.button !== undefined && ev.button !== 0) { return; }
      arrastando = true;
      mexeu = false;
      x0 = ev.clientX;
      ultimoX = ev.clientX;
      base = ang;
      vel = 0;
      caixa.setPointerCapture && caixa.setPointerCapture(ev.pointerId);
    });

    caixa.addEventListener('pointermove', function (ev) {
      if (!arrastando) { return; }
      var dx = ev.clientX - x0;
      if (Math.abs(dx) > 6) { mexeu = true; }
      ang = base + dx * 0.35;
      vel = (ev.clientX - ultimoX) * 0.06;
      ultimoX = ev.clientX;
      aplica();
    });

    function solta() {
      arrastando = false;
    }
    caixa.addEventListener('pointerup', solta);
    caixa.addEventListener('pointercancel', solta);
    caixa.addEventListener('pointerleave', solta);
    caixa.addEventListener('click', function (ev) {
      if (mexeu) { ev.preventDefault(); ev.stopPropagation(); mexeu = false; }
    }, true);

    aplica();
    requestAnimationFrame(quadro);
  })();
"""

if "carrossel3d" not in js:
    i = js.rfind("})();")
    js = js[:i] + CARROSSEL + js[i:]
    io.open(p, "w", encoding="utf-8", newline="\n").write(js)
print("carrossel 3d:", "carrossel3d" in js)
