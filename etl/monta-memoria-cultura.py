"""Gera a página 'Memória e cultura' (porta Mística).

Separa o que antes vivia junto em `memoria.html`:
  * `memoria-e-cultura.html` — homenagens, crônicas, arte e datas (cultura);
  * `memoria.html` — registro histórico da AJP e da RENAP (Rede e pesquisa).

A casca vem de `cultura.html` para herdar topo, rádio, rodapé e scripts.
"""
import html
import io
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
BASE = os.path.join(RAIZ, "cultura.html")
SAIDA = os.path.join(RAIZ, "memoria-e-cultura.html")

GRUPOS = [
    ("homenagens", "Homenagens e presenças", "Gente que fez a AJP e segue presente na memória da rede.", [
        "homenagens-ao-advogado-eugenio-lyra", "poemas-em-homenagem-a-eugenio-lyra",
        "companheiro-baldez-presente", "companheiro-baldez-presente-2",
        "companheiro-lavratti-presente", "thomaz-miguel-pressburger-presente",
        "morreu-lia-pires-e-com-ele-a-advocacia", "com-tristeza-luis-adeus",
        "falece-herrera-flores", "tres-anos-sem-caju-sepe-tiaraju",
        "adeus-sete-quedas-adeus-ivo-rodrigues", "80-anos-do-miguel-baldez",
    ]),
    ("cronicas", "Crônicas e relatos", "O conflito, o cotidiano e a resistência contados por quem viveu.", [
        "imbituba-cronica-de-um-mandado-de-despejo", "relato-em-praca-de-guerra",
        "o-dia-9-o-dia-10-o-dia-11-e-o-dia-12", "microconto",
        "uma-sensacao", "auto-retrato", "carta-do-ano-que-nao-terminou",
        "advocacia-delirante-parte-i", "advocacia-delirante-parte-ii",
    ]),
    ("arte", "Arte, música e imagem", "Teatro do oprimido, cinema, música e o fazer cultural na AJP.", [
        "o-teatro-e-o-ensino-do-direito-1", "o-teatro-e-o-ensino-do-direito-2",
        "o-teatro-e-o-ensino-do-direito-3", "cultura-negra-historia-e-musica",
        "cineclube-ajp-narradores-de-jave", "cinema-e-luta-no-campo",
        "documentario-o-cinema-libertario", "papo-de-cinema",
        "mercedes-sosa-e-sebastiao-salgado", "coraje-e-musica",
        "quem-planta-cultura-colhe-revolucao", "quem-planta-cultura-colhe-revolucao-2",
    ]),
    ("datas", "Datas que a rede celebra", "Março das mulheres, primeiro de maio, natal dos sem, ano novo.", [
        "08-de-marco-dia-de-luta-das-mulheres-estudantes", "dia-internacional-da-mulher",
        "mais-sobre-o-dia-da-mulher-e-o-feminismo", "maio-mes-do-trabalho",
        "o-natal-dos-sem-no-brasil", "presente-de-ano-novo",
    ]),
]


def esc(t):
    return html.escape(t or "", quote=False)


idx = json.load(io.open(INDICE, encoding="utf-8"))
por_slug = {r["slug"]: r for r in idx}


def cartao(slug, etiqueta):
    reg = por_slug.get(slug)
    if not reg:
        return ""
    titulo = reg.get("titulo") or slug
    resumo = (reg.get("resumo") or "").strip()
    if len(resumo) > 150:
        corte = resumo[:150].rsplit(" ", 1)[0].rstrip(",.;:—–-")
        resumo = corte + "…"
    ano = (reg.get("data") or "")[:4]
    return ('<a class="cartao destaque colecao__post" href="%s.html">\n'
            '      <span class="etiqueta">%s · %s</span>\n'
            '      <h3>%s</h3>\n'
            '      <p>%s</p>\n'
            '    </a>') % (esc(slug), esc(etiqueta), esc(ano), esc(titulo), esc(resumo))


blocos = []
atalhos = []
total = 0
for ident, titulo, nota, slugs in GRUPOS:
    cartoes = "".join(cartao(s, titulo) for s in slugs)
    if not cartoes:
        continue
    n = cartoes.count('class="cartao destaque colecao__post"')
    total += n
    atalhos.append('<a href="#%s">%s</a>' % (ident, esc(titulo.split(" e ")[0] if ident != "arte" else "Arte")))
    blocos.append("""<section class="secao" id="%s" aria-labelledby="%s-titulo">
          <div class="secao__cabeca"><h2 id="%s-titulo">%s</h2>
          <p class="secao__nota">%s</p></div>
          <div class="grade-3">%s</div>
        </section>""" % (ident, ident, ident, esc(titulo), esc(nota), cartoes))

corpo = """
  <nav class="migalha" aria-label="Você está em"><a href="index.html">Início</a> <span aria-hidden="true">/</span> <a href="mistica.html">Mística</a> <span aria-hidden="true">/</span> <span aria-current="page">Memória e cultura</span></nav>
  <nav class="subnav" aria-label="Dentro de Mística"><span class="subnav__rotulo">Mística</span><a href="mistica.html">← Mística</a><a href="memoria-e-cultura.html" aria-current="page">Memória e cultura</a><a href="cultura.html">Cultura</a><a href="poemas.html">Poemas e Caderno</a></nav>
  <section class="hero hero--texto colecao-hero">
    <div class="hero__foto" style="background-image:url('fotos/eventos/2012-nasce-a-coluna-direitos-das-marias-046.jpg')" aria-hidden="true"></div>
    <div class="hero__veu" aria-hidden="true"></div>
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Mística</p>
      <h1>Memória e cultura</h1>
      <p class="lead">O que o acervo guarda da vida da AJP: homenagens a quem fez a rede,
      crônicas do conflito, arte e as datas que a luta celebra.</p>
    </div>
  </section>
  <div class="miolo">
    <nav class="colecao__atalhos" aria-label="Memória e cultura">%s</nav>
    <p class="colecao__nota">Esta página reúne a <b>memória cultural</b> da assessoria.
    A cronologia da rede — marcos, publicações por ano e efemérides — está em
    <a href="memoria.html">Memória da AJP e da RENAP</a>, dentro de Rede e pesquisa.
    Os poemas ficam em <a href="poemas.html">Poemas e Caderno</a>.</p>
    %s
    <section class="secao" aria-labelledby="mais-titulo">
      <div class="secao__cabeca"><h2 id="mais-titulo">Continuar</h2></div>
      <p><a class="botao" href="cultura.html">Ver a coleção Cultura →</a></p>
    </section>
  </div>
""" % ("".join(atalhos), "\n".join(blocos))

t = io.open(BASE, encoding="utf-8").read()
t = re.sub(r"<title>.*?</title>",
           "<title>Memória e cultura · Mística · AJP — Assessoria Jurídica Popular</title>",
           t, count=1, flags=re.S)
t = re.sub(r'<meta name="description" content="[^"]*"',
           '<meta name="description" content="Homenagens, crônicas, arte e datas da AJP: a memória cultural da assessoria jurídica popular."',
           t, count=1)
t = re.sub(r"<main\b[^>]*>.*?</main>",
           lambda m: "<main id=\"conteudo\">\n%s\n</main>" % corpo, t, count=1, flags=re.S)

io.open(SAIDA, "w", encoding="utf-8", newline="\n").write(t)
print("memoria-e-cultura.html:", len(t), "bytes |", total, "cartões")
