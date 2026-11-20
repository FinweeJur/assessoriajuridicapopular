"""Rodapé mais curto: parceria em uma linha, ao lado das colunas."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
GEN = os.path.join(RAIZ, "etl", "monta-secoes.py")
CSS = os.path.join(RAIZ, "acervo.css")

with io.open(GEN, encoding="utf-8") as f:
    g = f.read()

# 1. Remove a coluna "Parceria" e o aviso, que viram uma linha só
import re
g = re.sub(r'    <div>\s*<h2>Parceria</h2>.*?</div>\n', "", g, count=1, flags=re.S)

# 2. Linha única de parceria + retirada, antes das logos
LINHA = """  <p class="rodape__linha">
    <b>Parceria:</b> <a href="https://ipdms.org.br/" target="_blank" rel="noopener">IPDMS</a> — GT de Assessoria Jurídica Popular ·
    <a href="https://www.renap.org.br/" target="_blank" rel="noopener">RENAP</a> ·
    <a href="https://mab.org.br/" target="_blank" rel="noopener">MAB</a> ·
    <span>Retirada de imagem: <a href="mailto:artur.colito@ufvjm.edu.br">artur.colito@ufvjm.edu.br</a></span>
  </p>
"""
if "rodape__linha" not in g:
    g = g.replace('  <div class="parcerias" aria-label="Realização e parceria">',
                  LINHA + '  <div class="parcerias" aria-label="Realização e parceria">', 1)

with io.open(GEN, "w", encoding="utf-8", newline="\n") as f:
    f.write(g)

# 3. CSS: três colunas, respiro menor e linha de parceria
EXTRA = """
/* Rodapé curto: três colunas + uma linha de parceria */
.rodape__interno { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }
.rodape__topo { padding-bottom: var(--e2) !important; }
.rodape__linha {
  max-width: var(--largura); margin: 0 auto;
  padding: var(--e2) clamp(16px, 4vw, 40px);
  font-size: .82rem; color: var(--cp-text-soft); text-align: center;
}
.rodape__linha b { color: var(--cp-text); }
.parcerias { padding: var(--e4) var(--e4) var(--e5) !important; }
@media (max-width: 760px) {
  .rodape__interno { grid-template-columns: 1fr !important; gap: var(--e4) !important; }
}
"""

with io.open(CSS, encoding="utf-8") as f:
    css = f.read()
if "Rodapé curto" not in css:
    css = css.rstrip() + "\n" + EXTRA
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

print("rodape coluna removida:", "rodape__linha" in g)
