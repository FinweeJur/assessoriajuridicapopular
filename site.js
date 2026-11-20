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
  var anos = document.querySelector('[data-ano-filtro]');
  var palavras = document.querySelector('[data-palavra-filtro]');
  var chips = [].slice.call(document.querySelectorAll('[data-tipo-f]'));
  var tipoAtual = 'todos';
  var ordem = document.querySelector('[data-ordem]');

  var itens = [].slice.call(listas[0].querySelectorAll('.item'));
  var mostrados = PASSOS;

  function semAcento(t) {
    return (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  }

  function visiveis() {
    // O hidden é consequência da paginação; o filtro olha só o que foi excluído.
    return itens.filter(function (li) { return li.dataset.fora !== '1'; });
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

  function filtra() {
    var termo = semAcento((busca && busca.value || '').trim());
    var ano = anos && anos.value || '';
    var palavra = palavras && palavras.value || '';
    itens.forEach(function (li) {
      var alvo = semAcento(li.textContent + ' ' + (li.dataset.temas || ''));
      var bateTermo = !termo || alvo.indexOf(termo) > -1;
      var bateTipo = tipoAtual === 'todos' || (li.dataset.tipo || 'formativo') === tipoAtual;
      var bateAno = !ano || li.dataset.ano === ano;
      var batePalavra = !palavra || (li.dataset.palavras || '').indexOf(palavra) > -1;
      li.dataset.fora = (bateTermo && bateTipo && bateAno && batePalavra) ? '' : '1';
    });
    mostrados = PASSOS;
    aplica();
  }

  if (busca) { busca.addEventListener('input', filtra); }
  if (anos) { anos.addEventListener('change', filtra); }
  if (palavras) { palavras.addEventListener('change', filtra); }

  chips.forEach(function (botao) {
    botao.addEventListener('click', function () {
      tipoAtual = botao.dataset.tipoF;
      chips.forEach(function (outro) {
        outro.setAttribute('aria-pressed', String(outro === botao));
      });
      filtra();
    });
  });

  if (anos) {
    var vistos = {};
    itens.forEach(function (li) {
      var ano = li.dataset.ano;
      if (ano && !vistos[ano]) {
        vistos[ano] = true;
        var opcao = document.createElement('option');
        opcao.value = ano;
        opcao.textContent = ano;
        anos.appendChild(opcao);
      }
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



  if (palavras) {
    var vistas = {};
    itens.forEach(function (li) {
      (li.dataset.palavras || '').split(' ').forEach(function (p) {
        if (p && !vistas[p]) {
          vistas[p] = true;
          var opcao = document.createElement('option');
          opcao.value = p;
          opcao.textContent = p;
          palavras.appendChild(opcao);
        }
      });
    });
  }

  // Parâmetros da barra global: q, tipo, ano e ordem.
  (function aplicaParametros() {
    var params = new URLSearchParams(window.location.search);
    var termo = params.get('q');
    if (termo && busca) { busca.value = termo; }

    var tipo = params.get('tipo');
    if (tipo) {
      var escolhido = null;
      chips.forEach(function (b) { if (b.dataset.tipoF === tipo) { escolhido = b; } });
      if (escolhido) {
        tipoAtual = escolhido.dataset.tipoF;
        chips.forEach(function (b) { b.setAttribute('aria-pressed', String(b === escolhido)); });
      }
    }

    var ano = params.get('ano');
    if (ano && anos) { anos.value = ano; }

    var qualOrdem = params.get('ordem');
    if (qualOrdem && ordem) {
      ordem.value = qualOrdem;
      ordem.dispatchEvent(new Event('change'));
    }
    filtra();
  })();

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
