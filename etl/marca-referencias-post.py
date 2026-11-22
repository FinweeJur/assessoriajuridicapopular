"""Adiciona ou atualiza o botão “Referências citadas neste texto”.

O botão fica antes de `</article>` e aponta para o grupo `#fonte-<slug>` da
página `referencias-citadas.html`. A contagem é recalculada a cada execução;
posts que perderam todas as referências têm o botão removido.
"""
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")

BOTAO = re.compile(
    r'\n?[ \t]*<p class="referencias-post"><a class="botao secundario" '
    r'href="referencias-citadas\.html#fonte-([^"]+)">'
    r'Referências citadas neste texto \(\d+\)</a></p>\n?'
)


def monta(slug, n):
    return (
        '\n    <p class="referencias-post">'
        '<a class="botao secundario" href="referencias-citadas.html#fonte-%s">'
        'Referências citadas neste texto (%d)</a></p>\n' % (slug, n)
    )


def main():
    dados = json.load(io.open(REF, encoding="utf-8"))
    refs = dados.get("referencias", []) if isinstance(dados, dict) else dados
    por_fonte = {}
    for r in refs:
        s = r.get("fonte_slug")
        if s:
            por_fonte[s] = por_fonte.get(s, 0) + 1

    adicionados = atualizados = removidos = 0
    for nome in os.listdir(RAIZ):
        if not nome.endswith(".html"):
            continue
        slug = nome[:-5]
        caminho = os.path.join(RAIZ, nome)
        t = io.open(caminho, encoding="utf-8").read()
        if "referencias-citadas.html#fonte-" not in t:
            if slug not in por_fonte:
                continue
            pos = t.rfind("</article>")
            if pos < 0:
                continue
            t = t[:pos] + monta(slug, por_fonte[slug]) + t[pos:]
            adicionados += 1
        else:
            if slug not in por_fonte:
                novo = BOTAO.sub("\n", t)
                if novo != t:
                    t = novo
                    removidos += 1
            else:
                def troca(m):
                    return monta(m.group(1), por_fonte[slug])
                novo = BOTAO.sub(troca, t)
                if novo != t:
                    t = novo
                    atualizados += 1
        io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)

    print(
        "botões: %d adicionados, %d atualizados, %d removidos"
        % (adicionados, atualizados, removidos)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
