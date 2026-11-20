"""Gera as seis páginas-chave e o blog a partir do índice do acervo.

Entrada: _indice.json (713 registros: slug, titulo, data, autor, resumo, temas)
Saída:   <slug>.html para cada seção + blog.html

Cada página tem: topo igual ao da capa, hero com foto, lista filtrada pelo
tema, navegação entre as seções e rodapé com as parcerias.
"""
import html
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

SECOES = [
    ("assessoria-juridica-popular", "O que é assessoria jurídica popular",
     "assessoria-juridica-popular",
     "A definição, a história e a prática: o texto de 2009 que abre o acervo e os que vieram depois.",
     "img/foto-02.jpg"),
    ("direitos-humanos", "Direitos humanos", "direitos-humanos",
     "O que a assessoria jurídica popular faz quando o direito não chega: casos, denúncias e vitórias.",
     "img/foto-06.jpg"),
    ("movimentos-sociais", "Movimentos sociais", "movimentos-sociais",
     "Terra, moradia, água e trabalho: os movimentos que chamam a assessoria para perto.",
     "img/foto-09.jpg"),
    ("memoria-e-cultura", "Memória e cultura", "memoria",
     "Encontros, cartas políticas, poesia e o que a rede guarda desde 2009.",
     "img/foto-03.jpg"),
    ("teoria-critica", "Teoria crítica do direito", "teoria-critica",
     "Resenhas, livros e aulas: a estante de quem pensa o direito a partir da luta.",
     "img/foto-13.jpg"),
    ("educacao-popular", "Educação popular", "educacao-popular",
     "Formação, oficinas e metodologia: como se aprende e se ensina assessoria jurídica popular.",
     "img/foto-05.jpg"),
]


def esc(t):
    return html.escape(t or "", quote=False)


def data_curta(iso):
    if not iso or len(iso) < 10:
        return ""
    ano, mes, dia = iso[:10].split("-")
    return "%d de %s de %s" % (int(dia), MESES[int(mes) - 1], ano)


def topo(ativo):
    secoes = "\n".join(
        '          <li><a href="%s.html"%s>%s</a></li>' % (
            slug, ' aria-current="page"' if slug == ativo else "", esc(titulo))
        for slug, titulo, _, _, _ in SECOES)
    return """<header class="topo">
  <div class="topo__interno">
    <a class="topo__marca" href="index.html">
      <span class="ponto" aria-hidden="true"></span>
      AJP <span>· Assessoria Jurídica Popular</span>
    </a>
    <nav class="topo__links" aria-label="Seções">
      <a href="index.html"%s>Acervo</a>
      <div class="menu">
        <button class="menu__botao" type="button" aria-expanded="false" aria-controls="menu-secoes">
          Seções <span aria-hidden="true">▾</span>
        </button>
        <ul class="menu__lista" id="menu-secoes">
%s
        </ul>
      </div>
      <a href="autores.html">Autores</a>
      <a href="blog.html"%s>Blog</a>
    </nav>
    <div class="topo__tema">
      <label for="tema">Tema</label>
      <select id="tema" name="tema">
        <option value="light">🌞 Claro</option>
        <option value="dark">🌙 Escuro</option>
        <option value="brasil">🟢 Brasil</option>
        <option value="high-contrast">◐ Alto contraste</option>
        <option value="pequi">🟠 Pequi</option>
        <option value="cerrado">🌾 Cerrado</option>
        <option value="mata-atlantica">🌿 Mata Atlântica</option>
        <option value="caatinga">🌵 Caatinga</option>
        <option value="pantanal">🐊 Pantanal</option>
      </select>
    </div>
  </div>
</header>""" % (' aria-current="page"' if ativo == "acervo" else "", secoes,
                ' aria-current="page"' if ativo == "blog" else "")


