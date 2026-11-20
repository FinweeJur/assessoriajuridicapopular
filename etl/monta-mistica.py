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
    blocos = [b for b in blocos if b]
    if len(blocos) < 3:  # documento exportado com uma linha por parágrafo
        blocos = [re.sub(r"[ \t]+", " ", p).strip() for p in texto.split("\n")]
        blocos = [b for b in blocos if b]
    return blocos


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
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mística: acúmulos, aprendizados, saberes — AJP</title>
  <meta name="description" content="Texto dos movimentos populares sobre mística, com citação de Ademar Bogo." />
  <link rel="stylesheet" href="fontes/fontshare.css?v=2" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=27" />
  <link rel="stylesheet" href="reveal.css?v=27" />
  <link rel="stylesheet" href="componentes/radio.css" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
@@TOPO@@

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
        <div class="ficha__linha"><dt>Fonte</dt><dd><a href="@@DOC_MISTICA@@" target="_blank" rel="noopener">documento original</a></dd></div>
      </dl>
    </header>

    <figure class="cartao citacao">
      <blockquote cite="@@DOC_BOGO@@">
        @@CITACAO@@
      </blockquote>
      <figcaption>
        <b>Ademar Bogo</b>, em “A mística: parte da vida e da luta”,
        <a href="@@DOC_BOGO@@" target="_blank" rel="noopener">texto completo no documento</a>.
        Capturado em <time datetime="2026-11-20">20 de novembro de 2026</time>.
      </figcaption>
    </figure>

    <div data-revelar-grupo class="cartao corpo">
      @@CORPO@@
    </div>

    <section class="compartilhar" data-compartilhar
             data-url="https://finweejur.github.io/assessoriajuridicapopular/mistica.html"
             data-titulo="Mística: acúmulos, aprendizados, saberes e apontamentos iniciais"
             data-autor="Militantes dos movimentos populares brasileiros"
             data-data="2023-01-01" data-fonte-url="@@DOC_MISTICA@@"
             data-fonte="Levante Popular da Juventude">
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
<script src="casca.js?v=3" defer></script>
</body>
</html>
""".replace("@@TOPO@@", ms.topo("texto")).replace("@@DOC_BOGO@@", DOC_BOGO).replace("@@CITACAO@@", citacao_html).replace("@@CORPO@@", corpo_html).replace("@@DOC_MISTICA@@", DOC_MISTICA).replace("@@RODAPE@@", ms.rodape())

with io.open(os.path.join(RAIZ, "mistica.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(PAGINA)

print("mistica.html:", len(PAGINA), "bytes | trechos citados:", len(trechos), "| parágrafos:", len(corpo))
