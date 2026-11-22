"""Orquestrador mínimo do ETL do acervo AJP.

Não substitui a revisão humana; junta as etapas que já existem em uma ordem
explícita. `--dry-run` mostra os comandos; `--only` roda um recorte.

Uso:
  python etl/run.py --dry-run
  python etl/run.py --only audit
  python etl/run.py --only parse,pages,enrich
  python etl/run.py --all
"""
import argparse
import datetime as dt
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
FEED = r"G:\Meu Drive\RENAP-AJP\feed"
POSTS = r"G:\Meu Drive\RENAP-AJP\posts"
STAGING = r"G:\Meu Drive\RENAP-AJP\staging-full"

ETAPAS = {
    "audit": [
        [PY, os.path.join(RAIZ, "etl", "audita-acervo.py")],
    ],
    "parse": [
        [PY, os.path.join(RAIZ, "etl", "parse-ajp.py"), "--todos",
         "--feed", FEED, "--posts", POSTS, "--saida", STAGING,
         "--capturado-em", dt.date.today().isoformat()],
    ],
    "pages": [
        [PY, os.path.join(RAIZ, "etl", "monta-paginas.py"),
         "--fonte", STAGING, "--somente-novos"],
    ],
    "enrich": [
        [PY, os.path.join(RAIZ, "etl", "classifica.py")],
        [PY, os.path.join(RAIZ, "etl", "palavras.py")],
        [PY, os.path.join(RAIZ, "etl", "tema-principal.py")],
        [PY, os.path.join(RAIZ, "etl", "marca-redes.py")],
    ],
    "build": [
        [PY, os.path.join(RAIZ, "etl", "monta-secoes.py")],
        [PY, os.path.join(RAIZ, "etl", "monta-autores.py")],
        [PY, os.path.join(RAIZ, "etl", "monta-indice.py")],
        [PY, os.path.join(RAIZ, "etl", "sitemap-linha.py")],
        [PY, os.path.join(RAIZ, "etl", "atualiza-indice.py")],
    ],
    "rag": [
        [PY, os.path.join(RAIZ, "etl", "monta-rag.py")],
    ],
    "refs": [
        [PY, os.path.join(RAIZ, "etl", "extrai-referencias.py"), "--tudo",
         "--saida", os.path.join(RAIZ, "dados", "referencias.json")],
        [PY, os.path.join(RAIZ, "etl", "mescla-referencias-resolvidas.py")],
        [PY, os.path.join(RAIZ, "etl", "busca-referencias-externas.py"), "--aplicar"],
        [PY, os.path.join(RAIZ, "etl", "monta-referencias-abnt.py")],
        [PY, os.path.join(RAIZ, "etl", "monta-referencias-pagina.py")],
        [PY, os.path.join(RAIZ, "etl", "marca-referencias-post.py")],
        [PY, os.path.join(RAIZ, "etl", "relatorio-referencias-links.py")],
        [PY, os.path.join(RAIZ, "etl", "audita-referencias-abnt.py")],
    ],
    "manifest": [
        [PY, os.path.join(RAIZ, "etl", "gera-manifest.py")],
    ],
}

ORDEM = ["audit", "parse", "pages", "enrich", "build", "rag", "refs", "manifest", "audit"]


def roda(cmd, dry):
    print("$", " ".join('"%s"' % c if " " in c else c for c in cmd))
    if dry:
        return 0
    return subprocess.run(cmd, cwd=RAIZ).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="etapas separadas por vírgula")
    ap.add_argument("--all", action="store_true", help="roda a ordem completa")
    args = ap.parse_args()

    if args.only:
        escolhidas = [x.strip() for x in args.only.split(",") if x.strip()]
    elif args.all:
        escolhidas = ORDEM
    else:
        escolhidas = ["audit"]

    for etapa in escolhidas:
        if etapa not in ETAPAS:
            print("etapa desconhecida:", etapa)
            return 2
        print("\n== %s ==" % etapa)
        for cmd in ETAPAS[etapa]:
            codigo = roda(cmd, args.dry_run)
            if codigo:
                print("falhou:", etapa, "código", codigo)
                return codigo
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