def rodape():
    return """<footer class="rodape">
  <div class="rodape__topo">
    <p class="rodape__marca"><span class="ponto" aria-hidden="true"></span> AJP · Assessoria Jurídica Popular</p>
    <p class="rodape__lema">Textos em citação direta, com autor, data e fonte.</p>
  </div>
  <div class="rodape__interno">
    <div>
      <h2>Acervo</h2>
      <ul>
        <li><a href="index.html">Todos os textos</a></li>
        <li><a href="blog.html">Blog, em ordem</a></li>
        <li><a href="o-que-e-assessoria-juridica-popular.html">O que é AJP</a></li>
      </ul>
    </div>
    <div>
      <h2>Seções</h2>
      <ul>
        <li><a href="direitos-humanos.html">Direitos humanos</a></li>
        <li><a href="movimentos-sociais.html">Movimentos sociais</a></li>
        <li><a href="memoria-e-cultura.html">Memória e cultura</a></li>
        <li><a href="teoria-critica.html">Teoria crítica</a></li>
        <li><a href="educacao-popular.html">Educação popular</a></li>
      </ul>
    </div>
    <div>
      <h2>Fonte</h2>
      <p>Textos publicados originalmente no blog
      <a href="https://assessoriajuridicapopular.blogspot.com/" target="_blank" rel="noopener">Assessoria Jurídica Popular</a>,
      em citação direta, com autor, data e link.</p>
    </div>
    <div>
      <h2>Parceria</h2>
      <p>Publicação e curadoria com o
      <a href="https://ipdms.org.br/" target="_blank" rel="noopener">IPDMS</a>
      — GT de Assessoria Jurídica Popular.</p>
    </div>
  </div>
  <div class="parcerias" aria-label="Realização e parceria">
    <p class="parcerias__titulo">Realização e parceria</p>
    <ul class="parcerias__lista">
      <li><a href="https://www.renap.org.br/" target="_blank" rel="noopener"><img src="logos/renap.png" alt="RENAP" loading="lazy" /></a></li>
      <li><a href="https://ipdms.org.br/" target="_blank" rel="noopener"><img src="logos/ipdms.png" alt="IPDMS" loading="lazy" /></a></li>
      <li><a href="https://mab.org.br/" target="_blank" rel="noopener"><img src="logos/mab.png" alt="MAB" loading="lazy" /></a></li>
    </ul>
  </div>
</footer>"""


def cartao(registro):
    return """      <li class="item" data-temas="%s" data-data="%s" data-titulo="%s" data-tipo="%s" data-ano="%s">
        <a class="item__link" href="%s.html">
          <span class="etiqueta">%s · %s</span>
          <h3>%s</h3>
          <p>%s</p>
          <span class="item__ficha">%s · %s</span>
        </a>
      </li>""" % (
        esc(" ".join((registro.get("temas") or [""])[0].split("-"))),
        esc(registro.get("data")), esc(registro.get("titulo")),
        esc(registro.get("tipo") or "formativo"), esc(registro.get("ano") or ""),
        esc(registro["slug"]), esc(registro.get("tema")), esc(registro.get("ano")),
        esc(registro.get("titulo")), esc((registro.get("resumo") or "")[:200]),
        esc(registro.get("autor")), esc(data_curta(registro.get("data"))))


