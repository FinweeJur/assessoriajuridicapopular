/* Lista com paginação, filtro e volta ao topo — sem biblioteca.
   Funciona sem JS: com JS desligado, todos os itens aparecem. */
(function () {
  'use strict';
  var PASSOS = 24;

  var listas = [].slice.call(document.querySelectorAll('[data-paginada]'));
  if (!listas.length) { return; }

  var botaoMais = document.querySelector('[data-mais]');
  var conta = document.querySelector('[data-conta]');
  var busca = document.querySelector('[data-busca]');
  var ordem = document.querySelector('[data-ordem]');

  var itens = [].slice.call(listas[0].querySelectorAll('.item'));
  var mostrados = PASSOS;

  function semAcento(t) {
    return (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  }

  function visiveis() {
    return itens.filter(function (li) { return !li.hidden && !li.dataset.fora; });
  }

  function aplica() {
    var vivos = visiveis();
    itens.forEach(function (li) {
      var posicao = vivos.indexOf(li);
      li.hidden = posicao === -1 || posicao >= mostrados;
    });
    if (conta) {
      conta.textContent = vivos.length + (vivos.length === 1 ? ' texto' : ' textos');
    }
    if (botaoMais) {
      var restam = vivos.length - mostrados;
      botaoMais.hidden = restam <= 0;
      botaoMais.textContent = 'Ver mais ' + Math.min(PASSOS, Math.max(restam, 0));
    }
  }

  if (busca) {
    busca.addEventListener('input', function () {
      var termo = semAcento(busca.value.trim());
      itens.forEach(function (li) {
        var alvo = semAcento(li.textContent + ' ' + (li.dataset.temas || ''));
        li.dataset.fora = termo && alvo.indexOf(termo) === -1 ? '1' : '';
      });
      mostrados = PASSOS;
      aplica();
    });
  }

  if (ordem) {
    ordem.addEventListener('change', function () {
      var lista = listas[0];
      var copia = itens.slice();
      copia.sort(function (a, b) {
        var da = a.dataset.data || '', db = b.dataset.data || '';
        var ta = semAcento(a.dataset.titulo), tb = semAcento(b.dataset.titulo);
        if (ordem.value === 'antigo') { return da < db ? -1 : da > db ? 1 : 0; }
        if (ordem.value === 'titulo') { return ta < tb ? -1 : ta > tb ? 1 : 0; }
        return da > db ? -1 : da < db ? 1 : 0;
      });
      copia.forEach(function (li) { lista.appendChild(li); });
      itens = copia;
      mostrados = PASSOS;
      aplica();
    });
  }

  if (botaoMais) {
    botaoMais.addEventListener('click', function () {
      mostrados += PASSOS;
      aplica();
    });
  }

  aplica();

  // Volta ao topo
  var topo = document.querySelector('[data-topo]');
  if (topo) {
    window.addEventListener('scroll', function () {
      topo.dataset.visivel = window.scrollY > 600 ? 'true' : 'false';
    }, { passive: true });
    topo.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();
