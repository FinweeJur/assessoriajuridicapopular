/* Leitura: menu lento, tema persistente, A-/A+ e ouvir. */
(function () {
  'use strict';

  // Menu: hover só com mouse, clique e teclado alternam, Esc fecha.
  function preparaMenu(menu) {
    var botao = menu.querySelector('.menu__botao');
    var lista = menu.querySelector('.menu__lista');
    var relogio = null;
    function abre() {
      clearTimeout(relogio);
      menu.dataset.aberto = 'true';
      if (botao) { botao.setAttribute('aria-expanded', 'true'); }
    }
    function fecha() {
      clearTimeout(relogio);
      menu.dataset.aberto = 'false';
      if (botao) { botao.setAttribute('aria-expanded', 'false'); }
    }
    function agenda() {
      clearTimeout(relogio);
      relogio = setTimeout(function () {
        if (menu.matches(':hover') || (lista && lista.matches(':hover'))) { agenda(); return; }
        fecha();
      }, 1200);
    }
    if (window.matchMedia('(hover: hover)').matches) {
      menu.addEventListener('pointerenter', abre);
      menu.addEventListener('pointerleave', agenda);
      if (lista) {
        lista.addEventListener('pointerenter', abre);
        lista.addEventListener('pointerleave', agenda);
      }
    }
    if (botao) {
      botao.addEventListener('click', function (ev) {
        ev.preventDefault();
        if (menu.dataset.aberto === 'true') { fecha(); } else { abre(); }
      });
    }
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { fecha(); if (botao) { botao.blur(); } }
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.menu'), preparaMenu);

  // Tema: o escolhido manda em todas as páginas; sem escolha, pequi.
  var raiz = document.documentElement;
  var guardado = null;
  try { guardado = localStorage.getItem('renap-tema'); } catch (e) {}
  if (guardado) {
    raiz.dataset.theme = guardado;
  } else if (!raiz.dataset.theme) {
    raiz.dataset.theme = 'pequi';
  }
  var seletor = document.getElementById('tema');
  if (seletor) {
    seletor.value = raiz.dataset.theme;
    seletor.addEventListener('change', function () {
      raiz.dataset.theme = seletor.value;
      try { localStorage.setItem('renap-tema', seletor.value); } catch (e) {}
    });
    // Mantém a barra sincronizada mesmo quando outro script muda o tema.
    if (window.MutationObserver) {
      new MutationObserver(function () {
        if (seletor.value !== raiz.dataset.theme) {
          seletor.value = raiz.dataset.theme;
        }
      }).observe(raiz, { attributes: true, attributeFilter: ['data-theme'] });
    }
    window.addEventListener('storage', function (ev) {
      if (ev.key !== 'renap-tema' || !ev.newValue) { return; }
      raiz.dataset.theme = ev.newValue;
    });
  }

  // Leitura: A-, A+ e ouvir.
  var topo = document.querySelector('.topo__interno');
  if (topo && !document.querySelector('[data-leitura]')) {
    var caixa = document.createElement('div');
    caixa.className = 'topo__leitura';
    caixa.setAttribute('data-leitura', '');
    caixa.innerHTML =
      '<button type="button" data-fonte-menos aria-label="Diminuir o texto" data-dica="Texto menor">A−</button>' +
      '<button type="button" data-fonte-mais aria-label="Aumentar o texto" data-dica="Texto maior">A+</button>' +
      '<button type="button" data-ouvir aria-pressed="false" data-dica="Ouvir a página">Ouvir</button>';
    topo.appendChild(caixa);

    var escala = 1;
    try { escala = parseFloat(localStorage.getItem('renap-escala') || '1'); } catch (e) {}
    function aplica() {
      document.documentElement.style.fontSize = (16 * escala) + 'px';
      try { localStorage.setItem('renap-escala', String(escala)); } catch (e) {}
    }
    aplica();

    caixa.querySelector('[data-fonte-menos]').addEventListener('click', function () {
      escala = Math.max(0.85, Math.round((escala - 0.1) * 10) / 10); aplica();
    });
    caixa.querySelector('[data-fonte-mais]').addEventListener('click', function () {
      escala = Math.min(1.4, Math.round((escala + 0.1) * 10) / 10); aplica();
    });

    var ouvir = caixa.querySelector('[data-ouvir]');
    var falando = false;
    ouvir.addEventListener('click', function () {
      if (!('speechSynthesis' in window)) { return; }
      if (falando) {
        speechSynthesis.cancel(); falando = false; ouvir.setAttribute('aria-pressed', 'false');
        return;
      }
      var texto = (document.querySelector('main') || document.body).innerText.slice(0, 4000);
      var fala = new SpeechSynthesisUtterance(texto);
      fala.lang = 'pt-BR';
      fala.onend = function () { falando = false; ouvir.setAttribute('aria-pressed', 'false'); };
      speechSynthesis.speak(fala);
      falando = true; ouvir.setAttribute('aria-pressed', 'true');
    });
  }
})();
