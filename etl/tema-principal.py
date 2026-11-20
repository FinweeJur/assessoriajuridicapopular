"""Tema principal: cada texto aparece em uma seção só. Os outros temas viram tags."""
import io
import json
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
INDICE = os.path.join(RAIZ, "_indice.json")

# Ordem de prioridade quando o parser não decidiu: o tema mais específico ganha.
PRIORIDADE = [
    "teoria-critica", "educacao-popular", "movimentos-sociais",
    "direitos-humanos", "memoria", "assessoria-juridica-popular",
]


def principal(registro):
    temas = registro.get("temas") or []
    for tema in PRIORIDADE:
        if tema in temas:
            return tema
    return temas[0] if temas else "assessoria-juridica-popular"


def main():
    with io.open(INDICE, encoding="utf-8") as f:
        registros = json.load(f)

    for r in registros:
        tema = principal(r)
        r["tema_principal"] = tema
        rotulos = {
            "assessoria-juridica-popular": "Assessoria jurídica popular",
            "direitos-humanos": "Direitos humanos",
            "movimentos-sociais": "Movimentos sociais",
            "memoria": "Memória e cultura",
            "teoria-critica": "Teoria crítica",
            "educacao-popular": "Educação popular",
        }
        r["tema"] = rotulos.get(tema, r.get("tema") or "Assessoria jurídica popular")

    with io.open(INDICE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(registros, f, ensure_ascii=False, indent=1)

    contagem = {}
    for r in registros:
        contagem[r["tema_principal"]] = contagem.get(r["tema_principal"], 0) + 1
    print("por tema principal:", contagem)


if __name__ == "__main__":
    main()
