"""Relatório do que falta nas referências: sem URL, restrito ou morto.

Saída: `docs/referencias-sem-link.csv` e `docs/referencias-links-status.md`.
Não acessa a rede.
"""
import csv
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
LINKS = os.path.join(RAIZ, "dados", "referencias-links.json")
DOCS = os.path.join(RAIZ, "docs")

dados = json.load(io.open(REF, encoding="utf-8"))
refs = dados.get("referencias", []) if isinstance(dados, dict) else dados
links = json.load(io.open(LINKS, encoding="utf-8"))

status = {}
for r in refs:
    u = (r.get("url") or "").strip()
    if not u:
        s = "sem_url"
    else:
        s = (links.get(u) or {}).get("acesso") or "nao_verificado"
    status.setdefault(s, []).append(r)

todos = status.get("sem_url", []) + status.get("restrito", []) + status.get("morto_ou_instavel", []) + status.get("nao_verificado", [])
with io.open(os.path.join(DOCS, "referencias-sem-link.csv"), "w", encoding="utf-8", newline="\n") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["motivo", "id", "tipo", "autor", "titulo", "ano", "veiculo", "fonte_slug", "confianca"])
    for s in ("sem_url", "restrito", "morto_ou_instavel", "nao_verificado"):
        for r in status.get(s, []):
            w.writerow([s, r.get("id", ""), r.get("tipo", ""), r.get("autor", ""), r.get("titulo", ""),
                        r.get("ano", ""), r.get("veiculo", ""), r.get("fonte_slug", ""), r.get("confianca", "")])

linhas = [
    "# O que falta nas referências",
    "",
    "> Base: 606 referências; 177 com URL; 102 links abertos, 4 restritos, 74 mortos/instáveis e 426 sem URL.",
    "> O CSV `referencias-sem-link.csv` traz todas as pendências para a próxima rodada.",
    "",
    "## Restritos (4)",
]
for r in status.get("restrito", []):
    linhas.append("- **%s** — %s (%s) — %s" % (r.get("titulo"), r.get("autor") or "autoria não identificada", r.get("ano") or "s.d.", r.get("url")))
linhas.append("")
linhas.append("## Mortos ou instáveis (74)")
for r in status.get("morto_ou_instavel", [])[:30]:
    linhas.append("- **%s** — %s (%s) — %s" % (r.get("titulo"), r.get("autor") or "autoria não identificada", r.get("ano") or "s.d.", r.get("url")))
if len(status.get("morto_ou_instavel", [])) > 30:
    linhas.append("- … mais %d no CSV." % (len(status.get("morto_ou_instavel", [])) - 30))
linhas.append("")
linhas.append("## Sem URL (426)")
for r in status.get("sem_url", [])[:30]:
    linhas.append("- **%s** — %s (%s) — confiança %s" % (r.get("titulo"), r.get("autor") or "autoria não identificada", r.get("ano") or "s.d.", r.get("confianca") or "baixa"))
if len(status.get("sem_url", [])) > 30:
    linhas.append("- … mais %d no CSV." % (len(status.get("sem_url", [])) - 30))
linhas.append("")
linhas.append("## Como resolver")
linhas.append("1. Priorizar as 221 de confiança alta; buscar Open Library/Crossref/BDTD/SciELO/Planalto.")
linhas.append("2. Substituir link morto por repositório, DOI ou cópia em domínio público/empréstimo.")
linhas.append("3. Não usar login, paywall, CAPTCHA ou raspagem de Instagram/Facebook.")
linhas.append("4. Registrar `fonte`, `tipo_acesso` e `verificado_em` em cada nova descoberta.")

io.open(os.path.join(DOCS, "referencias-links-status.md"), "w", encoding="utf-8", newline="\n").write("\n".join(linhas) + "\n")
print({k: len(v) for k, v in status.items()})
