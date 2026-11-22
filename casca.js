/* Casca comum: rolagem, assistente e atalhos. Sem dependência.
   Entra em todas as páginas pelo script no fim do body. */
(function () {
  'use strict';

  // ── Discagem rápida: topo, descer e buscar/compartilhar ────────────────
  if (!document.querySelector('[data-dial]')) {
    var dial = document.createElement('div');
    dial.className = 'casca-dial';
    dial.setAttribute('data-dial', '');
    dial.dataset.aberto = 'false';
    dial.dataset.visivel = 'false';

    var busca = document.querySelector('[data-busca]');
    var compartilhar = document.querySelector('.compartilhar');
    var terceira = busca
      ? '<button type="button" data-dial-busca style="--i:2"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg> Buscar</button>'
      : (compartilhar
        ? '<button type="button" data-dial-compartilhar style="--i:2"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 10.7 6.8-4.1M8.6 13.3l6.8 4.1"/></svg> Compartilhar</button>'
        : '<button type="button" data-dial-acervo style="--i:2"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/></svg> Acervo</button>');

    dial.innerHTML =
      '<div class="casca-dial__acoes">' +
      '<button type="button" data-dial-topo style="--i:0"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg> Topo</button>' +
      '<button type="button" data-dial-descer style="--i:1"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg> Descer</button>' +
      terceira +
      '<button type="button" data-dial-radio style="--i:3"><span aria-hidden="true">📻</span> Rádio</button>' +
      '<button type="button" data-dial-perguntar style="--i:4"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/></svg> Perguntar</button>' +
      '</div>' +
      '<button class="casca-dial__botao" type="button" data-dial-toggle aria-expanded="false" aria-label="Ações da página">' +
      '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg></button>';
    document.body.appendChild(dial);

    var botaoDial = dial.querySelector('[data-dial-toggle]');

    function rolaPara(y) {
      var html = document.documentElement;
      var antes = html.style.scrollBehavior;
      html.style.scrollBehavior = 'auto';
      window.scrollTo(0, y);
      html.style.scrollBehavior = antes;
    }

    function fechaDial() {
      dial.dataset.aberto = 'false';
      botaoDial.setAttribute('aria-expanded', 'false');
    }
    botaoDial.addEventListener('click', function () {
      var aberto = dial.dataset.aberto === 'true';
      dial.dataset.aberto = String(!aberto);
      botaoDial.setAttribute('aria-expanded', String(!aberto));
    });
    document.addEventListener('click', function (ev) {
      if (!dial.contains(ev.target)) { fechaDial(); }
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { fechaDial(); }
    });

    dial.querySelector('[data-dial-topo]').addEventListener('click', function () {
      rolaPara(0);
      fechaDial();
    });
    dial.querySelector('[data-dial-descer]').addEventListener('click', function () {
      rolaPara(window.scrollY + Math.round(window.innerHeight * 0.85));
      fechaDial();
    });

    dial.querySelector('[data-dial-radio]').addEventListener('click', function () {
      var b = document.querySelector('[data-radio-toggle]');
      if (b) { b.click(); }
      fechaDial();
    });
    dial.querySelector('[data-dial-perguntar]').addEventListener('click', function () {
      var b = document.querySelector('[data-assistente-toggle]');
      if (b) { b.click(); }
      fechaDial();
    });
    if (busca) {
      dial.querySelector('[data-dial-busca]').addEventListener('click', function () {
        busca.scrollIntoView({ behavior: 'smooth', block: 'center' });
        window.setTimeout(function () { busca.focus(); }, 420);
        fechaDial();
      });
    }
    if (!busca && compartilhar) {
      dial.querySelector('[data-dial-compartilhar]').addEventListener('click', function () {
        compartilhar.scrollIntoView({ behavior: 'smooth', block: 'center' });
        var alvo = compartilhar.querySelector('button, a');
        if (alvo) { window.setTimeout(function () { alvo.focus(); }, 420); }
        fechaDial();
      });
    }
    if (!busca && !compartilhar) {
      dial.querySelector('[data-dial-acervo]').addEventListener('click', function () {
        window.location.href = 'acervo.html?q=' + encodeURIComponent(termo) + '#lista-acervo';
      });
    }

    // O + fica sempre visível: é a porta do rádio e do chatbot.
    dial.dataset.visivel = 'true';
  }

  // ── Barra global de busca, filtro e ordem ────────────────────────────────
  (function buscaGlobal() {
    if (document.querySelector('.fita') || document.querySelector('.busca-global')) { return; }
    var arquivo = location.pathname.split('/').pop() || 'index.html';
    // Sem busca na capa e em páginas que não listam textos
    if (arquivo === '' || arquivo === 'index.html') { return; }
    if (!document.querySelector('.lista-acervo, [data-paginada], .grade-3, .item')) { return; }
    var topo = document.querySelector('.topo');
    if (!topo) { return; }

    var anos = '';
    for (var a = 2024; a >= 2003; a--) {
      anos += '<option value="' + a + '">' + a + '</option>';
    }

    var secao = document.createElement('section');
    secao.className = 'busca-global';
    secao.setAttribute('aria-label', 'Buscar e filtrar o acervo');
    secao.innerHTML =
      '<form class="busca-global__form" role="search" method="get" action="acervo.html">' +
        '<div class="busca-global__campo">' +
          '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
          '<input type="search" name="q" aria-label="Buscar no acervo" placeholder="Buscar no acervo" autocomplete="off" />' +
        '</div>' +
        '<select name="tipo" aria-label="Tipo de texto">' +
          '<option value="todos">Todos os tipos</option>' +
          '<option value="formativo">Textos</option>' +
          '<option value="evento">Eventos</option>' +
          '<option value="poesia">Poesia</option>' +
          '<option value="resenha">Livros</option>' +
          '<option value="documento">Documentos</option>' +
          '<option value="notícia">Notícias</option>' +
        '</select>' +
        '<select name="ano" aria-label="Ano"><option value="">Todos os anos</option>' + anos + '</select>' +
        '<select name="rede" aria-label="Rede ou organização">' +
          '<option value="">Todas as redes</option>' +
          '<option value="renap">RENAP</option>' +
          '<option value="ipdms">IPDMS</option>' +
          '<option value="renaju-ajup">RENAJU/AJUPs</option>' +
        '</select>' +
        '<select name="ordem" aria-label="Ordenar">' +
          '<option value="recente">Mais recente</option>' +
          '<option value="antigo">Mais antigo</option>' +
          '<option value="titulo">Título</option>' +
        '</select>' +
        '<button type="submit">Filtrar</button>' +
      '</form>';
    topo.insertAdjacentElement('afterend', secao);

    var form = secao.querySelector('form');
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var q = form.querySelector('input[name="q"]').value.trim();
      var tipo = form.querySelector('select[name="tipo"]').value;
      var ano = form.querySelector('select[name="ano"]').value;
      var rede = form.querySelector('select[name="rede"]').value;
      var ordem = form.querySelector('select[name="ordem"]').value;
      var params = new URLSearchParams();
      if (q) { params.set('q', q); }
      if (tipo && tipo !== 'todos') { params.set('tipo', tipo); }
      if (ano) { params.set('ano', ano); }
      if (rede) { params.set('rede', rede); }
      if (ordem && ordem !== 'recente') { params.set('ordem', ordem); }
      var url = 'acervo.html';
      if (params.toString()) { url += '?' + params.toString(); }
      window.location.href = url + '#lista-acervo';
    });
  })();


  // ── Busca expansível na barra do topo ────────────────────────────────────
  (function buscaTopo() {
    var interno = document.querySelector('.topo__interno');
    if (!interno || interno.querySelector('[data-topo-busca]')) { return; }
    var caixa = document.createElement('div');
    caixa.className = 'topo__busca';
    caixa.setAttribute('data-topo-busca', '');
    caixa.innerHTML =
      '<button type="button" class="topo__busca-botao" data-topo-busca-toggle aria-expanded="false" aria-controls="topo-busca-form" aria-label="Buscar no acervo">' +
      '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></button>' +
      '<form class="topo__busca-form" id="topo-busca-form" role="search" action="acervo.html">' +
      '<input type="search" name="q" placeholder="Buscar no acervo" aria-label="Buscar no acervo" autocomplete="off" />' +
      '<button type="submit" aria-label="Buscar">Ir</button></form>';
    var tema = interno.querySelector('.topo__tema');
    interno.insertBefore(caixa, tema || null);

    var botao = caixa.querySelector('[data-topo-busca-toggle]');
    var form = caixa.querySelector('.topo__busca-form');
    var campo = form.querySelector('input');
    function abre() {
      caixa.dataset.aberto = 'true';
      botao.setAttribute('aria-expanded', 'true');
      window.setTimeout(function () { campo.focus(); }, 60);
    }
    function fecha() {
      caixa.dataset.aberto = 'false';
      botao.setAttribute('aria-expanded', 'false');
    }
    botao.addEventListener('click', function () {
      if (caixa.dataset.aberto === 'true') { fecha(); } else { abre(); }
    });
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var termo = campo.value.trim();
      if (!termo) { campo.focus(); return; }
      window.location.href = 'acervo.html?q=' + encodeURIComponent(termo) + '#lista-acervo';
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { fecha(); }
    });
    document.addEventListener('click', function (ev) {
      if (!caixa.contains(ev.target)) { fecha(); }
    });
  })();

  // ── Subir/descer sempre visíveis na lateral direita ─────────────────────
  (function rolagemLateral() {
    if (document.querySelector('[data-rolagem]')) { return; }
    var caixa = document.createElement('div');
    caixa.className = 'casca-rolagem';
    caixa.setAttribute('data-rolagem', '');
    caixa.innerHTML =
      '<button type="button" data-rolagem-subir aria-label="Subir a página" title="Subir">' +
        '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m18 15-6-6-6 6"/></svg>' +
      '</button>' +
      '<button type="button" data-rolagem-descer aria-label="Descer a página" title="Descer">' +
        '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>' +
      '</button>';
    document.body.appendChild(caixa);
    function rolaLateral(y) {
      var html = document.documentElement;
      var antes = html.style.scrollBehavior;
      html.style.scrollBehavior = 'auto';
      window.scrollTo(0, y);
      html.style.scrollBehavior = antes;
    }
    caixa.querySelector('[data-rolagem-subir]').addEventListener('click', function () {
      rolaLateral(0);
    });
    caixa.querySelector('[data-rolagem-descer]').addEventListener('click', function () {
      rolaLateral(window.scrollY + Math.round(window.innerHeight * 0.85));
    });
  })();

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
      '<div class="assistente__barra" role="group" aria-label="Ajustes de leitura">' +
      '<span class="assistente__barra-rotulo">Texto</span>' +
      '<button type="button" data-assistente-fonte="menos" aria-label="Diminuir o texto" data-dica="Texto menor">A−</button>' +
      '<button type="button" data-assistente-fonte="mais" aria-label="Aumentar o texto" data-dica="Texto maior">A+</button>' +
      '<label class="assistente__tema"><span>Tema</span>' +
      '<select data-assistente-tema aria-label="Tema do site"></select></label>' +
      '</div>' +
      '<p class="assistente__nota">Busca nos 713 textos e devolve trechos com autor, ano e link. <a href="dados/prompt-ia.md" target="_blank" rel="noopener">Como respondo</a>.</p>' +
      '<form class="assistente__form"><label class="sr-only" for="assistente-campo">Sua pergunta</label>' +
      '<input id="assistente-campo" type="search" placeholder="Ex.: o que é assessoria jurídica popular?" autocomplete="off" />' +
      '<button type="submit">Buscar</button></form>' +
      '<div class="assistente__curadas" data-assistente-curadas></div>' +
      '<p class="assistente__status" role="status" aria-live="polite"></p>' +
      '<ul class="assistente__lista"></ul></div>';
    document.body.appendChild(painel);

    var campo = painel.querySelector('#assistente-campo');
    var lista = painel.querySelector('.assistente__lista');
    var status = painel.querySelector('.assistente__status');
    var indice = null;
    var curadas = [];
    var curadasBox = painel.querySelector('[data-assistente-curadas]');

    // Ajustes de leitura: fonte e tema, reaproveitando a barra do topo.
    var selTema = painel.querySelector('[data-assistente-tema]');
    var temaTopo = document.getElementById('tema');
    if (selTema) {
      if (temaTopo) { selTema.innerHTML = temaTopo.innerHTML; }
      selTema.value = document.documentElement.dataset.theme || (temaTopo ? temaTopo.value : 'pequi');
      selTema.addEventListener('change', function () {
        if (temaTopo) {
          temaTopo.value = selTema.value;
          temaTopo.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
          document.documentElement.dataset.theme = selTema.value;
          try { localStorage.setItem('renap-tema', selTema.value); } catch (e) {}
        }
      });
      if (window.MutationObserver) {
        new MutationObserver(function () {
          var atual = document.documentElement.dataset.theme;
          if (atual && selTema.value !== atual) { selTema.value = atual; }
        }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
      }
    }

    function ajustaFonte(dir) {
      var b = document.querySelector(dir === 'mais' ? '[data-fonte-mais]' : '[data-fonte-menos]');
      if (b) { b.click(); return; }
      var escala = 1;
      try { escala = parseFloat(localStorage.getItem('renap-escala') || '1'); } catch (e) {}
      escala = dir === 'mais' ? Math.min(1.4, escala + 0.1) : Math.max(0.85, escala - 0.1);
      document.documentElement.style.fontSize = (16 * escala) + 'px';
      try { localStorage.setItem('renap-escala', String(escala)); } catch (e) {}
    }
    painel.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-assistente-fonte]');
      if (!b) { return; }
      ajustaFonte(b.getAttribute('data-assistente-fonte'));
    });

    function escapa(t) {
      return (t || '').replace(/[&<>"]/g, function (c) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
      });
    }

    function mostraCurada(q) {
      if (!q) { return; }
      status.textContent = 'Resposta curada.';
      var links = (q.links || []).map(function (l) {
        var externo = /^https?:/.test(l.url) ? ' target="_blank" rel="noopener"' : '';
        return '<a href="' + l.url + '"' + externo + '>' + escapa(l.texto) + '</a>';
      }).join('');
      lista.innerHTML = '<li class="assistente__resposta"><b>' + escapa(q.pergunta) + '</b>' +
        '<p>' + escapa(q.resposta) + '</p>' + (links ? '<div>' + links + '</div>' : '') + '</li>';
    }

    fetch('dados/perguntas.json').then(function (r) { return r.json(); }).then(function (qs) {
      curadas = qs || [];
      if (!curadasBox || !curadas.length) { return; }
      curadasBox.innerHTML = '<span class="assistente__curadas-rotulo">Perguntas rápidas</span>' +
        curadas.map(function (q, i) {
          return '<button type="button" data-curada="' + i + '">' + escapa(q.pergunta) + '</button>';
        }).join('');
    }).catch(function () {});

    if (curadasBox) {
      curadasBox.addEventListener('click', function (ev) {
        var b = ev.target.closest('button[data-curada]');
        if (!b) { return; }
        mostraCurada(curadas[parseInt(b.getAttribute('data-curada'), 10)]);
      });
    }


    var semAcento = function (t) {
      return (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    };

    var rag = null;
    function carregaRag() {
      if (rag) { return Promise.resolve(rag); }
      return fetch('dados/rag.json').then(function (r) { return r.json(); })
        .then(function (d) { rag = d; return d; })
        .catch(function () { rag = []; return rag; });
    }

    function trecho(texto, termos) {
      var baixo = semAcento(texto);
      var pos = -1;
      termos.forEach(function (t) {
        var i = baixo.indexOf(t);
        if (pos < 0 || (i > -1 && i < pos)) { pos = i; }
      });
      if (pos < 0) { pos = 0; }
      var ini = Math.max(0, pos - 120);
      var fim = Math.min(texto.length, ini + 290);
      return (ini > 0 ? '… ' : '') + texto.slice(ini, fim).trim() + (fim < texto.length ? ' …' : '');
    }

    function busca(pergunta) {
      var termos = semAcento(pergunta).split(/[^a-z0-9]+/).filter(function (t) { return t.length > 2; });
      return carregaRag().then(function (dados) {
        return dados.map(function (r) {
          var alvo = semAcento([r.titulo, r.autor, (r.temas || []).join(' '), r.texto].join(' '));
          var nota = 0;
          termos.forEach(function (t) {
            var n = alvo.split(t).length - 1;
            if (n) { nota += Math.min(n, 6) * (t.length > 4 ? 3 : 1); }
            if (semAcento(r.titulo || '').indexOf(t) > -1) { nota += 8; }
          });
          return { r: r, nota: nota };
        }).filter(function (x) { return x.nota > 0; })
          .sort(function (a, b) { return b.nota - a.nota; })
          .slice(0, 4)
          .map(function (x) { return { r: x.r, termos: termos }; });
      });
    }

    function itemHtml(x) {
      var r = x.r;
      var titulo = escapa(r.titulo || '');
      return '<li class="assistente__item"><a href="' + r.slug + '.html">' + titulo + '</a>' +
        '<span>' + escapa(r.autor || '') + ' · ' + escapa(r.ano || '') + ' · ' + escapa(r.tema || '') + '</span>' +
        '<p class="assistente__trecho">' + escapa(trecho(r.texto || '', x.termos)) + '</p></li>';
    }

    painel.querySelector('[data-assistente-toggle]').addEventListener('click', function () {
      var aberto = painel.dataset.aberto === 'true';
      painel.dataset.aberto = String(!aberto);
      this.setAttribute('aria-expanded', String(!aberto));
      var d = document.querySelector('.casca-dial');
      if (d) { d.dataset.visivel = aberto ? 'true' : 'false'; }
      if (!aberto) { campo.focus(); }
    });
    painel.querySelector('[data-assistente-fechar]').addEventListener('click', function () {
      painel.dataset.aberto = 'false';
      painel.querySelector('[data-assistente-toggle]').setAttribute('aria-expanded', 'false');
      var d = document.querySelector('.casca-dial');
      if (d) { d.dataset.visivel = 'true'; }
    });
    painel.querySelector('.assistente__form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var pergunta = campo.value.trim();
      if (!pergunta) { return; }
      var alvo = semAcento(pergunta);
      var curada = curadas.filter(function (q) {
        var p = semAcento(q.pergunta);
        return p.indexOf(alvo) > -1 || alvo.indexOf(p) > -1;
      })[0];
      if (curada) { mostraCurada(curada); return; }
      status.textContent = 'Procurando nos textos…';
      lista.innerHTML = '';
      busca(pergunta).then(function (achados) {
        if (!achados.length) {
          status.textContent = 'Não achei isso no acervo. Tente outra palavra ou use a busca.';
          return;
        }
        status.textContent = achados.length + ' trechos com fonte. Sem geração livre.';
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
  })();

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

  // ── Ímã: botões e atalhos seguem de leve o ponteiro ─────────────────────
  (function ima() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { return; }
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) { return; }
    var alvos = document.querySelectorAll('.botao, .chip-f, .radio-flut__botao, .assistente__botao, .menu__botao, .topo__abrir, .casca-dial__botao, .casca-dial__acoes button, .topo__marca');
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

  // ── Magic card: holofote que segue o ponteiro ───────────────────────────
  (function magicCards() {
    var cards = document.querySelectorAll('a.cartao, .item__link, .destaque, .bento__item');
    Array.prototype.forEach.call(cards, function (card) {
      card.addEventListener('pointermove', function (ev) {
        var r = card.getBoundingClientRect();
        card.style.setProperty('--mx', ((ev.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        card.style.setProperty('--my', ((ev.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      });
    });
  })();

  // ── Electro border: no máximo dois por página ───────────────────────────
  (function electro() {
    if (!document.getElementById('electro-filtro')) {
      var caixaFiltro = document.createElement('div');
      caixaFiltro.setAttribute('aria-hidden', 'true');
      caixaFiltro.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
      caixaFiltro.innerHTML =
        '<svg xmlns="http://www.w3.org/2000/svg">' +
        '<defs>' +
        '<filter id="electro-filtro" color-interpolation-filters="sRGB" x="-20%" y="-20%" width="140%" height="140%">' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise1" seed="1" />' +
        '<feOffset in="noise1" dx="0" dy="0" result="offsetNoise1"><animate attributeName="dy" values="460; 0" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise2" seed="1" />' +
        '<feOffset in="noise2" dx="0" dy="0" result="offsetNoise2"><animate attributeName="dy" values="0; -460" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise3" seed="2" />' +
        '<feOffset in="noise3" dx="0" dy="0" result="offsetNoise3"><animate attributeName="dx" values="336; 0" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise4" seed="2" />' +
        '<feOffset in="noise4" dx="0" dy="0" result="offsetNoise4"><animate attributeName="dx" values="0; -336" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feComposite in="offsetNoise1" in2="offsetNoise2" result="part1" />' +
        '<feComposite in="offsetNoise3" in2="offsetNoise4" result="part2" />' +
        '<feBlend in="part1" in2="part2" mode="color-dodge" result="combinedNoise" />' +
        '<feDisplacementMap in="SourceGraphic" in2="combinedNoise" scale="30" xChannelSelector="R" yChannelSelector="B" />' +
        '</filter>' +
        '<filter id="electro-filtro-parado" color-interpolation-filters="sRGB" x="-20%" y="-20%" width="140%" height="140%">' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise1" seed="1" />' +
        '<feOffset in="noise1" dx="0" dy="0" result="offsetNoise1" />' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise2" seed="1" />' +
        '<feOffset in="noise2" dx="0" dy="0" result="offsetNoise2" />' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise3" seed="2" />' +
        '<feOffset in="noise3" dx="0" dy="0" result="offsetNoise3" />' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise4" seed="2" />' +
        '<feOffset in="noise4" dx="0" dy="0" result="offsetNoise4" />' +
        '<feComposite in="offsetNoise1" in2="offsetNoise2" result="part1" />' +
        '<feComposite in="offsetNoise3" in2="offsetNoise4" result="part2" />' +
        '<feBlend in="part1" in2="part2" mode="color-dodge" result="combinedNoise" />' +
        '<feDisplacementMap in="SourceGraphic" in2="combinedNoise" scale="30" xChannelSelector="R" yChannelSelector="B" />' +
        '</filter>' +
        '</defs></svg>';
      document.body.appendChild(caixaFiltro);
    }
    function semAcento(t) {
      return (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }

    function pontuaAtemporal(el) {
      var li = el.closest('.item');
      if (!li || li.hidden) { return -99; }
      var tipo = semAcento(li.getAttribute('data-tipo') || '');
      var titulo = semAcento(li.getAttribute('data-titulo') || '');
      var resumo = el.querySelector('p') ? el.querySelector('p').textContent : '';
      var nota = 0;
      if (tipo === 'formativo') { nota += 5; }
      else if (tipo === 'resenha') { nota += 4; }
      else if (tipo === 'poesia') { nota += 2; }
      else if (tipo === 'evento' || tipo === 'noticia' || tipo === 'documento') { nota -= 6; }
      nota += Math.min(4, resumo.length / 60);
      var ruins = ['programacao', 'convite', 'inscri', 'oficina', 'encontro', 'seminario',
        'mesa', 'debate', 'live', 'aula', 'curso', 'jornada', 'evento', 'festival',
        'mostra', 'lancamento', 'assembleia', 'abaixo-assinado', 'convocatoria', 'selecao'];
      if (ruins.some(function (w) { return titulo.indexOf(w) > -1; })) { nota -= 7; }
      var bons = ['direito', 'assessoria', 'teoria', 'critica', 'movimento', 'terra',
        'trabalho', 'democracia', 'constituicao', 'racismo', 'genero', 'educacao',
        'justica', 'reforma', 'politica'];
      if (bons.some(function (w) { return titulo.indexOf(w) > -1; })) { nota += 2; }
      return nota;
    }

    // Electric só em card grande: bento da home ou hero da seção.
    var grande = document.querySelector('.bento__item--grande');
    var hero = document.querySelector('.hero__interno');
    var alvos = grande ? [grande] : (hero ? [hero] : []);
    alvos.forEach(function (el) {
      el.classList.add('electro');
      var aura = document.createElement('span');
      aura.className = 'electro__aura';
      aura.setAttribute('aria-hidden', 'true');
      el.appendChild(aura);
    });

    // Meteor Impact Border nos cards visíveis de acervo, posts e destaques.
    function marcaMeteoros() {
      var links = Array.prototype.slice.call(document.querySelectorAll('.item__link'));
      var candidatos;
      if (links.length) {
        var visiveis = links.filter(function (a) {
          var li = a.closest('.item');
          return li && !li.hidden;
        });
        candidatos = (visiveis.length ? visiveis : links.slice(0, 24));
        candidatos.sort(function (a, b) { return pontuaAtemporal(b) - pontuaAtemporal(a); });
      } else {
        candidatos = Array.prototype.slice.call(
          document.querySelectorAll('.cp-cartao, .tl__cartao, figure.cartao')
        );
      }
      candidatos.slice(0, 2).forEach(function (el) {
        if (!el.classList.contains('meteoro-borda')) { el.classList.add('meteoro-borda'); }
      });
    }
    if (document.readyState === 'complete') { marcaMeteoros(); }
    else { window.addEventListener('load', marcaMeteoros); }
  })();

  // ── Busca expansível: limpar com um clique ──────────────────────────────
  (function buscaExpansivel() {
    var campos = document.querySelectorAll('[data-busca], .busca__campo input[type="search"]');
    Array.prototype.forEach.call(campos, function (campo) {
      if (campo.parentNode.querySelector('.busca__limpar')) { return; }
      var limpar = document.createElement('button');
      limpar.type = 'button';
      limpar.className = 'busca__limpar';
      limpar.setAttribute('aria-label', 'Limpar a busca');
      limpar.textContent = '×';
      campo.insertAdjacentElement('afterend', limpar);
      limpar.addEventListener('click', function () {
        campo.value = '';
        campo.dispatchEvent(new Event('input', { bubbles: true }));
        campo.focus();
      });
    });
  })();

  // ── Busca na barra do topo (telas estreitas) ───────────────────────────
  (function buscaNoTopo() {
    var interno = document.querySelector('.topo__interno');
    if (!interno || interno.querySelector('.topo__busca-movel')) { return; }
    if (document.querySelector('.busca-global')) { return; }
    var form = document.createElement('form');
    form.className = 'topo__busca-movel';
    form.setAttribute('role', 'search');
    form.innerHTML =
      '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
      '<input type="search" aria-label="Buscar no acervo" placeholder="Buscar no acervo" autocomplete="off" />';
    interno.appendChild(form);

    var campo = form.querySelector('input');
    var principal = document.querySelector('[data-busca]');
    if (principal) {
      campo.addEventListener('input', function () {
        principal.value = campo.value;
        principal.dispatchEvent(new Event('input', { bubbles: true }));
      });
    }
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var termo = campo.value.trim();
      if (!termo) { return; }
      if (principal) {
        principal.value = termo;
        principal.dispatchEvent(new Event('input', { bubbles: true }));
        principal.scrollIntoView({ behavior: 'smooth', block: 'center' });
        window.setTimeout(function () { principal.focus(); }, 380);
      } else {
        try { sessionStorage.setItem('ajp-busca', termo); } catch (e) {}
        window.location.href = 'acervo.html?q=' + encodeURIComponent(termo) + '#lista-acervo';
      }
    });

    window.addEventListener('load', function () {
      var params = new URLSearchParams(window.location.search);
      var termo = params.get('q') || '';
      if (!termo) {
        try {
          termo = sessionStorage.getItem('ajp-busca') || '';
          if (termo) { sessionStorage.removeItem('ajp-busca'); }
        } catch (e) {}
      }
      if (!termo || !principal) { return; }
      principal.value = termo;
      principal.dispatchEvent(new Event('input', { bubbles: true }));
      principal.scrollIntoView({ block: 'center' });
      if (params.get('q')) {
        try { history.replaceState(null, '', window.location.pathname + window.location.hash); } catch (e) {}
      }
    });
  })();

  // ── Navegação dinâmica: pílula e tubelight seguem o item ativo ─────────
  (function navDinamica() {
    var nav = document.querySelector('.topo__links');
    if (!nav) { return; }
    var pilha = document.createElement('span');
    pilha.className = 'topo__pilha';
    pilha.setAttribute('aria-hidden', 'true');
    var tubo = document.createElement('span');
    tubo.className = 'topo__tubo';
    tubo.setAttribute('aria-hidden', 'true');
    nav.appendChild(pilha);
    nav.appendChild(tubo);

    var ativo = nav.querySelector(':scope > a[aria-current="page"]');
    if (!ativo) {
      var dentro = nav.querySelector('.menu__lista a[aria-current="page"]');
      if (dentro) {
      var menuAtivo = dentro.closest('.menu');
      ativo = menuAtivo ? menuAtivo.querySelector('.menu__botao') : null;
    }
    }
    if (!ativo) { ativo = nav.querySelector('.menu__botao[aria-current="page"]'); }

    function move(el) {
      if (!el) {
        pilha.style.opacity = '0';
        tubo.style.opacity = '0';
        return;
      }
      var nr = nav.getBoundingClientRect();
      var r = el.getBoundingClientRect();
      if (r.width < 2) { return; }
      var esq = r.left - nr.left;
      pilha.style.left = esq + 'px';
      pilha.style.width = r.width + 'px';
      pilha.style.opacity = '1';
      tubo.style.left = (esq + 8) + 'px';
      tubo.style.width = Math.max(8, r.width - 16) + 'px';
      tubo.style.opacity = '1';
    }

    Array.prototype.forEach.call(nav.querySelectorAll('a, .menu__botao'), function (el) {
      if (el.closest('.menu__lista')) { return; }
      el.addEventListener('pointerenter', function () { move(el); });
      el.addEventListener('focus', function () { move(el); });
    });
    nav.addEventListener('pointerleave', function () { move(ativo); });
    function reposiciona() { move(ativo); }
    window.addEventListener('resize', reposiciona);
    window.addEventListener('load', function () {
      reposiciona();
      window.setTimeout(reposiciona, 250);
      window.setTimeout(reposiciona, 900);
    });
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        reposiciona();
        window.setTimeout(reposiciona, 150);
      });
    }
    if (window.ResizeObserver) { new ResizeObserver(reposiciona).observe(nav); }
    reposiciona();
  })();

  // ── Seções caem ao entrar na tela (falling sections) ───────────────────
  (function secoesCaindo() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { return; }
    if (!('IntersectionObserver' in window)) { return; }
    var alvos = document.querySelectorAll('.pagina .secao, .miolo > .secao, .referencias');
    if (!alvos.length) { return; }
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (entrada.isIntersecting) {
          entrada.target.dataset.caiu = 'true';
          observador.unobserve(entrada.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' });
    Array.prototype.forEach.call(alvos, function (el) {
      el.classList.add('cai');
      observador.observe(el);
    });
  })();

  // Acordeões: abre o <details> quando o endereço aponta para ele
  (function acordeoes() {
    function abre() {
      if (!location.hash) { return; }
      var alvo = document.getElementById(location.hash.slice(1));
      if (alvo && alvo.tagName === 'DETAILS') { alvo.open = true; }
    }
    abre();
    window.addEventListener('hashchange', abre);
  })();

  // Barra wiki: anterior, índice e próxima entre as páginas principais
  (function wikiNav() {
    var ordem = [
      ['acervo.html', 'Acervo'],
      ['blog.html', 'Blog'],
      ['autores.html', 'Autores'],
      ['memoria.html', 'Memória'],
      ['formacao.html', 'Formação'],
      ['biblioteca.html', 'Biblioteca'],
      ['cultura.html', 'Cultura'],
      ['assessoria-juridica-popular-no-mundo.html', 'AJP pelo mundo']
    ];
    var atual = location.pathname.split('/').pop() || 'index.html';
    var pos = -1;
    for (var i = 0; i < ordem.length; i += 1) {
      if (ordem[i][0] === atual) { pos = i; }
    }
    var main = document.querySelector('main');
    if (pos < 0 || !main || main.querySelector('.wiki-nav')) { return; }
    var nav = document.createElement('nav');
    nav.className = 'wiki-nav';
    nav.setAttribute('aria-label', 'Navegação entre páginas');
    var partes = [];
    if (pos > 0) {
      partes.push('<a class="wiki-nav__ant" href="' + ordem[pos - 1][0] + '">← ' + ordem[pos - 1][1] + '</a>');
    } else {
      partes.push('<span class="wiki-nav__vazio"></span>');
    }
    partes.push('<a class="wiki-nav__indice" href="indice.html">Índice</a>');
    if (pos < ordem.length - 1) {
      partes.push('<a class="wiki-nav__prox" href="' + ordem[pos + 1][0] + '">' + ordem[pos + 1][1] + ' →</a>');
    }
    nav.innerHTML = partes.join('');
    main.appendChild(nav);
  })();

})();
