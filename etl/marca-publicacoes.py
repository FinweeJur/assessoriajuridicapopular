"""Insere as produções do IPDMS e os Cadernos da RENAP na Biblioteca."""
import html
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = os.path.join(RAIZ, "biblioteca.html")


def esc(t):
    return html.escape(t or "", quote=False)


def cartao(item):
    etiqueta = " · ".join(x for x in (item.get("serie"), item.get("ano")) if x and x != "—")
    acoes = "".join(
        '<a class="botao secundario" href="%s" target="_blank" rel="noopener">%s</a>'
        % (esc(l["url"]), esc(l["rotulo"])) for l in item.get("links", [])
    ) or '<a class="botao" href="%s" target="_blank" rel="noopener">Abrir</a>' % esc(item.get("url", ""))
    return ('<li class="cartao publicacao"><span class="etiqueta">%s</span>'
            "<h3>%s</h3><p>%s</p><p class=\"publicacao__acoes\">%s</p></li>"
            % (esc(etiqueta), esc(item["titulo"]), esc(item.get("descricao")), acoes))


def secao(ident, titulo, nota, itens):
    return """<section class="secao" id="%s" aria-labelledby="%s-titulo">
      <div class="secao__cabeca"><h2 id="%s-titulo">%s</h2>
      <p class="secao__nota">%s</p></div>
      <ul class="lista-publicacoes">%s</ul>
    </section>""" % (ident, ident, ident, esc(titulo), esc(nota),
                     "".join(cartao(i) for i in itens))


def main():
    ipdms = json.load(io.open(os.path.join(RAIZ, "dados", "ipdms.json"), encoding="utf-8"))
    renap = json.load(io.open(os.path.join(RAIZ, "dados", "renap-cadernos.json"), encoding="utf-8"))

    bloco = secao("ipdms", "Produções do IPDMS",
                  "Cadernos Insurgentes, revista InSURgência, anais e publicações",
                  ipdms)
    bloco += "\n" + secao("renap", "Cadernos da RENAP",
                          "Seis cadernos e dois volumes sobre Defensoria e AJP, publicados pela rede",
                          renap)

    t = io.open(PAGINA, encoding="utf-8").read()
    if 'id="ipdms"' in t and 'id="renap"' in t:
        print("publicacoes: ja inseridas")
        return

    for ident in ("ipdms", "renap"):
        i = t.find('<section class="secao" id="%s"' % ident)
        if i >= 0:
            j = t.find("</section>", i) + len("</section>")
            t = t[:i] + t[j:]

    i = t.rfind("</main>")
    j = t.rfind("</div>", 0, i)
    t = t[:j] + "\n" + bloco + "\n" + t[j:]
    io.open(PAGINA, "w", encoding="utf-8", newline="\n").write(t)
    print("publicacoes:", len(ipdms), "IPDMS +", len(renap), "RENAP")


if __name__ == "__main__":
    main()
