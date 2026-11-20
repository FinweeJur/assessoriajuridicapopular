"""Palavras-chave por texto, a partir de um dicionário de sinônimos.

Entrada e saída: _indice.json. Cada registro ganha `palavras` (até 6).
"""
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")

PALAVRAS = {
    "mulheres": ["mulher", "mulheres", "feminista", "feminismo", "gênero", "genero", "marias"],
    "transporte": ["tarifa", "ônibus", "onibus", "transporte", "mobilidade", "passagem"],
    "educação": ["educação", "educacao", "escola", "ensino", "universidade", "estudant"],
    "MST": ["mst", "sem-terra", "sem terra", "assentamento", "acampamento"],
    "MAB": ["mab", "barragem", "barragens", "atingid"],
    "mineração": ["mineração", "mineracao", "mineradora", "minério", "minerio", "vale "],
    "clima": ["clima", "climático", "climatico", "ambiental", "floresta", "desmatamento"],
    "criminalização": ["criminaliza", "criminalizad", "criminalização"],
    "criminologia": ["criminologia", "criminológic", "criminologic", "penal", "prisão", "prisao"],
    "pesquisa": ["pesquisa", "pesquisador", "monografia", "disserta", "tese"],
    "oficina": ["oficina", "curso", "formação", "formacao", "capacita"],
    "poesia": ["poema", "poesia", "poetiz", "verso", "cordel"],
    "teatro": ["teatro", "teatral", "dramaturg"],
    "quilombo": ["quilombo", "quilombola"],
    "indígena": ["indígena", "indigena", "povos originários", "xokleng", "guarani"],
    "terra": ["terra", "agrária", "agraria", "reforma agrária", "latifúndio", "latifundio"],
    "moradia": ["moradia", "ocupação", "ocupacao", "despejo", "habitação", "habitacao"],
    "água": ["água", "agua", "rio ", "bacia", "saneamento"],
    "trabalho": ["trabalho", "trabalhador", "sindicat", "greve"],
    "ditadura": ["ditadura", "anistia", "tortura", "militares"],
    "direitos humanos": ["direitos humanos", "dh ", "direitos da pessoa"],
    "assessoria jurídica popular": ["assessoria jurídica", "assessoria juridica", "ajp", "advocacia popular"],
    "teoria crítica": ["teoria crítica", "teoria critica", "marx", "marxismo", "critical"],
}


def main():
    with io.open(INDICE, encoding="utf-8") as f:
        registros = json.load(f)

    for r in registros:
        alvo = " ".join([r.get("titulo") or "", r.get("resumo") or "",
                         " ".join(r.get("temas") or [])]).lower()
        r["palavras"] = [nome for nome, chaves in PALAVRAS.items()
                         if any(chave in alvo for chave in chaves)][:6]

    with io.open(INDICE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(registros, f, ensure_ascii=False, indent=1)

    com = sum(1 for r in registros if r["palavras"])
    print("palavras-chave:", com, "de", len(registros))


if __name__ == "__main__":
    main()
