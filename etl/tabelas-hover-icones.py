"""Tabelas legíveis, hover de cartão e ícones Lucide nos botões de compartilhar."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
CSS = os.path.join(RAIZ, "acervo.css")

EXTRA = """
/* ── Tabelas: colunas com respiro e leitura por linha ───────────────────── */
.tabela {
  padding: 0 !important; overflow-x: auto;
  border-radius: var(--raio); border: 1px solid var(--borda);
}
.tabela table {
  width: 100%; border-collapse: collapse; min-width: 34rem;
  font-size: .92rem;
}
.tabela caption {
  text-align: left; padding: 12px 16px;
  font-size: .78rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--cp-text-soft);
}
.tabela th, .tabela td {
  padding: 11px 16px; text-align: left; vertical-align: top;
  line-height: 1.45;
}
.tabela thead th {
  font-size: .76rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--cp-text-soft); border-bottom: 1px solid var(--borda);
  white-space: nowrap;
}
.tabela tbody tr + tr td { border-top: 1px solid color-mix(in srgb, var(--cp-border) 55%, transparent); }
.tabela tbody tr:hover td { background: color-mix(in srgb, var(--cp-primary) 7%, transparent); }
.tabela td:first-child { font-weight: 600; color: var(--cp-text); }
.tabela td:nth-child(2) { color: var(--cp-text); }

/* ── Cartão que levanta, sem sublinhado ─────────────────────────────────── */
a.cartao, .item__link, .destaque {
  text-decoration: none !important;
  transition: transform .18s var(--curva), border-color .18s var(--curva),
              box-shadow .18s var(--curva), background-color .18s var(--curva);
}
a.cartao:hover, a.cartao:focus-visible,
.item__link:hover, .item__link:focus-visible,
.destaque:hover, .destaque:focus-visible {
  transform: translateY(-3px);
  border-color: var(--cp-primary) !important;
  box-shadow: 0 16px 34px rgba(0, 0, 0, .3);
  text-decoration: none !important;
}
@media (prefers-reduced-motion: reduce) {
  a.cartao:hover, .item__link:hover, .destaque:hover { transform: none; }
}

/* ── Ícones Lucide: traço de 2 px, tamanho do texto ─────────────────────── */
.ico {
  width: 1.05em; height: 1.05em; flex: 0 0 auto;
  stroke: currentColor; fill: none; stroke-width: 2;
  stroke-linecap: round; stroke-linejoin: round;
  vertical-align: -.15em;
}
.busca__campo input,
.fita input[type="search"] {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%238a8a8a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.3-4.3'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: 14px 50%; background-size: 18px;
  padding-left: 42px;
}
"""

with io.open(CSS, encoding="utf-8") as f:
    css = f.read()
if "Tabelas: colunas com respiro" not in css:
    css = css.rstrip() + "\n" + EXTRA
    with io.open(CSS, "w", encoding="utf-8", newline="\n") as f:
        f.write(css)

# Ícones Lucide nos botões de compartilhar (modelo e páginas extras)
LUCIDE = {
    "whatsapp": '<svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 21l2.2-5.3A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8.5 10.5c.5 2 2 3.5 4 4l1.5-1.5 2 1"/></svg> ',
    "telegram": '<svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="m22 3-9.5 18-2-7.5L3 11l19-8Z"/><path d="m10.5 13.5 3-3"/></svg> ',
    "instagram": '<svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8"/></svg> ',
    "copiar-texto": '<svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg> ',
    "copiar-citacao": '<svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16M4 12h10M4 17h7"/><path d="m17 15 3 2-3 2"/></svg> ',
}

for relativo in ["_modelo.html",
                 r"etl\paginas-extras.py",
                 r"etl\paginas-caderno-comparado.py",
                 r"etl\monta-mistica.py",
                 r"etl\corrige-e-antologia.py"]:
    caminho = os.path.join(RAIZ, relativo)
    if not os.path.exists(caminho):
        continue
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    for acao, svg in LUCIDE.items():
        t = t.replace('data-acao="%s">' % acao, 'data-acao="%s">%s' % (acao, svg))
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)

print("css:", "Tabelas: colunas com respiro" in css)
