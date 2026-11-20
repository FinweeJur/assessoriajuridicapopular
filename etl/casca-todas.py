"""Põe a casca (rolagem + assistente) em todas as páginas e ajusta estilos."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
CSS = os.path.join(RAIZ, "acervo.css")

EXTRA = """
/* ── Casca: rolagem e assistente ────────────────────────────────────────── */
.casca-rolagem {
  position: fixed; right: 14px; bottom: 84px; z-index: 45;
  display: grid; gap: 8px;
}
.casca-rolagem button {
  width: 44px; height: 44px; border-radius: 50%;
  display: grid; place-items: center; cursor: pointer;
  border: 1px solid var(--borda);
  background: color-mix(in srgb, var(--cp-bg) 88%, transparent);
  color: var(--cp-text);
  backdrop-filter: blur(8px);
  opacity: 0; visibility: hidden; transform: translateY(6px);
  transition: opacity .16s var(--curva), transform .16s var(--curva), border-color .16s var(--curva);
}
.casca-rolagem button[data-visivel="true"] { opacity: 1; visibility: visible; transform: none; }
.casca-rolagem button:hover { border-color: var(--cp-primary); color: var(--cp-primary); }

.assistente { position: fixed; right: 14px; bottom: 20px; z-index: 46; }
.assistente__botao {
  display: inline-flex; align-items: center; gap: 8px;
  min-height: 44px; padding: 10px 16px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--borda); background: var(--cp-primary);
  color: var(--cp-primary-ink); font: inherit; font-size: .88rem; font-weight: 700;
}
.assistente__painel {
  display: none; position: absolute; right: 0; bottom: calc(100% + 10px);
  width: min(24rem, calc(100vw - 28px)); max-height: min(70vh, 32rem);
  overflow: auto; padding: var(--e4);
  background: var(--cp-surface); border: 1px solid var(--borda); border-radius: 14px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, .4);
}
.assistente[data-aberto="true"] .assistente__painel { display: block; }
.assistente__painel h2 { font-size: 1rem; margin: 0 0 6px; }
.assistente__nota { font-size: .78rem; color: var(--cp-text-soft); margin: 0 0 10px; }
.assistente__fechar {
  position: absolute; top: 8px; right: 10px; width: 32px; height: 32px;
  border: 0; background: transparent; color: var(--cp-text-soft); font-size: 1.3rem; cursor: pointer;
}
.assistente__form { display: flex; gap: 6px; }
.assistente__form input {
  flex: 1; min-height: 44px; padding: 10px 12px; font: inherit;
  color: var(--cp-text); background: var(--cp-bg);
  border: 1px solid var(--borda); border-radius: 10px;
}
.assistente__form button {
  min-height: 44px; padding: 10px 14px; border-radius: 10px; cursor: pointer;
  border: 0; background: var(--cp-primary); color: var(--cp-primary-ink); font: inherit; font-weight: 700;
}
.assistente__status { margin: 10px 0; font-size: .8rem; color: var(--cp-text-soft); }
.assistente__lista { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.assistente__item a { display: block; font-size: .9rem; font-weight: 600; }
.assistente__item span { font-size: .74rem; color: var(--cp-text-soft); }

/* Autores: cartão 25% mais baixo e mais estreito */
.lista-autores { grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr)) !important; }
.lista-autores .item__link { min-height: 7.2rem !important; padding: 14px 16px !important; }
.lista-autores .item__link h3 { font-size: .98rem; }

/* Navbar: menu no celular e na meia janela */
.topo__abrir { display: none; }
@media (max-width: 880px) {
  .topo__abrir {
    display: inline-grid; place-items: center; width: 44px; height: 44px;
    margin-left: auto; border-radius: 10px; cursor: pointer;
    border: 1px solid var(--borda); background: transparent; color: var(--cp-text);
  }
  .topo__links {
    position: absolute; left: 0; right: 0; top: 100%;
    display: none; flex-direction: column; align-items: stretch;
    padding: 8px; gap: 2px;
    background: var(--cp-surface); border-bottom: 1px solid var(--borda);
    box-shadow: 0 18px 40px rgba(0, 0, 0, .35);
  }
  .topo[data-aberto="true"] .topo__links { display: flex; }
  .menu__lista { position: static; display: grid; box-shadow: none; border: 0; }
  .topo__interno { flex-wrap: nowrap; }
  .topo__marca span { display: none; }
}
@media (max-width: 560px) {
  .assistente { right: 10px; bottom: 14px; }
  .casca-rolagem { right: 10px; bottom: 76px; }
}
"""

with io.open(CSS, encoding="utf-8") as f:
    css = f.read()
if "Casca: rolagem e assistente" not in css:
    css = css.rstrip() + "\n" + EXTRA
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

# script em todas as páginas
alterados = 0
for nome in os.listdir(RAIZ):
    if not nome.endswith(".html"):
        continue
    caminho = os.path.join(RAIZ, nome)
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    novo = t
    if "casca.js" not in novo:
        novo = novo.replace("</body>", '<script src="casca.js?v=2" defer></script>\n</body>', 1)
    novo = novo.replace("acervo.css?v=6", "acervo.css?v=7").replace("reveal.css?v=6", "reveal.css?v=7")
    if novo != t:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(novo)
        alterados += 1

# geradores
for rel in ["etl/monta-secoes.py", "etl/monta-paginas.py", "_modelo.html",
            "etl/paginas-extras.py", "etl/paginas-caderno-comparado.py",
            "etl/monta-mistica.py", "etl/corrige-e-antologia.py"]:
    caminho = os.path.join(RAIZ, rel)
    if not os.path.exists(caminho):
        continue
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    novo = t.replace("acervo.css?v=6", "acervo.css?v=7").replace("reveal.css?v=6", "reveal.css?v=7")
    novo = novo.replace("acervo.css?v=5", "acervo.css?v=7").replace("reveal.css?v=5", "reveal.css?v=7")
    novo = novo.replace("acervo.css?v=4", "acervo.css?v=7").replace("reveal.css?v=4", "reveal.css?v=7")
    if "casca.js" not in novo and rel.endswith(".py"):
        novo = novo.replace("</body>", '<script src="casca.js?v=2" defer></script>\n</body>', 1)
    if novo != t:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(novo)

print("html:", alterados)
