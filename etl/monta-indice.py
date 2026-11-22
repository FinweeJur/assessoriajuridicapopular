"""Gera o Índice do site: um mapa wiki de todas as portas de entrada."""
import collections
import html
import importlib.util
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)


def esc(t):
    return html.escape(t or "", quote=False)


def carrega(nome, padrao):
    try:
        return json.load(io.open(os.path.join(RAIZ, "dados", nome), encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return padrao


indice = json.load(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8"))
autores = {r.get("autor") for r in indice if r.get("autor")}
poemas = sum(1 for r in indice if r.get("tipo") == "poesia")
refs = carrega("leapspace-refs.json", [])
abertas = sum(1 for r in refs if r.get("aberto"))
biblioteca = carrega("biblioteca.json", [])
cultura = carrega("cultura.json", [])
trilhas = carrega("trilhas.json", [])
memoria = carrega("memoria.json", [])

SECOES_INFO = [
    ("assessoria-juridica-popular", "assessoria-juridica-popular.html",
     "O que é assessoria jurídica popular", "a prática, a história e os debates do campo"),
    ("direitos-humanos", "direitos-humanos.html",
     "Direitos humanos", "violações, denúncia e proteção"),
    ("movimentos-sociais", "movimentos-sociais.html",
     "Movimentos sociais", "lutas por terra, moradia, trabalho e cidade"),
    ("educacao-popular", "educacao-popular.html",
     "Educação popular", "Freire, formação e metodologia"),
    ("teoria-critica", "teoria-critica.html",
     "Teoria crítica do direito", "crítica do direito e do ensino jurídico"),
]
_contagem = collections.Counter(r.get("tema_principal") for r in indice)
secoes = [(arquivo, titulo, _contagem.get(chave, 0), desc)
          for chave, arquivo, titulo, desc in SECOES_INFO]

colecoes = [
    ("memoria.html", "Memória", "acontecimentos, publicações por ano e efemérides"),
    ("formacao.html", "Formação", "seis trilhas, mais citações, recomendações e glossário"),
    ("biblioteca.html", "Biblioteca", "artigos, teses, cadernos da RENAP e produções do IPDMS"),
    ("cultura.html", "Cultura", "poesia, cinema, teatro, música e documentários — com Poemas e Mística"),
    ("assessoria-juridica-popular-no-mundo.html", "AJP pelo mundo",
     "Brasil, América Latina e panorama da pesquisa (154 referências)"),
]

dentro = [
    ("rede.html", "Rede e comunidade", "quem somos, blogues, entidades, mapeamento e movimentos"),
    ("mapeamento-ajups.html", "Mapeamento de AJUPs", "38 organizações de 2011 + 2 redes atuais"),
    ("poemas.html", "Poemas e Caderno", "%d poemas publicados e o caderno" % poemas),
    ("mistica.html", "Mística", "o que sustenta a luta: arte, memória e celebração"),
    ("citacoes.html", "Citações", "falas do acervo por tema"),
    ("recomendacoes.html", "Recomendações", "livros, filmes e músicas"),
    ("glossario.html", "Glossário", "termos do direito e da organização popular"),
]

comeco = [
    ("index.html", "Apresentação", "a capa do acervo"),
    ("acervo.html", "Acervo completo", "%d textos com busca e filtros" % len(indice)),
    ("indice.html", "Índice", "esta página: todas as portas de entrada"),
]

acervo_sub = [
    ("acervo.html", "Todos os textos", "busca por palavra, tipo, ano e rede"),
    ("blog.html", "Por ano", "os mesmos textos em ordem cronológica, 2003 a 2024"),
    ("autores.html", "Autores", "%d pessoas que assinam textos" % len(autores)),
]

redes = [
    ("acervo.html?rede=renap", "RENAP", "Rede Nacional de Advogadas e Advogados Populares"),
    ("acervo.html?rede=ipdms", "IPDMS", "Instituto de Pesquisa, Direito e Movimentos Sociais"),
    ("acervo.html?rede=renaju-ajup", "RENAJU/AJUPs", "assessorias jurídicas universitárias e populares"),
]


def item(href, titulo, desc, externo=False):
    extra = ' target="_blank" rel="noopener"' if externo else ""
    return ('<li data-busca="%s"><a class="indice-lista__link" href="%s"%s>'
            '<b>%s</b><span>%s</span></a></li>'
            % (esc((titulo + " " + desc).lower()), esc(href), extra, esc(titulo), esc(desc)))


def grupo(titulo, nota, itens):
    return """<section class="secao indice-grupo">
      <div class="secao__cabeca"><h2>%s</h2><p class="secao__nota">%s</p></div>
      <ul class="indice-lista">%s</ul>
    </section>""" % (esc(titulo), esc(nota), "".join(itens))


corpo = """<section class="secao indice-topo">
  <div class="secao__cabeca">
    <h2>Índice do site</h2>
    <p class="secao__nota">Todas as portas de entrada, em uma página</p>
  </div>
  <p>O acervo tem %d textos, seis seções, cinco coleções e uma página de pesquisa.
  Use o campo abaixo para filtrar o índice, ou a busca do topo para procurar dentro dos textos.</p>
  <div class="indice-busca">
    <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input type="search" data-indice-busca placeholder="Filtrar páginas do índice" aria-label="Filtrar páginas do índice" autocomplete="off" />
    <span class="indice-conta" data-indice-conta></span>
  </div>
</section>

%s
%s
%s
%s
%s
%s

<section class="secao indice-grupo">
  <div class="secao__cabeca"><h2>Parceiros e fontes</h2>
  <p class="secao__nota">Saem do site, abrem em outra aba</p></div>
  <ul class="indice-lista">
    <li><a class="indice-lista__link" href="https://www.controlepopular.com.br/" target="_blank" rel="noopener"><b>Controle Popular</b><span>dados públicos, jurisprudência e biblioteca</span></a></li>
    <li><a class="indice-lista__link" href="https://ipdms.org.br/" target="_blank" rel="noopener"><b>IPDMS</b><span>pesquisa, direito e movimentos sociais</span></a></li>
    <li><a class="indice-lista__link" href="https://mab.org.br/" target="_blank" rel="noopener"><b>MAB</b><span>Movimento dos Atingidos por Barragens</span></a></li>
  </ul>
</section>

<script>
(function () {
  var campo = document.querySelector('[data-indice-busca]');
  var conta = document.querySelector('[data-indice-conta]');
  if (!campo) { return; }
  var grupos = [].slice.call(document.querySelectorAll('.indice-grupo'));
  function semAcento(t) {
    return (t || '').normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase();
  }
  function aplica() {
    var termo = semAcento(campo.value.trim());
    var visiveis = 0;
    grupos.forEach(function (g) {
      var algum = false;
      [].slice.call(g.querySelectorAll('li')).forEach(function (li) {
        var bate = !termo || semAcento(li.getAttribute('data-busca') || '').indexOf(termo) >= 0;
        li.hidden = !bate;
        if (bate) { algum = true; visiveis += 1; }
      });
      g.hidden = !algum;
    });
    if (conta) { conta.textContent = termo ? visiveis + ' páginas' : ''; }
  }
  campo.addEventListener('input', aplica);
})();
</script>""" % (
    len(indice),
    grupo("Comece por aqui", "O essencial em três links", [item(*x) for x in comeco]),
    grupo("Dentro do Acervo", "Uma porta, três jeitos de ler", [item(*x) for x in acervo_sub]),
    grupo("Seções", "Os seis recortes temáticos do acervo",
          [item(h, t, "%d textos · %s" % (n, d)) for h, t, n, d in secoes]),
    grupo("Coleções", "Páginas que reúnem materiais por uso", [item(*x) for x in colecoes]),
    grupo("Dentro de Cultura e Formação", "Subpáginas das duas coleções", [item(*x) for x in dentro]),
    grupo("Recortes por rede", "Quem produz e articula o campo", [item(*x) for x in redes]),
)

pagina = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Índice do site · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="Mapa de todas as páginas do acervo: seções, coleções, poemas, autores e o panorama da pesquisa sobre assessoria jurídica popular." />
  <link rel="icon" href="data:," />
  <link rel="stylesheet" href="fontes/fontshare.css?v=3" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=93" />
  <link rel="stylesheet" href="reveal.css?v=93" />
  <link rel="stylesheet" href="componentes/radio.css" />
  <link rel="stylesheet" href="leitura.css?v=1" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s
<main id="conteudo">
  <nav class="migalha" aria-label="Você está em"><a href="index.html">Início</a>
    <span aria-hidden="true">/</span> <span aria-current="page">Índice</span></nav>
  <section class="hero hero--texto colecao-hero">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Mapa do site</p>
      <h1>Índice</h1>
      <p class="lead">Tudo o que existe no acervo, agrupado por uso: começar, estudar, pesquisar, ler e voltar.</p>
    </div>
  </section>
  <div class="miolo">
%s
  </div>
</main>
%s
<script src="casca.js?v=30" defer></script>
<script src="leitura.js?v=3" defer></script>
<script src="reveal.js?v=75" defer></script>
<script src="fundo-grade.js?v=6" defer></script>
</body>
</html>
""" % (ms.topo("indice"), corpo, ms.rodape())

io.open(os.path.join(RAIZ, "indice.html"), "w", encoding="utf-8", newline="\n").write(pagina)
print("indice: %d autores, %d poemas, %d refs" % (len(autores), poemas, len(refs)))
