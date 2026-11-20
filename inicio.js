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

  // ── Meteoros: feixes coloridos do núcleo aos três nós ─────────────────
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

      var icoMeio = nos[1].querySelector('.fluxo__ico');
      var rm = icoMeio.getBoundingClientRect();
      var core = {
        x: rm.left + rm.width / 2 - pr.left,
        y: rm.top + rm.height / 2 - pr.top
      };

      var defs = cria('defs');
      svg.appendChild(defs);

      var filtro = cria('filter', {
        id: 'fluxo-brilho', x: '-30%', y: '-30%', width: '160%', height: '160%'
      });
      filtro.appendChild(cria('feGaussianBlur', { stdDeviation: '3.5', result: 'blur' }));
      var transf = cria('feComponentTransfer', { in: 'blur', result: 'glow' });
      transf.appendChild(cria('feFuncA', { type: 'linear', slope: '1.8' }));
      filtro.appendChild(transf);
      var merge = cria('feMerge');
      merge.appendChild(cria('feMergeNode', { in: 'glow' }));
      merge.appendChild(cria('feMergeNode', { in: 'SourceGraphic' }));
      filtro.appendChild(merge);
      defs.appendChild(filtro);

      var radial = cria('radialGradient', { id: 'fluxo-core' });
      radial.appendChild(cria('stop', { offset: '0%', 'stop-color': '#38bdf8', 'stop-opacity': '.3' }));
      radial.appendChild(cria('stop', { offset: '100%', 'stop-color': '#38bdf8', 'stop-opacity': '0' }));
      defs.appendChild(radial);
      svg.appendChild(cria('circle', {
        cx: core.x, cy: core.y, r: 80, fill: 'url(#fluxo-core)', opacity: '.9'
      }));

      [[nos[0], 0], [nos[2], 1]].forEach(function (par) {
        var no = par[0];
        var idx = par[1];
        var ico = no.querySelector('.fluxo__ico');
        var r = ico.getBoundingClientRect();
        var centro = {
          x: r.left + r.width / 2 - pr.left,
          y: r.top + r.height / 2 - pr.top
        };
        var inicio = idx === 0 ? centro : core;
        var fim = idx === 0 ? core : centro;
        var vertical = Math.abs(fim.x - inicio.x) < 90;
        var d;
        if (vertical) {
          var meioY = (inicio.y + fim.y) / 2;
          d = 'M' + inicio.x + ' ' + inicio.y +
              ' C' + (inicio.x + 80) + ' ' + (inicio.y + 30) +
              ' ' + (fim.x + 80) + ' ' + meioY +
              ' ' + fim.x + ' ' + fim.y;
        } else {
          var cx = (inicio.x + fim.x) / 2;
          var cy = Math.min(inicio.y, fim.y) - 70;
          d = 'M' + inicio.x + ' ' + inicio.y +
              ' Q' + cx + ' ' + cy +
              ' ' + fim.x + ' ' + fim.y;
        }

        var cores = idx ? ['#38bdf8', '#c084fc'] : ['#ff7a3d', '#38bdf8'];
        var gid = 'fluxo-grad-' + idx;
        var grad = cria('linearGradient', {
          id: gid, gradientUnits: 'userSpaceOnUse',
          x1: inicio.x, y1: inicio.y, x2: fim.x, y2: fim.y
        });
        grad.appendChild(cria('stop', { offset: '0%', 'stop-color': cores[0], 'stop-opacity': '1' }));
        grad.appendChild(cria('stop', { offset: '55%', 'stop-color': cores[1], 'stop-opacity': '.8' }));
        grad.appendChild(cria('stop', { offset: '100%', 'stop-color': cores[1], 'stop-opacity': '.15' }));
        defs.appendChild(grad);

        var base = cria('path', {
          d: d, 'class': 'fluxo__base', stroke: 'url(#' + gid + ')',
          'stroke-width': '7', opacity: '.28',
          filter: 'url(#fluxo-brilho)'
        });
        var linha = cria('path', {
          d: d, 'class': 'fluxo__brilho', stroke: 'url(#' + gid + ')',
          'stroke-width': '2', opacity: '.95'
        });
        svg.appendChild(base);
        svg.appendChild(linha);

        var total = base.getTotalLength();

        if (!reduz) {
          for (var k = 0; k < 3; k++) {
            var seg = 64 + k * 20;
            var met = cria('path', {
              d: d, 'class': 'fluxo__brilho', stroke: 'url(#' + gid + ')',
              'stroke-width': '3.2',
              'stroke-dasharray': seg + ' ' + (total + 1),
              'stroke-dashoffset': (total + seg),
              filter: 'url(#fluxo-brilho)', opacity: '.95'
            });
            met.appendChild(cria('animate', {
              attributeName: 'stroke-dashoffset',
              values: '0;-' + (total + seg),
              dur: (2.2 + k * 0.35) + 's',
              begin: (k * 0.65) + 's',
              repeatCount: 'indefinite'
            }));
            svg.appendChild(met);
          }

          for (var f = 0; f < 4; f++) {
            var faisca = cria('circle', {
              cx: fim.x, cy: fim.y, r: 1.5, 'class': 'impacto',
              stroke: cores[1], fill: 'none'
            });
            faisca.appendChild(cria('animate', {
              attributeName: 'r', values: '1.5;9', dur: '1.3s',
              begin: (f * 0.28) + 's', repeatCount: 'indefinite'
            }));
            faisca.appendChild(cria('animate', {
              attributeName: 'opacity', values: '1;0', dur: '1.3s',
              begin: (f * 0.28) + 's', repeatCount: 'indefinite'
            }));
            svg.appendChild(faisca);
          }
        }
      });
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

