"""Glossário e linha do tempo, com link no menu e no rodapé."""
import importlib.util
import io
import json
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

MODELO = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>@@TITULO@@ · AJP — Assessoria Jurídica Popular</title>
  <link rel="stylesheet" href="fontes/fontshare.css?v=3" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=36" />
  <link rel="stylesheet" href="reveal.css?v=36" />
  <link rel="stylesheet" href="componentes/radio.css" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
@@TOPO@@
<main id="conteudo">
  <section class="hero hero--texto">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>@@OLHO@@</p>
      <h1>@@TITULO@@</h1>
      <p class="lead">@@LEAD@@</p>
    </div>
  </section>
  <div class="miolo">@@CORPO@@</div>
</main>
@@RODAPE@@
<script src="casca.js?v=6" defer></script>
<script src="site.js?v=2" defer></script>
<script src="reveal.js" defer></script>
<script src="componentes/radio.js" defer></script>
<script src="fundo-grade.js?v=3" defer></script>
</body>
</html>
"""


def escreve(arquivo, titulo, olho, lead, corpo):
    html = MODELO.replace("@@TOPO@@", ms.topo("texto")).replace("@@RODAPE@@", ms.rodape())
    html = html.replace("@@CORPO@@", corpo)
    for chave, valor in {"@@TITULO@@": ms.esc(titulo), "@@OLHO@@": ms.esc(olho),
                         "@@LEAD@@": ms.esc(lead)}.items():
        html = html.replace(chave, valor)
    with io.open(os.path.join(RAIZ, arquivo), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("ok:", arquivo)


TERMOS = [
    ("Assessoria jurídica popular", "Trabalho de advogados, estudantes e educadores com movimentos sociais: orientação jurídica, educação popular e organização. Não é caridade.", "o-que-e-assessoria-juridica-popular.html"),
    ("Advocacia popular", "Prática de advogados que colocam o direito a serviço das lutas coletivas, e não só do caso individual.", "assessoria-juridica-popular.html"),
    ("AJUP", "Assessoria jurídica universitária popular: núcleo de estudantes que atende movimentos e forma juristas.", "educacao-popular.html"),
    ("Direito insurgente", "Leitura do direito a partir das lutas: o direito também é campo de disputa, não só norma posta.", "teoria-critica.html"),
    ("Pluralismo jurídico", "Reconhecimento de que mais de uma ordem jurídica coexiste — a estatal e as comunitárias, indígenas e camponesas.", "teoria-critica.html"),
    ("Educação popular", "Formação feita com o povo, não para o povo: parte do saber de quem vive a situação.", "educacao-popular.html"),
    ("Movimento social", "Organização coletiva que reivindica direitos: terra, moradia, água, trabalho, território.", "movimentos-sociais.html"),
    ("RENAP", "Rede Nacional de Advogados e Advogadas Populares, articulada há três décadas.", "https://www.renap.org.br/"),
    ("RENAJU", "Rede Nacional de Assessoria Jurídica Universitária.", "educacao-popular.html"),
    ("IPDMS", "Instituto de Pesquisa, Direitos e Movimentos Sociais, parceiro deste acervo.", "https://ipdms.org.br/"),
    ("MAB", "Movimento dos Atingidos por Barragens.", "https://mab.org.br/"),
    ("MST", "Movimento dos Trabalhadores Rurais Sem Terra.", "https://mst.org.br/"),
    ("CPT", "Comissão Pastoral da Terra: acervo de conflitos no campo.", "https://www.cptnacional.org.br/"),
    ("CIMI", "Conselho Indigenista Missionário.", "https://cimi.org.br/"),
    ("Defensoria Pública", "Órgão estatal de assistência jurídica gratuita, previsto na Constituição de 1988.", "assessoria-juridica-popular-no-mundo.html"),
    ("Mística", "Energia que sustenta a luta: arte, memória e celebração dentro da organização popular.", "mistica.html"),
    ("Criminalização", "Uso do direito penal contra movimentos e defensores de direitos.", "direitos-humanos.html"),
    ("Torto Arado", "Romance de Itamar Vieira Junior sobre terra, trabalho e ancestralidade.", ""),
]

def linha_termo(termo, definicao, url):
    if not url:
        return '        <li><b>%s</b> — %s</li>' % (ms.esc(termo), ms.esc(definicao))
    externo = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
    return '        <li><b>%s</b> — %s <a href="%s"%s>ver</a></li>' % (
        ms.esc(termo), ms.esc(definicao), url, externo)


linhas = "\n".join(linha_termo(termo, definicao, url) for termo, definicao, url in TERMOS)

corpo = """    <section class="secao">
      <div class="secao__cabeca"><h2>Termos do acervo</h2>
      <p class="secao__nota">%d verbetes, em uma linha cada</p></div>
      <ul class="linhas glossario">
