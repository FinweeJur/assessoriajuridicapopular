/* Mística do dia — mesma lógica do Controle Popular.
   Lê dados/calendario.json, pega as entradas de hoje (MM-DD) e preenche o cartão.
   Sem data para hoje, mostra a data mais próxima para trás. */
(function () {
  'use strict';

  var caixa = document.querySelector('[data-mistica]');
  if (!caixa) { return; }

  var hoje = new Date();
  var mmdd = ('0' + (hoje.getMonth() + 1)).slice(-2) + '-' + ('0' + hoje.getDate()).slice(-2);

  function escapa(t) {
    return (t || '').replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }

  fetch('dados/calendario.json')
    .then(function (r) { return r.json(); })
    .then(function (lista) {
      var doDia = lista.filter(function (e) { return e.diaMes === mmdd; });
      if (!doDia.length) {
        for (var passo = 1; passo <= 7 && !doDia.length; passo++) {
          var d = new Date(hoje.getTime() - passo * 86400000);
          var alvo = ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
          doDia = lista.filter(function (e) { return e.diaMes === alvo; });
        }
      }
      if (!doDia.length) { caixa.hidden = true; return; }

      var e = doDia[hoje.getDate() % doDia.length];
      var cartao = caixa.querySelector('.mistica-cartao') || caixa;
      var campo = function (sel) { return cartao.querySelector(sel); };

      var data = campo('.mistica__data');
      if (data) { data.textContent = mmdd.split('-').reverse().join('/') + ' · ' + (e.ano || ''); }

      var titulo = campo('.mistica__titulo');
      if (titulo) { titulo.innerHTML = escapa(e.titulo); }

      var resumo = campo('.mistica__resumo');
      if (resumo) { resumo.innerHTML = escapa(e.resumo); }

      var fonte = campo('.mistica__fonte');
      if (fonte) { fonte.innerHTML = escapa(e.autor || ''); }

      caixa.hidden = false;
    })
    .catch(function () { caixa.hidden = true; });
})();