def pagina(slug, titulo, ativo, lead, foto, itens, extra=""):
    lista = "\n".join(cartao(r) for r in itens)
    n = len(itens)
    return """<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>%s · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="%s" />
  <link rel="icon" href="data:," />
  <link rel="stylesheet" href="fontes/fontshare.css" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css" />
  <link rel="stylesheet" href="reveal.css" />
  <link rel="stylesheet" href="componentes/radio.css" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s

<main id="conteudo">
  <section class="hero hero--texto">
    <div class="hero__foto" style="background-image:url('%s')" aria-hidden="true"></div>
    <div class="hero__veu" aria-hidden="true"></div>
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Seção do acervo</p>
      <h1>%s</h1>
      <p class="lead">%s</p>
      <p class="busca__contagem">%d %s nesta seção</p>
    </div>
  </section>

  <div class="miolo">
    <section class="secao" aria-labelledby="titulo-lista">
      <div class="secao__cabeca">
        <h2 id="titulo-lista">Textos</h2>
        <p class="secao__nota">Em ordem, do mais recente ao mais antigo</p>
      </div>
      <div class="fita">
        <label class="sr-only" for="f-busca">Filtrar nesta seção</label>
        <input id="f-busca" type="search" placeholder="Filtrar por palavra-chave" data-busca autocomplete="off" />
        <div class="fita__tipos" role="group" aria-label="Tipo de texto">
          <button type="button" class="chip-f" data-tipo-f="todos" aria-pressed="true">Todos</button>
          <button type="button" class="chip-f" data-tipo-f="formativo" aria-pressed="false">Textos</button>
          <button type="button" class="chip-f" data-tipo-f="evento" aria-pressed="false">Eventos</button>
          <button type="button" class="chip-f" data-tipo-f="poesia" aria-pressed="false">Poesia</button>
          <button type="button" class="chip-f" data-tipo-f="resenha" aria-pressed="false">Livros</button>
          <button type="button" class="chip-f" data-tipo-f="documento" aria-pressed="false">Documentos</button>
          <button type="button" class="chip-f" data-tipo-f="notícia" aria-pressed="false">Notícias</button>
        </div>
        <label class="sr-only" for="f-ano">Ano</label>
        <select id="f-ano" data-ano-filtro>
          <option value="">Todos os anos</option>
        </select>
        <label class="sr-only" for="f-ordem">Ordenar</label>
        <select id="f-ordem" data-ordem>
          <option value="recente">Mais recente</option>
          <option value="antigo">Mais antigo</option>
          <option value="titulo">Título</option>
        </select>
        <span class="fita__conta" data-conta role="status" aria-live="polite"></span>
      </div>
      <ul class="lista-acervo" data-revelar-grupo data-paginada>
%s
      </ul>
      <div class="mais"><button type="button" data-mais>Ver mais 24</button></div>
    </section>
%s

    <section class="secao veja" aria-labelledby="veja">
      <div class="secao__cabeca">
        <h2 id="veja">Veja também</h2>
        <p class="secao__nota">Do outro lado, com fonte e metodologia</p>
      </div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">🏛️</span><b>Jurisprudência:</b>
          <a href="https://www.controlepopular.com.br/jurisprudencia/" target="_blank" rel="noopener">decisões e acórdãos no Controle Popular</a>.</li>
        <li><span class="emoji" aria-hidden="true">📚</span><b>Biblioteca:</b>
          <a href="https://www.controlepopular.com.br/biblioteca/" target="_blank" rel="noopener">peças e publicações no Controle Popular</a>.</li>
        <li><span class="emoji" aria-hidden="true">✊</span><b>Direitos em movimento:</b>
          <a href="https://www.controlepopular.com.br/direitos-em-movimento/" target="_blank" rel="noopener">o recorte por tema no Controle Popular</a>.</li>
      </ul>
    </section>
  </div>
</main>

%s

<script>
  (function () {
    var raiz = document.documentElement;
    var seletor = document.getElementById('tema');
    var guardado = localStorage.getItem('renap-tema');
    if (guardado) { raiz.dataset.theme = guardado; seletor.value = guardado; }
    seletor.addEventListener('change', function () {
      raiz.dataset.theme = seletor.value;
      localStorage.setItem('renap-tema', seletor.value);
    });
  })();
</script>
<div class="radio-flut" data-radio data-aberto="false">
  <button data-dica="Abrir ou fechar o rádio" class="radio-flut__botao" type="button" data-radio-toggle aria-expanded="false" aria-controls="radio-painel">
    <span aria-hidden="true">📻</span> Rádio
  </button>
  <div class="radio-flut__painel" id="radio-painel">
    <button class="radio-flut__fechar" type="button" data-radio-fechar aria-label="Fechar o rádio">×</button>
        <div class="rp__controles">
          <div class="rp__linha">
            <button class="rp__tocar" type="button" data-radio-tocar data-tocando="false" aria-label="Tocar rádio">▶</button>
            <button class="rp__parar" type="button" data-radio-parar aria-label="Parar o rádio" title="Parar o rádio">■</button>
            <div>
              <div class="rp__nome" data-radio-nome>Rádio Brasil de Fato<span class="rp__meta" data-radio-meta>toque em ▶ ou escolha outra estação</span></div>
            </div>
          </div>
          <label class="rp__volume">
            <span>Volume</span>
            <input type="range" min="0" max="100" value="70" data-radio-volume aria-label="Volume do rádio" />
          </label>
          <p class="rp__status" data-radio-status aria-live="polite"></p>
        </div>
        <div class="rp__lista-area">
          <div class="rp__busca">
            <input type="search" placeholder="Buscar estação, cidade ou UF" data-radio-busca aria-label="Buscar estação" />
            <span class="rp__contagem" data-radio-contagem></span>
          </div>
          <div class="rp__lista" data-radio-lista></div>
        </div>
        <audio data-radio-audio preload="none"></audio>
  </div>
</div>
<script src="componentes/radio.js" defer></script>
<script src="site.js" defer></script>
<script src="reveal.js" defer></script>
<button class="ao-topo" type="button" data-topo aria-label="Voltar ao topo">↑</button>
</body>
</html>
""" % (esc(titulo), esc(lead), topo(ativo), foto, esc(titulo), esc(lead), n,
       "texto" if n == 1 else "textos", lista, extra, rodape())


