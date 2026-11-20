"""Corrige paginação e blog, e publica a antologia do Caderno de Poesias."""
import io
import os
import re
import unicodedata

from pypdf import PdfReader

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# ── 1. site.js: paginação não pode filtrar pelo próprio hidden ─────────────
js_path = os.path.join(RAIZ, "site.js")
with io.open(js_path, encoding="utf-8") as f:
    js = f.read()

js = js.replace("""  function visiveis() {
    return itens.filter(function (li) { return !li.hidden && !li.dataset.fora; });
  }""",
"""  function visiveis() {
    // O hidden é consequência da paginação; o filtro olha só o que foi excluído.
    return itens.filter(function (li) { return li.dataset.fora !== '1'; });
  }""")

with io.open(js_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)

# ── 2. Blog: uma lista só, sem paginação quebrada ─────────────────────────
gen = os.path.join(RAIZ, "etl", "monta-secoes.py")
with io.open(gen, encoding="utf-8") as f:
    g = f.read()

if 'blog = blog.replace' not in g:
    g = g.replace("""    with io.open(os.path.join(RAIZ, "blog.html"), "w", encoding="utf-8", newline="\\n") as f:
        f.write(blog)""",
"""    # Blog: sem paginação e sem fita — a lista por ano já é a navegação.
    blog = blog.replace(' data-paginada', '')
    blog = re.sub(r'<div class="fita">.*?</div>\\s*</section>', '</section>', blog, count=1, flags=re.S)
    blog = blog.replace('<div class="mais"><button type="button" data-mais>Ver mais 24</button></div>', '')
    blog = blog.replace('0 textos nesta seção', '%d textos em %d anos' % (len(registros), len(grupos)))

    with io.open(os.path.join(RAIZ, "blog.html"), "w", encoding="utf-8", newline="\\n") as f:
        f.write(blog)""", 1)
    with io.open(gen, "w", encoding="utf-8", newline="\n") as f:
        f.write(g)

# ── 3. Antologia completa ─────────────────────────────────────────────────
import importlib.util
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

caminho = os.path.join(RAIZ, "fontes-textos", "Poesias e Crônicas-20261120T070851Z-1-001",
                       "Poesias e Crônicas", "CADERNO DE POESIAS - CMM.pdf")

leitor = PdfReader(caminho)
partes = []
for numero, pagina in enumerate(leitor.pages, start=1):
    if numero <= 8:   # sumário
        continue
    texto = (pagina.extract_text() or "").strip()
    if not texto:
        continue
    partes.append('<section class="poema" id="p%d"><p class="poema__fonte">p. %d</p><pre class="poema__texto">%s</pre></section>'
                  % (numero, numero, ms.esc(texto)))

corpo = """    <p class="aviso-lote"><b>Antologia publicada com autorização.</b> O organizador declara que os
    direitos estão liberados; o crédito de cada autor permanece no texto. Trechos e poemas podem ser
    citados com o nome do autor e o Caderno.</p>

    <section class="secao" aria-labelledby="ler">
      <div class="secao__cabeca"><h2 id="ler">Ler a antologia</h2>
      <p class="secao__nota">Texto extraído do PDF, página por página</p></div>
      <div class="cartao antologia">
%s
      </div>
    </section>

    <section class="secao" aria-labelledby="creditos">
      <div class="secao__cabeca"><h2 id="creditos">Créditos</h2></div>
      <p class="folha">MORI, Cleber (org.). <i>Caderno de Poesias</i>. 2010.</p>
    </section>""" % "\n".join(partes)

MODELO = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Caderno de Poesias · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="Antologia Caderno de Poesias (CMM, 2010), publicada com autorização." />
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
  <nav class="migalha" aria-label="Você está em">
    <a href="index.html">Acervo</a> <span aria-hidden="true">/</span>
    <a href="memoria-e-cultura.html">Memória e cultura</a> <span aria-hidden="true">/</span>
    <span aria-current="page">Caderno de Poesias</span>
  </nav>
  <article data-revelar-grupo class="pagina">
    <header>
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Poesia · 2010</p>
      <h1 id="titulo">Caderno de Poesias</h1>
      <p class="lead">A antologia completa, com os autores e os textos como estão no caderno.</p>
    </header>
    @@CORPO@@
    <section class="compartilhar" data-compartilhar
             data-url="https://finweejur.github.io/assessoriajuridicapopular/caderno-de-poesias.html"
             data-titulo="Caderno de Poesias" data-autor="Cleber Mori (org.)" data-data="2010-01-01"
             data-fonte-url="" data-fonte="Caderno de Poesias">
      <h2>Compartilhar e citar</h2>
      <div class="compartilhar__botoes">
        <button type="button" data-acao="whatsapp"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 21l2.2-5.3A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8.5 10.5c.5 2 2 3.5 4 4l1.5-1.5 2 1"/></svg> WhatsApp</button>
        <button type="button" data-acao="telegram"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="m22 3-9.5 18-2-7.5L3 11l19-8Z"/><path d="m10.5 13.5 3-3"/></svg> Telegram</button>
        <button type="button" data-acao="instagram"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8"/></svg> Instagram</button>
        <button type="button" data-acao="copiar-texto"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg> Copiar texto</button>
        <button type="button" data-acao="copiar-citacao"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16M4 12h10M4 17h7"/><path d="m17 15 3 2-3 2"/></svg> Copiar citação ABNT</button>
      </div>
      <p class="compartilhar__status" data-status role="status" aria-live="polite" data-visivel="false"></p>
    </section>
  </article>
</main>
@@RODAPE@@
<script src="compartilhar.js" defer></script>
<script src="site.js?v=2" defer></script>
<script src="reveal.js" defer></script>
<script src="componentes/radio.js" defer></script>
<script src="casca.js?v=6" defer></script>
<script src="fundo-grade.js?v=3" defer></script>
</body>
</html>
"""

html = MODELO.replace("@@TOPO@@", ms.topo("texto")).replace("@@RODAPE@@", ms.rodape()).replace("@@CORPO@@", corpo)
with io.open(os.path.join(RAIZ, "caderno-de-poesias.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

print("antologia:", len(partes), "páginas | html:", round(len(html)/1024), "KB")
