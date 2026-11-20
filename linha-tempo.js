/* Linha do tempo: preenche o trilho e acende os pontos conforme a rolagem. */
(function () {
  'use strict';

  var caixa = document.querySelector('[data-tl]');
  if (!caixa) { return; }

  var linha = caixa.querySelector('[data-tl-linha]');
  var itens = [].slice.call(caixa.querySelectorAll('.tl__item'));
  var semMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function desenha() {
    var r = caixa.getBoundingClientRect();
    var visivel = window.innerHeight - r.top;
    var total = r.height;
    var parte = Math.max(0, Math.min(1, visivel / total));
    if (linha && !semMovimento) { linha.style.height = (parte * 100).toFixed(1) + '%'; }

    itens.forEach(function (item) {
      if (semMovimento) { item.dataset.aceso = 'true'; return; }
      var c = item.getBoundingClientRect();
      item.dataset.aceso = c.top < window.innerHeight * 0.75 ? 'true' : 'false';
    });
  }

  window.addEventListener('scroll', desenha, { passive: true });
  window.addEventListener('resize', desenha);
  desenha();
})();
