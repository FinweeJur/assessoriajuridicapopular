"""Rodapé em uma linha (4 colunas) e chatbot embaixo do rádio."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
GEN = os.path.join(RAIZ, "etl", "monta-secoes.py")

# ── 1. Rodapé novo ─────────────────────────────────────────────────────────
with io.open(GEN, encoding="utf-8") as f:
    g = f.read()

novo_rodape = '''def rodape():
    return """<footer class="rodape">
  <div class="rodape__topo">
    <p class="rodape__marca"><span class="ponto" aria-hidden="true"></span> AJP · Assessoria Jurídica Popular</p>
  </div>
  <div class="rodape__interno rodape__interno--linha">
    <div>
      <h2>Acervo</h2>
      <ul>
        <li><a href="index.html">Todos os textos</a></li>
        <li><a href="blog.html">Blog, em ordem</a></li>
        <li><a href="glossario.html">Glossário</a></li>
        <li><a href="linha-do-tempo.html">Linha do tempo</a></li>
        <li><a href="o-que-e-assessoria-juridica-popular.html">O que é AJP</a></li>
      </ul>
    </div>
    <div>
      <h2>Seções</h2>
      <ul>
        <li><a href="assessoria-juridica-popular.html">Assessoria jurídica popular</a></li>
        <li><a href="direitos-humanos.html">Direitos humanos</a></li>
        <li><a href="movimentos-sociais.html">Movimentos sociais</a></li>
        <li><a href="memoria-e-cultura.html">Memória e cultura</a></li>
        <li><a href="teoria-critica.html">Teoria crítica</a></li>
        <li><a href="educacao-popular.html">Educação popular</a></li>
      </ul>
    </div>
    <div>
      <h2>Assessoria Jurídica Popular</h2>
      <p>Textos publicados originalmente no blog
      <a href="https://assessoriajuridicapopular.blogspot.com/" target="_blank" rel="noopener">Assessoria Jurídica Popular</a>,
      em citação direta, com autor, data e link.</p>
      <h2>Fonte</h2>
      <p>Acervo montado a partir do blog original, com captura em 20/11/2026.</p>
    </div>
    <div>
      <h2>Parcerias</h2>
      <ul class="parcerias__lista">
        <li><a href="https://www.renap.org.br/" target="_blank" rel="noopener"><img src="logos/renap.png" alt="RENAP" loading="lazy" /></a></li>
        <li><a href="https://ipdms.org.br/" target="_blank" rel="noopener"><img src="logos/ipdms.png" alt="IPDMS" loading="lazy" /></a></li>
        <li><a href="https://mab.org.br/" target="_blank" rel="noopener"><img src="logos/mab.png" alt="MAB" loading="lazy" /></a></li>
      </ul>
      <p><b>GT de Assessoria Jurídica Popular do IPDMS</b></p>
      <p>Desenvolvimento e retirada de imagens ou conteúdo:
      <a href="mailto:artur.colito@ufvjm.edu.br">artur.colito@ufvjm.edu.br</a></p>
    </div>
  </div>
</footer>"""


'''

inicio = g.find("def rodape():")
fim = g.find("def pagina(")
if inicio < 0 or fim < 0:
    raise SystemExit("nao achei rodape/pagina")
g = g[:inicio] + novo_rodape + g[fim:]

with io.open(GEN, "w", encoding="utf-8", newline="\n") as f:
    f.write(g)
print("rodape: 4 colunas")

# ── 2. CSS do rodapé e do chatbot abaixo do rádio ─────────────────────────
CSS = os.path.join(RAIZ, "acervo.css")
with io.open(CSS, encoding="utf-8") as f:
    css = f.read()

EXTRA = """
/* Rodapé em uma linha: quatro colunas, alinhadas no topo */
.rodape__topo { padding: var(--e5) var(--e4) var(--e2) !important; }
.rodape__interno--linha {
  grid-template-columns: 1fr 1.1fr 1.3fr 1.5fr !important;
  align-items: start; text-align: left; gap: clamp(16px, 2.4vw, 36px) !important;
  padding-top: var(--e3) !important; padding-bottom: var(--e5) !important;
}
.rodape__interno--linha h2 { text-align: left; margin-top: 0; }
.rodape__interno--linha ul { justify-items: start; gap: 4px; }
.rodape__interno--linha p { max-width: 34ch; margin: 0 0 8px; }
.rodape__interno--linha .parcerias__lista {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px;
  justify-content: flex-start; margin: 0 0 10px; padding: 0;
}
.rodape__interno--linha .parcerias__lista img { max-height: 38px; width: auto; opacity: .75; }
.rodape__interno--linha .parcerias__lista a:hover img { opacity: 1; }
@media (max-width: 1000px) {
  .rodape__interno--linha { grid-template-columns: 1fr 1fr !important; }
}
@media (max-width: 620px) {
  .rodape__interno--linha { grid-template-columns: 1fr !important; }
}

/* Chatbot embaixo do rádio, na mesma coluna da esquerda */
.radio-flut { left: 14px !important; right: auto !important; bottom: 76px !important; }
.assistente { left: 14px !important; right: auto !important; bottom: 16px !important; }
.assistente__painel {
  left: 0 !important; right: auto !important;
  bottom: calc(100% + 10px) !important;
}
@media (max-width: 560px) {
  .radio-flut { left: 10px !important; bottom: 70px !important; }
  .assistente { left: 10px !important; bottom: 12px !important; }
  .assistente__painel { width: min(22rem, calc(100vw - 20px)); }
}
"""

if "Rodapé em uma linha" not in css:
    css = css.rstrip() + "\n" + EXTRA
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)
print("css: rodape + chatbot")

# ── 3. CSS v12 ────────────────────────────────────────────────────────────
for nome in os.listdir(RAIZ):
    if not nome.endswith(".html"):
        continue
    caminho = os.path.join(RAIZ, nome)
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    novo = t.replace("acervo.css?v=27", "acervo.css?v=27").replace("acervo.css?v=27", "acervo.css?v=27")
    if novo != t:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(novo)
print("css v12")