%s
      </ul>
    </section>""" % (len(TERMOS), linhas)

escreve("glossario.html", "Glossário", "Glossário",
        "Os termos que aparecem nos textos, explicados em uma linha.", corpo)

# Linha do tempo
registros = json.loads(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8").read())
por_ano = {}
for r in registros:
    ano = (r.get("data") or "")[:4]
    if ano:
        por_ano[ano] = por_ano.get(ano, 0) + 1

maior = max(por_ano.values()) if por_ano else 1
itens = []
for ano in sorted(por_ano, reverse=True):
    n = por_ano[ano]
    largura = max(2, round(n / maior * 100))
    itens.append('        <li class="ano"><a href="blog.html#ano-%s">'
                 '<b>%s</b><span class="ano__barra" style="--n:%d%%"></span>'
                 '<span class="ano__conta">%d %s</span></a></li>'
                 % (ano, ano, largura, n, "texto" if n == 1 else "textos"))

corpo = """    <section class="secao">
      <div class="secao__cabeca"><h2>2009 a 2024</h2>
      <p class="secao__nota">Textos por ano. 2014 não tem publicação.</p></div>
      <ul class="linha-tempo">
%s
      </ul>
    </section>
    <section class="secao">
      <div class="secao__cabeca"><h2>O que a curva diz</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">📈</span><b>2010 e 2011 concentram 450 textos</b> — o blogue nasce como boletim da rede.</li>
        <li><span class="emoji" aria-hidden="true">🕳️</span><b>2014 sem publicação</b> e 2017 com três: a virada para o site institucional.</li>
        <li><span class="emoji" aria-hidden="true">🕰️</span><b>Depois de 2016, 22 textos</b> — memória e balanço, não notícia.</li>
      </ul>
    </section>""" % "\n".join(itens)

escreve("linha-do-tempo.html", "Linha do tempo", "Série histórica",
        "O acervo ano a ano: quando a rede escreveu mais e quando parou.", corpo)

# Link no menu e no rodapé
gen = os.path.join(RAIZ, "etl", "monta-secoes.py")
with io.open(gen, encoding="utf-8") as f:
    g = f.read()
if "linha-do-tempo.html" not in g:
    g = g.replace('<a href="autores.html">Autores</a>',
                  '<a href="linha-do-tempo.html">Linha do tempo</a>\n      <a href="autores.html">Autores</a>', 1)
    g = g.replace('<li><a href="o-que-e-assessoria-juridica-popular.html">O que é AJP</a></li>',
                  '<li><a href="o-que-e-assessoria-juridica-popular.html">O que é AJP</a></li>\n'
                  '        <li><a href="glossario.html">Glossário</a></li>\n'
                  '        <li><a href="linha-do-tempo.html">Linha do tempo</a></li>', 1)
    with io.open(gen, "w", encoding="utf-8", newline="\n") as f:
        f.write(g)
print("menu:", "linha-do-tempo.html" in g)
