"""Páginas de autor e índice de autores.

Cada autor ganha uma página com todos os seus textos, em ordem.
A casca (topo, rodapé, rádio, scripts) vem de `biblioteca.html`, para os
autores não ficarem com um layout antigo isolado.

Além dos textos do acervo, a página mostra as publicações externas detectadas
por `etl/rastreia-autores.py` (OpenAlex/Crossref/Google Books), quando houver.
"""
import html
import io
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
ARTIGOS = os.path.join(RAIZ, "dados", "autores-artigos.jsonl")
BASE = os.path.join(RAIZ, "biblioteca.html")


def casca_base():
    """HTML-modelo das páginas de autor.

    Usa sempre a versão do último commit (HEAD), nunca a do disco: o arquivo
    `biblioteca.html` pode estar com modificações em curso de outra sessão, e
    as páginas de autor não devem herdar estados instáveis.
    """
    import subprocess
    try:
        r = subprocess.run(
            ["git", "-C", RAIZ, "show", "HEAD:biblioteca.html"],
            capture_output=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.decode("utf-8", "replace")
    except Exception:
        pass
    return io.open(BASE, encoding="utf-8").read()

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def esc(t):
    return html.escape(t or "", quote=False)


def slug(texto):
    sem = unicodedata.normalize("NFD", texto or "")
    sem = "".join(c for c in sem if unicodedata.category(c) != "Mn")
    sem = re.sub(r"[^a-zA-Z0-9]+", "-", sem).strip("-").lower()
    return sem[:60] or "autor"


def norm(s):
    t = unicodedata.normalize("NFD", s or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\s]", " ", t).lower().strip()


def data_curta(iso):
    if not iso or len(iso) < 10:
        return ""
    ano, mes, dia = iso[:10].split("-")
    return "%d de %s de %s" % (int(dia), MESES[int(mes) - 1], ano)


def carrega_rastreados():
    """Mapa nome -> dict com confirmadas/revisao detectadas fora do acervo."""
    mapa = {}
    if not os.path.exists(ARTIGOS):
        return mapa
    for linha in io.open(ARTIGOS, encoding="utf-8"):
        try:
            r = json.loads(linha)
        except Exception:
            continue
        mapa[norm(r.get("nome") or "")] = r
    return mapa


def rotulo_acesso(o):
    doi = o.get("doi") or ""
    if doi:
        url = doi if doi.startswith(("http://", "https://")) else "https://doi.org/" + doi
        return ("DOI", "selo selo--aberto", url)
    url = o.get("url") or ""
    if url and "pdf" in url.lower():
        return ("PDF", "selo selo--aberto", url)
    if url:
        return ("link", "selo", url)
    return ("registro", "selo", "")


def secao_rastreados(nome):
    """Bloco 'publicações fora do acervo' para a página do autor.

    Só aparece quando há pelo menos uma obra confirmada (autoria atestada + tema
    do acervo). Obras apenas prováveis ficam na base interna, fora da página.
    """
    reg = RASTREADOS.get(norm(nome))
    if not reg:
        return ""
    conf = reg.get("detalhe", {}).get("confirmadas", []) or []
    if not conf:
        return ""
    rev = reg.get("detalhe", {}).get("revisao", []) or []
    itens = []
    for o in conf[:40]:
        rot, classe, href = rotulo_acesso(o)
        titulo = esc((o.get("titulo") or "")[:220])
        if href:
            titulo = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(href), titulo)
        ano = " (%s)" % esc(o.get("ano")) if o.get("ano") else ""
        fonte = " · %s" % esc(o.get("fonte").replace("_", " ").title()) if o.get("fonte") else ""
        itens.append("<li>%s%s%s <span class=\"%s\">%s</span></li>" % (
            titulo, ano, fonte, classe, esc(rot)))
    nota_rev = ""
    if rev:
        nota_rev = ("Há ainda %d obra(s) com autoria provável, em revisão."
                    % len(rev))
    corpo_itens = "\n".join(itens)
    return """
<section class="secao" id="fora-do-acervo" aria-labelledby="fora-titulo">
  <div class="secao__cabeca"><h2 id="fora-titulo">Publicações fora do acervo</h2>
  <p class="secao__nota">%d obra(s) rastreada(s) em índices abertos</p></div>
  <p class="colecao__nota">Detectadas em OpenAlex, Crossref e Google Books a partir
  do nome de autoria. Onde há link verificado, ele abre o DOI ou o texto integral;
  o restante é registro bibliográfico para pesquisa.</p>
  <ul class="linhas">
%s
  </ul>
  %s
</section>""" % (len(conf), corpo_itens, ("<p class=\"secao__nota\">%s</p>" % nota_rev))


