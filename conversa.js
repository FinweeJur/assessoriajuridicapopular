/* Conversa aberta no fim da home: perguntas curadas com respostas e links. */
(function () {
  'use strict';

  var caixa = document.querySelector('[data-conversa]');
  if (!caixa) { return; }
  var corpo = caixa.querySelector('[data-conversa-corpo]');
  var perguntas = caixa.querySelector('[data-conversa-perguntas]');
  var form = caixa.querySelector('[data-conversa-form]');
  var campo = caixa.querySelector('#conversa-campo');
  var curadas = [];

  function escapa(t) {
    return (t || '').replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }

  function rola() { corpo.scrollTop = corpo.scrollHeight; }

  function fala(texto, quem, links) {
    var p = document.createElement('p');
    p.className = 'conversa__fala conversa__fala--' + quem;
    p.innerHTML = escapa(texto);
    (links || []).forEach(function (l) {
      var a = document.createElement('a');
      a.href = l.url;
      a.textContent = l.texto;
      if (/^https?:/.test(l.url)) { a.target = '_blank'; a.rel = 'noopener'; }
      p.appendChild(document.createTextNode(' '));
      p.appendChild(a);
    });
    corpo.appendChild(p);
    rola();
  }

  function responde(q) {
    if (!q) { return; }
    fala(q.pergunta, 'voce');
    fala(q.resposta, 'bot', q.links);
    campo.value = '';
  }

  function semAcento(t) {
    return (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  }

  fetch('dados/perguntas.json').then(function (r) { return r.json(); }).then(function (qs) {
    curadas = qs || [];
    if (!perguntas || !curadas.length) { return; }
    perguntas.innerHTML = curadas.map(function (q, i) {
      return '<button type="button" data-conversa-q="' + i + '">' + escapa(q.pergunta) + '</button>';
    }).join('');
  }).catch(function () {});

  if (perguntas) {
    perguntas.addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-conversa-q]');
      if (!b) { return; }
      responde(curadas[parseInt(b.getAttribute('data-conversa-q'), 10)]);
    });
  }

  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var texto = campo.value.trim();
      if (!texto) { return; }
      var alvo = semAcento(texto);
      var achada = curadas.filter(function (q) {
        return semAcento(q.pergunta).indexOf(alvo) > -1 || alvo.indexOf(semAcento(q.pergunta)) > -1;
      })[0];
      if (achada) { responde(achada); return; }
      try { sessionStorage.setItem('ajp-busca', texto); } catch (e) {}
      fala('Vou procurar “' + texto + '” no acervo completo.', 'bot');
      window.setTimeout(function () { window.location.href = 'acervo.html#lista-acervo'; }, 500);
    });
  }
})();
