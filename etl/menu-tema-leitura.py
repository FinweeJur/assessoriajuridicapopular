"""Menu com fechamento lento, tema pequi padrão e controles de leitura na navbar."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

# ── 1. Tema padrão pequi em todas as páginas ──────────────────────────────
n = 0
for nome in os.listdir(RAIZ):
    if not nome.endswith(".html"):
        continue
    caminho = os.path.join(RAIZ, nome)
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    novo = t.replace('data-theme="light"', 'data-theme="pequi"')
    novo = novo.replace('<option value="light" selected>', '<option value="light">')
    novo = novo.replace('<option value="pequi">⚪', '<option value="pequi">🟠')
    if '<option value="pequi" selected>' not in novo:
        novo = novo.replace('<option value="pequi">', '<option value="pequi" selected>', 1)
    if novo != t:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(novo)
        n += 1
print("páginas com pequi:", n)

# ── 2. Geradores: também nascem em pequi ─────────────────────────────────
for rel in ["etl/monta-secoes.py", "etl/monta-paginas.py", "_modelo.html",
            "etl/paginas-extras.py", "etl/paginas-caderno-comparado.py",
            "etl/monta-mistica.py", "etl/corrige-revisao.py", "etl/glossario-linha.py"]:
    caminho = os.path.join(RAIZ, rel)
    if not os.path.exists(caminho):
        continue
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    novo = t.replace('data-theme="light"', 'data-theme="pequi"')
    if novo != t:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(novo)

# ── 3. casca.js: menu lento, tema persistente e controles de leitura ─────
js_path = os.path.join(RAIZ, "casca.js")
with io.open(js_path, encoding="utf-8") as f:
    js = f.read()

EXTRA = """
  // ── Menu: fecha devagar e ignora o vão entre botão e painel ─────────────
  (function menuLento() {
    var menu = document.querySelector('.menu');
    if (!menu) { return; }
    var botao = menu.querySelector('.menu__botao');
    var lista = menu.querySelector('.menu__lista');
    if (!botao || !lista) { return; }
    var relogio = null;

    function abre() {
      clearTimeout(relogio);
      menu.dataset.aberto = 'true';
      botao.setAttribute('aria-expanded', 'true');
    }
    function agenda() {
      clearTimeout(relogio);
      relogio = setTimeout(function () {
        // Se o ponteiro ainda estiver sobre o menu ou o painel, não fecha.
        if (menu.matches(':hover') || lista.matches(':hover')) { agenda(); return; }
        menu.dataset.aberto = 'false';
        botao.setAttribute('aria-expanded', 'false');
      }, 1200);
    }
    menu.addEventListener('pointerenter', abre);
    menu.addEventListener('pointerleave', agenda);
    lista.addEventListener('pointerenter', abre);
    lista.addEventListener('pointerleave', agenda);
    menu.addEventListener('focusin', abre);
    menu.addEventListener('focusout', agenda);
    botao.addEventListener('click', function (ev) {
      ev.preventDefault();
      if (menu.dataset.aberto === 'true') { agenda(); } else { abre(); }
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { clearTimeout(relogio); menu.dataset.aberto = 'false'; }
    });
  })();

  // ── Tema: pequi por padrão e memória entre páginas ──────────────────────
  (function temaPersistente() {
    var raiz = document.documentElement;
    var guardado = null;
    try { guardado = localStorage.getItem('renap-tema'); } catch (e) {}
    if (!raiz.dataset.theme || raiz.dataset.theme === 'light') {
      raiz.dataset.theme = guardado || 'pequi';
    }
    var seletor = document.getElementById('tema');
    if (!seletor) { return; }
    seletor.value = raiz.dataset.theme;
    seletor.addEventListener('change', function () {
      raiz.dataset.theme = seletor.value;
      try { localStorage.setItem('renap-tema', seletor.value); } catch (e) {}
    });
  })();

  // ── Leitura: A-, A, A+ e ouvir ──────────────────────────────────────────
  (function controlesLeitura() {
    var topo = document.querySelector('.topo__interno');
    if (!topo || document.querySelector('[data-leitura]')) { return; }
    var caixa = document.createElement('div');
    caixa.className = 'topo__leitura';
    caixa.setAttribute('data-leitura', '');
    caixa.innerHTML =
      '<button type="button" data-fonte-menos aria-label="Diminuir o texto" data-dica="Texto menor">A−</button>' +
      '<button type="button" data-fonte-mais aria-label="Aumentar o texto" data-dica="Texto maior">A+</button>' +
      '<button type="button" data-ouvir aria-pressed="false" data-dica="Ouvir a página">' +
      '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 10v4h4l5 4V6L7 10H3Z"/><path d="M16 9a4 4 0 0 1 0 6"/></svg> Ouvir</button>';
    topo.appendChild(caixa);

    var escala = 1;
    try { escala = parseFloat(localStorage.getItem('renap-escala') || '1'); } catch (e) {}

    function aplica() {
      document.documentElement.style.fontSize = (16 * escala) + 'px';
      try { localStorage.setItem('renap-escala', String(escala)); } catch (e) {}
    }
    aplica();

    caixa.querySelector('[data-fonte-menos]').addEventListener('click', function () {
      escala = Math.max(0.85, Math.round((escala - 0.1) * 10) / 10); aplica();
    });
    caixa.querySelector('[data-fonte-mais]').addEventListener('click', function () {
      escala = Math.min(1.4, Math.round((escala + 0.1) * 10) / 10); aplica();
    });

    var ouvir = caixa.querySelector('[data-ouvir]');
    var falando = false;
    ouvir.addEventListener('click', function () {
      if (!('speechSynthesis' in window)) { return; }
      if (falando) {
        speechSynthesis.cancel(); falando = false; ouvir.setAttribute('aria-pressed', 'false');
        return;
      }
      var texto = (document.querySelector('main') || document.body).innerText.slice(0, 4000);
      var fala = new SpeechSynthesisUtterance(texto);
      fala.lang = 'pt-BR';
      fala.onend = function () { falando = false; ouvir.setAttribute('aria-pressed', 'false'); };
      speechSynthesis.speak(fala);
      falando = true; ouvir.setAttribute('aria-pressed', 'true');
    });
  })();
