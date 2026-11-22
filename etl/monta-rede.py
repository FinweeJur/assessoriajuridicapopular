"""Monta `rede.html` e `mapeamento-ajups.html` a partir dos dados de 2026.

A casca (topo, rodapé, scripts, rádio) vem de `biblioteca.html`; o miolo é
trocado. Não altera as páginas existentes.
"""
import html
import io
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RAIZ, "biblioteca.html")
AJUPS = os.path.join(RAIZ, "dados", "ajups.json")
PARC = os.path.join(RAIZ, "docs", "links-parceiros-2026-11-22.json")
COLUNAS = os.path.join(RAIZ, "dados", "colunistas.json")


def esc(t):
    return html.escape(str(t or ""), quote=True)


def carrega(p, padrao):
    try:
        return json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return padrao


def shell(titulo, descricao, corpo, sem_busca=False):
    t = io.open(BASE, encoding="utf-8").read()
    if sem_busca:
        t = t.replace("<body>", "<body data-sem-busca-global>", 1)
    t = re.sub(r"<title>.*?</title>", "<title>%s · AJP — Assessoria Jurídica Popular</title>" % esc(titulo), t, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*"', '<meta name="description" content="%s"' % esc(descricao), t, count=1)
    t = re.sub(r"<main\b[^>]*>.*?</main>",
               lambda m: '<main id="conteudo">\n%s\n</main>' % corpo, t, count=1, flags=re.S)
    return t


def status_rotulo(s):
    return {
        "ativo": "Ativo",
        "historico": "Histórico",
        "nao_verificado": "Não verificado",
        "site_fora_do_ar": "Site fora do ar",
        "informado_pelo_dono": "Informado pelo dono",
    }.get(s, s or "—")


def links_item(x):
    b = []
    if x.get("site"):
        alvo = x["site"]
        externo = alvo.startswith("http")
        b.append('<a class="botao secundario" href="%s"%s>Site</a>' % (
            esc(alvo), ' target="_blank" rel="noopener"' if externo else ""))
    if x.get("instagram"):
        b.append('<a class="botao secundario" href="%s" target="_blank" rel="noopener">Instagram</a>' % esc(x["instagram"]))
    if x.get("facebook"):
        b.append('<a class="botao secundario" href="%s" target="_blank" rel="noopener">Facebook</a>' % esc(x["facebook"]))
    if x.get("youtube"):
        b.append('<a class="botao secundario" href="%s" target="_blank" rel="noopener">YouTube</a>' % esc(x["youtube"]))
    if x.get("repositorio"):
        b.append('<a class="botao secundario" href="%s" target="_blank" rel="noopener">Publicações</a>' % esc(x["repositorio"]))
    if not b:
        b.append('<span class="colecao__nota">Sem link confirmado em %s.</span>' % esc(x.get("verificado_em")))
    return " ".join(b)


def cartao_ajup(x):
    return """<li class="cartao" data-ajup data-tipo="%s" data-uf="%s" data-nome="%s %s">
  <span class="etiqueta">%s · %s</span>
  <h3>%s</h3>
  <p>%s</p>
  <p class="colecao__fonte"><b>%s</b> · verificado em %s</p>
  <p class="colecao__acoes">%s</p>
</li>""" % (
        esc(x.get("tipo")), esc(x.get("uf")), esc(x.get("nome")), esc(x.get("cidade") or ""),
        esc(x.get("tipo")), esc(x.get("uf") or "BR"),
        esc(x.get("nome")),
        esc(x.get("observacao") or "Organização do mapeamento histórico de 2011."),
        esc(status_rotulo(x.get("status"))), esc(x.get("verificado_em")),
        links_item(x),
    )


def secao_mapeamento(dados):
    grupos = [
        ("Redes", dados.get("redes", [])),
        ("Advocacias populares", dados.get("advocacias", [])),
        ("Assessorias universitárias", dados.get("universitarias", [])),
        ("Movimentos sociais", dados.get("movimentos", [])),
    ]
    blocos = []
    for titulo, itens in grupos:
        if not itens:
            continue
        blocos.append("""<section class="secao" aria-labelledby="map-%s">
  <div class="secao__cabeca"><h2 id="map-%s">%s</h2><p class="secao__nota">%d registros</p></div>
  <ul class="grade-3 lista-ajups">%s</ul>
</section>""" % (re.sub(r"\W+", "-", titulo.lower()), re.sub(r"\W+", "-", titulo.lower()),
                 esc(titulo), len(itens), "".join(cartao_ajup(x) for x in itens)))
    return "\n".join(blocos)


def pagina_rede(dados, parceiros, colunas):
    blogs = [x for x in parceiros if x.get("grupo") == "blog"]
    entidades = [x for x in parceiros if x.get("grupo") == "entidade"]
    movs = dados.get("movimentos", [])

    def lista_links(itens):
        return "<ul class=\"lateral-lista\">%s</ul>" % "".join(
            '<li><a href="%s" target="_blank" rel="noopener">%s</a> <span class="colecao__nota">%s</span></li>' % (
                esc(x.get("url_final") or x.get("url_original") or "#"),
                esc(x.get("nome")),
                esc("link ativo" if x.get("status") == 200 else "verificar"),
            ) for x in itens
        )

    col = "".join(
        '<li><a href="%s">%s</a> <span class="colecao__nota">%s</span></li>' % (
            esc(c["slug"] if (c.get("slug") or "").endswith(".html") else (("autor-%s.html" % c["slug"]) if c.get("slug") else "autores.html")),
            esc(c.get("nome")), esc(c.get("bio", "")[:90]))
        for c in colunas
    )

    corpo = """
<section class="hero hero--texto">
  <div class="hero__interno">
    <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Rede e comunidade</p>
    <h1>Quem faz, quem apoia, onde se formar</h1>
    <p class="lead">A antiga coluna do blog — páginas, blogues parceiros, entidades, mapeamento e colunas — agora vive aqui. Os textos continuam no Acervo; esta porta é para a rede.</p>
  </div>
</section>

<div class="miolo">
<nav class="colecao__atalhos" aria-label="Atalhos da rede">
  <a href="#quem-somos">Quem somos</a><a href="#como-postar">Como postar</a>
  <a href="#blogues">Blogues parceiros</a><a href="#entidades">Entidades</a>
  <a href="#movimentos">Movimentos</a><a href="#mapeamento">Mapeamento de AJUPs</a>
  <a href="#colunas">Colunas</a><a href="#bibliotecas">Bibliotecas</a>
</nav>

<section class="secao" id="quem-somos" aria-labelledby="quem-titulo">
  <div class="secao__cabeca"><h2 id="quem-titulo">Quem somos</h2></div>
  <div class="cartao">
    <p>O blog <b>Assessoria Jurídica Popular</b> é um coletivo de comunicação que publica pesquisas, resenhas, notícias e poemas sobre assessoria jurídica popular, educação popular em direitos humanos e organização com movimentos sociais.</p>
    <p>Comece por <a href="o-que-e-assessoria-juridica-popular.html">O que é assessoria jurídica popular?</a> e por <a href="como-formar-uma-ajup.html">Como formar uma assessoria jurídica popular universitária?</a>.</p>
  </div>
</section>

<section class="secao" id="como-postar" aria-labelledby="postar-titulo">
  <div class="secao__cabeca"><h2 id="postar-titulo">Como postar</h2></div>
  <div class="cartao">
    <p>Contribuições têm cerca de 2.000 caracteres, autodescrição, cidade de origem, imagem e pelo menos três palavras-chave, entre elas o nome completo de quem assina.</p>
    <p>Envie para <a href="mailto:assessoriajuridicapopular@gmail.com">assessoriajuridicapopular@gmail.com</a>. A publicação é de curadoria e citação; o texto continua assinado por quem escreveu.</p>
  </div>
</section>

<section class="secao" id="blogues" aria-labelledby="blogues-titulo">
  <div class="secao__cabeca"><h2 id="blogues-titulo">Blogues parceiros</h2><p class="secao__nota">21 links do blog original; 19 responderam em 22/11/2026.</p></div>
  %s
</section>

<section class="secao" id="entidades" aria-labelledby="entidades-titulo">
  <div class="secao__cabeca"><h2 id="entidades-titulo">Entidades parceiras</h2><p class="secao__nota">12 entidades; sites ativos quando confirmados.</p></div>
  %s
</section>

<section class="secao" id="movimentos" aria-labelledby="mov-titulo">
  <div class="secao__cabeca"><h2 id="mov-titulo">Movimentos sociais</h2><p class="secao__nota">Os três citados no mapeamento de 2011; confira o site atual antes de publicar.</p></div>
  <ul class="grade-3">%s</ul>
</section>

<section class="secao" id="mapeamento" aria-labelledby="map-titulo">
  <div class="secao__cabeca"><h2 id="map-titulo">Mapeamento de AJUPs</h2><p class="secao__nota">38 organizações históricas + 2 redes atuais, com status e data.</p></div>
  <p>O levantamento de 2011 está preservado; a página nova permite filtrar por tipo, UF e rede e mostra o que foi confirmado em 2026.</p>
  <p><a class="botao" href="mapeamento-ajups.html">Abrir o mapeamento</a></p>
</section>

<section class="secao" id="colunas" aria-labelledby="colunas-titulo">
  <div class="secao__cabeca"><h2 id="colunas-titulo">Colunas</h2></div>
  <ul class="lateral-lista">%s</ul>
</section>

<section class="secao" id="bibliotecas" aria-labelledby="biblio-titulo">
  <div class="secao__cabeca"><h2 id="biblio-titulo">Bibliotecas e cadernos</h2></div>
  <p><a href="biblioteca.html">Biblioteca</a> · <a href="biblioteca.html#renap">Cadernos da RENAP</a> · <a href="biblioteca.html#ipdms">Publicações do IPDMS</a> · <a href="poemas.html">Poemas</a></p>
</section>
</div>
""" % (lista_links(blogs), lista_links(entidades),
       "".join('<li class="cartao"><h3>%s</h3><p>%s</p><p>%s</p></li>' % (
           esc(m.get("nome")), esc(m.get("observacao")), links_item(m)) for m in movs),
       col)
    return shell("Rede e comunidade", "Quem faz, quem apoia, onde se formar e como publicar no acervo AJP.", corpo, sem_busca=True)


def pagina_mapeamento(dados):
    todos = dados.get("redes", []) + dados.get("advocacias", []) + dados.get("universitarias", []) + dados.get("movimentos", [])
    ufs = sorted({x.get("uf") for x in todos if x.get("uf")})
    corpo = """
<section class="hero hero--texto">
  <div class="hero__interno">
    <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Rede</p>
    <h1>Mapeamento de AJUPs</h1>
    <p class="lead">Do levantamento de 2011 à verificação de 2026. Filtre por tipo e UF; confira sempre a data e a fonte. Instagram e Facebook não são raspados.</p>
  </div>
</section>

<div class="miolo">
<section class="fita-secao" aria-label="Filtrar o mapeamento">
  <div class="fita">
    <label class="sr-only" for="filtro-ajup">Buscar organização</label>
    <input id="filtro-ajup" type="search" placeholder="Buscar por nome, sigla ou cidade" />
    <label class="sr-only" for="filtro-tipo">Tipo</label>
    <select id="filtro-tipo"><option value="">Todos os tipos</option><option value="rede">Redes</option><option value="advocacia">Advocacias populares</option><option value="universitaria">Assessorias universitárias</option><option value="movimento">Movimentos</option></select>
    <label class="sr-only" for="filtro-uf">UF</label>
    <select id="filtro-uf"><option value="">Todas as UFs</option>%s</select>
    <span class="fita__conta" id="conta-ajup" role="status" aria-live="polite">%d registros</span>
  </div>
</section>

%s
<p id="vazio-ajup" class="colecao__nota" hidden>Nenhuma organização com esses filtros. Limpe a busca ou troque o tipo/UF.</p>
</div>

<script>
(function () {
  var busca = document.getElementById('filtro-ajup');
  var tipo = document.getElementById('filtro-tipo');
  var uf = document.getElementById('filtro-uf');
  var conta = document.getElementById('conta-ajup');
  var vazio = document.getElementById('vazio-ajup');
  var itens = [].slice.call(document.querySelectorAll('[data-ajup]'));
  var grupos = [].slice.call(document.querySelectorAll('.secao')).filter(function (g) {
    return g.querySelector('[data-ajup]');
  });
  function semAcento(t) {
    return (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  }
  function filtra() {
    var q = semAcento(busca.value).trim();
    var t = tipo.value, u = uf.value, n = 0;
    itens.forEach(function (el) {
      var ok = (!q || semAcento(el.dataset.nome).indexOf(q) > -1) &&
               (!t || el.dataset.tipo === t) && (!u || el.dataset.uf === u);
      el.hidden = !ok; if (ok) n++;
    });
    grupos.forEach(function (g) {
      var vis = g.querySelectorAll('[data-ajup]:not([hidden])').length;
      var nota = g.querySelector('.secao__nota');
      if (nota) { nota.textContent = vis + (vis === 1 ? ' registro' : ' registros'); }
      g.hidden = vis === 0;
    });
    vazio.hidden = n !== 0;
    conta.textContent = n + (n === 1 ? ' registro' : ' registros');
  }
  [busca, tipo, uf].forEach(function (el) { el.addEventListener('input', filtra); });
})();
</script>
""" % ("".join('<option value="%s">%s</option>' % (esc(u), esc(u)) for u in ufs),
       len(todos), secao_mapeamento(dados))
    return shell("Mapeamento de AJUPs", "Mapa histórico e verificação de 2026 das assessorias jurídicas populares, AJUPs e movimentos.", corpo, sem_busca=True)


def main():
    dados = carrega(AJUPS, {})
    parceiros = carrega(PARC, [])
    colunas = carrega(COLUNAS, [])
    for nome, texto in [
        ("rede.html", pagina_rede(dados, parceiros, colunas)),
        ("mapeamento-ajups.html", pagina_mapeamento(dados)),
    ]:
        texto = texto.replace('<a href="biblioteca.html" aria-current="page">Biblioteca</a>',
                              '<a href="biblioteca.html">Biblioteca</a>')
        texto = texto.replace('<a href="rede.html">Rede</a>',
                              '<a href="rede.html" aria-current="page">Rede</a>')
        io.open(os.path.join(RAIZ, nome), "w", encoding="utf-8", newline="\n").write(texto)
        print(nome, len(texto))
    print("ajups:", len(dados.get("redes", [])) + len(dados.get("advocacias", [])) +
          len(dados.get("universitarias", [])) + len(dados.get("movimentos", [])))


if __name__ == "__main__":
    main()
