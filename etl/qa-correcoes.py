"""Correções do QA: logos nos temas escuros, lista com respiro, alvos e menu único."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# ── 1. CSS ────────────────────────────────────────────────────────────────
CSS = os.path.join(RAIZ, "acervo.css")
with io.open(CSS, encoding="utf-8") as f:
    css = f.read()

EXTRA = """
/* Logos visíveis em qualquer tema: marca escura vira branca no fundo escuro */
[data-theme="dark"] .parcerias__lista img[alt="RENAP"],
[data-theme="dark"] .parcerias__lista img[alt="IPDMS"],
[data-theme="pequi"] .parcerias__lista img[alt="RENAP"],
[data-theme="pequi"] .parcerias__lista img[alt="IPDMS"],
[data-theme="cerrado"] .parcerias__lista img[alt="RENAP"],
[data-theme="cerrado"] .parcerias__lista img[alt="IPDMS"],
[data-theme="mata-atlantica"] .parcerias__lista img[alt="RENAP"],
[data-theme="mata-atlantica"] .parcerias__lista img[alt="IPDMS"],
[data-theme="caatinga"] .parcerias__lista img[alt="RENAP"],
[data-theme="caatinga"] .parcerias__lista img[alt="IPDMS"],
[data-theme="pantanal"] .parcerias__lista img[alt="RENAP"],
[data-theme="pantanal"] .parcerias__lista img[alt="IPDMS"],
[data-theme="brasil"] .parcerias__lista img[alt="RENAP"],
[data-theme="brasil"] .parcerias__lista img[alt="IPDMS"] {
  filter: brightness(0) invert(1); opacity: .92;
}

/* Lista da capa com respiro, como as seções */
#lista-acervo {
  max-width: var(--largura); margin-left: auto; margin-right: auto;
  padding-left: clamp(16px, 4vw, 40px); padding-right: clamp(16px, 4vw, 40px);
}

/* Alvos de toque */
.chip, .chip-f { min-height: 44px; display: inline-flex; align-items: center; }
#tema { min-height: 44px; }
.etiqueta { font-size: .75rem; }

/* Menu: só o estado manda (sem focus-within prendendo aberto) */
.menu:focus-within .menu__lista { display: none; }
.menu[data-aberto="true"] .menu__lista { display: grid; gap: 2px; }
"""

if "Logos visíveis em qualquer tema" not in css:
    css = css.rstrip() + "\n" + EXTRA
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

# ── 2. site.js: sai o menu duplicado ──────────────────────────────────────
JS = os.path.join(RAIZ, "site.js")
with io.open(JS, encoding="utf-8") as f:
    js = f.read()

js = re.sub(r"\n  // Menu de seções: abre no hover e demora 350 ms para fechar\..*?\n  \}\n", "\n", js, flags=re.S)
with io.open(JS, "w", encoding="utf-8", newline="\n") as f:
    f.write(js)

# ── 3. leitura.js: Esc fecha de verdade e tira o foco ─────────────────────
LE = os.path.join(RAIZ, "leitura.js")
with io.open(LE, encoding="utf-8") as f:
    le = f.read()

le = le.replace("""    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { clearTimeout(relogio); menu.dataset.aberto = 'false'; }
    });""",
"""    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') {
        clearTimeout(relogio);
        menu.dataset.aberto = 'false';
        botao.setAttribute('aria-expanded', 'false');
        if (botao === document.activeElement) { botao.blur(); }
      }
    });""")

# botão de clique também fecha mesmo com foco
le = le.replace("""    menu.addEventListener('focusin', abre);
    menu.addEventListener('focusout', agenda);""",
"""    menu.addEventListener('focusin', abre);
    botao.addEventListener('click', function (ev) {
      ev.preventDefault();
      if (menu.dataset.aberto === 'true') {
        clearTimeout(relogio);
        menu.dataset.aberto = 'false';
        botao.setAttribute('aria-expanded', 'false');
      } else {
        abre();
      }
    });""")

with io.open(LE, "w", encoding="utf-8", newline="\n") as f:
    f.write(le)

# ── 4. versão nova do CSS ─────────────────────────────────────────────────
n = 0
for nome in os.listdir(RAIZ):
    if nome.endswith(".html"):
        caminho = os.path.join(RAIZ, nome)
        with io.open(caminho, encoding="utf-8") as f:
            t = f.read()
        novo = re.sub(r"acervo\.css\?v=\d+", "acervo.css?v=29", t)
        novo = re.sub(r"reveal\.css\?v=\d+", "reveal.css?v=29", novo)
        if novo != t:
            with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
                f.write(novo)
            n += 1

print("css:", "Logos visíveis em qualquer tema" in css, "| menu unico:", "focusin', abre" in le, "| v19:", n)
