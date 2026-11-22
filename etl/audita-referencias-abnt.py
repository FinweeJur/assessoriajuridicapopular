"""Audita o documento ABNT gerado contra o JSON de referências.

Não corrige nada: conta os defeitos que ainda dependem de revisão humana e
imprime uma tabela. Sai com código 1 se algum limite do relatório
`docs/REFERENCIAS-ABNT-REVISAO.md` for violado, para poder rodar em CI.
"""
import importlib.util
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
DOC = os.path.join(RAIZ, "docs", "referencias-abnt.md")

spec = importlib.util.spec_from_file_location(
    "ab", os.path.join(RAIZ, "etl", "monta-referencias-abnt.py")
)
ab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ab)

refs = json.load(io.open(REF, encoding="utf-8"))["referencias"]
texto = io.open(DOC, encoding="utf-8").read()

# Imprenta explícita no trecho: "Local: Editora, ano" (aceita mês abreviado).
IMPRENTA = re.compile(
    r"([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*(?:\s+(?:d[aeo]s?|[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*)){0,4})"
    r":\s*([^,;]{2,55}),\s*(?:[a-z]{3,9}\.?\s*)?(\d{4})"
)


def imprenta(trecho):
    achados = IMPRENTA.findall(trecho or "")
    return achados[-1] if achados else None


def conta(cond):
    return sum(1 for r in refs if cond(r))


def sem_autor(r):
    return not ab.autor_abnt(r)


def autor_suspeito(r):
    """Olha a saída, não o campo bruto: nome natural, lixo ou partícula solta."""
    if not ab.autor_abnt(r):
        return False
    if r.get("autor_tipo") == "institucional":
        return False
    bruto = (r.get("autor") or "").lower()
    if re.search(r"\s[-–]\s", bruto) or any(p.strip(".,;") in ab.ORGS for p in bruto.split()):
        return False
    cabeca = ab.abnt(r).split(". ")[0]
    cabeca = cabeca.replace("(Org.)", "")
    if re.search(r"[*()\d]| em \d{1,2} de ", cabeca):
        return True
    sobrenome = cabeca.split(",")[0].strip()
    if sobrenome.lower() in ("de", "da", "do", "das", "dos", "e"):
        return True
    if " e " in sobrenome:
        return True
    return False


def entradas_do_documento():
    """(autor, ano, linha) de cada item numerado do corpo."""
    corpo = texto.split("## Referências em ordem alfabética", 1)[-1]
    itens = []
    for linha in corpo.splitlines():
        m = re.match(r"^\d+\.\s+(.+)$", linha)
        if not m:
            continue
        texto_item = m.group(1)
        autor = texto_item.split(". ")[0]
        # O ano de publicação vem antes de "Disponível em"/"Acesso em";
        # a data de acesso não conta para o sufixo a/b.
        corte = re.split(r"Dispon[ií]vel em|Acesso em", texto_item)[0]
        ano = re.search(r"(\d{4}[a-z]?)\s*(?:\.|,|$)", corte)
        itens.append((autor, ano.group(1) if ano else "", texto_item))
    return itens


def duplicados(itens):
    """Duplicatas no documento final, já com títulos normalizados."""
    vistos = {}
    for autor, ano, linha in itens:
        m = re.search(r"\*\*(.+?)\*\*", linha)
        titulo = m.group(1) if m else linha
        chave = (
            re.sub(r"[^a-z0-9]", "", ab.sem_acento(titulo)),
            re.sub(r"[^a-z0-9]", "", ab.sem_acento(autor)),
            re.sub(r"[a-z]$", "", ano),
        )
        vistos.setdefault(chave, []).append(linha[:70])
    return {k: v for k, v in vistos.items() if len(v) > 1}


itens = entradas_do_documento()
grupos_ano = {}
for autor, ano, linha in itens:
    if re.fullmatch(r"\d{4}[a-z]?", ano):
        grupos_ano.setdefault((autor, ano), []).append((ano, linha))
sem_sufixo = 0
for (autor, ano), linhas in grupos_ano.items():
    if len(linhas) < 2:
        continue
    if not any(re.fullmatch(r"\d{4}[a-z]", a) for a, _ in linhas):
        sem_sufixo += len(linhas)

dups = duplicados(itens)
checks = [
    (
        "[s.l.] com imprenta explícita no trecho",
        conta(lambda r: "[s.l.]" in ab.abnt(r) and imprenta(r.get("trecho"))),
    ),
    (
        "[s.n.] com editora explícita no trecho",
        conta(lambda r: "[s.n.]" in ab.abnt(r) and imprenta(r.get("trecho"))),
    ),
    (
        "capítulo com p. no trecho e sem p. na saída",
        conta(
            lambda r: r.get("tipo") == "capitulo"
            and re.search(r"\bp\.\s*\d", r.get("trecho") or "")
            and " p. " not in ab.abnt(r)
        ),
    ),
    ("autor com asterisco, dígito, partícula ou 'e'", conta(autor_suspeito)),
    ("título com mais de 200 caracteres", conta(lambda r: len(ab.titulo(r)) > 200)),
    (
        "título com imprenta colada",
        conta(lambda r: re.search(r":\s*[^:]{2,60},\s*\d{4}$", ab.titulo(r))),
    ),
    ("duplicatas por título+autor+ano", len(dups)),
    ("(autor, ano) repetido sem sufixo a/b", sem_sufixo),
]
numeros = [int(n) for n in re.findall(r"^(\d+)\. ", texto, re.M)]
checks.append(("números de entrada repetidos", len(numeros) - len(set(numeros))))
cabeca = texto.split("## Referências em ordem alfabética")[0]
declarado = re.search(r"Referências na lista[^|]*\|\s*(\d+)", cabeca)
checks.append(
    (
        "contagem do cabeçalho diferente do corpo",
        abs(int(declarado.group(1)) - len(numeros)) if declarado else -1,
    )
)

print("referências no JSON:", len(refs), "| entradas no documento:", len(numeros))
print("%-48s %5d  (informativo: lacuna da fonte)" % ("entrada sem autor identificado", conta(sem_autor)))
falhou = False
for nome, valor in checks:
    estado = "ok" if valor == 0 else "FALHA"
    falhou = falhou or valor != 0
    print("%-48s %5d  (%s)" % (nome, valor, estado))

if dups:
    print("\nduplicatas:")
    for chave, ids in list(dups.items())[:10]:
        print("  ", chave[0][:70], "->", ids)

sys.exit(1 if falhou else 0)
