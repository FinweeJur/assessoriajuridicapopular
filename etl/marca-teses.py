"""Insere as teses e dissertações do Catálogo CAPES na página da Biblioteca.

Idempotente: procura o marcador id="teses-capes" antes de inserir.
"""
import html
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados", "teses-capes.json")
PAGINA = os.path.join(RAIZ, "biblioteca.html")


def esc(t):
    return html.escape(t or "", quote=False)


def main():
    teses = json.load(io.open(DADOS, encoding="utf-8"))
    teses.sort(key=lambda x: (x.get("ano", ""), x.get("autoria", "")))

    itens = []
    for t in teses:
        etiqueta = " · ".join(x for x in (t.get("grau"), t.get("ano"), t.get("instituicao")) if x)
        temas = "".join("<span>%s</span>" % esc(x) for x in t.get("temas", []))
        capes = ""
        if t.get("capes"):
            capes = (' <a class="botao secundario" href="%s" target="_blank" rel="noopener">'
                     "Catálogo CAPES</a>" % esc(t["capes"]))
        itens.append(
            '<li class="cartao tese">'
            '<span class="etiqueta">%s</span>'
            "<h3>%s</h3>"
            '<p class="tese__autoria">%s · %s</p>'
            '<p class="tese__temas">%s</p>'
            '<p class="tese__acoes"><a class="botao" href="%s" target="_blank" rel="noopener">'
            "Abrir no repositório</a>%s</p></li>"
            % (esc(etiqueta), esc(t["titulo"]), esc(t.get("autoria")), esc(t.get("programa")),
               temas, esc(t["url"]), capes)
        )

    bloco = """<section class="secao" id="teses-capes" aria-labelledby="teses-titulo">
      <div class="secao__cabeca"><h2 id="teses-titulo">Teses e dissertações</h2>
      <p class="secao__nota">%d trabalhos defendidos no Brasil, com link para o repositório de cada instituição</p></div>
      <p class="colecao__nota">Levantamento feito no
      <a href="https://catalogodeteses.capes.gov.br/catalogo-teses/" target="_blank" rel="noopener">Catálogo de Teses e Dissertações da CAPES</a>
      em 22/11/2026, a partir das palavras-chave do acervo. O botão principal abre o trabalho no
      repositório da própria instituição; quando existe registro na CAPES, o segundo botão leva ao catálogo.
      Alguns repositórios pedem validação de rede institucional.</p>
      <ul class="lista-teses">%s</ul>
    </section>""" % (len(teses), "\n".join(itens))

    t = io.open(PAGINA, encoding="utf-8").read()
    inicio = t.find('<section class="secao" id="teses-capes"')
    if inicio >= 0:
        fim = t.find("</section>", inicio) + len("</section>")
        t = t[:inicio] + bloco + t[fim:]
    else:
        i = t.rfind("</main>")
        j = t.rfind("</div>", 0, i)
        t = t[:j] + "\n" + bloco + "\n" + t[j:]
    io.open(PAGINA, "w", encoding="utf-8", newline="\n").write(t)
    print("teses inseridas:", len(teses))


if __name__ == "__main__":
    main()
