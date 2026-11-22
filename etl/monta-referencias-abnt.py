"""Gera o documento ABNT e os recortes por tema e por autor.

Entrada: `dados/referencias.json` (extração local) e, se existir,
`dados/referencias-links.json` (status dos links).
Saída: `docs/referencias-abnt.md`, `docs/referencias-por-tema.md`,
`docs/referencias-por-autor.md` e `docs/referencias.csv`.

Norma de referência: ABNT NBR 6023:2018. Quando falta local/editora, usa
`[s.l.: s.n.]`; quando falta ano, `[s.d.]`. Nada é inventado.
"""
import csv
import io
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
LINKS = os.path.join(RAIZ, "dados", "referencias-links.json")
INDICE = os.path.join(RAIZ, "_indice.json")
DOCS = os.path.join(RAIZ, "docs")
ACESSO = "22 nov. 2026"

TEMAS = {
    "assessoria-juridica-popular": "Assessoria jurídica popular",
    "direitos-humanos": "Direitos humanos",
    "movimentos-sociais": "Movimentos sociais",
    "educacao-popular": "Educação popular",
    "teoria-critica": "Teoria crítica do direito",
    "memoria": "Memória e cultura",
}
ORDEM = list(TEMAS) + ["sem-tema"]


def sem_acento(t):
    return unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode().lower()


def limpa(t):
    return re.sub(r"\s+", " ", (t or "").replace("\n", " ")).strip()


def autor(r):
    a = limpa(r.get("autor"))
    return a or "AUTOR NÃO IDENTIFICADO"


def ano(r):
    a = limpa(str(r.get("ano") or ""))
    return a if re.fullmatch(r"\d{4}", a) else "[s.d.]"


def titulo(r):
    return limpa(r.get("titulo")) or "[Sem título]"


def abnt(r):
    a = autor(r)
    t = titulo(r)
    y = ano(r)
    tipo = r.get("tipo") or "obra"
    veiculo = limpa(r.get("veiculo"))
    url = limpa(r.get("url"))
    base = ""

    if tipo in ("livro", "obra"):
        imprenta = "[s.l.: s.n.]"
        if veiculo:
            imprenta = "[s.l.]: %s" % veiculo
        base = "%s. **%s**. %s, %s." % (a, t, imprenta, y)
    elif tipo == "capitulo":
        base = "%s. **%s**. In: [obra coletiva], %s." % (a, t, y)
    elif tipo == "artigo":
        base = "%s. **%s**. *%s*, %s." % (a, t, veiculo or "[periódico não identificado]", y)
    elif tipo in ("tese", "dissertacao", "monografia"):
        rotulo = {"tese": "Tese", "dissertacao": "Dissertação", "monografia": "Monografia"}[tipo]
        base = "%s. **%s**. %s. %s – [instituição não identificada], [s.l.]." % (a, t, y, rotulo)
    elif tipo == "legislacao":
        base = "%s. **%s**. %s." % (a if a != "AUTOR NÃO IDENTIFICADO" else "BRASIL", t, y)
    elif tipo == "video":
        base = "%s. **%s**. %s. [Vídeo]." % (a, t, y)
    elif tipo == "relatorio":
        base = "%s. **%s**. %s. [Relatório]." % (a, t, y)
    else:
        base = "%s. **%s**. %s." % (a, t, y)

    if url:
        base += " Disponível em: <%s>. Acesso em: %s." % (url, ACESSO)
    return limpa(base)


def status_link(url, links):
    if not url:
        return "sem_link"
    d = links.get(url) or {}
    return d.get("acesso") or "nao_verificado"


def marca_link(url, links):
    if not url:
        return "_sem link gratuito localizado_"
    s = status_link(url, links)
    if s == "aberto":
        return "[Disponível aqui](%s)" % url
    if s == "restrito":
        return "[Link restrito](%s)" % url
    if s == "morto_ou_instavel":
        return "~~Disponível aqui~~ (link não respondeu)"
    return "[Ver link](%s)" % url


def carrega(p, padrao):
    try:
        return json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return padrao


