/* Fundo: grade interativa de quadrados pequenos em todas as páginas. */
(function () {
  'use strict';

  var canvas = document.querySelector('.grade-interativa');
  if (!canvas) {
    canvas = document.createElement('canvas');
    canvas.className = 'grade-interativa';
    canvas.setAttribute('aria-hidden', 'true');
    document.body.appendChild(canvas);
  }
  if (!canvas.getContext) { return; }

  var ctx = canvas.getContext('2d');
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0;
  var px = -9999, py = -9999, quadro = 0;
  var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fino = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  function resolve(nome, fallback) {
    var sonda = document.createElement('span');
    sonda.style.color = 'var(' + nome + ')';
    sonda.style.display = 'none';
    document.body.appendChild(sonda);
    var cor = getComputedStyle(sonda).color;
    sonda.remove();
    return cor || fallback;
  }

  var primaria = resolve('--cp-primary', '#ffd700');
  var texto = resolve('--cp-text', '#ffffff');

  function mede() {
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    desenha();
  }

  function desenha() {
    ctx.clearRect(0, 0, W, H);
    var tam = W < 620 ? 10 : 14;
    var passo = tam + 4;
    var raio = 102; // 40% menor que o brilho anterior
    for (var y = 4; y < H; y += passo) {
      for (var x = 4; x < W; x += passo) {
        var d = Math.hypot(x + tam / 2 - px, y + tam / 2 - py);
        var a = d < raio ? (1 - d / raio) : 0;
        ctx.globalAlpha = 0.027 + a * 0.3;
        ctx.fillStyle = a > 0.02 ? primaria : texto;
        ctx.fillRect(x, y, tam, tam);
      }
    }
    ctx.globalAlpha = 1;
  }

  function anima() {
    quadro = 0;
    desenha();
  }

  function agenda() {
    if (!quadro) { quadro = requestAnimationFrame(anima); }
  }

  if (!reduz && fino) {
    window.addEventListener('pointermove', function (ev) {
      px = ev.clientX;
      py = ev.clientY;
      agenda();
    }, { passive: true });
    window.addEventListener('pointerleave', function () {
      px = -9999;
      py = -9999;
      agenda();
    });
  }

  window.addEventListener('resize', mede);
  new MutationObserver(function () {
    primaria = resolve('--cp-primary', '#ffd700');
    texto = resolve('--cp-text', '#ffffff');
    agenda();
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  mede();
})();