def shell(titulo, descricao, corpo):
    global _CASA_CACHE
    try:
        t = _CASA_CACHE
    except NameError:
        t = _CASA_CACHE = casca_base()
    t = re.sub(r"<title>.*?</title>",
               "<title>%s · Autores · AJP — Assessoria Jurídica Popular</title>" % esc(titulo),
               t, count=1, flags=re.S)
    t = re.sub(r'<meta name="description" content="[^"]*"',
               '<meta name="description" content="%s"' % esc(descricao), t, count=1)
    t = re.sub(r"<main\b[^>]*>.*?</main>",
               lambda m: '<main id="conteudo">\n%s\n</main>' % corpo, t, count=1, flags=re.S)
    return t


def main():
    global RASTREADOS
    registros = json.loads(io.open(INDICE, encoding="utf-8").read())
    RASTREADOS = carrega_rastreados()

    autores = {}
    for r in registros:
        nome = (r.get("autor") or "Redação").strip()
        autores.setdefault(nome, []).append(r)

    linhas = []
    for nome, itens in sorted(autores.items(), key=lambda x: -len(x[1])):
        anos = sorted({(i.get("data") or "")[:4] for i in itens if i.get("data")})
        linhas.append(
            '<li class="item"><a class="item__link" href="autor-%s.html">'
            '<span class="etiqueta">%d %s</span><h3>%s</h3>'
            '<p>%s a %s</p><span class="item__ficha">Ver todos os textos</span></a></li>'
            % (slug(nome), len(itens), "texto" if len(itens) == 1 else "textos",
               esc(nome), anos[0] if anos else "", anos[-1] if anos else ""))

    corpo_indice = """
<nav class="migalha" aria-label="Você está em"><a href="index.html">Início</a> <span aria-hidden="true">/</span> <span aria-current="page">Autores</span></nav>
<section class="hero hero--texto">
  <div class="hero__interno">
    <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Quem escreve</p>
    <h1>Autores do acervo</h1>
    <p class="lead">%d pessoas assinam os %d textos. Cada nome abre a lista completa.</p>
  </div>
</section>
  <nav class="subnav" aria-label="Dentro de Acervo"><span class="subnav__rotulo">Acervo</span><a href="acervo.html">Todos os textos</a><a href="blog.html">Por ano</a><a href="autores.html" aria-current="page">Autores</a><a href="memoria.html">Memória</a><a href="cultura.html">Cultura</a></nav>
  <nav class="subnav" aria-label="Seções do acervo">
    <span class="subnav__rotulo">Seções</span>
    <a href="assessoria-juridica-popular.html">AJP</a>
    <a href="direitos-humanos.html">Direitos humanos</a>
    <a href="movimentos-sociais.html">Movimentos sociais</a>
    <a href="educacao-popular.html">Educação popular</a>
    <a href="teoria-critica.html">Teoria crítica</a>
  </nav>
<div class="miolo">
  <ul class="lista-acervo lista-autores" data-revelar-grupo data-paginada>
%s
  </ul>
</div>
""" % (len(autores), len(registros), "\n".join(linhas))

    with io.open(os.path.join(RAIZ, "autores.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(shell("Autores", "Quem assina os textos do acervo AJP.", corpo_indice))

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
        corpo = """
<nav class="migalha" aria-label="Você está em"><a href="index.html">Início</a> <span aria-hidden="true">/</span> <a href="autores.html">Autores</a> <span aria-hidden="true">/</span> <span aria-current="page">%s</span></nav>
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
""" % (esc(nome), esc(nome), len(itens), "texto" if len(itens) == 1 else "textos",
       anos[0] if anos else "", anos[-1] if anos else "", cartoes)
        corpo += secao_rastreados(nome)
        pagina = shell(nome, "Textos de %s no acervo AJP." % nome, corpo)
        with io.open(os.path.join(RAIZ, "autor-%s.html" % slug(nome)), "w", encoding="utf-8", newline="\n") as f:
            f.write(pagina)

    print("autores:", len(autores))
    for nome, itens in sorted(autores.items(), key=lambda x: -len(x[1]))[:6]:
        print("  %-32s %3d" % (nome[:32], len(itens)))

    gera_paginas_bibliografia(autores)


# Autores da bibliografia cujo nome no acervo é outro.
ALIAS_BIB = {
    "vladimir de carvalho luz": "vladimir luz",
}


def gera_paginas_bibliografia(autores):
    """Cria página para autor que existe só na bibliografia (sem posts).

    A Biblioteca linka para `autor-<slug>.html`; sem esta etapa esses links
    ficam quebrados.
    """
    caminho = os.path.join(RAIZ, "dados", "bibliografia-autores.json")
    if not os.path.exists(caminho):
        return
    bib = json.load(io.open(caminho, encoding="utf-8"))
    existentes = {norm(n) for n in autores}
    criadas = 0
    for autor in bib:
        nome = autor.get("nome") or ""
        if not nome or norm(nome) in existentes:
            continue
        alvo_posts = ALIAS_BIB.get(norm(nome))
        if alvo_posts and norm(alvo_posts) in existentes:
            # autor com posts assinados por outro nome: página de bibliografia
            # aponta também para os textos no acervo
            pass
        elif alvo_posts:
            continue
        destino = autor.get("slug") or "autor-%s.html" % slug(nome)
        obras = autor.get("obras") or []
        itens = []
        for o in obras:
            titulo = esc(o.get("titulo"))
            if o.get("url"):
                alvo = o["url"]
                externo = ' target="_blank" rel="noopener"' if alvo.startswith("http") else ""
                titulo = '<a href="%s"%s>%s</a>' % (esc(alvo), externo, titulo)
            ano = " (%s)" % esc(o.get("ano")) if o.get("ano") else ""
            fonte = " · %s" % esc(o.get("fonte")) if o.get("fonte") else ""
            selo = {"aberto": ("texto integral", "selo selo--aberto"),
                    "consulta": ("catálogo", "selo"),
                    "doi": ("DOI", "selo"),
                    "restrito": ("restrito", "selo selo--restrito"),
                    "acervo": ("no acervo", "selo selo--acervo"),
                    "registro": ("registro", "selo")}.get(o.get("acesso"), ("registro", "selo"))
            itens.append('<li>%s%s%s <span class="%s">%s</span></li>'
                         % (titulo, ano, fonte, selo[1], esc(selo[0])))
        acoes = ('<p class="hero__acoes"><a class="botao secundario" href="autores.html">← Todos os autores</a>\n'
                 '    <a class="botao secundario" href="biblioteca.html#autores">Biblioteca</a>')
        if alvo_posts:
            acoes += ('\n    <a class="botao" href="autor-%s.html">Ver os textos no acervo</a>'
                      % slug(alvo_posts))
        acoes += "</p>"
        corpo = """
<nav class="migalha" aria-label="Você está em"><a href="index.html">Início</a> <span aria-hidden="true">/</span> <a href="autores.html">Autores</a> <span aria-hidden="true">/</span> <span aria-current="page">%s</span></nav>
<section class="hero hero--texto">
  <div class="hero__interno">
    <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Bibliografia</p>
    <h1>%s</h1>
    <p class="lead">%s</p>
    %s
  </div>
</section>
<div class="miolo">
  <section class="secao" aria-labelledby="obras-titulo">
    <div class="secao__cabeca"><h2 id="obras-titulo">Obras de referência</h2>
    <p class="secao__nota">%d obra(s) na bibliografia do acervo</p></div>
    <p class="colecao__nota">%s</p>
    <ul class="linhas">
%s
    </ul>
  </section>
</div>
""" % (esc(nome), esc(nome), esc(autor.get("papel") or ""), acoes, len(obras),
       esc(autor.get("nota") or ""), "\n".join(itens))
        with io.open(os.path.join(RAIZ, destino), "w", encoding="utf-8", newline="\n") as f:
            f.write(shell(nome, "Obras de %s na bibliografia AJP." % nome, corpo))
        criadas += 1
    print("páginas de bibliografia:", criadas)


if __name__ == "__main__":
    main()
