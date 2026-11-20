"""Reproduz imagens sem crédito, com aviso de retirada no rodapé."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# 1. Renderizador de imagem: reproduz e avisa
caminho = os.path.join(RAIZ, "etl", "monta-paginas.py")
with io.open(caminho, encoding="utf-8") as f:
    t = f.read()

velho = """        if b.get("licenca") == "link" or not b.get("credito"):
            rotulo = esc(legenda) if legenda else "Ver a imagem no original"
            return ('<figure class="cartao imagem-link"><a href="%s" target="_blank" rel="noopener">'
                    '%s<span class="sr-only"> (abre em outra aba)</span></a>'
                    '<figcaption>Imagem do original, sem licença declarada.</figcaption></figure>'
                    % (esc(src), rotulo))"""

novo = """        if b.get("licenca") == "link" or not b.get("credito"):
            # Reprodução com aviso: sem crédito declarado, o titular pede retirada.
            return ('<figure class="reproducao"><img src="%s" alt="%s" loading="lazy" />'
                    '<figcaption>%s<span class="reproducao__aviso">Imagem sem crédito declarado no original. '
                    'Se você é titular e quer a retirada, escreva para '
                    '<a href="mailto:artur.colito@ufvjm.edu.br">artur.colito@ufvjm.edu.br</a>.</span>'
                    '</figcaption></figure>'
                    % (esc(src), esc(b.get("alt") or legenda or "Imagem do texto"),
                       (esc(legenda) + " — ") if legenda else ""))"""

if velho in t:
    t = t.replace(velho, novo, 1)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    print("renderizador: ok")
else:
    print("renderizador: nao achou o bloco")

# 2. Rodapé: aviso de retirada
gen = os.path.join(RAIZ, "etl", "monta-secoes.py")
with io.open(gen, encoding="utf-8") as f:
    g = f.read()

if "ufvjm.edu.br" not in g:
    g = g.replace("""      <p>Publicação e curadoria com o""",
                  """      <p>Imagens sem crédito declarado: pedidos de retirada para
      <a href="mailto:artur.colito@ufvjm.edu.br">artur.colito@ufvjm.edu.br</a>.</p>
      <p>Publicação e curadoria com o""", 1)
    with io.open(gen, "w", encoding="utf-8", newline="\n") as f:
        f.write(g)
    print("rodape: ok")
else:
    print("rodape: ja tinha")

# 3. CSS do aviso
css_path = os.path.join(RAIZ, "acervo.css")
with io.open(css_path, encoding="utf-8") as f:
    css = f.read()

if "reproducao__aviso" not in css:
    css = css.rstrip() + """

/* Imagem reproduzida sem crédito declarado */
.reproducao img { width: 100%; height: auto; border-radius: 10px; border: 1px solid var(--borda); }
.reproducao figcaption { margin-top: 8px; font-size: .84rem; color: var(--cp-text-soft); }
.reproducao__aviso { display: block; margin-top: 4px; font-size: .76rem; }
"""
    with io.open(css_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)
    print("css: ok")
