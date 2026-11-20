/* Início: grade interativa de quadrados + holofote do bento. */
(function () {
  'use strict';

  var sec = document.querySelector('.inicio');
  var canvas = document.querySelector('[data-grade]');
  if (!sec || !canvas || !canvas.getContext) { return; }

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
    var r = sec.getBoundingClientRect();
    W = r.width;
    H = r.height;
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
    for (var y = 4; y < H; y += passo) {
      for (var x = 4; x < W; x += passo) {
        var d = Math.hypot(x + tam / 2 - px, y + tam / 2 - py);
        var a = d < 170 ? (1 - d / 170) : 0;
        ctx.globalAlpha = 0.045 + a * 0.5;
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
    sec.addEventListener('pointermove', function (ev) {
      var r = sec.getBoundingClientRect();
      px = ev.clientX - r.left;
      py = ev.clientY - r.top;
      agenda();
    });
    sec.addEventListener('pointerleave', function () {
      px = -9999;
      py = -9999;
      agenda();
    });
  }

  window.addEventListener('resize', mede);
  if (window.ResizeObserver) { new ResizeObserver(mede).observe(sec); }
  new MutationObserver(function () {
    primaria = resolve('--cp-primary', '#ffd700');
    texto = resolve('--cp-text', '#ffffff');
    agenda();
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  mede();

  // Holofote que segue o ponteiro nos cartões do bento.
  Array.prototype.forEach.call(document.querySelectorAll('.bento__item'), function (card) {
    card.addEventListener('pointermove', function (ev) {
      var r = card.getBoundingClientRect();
      card.style.setProperty('--bx', ((ev.clientX - r.left) / r.width * 100).toFixed(1) + '%');
      card.style.setProperty('--by', ((ev.clientY - r.top) / r.height * 100).toFixed(1) + '%');
    });
  });
})();
