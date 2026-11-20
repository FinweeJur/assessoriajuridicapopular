"""Sitemap completo e linha do tempo com efeito de rolagem (Lightswind)."""
import importlib.util
import io
import json
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
BASE = "https://finweejur.github.io/assessoriajuridicapopular"

spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

# ── 1. Sitemap com tudo que é público ─────────────────────────────────────
registros = json.loads(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8").read())
urls = [BASE + "/" + r["slug"] + ".html" for r in registros]
extras = ["", "blog", "autores", "glossario", "linha-do-tempo", "mistica",
          "coracao-sem-medo", "citacoes", "recomendacoes", "caderno-de-poesias",
          "poemas", "assessoria-juridica-popular-no-mundo", "direito-critico-comparado",
          "assessoria-juridica-popular", "direitos-humanos", "movimentos-sociais",
          "memoria-e-cultura", "teoria-critica", "educacao-popular"]
for e in extras:
    caminho = os.path.join(RAIZ, (e or "index") + ".html")
    if os.path.exists(caminho):
        urls.append(BASE + "/" + (e + ".html" if e else ""))

itens = "\n".join("  <url><loc>%s</loc></url>" % u.replace("&", "&amp;") for u in urls)
sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + itens + "\n</urlset>\n")
io.open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(sitemap)
print("sitemap:", len(urls), "URLs")

# ── 2. Linha do tempo com scroll timeline ─────────────────────────────────
por_ano = {}
for r in registros:
    ano = (r.get("data") or "")[:4]
    if ano:
        por_ano[ano] = por_ano.get(ano, 0) + 1

maior = max(por_ano.values()) if por_ano else 1
itens_ano = []
for ano in sorted(por_ano):
    n = por_ano[ano]
    largura = max(6, round(n / maior * 100))
    itens_ano.append(
        '<li class="tl__item" data-revelar><a class="tl__cartao" href="blog.html#ano-%s">'
        '<span class="tl__ponto" aria-hidden="true"></span>'
        '<b class="tl__ano">%s</b>'
        '<span class="tl__barra" aria-hidden="true"><i style="width:%d%%"></i></span>'
        '<span class="tl__conta">%d %s</span></a></li>'
        % (ano, ano, largura, n, "texto" if n == 1 else "textos"))

CORPO = """    <section class="secao">
      <div class="secao__cabeca"><h2>A linha do acervo</h2>
      <p class="secao__nota">Role a página: a linha se preenche e os anos acendem.</p></div>
      <div class="tl" data-tl>
        <span class="tl__trilho" aria-hidden="true"><i data-tl-linha></i></span>
        <ul class="tl__lista">
%s
        </ul>
      </div>
    </section>
    <section class="secao">
      <div class="secao__cabeca"><h2>O que a curva diz</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">📈</span><b>2010 e 2011 concentram 450 textos</b> — o blogue nasce como boletim da rede.</li>
        <li><span class="emoji" aria-hidden="true">🕳️</span><b>2014 sem publicação</b> e 2017 com três: a virada para o site institucional.</li>
        <li><span class="emoji" aria-hidden="true">🕰️</span><b>Depois de 2016, 22 textos</b> — memória e balanço, não notícia.</li>
      </ul>
    </section>""" % "\n".join(itens_ano)

PAGINA = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Linha do tempo · AJP — Assessoria Jurídica Popular</title>
  <link rel="stylesheet" href="fontes/fontshare.css" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=17" />
  <link rel="stylesheet" href="reveal.css?v=17" />
  <link rel="stylesheet" href="componentes/radio.css" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s
<main id="conteudo">
  <section class="hero hero--texto">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Série histórica</p>
      <h1>Linha do tempo</h1>
      <p class="lead">O acervo ano a ano: quando a rede escreveu mais e quando parou.</p>
    </div>
  </section>
  <div class="miolo">%s</div>
</main>
%s
<script src="linha-tempo.js" defer></script>
<script src="leitura.js" defer></script>
<script src="casca.js" defer></script>
<script src="site.js" defer></script>
<script src="reveal.js" defer></script>
<script src="componentes/radio.js" defer></script>
</body>
</html>
""" % (ms.topo("texto"), CORPO, ms.rodape())

io.open(os.path.join(RAIZ, "linha-do-tempo.html"), "w", encoding="utf-8", newline="\n").write(PAGINA)

# ── 3. CSS do trilho ─────────────────────────────────────────────────────
EXTRA = """
/* Linha do tempo: trilho que se preenche conforme a rolagem */
.tl { position: relative; padding-left: 28px; }
.tl__trilho {
  position: absolute; left: 8px; top: 0; bottom: 0; width: 2px;
  background: color-mix(in srgb, var(--cp-border) 70%, transparent);
  border-radius: 2px; overflow: hidden;
}
.tl__trilho i {
  display: block; width: 100%; height: 0;
  background: linear-gradient(to bottom, var(--cp-primary), color-mix(in srgb, var(--cp-primary) 40%, transparent));
  box-shadow: 0 0 14px color-mix(in srgb, var(--cp-primary) 55%, transparent);
  transition: height .12s linear;
}
.tl__lista { list-style: none; margin: 0; padding: 0; display: grid; gap: 14px; }
.tl__item { position: relative; }
.tl__cartao {
  display: grid; grid-template-columns: 1fr auto; align-items: center;
  gap: 6px 14px; padding: 14px 16px; text-decoration: none !important;
  border: 1px solid var(--borda); border-radius: 12px; color: var(--cp-text);
  transition: border-color .18s var(--curva), transform .18s var(--curva),
              box-shadow .18s var(--curva), background-color .18s var(--curva);
}
.tl__cartao:hover, .tl__cartao:focus-visible {
  border-color: var(--cp-primary); transform: translateX(4px);
  box-shadow: 0 10px 28px rgba(0,0,0,.28);
  background: color-mix(in srgb, var(--cp-primary) 8%, transparent);
}
.tl__ponto {
  position: absolute; left: -24px; top: 22px; width: 10px; height: 10px;
  border-radius: 50%; background: var(--cp-bg);
  border: 2px solid color-mix(in srgb, var(--cp-border) 80%, transparent);
  transition: border-color .2s var(--curva), box-shadow .2s var(--curva), transform .2s var(--curva);
}
.tl__item[data-aceso="true"] .tl__ponto {
  border-color: var(--cp-primary); transform: scale(1.15);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--cp-primary) 22%, transparent),
              0 0 18px color-mix(in srgb, var(--cp-primary) 55%, transparent);
}
.tl__ano { font-family: var(--font-display); font-size: 1.15rem; }
.tl__barra { grid-column: 1 / -1; height: 6px; border-radius: 6px; background: color-mix(in srgb, var(--cp-border) 45%, transparent); overflow: hidden; }
.tl__barra i { display: block; height: 100%; background: var(--cp-primary); border-radius: 6px; }
.tl__conta { font-size: .78rem; color: var(--cp-text-soft); }
@media (prefers-reduced-motion: reduce) {
  .tl__trilho i { transition: none; }
  .tl__cartao:hover { transform: none; }
}
"""

CSS = os.path.join(RAIZ, "acervo.css")
with io.open(CSS, encoding="utf-8") as f:
    css = f.read()
if "Linha do tempo: trilho" not in css:
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css.rstrip() + "\n" + EXTRA)
print("linha do tempo: ok")
