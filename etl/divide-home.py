"""Separa a home (apresentação) do acervo (lista de posts)."""
import importlib.util
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

p = os.path.join(RAIZ, "index.html")
t = io.open(p, encoding="utf-8").read()

if os.path.exists(os.path.join(RAIZ, "acervo.html")):
    print("acervo.html ja existe; nada a fazer")
else:
    ini = t.find('<section class="fita-secao"')
    fim = t.find('<section class="referencias"')
    if ini < 0 or fim < 0:
        raise SystemExit("nao achei filtros/lista na home")
    bloco = t[ini:fim].rstrip()

    # Remove a lista da home
    t = t[:ini] + t[fim:]
    # CTA do bento e do herói vão para o acervo
    t = t.replace('href="#lista-acervo"', 'href="acervo.html#lista-acervo"')
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)

    ACERVO = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Acervo · 713 textos · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="Os 713 textos do blog Assessoria Jurídica Popular, de 2009 a 2024, com busca, filtros por tipo, ano e palavra-chave." />
  <link rel="stylesheet" href="fontes/fontshare.css?v=3" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=48" />
  <link rel="stylesheet" href="reveal.css?v=48" />
  <link rel="stylesheet" href="componentes/radio.css" />
  <link rel="stylesheet" href="leitura.css?v=1" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s
<main id="conteudo">
  <section class="hero hero--texto">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Acervo</p>
      <h1>713 textos em citação direta</h1>
      <p class="lead">Busque por título, autor, tema ou palavra-chave. Filtre por tipo de
      texto, ano e ordem. Cada página traz autor, data, link para o original e data de captura.</p>
      <p class="hero__acoes"><a class="botao secundario" href="index.html">← Voltar à apresentação</a></p>
    </div>
  </section>
%s
</main>
%s
<script src="casca.js?v=15" defer></script>
<script src="site.js?v=2" defer></script>
<script src="reveal.js" defer></script>
<script src="componentes/radio.js" defer></script>
<script src="leitura.js?v=2" defer></script>
<script src="fundo-grade.js?v=5" defer></script>
</body>
</html>
""" % (ms.topo("acervo"), bloco, ms.rodape())
    io.open(os.path.join(RAIZ, "acervo.html"), "w", encoding="utf-8", newline="\n").write(ACERVO)
    print("acervo.html:", len(ACERVO), "bytes")

# 2. Navbar e rodapé passam a apontar para acervo.html
p = os.path.join(RAIZ, "etl", "monta-secoes.py")
g = io.open(p, encoding="utf-8").read()
g = g.replace('<a href="index.html"%s>Acervo</a>', '<a href="acervo.html"%s>Acervo</a>', 1)
g = g.replace('<li><a href="index.html">Todos os textos</a></li>',
              '<li><a href="acervo.html">Todos os textos</a></li>', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(g)
print("navbar acervo:", 'href="acervo.html"' in g)

# 3. atualiza-indice passa a escrever no acervo
p = os.path.join(RAIZ, "etl", "atualiza-indice.py")
a = io.open(p, encoding="utf-8").read()
a = a.replace('CAPA = os.path.join(RAIZ, "index.html")', 'CAPA = os.path.join(RAIZ, "acervo.html")')
io.open(p, "w", encoding="utf-8", newline="\n").write(a)
print("atualiza-indice:", 'acervo.html' in a)
