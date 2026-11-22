"""Reescreve a lista da capa a partir de _indice.json."""
import html
import io
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
CAPA = os.path.join(RAIZ, "acervo.html")


def esc(t):
    return html.escape(t or "", quote=False)


MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho',
         'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


def data_curta(iso):
    if not iso or len(iso) < 10:
        return ''
    ano, mes, dia = iso[:10].split('-')
    return '%d de %s de %s' % (int(dia), MESES[int(mes) - 1], ano)


def item(registro):
    temas = " ".join((registro.get("temas") or [""])[0].split("-"))
    palavras = " ".join(registro.get("palavras") or [])
    palavras_tags = (registro.get("palavras") or [])[:3]
    tags = ""
    if palavras_tags:
        tags = '<span class="item__tags">%s</span>' % "".join(
            '<span class="item__tag">%s</span>' % esc(p) for p in palavras_tags)
    redes = registro.get("redes") or []
    rotulos = {"renap": "RENAP", "ipdms": "IPDMS", "renaju-ajup": "RENAJU/AJUPs"}
    redes_tags = ""
    if redes:
        redes_tags = '<span class="item__redes">%s</span>' % "".join(
            '<span class="item__rede">%s</span>' % rotulos[r] for r in redes if r in rotulos)
    return """      <li class="item" data-temas="%s" data-data="%s" data-titulo="%s" data-tipo="%s" data-ano="%s" data-palavras="%s" data-redes="%s">
        <a class="cartao item__link" href="%s.html">
          <span class="etiqueta">%s · %s</span>
          <h3>%s</h3>
          <p>%s</p>
          %s
          %s
          <span class="item__ficha">%s · %s</span>
        </a>
      </li>""" % (
        esc(temas), esc(registro.get("data")), esc(registro.get("titulo")),
        esc(registro.get("tipo") or "formativo"), esc(registro.get("ano")), esc(palavras),
        esc(" ".join(registro.get("redes") or [])),
        esc(registro["slug"]), esc(registro.get("tema")), esc(registro.get("ano")),
        esc(registro.get("titulo")), esc((registro.get("resumo") or "")[:220]),
        tags, redes_tags, esc(registro.get("autor")), esc(data_curta(registro.get("data"))))


def main():
    with io.open(INDICE, encoding="utf-8") as f:
        registros = json.load(f)

    with io.open(CAPA, encoding="utf-8") as f:
        t = f.read()

    inicio = t.find('<ul class="lista-acervo" id="lista-acervo"')
    if inicio < 0:
        raise SystemExit("nao achei a lista na capa")
    fim = t.find("</ul>", inicio) + len("</ul>")
    lista = ('<ul class="lista-acervo" id="lista-acervo" data-revelar-grupo data-paginada>\n\n'
             + "\n\n".join(item(r) for r in registros) + "\n\n    </ul>")
    t = t[:inicio] + lista + t[fim:]

    n = len(registros)
    t = re.sub(r'<p class="busca__contagem"[^>]*>[^<]*</p>',
               '<p class="busca__contagem" id="busca-contagem" role="status" aria-live="polite">%d %s</p>'
               % (n, "texto" if n == 1 else "textos"), t, count=1)

    aviso = ("O acervo entra em lotes: %d de 713 textos publicados. "
             "O restante está sendo baixado e revisado." % n) if n < 713 else \
            ("Acervo completo: %d textos." % n)
    t = re.sub(r'<p class="aviso-lote">.*?</p>',
               '<p class="aviso-lote">%s</p>' % html.escape(aviso), t, flags=re.S, count=1)

    with io.open(CAPA, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)

    print("lista atualizada:", n, "itens")


if __name__ == "__main__":
    main()
