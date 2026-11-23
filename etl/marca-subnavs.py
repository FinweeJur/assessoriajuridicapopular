"""Marca a subnavegação dentro dos hubs (Acervo, Cultura, Formação).

Idempotente: roda depois dos geradores para que um rebuild não perca as
subpáginas que saíram da barra superior.
"""
import io
import re
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MIGALHAS = {
    "blog.html": ["Início", "Blog"],
    "assessoria-juridica-popular.html": ["Início", "Seções", "O que é assessoria jurídica popular"],
    "direitos-humanos.html": ["Início", "Seções", "Direitos humanos"],
    "movimentos-sociais.html": ["Início", "Seções", "Movimentos sociais"],
    "educacao-popular.html": ["Início", "Seções", "Educação popular"],
    "teoria-critica.html": ["Início", "Seções", "Teoria crítica do direito"],
}

SUBS = {
    "acervo.html": ("Acervo", [
        ("acervo.html", "Todos os textos", True),
        ("blog.html", "Por ano", False),
        ("autores.html", "Autores", False),
   ("memoria.html", "Memória", False),
        ("cultura.html", "Cultura", False),
     ]),
    "blog.html": ("Acervo", [
        ("acervo.html", "Todos os textos", False),
        ("blog.html", "Por ano", True),
        ("autores.html", "Autores", False),
   ("memoria.html", "Memória", False),
        ("cultura.html", "Cultura", False),
     ]),
    "autores.html": ("Acervo", [
        ("acervo.html", "Todos os textos", False),
        ("blog.html", "Por ano", False),
        ("autores.html", "Autores", True),
   ("memoria.html", "Memória", False),
        ("cultura.html", "Cultura", False),
     ]),
    "cultura.html": ("Mística", [
        ("mistica.html", "← Mística", False),
        ("cultura.html", "Cultura", True),
        ("poemas.html", "Poemas e Caderno", False),
    ]),
    "poemas.html": ("Mística", [
        ("mistica.html", "← Mística", False),
        ("cultura.html", "Cultura", False),
        ("poemas.html", "Poemas e Caderno", True),
    ]),
    "mistica.html": ("Mística", [
        ("mistica.html", "Mística", True),
        ("cultura.html", "Cultura", False),
        ("poemas.html", "Poemas e Caderno", False),
    ]),

    "biblioteca.html": ("Biblioteca", [
        ("biblioteca.html#acervo", "Acervos", True),
        ("biblioteca.html#obra", "Obras", False),
        ("formacao.html", "Formação", False),
        ("biblioteca.html#teses-capes", "Teses", False),
        ("biblioteca.html#ipdms", "IPDMS", False),
        ("biblioteca.html#renap", "RENAP", False),
        ("citacoes.html", "Citações", False),
        ("recomendacoes.html", "Recomendações", False),
        ("glossario.html", "Glossário", False),
        ("ia.html", "IA", False),
    ]),
    "formacao.html": ("Formação", [
        ("formacao.html", "Trilhas", True),
        ("citacoes.html", "Citações", False),
        ("recomendacoes.html", "Recomendações", False),
        ("glossario.html", "Glossário", False),
    ]),
    "citacoes.html": ("Formação", [
        ("formacao.html", "← Formação", False),
        ("citacoes.html", "Citações", True),
        ("recomendacoes.html", "Recomendações", False),
        ("glossario.html", "Glossário", False),
    ]),
    "recomendacoes.html": ("Formação", [
        ("formacao.html", "← Formação", False),
        ("citacoes.html", "Citações", False),
        ("recomendacoes.html", "Recomendações", True),
        ("glossario.html", "Glossário", False),
    ]),
    "glossario.html": ("Formação", [
        ("formacao.html", "← Formação", False),
        ("citacoes.html", "Citações", False),
        ("recomendacoes.html", "Recomendações", False),
        ("glossario.html", "Glossário", True),
    ]),
}


