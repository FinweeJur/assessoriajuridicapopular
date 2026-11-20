/* Mística do dia — mesma lógica do Controle Popular.
   Lê dados/calendario.json, pega as entradas de hoje (MM-DD) e mostra uma.
   Sem data para hoje, mostra a data mais próxima para trás. */
(function () {
  'use strict';

  var caixa = document.querySelector('[data-mistica]');
  if (!caixa) { return; }

  var hoje = new Date();
  var mmdd = ('0' + (hoje.getMonth() + 1)).slice(-2) + '-' + ('0' + hoje.getDate()).slice(-2);

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
      caixa.innerHTML =
        '<p class="mistica__data">' + mmdd.split('-').reverse().join('/') + ' · ' + (e.ano || '') + '</p>' +
        '<h2 class="mistica__titulo">' + escapa(e.titulo) + '</h2>' +
        '<p class="mistica__resumo">' + escapa(e.resumo) + '</p>' +
        (e.autor ? '<p class="mistica__fonte">' + escapa(e.autor) + '</p>' : '');
      caixa.hidden = false;

      function escapa(t) {
        return (t || '').replace(/[&<>"]/g, function (c) {
          return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
        });
      }
    })
    .catch(function () { caixa.hidden = true; });
})();
