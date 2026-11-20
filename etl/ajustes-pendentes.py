"""Mística na capa, Redação da Página e cartões de autor menores."""
import io
import json
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# ── 1. Mística na capa ─────────────────────────────────────────────────────
capa = os.path.join(RAIZ, "index.html")
with io.open(capa, encoding="utf-8") as f:
    t = f.read()

if "data-mistica" not in t:
    bloco = '''  <section class="mistica-dia" aria-labelledby="mistica-titulo" hidden data-mistica>
    <div class="miolo">
      <div class="mistica-cartao">
        <p class="olho" id="mistica-titulo"><span class="olho__ponto" aria-hidden="true"></span>Mística do dia</p>
      </div>
    </div>
  </section>

'''
    t = t.replace('  <section class="destaques"', bloco + '  <section class="destaques"', 1)
if "mistica-dia.js" not in t:
    t = t.replace('<script src="casca.js?v=6" defer></script>',
                  '<script src="mistica-dia.js?v=2" defer></script>\n<script src="casca.js?v=6" defer></script>', 1)
with io.open(capa, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)
print("capa mística:", "data-mistica" in t)

# ── 2. Redação da Página ───────────────────────────────────────────────────
GENÉRICOS = {"anônimo", "anonimo", "unknown", "anonymous", "adminblogueajpopular",
             "adminblogueajpopular ", "redação", "redacao", ""}


def limpa(nome):
    return "Redação da Página" if (nome or "").strip().lower() in GENÉRICOS else nome.strip()


indice = os.path.join(RAIZ, "_indice.json")
with io.open(indice, encoding="utf-8") as f:
    registros = json.load(f)
for r in registros:
    r["autor"] = limpa(r.get("autor"))
with io.open(indice, "w", encoding="utf-8", newline="\n") as f:
    json.dump(registros, f, ensure_ascii=False, indent=1)
print("redação:", sum(1 for r in registros if r["autor"] == "Redação da Página"))

# No gerador de páginas, a assinatura também passa pelo filtro
mp = os.path.join(RAIZ, "etl", "monta-paginas.py")
with io.open(mp, encoding="utf-8") as f:
    g = f.read()

if "def autor_limpo" not in g:
    g = g.replace("def slug_autor(nome):", '''GENÉRICOS = {"anônimo", "anonimo", "unknown", "anonymous", "adminblogueajpopular",
             "redação", "redacao", ""}


def autor_limpo(nome):
    return "Redação da Página" if (nome or "").strip().lower() in GENÉRICOS else (nome or "").strip()


def slug_autor(nome):''', 1)
    g = g.replace('    autor = (post.get("autor") or {}).get("nome") or "Redação do blog"',
                  '    autor = autor_limpo((post.get("autor") or {}).get("nome")) or "Redação da Página"', 1)
    g = g.replace('        "AUTOR": esc(autor.get("nome") or "Redação do blog"),',
                  '        "AUTOR": esc(autor_limpo(autor.get("nome")) or "Redação da Página"),', 1)
    with io.open(mp, "w", encoding="utf-8", newline="\n") as f:
        f.write(g)
print("monta-paginas:", "autor_limpo" in g)

# ── 3. Cartões de autor menores ────────────────────────────────────────────
ma = os.path.join(RAIZ, "etl", "monta-autores.py")
with io.open(ma, encoding="utf-8") as f:
    a = f.read()

if 'lista-autores' not in a:
    a = a.replace('<ul class="lista-acervo" data-revelar-grupo data-paginada>',
                  '<ul class="lista-acervo lista-autores" data-revelar-grupo data-paginada>')
    with io.open(ma, "w", encoding="utf-8", newline="\n") as f:
        f.write(a)
print("autores menor:", "lista-autores" in a)
