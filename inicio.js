/* Início: holofote do bento seguindo o ponteiro. */
(function () {
  'use strict';

  var cartoes = document.querySelectorAll('.bento__item');
  if (!cartoes.length) { return; }

  Array.prototype.forEach.call(cartoes, function (card) {
    card.addEventListener('pointermove', function (ev) {
      var r = card.getBoundingClientRect();
      card.style.setProperty('--bx', ((ev.clientX - r.left) / r.width * 100).toFixed(1) + '%');
      card.style.setProperty('--by', ((ev.clientY - r.top) / r.height * 100).toFixed(1) + '%');
    });
  });

  // ── Carrossel 3D das referências: órbita, arrasto e momento ────────────
  (function carrossel3d() {
    var caixa = document.querySelector('[data-carrossel]');
    if (!caixa) { return; }
    var palco = caixa.querySelector('.carrossel-3d__palco');
    if (!palco) { return; }

    var ang = 0, vel = 0, arrastando = false, x0 = 0, base = 0, ultimoX = 0, mexeu = false;
    var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var fino = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var auto = !reduz;
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
      if (!arrastando && auto) { ang += 0.16; }
      if (!arrastando && Math.abs(vel) > 0.01) { ang += vel; vel *= 0.93; }
      aplica();
      if (!auto && !arrastando && Math.abs(vel) < 0.01) { return; }
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

  // ── Meteoros ligando blog, OpenCode e GitHub ───────────────────────────
  (function meteoros() {
    var palco = document.querySelector('[data-meteoros]');
    if (!palco) { return; }
    var svg = palco.querySelector('.fluxo__svg');
    if (!svg) { return; }
    var NS = 'http://www.w3.org/2000/svg';
    var XLINK = 'http://www.w3.org/1999/xlink';
    var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var quadro = 0;

    function cria(tag, attrs) {
      var el = document.createElementNS(NS, tag);
      if (attrs) { Object.keys(attrs).forEach(function (k) { el.setAttribute(k, attrs[k]); }); }
      return el;
    }

    function desenha() {
      var pr = palco.getBoundingClientRect();
      svg.setAttribute('viewBox', '0 0 ' + pr.width + ' ' + pr.height);
      while (svg.firstChild) { svg.removeChild(svg.firstChild); }
      var nos = [].slice.call(palco.querySelectorAll('.fluxo__no'));
      if (nos.length < 3) { return; }

      for (var i = 0; i < 2; i++) {
        var a = nos[i].getBoundingClientRect();
        var b = nos[i + 1].getBoundingClientRect();
        var vertical = b.top > a.bottom - 12;
        var ax, ay, bx, by, d;
        if (vertical) {
          ax = a.left + a.width / 2 - pr.left;
          ay = a.bottom - pr.top;
          bx = b.left + b.width / 2 - pr.left;
          by = b.top - pr.top;
          d = 'M' + ax + ' ' + ay + ' C' + (ax + 70) + ' ' + ay + ' ' + (bx + 70) + ' ' + by + ' ' + bx + ' ' + by;
        } else {
          ax = a.right - pr.left;
          ay = a.top + a.height / 2 - pr.top;
          bx = b.left - pr.left;
          by = b.top + b.height / 2 - pr.top;
          var mx = (ax + bx) / 2;
          var curva = i % 2 ? 54 : -54;
          d = 'M' + ax + ' ' + ay + ' C' + mx + ' ' + (ay + curva) + ' ' + mx + ' ' + (by + curva) + ' ' + bx + ' ' + by;
        }

        var id = 'fluxo-caminho-' + i;
        var caminho = cria('path', { d: d, 'class': 'fluxo__linha', id: id });
        svg.appendChild(caminho);

        if (!reduz) {
          for (var m = 0; m < 2; m++) {
            var meteoro = cria('circle', { r: m ? 2.2 : 3, 'class': 'meteoro' });
            var mover = cria('animateMotion', {
              dur: (2.6 + m * 0.5) + 's',
              begin: (m * 1.1) + 's',
              repeatCount: 'indefinite',
              rotate: 'auto'
            });
            var mpath = cria('mpath');
            mpath.setAttribute('href', '#' + id);
            mpath.setAttributeNS(XLINK, 'xlink:href', '#' + id);
            mover.appendChild(mpath);
            meteoro.appendChild(mover);
            svg.appendChild(meteoro);
          }
          for (var f = 0; f < 3; f++) {
            var faisca = cria('circle', { cx: bx, cy: by, r: 1.5, 'class': 'impacto' });
            var raio = cria('animate', {
              attributeName: 'r', values: '1.5;8', dur: '1.4s',
              begin: (f * 0.32) + 's', repeatCount: 'indefinite'
            });
            var opac = cria('animate', {
              attributeName: 'opacity', values: '1;0', dur: '1.4s',
              begin: (f * 0.32) + 's', repeatCount: 'indefinite'
            });
            faisca.appendChild(raio);
            faisca.appendChild(opac);
            svg.appendChild(faisca);
          }
        }
      }
    }

    function agenda() {
      if (quadro) { return; }
      quadro = requestAnimationFrame(function () { quadro = 0; desenha(); });
    }

    window.addEventListener('resize', agenda);
    if (window.ResizeObserver) { new ResizeObserver(agenda).observe(palco); }
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(agenda); }
    window.addEventListener('load', agenda);
    desenha();
  })();
})();
