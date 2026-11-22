"""Coloca as fotos dos colunistas na página de Autores e nas páginas de autor."""
import html
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTORES = os.path.join(RAIZ, "autores.html")
DADOS = os.path.join(RAIZ, "dados", "colunistas.json")


def esc(t):
    return html.escape(t or "", quote=False)


def main():
    colunistas = json.load(io.open(DADOS, encoding="utf-8"))

    cards = []
    for c in colunistas:
        slug = c.get("slug") or ""
        if slug:
            href, extra = slug, ""
            acao = "Ver os textos"
        else:
            href, extra = c["blog"], ' target="_blank" rel="noopener"'
            acao = "No blog"
        cards.append(
            '<li><a class="cartao colunista" href="%s"%s>'
            '<img src="%s" alt="Foto de %s" loading="lazy" width="96" height="96" />'
            "<h3>%s</h3><p>%s</p><span class=\"colunista__acao\">%s</span></a></li>"
            % (esc(href), extra, esc(c["foto"]), esc(c["nome"]), esc(c["nome"]),
               esc(c["bio"]), esc(acao))
        )

    bloco = """<section class="secao colunistas" id="colunistas" aria-labelledby="colunistas-titulo">
      <div class="secao__cabeca"><h2 id="colunistas-titulo">Colunistas</h2>
      <p class="secao__nota">Quem assinava as colunas fixas do blog original</p></div>
      <ul class="lista-colunistas">%s</ul>
      <p class="colecao__nota">Fotos e apresentações da página
      <a href="https://assessoriajuridicapopular.blogspot.com/p/colunistas.html" target="_blank" rel="noopener">Colunas</a>
      do blog original.</p>
    </section>""" % "\n".join(cards)

    t = io.open(AUTORES, encoding="utf-8").read()
    if 'id="colunistas"' not in t:
        i = t.find('<div class="miolo">')
        if i < 0:
            raise SystemExit("miolo de autores nao encontrado")
        t = t[:i] + bloco + "\n" + t[i:]
        io.open(AUTORES, "w", encoding="utf-8", newline="\n").write(t)
        print("colunistas na pagina de autores")
    else:
        print("colunistas ja inseridos")

    # foto no topo de cada pagina de autor
    for c in colunistas:
        slug = c.get("slug") or ""
        if not slug:
            continue
        caminho = os.path.join(RAIZ, slug)
        if not os.path.exists(caminho):
            continue
        t = io.open(caminho, encoding="utf-8").read()
        if "autor-hero__foto" in t:
            continue
        img = ('<img class="autor-hero__foto" src="%s" alt="Foto de %s" width="96" height="96" />'
               % (esc(c["foto"]), esc(c["nome"])))
        i = t.find("<h1>")
        if i < 0:
            continue
        t = t[:i] + img + "\n      " + t[i:]
        io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)
        print("foto:", slug)


if __name__ == "__main__":
    main()
