"""Menu hambúrguer em tela estreita e fusão do comparado com o direito crítico."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# ── 1. Hambúrguer injetado e ligado ───────────────────────────────────────
JS = os.path.join(RAIZ, "casca.js")
with io.open(JS, encoding="utf-8") as f:
    js = f.read()

BLOCO = """
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
    interno.appendChild(botao);

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
"""

if "menuEstreito" not in js:
    js = js.replace("})();", BLOCO + "})();", 1)
    with io.open(JS, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)

# ── 2. Fusão: comparado + direito crítico ─────────────────────────────────
PAG = os.path.join(RAIZ, "assessoria-juridica-popular-no-mundo.html")
with io.open(PAG, encoding="utf-8") as f:
    t = f.read()

SECAO = """
    <section class="secao" id="direito-critico"><div class="secao__cabeca">
      <h2>4. Direito crítico comparado</h2>
      <p class="secao__nota">O mesmo assunto em três casas: aqui, no Controle Popular e na estante de teoria crítica</p></div>
      <p>Comparar não é copiar: cada acervo guarda o seu. Esta tabela mostra onde procurar
      cada coisa, com link direto.</p>
      <div class="tabela cartao"><table>
        <caption>Quem guarda o quê</caption>
        <thead><tr><th scope="col">Assunto</th><th scope="col">Aqui</th><th scope="col">Controle Popular</th><th scope="col">Direito crítico</th></tr></thead>
        <tbody>
          <tr><td>O que é assessoria jurídica popular</td>
              <td><a href="assessoria-juridica-popular.html">textos da seção</a></td>
              <td><a href="https://www.controlepopular.com.br/jurisprudencia/" target="_blank" rel="noopener">decisões e acórdãos</a></td>
              <td><a href="https://github.com/FinweeJur" target="_blank" rel="noopener">teoria crítica</a></td></tr>
          <tr><td>Criminologia crítica</td>
              <td><a href="teoria-critica.html">seção de teoria</a></td>
              <td><a href="https://www.controlepopular.com.br/jurisprudencia/" target="_blank" rel="noopener">casos de criminalização</a></td>
              <td><a href="https://github.com/FinweeJur" target="_blank" rel="noopener">estudos de criminologia</a></td></tr>
          <tr><td>Direitos humanos e movimentos</td>
              <td><a href="direitos-humanos.html">seção de direitos</a></td>
              <td><a href="https://www.controlepopular.com.br/direitos-em-movimento/" target="_blank" rel="noopener">recorte por tema</a></td>
              <td><a href="https://github.com/FinweeJur" target="_blank" rel="noopener">direito comparado latino-americano</a></td></tr>
          <tr><td>Educação popular e formação</td>
              <td><a href="educacao-popular.html">seção de educação</a></td>
              <td><a href="https://www.controlepopular.com.br/biblioteca/" target="_blank" rel="noopener">biblioteca e peças</a></td>
              <td><a href="https://github.com/FinweeJur" target="_blank" rel="noopener">pesquisa e extensão</a></td></tr>
        </tbody></table></div>
      <p class="secao__nota">Definições de trabalho: <b>assessoria jurídica popular</b> é o trabalho de advogados,
      estudantes e educadores com movimentos sociais; <b>direito crítico</b> é a leitura do direito como campo
      de disputa, não só norma posta; <b>direito insurgente</b> é a práxis que parte das lutas.</p>
    </section>
"""

if 'id="direito-critico"' not in t:
    marcador = '    <section class="secao"><div class="secao__cabeca"><h2>O que isso muda para o acervo</h2></div>'
    t = t.replace(marcador, SECAO + marcador, 1)
    with io.open(PAG, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
print("comparado fundido:", "direito-critico" in t)

# página antiga passa a redirecionar
ANTIGA = os.path.join(RAIZ, "direito-critico-comparado.html")
with io.open(ANTIGA, "w", encoding="utf-8", newline="\n") as f:
    f.write("""<!DOCTYPE html>
<html lang="pt-BR"><head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script><meta charset="utf-8" />
<meta http-equiv="refresh" content="0; url=assessoria-juridica-popular-no-mundo.html#direito-critico" />
<title>Direito crítico comparado · AJP</title>
<link rel="canonical" href="assessoria-juridica-popular-no-mundo.html" />
</head><body><p>O conteúdo está em
<a href="assessoria-juridica-popular-no-mundo.html#direito-critico">Direito crítico comparado</a>.</p><script src="fundo-grade.js?v=3" defer></script>
</body></html>
""")
print("redirecionamento: ok")
