/* Casca comum: rolagem, assistente e atalhos. Sem dependência.
   Entra em todas as páginas pelo script no fim do body. */
(function () {
  'use strict';

  // ── Rolagem: descer e subir ──────────────────────────────────────────────
  if (!document.querySelector('[data-casca-rolagem]')) {
    var caixa = document.createElement('div');
    caixa.className = 'casca-rolagem';
    caixa.setAttribute('data-casca-rolagem', '');
    caixa.innerHTML =
      '<button type="button" data-casca-subir aria-label="Subir a página" data-dica="Subir">' +
      '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg></button>' +
      '<button type="button" data-casca-descer aria-label="Descer a página" data-dica="Descer">' +
      '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></button>';
    document.body.appendChild(caixa);

    var subir = caixa.querySelector('[data-casca-subir]');
    var descer = caixa.querySelector('[data-casca-descer]');

    subir.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    descer.addEventListener('click', function () {
      window.scrollBy({ top: window.innerHeight * 0.85, behavior: 'smooth' });
    });

    function avalia() {
      var y = window.scrollY;
      var fim = y + window.innerHeight >= document.body.scrollHeight - 80;
      subir.dataset.visivel = y > 500 ? 'true' : 'false';
      descer.dataset.visivel = fim ? 'false' : 'true';
    }
    window.addEventListener('scroll', avalia, { passive: true });
    window.addEventListener('resize', avalia);
    avalia();
  }

  // ── Assistente do acervo ─────────────────────────────────────────────────
  if (!document.querySelector('[data-assistente]')) {
    var painel = document.createElement('div');
    painel.className = 'assistente';
    painel.setAttribute('data-assistente', '');
    painel.dataset.aberto = 'false';
    painel.innerHTML =
      '<button class="assistente__botao" type="button" data-assistente-toggle aria-expanded="false" aria-controls="assistente-painel" data-dica="Perguntar ao acervo">' +
      '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/></svg> Perguntar</button>' +
      '<div class="assistente__painel" id="assistente-painel" role="dialog" aria-label="Perguntar ao acervo">' +
      '<button class="assistente__fechar" type="button" data-assistente-fechar aria-label="Fechar">×</button>' +
      '<h2>Perguntar ao acervo</h2>' +
      '<p class="assistente__nota">Busca nos 713 textos e devolve trechos com autor, ano e link. A resposta em texto com IA depende de um serviço à parte.</p>' +
      '<form class="assistente__form"><label class="sr-only" for="assistente-campo">Sua pergunta</label>' +
      '<input id="assistente-campo" type="search" placeholder="Ex.: o que é assessoria jurídica popular?" autocomplete="off" />' +
      '<button type="submit">Buscar</button></form>' +
      '<p class="assistente__status" role="status" aria-live="polite"></p>' +
      '<ul class="assistente__lista"></ul></div>';
    document.body.appendChild(painel);

    var campo = painel.querySelector('#assistente-campo');
    var lista = painel.querySelector('.assistente__lista');
    var status = painel.querySelector('.assistente__status');
    var indice = null;

    var semAcento = function (t) {
      return (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    };

    function carrega() {
      if (indice) { return Promise.resolve(indice); }
      return fetch('_indice.json').then(function (r) { return r.json(); })
        .then(function (d) { indice = d; return d; })
        .catch(function () { indice = []; return indice; });
    }

    function busca(pergunta) {
      var termos = semAcento(pergunta).split(/[^a-z0-9]+/).filter(function (t) { return t.length > 2; });
      return carrega().then(function (dados) {
        return dados.map(function (r) {
          var alvo = semAcento([r.titulo, r.resumo, r.autor, (r.temas || []).join(' '), (r.palavras || []).join(' ')].join(' '));
          var nota = 0;
          termos.forEach(function (t) {
            var n = alvo.split(t).length - 1;
            if (n) { nota += n * (t.length > 4 ? 3 : 1); }
            if (semAcento(r.titulo || '').indexOf(t) > -1) { nota += 6; }
          });
          return { r: r, nota: nota };
        }).filter(function (x) { return x.nota > 0; })
          .sort(function (a, b) { return b.nota - a.nota; })
          .slice(0, 6)
          .map(function (x) { return x.r; });
      });
    }

    function itemHtml(r) {
      var titulo = (r.titulo || '').replace(/[&<>"]/g, function (c) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
      });
      return '<li class="assistente__item"><a href="' + r.slug + '.html">' + titulo + '</a>' +
        '<span>' + (r.autor || '') + ' · ' + (r.ano || '') + ' · ' + (r.tema || '') + '</span></li>';
    }

    painel.querySelector('[data-assistente-toggle]').addEventListener('click', function () {
      var aberto = painel.dataset.aberto === 'true';
      painel.dataset.aberto = String(!aberto);
      this.setAttribute('aria-expanded', String(!aberto));
      if (!aberto) { campo.focus(); }
    });
    painel.querySelector('[data-assistente-fechar]').addEventListener('click', function () {
      painel.dataset.aberto = 'false';
      painel.querySelector('[data-assistente-toggle]').setAttribute('aria-expanded', 'false');
    });
    painel.querySelector('.assistente__form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var pergunta = campo.value.trim();
      if (!pergunta) { return; }
      status.textContent = 'Procurando…';
      lista.innerHTML = '';
      busca(pergunta).then(function (achados) {
        if (!achados.length) {
          status.textContent = 'Não achei nada com essas palavras. Tente outra palavra ou use a busca da capa.';
          return;
        }
        status.textContent = achados.length + ' trechos com fonte.';
        lista.innerHTML = achados.map(itemHtml).join('');
      });
    });
  }

  // ── Rádio: abre e fecha o painel, mesmo se o script antigo falhar ───────
  (function radioFlutuanteCasca() {
    var caixa = document.querySelector('.radio-flut');
    if (!caixa) { return; }
    var botao = caixa.querySelector('.radio-flut__botao');
    var fechar = caixa.querySelector('[data-radio-fechar]');
    if (!botao) { return; }
    // Evita dois toggles no mesmo clique.
    botao.removeAttribute('data-radio-toggle');
    botao.addEventListener('click', function () {
      var aberto = caixa.dataset.aberto === 'true';
      caixa.dataset.aberto = String(!aberto);
      botao.setAttribute('aria-expanded', String(!aberto));
    });
    if (fechar) {
      fechar.addEventListener('click', function () {
        caixa.dataset.aberto = 'false';
        botao.setAttribute('aria-expanded', 'false');
      });
    }
  
  // Menu hambúrguer em tela estreita
  (function menuEstreito() {
    var topo = document.querySelector('.topo');
    var interno = document.querySelector('.topo__interno');
    var links = document.querySelector('.topo__links');
    if (!topo || !interno || !links || document.querySelector('.topo__abrir')) { return; }
    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'topo__abrir';
    botao.setAttribute('aria-label', 'Abrir o menu');
    botao.setAttribute('aria-expanded', 'false');
    botao.setAttribute('aria-controls', 'menu-principal');
    botao.innerHTML = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>';
    links.id = 'menu-principal';
    var marca = interno.querySelector('.topo__marca');
    if (marca) { marca.insertAdjacentElement('afterend', botao); } else { interno.appendChild(botao); }

    botao.addEventListener('click', function () {
      var aberto = topo.dataset.aberto === 'true';
      topo.dataset.aberto = String(!aberto);
      botao.setAttribute('aria-expanded', String(!aberto));
      botao.setAttribute('aria-label', aberto ? 'Abrir o menu' : 'Fechar o menu');
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { topo.dataset.aberto = 'false'; botao.setAttribute('aria-expanded', 'false'); }
    });
  })();
})();

  // ── Ímã: botões e atalhos seguem de leve o ponteiro ─────────────────────
  (function ima() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { return; }
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) { return; }
    var alvos = document.querySelectorAll('.botao, .chip-f, .radio-flut__botao, .assistente__botao, .menu__botao, .topo__abrir, .casca-rolagem button, .topo__marca');
    Array.prototype.forEach.call(alvos, function (el) {
      el.setAttribute('data-magnet', '');
      el.addEventListener('pointermove', function (ev) {
        var r = el.getBoundingClientRect();
        var dx = (ev.clientX - (r.left + r.width / 2)) * 0.18;
        var dy = (ev.clientY - (r.top + r.height / 2)) * 0.22;
        var limite = 8;
        dx = Math.max(-limite, Math.min(limite, dx));
        dy = Math.max(-limite, Math.min(limite, dy));
        el.style.setProperty('--mx', dx.toFixed(1) + 'px');
        el.style.setProperty('--my', dy.toFixed(1) + 'px');
      });
      function solta() {
        el.style.setProperty('--mx', '0px');
        el.style.setProperty('--my', '0px');
      }
      el.addEventListener('pointerleave', solta);
      el.addEventListener('blur', solta);
    });
  })();

  // ── Rádio e Perguntar: só aparecem depois que a página rola ──────────────
  (function botoesNoComeco() {
    var corpo = document.body;
    function avalia() {
      var rolavel = document.documentElement.scrollHeight > window.innerHeight + 120;
      corpo.dataset.comeco = (rolavel && window.scrollY < 140) ? 'true' : 'false';
    }
    window.addEventListener('scroll', avalia, { passive: true });
    window.addEventListener('resize', avalia);
    avalia();
  })();
})();
