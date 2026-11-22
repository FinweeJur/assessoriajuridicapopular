"""Tema principal determinístico: cinco seções, com rebalanceamento por sinais.

Cada texto mantém suas tags em `temas`; aqui escolhemos o tema principal que
define a seção. As regras são auditáveis: termos no título/resumo/palavras,
bônus por tag existente e pesos calibrados para reduzir o peso excessivo de
"teoria crítica" e "educação popular".
"""
import csv
import io
import json
import os
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
CSV = os.path.join(RAIZ, "dados", "rebalanceamento.csv")

TEMAS = ["assessoria-juridica-popular", "direitos-humanos", "movimentos-sociais",
         "educacao-popular", "teoria-critica"]

ROTULOS = {
    "assessoria-juridica-popular": "Assessoria jurídica popular",
    "direitos-humanos": "Direitos humanos",
    "movimentos-sociais": "Movimentos sociais",
    "educacao-popular": "Educação popular",
    "teoria-critica": "Teoria crítica do direito",
}

PESOS = {
    "assessoria-juridica-popular": 0.8,
    "direitos-humanos": 3.0,
    "movimentos-sociais": 3.4,
    "educacao-popular": 1.6,
    "teoria-critica": 4.6,
}
BONUS_TAG = 0.8

TERMOS = {
    "assessoria-juridica-popular": [
        "assessoria juridica popular", "assessoria jurídica popular", "ajup", "saju", "najup",
        "advocacia popular", "advogado popular", "advogada popular", "assessoria popular", "ajp"],
    "direitos-humanos": [
        "direitos humanos", "violacao", "violação", "criminaliz", "prisao", "prisão", "massacre",
        "tortura", "racismo", "indigena", "indígena", "quilombola", "lgbt", "feminicidio",
        "feminicídio", "violencia", "violência", "desaparec", "execucao", "execução", "ameaca",
        "ameaça", "impunidade", "ditadura"],
    "movimentos-sociais": [
        "mst", "mtst", "ocupacao", "ocupação", "movimento social", "movimentos sociais",
        "sindicato", "greve", "reforma agraria", "reforma agrária", "moradia", "sem-terra",
        "assentamento", "quilombo", "estudantil", "luta pela terra", "despejo", "reintegracao",
        "reintegração", "acampamento", "campones", "trabalhadores rurais"],
    "educacao-popular": [
        "educacao popular", "educação popular", "oficina", "curso", "formacao", "formação",
        "ensino juridico", "ensino jurídico", "pedagogia", "paulo freire", "freire",
        "extensao universitaria", "extensão universitária", "seminario", "seminário", "encontro",
        "jornada", "palestra", "aula", "universidade"],
    "teoria-critica": [
        "teoria critica", "teoria crítica", "teoria", "critica do direito", "crítica do direito",
        "marx", "marxismo", "pachukanis", "lyra filho", "pluralismo juridico",
        "pluralismo jurídico", "direito insurgente", "insurgente", "epistemologia", "filosofia",
        "ontologia", "dialetica", "dialética", "hegel", "gramsci", "dussel", "marini",
        "descolonial", "decolonial", "direito alternativo"],
}

ORDEM_DESEMPATE = ["movimentos-sociais", "direitos-humanos", "teoria-critica",
                   "educacao-popular", "assessoria-juridica-popular"]


def norm(t):
    return unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode().lower()


def principal(registro):
    texto = norm(" ".join([registro.get("titulo") or "", registro.get("resumo") or "",
                           " ".join(registro.get("palavras") or [])]))
    tags = set(registro.get("temas") or [])
    pontos = {}
    for tema in TEMAS:
        pts = BONUS_TAG if tema in tags else 0.0
        for termo in TERMOS[tema]:
            if norm(termo) in texto:
                pts += PESOS[tema]
        pontos[tema] = pts
    melhor = max(pontos.values())
    if melhor <= 0:
        return "assessoria-juridica-popular", pontos
    for tema in ORDEM_DESEMPATE:
        if pontos[tema] >= melhor - 0.001:
            return tema, pontos
    return ORDEM_DESEMPATE[0], pontos


def main():
    registros = json.load(io.open(INDICE, encoding="utf-8"))
    linhas = []
    for r in registros:
        antigo = r.get("tema_principal") or ""
        tema, pontos = principal(r)
        r["tema_principal"] = tema
        r["tema"] = ROTULOS.get(tema, "Assessoria jurídica popular")
        if antigo and antigo != tema:
            linhas.append({
                "slug": r.get("slug", ""),
                "titulo": (r.get("titulo") or "")[:120],
                "antes": antigo,
                "depois": tema,
                "pontos": " | ".join("%s=%.1f" % (t, pontos[t]) for t in TEMAS),
            })
    json.dump(registros, io.open(INDICE, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)

    with io.open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["slug", "titulo", "antes", "depois", "pontos"])
        w.writeheader()
        w.writerows(linhas)

    contagem = {}
    for r in registros:
        contagem[r["tema_principal"]] = contagem.get(r["tema_principal"], 0) + 1
    print("por tema principal:", contagem)
    print("mudancas:", len(linhas), "| csv:", CSV)


if __name__ == "__main__":
    main()
