"""Marca a subnavegação dentro dos hubs (Acervo, Cultura, Formação).

Idempotente: roda depois dos geradores para que um rebuild não perca as
subpáginas que saíram da barra superior.
"""
import io
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUBS = {
    "acervo.html": ("Acervo", [
        ("acervo.html", "Todos os textos", True),
        ("blog.html", "Por ano", False),
        ("autores.html", "Autores", False),
    ]),
    "blog.html": ("Acervo", [
        ("acervo.html", "Todos os textos", False),
        ("blog.html", "Por ano", True),
        ("autores.html", "Autores", False),
    ]),
    "autores.html": ("Acervo", [
        ("acervo.html", "Todos os textos", False),
        ("blog.html", "Por ano", False),
        ("autores.html", "Autores", True),
    ]),
    "cultura.html": ("Cultura", [
        ("cultura.html#poesia", "Poesia", False),
        ("poemas.html", "Poemas e Caderno", False),
        ("mistica.html", "Mística", False),
        ("cultura.html#documentario", "Documentários", False),
        ("cultura.html#cinema-teatro-musica", "Cinema, teatro e música", False),
        ("cultura.html#cronicas", "Crônicas", False),
    ]),
    "poemas.html": ("Cultura", [
        ("cultura.html", "← Cultura", False),
        ("poemas.html", "Poemas e Caderno", True),
        ("mistica.html", "Mística", False),
    ]),
    "mistica.html": ("Cultura", [
        ("cultura.html", "← Cultura", False),
        ("poemas.html", "Poemas e Caderno", False),
        ("mistica.html", "Mística", True),
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


def main():
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
    print("subnavs:", feitos)


if __name__ == "__main__":
    main()
