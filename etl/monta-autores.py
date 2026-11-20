"""Páginas de autor e índice de autores.

Cada autor ganha uma página com todos os seus textos, em ordem.
Autores com um só texto também entram: a página existe para dar rosto ao acervo.
"""
import html
import io
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def esc(t):
    return html.escape(t or "", quote=False)


def slug(texto):
    sem = unicodedata.normalize("NFD", texto or "")
    sem = "".join(c for c in sem if unicodedata.category(c) != "Mn")
    sem = re.sub(r"[^a-zA-Z0-9]+", "-", sem).strip("-").lower()
    return sem[:60] or "autor"


def data_curta(iso):
    if not iso or len(iso) < 10:
        return ""
    ano, mes, dia = iso[:10].split("-")
    return "%d de %s de %s" % (int(dia), MESES[int(mes) - 1], ano)


def main():
    registros = json.loads(io.open(INDICE, encoding="utf-8").read())

    autores = {}
    for r in registros:
        nome = (r.get("autor") or "Redação").strip()
        autores.setdefault(nome, []).append(r)

    # índice de autores
    linhas = []
    for nome, itens in sorted(autores.items(), key=lambda x: -len(x[1])):
        anos = sorted({(i.get("data") or "")[:4] for i in itens if i.get("data")})
        linhas.append(
            '<li class="item"><a class="item__link" href="autor-%s.html">'
            '<span class="etiqueta">%d %s</span><h3>%s</h3>'
            '<p>%s a %s</p><span class="item__ficha">Ver todos os textos</span></a></li>'
            % (slug(nome), len(itens), "texto" if len(itens) == 1 else "textos",
               esc(nome), anos[0] if anos else "", anos[-1] if anos else ""))

    indice_autores = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Autores · AJP — Assessoria Jurídica Popular</title>
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
<main id="conteudo">
  <section class="hero hero--texto">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Quem escreve</p>
      <h1>Autores do acervo</h1>
      <p class="lead">%d pessoas assinam os %d textos. Cada nome abre a lista completa.</p>
    </div>
  </section>
  <div class="miolo">
    <ul class="lista-acervo lista-autores" data-revelar-grupo data-paginada>
%s
    </ul>
  </div>
</main>
<script src="casca.js?v=15" defer></script>
<script src="leitura.js?v=2" defer></script>
<script src="site.js?v=2" defer></script>
<script src="reveal.js" defer></script>
<script src="fundo-grade.js?v=3" defer></script>
</body>
</html>
""" % (len(autores), len(registros), "\n".join(linhas))

    with io.open(os.path.join(RAIZ, "autores.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(indice_autores)

    # páginas individuais
    for nome, itens in autores.items():
        itens.sort(key=lambda r: r.get("data") or "", reverse=True)
        cartoes = "\n".join(
            '<li class="item"><a class="item__link" href="%s.html">'
            '<span class="etiqueta">%s · %s</span><h3>%s</h3><p>%s</p>'
            '<span class="item__ficha">%s</span></a></li>'
            % (esc(r["slug"]), esc(r.get("tema")), esc(r.get("ano")), esc(r.get("titulo")),
               esc((r.get("resumo") or "")[:180]), esc(data_curta(r.get("data"))))
            for r in itens)
        anos = sorted({(i.get("data") or "")[:4] for i in itens if i.get("data")})
        pagina = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>%s · Autores · AJP</title>
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
<main id="conteudo">
  <section class="hero hero--texto">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Autor</p>
      <h1>%s</h1>
      <p class="lead">%d %s no acervo, de %s a %s.</p>
      <p class="hero__acoes"><a class="botao secundario" href="autores.html">← Todos os autores</a></p>
    </div>
  </section>
  <div class="miolo">
    <ul class="lista-acervo lista-autores" data-revelar-grupo data-paginada>
%s
    </ul>
  </div>
</main>
<script src="casca.js?v=15" defer></script>
<script src="leitura.js?v=2" defer></script>
<script src="site.js?v=2" defer></script>
<script src="reveal.js" defer></script>
<script src="fundo-grade.js?v=3" defer></script>
</body>
</html>
""" % (esc(nome), esc(nome), len(itens), "texto" if len(itens) == 1 else "textos",
       anos[0] if anos else "", anos[-1] if anos else "", cartoes)
        with io.open(os.path.join(RAIZ, "autor-%s.html" % slug(nome)), "w", encoding="utf-8", newline="\n") as f:
            f.write(pagina)

    print("autores:", len(autores))
    for nome, itens in sorted(autores.items(), key=lambda x: -len(x[1]))[:6]:
        print("  %-32s %3d" % (nome[:32], len(itens)))


if __name__ == "__main__":
    main()
