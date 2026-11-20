/* Fundo: grade interativa + estrelas que esticam com a rolagem. */
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
  var vel = 0, ultimoY = window.scrollY;
  var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fino = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var estrelas = [];

  function resolve(nome, fallback) {
    var sonda = document.createElement('span');
    sonda.style.color = 'var(' + nome + ')';
    sonda.style.display = 'none';
    document.body.appendChild(sonda);
    var cor = getComputedStyle(sonda).color;
    sonda.remove();
    return cor || fallback;
  }

  var primaria = resolve('--cor-tema', resolve('--cp-primary', '#ffd700'));
  var texto = resolve('--cp-text', '#ffffff');

  function criaEstrelas() {
    estrelas = [];
    var n = Math.max(26, Math.round(W * H / 26000));
    for (var i = 0; i < n; i++) {
      estrelas.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: 0.6 + Math.random() * 1.2,
        a: 0.12 + Math.random() * 0.22
      });
    }
  }

  function mede() {
    W = document.documentElement.clientWidth || window.innerWidth;
    H = window.innerHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    criaEstrelas();
    desenha();
  }

  function desenha() {
    ctx.clearRect(0, 0, W, H);

    // Grade de quadrados pequenos.
    var tam = W < 620 ? 10 : 14;
    var passo = tam + 4;
    var raio = 102;
    for (var y = 4; y < H; y += passo) {
      for (var x = 4; x < W; x += passo) {
        var d = Math.hypot(x + tam / 2 - px, y + tam / 2 - py);
        var a = d < raio ? (1 - d / raio) : 0;
        ctx.globalAlpha = 0.027 + a * 0.3;
        ctx.fillStyle = a > 0.02 ? primaria : texto;
        ctx.fillRect(x, y, tam, tam);
      }
    }

    // Estrelas: pontos parados ou riscos na velocidade da rolagem.
    ctx.fillStyle = texto;
    var risco = Math.max(0, Math.min(46, Math.abs(vel) * 2.4));
    for (var i = 0; i < estrelas.length; i++) {
      var e = estrelas[i];
      e.y += vel * 0.35;
      if (e.y < -8) { e.y = H + 8; e.x = Math.random() * W; }
      if (e.y > H + 8) { e.y = -8; e.x = Math.random() * W; }
      ctx.globalAlpha = e.a;
      if (risco > 1.5) {
        ctx.fillRect(e.x, e.y - Math.sign(vel) * risco, e.r, risco + e.r);
      } else {
        ctx.fillRect(e.x, e.y, e.r, e.r);
      }
    }

    ctx.globalAlpha = 1;
    vel *= 0.82;
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

  if (!reduz) {
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      vel = Math.max(-70, Math.min(70, y - ultimoY));
      ultimoY = y;
      agenda();
    }, { passive: true });
  }

  window.addEventListener('resize', mede);
  new MutationObserver(function () {
    primaria = resolve('--cor-tema', resolve('--cp-primary', '#ffd700'));
    texto = resolve('--cp-text', '#ffffff');
    agenda();
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  mede();
})();