// ── Beam Flow em canvas: coluna de filamentos e base larga ────────────────
(function fluxoBeam() {
  var cartao = document.querySelector('.mistica-cartao');
  if (!cartao) { return; }
  var canvas = cartao.querySelector('.beam-canvas');
  if (!canvas || !canvas.getContext) { return; }
  var ctx = canvas.getContext('2d');
  var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fios = [];
  var w = 0, h = 0, baseY = 0, x = 0, beam = 0, dpr = 1, raf = 0;

  for (var i = 0; i < 26; i++) {
    fios.push({
      x: (Math.random() * 2 - 1) * 8,
      largura: .5 + Math.random() * 1.5,
      amp: .8 + Math.random() * 3.2,
      fase: Math.random() * Math.PI * 2,
      vel: .35 + Math.random() * .8,
      alfa: .22 + Math.random() * .55,
      grad: null
    });
  }

  function medir() {
    var r = canvas.getBoundingClientRect();
    if (!r.width || !r.height) { return false; }
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = r.width; h = r.height;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    beam = parseFloat(getComputedStyle(cartao).getPropertyValue('--beam')) || (h - 20);
    baseY = h - 20;
    x = w * .62;
    for (var i = 0; i < fios.length; i++) {
      var f = fios[i];
      var g = ctx.createLinearGradient(0, baseY, 0, 0);
      g.addColorStop(0, 'rgba(230,255,245,' + (.8 * f.alfa).toFixed(3) + ')');
      g.addColorStop(.16, 'rgba(90,255,195,' + (.55 * f.alfa).toFixed(3) + ')');
      g.addColorStop(.62, 'rgba(26,255,156,' + (.18 * f.alfa).toFixed(3) + ')');
      g.addColorStop(1, 'rgba(26,255,156,0)');
      f.grad = g;
    }
    return true;
  }

  function desenha(t) {
    if (!w) { return; }
    ctx.clearRect(0, 0, w, h);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';

    var largura = Math.min(w * .42, 520);

    // Base elíptica larga, como o impacto do Beam Flow.
    var g = ctx.createRadialGradient(x, baseY, 0, x, baseY, largura);
    g.addColorStop(0, 'rgba(225,255,240,.95)');
    g.addColorStop(.07, 'rgba(90,255,195,.72)');
    g.addColorStop(.28, 'rgba(26,255,156,.28)');
    g.addColorStop(1, 'rgba(26,255,156,0)');
    ctx.save();
    ctx.translate(x, baseY);
    ctx.scale(1, .075);
    ctx.beginPath();
    ctx.arc(0, 0, largura, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();
    ctx.restore();

    // Bico largo que sobe do centro para a coluna.
    ctx.beginPath();
    ctx.moveTo(x - largura * .78, baseY + 2);
    ctx.bezierCurveTo(x - largura * .34, baseY - 5, x - 24, baseY - 12, x - 7, baseY - 28);
    ctx.quadraticCurveTo(x, baseY - 38, x + 7, baseY - 28);
    ctx.bezierCurveTo(x + 24, baseY - 12, x + largura * .34, baseY - 5, x + largura * .78, baseY + 2);
    ctx.closePath();
    var gf = ctx.createLinearGradient(0, baseY - 38, 0, baseY + 2);
    gf.addColorStop(0, 'rgba(120,255,205,.35)');
    gf.addColorStop(.35, 'rgba(26,255,156,.7)');
    gf.addColorStop(1, 'rgba(26,255,156,.04)');
    ctx.fillStyle = gf;
    ctx.shadowColor = '#1aff9c';
    ctx.shadowBlur = 16;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Filamentos que sobem com leve deriva.
    var tt = t * .001;
    for (var i = 0; i < fios.length; i++) {
      var f = fios[i];
      var sway = Math.sin(tt * .9 * f.vel + f.fase) * f.amp;
      var drift = Math.sin(tt * .33 * f.vel + f.fase * 1.7) * 2.2;
      ctx.strokeStyle = f.grad;
      ctx.lineWidth = f.largura;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(x + f.x + sway * .35, baseY);
      ctx.bezierCurveTo(
        x + f.x * .85 + sway, baseY - beam * .26,
        x + f.x * .5 + drift, beam * .38,
        x + f.x * .22 + drift * .55, 0
      );
      ctx.stroke();
    }

    // Núcleo branco-esverdeado.
    var gc = ctx.createLinearGradient(0, baseY, 0, 0);
    gc.addColorStop(0, 'rgba(245,255,250,.98)');
    gc.addColorStop(.2, 'rgba(130,255,215,.9)');
    gc.addColorStop(.66, 'rgba(26,255,156,.42)');
    gc.addColorStop(1, 'rgba(26,255,156,0)');
    ctx.strokeStyle = gc;
    ctx.lineWidth = 3.4;
    ctx.shadowColor = '#1aff9c';
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.moveTo(x, baseY);
    ctx.lineTo(x, 0);
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Linha intensa no ponto de impacto.
    var gh = ctx.createLinearGradient(0, 0, w, 0);
    gh.addColorStop(0, 'rgba(26,255,156,0)');
    gh.addColorStop(.35, 'rgba(26,255,156,.25)');
    gh.addColorStop(.5, 'rgba(220,255,240,.85)');
    gh.addColorStop(.65, 'rgba(26,255,156,.25)');
    gh.addColorStop(1, 'rgba(26,255,156,0)');
    ctx.fillStyle = gh;
    ctx.fillRect(0, baseY - 1, w, 2.5);

    // Faíscas subindo.
    for (var s = 0; s < 7; s++) {
      var p = (tt * 18 + s * 1.7) % 100 / 100;
      var sy = baseY * (1 - p);
      var sx = x + Math.sin(tt * 1.3 + s * 2.1) * 10 * (1 - p * .6);
      ctx.beginPath();
      ctx.arc(sx, sy, 1.1 + 1.4 * (1 - p), 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(200,255,230,' + (.6 * (1 - p)).toFixed(3) + ')';
      ctx.fill();
    }

    ctx.restore();
  }

  function anima(t) {
    if (!w) { medir(); }
    if (w && !document.hidden) { desenha(t); }
    raf = requestAnimationFrame(anima);
  }

  function comeca() {
    if (!medir()) { setTimeout(comeca, 300); return; }
    cartao.classList.add('com-beam');
    if (reduz) { desenha(0); } else { raf = requestAnimationFrame(anima); }
  }

  if (window.ResizeObserver) {
    new ResizeObserver(function () {
      if (medir() && reduz) { desenha(0); }
    }).observe(canvas);
  }
  window.addEventListener('resize', function () {
    if (medir() && reduz) { desenha(0); }
  });
  comeca();
})();
