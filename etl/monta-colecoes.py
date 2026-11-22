"""Gera as páginas das coleções: memória, formação, biblioteca e cultura."""
import html
import importlib.util
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)


def esc(t):
    return html.escape(t or "", quote=False)


def le(nome):
    return json.load(io.open(os.path.join(DADOS, nome), encoding="utf-8"))


indice = {r["slug"]: r for r in json.load(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8"))}


def pagina(slug, titulo, ativo, lead, corpo):
    if ativo == "memoria":
        trilha = ('<a href="index.html">Início</a> <span aria-hidden="true">/</span> '
                  '<span aria-current="page">Memória</span>')
    else:
        trilha = ('<a href="index.html">Início</a> <span aria-hidden="true">/</span> '
                  '<a href="indice.html">Coleções</a> <span aria-hidden="true">/</span> '
                  '<span aria-current="page">%s</span>' % esc(titulo))
    migalha = '<nav class="migalha" aria-label="Você está em">%s</nav>' % trilha
    return """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>%s · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="%s" />
  <link rel="icon" href="data:," />
  <link rel="stylesheet" href="fontes/fontshare.css?v=3" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=107" />
  <link rel="stylesheet" href="reveal.css?v=107" />
  <link rel="stylesheet" href="componentes/radio.css" />
  <link rel="stylesheet" href="leitura.css?v=1" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s
<main id="conteudo">
  %s
  <section class="hero hero--texto colecao-hero">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Coleção</p>
      <h1>%s</h1>
      <p class="lead">%s</p>
    </div>
  </section>
  <div class="miolo">
%s
  </div>
</main>
%s
<script src="casca.js?v=37" defer></script>
<script src="leitura.js?v=3" defer></script>
<script src="reveal.js?v=75" defer></script>
<script src="fundo-grade.js?v=6" defer></script>
</body>
</html>
""" % (esc(titulo), esc(lead), ms.topo(ativo), migalha, esc(titulo), esc(lead), corpo, ms.rodape())


def cartao_post(slug, nota=""):
    r = indice.get(slug)
    if not r:
        return ""
    return """<a class="cartao destaque colecao__post" href="%s.html">
      <span class="etiqueta">%s · %s</span>
      <h3>%s</h3>
      <p>%s</p>
      <span class="item__ficha">%s%s</span>
    </a>""" % (esc(slug), esc(r.get("tema") or "Acervo"), esc(r.get("ano")),
               esc(r.get("titulo")), esc(r.get("resumo") or ""),
               esc(r.get("autor") or "Acervo AJP"), esc(nota))


def cartao_link(url, titulo, desc, tag="Acervo", fonte=""):
    externo = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
    if fonte:
        return """<div class="cartao destaque colecao__post">
      <span class="etiqueta">%s</span>
      <h3><a href="%s"%s>%s</a></h3>
      <p>%s</p>
      <p class="colecao__fonte"><a href="%s" target="_blank" rel="noopener">No blog original ↗</a></p>
    </div>""" % (esc(tag), esc(url), externo, esc(titulo), esc(desc), esc(fonte))
    return """<a class="cartao destaque colecao__post" href="%s"%s>
      <span class="etiqueta">%s</span>
      <h3>%s</h3>
      <p>%s</p>
    </a>""" % (esc(url), externo, esc(tag), esc(titulo), esc(desc))


def memoria():
    eventos = le("historia.json")
    anos = le("memoria.json")["anos"]
    blocos_eventos = []
    for e in eventos:
        blocos_eventos.append("""<li class="memoria__evento">
          <span class="memoria__ano">%s</span>
          <div><h3>%s</h3><p>%s</p>
          <a href="%s">%s</a></div>
        </li>""" % (esc(e["ano"]), esc(e["titulo"]), esc(e["descricao"]),
                   esc(e["fonte"]), esc(e["fonte_label"])))
    blocos_anos = []
    for a in anos:
        posts = "".join('<li><a href="%s.html">%s</a> <span>%s</span></li>' % (
            esc(p["slug"]), esc(p["titulo"]), esc((p.get("data") or "")[:10]))
            for p in a["posts"])
        blocos_anos.append("""<article class="memoria__ano-card">
          <div class="memoria__ano-topo"><h3>%s</h3><span>%d textos</span></div>
          <ul>%s</ul>
          <a class="colecao__mais" href="acervo.html?ano=%s">Ver todos de %s →</a>
        </article>""" % (esc(a["ano"]), a["total"], posts, esc(a["ano"]), esc(a["ano"])))
    corpo = """
    <nav class="colecao__atalhos" aria-label="Camadas da memória">
      <a href="#acontecimentos">Acontecimentos</a>
      <a href="#linha-do-tempo">Publicações por ano</a>
      <a href="#efemerides">Efemérides</a>
    </nav>

    <section class="secao" id="acontecimentos" aria-labelledby="acontecimentos-titulo">
      <div class="secao__cabeca"><h2 id="acontecimentos-titulo">Acontecimentos</h2>
      <p class="secao__nota">Marcos da AJP e da RENAP, com fonte</p></div>
      <p class="colecao__nota">Esta é uma curadoria inicial. A data exata nem sempre existe;
      quando há divergência, registramos a fonte e a diferença. Não confundir efeméride com atividade da rede.</p>
      <ol class="memoria__eventos">%s</ol>
    </section>

    <section class="secao" id="linha-do-tempo" aria-labelledby="linha-titulo">
      <div class="secao__cabeca"><h2 id="linha-titulo">Publicações por ano</h2>
      <p class="secao__nota">Quando o blog publicou — não quando o fato aconteceu</p></div>
      <p class="colecao__nota">A linha abaixo é do acervo: 713 textos, de 2009 a 2024.
      Os anos com poucos posts não significam ausência de atividade da AJP.</p>
      <div class="memoria__anos">%s</div>
    </section>

    <section class="secao" id="efemerides" aria-labelledby="efemerides-titulo">
      <div class="secao__cabeca"><h2 id="efemerides-titulo">Efemérides</h2>
      <p class="secao__nota">A mística do dia é memória social, não registro institucional</p></div>
      <p>O <code>calendario.json</code> reúne 494 datas de lutas sociais, de 1381 a 2019.
      Elas ajudam a situar o repertório político, mas não são atividades da AJP.</p>
      <p><a class="botao secundario" href="index.html">Ver a mística do dia na home →</a></p>
    </section>
    """ % ("\n".join(blocos_eventos), "\n".join(blocos_anos))
    return pagina("memoria", "Memória", "memoria",
                  "Acontecimentos da AJP e da RENAP, publicações do acervo e efemérides — em uma só página, com as três camadas separadas.",
                  corpo)


def formacao():
    trilhas = le("trilhas.json")
    blocos = []
    for t in trilhas:
        cards = "".join(cartao_post(s) for s in t["posts"])
        blocos.append("""<section class="secao trilha" id="%s" aria-labelledby="%s-titulo">
          <div class="secao__cabeca"><h2 id="%s-titulo">%s</h2>
          <p class="secao__nota">%s · %d leituras</p></div>
          <p>%s</p>
          <div class="grade-3">%s</div>
        </section>""" % (esc(t["id"]), esc(t["id"]), esc(t["id"]), esc(t["titulo"]),
                         esc(t["nivel"]), len(t["posts"]), esc(t["descricao"]), cards))
    corpo = """
    <nav class="colecao__atalhos" aria-label="Trilhas">
      <a href="#o-que-e-ajp">O que é AJP</a>
      <a href="#direito-achado-insurgente">Direito e crítica</a>
      <a href="#educacao-popular">Educação popular</a>
      <a href="#terra-moradia">Terra e moradia</a>
      <a href="#teoria-critica">Teoria crítica</a>
      <a href="#memoria-ditadura">Memória e ditadura</a>
    </nav>
    <p class="colecao__nota">Trilhas curatoriais, não uma lista cronológica. Cada percurso
    reúne textos formativos e atemporais; eventos, chamadas e notícias ficam de fora.</p>
    %s
    """ % ("\n".join(blocos))
    return pagina("formacao", "Formação", "formacao",
                  "Seis trilhas para começar, aprofundar e voltar: do que é assessoria jurídica popular à crítica do direito.",
                  corpo)


def biblioteca():
    itens = le("biblioteca.json")
    grupos = {}
    for i in itens:
        grupos.setdefault(i["tipo"], []).append(i)
    blocos = []
    ids = {"Acervo": "acervo", "Obra": "obra", "Dossiê": "dossie"}
    for tipo in ("Acervo", "Obra", "Dossiê"):
        cards = "".join(cartao_link(i["url"], i["titulo"], i["descricao"], tipo, i.get("fonte", "")) for i in grupos.get(tipo, []))
        ident = ids[tipo]
        blocos.append("""<section class="secao" id="%s" aria-labelledby="%s-titulo">
          <div class="secao__cabeca"><h2 id="%s-titulo">%s</h2>
          <p class="secao__nota">%d registros</p></div>
          <div class="grade-3">%s</div>
        </section>""" % (ident, ident, ident, esc(tipo), len(grupos.get(tipo, [])), cards))
    corpo = """
    <nav class="colecao__atalhos" aria-label="Biblioteca">
      <a href="#acervo">Acervos</a><a href="#obra">Obras</a><a href="#dossie">Dossiê</a>
      <a href="acervo.html?tipo=resenha">Resenhas no acervo</a>
    </nav>
    <p class="colecao__nota">Esta página separa <b>obras</b> de <b>posts sobre obras</b>.
    Há 111 resenhas no acervo, mas nem toda resenha é uma obra acadêmica. Os PDFs e
    textos completos permanecem nos sites de origem, quando disponíveis.</p>
    <p class="colecao__nota">As bibliotecas abaixo vêm da página
    <a href="https://assessoriajuridicapopular.blogspot.com/p/bibliotecas.html" target="_blank" rel="noopener">Bibliotecas</a>
    do blog original. Cada cartão leva ao acervo no site e, quando existe, à página de origem.</p>
    %s
    <section class="secao" aria-labelledby="busca-titulo">
      <div class="secao__cabeca"><h2 id="busca-titulo">Como procurar</h2></div>
      <p>Use a busca do acervo para localizar autores, instituições e temas; para obras
      externas, comece pelas bibliotecas acima. Se você tem uma monografia, dissertação
      ou tese para incluir, escreva para o contato do rodapé.</p>
      <p><a class="botao" href="acervo.html?tipo=resenha">Ver as resenhas do acervo →</a></p>
    </section>
    """ % ("\n".join(blocos))
    return pagina("biblioteca", "Biblioteca", "biblioteca",
                  "Artigos, monografias, dissertações, teses e dossiês sobre AJP, AJUPs, Direito Achado na Rua, Direito Insurgente e uso tático do direito.",
                  corpo)


def cultura():
    grupos = le("cultura.json")
    blocos = []
    for g in grupos:
        cards = "".join(cartao_link(u, t, "", g["titulo"]) for u, t in g["links"])
        blocos.append("""<section class="secao" id="%s" aria-labelledby="%s-titulo">
          <div class="secao__cabeca"><h2 id="%s-titulo">%s</h2>
          <p class="secao__nota">%s</p></div>
          <div class="grade-3">%s</div>
        </section>""" % (esc(g["id"]), esc(g["id"]), esc(g["id"]), esc(g["titulo"]),
                         esc(g["descricao"]), cards))
    corpo = """
    <nav class="colecao__atalhos" aria-label="Cultura">
      <a href="#poesia">Poesia</a><a href="#documentario">Documentários e vídeos</a>
      <a href="#cinema-teatro-musica">Cinema, teatro e música</a><a href="#cronicas">Crônicas</a>
    </nav>
    <p class="colecao__nota">Cultura é o guarda-chuva; poema, crônica, documentário,
    vídeo e cinema são formatos. O Caderno de Poesias e a poesia do blog agora vivem
    em uma única página.</p>
    %s
    """ % ("\n".join(blocos))
    return pagina("cultura", "Cultura", "cultura",
                  "Poesia, crônica, documentário, vídeo, cinema, teatro e música: o acervo cultural da AJP.",
                  corpo)


def main():
    for nome, texto in [("memoria.html", memoria()), ("formacao.html", formacao()),
                        ("biblioteca.html", biblioteca()), ("cultura.html", cultura())]:
        with io.open(os.path.join(RAIZ, nome), "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        print(nome, len(texto))


if __name__ == "__main__":
    main()
