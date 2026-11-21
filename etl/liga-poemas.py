"""Liga o índice do Caderno à página dos poemas publicados e põe o link no rodapé."""
import io
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# 1. Caderno: chamada para os poemas publicados
p = RAIZ + r"\poemas.html"
t = io.open(p, encoding="utf-8").read()

velho = ("<p class=\"aviso-lote\"><b>Índice, não reprodução.</b> A Coletânea de Poesias (CMM, 2010) tem\n"
         "    272 páginas e dezenas de autores com direitos próprios. Aqui ficam os nomes e os títulos; o texto\n"
         "    dos poemas continua no caderno original. Pedidos de retirada: artur.colito@ufvjm.edu.br.</p>")
novo = ("<p class=\"aviso-lote\"><b>Índice e antologia.</b> A Coletânea de Poesias (CMM, 2010) tem\n"
        "    272 páginas e dezenas de autores com direitos próprios. Aqui ficam os nomes e os títulos;\n"
        "    os poemas em domínio público e os publicados por autorização estão na antologia.\n"
        "    Pedidos de retirada: artur.colito@ufvjm.edu.br.</p>\n"
        "    <p><a class=\"botao\" href=\"poemas.html\">Ler os 135 poemas publicados</a></p>")
if velho in t:
    t = t.replace(velho, novo, 1)
elif "poemas.html" not in t:
    t = t.replace("</header>", "</header>\n    <p><a class=\"botao\" href=\"poemas.html\">Ler os 135 poemas publicados</a></p>", 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("caderno -> poemas:", "poemas.html" in t)

# 2. Rodapé: link na coluna Acervo
p = RAIZ + r"\etl\monta-secoes.py"
g = io.open(p, encoding="utf-8").read()
if "poemas.html" not in g:
    g = g.replace('        <li><a href="glossario.html">Glossário</a></li>',
                  '        <li><a href="poemas.html">Poemas publicados</a></li>\n'
                  '        <li><a href="glossario.html">Glossário</a></li>', 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(g)
print("rodape -> poemas:", "poemas.html" in g)

# 3. Sitemap: garante as páginas novas
p = RAIZ + r"\sitemap.xml"
s = io.open(p, encoding="utf-8").read()
base = "https://finweejur.github.io/assessoriajuridicapopular"
for slug in ["poemas", "glossario", "linha-do-tempo",
             "assessoria-juridica-popular-no-mundo", "caderno-de-poesias"]:
    url = base + "/" + slug + ".html"
    if url not in s:
        s = s.replace("</urlset>", "  <url><loc>%s</loc></url>\n</urlset>" % url)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("sitemap urls:", s.count("<url>"))
