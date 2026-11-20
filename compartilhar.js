/* Compartilhar e citar — sem dependência.
   WhatsApp e Telegram usam link oficial; Instagram usa a folha do sistema
   quando existe e, quando não existe, copia o link e abre o app. */
(function () {
  'use strict';

  var caixa = document.querySelector('[data-compartilhar]');
  if (!caixa) { return; }

  var url = caixa.dataset.url || location.href;
  var titulo = caixa.dataset.titulo || document.title;
  var autor = caixa.dataset.autor || '';
  var data = caixa.dataset.data || '';
  var fonte = caixa.dataset.fonte || 'Acervo AJP';
  var fonteUrl = caixa.dataset.fonteUrl || url;
  var status = caixa.querySelector('[data-status]');
  var corpo = document.querySelector('.corpo');

  function avisa(texto) {
    if (!status) { return; }
    status.textContent = texto;
    status.dataset.visivel = 'true';
    clearTimeout(avisa.timer);
    avisa.timer = setTimeout(function () {
      status.dataset.visivel = 'false';
    }, 3200);
  }

  function copia(texto, mensagem) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(function () { avisa(mensagem); },
        function () { avisa('Não deu para copiar. Selecione o texto.'); });
      return;
    }
    var campo = document.createElement('textarea');
    campo.value = texto;
    campo.setAttribute('readonly', '');
    campo.style.position = 'fixed';
    campo.style.opacity = '0';
    document.body.appendChild(campo);
    campo.select();
    try { document.execCommand('copy'); avisa(mensagem); }
    catch (e) { avisa('Não deu para copiar.'); }
    document.body.removeChild(campo);
  }

  function mesAbreviado(iso) {
    var meses = ['jan.', 'fev.', 'mar.', 'abr.', 'maio', 'jun.', 'jul.',
                 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
    if (!iso || iso.length < 10) { return ''; }
    var a = iso.slice(0, 4), m = parseInt(iso.slice(5, 7), 10), d = parseInt(iso.slice(8, 10), 10);
    return d + ' ' + meses[m - 1] + ' ' + a;
  }

  function hoje() {
    var agora = new Date();
    return mesAbreviado(agora.toISOString().slice(0, 10));
  }

  function citacaoAbnt() {
    var sobrenome = autor.split(' ').slice(-1)[0].toUpperCase();
    var resto = autor.split(' ').slice(0, -1).join(' ');
    var nome = resto ? sobrenome + ', ' + resto : sobrenome;
    return nome + '. ' + titulo + '. ' + fonte + ', ' +
      (data ? mesAbreviado(data) : 's.d.') + '. Disponível em: <' + url +
      '>. Acesso em: ' + hoje() + '.';
  }

  caixa.addEventListener('click', function (ev) {
    var botao = ev.target.closest('[data-acao]');
    if (!botao) { return; }
    var acao = botao.dataset.acao;
    var texto = encodeURIComponent(titulo + ' — ' + url);

    if (acao === 'whatsapp') {
      window.open('https://wa.me/?text=' + texto, '_blank', 'noopener');
    } else if (acao === 'telegram') {
      window.open('https://t.me/share/url?url=' + encodeURIComponent(url) +
        '&text=' + encodeURIComponent(titulo), '_blank', 'noopener');
    } else if (acao === 'instagram') {
      if (navigator.share) {
        navigator.share({ title: titulo, url: url }).catch(function () {});
      } else {
        copia(url, 'Link copiado. Cole no Instagram.');
        window.open('https://www.instagram.com/', '_blank', 'noopener');
      }
    } else if (acao === 'copiar-texto') {
      copia(corpo ? corpo.innerText.trim() : titulo + '\n' + url, 'Texto copiado.');
    } else if (acao === 'copiar-citacao') {
      copia(citacaoAbnt(), 'Citação ABNT copiada.');
    }
  });
})();