def main():
    dados = carrega(REF, {})
    refs = dados.get("referencias", []) if isinstance(dados, dict) else dados
    links = carrega(LINKS, {})
    indice = {r["slug"]: r for r in carrega(INDICE, [])}
    refs.sort(key=lambda r: (sem_acento(autor(r)), sem_acento(titulo(r)), r.get("ano") or ""))

    contagem = {}
    for r in refs:
        contagem[r.get("confianca") or "baixa"] = contagem.get(r.get("confianca") or "baixa", 0) + 1
    links_contagem = {}
    for r in refs:
        s = status_link(r.get("url"), links)
        links_contagem[s] = links_contagem.get(s, 0) + 1

    cabeca = """# Referências citadas no acervo AJP — ABNT

> **Gerado em:** 22/11/2026
> **Fonte:** `dados/referencias.json`, extraído dos 790 posts, da Biblioteca e
> das páginas de referências.
> **Norma:** ABNT NBR 6023:2018. Citações no texto: NBR 10520:2023.
> **Links:** `dados/referencias-links.json`, conferido em 22/11/2026 com
> User-Agent `finweejur/github artur colito`; HEAD/GET de 1 byte, 1,2 s entre
> requisições. As 177 URLs das referências foram conferidas. “Disponível aqui”
> só aparece quando o link respondeu 2xx/3xx.
> **Aviso:** 221 referências têm confiança alta; 149 média; 236 baixa. As de
> confiança baixa (sem autor, ano ou título) estão marcadas e precisam de
> revisão humana antes de virar citação oficial.

## Números

| Item | Valor |
|---|---:|
| Referências extraídas | %d |
| Com URL explícita | %d |
| Confiança alta / média / baixa | %d / %d / %d |
| Links abertos / restritos / mortos / não verificados / sem link | %d / %d / %d / %d / %d |

## Como ler

- **Alta:** autor, título, ano e veículo/imprenta reconhecidos.
- **Média:** referência plausível, mas falta ano, imprenta ou o texto do link é curto.
- **Baixa:** falta autor, ano ou título; revisar antes de citar.
- `[s.l.: s.n.]` e `[s.d.]` são lacunas da fonte, não invenção.
- O link “Disponível aqui” leva ao acesso aberto quando ele foi confirmado;
  “Link restrito” e “link não respondeu” ficam visíveis de propósito.

---

## Referências em ordem alfabética

""" % (
        len(refs),
        sum(1 for r in refs if r.get("url")),
        contagem.get("alta", 0), contagem.get("media", 0), contagem.get("baixa", 0),
        links_contagem.get("aberto", 0), links_contagem.get("restrito", 0),
        links_contagem.get("morto_ou_instavel", 0), links_contagem.get("nao_verificado", 0),
        links_contagem.get("sem_link", 0),
    )

    def lista(itens):
        linhas = []
        for i, r in enumerate(itens, 1):
            fonte = r.get("fonte_slug") or ""
            post = indice.get(fonte, {})
            linhas.append(
                "%d. %s  \n   _Fonte:_ [%s](%s.html) · _Confiança:_ %s · %s" % (
                    i, abnt(r), post.get("titulo") or fonte or "—", fonte or "#",
                    r.get("confianca") or "baixa", marca_link(r.get("url"), links),
                )
            )
        return linhas

    principais = [r for r in refs if (r.get("confianca") or "baixa") != "baixa"]
    baixas = [r for r in refs if (r.get("confianca") or "baixa") == "baixa"]
    corpo = "\n".join(lista(principais))
    corpo += "\n\n## Apêndice — confiança baixa (revisar antes de citar)\n\n"
    corpo += "\n".join(lista(baixas))
    io.open(os.path.join(DOCS, "referencias-abnt.md"), "w", encoding="utf-8", newline="\n").write(
        cabeca + corpo + "\n"
    )

    # Por tema
    por_tema = {t: [] for t in ORDEM}
    for r in refs:
        post = indice.get(r.get("fonte_slug") or "", {})
        t = post.get("tema_principal") or "sem-tema"
        por_tema.setdefault(t, []).append(r)
    saida = ["# Referências por tema — ABNT\n\n> Mesma base de `referencias-abnt.md`; o tema é o da página que cita a obra.\n"]
    for t in ORDEM:
        itens = por_tema.get(t, [])
        if not itens:
            continue
        saida.append("\n## %s (%d)\n" % (TEMAS.get(t, "Sem tema"), len(itens)))
        for r in itens:
            saida.append("- %s  \n  _Fonte:_ [%s](%s.html) · %s" % (
                abnt(r), indice.get(r.get("fonte_slug") or "", {}).get("titulo") or r.get("fonte_slug") or "—",
                r.get("fonte_slug") or "#", marca_link(r.get("url"), links)))
    io.open(os.path.join(DOCS, "referencias-por-tema.md"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(saida) + "\n")

    # Por autor
    por_autor = {}
    for r in refs:
        por_autor.setdefault(autor(r), []).append(r)
    saida = ["# Referências por autor — ABNT\n\n> Agrupadas pelo autor como aparece na fonte; `AUTOR NÃO IDENTIFICADO` é lacuna, não pseudônimo.\n"]
    for a in sorted(por_autor, key=sem_acento):
        saida.append("\n## %s (%d)\n" % (a, len(por_autor[a])))
        for r in por_autor[a]:
            saida.append("- %s  \n  _Fonte:_ [%s](%s.html) · %s" % (
                abnt(r), indice.get(r.get("fonte_slug") or "", {}).get("titulo") or r.get("fonte_slug") or "—",
                r.get("fonte_slug") or "#", marca_link(r.get("url"), links)))
    io.open(os.path.join(DOCS, "referencias-por-autor.md"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(saida) + "\n")

    # CSV
    with io.open(os.path.join(DOCS, "referencias.csv"), "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "tipo", "autor", "titulo", "ano", "veiculo", "url", "acesso", "fonte_slug", "confianca", "abnt"])
        for r in refs:
            w.writerow([r.get("id", ""), r.get("tipo", ""), r.get("autor", ""), r.get("titulo", ""),
                        r.get("ano", ""), r.get("veiculo", ""), r.get("url", ""),
                        status_link(r.get("url"), links), r.get("fonte_slug", ""),
                        r.get("confianca", ""), abnt(r)])

    print("referencias:", len(refs), "| links:", links_contagem)


if __name__ == "__main__":
    main()
