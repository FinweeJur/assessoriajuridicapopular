"""Baixa Cabinet Grotesk e Switzer do Fontshare e troca os tokens de fonte."""
import io
import os
import re
import urllib.request

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
FONTES = os.path.join(RAIZ, "fontes")
UA = "finweejur/github artur colito"

API = ("https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@500,700,800"
       "&f[]=switzer@400,500,600,700&display=swap")

req = urllib.request.Request(API, headers={"User-Agent": UA})
css = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")

blocos = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)
baixados = []

for b in blocos:
    fam = re.search(r"font-family:\s*'([^']+)'", b)
    peso = re.search(r"font-weight:\s*(\d+)", b)
    url = re.search(r"url\('(//[^']+\.woff2)'\)", b)
    if not (fam and peso and url):
        continue
    nome = fam.group(1).lower().replace(" ", "-")
    destino = os.path.join(FONTES, "%s-%s.woff2" % (nome, peso.group(1)))
    if not os.path.exists(destino):
        pedido = urllib.request.Request("https:" + url.group(1), headers={"User-Agent": UA})
        dados = urllib.request.urlopen(pedido, timeout=60).read()
        with io.open(destino, "wb") as f:
            f.write(dados)
    baixados.append((fam.group(1), peso.group(1), os.path.basename(destino),
                     os.path.getsize(destino)))

# Bloco @font-face novo + tokens
linhas = ["", "/* Fontshare: Cabinet Grotesk (títulos) + Switzer (texto) */"]
por_familia = {}
for fam, peso, arquivo, _ in baixados:
    por_familia.setdefault(fam, []).append((peso, arquivo))

for fam, pesos in por_familia.items():
    for peso, arquivo in sorted(pesos):
        linhas.append('@font-face {')
        linhas.append('  font-family: "%s";' % fam)
        linhas.append('  src: url("%s") format("woff2");' % arquivo)
        linhas.append('  font-weight: %s;' % peso)
        linhas.append('  font-style: normal;')
        linhas.append('  font-display: swap;')
        linhas.append('}')

bloco = "\n".join(linhas) + "\n"

caminho = os.path.join(FONTES, "fontshare.css")
with io.open(caminho, encoding="utf-8") as f:
    atual = f.read()

if "Cabinet Grotesk (títulos)" in atual:
    atual = re.sub(r"\n/\* Fontshare: Cabinet Grotesk.*$", "", atual, flags=re.S)
atual = atual.rstrip() + "\n" + bloco
atual = atual.replace(
    '--font-display: "Clash Display", "General Sans", system-ui, sans-serif;',
    '--font-display: "Cabinet Grotesk", "Clash Display", system-ui, sans-serif;')
atual = atual.replace(
    '--font-body: "General Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;',
    '--font-body: "Switzer", "General Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;')

with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
    f.write(atual)

for item in baixados:
    print(item)
print("tokens:", "--font-display" in atual, 'Cabinet Grotesk' in atual)
