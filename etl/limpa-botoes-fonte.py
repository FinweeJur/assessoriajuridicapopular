"""Tira os botões grandes "Ler no blog original" / "Sobre autor" dos posts.

O pedido do dono (22/11/2026): o link do original deve ficar na ficha de
origem, na linha "Blog", no mesmo tamanho do texto; os dois botões que
apareciam depois da citação saem. O botão "Sobre autor" some porque o link
"Todos os textos de ..." já cumpre o papel.

Uso:
  python etl/limpa-botoes-fonte.py --dry-run
  python etl/limpa-botoes-fonte.py
"""
import argparse
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCO = re.compile(r'\n?\s*<p class="acoes-fonte">.*?</p>\s*\n?', re.S)
LINK_BLOCO = re.compile(r'<a class="botao" href="([^"]+)"', re.S)
LINHA_BLOG = re.compile(
    r'(<dt>Blog</dt>\s*<dd>\s*)(<a class="link-fonte".*?</a>)(\s*</dd>)',
    re.S,
)
INLINE = (
    '<span class="link-original-sep" aria-hidden="true">·</span> '
    '<a class="link-original-inline" href="%s" target="_blank" rel="noopener">'
    'Ler no blog original<span class="sr-only"> (abre em outra aba)</span></a>'
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    mudados = 0
    sem_linha = 0
    ja_limpos = 0
    for nome in sorted(os.listdir(RAIZ)):
        if not nome.endswith(".html") or nome in ("radio-markup.html",):
            continue
        caminho = os.path.join(RAIZ, nome)
        t = io.open(caminho, encoding="utf-8").read()
        if "acoes-fonte" not in t:
            if "link-original-inline" in t:
                ja_limpos += 1
            continue
        bloco = BLOCO.search(t)
        if not bloco:
            continue
        achado = LINK_BLOCO.search(bloco.group(0))
        url = achado.group(1) if achado else ""
        novo = BLOCO.sub("\n", t, count=1)
        if url:
            linha = LINHA_BLOG.search(novo)
            if linha and "link-original-inline" not in linha.group(0):
                novo = (
                    novo[: linha.start()]
                    + linha.group(1)
                    + linha.group(2)
                    + " "
                    + INLINE % url
                    + linha.group(3)
                    + novo[linha.end() :]
                )
            elif not linha:
                sem_linha += 1
        if novo != t:
            mudados += 1
            if not args.dry_run:
                io.open(caminho, "w", encoding="utf-8", newline="\n").write(novo)
    print("paginas alteradas:", mudados, "| ja limpas:", ja_limpos, "| sem linha Blog:", sem_linha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
