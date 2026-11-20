"""Classifica cada texto por tipo e ano, para filtrar por tipo de post."""
import json
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
INDICE = os.path.join(RAIZ, "_indice.json")

REGRAS = [
    ("evento", r"oficina|curso|seminário|seminario|encontro|jornada|programação|programacao|"
               r"inscri|palestra|mesa|conferência|conferencia|evento|erenaju|erenap|"
               r"congresso|simposio|simpósio|mostra|feira"),
    ("poesia", r"poema|poesia|poetiz|verso|ode |soneto|haicai|cordel"),
    ("resenha", r"resenha|livro|revista|artigo|monografia|tese|disserta|publicação|publicacao"),
    ("documento", r"petição|peticao|edital|estatuto|carta |manifesto|nota |moção|mocao|abaixo-assinado"),
    ("notícia", r"urgente|denúncia|denuncia|preso|prisão|prisao|morte|morre|assassin|massacre|"
                r"despejo|operação|operacao|julgamento|decisão|decisao"),
]

CURTOS = {
    "evento": "Evento",
    "poesia": "Poesia",
    "resenha": "Resenha e livro",
    "documento": "Documento",
    "notícia": "Notícia",
    "formativo": "Texto formativo",
}


def classifica(registro):
    alvo = (" ".join([registro.get("titulo") or "", registro.get("resumo") or ""])).lower()
    for tipo, padrao in REGRAS:
        if re.search(padrao, alvo):
            return tipo
    return "formativo"


def main():
    with io.open(INDICE, encoding="utf-8") as f:
        registros = json.load(f)

    for r in registros:
        r["tipo"] = classifica(r)
        r["tipo_rotulo"] = CURTOS[r["tipo"]]

    with io.open(INDICE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(registros, f, ensure_ascii=False, indent=1)

    contagem = {}
    for r in registros:
        contagem[r["tipo"]] = contagem.get(r["tipo"], 0) + 1
    print("tipos:", contagem)


if __name__ == "__main__":
    main()