'''
if "controlesLeitura" not in js:
    js = js.replace("})();", EXTRA + "})();", 1)
    with io.open(js_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(js)

# ── 4. CSS dos controles ─────────────────────────────────────────────────
css_path = os.path.join(RAIZ, "acervo.css")
with io.open(css_path, encoding="utf-8") as f:
    css = f.read()

BLOCO = """
/* Controles de leitura na navbar */
.topo__leitura { display: inline-flex; align-items: center; gap: 4px; margin-left: auto; }
.topo__leitura button {
  min-height: 40px; min-width: 40px; padding: 0 10px; cursor: pointer;
  font: inherit; font-size: .82rem; font-weight: 700;
  color: var(--cp-text); background: transparent;
  border: 1px solid var(--borda); border-radius: 8px;
}
.topo__leitura button:hover { border-color: var(--cp-primary); color: var(--cp-primary); }
.topo__leitura button[aria-pressed="true"] { background: var(--cp-primary); color: var(--cp-primary-ink); }
@media (max-width: 880px) { .topo__leitura { margin-left: 0; } .topo__leitura [data-ouvir] { display: none; } }
"""
if "Controles de leitura na navbar" not in css:
    css = css.rstrip() + "\n" + BLOCO
    with io.open(css_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

# ── 5. CSS v10 ───────────────────────────────────────────────────────────
for nome in os.listdir(RAIZ):
    if nome.endswith(".html"):
        caminho = os.path.join(RAIZ, nome)
        with io.open(caminho, encoding="utf-8") as f:
            t = f.read()
        novo = t.replace("acervo.css?v=9", "acervo.css?v=10").replace("reveal.css?v=9", "reveal.css?v=10")
        if novo != t:
            with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
                f.write(novo)

print("casca: controles e tema; css v10")