def main():
    registros = json.loads(io.open(INDICE, encoding="utf-8").read())
    for slug, titulo, tema, lead, foto in SECOES:
        itens = [r for r in registros if tema in (r.get("temas") or [])]
        itens.sort(key=lambda r: r.get("data") or "", reverse=True)
        outras = "\n".join(
            '        <li><a href="%s.html">%s</a></li>' % (s, esc(t)) for s, t, _, _, _ in SECOES if s != slug)
        extra = """    <section class="secao" aria-labelledby="titulo-outras">
      <div class="secao__cabeca"><h2 id="titulo-outras">Continuar por</h2></div>
      <ul class="lateral-lista">
%s
      </ul>
    </section>""" % outras
        saida = pagina(slug, titulo, slug, lead, foto, itens, extra)
        with io.open(os.path.join(RAIZ, slug + ".html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(saida)
        print("%-46s %4d textos" % (slug, len(itens)))

    # Blog: tudo em ordem, agrupado por ano.
    registros.sort(key=lambda r: r.get("data") or "", reverse=True)
    grupos = {}
    for r in registros:
        grupos.setdefault((r.get("data") or "")[:4], []).append(r)
    blocos = []
    for ano in sorted(grupos, reverse=True):
        itens = "\n".join(cartao(r) for r in grupos[ano])
        blocos.append("""    <section class="secao" aria-labelledby="ano-%s">
      <div class="secao__cabeca"><h2 id="ano-%s">%s</h2>
      <p class="secao__nota">%d %s</p></div>
      <ul class="lista-acervo" data-revelar-grupo>
%s
      </ul>
    </section>""" % (ano, ano, ano, len(grupos[ano]),
                     "texto" if len(grupos[ano]) == 1 else "textos", itens))
    blog = pagina("blog", "Blog: tudo em ordem", "blog",
                  "Os %d textos do acervo, do mais recente ao mais antigo." % len(registros),
                  "img/foto-22.jpg", [], "\n".join(blocos))
    # A página do blog não usa a lista única: troca o bloco vazio.
    blog = blog.replace('<ul class="lista-acervo" data-revelar-grupo>\n\n      </ul>\n\n    \n  </div>',
                        "  </div>")
    with io.open(os.path.join(RAIZ, "blog.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(blog)
    print("blog:", len(registros), "textos em", len(grupos), "anos")


if __name__ == "__main__":
    main()
