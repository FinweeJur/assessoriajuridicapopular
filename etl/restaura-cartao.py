"""Restaura a função cartao() apagada junto com o rodapé."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
GEN = os.path.join(RAIZ, "etl", "monta-secoes.py")

with io.open(GEN, encoding="utf-8") as f:
    g = f.read()

if "def cartao(" not in g:
    funcao = '''def cartao(registro):
    return """      <li class="item" data-temas="%s" data-data="%s" data-titulo="%s" data-tipo="%s" data-ano="%s" data-palavras="%s">
        <a class="item__link" href="%s.html">
          <span class="etiqueta">%s · %s</span>
          <h3>%s</h3>
          <p>%s</p>
          <span class="item__tags">%s</span>
          <span class="item__ficha">%s · %s</span>
        </a>
      </li>""" % (
        esc(" ".join((registro.get("temas") or [""])[0].split("-"))),
        esc(registro.get("data")), esc(registro.get("titulo")),
        esc(registro.get("tipo") or "formativo"), esc(registro.get("ano")),
        esc(" ".join(registro.get("palavras") or [])),
        esc(registro["slug"]), esc(registro.get("tema")), esc(registro.get("ano")),
        esc(registro.get("titulo")), esc((registro.get("resumo") or "")[:200]),
        esc(" · ".join((registro.get("palavras") or [])[:3])),
        esc(registro.get("autor")), esc(data_curta(registro.get("data"))))


'''
    g = g.replace("def pagina(", funcao + "def pagina(", 1)
    with io.open(GEN, "w", encoding="utf-8", newline="\n") as f:
        f.write(g)
    print("cartao: restaurado")
else:
    print("cartao: já existia")
