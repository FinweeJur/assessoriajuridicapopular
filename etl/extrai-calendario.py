"""Extrai o calendário da mística do Controle Popular para JSON, e monta o
bloco 'Mística do dia' na home do acervo."""
import html
import io
import json
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
ORIGEM = r"X:\DevCoder\controle-popular\apps\web\lib\memoria\calendario.ts"
DESTINO = os.path.join(RAIZ, "dados")

t = io.open(ORIGEM, encoding="utf-8").read()
blocos = re.split(r"\n\s*\{\s*\n\s*diaMes:", t)[1:]
print("blocos:", len(blocos))


def campo(bloco, nome):
    m = re.search(nome + r':\s*"((?:[^"\\]|\\.)*)"', bloco, re.S)
    if not m:
        return ""
    return m.group(1).replace('\\"', '"').replace("\\n", " ").strip()


entradas = []
for bloco in blocos:
    dia = campo(bloco, "diaMes")
    if not re.match(r"^\d{2}-\d{2}$", dia):
        continue
    entradas.append({
        "diaMes": dia,
        "ano": campo(bloco, "ano"),
        "titulo": campo(bloco, "titulo"),
        "resumo": campo(bloco, "resumo"),
        "autor": campo(bloco, "autor"),
        "fonte": campo(bloco, "fonte"),
    })

print("entradas:", len(entradas))
os.makedirs(DESTINO, exist_ok=True)
with io.open(os.path.join(DESTINO, "calendario.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(entradas, f, ensure_ascii=False)

# quantos dias têm pelo menos uma entrada
dias = {e["diaMes"] for e in entradas}
print("dias cobertos:", len(dias), "de 366")
