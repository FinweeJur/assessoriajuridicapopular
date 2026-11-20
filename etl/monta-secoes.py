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
    links = [("index.html", "Acervo", "acervo")]
    links += [(slug + ".html", titulo, slug) for slug, titulo, _, _, _ in SECOES]
    links.append(("blog.html", "Blog", "blog"))
    itens = "\n".join(
        '        <a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if chave == ativo else "", esc(rotulo))
        for href, rotulo, chave in links)
    return """<header class="topo">
  <div class="topo__interno">
    <a class="topo__marca" href="index.html">
      <span class="ponto" aria-hidden="true"></span>
      RENAP <span>· Acervo</span>
    </a>
    <nav class="topo__links" aria-label="Seções">
%s
    </nav>
    <div class="topo__tema">
      <label for="tema">Tema</label>
      <select id="tema" name="tema">
        <option value="light">Claro</option>
        <option value="dark">Escuro</option>
        <option value="brasil">Brasil</option>
        <option value="high-contrast">Alto contraste</option>
        <option value="pequi">Pequi</option>
        <option value="cerrado">Cerrado</option>
        <option value="mata-atlantica">Mata Atlântica</option>
        <option value="caatinga">Caatinga</option>
        <option value="pantanal">Pantanal</option>
      </select>
    </div>
  </div>
</header>""" % itens


def rodape():
    return """<footer class="rodape">
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
    return """      <li class="item" data-temas="%s">
        <a class="item__link" href="%s.html">
          <span class="etiqueta">%s · %s</span>
          <h3>%s</h3>
          <p>%s</p>
          <span class="item__ficha">%s · %s</span>
        </a>
      </li>""" % (
        esc(" ".join((registro.get("temas") or [""])[0].split("-"))),
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
  <title>%s · Acervo Assessoria Jurídica Popular</title>
  <meta name="description" content="%s" />
  <link rel="icon" href="data:," />
  <link rel="stylesheet" href="fontes/fontshare.css" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css" />
  <link rel="stylesheet" href="reveal.css" />
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
      <ul class="lista-acervo" data-revelar-grupo>
%s
      </ul>
    </section>
%s
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
<script src="reveal.js" defer></script>
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
