"""Página da mística: texto dos movimentos + citação de Ademar Bogo."""
import importlib.util
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
FONTES = os.path.join(RAIZ, "fontes-textos")

spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)


def paragrafos(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        texto = f.read().lstrip("\ufeff").replace("\r\n", "\n")
    blocos = [re.sub(r"[ \t]+", " ", p).strip() for p in re.split(r"\n\s*\n", texto)]
    return [b for b in blocos if b]


mistica = paragrafos(os.path.join(FONTES, "mistica.txt"))
citacao = paragrafos(os.path.join(FONTES, "citacao.txt"))

# Mística: título, crédito, corpo
titulo = mistica[0].split(" - ")[-1].strip().rstrip(".") if mistica else "Mística"
credito = next((p for p in mistica if p.lower().startswith("escrito por")), "")
corpo = [p for p in mistica[1:] if p != credito]

# Citação: as quatro primeiras passagens de Ademar Bogo, sem o cabeçalho
inicio = next((i for i, p in enumerate(citacao) if "Ademar Bogo" in p), 0)
trechos = citacao[inicio + 1: inicio + 5]

DOC_MISTICA = "https://docs.google.com/document/d/1hxF-AgZYoka9yU0PLZ0MDCqWvpGq0UFnthlDXSP1W_w/edit"
DOC_BOGO = "https://docs.google.com/document/d/1RMnMFcnBsUKNji-1z7j1jH9dNulNUSkG/edit"

corpo_html = "\n      ".join("<p>%s</p>" % ms.esc(p) for p in corpo)
citacao_html = "\n        ".join("<p>%s</p>" % ms.esc(p) for p in trechos)

PAGINA = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mística: acúmulos, aprendizados, saberes — AJP</title>
  <meta name="description" content="Texto dos movimentos populares sobre mística, com citação de Ademar Bogo." />
  <link rel="stylesheet" href="fontes/fontshare.css" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=3" />
  <link rel="stylesheet" href="reveal.css?v=3" />
  <link rel="stylesheet" href="componentes/radio.css" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s

<main id="conteudo">
  <nav class="migalha" aria-label="Você está em">
    <a href="index.html">Acervo</a> <span aria-hidden="true">/</span>
    <a href="memoria-e-cultura.html">Memória e cultura</a> <span aria-hidden="true">/</span>
    <span aria-current="page">Mística</span>
  </nav>

  <article data-revelar-grupo class="pagina">
    <header>
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Mística · 2023</p>
      <h1 id="titulo">Mística: acúmulos, aprendizados, saberes e apontamentos iniciais</h1>
      <dl class="ficha">
        <div class="ficha__linha"><dt>Autoria</dt><dd>Militantes dos movimentos populares brasileiros</dd></div>
        <div class="ficha__linha"><dt>Feito para</dt><dd>3º Acampamento Estadual do Levante Popular da Juventude, UFJF, Juiz de Fora/MG</dd></div>
        <div class="ficha__linha"><dt>Ano</dt><dd>2023</dd></div>
        <div class="ficha__linha"><dt>Fonte</dt><dd><a href="%s" target="_blank" rel="noopener">documento original</a></dd></div>
      </dl>
    </header>

    <figure class="cartao citacao">
      <blockquote cite="%s">
        %s
      </blockquote>
      <figcaption>
        <b>Ademar Bogo</b>, em “A mística: parte da vida e da luta”,
        <a href="%s" target="_blank" rel="noopener">texto completo no documento</a>.
        Capturado em <time datetime="2026-11-20">20 de novembro de 2026</time>.
      </figcaption>
    </figure>

    <div data-revelar-grupo class="cartao corpo">
      %s
    </div>

    <section class="compartilhar" data-compartilhar
             data-url="https://finweejur.github.io/assessoriajuridicapopular/mistica.html"
             data-titulo="Mística: acúmulos, aprendizados, saberes e apontamentos iniciais"
             data-autor="Militantes dos movimentos populares brasileiros"
             data-data="2023-01-01" data-fonte-url="%s"
             data-fonte="Levante Popular da Juventude">
      <h2>Compartilhar e citar</h2>
      <div class="compartilhar__botoes">
        <button type="button" data-acao="whatsapp">WhatsApp</button>
        <button type="button" data-acao="telegram">Telegram</button>
        <button type="button" data-acao="instagram">Instagram</button>
        <button type="button" data-acao="copiar-texto">Copiar texto</button>
        <button type="button" data-acao="copiar-citacao">Copiar citação ABNT</button>
      </div>
      <p class="compartilhar__status" data-status role="status" aria-live="polite" data-visivel="false"></p>
    </section>
  </article>
</main>

%s

<script src="compartilhar.js" defer></script>
<script src="site.js" defer></script>
<script src="reveal.js" defer></script>
<script src="componentes/radio.js" defer></script>
</body>
</html>
""" % (ms.topo("texto"), DOC_BOGO, citacao_html, DOC_BOGO, corpo_html, DOC_MISTICA, ms.rodape())

with io.open(os.path.join(RAIZ, "mistica.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(PAGINA)

print("mistica.html:", len(PAGINA), "bytes | trechos citados:", len(trechos), "| parágrafos:", len(corpo))
