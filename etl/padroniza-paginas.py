"""Padroniza topo, rodapé, rádio e scripts em todas as páginas.

- troca o topo e o rodapé pelos modelos atuais de etl/monta-secoes.py;
- garante leitura.css, radio.css, casca.js, leitura.js e radio.js;
- injeta o bloco do rádio onde ele ainda não existe.
"""
import importlib.util
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

# Bloco canônico do rádio, copiado da capa.
with io.open(os.path.join(RAIZ, "index.html"), encoding="utf-8") as f:
    capa = f.read()
i = capa.find('<div class="radio-flut"')
prof = 0
j = i
for m in re.finditer(r"<div\b|</div>", capa[i:]):
    if m.group(0) == "</div>":
        prof -= 1
        if prof == 0:
            j = i + m.end()
            break
    else:
        prof += 1
RADIO = capa[i:j]
print("radio canonico:", len(RADIO), "bytes")

SLUGS = [s[0] for s in ms.SECOES]


def ativo_de(nome):
    base = nome[:-5]
    if base in SLUGS:
        return base
    if base == "blog":
        return "blog"
    if base == "acervo":
        return "acervo"
    if base == "index":
        return "texto"
    return "texto"


mudados = 0
for nome in sorted(os.listdir(RAIZ)):
    if not nome.endswith(".html") or nome == "direito-critico-comparado.html":
        continue
    caminho = os.path.join(RAIZ, nome)
    with io.open(caminho, encoding="utf-8") as f:
        t = f.read()
    original = t
    ativo = ativo_de(nome)
    topo = ms.topo(ativo)
    rodape = ms.rodape()

    # 1. Topo
    if re.search(r'<header class="topo"[^>]*>.*?</header>', t, re.S):
        t = re.sub(r'<header class="topo"[^>]*>.*?</header>', topo, t, count=1, flags=re.S)
    else:
        marca = '<a class="pular" href="#conteudo">Pular para o conteúdo</a>'
        if marca in t:
            t = t.replace(marca, marca + "\n" + topo, 1)
        else:
            t = re.sub(r'(<body[^>]*>)', r'\1\n' + topo, t, count=1)

    # 2. Rodapé
    if re.search(r'<footer class="rodape"[^>]*>.*?</footer>', t, re.S):
        t = re.sub(r'<footer class="rodape"[^>]*>.*?</footer>', rodape, t, count=1, flags=re.S)
    else:
        alvo = re.search(r'<script src="[^"]+"', t)
        if alvo:
            t = t[:alvo.start()] + rodape + "\n" + t[alvo.start():]
        else:
            t = t.replace("</body>", rodape + "\n</body>", 1)

    # 3. CSS
    if "leitura.css" not in t:
        t = t.replace("</head>", '  <link rel="stylesheet" href="leitura.css?v=1" />\n</head>', 1)
    if "componentes/radio.css" not in t:
        t = t.replace("</head>", '  <link rel="stylesheet" href="componentes/radio.css" />\n</head>', 1)

    # 4. Scripts
    if "casca.js" not in t:
        t = t.replace("</body>", '<script src="casca.js?v=15" defer></script>\n</body>', 1)
    if "leitura.js" not in t:
        t = t.replace('<script src="casca.js?v=15" defer></script>',
                      '<script src="casca.js?v=15" defer></script>\n<script src="leitura.js?v=2" defer></script>', 1)
    if "componentes/radio.js" not in t:
        t = t.replace("</body>", '<script src="componentes/radio.js" defer></script>\n</body>', 1)
    if "fundo-grade.js" not in t:
        t = t.replace("</body>", '<script src="fundo-grade.js?v=3" defer></script>\n</body>', 1)

    # 5. Rádio
    if "radio-flut" not in t:
        alvo = re.search(r'<script src="', t)
        if alvo:
            t = t[:alvo.start()] + RADIO + "\n" + t[alvo.start():]
        else:
            t = t.replace("</body>", RADIO + "\n</body>", 1)

    if t != original:
        with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
        mudados += 1

print("paginas padronizadas:", mudados)