SECOES_SUB = """
  <nav class="subnav" aria-label="Seções do acervo">
    <span class="subnav__rotulo">Seções</span>
    <a href="assessoria-juridica-popular.html">AJP</a>
    <a href="direitos-humanos.html">Direitos humanos</a>
    <a href="movimentos-sociais.html">Movimentos sociais</a>
    <a href="educacao-popular.html">Educação popular</a>
    <a href="teoria-critica.html">Teoria crítica</a>
  </nav>"""


def reposiciona_acervo(t):
    """Leva as subnavs de Acervo para baixo do cartão/filtros.

    A página do Acervo tinha duas fileiras de chips acima do hero e a barra de
    busca abaixo dele: três lugares de filtro. Agora tudo fica na mesma zona,
    depois do cartão central.
    """
    padrao = re.compile(
        r'\n?\s*<nav class="subnav"[^>]*aria-label="(?:Dentro de Acervo|'
        r'Seções do acervo)".*?</nav>',
        re.S,
    )
    navs = padrao.findall(t)
    if not navs:
        return t
    t = padrao.sub("", t)
    alvo = re.search(r'<section class="fita-secao".*?</section>', t, re.S)
    if not alvo:
        alvo = re.search(r'<section class="hero[^"]*".*?</section>', t, re.S)
    if not alvo:
        return t
    bloco = "\n  " + "\n  ".join(n.strip() for n in navs)
    return t[: alvo.end()] + bloco + t[alvo.end():]


def main():
    # migalha nas páginas geradas por monta-secoes
    for nome, trilha in MIGALHAS.items():
        caminho = os.path.join(RAIZ, nome)
        if not os.path.exists(caminho):
            continue
        t = io.open(caminho, encoding="utf-8").read()
        if 'class="migalha"' in t:
            continue
        partes = []
        for i, item in enumerate(trilha):
            if i == 0:
                partes.append('<a href="index.html">%s</a>' % item)
            elif i == len(trilha) - 1:
                partes.append('<span aria-current="page">%s</span>' % item)
            else:
                partes.append('<span>%s</span>' % item)
        nav = ('<nav class="migalha" aria-label="Você está em">'
               + ' <span aria-hidden="true">/</span> '.join(partes) + "</nav>")
        marcador = t.find('<main id="conteudo">')
        if marcador < 0:
            continue
        fim = marcador + len('<main id="conteudo">')
        t = t[:fim] + "\n  " + nav + t[fim:]
        io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)

    for nome in ("acervo.html", "blog.html", "autores.html"):
        caminho = os.path.join(RAIZ, nome)
        if not os.path.exists(caminho):
            continue
        t = io.open(caminho, encoding="utf-8").read()
        if 'aria-label="Seções do acervo"' in t:
            continue
        m = re.search(r'<nav class="subnav".*?</nav>', t, re.S)
        if not m:
            continue
        t = t[: m.end()] + SECOES_SUB + t[m.end():]
        io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)

    feitos = 0
    for nome, (rotulo, itens) in SUBS.items():
        caminho = os.path.join(RAIZ, nome)
        if not os.path.exists(caminho):
            continue
        t = io.open(caminho, encoding="utf-8").read()
        if 'class="subnav"' in t:
            continue
        links = "".join(
            '<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if atual else "", texto)
            for href, texto, atual in itens
        )
        bloco = ('\n  <nav class="subnav" aria-label="Dentro de %s">'
                 '<span class="subnav__rotulo">%s</span>%s</nav>' % (rotulo, rotulo, links))
        marca = t.find('class="migalha"')
        if marca < 0:
            continue
        fim = t.find("</nav>", marca)
        if fim < 0:
            continue
        fim += len("</nav>")
        t = t[:fim] + bloco + t[fim:]
        io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)
        feitos += 1
    for nome in ("acervo.html", "blog.html", "autores.html"):
        caminho = os.path.join(RAIZ, nome)
        if not os.path.exists(caminho):
            continue
        t = io.open(caminho, encoding="utf-8").read()
        novo = reposiciona_acervo(t)
        if novo != t:
            io.open(caminho, "w", encoding="utf-8", newline="\n").write(novo)
            print("subnav reposicionada:", nome)
    print("subnavs:", feitos)


if __name__ == "__main__":
    main()
