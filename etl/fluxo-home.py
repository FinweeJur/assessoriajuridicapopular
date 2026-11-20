"""Fluxo do blog ao novo site, com meteoros ligando os três nós."""
import io

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

WP = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" />'
      '<path d="M7.2 8.2 9.3 16l2.7-7.1 2.7 7.1 2.1-7.8" /></svg>')
CODE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="3" />'
        '<path d="m7 9 3 3-3 3" /><path d="M13 15h4" /></svg>')
GIT = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />'
       '<path d="M9 18c-4.51 2-5-2-7-2" /></svg>')

FLUXO = """  <section class="fluxo" aria-labelledby="fluxo-titulo">
    <div class="miolo">
      <div class="secao__cabeca">
        <h2 id="fluxo-titulo">Do blog ao novo site</h2>
        <p class="secao__nota">O caminho deste acervo, em três paradas</p>
      </div>
      <div class="fluxo__palco" data-meteoros>
        <svg class="fluxo__svg" aria-hidden="true"></svg>
        <a class="fluxo__no fluxo__no--blog" href="https://assessoriajuridicapopular.blogspot.com/" target="_blank" rel="noopener">
          <span class="fluxo__ico fluxo__ico--wp">%s</span>
          <b>Blog original AJP</b>
          <small>Blogger</small>
        </a>
        <div class="fluxo__no fluxo__no--code">
          <span class="fluxo__ico fluxo__ico--code">%s</span>
          <b>OpenCode</b>
          <small>programa</small>
        </div>
        <a class="fluxo__no fluxo__no--git" href="https://github.com/FinweeJur/assessoriajuridicapopular" target="_blank" rel="noopener">
          <span class="fluxo__ico fluxo__ico--git">%s</span>
          <b>GitHub</b>
          <small>acervo publicado</small>
        </a>
        <span class="fluxo__novo">Novo Site
          <svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></svg>
        </span>
      </div>
    </div>
  </section>

""" % (WP, CODE, GIT)

p = RAIZ + r"\index.html"
t = io.open(p, encoding="utf-8").read()
if "class=\"fluxo\"" not in t:
    i = t.rfind("</main>")
    t = t[:i] + FLUXO + t[i:]
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("fluxo:", "class=\"fluxo\"" in t)

# CSS
p = RAIZ + r"\acervo.css"
css = io.open(p, encoding="utf-8").read()
EXTRA = """
/* ── Fluxo blog → OpenCode → GitHub ──────────────────────────────────── */
.fluxo {
  padding: clamp(40px, 6vw, 72px) 0;
  border-top: 1px solid var(--borda);
}
.fluxo__palco {
  position: relative; isolation: isolate;
  display: grid; grid-template-columns: 1fr auto 1fr auto;
  align-items: center; gap: clamp(18px, 3vw, 48px);
  min-height: 220px; margin-top: 20px;
}
.fluxo__svg {
  position: absolute; inset: 0; width: 100%; height: 100%;
  overflow: visible; pointer-events: none; z-index: 0;
}
.fluxo__linha { fill: none; stroke: color-mix(in srgb, var(--cp-primary) 30%, transparent); stroke-width: 1.4; stroke-dasharray: 4 7; }
.meteoro { fill: var(--cp-primary); filter: drop-shadow(0 0 6px var(--cp-primary)); }
.impacto { fill: none; stroke: var(--cp-primary); stroke-width: 1.2; }
.fluxo__no {
  position: relative; z-index: 1; display: flex; flex-direction: column;
  align-items: center; gap: 6px; text-align: center;
  color: var(--cp-text); text-decoration: none !important;
}
.fluxo__ico {
  width: 72px; height: 72px; display: grid; place-items: center;
  border: 1px solid var(--borda); border-radius: 18px;
  background: color-mix(in srgb, var(--cp-surface) 70%, transparent);
  box-shadow: 0 12px 28px rgba(0, 0, 0, .22);
  color: var(--cp-primary);
}
.fluxo__ico svg { width: 36px; height: 36px; fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.fluxo__no b { font-family: var(--font-display); font-size: 1rem; line-height: 1.2; }
.fluxo__no small { font-size: .72rem; color: var(--cp-text-soft); }
.fluxo__novo {
  position: relative; z-index: 1; display: inline-flex; align-items: center; gap: 6px;
  justify-self: start; padding: 8px 14px; border-radius: 999px;
  background: var(--cp-primary); color: var(--cp-primary-ink);
  font-size: .78rem; font-weight: 800; letter-spacing: .04em; white-space: nowrap;
}
.fluxo__novo .ico { width: 15px; height: 15px; }
@media (max-width: 760px) {
  .fluxo__palco { grid-template-columns: 1fr; justify-items: center; gap: 34px; min-height: 0; }
  .fluxo__novo { justify-self: center; margin-top: 4px; }
}
@media (prefers-reduced-motion: reduce) {
  .meteoro, .impacto { display: none; }
}
"""
if "Fluxo blog → OpenCode → GitHub" not in css:
    io.open(p, "w", encoding="utf-8", newline="\n").write(css.rstrip() + "\n" + EXTRA)
print("css fluxo:", "Fluxo blog" in css)
