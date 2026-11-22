/**
 * RÁDIO — player estático com o acervo do Controle Popular.
 *
 * Porte fiel do `PlayerRadio.tsx` e do medidor `SloshGauge.tsx` do portal
 * (X:\DevCoder\controle-popular): índice em duas colunas, grupos por tipo,
 * logo da emissora, bandeiras de país e estado, dica com a descrição depois
 * de 1 s e volume com líquido à direita. Sem framework: a apresentação é um
 * HTML só e precisa abrir no celular.
 *
 * Dados em `componentes/radio-dados.js`, gerados de
 * `apps/web/lib/radio/estacoes.ts`. Só HTTPS, por causa de conteúdo misto.
 * HLS (`.m3u8`) não toca no Chrome: o hls.js entra sob demanda, só quando
 * alguém escolhe uma emissora nesse formato.
 *
 * Contratos: [data-radio] raiz, [data-radio-audio] <audio>,
 * [data-radio-lista], [data-radio-medidor], [data-radio-mudo],
 * [data-radio-status].
 */
(function () {
  "use strict";

  var dados = window.RADIO_DADOS;
  if (!dados) { return; }

  var raiz = document.querySelector("[data-radio]");
  if (!raiz) { return; }

  var lista = raiz.querySelector("[data-radio-lista]");
  var statusEl = raiz.querySelector("[data-radio-status]");
  var medidorEl = raiz.querySelector("[data-radio-medidor]");
  var mudoEl = raiz.querySelector("[data-radio-mudo]");
  var pctEl = raiz.querySelector("[data-radio-pct]");
  var botaoFlut = raiz.querySelector(".radio-flut__botao");

  var ESTACOES = dados.estacoes;
  var audio = raiz.querySelector("[data-radio-audio]");
  var atual = null;
  var tocando = false;
  var carregando = false;
  var volume = 100;
  var mudo = false;
  var hls = null;
  var hlsPronto = false;
  var medidor = null;
  var dicaTimer = null;
  var dicaAberta = null;

  var ICO_PLAY =
    '<svg class="rp__icone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="6 3 20 12 6 21 6 3"/></svg>';
  var ICO_PAUSE =
    '<svg class="rp__icone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="14" y="4" width="4" height="16" rx="1"/><rect x="6" y="4" width="4" height="16" rx="1"/></svg>';
  var ICO_VOLUME =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
  var ICO_MUDO =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="22" x2="16" y1="9" y2="15"/><line x1="16" x2="22" y1="9" y2="15"/></svg>';

  function el(tag, classe, texto) {
    var e = document.createElement(tag);
    if (classe) { e.className = classe; }
    if (texto) { e.textContent = texto; }
    return e;
  }

  function limitar(v, a, b) {
    return Math.min(b, Math.max(a, v));
  }

  function aviso(texto) {
    if (statusEl) { statusEl.textContent = texto || ""; }
  }

  /* ── Dados e ordem: a mesma régua de `compararEstacoes` do portal ─────── */
  function nomeDoEstado(e) {
    return e.uf ? (dados.nomeEstado[e.uf.trim().toUpperCase()] || e.uf) : "\uffff";
  }

  function comparar(a, b) {
    var ra = dados.ordemRegioes.indexOf(a.regiao);
    var rb = dados.ordemRegioes.indexOf(b.regiao);
    if (ra !== rb) { return ra - rb; }

    if (a.pais === "BR" && b.pais === "BR") {
      var ea = nomeDoEstado(a);
      var eb = nomeDoEstado(b);
      if (ea !== eb) { return ea.localeCompare(eb, "pt-BR"); }
    } else if (a.pais !== b.pais) {
      return String(a.paisNome || "").localeCompare(String(b.paisNome || ""), "pt-BR");
    }

    return String(a.nome || "").localeCompare(String(b.nome || ""), "pt-BR");
  }

  var ORDENADAS = ESTACOES.slice().sort(comparar);

  /* ── Logo: hotlink da fonte e monograma quando a imagem falha ─────────── */
  function monograma(nome) {
    var palavras = String(nome || "")
      .replace(/[^\p{L}\p{N}\s]/gu, " ")
      .split(/\s+/)
      .filter(function (p) {
        return p.length > 0 && !/^(de|da|do|das|dos|fm|am|radio|rádio)$/i.test(p);
      });
    var letras = palavras.slice(0, 2).map(function (p) {
      return (p[0] || "").toUpperCase();
    });
    return letras.join("") || String(nome || "").slice(0, 2).toUpperCase();
  }

  function logoMonograma(e) {
    var s = el("span", "rp__logo rp__logo--monograma", monograma(e.nome));
    s.setAttribute("aria-hidden", "true");
    return s;
  }

  function logoEfetiva(e) {
    if (e.logo) { return e.logo; }
    try {
      return new URL(e.site).origin + "/favicon.ico";
    } catch (err) {
      return "";
    }
  }

  function criaLogo(e) {
    var src = logoEfetiva(e);
    if (!src) { return logoMonograma(e); }

    var img = document.createElement("img");
    img.className = "rp__logo";
    img.src = src;
    img.alt = "";
    img.width = 22;
    img.height = 22;
    img.loading = "lazy";
    img.decoding = "async";
    img.referrerPolicy = "no-referrer";
    img.addEventListener("error", function () {
      if (img.parentNode) { img.parentNode.replaceChild(logoMonograma(e), img); }
    });
    return img;
  }

  /* ── Bandeiras: país no flagcdn e estado no Commons, como no portal ───── */
  function urlBandeiraEstado(uf) {
    var arquivo = uf ? dados.bandeiraEstado[uf.trim().toUpperCase()] : null;
    if (!arquivo) { return ""; }
    return (
      "https://commons.wikimedia.org/wiki/Special:FilePath/" +
      encodeURIComponent(arquivo) +
      "?width=40"
    );
  }

  function imagemBandeira(src, alt, titulo) {
    var img = document.createElement("img");
    img.src = src;
    img.alt = alt;
    if (titulo) { img.title = titulo; }
    img.loading = "lazy";
    img.decoding = "async";
    img.referrerPolicy = "no-referrer";
    return img;
  }

  function criaBandeiras(e) {
    var caixa = el("span", "rp__bandeiras");

    if (e.pais && /^[a-z]{2}$/i.test(e.pais)) {
      caixa.appendChild(
        imagemBandeira(
          "https://flagcdn.com/" + e.pais.toLowerCase() + ".svg",
          "Bandeira de " + (e.paisNome || "país")
        )
      );
    }

    var urlEstado = urlBandeiraEstado(e.uf);
    if (urlEstado) {
      var nome = dados.nomeEstado[e.uf.trim().toUpperCase()] || e.uf;
      caixa.appendChild(
        imagemBandeira(urlEstado, "Bandeira de " + nome, "Bandeira de " + nome)
      );
    }

    return caixa;
  }

  /* ── Dica "hover up": 1 s no item, fecha ao sair ou clicar ───────────── */
  function escondeDica() {
    if (dicaTimer) {
      window.clearTimeout(dicaTimer);
      dicaTimer = null;
    }
    if (dicaAberta) {
      var li = dicaAberta.parentNode;
      var botao = li ? li.querySelector(".rp__item") : null;
      if (botao) { botao.removeAttribute("aria-describedby"); }
      dicaAberta.remove();
      dicaAberta = null;
    }
  }

  function mostraDica(li, e, botao) {
    escondeDica();
    var texto = e.descricao || e.programacao || "";
    if (!texto) { return; }
    var dica = el("span", "rp__dica", texto);
    dica.id = "rp-dica-" + e.id;
    dica.setAttribute("role", "tooltip");
    li.appendChild(dica);
    botao.setAttribute("aria-describedby", dica.id);
    dicaAberta = dica;
  }

  /* ── Item do índice ──────────────────────────────────────────────────── */
  function criaItem(e) {
    var li = el("li", "rp__li");
    var botao = el("button", "rp__item");
    botao.type = "button";
    botao.dataset.id = e.id;

    botao.appendChild(criaLogo(e));
    botao.appendChild(el("span", "rp__item-nome", e.nome));

    var sintonizando = el("span", "rp__sintonizando", "Sintonizando…");
    sintonizando.hidden = true;
    botao.appendChild(sintonizando);

    botao.appendChild(criaBandeiras(e));
    botao.insertAdjacentHTML("beforeend", ICO_PLAY);

    botao.addEventListener("pointerdown", escondeDica);
    botao.addEventListener("click", function () {
      escondeDica();
      escolhe(e);
    });
    botao.addEventListener("mouseenter", function () {
      if (dicaTimer) { window.clearTimeout(dicaTimer); }
      dicaTimer = window.setTimeout(function () {
        dicaTimer = null;
        mostraDica(li, e, botao);
      }, 1000);
    });
    botao.addEventListener("mouseleave", escondeDica);
    botao.addEventListener("focus", function () { mostraDica(li, e, botao); });
    botao.addEventListener("blur", escondeDica);

    li.appendChild(botao);
    return li;
  }

  function desenhaLista() {
    if (!lista) { return; }
    var frag = document.createDocumentFragment();

    dados.ordemTipos.forEach(function (tipo) {
      var grupo = ORDENADAS.filter(function (e) { return e.tipo === tipo; });
      if (!grupo.length) { return; }

      var bloco = el("div", "rp__grupo-bloco");
      bloco.appendChild(el("p", "rp__grupo", dados.rotuloTipo[tipo]));

      var ul = el("ul", "rp__ul");
      grupo.forEach(function (e) { ul.appendChild(criaItem(e)); });
      bloco.appendChild(ul);
      frag.appendChild(bloco);
    });

    lista.innerHTML = "";
    lista.appendChild(frag);
  }

  /* ── Estado dos itens ────────────────────────────────────────────────── */
  function atualiza() {
    if (lista) {
      var itens = lista.querySelectorAll(".rp__item");
      for (var i = 0; i < itens.length; i++) {
        var item = itens[i];
        var ativa = !!atual && item.dataset.id === atual.id;
        item.classList.toggle("rp__item--ativa", ativa);

        var ico = item.querySelector(".rp__icone");
        if (ico) {
          ico.outerHTML = ativa && tocando ? ICO_PAUSE : ICO_PLAY;
        }

        var sinal = item.querySelector(".rp__sintonizando");
        if (sinal) { sinal.hidden = !(ativa && carregando); }
      }
    }

    if (botaoFlut) {
      botaoFlut.dataset.tocando = tocando ? "true" : "false";
      botaoFlut.setAttribute(
        "aria-label",
        tocando
          ? "Pausar " + (atual ? atual.nome : "a rádio")
          : "Ouvir " + (atual ? atual.nome : "a rádio")
      );
    }
  }

  /* ── Áudio: um elemento por troca de emissora ────────────────────────── */
  function audioNovo() {
    var antigo = audio;
    var novo = document.createElement("audio");
    novo.setAttribute("data-radio-audio", "");
    novo.preload = "none";
    novo.volume = volume / 100;
    novo.muted = mudo;

    novo.addEventListener("play", function () {
      if (novo !== audio) { return; }
      tocando = true;
      carregando = false;
      atualiza();
    });
    novo.addEventListener("playing", function () {
      if (novo !== audio) { return; }
      carregando = false;
      tocando = true;
      atualiza();
    });
    novo.addEventListener("pause", function () {
      if (novo !== audio) { return; }
      tocando = false;
      carregando = false;
      atualiza();
    });
    novo.addEventListener("waiting", function () {
      if (novo !== audio) { return; }
      carregando = true;
      atualiza();
    });
    novo.addEventListener("error", function () {
      if (novo !== audio || !novo.getAttribute("src")) { return; }
      aviso("Esta estação não abriu. Tente outra.");
      tocando = false;
      carregando = false;
      atualiza();
    });

    if (antigo && antigo.parentNode) {
      antigo.parentNode.replaceChild(novo, antigo);
    } else {
      raiz.appendChild(novo);
    }
    return novo;
  }

  function limpa() {
    if (hls) {
      try { hls.destroy(); } catch (err) { /* instância já descartada */ }
      hls = null;
    }
    if (audio) {
      audio.pause();
      audio.removeAttribute("src");
      try { audio.load(); } catch (err) { /* elemento já descartado */ }
    }
  }

  /* Para TODO áudio da página. É o cinto de segurança: se sobrou um elemento
     de uma troca anterior (ou de outra aba interna), ele cala aqui. */
  function pararTudo() {
    limpa();
    var todos = document.querySelectorAll("audio");
    for (var i = 0; i < todos.length; i++) {
      try {
        todos[i].pause();
        if (todos[i] !== audio) {
          todos[i].removeAttribute("src");
          todos[i].load();
        }
      } catch (err) { /* elemento já descartado */ }
    }
    tocando = false;
    carregando = false;
    atualiza();
  }

  function estacaoPadrao() {
    for (var i = 0; i < ESTACOES.length; i++) {
      if (ESTACOES[i].id === "radio-brasil-de-fato") { return ESTACOES[i]; }
    }
    return ESTACOES[0];
  }

  function carregaHls() {
    return new Promise(function (resolve, reject) {
      if (hlsPronto || window.Hls) { hlsPronto = true; resolve(); return; }
      var s = document.createElement("script");
      s.src = "https://cdn.jsdelivr.net/npm/hls.js@1/dist/hls.min.js";
      s.onload = function () { hlsPronto = true; resolve(); };
      s.onerror = function () { reject(new Error("hls")); };
      document.head.appendChild(s);
    });
  }

  function comAudio(alvo, e) {
    if (alvo !== audio) { return; }
    alvo.play().then(function () {
      if (alvo !== audio) { return; }
      tocando = true;
      carregando = false;
      atualiza();
      aviso("Tocando " + e.nome + " ao vivo.");
      if ("mediaSession" in navigator) {
        try {
          navigator.mediaSession.metadata = new window.MediaMetadata({
            title: e.nome,
            artist: "Rádio · RENAP",
            album: [e.cidade, e.uf].filter(Boolean).join(" / ")
          });
        } catch (err) { /* MediaMetadata indisponível */ }
      }
    }).catch(function () {
      if (alvo !== audio) { return; }
      carregando = false;
      tocando = false;
      atualiza();
      aviso("O navegador pediu um toque a mais. Toque na estação de novo.");
    });
  }

  function toca(e) {
    pararTudo();
    audio = audioNovo();
    var alvo = audio;
    atual = e;
    carregando = true;
    tocando = false;
    atualiza();
    aviso("Conectando a " + e.nome + "…");

    var nativo = alvo.canPlayType("application/vnd.apple.mpegurl") !== "";

    if (e.formato === "hls" && !nativo) {
      carregaHls().then(function () {
        if (alvo !== audio) { return; }
        if (window.Hls && window.Hls.isSupported()) {
          hls = new window.Hls({ lowLatencyMode: false });
          hls.loadSource(e.stream);
          hls.attachMedia(alvo);
          hls.on(window.Hls.Events.ERROR, function (_evt, detalhe) {
            if (detalhe && detalhe.fatal && alvo === audio) {
              aviso("Esta estação não abriu. Tente outra.");
              tocando = false;
              carregando = false;
              atualiza();
            }
          });
          comAudio(alvo, e);
        } else {
          alvo.src = e.stream;
          alvo.load();
          comAudio(alvo, e);
        }
      }).catch(function () {
        if (alvo !== audio) { return; }
        carregando = false;
        atualiza();
        aviso("Sem a biblioteca de HLS: esta estação não toca aqui.");
      });
      return;
    }

    alvo.src = e.stream;
    alvo.load();
    comAudio(alvo, e);
  }

  function escolhe(e) {
    if (atual && atual.id === e.id) {
      if (tocando) {
        audio.pause();
      } else if (audio) {
        audio.play().catch(function () {
          aviso("O navegador pediu um toque a mais. Toque na estação de novo.");
        });
      } else {
        toca(e);
      }
      return;
    }
    toca(e);
  }

  /* ── Volume: medidor de líquido, mudo e memória ──────────────────────── */
  function corSobre(cor) {
    var bruto = String(cor || "").trim().replace("#", "");
    var completo = bruto.length === 3
      ? bruto.split("").map(function (c) { return c + c; }).join("")
      : bruto;
    var n = parseInt(completo, 16);
    if (isNaN(n) || !/^[0-9a-f]{6}$/i.test(completo)) { return "#ffffff"; }
    var lum = (((n >> 16) & 255) * 299 + ((n >> 8) & 255) * 587 + (n & 255) * 114) / 1000;
    return lum >= 150 ? "#111111" : "#ffffff";
  }

  function pintaCoresDoMedidor() {
    if (!medidorEl) { return; }
    var cor = getComputedStyle(document.documentElement).getPropertyValue("--cp-primary").trim();
    medidorEl.style.setProperty("--sg-on-liquid", corSobre(cor));
  }

  function aplicaVolume(semMedidor) {
    if (audio) {
      audio.volume = volume / 100;
      audio.muted = mudo;
    }

    try { localStorage.setItem("renap-volume", String(volume)); } catch (err) { /* modo privado */ }

    var mostrado = mudo || volume === 0 ? 0 : volume;
    if (medidor && !semMedidor) { medidor.definir(mostrado, true); }
    if (pctEl) { pctEl.textContent = mudo || volume === 0 ? "mudo" : volume + "%"; }

    if (mudoEl) {
      mudoEl.innerHTML = mudo || volume === 0 ? ICO_MUDO : ICO_VOLUME;
      mudoEl.setAttribute("aria-pressed", String(mudo));
      mudoEl.setAttribute("aria-label", mudo ? "Ativar som da rádio" : "Silenciar rádio");
      mudoEl.setAttribute("title", mudo ? "Ativar som" : "Silenciar");
    }
  }

  /* Medidor de nível com líquido agitado (Slosh Gauge, React Bits, MIT +
     Commons Clause, copiado do portal em 06/10/2026). Em JS puro: a física
     é a mesma — mola-amortecida mirando o alvo, inclinação proporcional à
     velocidade e rebote nas bordas. `prefers-reduced-motion` desliga a onda. */
  function medidorLiquido(raizEl, opcoes) {
    var liquido = raizEl.querySelector(".rp__liquido");
    var marca = raizEl.querySelector(".rp__marca");
    var textos = raizEl.querySelectorAll(".rp__valor");
    var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)");
    var H = 1 / 120;
    var DT_MAX = 0.05;
    var GANHO_INCLINACAO = 0.07;
    var INCLINACAO_MAX = 30;
    var REPOUSO_POS = 0.05;
    var REPOUSO_VEL = 2;
    var PASSO = 2;
    var GRANDE = 10;
    var FAIXA = 10;
    var sim = { x: opcoes.valor, v: 0, L: opcoes.valor, raf: 0, ultimo: 0 };
    var pegada = null;

    function pintar() {
      var altura = raizEl.offsetHeight || 1;
      var largura = raizEl.offsetWidth || 1;
      var inclinacao = reduzido.matches ? 0 : limitar(0.45 * sim.v * GANHO_INCLINACAO, -INCLINACAO_MAX, INCLINACAO_MAX);
      var inclinar = (Math.tan((inclinacao * Math.PI) / 180) * largura) / 2;
      var topo = 100 - sim.x;
      if (liquido) {
        liquido.style.clipPath =
          "polygon(0 calc(" + topo + "% + " + inclinar + "px), 100% calc(" +
          topo + "% - " + inclinar + "px), 100% 100%, 0 100%)";
      }
      if (marca) {
        marca.style.transform = "translateY(" + ((100 - sim.L) * altura) / 100 + "px)";
      }
    }

    function anunciar() {
      var n = Math.round(sim.L);
      raizEl.setAttribute("aria-valuenow", String(n));
      for (var i = 0; i < textos.length; i++) {
        textos[i].textContent = n + "%";
      }
    }

    function bater(agora) {
      var dt = sim.ultimo ? Math.min((agora - sim.ultimo) / 1000, DT_MAX) : H;
      sim.ultimo = agora;
      var k = 1224 - 1044 * 0.15;
      var zeta = reduzido.matches ? 1 : 0.26 - 0.17 * 0.15;
      var c = 2 * zeta * Math.sqrt(k);
      var repouso = reduzido.matches ? 0 : 0.42;
      var n = Math.ceil(dt / H);
      var h = dt / n;

      for (; n > 0; n -= 1) {
        sim.v = sim.v * Math.exp(-c * h) + k * (sim.L - sim.x) * h;
        sim.x += sim.v * h;
        if (sim.x > 100) {
          sim.x = 100;
          sim.v = -sim.v * repouso;
        } else if (sim.x < 0) {
          sim.x = 0;
          sim.v = -sim.v * repouso;
        }
      }

      if (!pegada && Math.abs(sim.L - sim.x) < REPOUSO_POS && Math.abs(sim.v) < REPOUSO_VEL) {
        sim.x = sim.L;
        sim.v = 0;
      }

      pintar();
      if (!pegada && sim.x === sim.L && sim.v === 0) {
        sim.raf = 0;
        sim.ultimo = 0;
      } else {
        sim.raf = window.requestAnimationFrame(bater);
      }
    }

    function acordar() {
      if (!sim.raf) { sim.raf = window.requestAnimationFrame(bater); }
    }

    function definir(n, instantaneo) {
      sim.L = limitar(n, 0, 100);
      if (instantaneo) {
        sim.x = sim.L;
        sim.v = 0;
      }
      anunciar();
      pintar();
      acordar();
    }

    function nivelEm(clientY, g) {
      var altura = raizEl.offsetHeight || g.rect.height;
      return limitar((((g.rect.bottom - clientY) / g.escala) / altura) * 100, 0, 100);
    }

    function reportar() {
      var n = Math.round(sim.L);
      if (pegada && n !== pegada.enviado) {
        pegada.enviado = n;
        if (opcoes.aoMudar) { opcoes.aoMudar(n); }
      }
    }

    function pressionar(ev) {
      if (pegada || ev.button !== 0) { return; }
      var rect = raizEl.getBoundingClientRect();
      var escala = rect.height / (raizEl.offsetHeight || rect.height) || 1;
      var yMarca = rect.top + ((100 - sim.L) / 100) * rect.height;
      pegada = {
        id: ev.pointerId,
        rect: rect,
        escala: escala,
        faixa: Math.abs(ev.clientY - yMarca) <= FAIXA * escala,
        agarre: null,
        inicio: sim.L,
        enviado: NaN
      };
      raizEl.dataset.held = "true";
      try { raizEl.setPointerCapture(ev.pointerId); } catch (err) { /* melhor esforço */ }
      if (pegada.faixa) {
        acordar();
      } else {
        definir(nivelEm(ev.clientY, pegada));
        reportar();
      }
    }

    function mover(ev) {
      if (!pegada || pegada.id !== ev.pointerId) { return; }
      var em = nivelEm(ev.clientY, pegada);
      if (pegada.faixa && pegada.agarre === null) {
        pegada.agarre = sim.L - em;
        return;
      }
      definir(em + (pegada.agarre || 0));
      reportar();
    }

    function soltar(ev, motivo) {
      if (!pegada || pegada.id !== ev.pointerId) { return; }
      var g = pegada;
      pegada = null;
      raizEl.dataset.held = "false";
      try { raizEl.releasePointerCapture(ev.pointerId); } catch (err) { /* idem */ }
      if (motivo === "escape") {
        definir(g.inicio);
        if (opcoes.aoMudar) { opcoes.aoMudar(Math.round(g.inicio)); }
      }
      acordar();
    }

    function tecla(ev) {
      if (ev.key === "Escape") {
        if (pegada) { soltar({ pointerId: pegada.id }, "escape"); }
        return;
      }
      var L = sim.L;
      var d = ev.shiftKey ? GRANDE : PASSO;
      var proximo = {
        ArrowUp: L + d,
        ArrowRight: L + d,
        ArrowDown: L - d,
        ArrowLeft: L - d,
        PageUp: L + GRANDE,
        PageDown: L - GRANDE,
        Home: 0,
        End: 100
      }[ev.key];
      if (proximo === undefined) { return; }
      ev.preventDefault();
      definir(proximo, true);
      if (opcoes.aoMudar) { opcoes.aoMudar(Math.round(proximo)); }
    }

    raizEl.addEventListener("pointerdown", pressionar);
    raizEl.addEventListener("pointermove", mover);
    raizEl.addEventListener("pointerup", function (ev) { soltar(ev); });
    raizEl.addEventListener("pointercancel", function (ev) { soltar(ev, "cancelar"); });
    raizEl.addEventListener("lostpointercapture", function (ev) { soltar(ev, "cancelar"); });
    raizEl.addEventListener("keydown", tecla);
    if (window.ResizeObserver) {
      new window.ResizeObserver(pintar).observe(raizEl);
    }
    definir(opcoes.valor, true);

    return { definir: definir, pintar: pintar };
  }

  /* ── Montagem ────────────────────────────────────────────────────────── */
  desenhaLista();

  try {
    var salvo = localStorage.getItem("renap-volume");
    if (salvo !== null && salvo !== "" && !isNaN(Number(salvo))) {
      volume = limitar(Number(salvo), 0, 100);
    }
  } catch (err) { /* modo privado */ }

  if (medidorEl) {
    medidorEl.style.setProperty("--sg-liquid", "var(--cp-primary)");
    medidor = medidorLiquido(medidorEl, {
      valor: volume,
      aoMudar: function (n) {
        volume = n;
        if (n > 0 && mudo) { mudo = false; }
        // O próprio medidor já está no nível novo: não reposicionar à força,
        // senão a onda do líquido morre a cada pixel arrastado.
        aplicaVolume(true);
      }
    });
  } else {
    aplicaVolume();
  }

  pintaCoresDoMedidor();
  if (window.MutationObserver) {
    new window.MutationObserver(pintaCoresDoMedidor).observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"]
    });
  }

  if (mudoEl) {
    mudoEl.addEventListener("click", function () {
      mudo = !mudo;
      aplicaVolume();
    });
  }

  aplicaVolume();
  atualiza();

  /* Saiu da página? O áudio não pode continuar no fone de ninguém. */
  window.addEventListener("pagehide", pararTudo);
})();
