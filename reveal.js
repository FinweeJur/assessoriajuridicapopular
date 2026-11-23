/**
 * Scroll reveal sem biblioteca.
 *
 * Por que sem dependência: o site é HTML estático; um IntersectionObserver
 * resolve o mesmo que AOS/ScrollReveal com ~40 linhas e zero peso de CDN.
 * Regras:
 *   - nada aparece se `prefers-reduced-motion: reduce`;
 *   - o conteúdo nasce visível no HTML e o JS só esconde o que ainda não
 *     entrou na tela (sem "flash" de conteúdo invisível);
 *   - cada bloco entra uma vez e para de ser observado.
 *
 * Contrato: marcar `[data-revelar]` no HTML ou deixar o script marcar os
 * filhos de `[data-revelar-grupo]`.
 */
(function () {
  'use strict';

  var semMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (semMovimento || !('IntersectionObserver' in window)) {
    document.documentElement.classList.add('revelar-pronto');
    return;
  }

  function marcar() {
    var grupos = document.querySelectorAll('[data-revelar-grupo]');
    [].forEach.call(grupos, function (grupo) {
      [].forEach.call(grupo.children, function (filho, i) {
        if (filho.hasAttribute('data-revelar')) { return; }
        // Artigo de leitura inteiro não entra no reveal: é maior que a tela
        // e o IntersectionObserver de 8% nunca dispara. Os blocos internos
        // continuam animando pelo grupo do próprio artigo.
        if (filho.matches('article.pagina, .pagina')) { return; }
        filho.setAttribute('data-revelar', '');
        filho.style.setProperty('--atraso', Math.min(i, 6) * 60 + 'ms');
      });
    });
  }

  var alvos = [];

  function observa() {
    alvos = [].slice.call(document.querySelectorAll('[data-revelar]:not(.revelado)'));
    if (!alvos.length) { return; }

    var olho = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) { return; }
        entrada.target.classList.add('revelado');
        olho.unobserve(entrada.target);
      });
    // threshold 0: seções enormes (calendário com centenas de itens) nunca
    // atingiriam 2% de área visível e ficariam com opacity 0 para sempre.
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0 });

    alvos.forEach(function (alvo) { olho.observe(alvo); });
  }

  function inicia() {
    marcar();
    // Só esconde depois que o CSS está pronto, para não piscar.
    document.documentElement.classList.add('tem-revelar');
    observa();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicia);
  } else {
    inicia();
  }

  // Página gerada por script (busca, filtro) pode pedir nova varredura.
  window.revelarDeNovo = function () {
    marcar();
    observa();
  };
})();
