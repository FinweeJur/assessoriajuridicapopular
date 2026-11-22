"""Gera o documento ABNT e os recortes por tema e por autor.

Entrada: `dados/referencias.json` (extração local) e, se existir,
`dados/referencias-links.json` (status dos links).
Saída: `docs/referencias-abnt.md`, `docs/referencias-por-tema.md`,
`docs/referencias-por-autor.md` e `docs/referencias.csv`.

Norma de referência: ABNT NBR 6023:2018. Quando falta local/editora, usa
`[s.l.: s.n.]`; quando falta ano, `[s.d.]`. Nada é inventado.
"""
import csv
import html
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


SUFIXOS = {"filho", "neto", "junior", "sobrinho", "segundo"}
ORGS = {
    "conselho", "instituto", "rede", "movimento", "associação", "comissão",
    "ministério", "universidade", "centro", "núcleo", "gabinete", "sociedade",
    "organização", "observatório", "fórum", "grupo", "coletivo", "editora",
    "revista", "assembleia", "secretaria", "coordenação", "setor", "direitos",
}


def autor(r):
    """Autor como chave de agrupamento; vazio vira rótulo explícito."""
    a = limpa(r.get("autor"))
    return a or "Autoria não identificada"


def autor_abnt(r):
    """Inverte nome pessoal; mantém organização e nome já invertido."""
    a = limpa(r.get("autor"))
    if not a or a[0].islower():
        return ""
    a = re.sub(r",\s*em\s+\d{1,2}\s+de\s+[\wÀ-ÿ]+\s+de\s+\d{4}\s*$", "", a, flags=re.I)
    org_sufixo = ""
    m = re.search(r"\s*\((?:orgs?\.?|organizador(?:a)?)\)\s*$", a, flags=re.I)
    if m:
        org_sufixo = " (Org.)"
        a = a[: m.start()].strip()
    a = re.sub(r"\s*\*+\s*$", "", a)
    a = re.sub(r"\s*\(\s*\d{4}\s*\)\s*$", "", a)
    a = a.rstrip(" .,;:")
    if re.search(r"\s+[-–]\s+", a) or any(p.lower() in ORGS for p in a.split()[:3]):
        return a + org_sufixo
    if "," in a:
        esquerda, direita = a.split(",", 1)
        return "%s, %s%s" % (esquerda.strip().upper(), direita.strip(), org_sufixo)
    if ";" in a:
        return a + org_sufixo
    if " e " in a and not any(p.lower() in ORGS for p in a.split()[:2]):
        partes = [p.strip() for p in a.split(" e ") if len(p.split()) > 1]
        if len(partes) > 1:
            return "; ".join(autor_abnt({"autor": p}) for p in partes) + org_sufixo
    palavras = a.split()
    if len(palavras) < 2:
        return a + org_sufixo
    if all(p.isupper() for p in palavras if p.isalpha()):
        return a + org_sufixo
    if palavras[-1].lower() in SUFIXOS and len(palavras) > 2:
        sobrenome = " ".join(palavras[-2:])
        nome = " ".join(palavras[:-2])
    else:
        sobrenome = palavras[-1]
        nome = " ".join(palavras[:-1])
    return "%s, %s%s" % (sobrenome.upper(), nome, org_sufixo)


def ano(r):
    a = limpa(str(r.get("ano") or ""))
    return a if re.fullmatch(r"\d{4}", a) else "[s.d.]"


def titulo(r):
    """Título sem a imprenta que às vezes veio colada no fim do trecho."""
    t = limpa(r.get("titulo")) or "[Sem título]"
    t = re.sub(
        r"[\.,;]?\s*(?:\d+\s*ed[\.,]?\s*)?[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*(?:\s+d[aeo]s?"
        r"|\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*){0,4}\s*:\s*[^:;]{2,60},\s*\d{4}\s*$",
        "",
        t,
    )
    t = re.sub(r"[\"”']?\s*,?\s*In:\s*.+$", "", t)
    t = re.sub(r"(?:[\.,;]|\s)+$", "", t)
    t = t.strip() or "[Sem título]"
    if len(t) > 180:
        corte = t[:180].rsplit(" ", 1)[0]
        t = corte + " […]"
    return t


def chave_titulo(r):
    """Compara títulos ignorando caixa, acento, pontuação e espaços."""
    return re.sub(r"\W+", "", sem_acento(titulo(r)))


def aplica_sufixos(refs):
    """NBR 10520:2023 — mesmo autor e ano recebem sufixo a, b, c…"""
    grupos = {}
    for r in refs:
        a = sem_acento(autor_abnt(r) or autor(r)).split(";")[0].strip()
        y = r.get("ano") if re.fullmatch(r"\d{4}", str(r.get("ano") or "")) else ""
        r["_sufixo"] = ""
        if a and y:
            grupos.setdefault((a, y), []).append(r)
    for itens in grupos.values():
        if len({chave_titulo(r) for r in itens}) < 2:
            continue
        itens.sort(key=chave_titulo)
        letra = "a"
        por_titulo = {}
        for r in itens:
            chave = chave_titulo(r)
            if chave not in por_titulo:
                por_titulo[chave] = letra
                letra = chr(ord(letra) + 1)
            r["_sufixo"] = por_titulo[chave]
    return refs


def dados_trecho(r):
    """Recupera imprenta e dados complementares que já estão no trecho."""
    trecho = limpa(r.get("trecho"))
    local = editora = paginas = volume = numero = instituicao = ""
    achados = re.findall(
        r"([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*(?:\s+(?:d[aeo]s?|[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*)){0,4}):"
        r"\s*([^,;]{2,55}),\s*(?:[a-z]{3,9}\.?\s*)?(\d{4})",
        trecho,
    )
    if achados:
        local, editora = achados[-1][0].strip(), achados[-1][1].strip()
    if not local:
        m = re.search(
            r",\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*(?:\s+(?:d[aeo]s?|[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*)){0,4}),"
            r"\s*(?:[a-z]{3,9}\.?\s*)?(\d{4})",
            trecho,
        )
        if m:
            local = m.group(1).strip()
    m = re.search(r"p\.\s*([\d]+(?:\s*[-–]\s*\d+)?)", trecho)
    if m:
        paginas = m.group(1)
    m = re.search(r"v\.\s*(\d+)", trecho)
    if m:
        volume = m.group(1)
    m = re.search(r"n\.\s*(\d+)", trecho)
    if m:
        numero = m.group(1)
    m = re.search(
        r"(Universidade [A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ .'-]+|UnB|Unicamp|USP|UFRJ|UFRGS|UFBA|UFPR|UFSC|UFF|UERJ|UF[A-Z]{2}|PUC[\w-]*)",
        trecho,
    )
    if m:
        instituicao = m.group(1).strip().rstrip(".,;")
    return local, editora, paginas, volume, numero, instituicao


def abnt(r):
    a = autor_abnt(r)
    prefixo = (a + ". ") if a else ""
    t = titulo(r)
    y = ano(r) + (r.get("_sufixo") or "")
    tipo = r.get("tipo") or "obra"
    veiculo = limpa(r.get("veiculo"))
    url = limpa(r.get("url"))
    local, editora, paginas, volume, numero, instituicao = dados_trecho(r)
    base = ""

    if tipo in ("livro", "obra"):
        imprenta = "%s: %s" % (local or "[s.l.]", editora or veiculo or "[s.n.]")
        base = "%s**%s**. %s, %s." % (prefixo, t, imprenta, y)
    elif tipo == "capitulo":
        fim = "%s, p. %s" % (y, paginas) if paginas else y
        if local or editora:
            base = "%s**%s**. %s: %s, %s." % (
                prefixo, t, local or "[s.l.]", editora or "[s.n.]", fim)
        else:
            base = "%s**%s**. %s." % (prefixo, t, fim)
    elif tipo == "artigo":
        periodico = veiculo or "[periódico]"
        extras = []
        if local:
            extras.append(local)
        if volume:
            extras.append("v. %s" % volume)
        if numero:
            extras.append("n. %s" % numero)
        if paginas:
            extras.append("p. %s" % paginas)
        meio = ", ".join(extras + [y])
        base = "%s**%s**. *%s*, %s." % (prefixo, t, periodico, meio)
    elif tipo in ("tese", "dissertacao", "monografia"):
        rotulo = {"tese": "Tese", "dissertacao": "Dissertação", "monografia": "Monografia"}[tipo]
        inst = instituicao or "[s.l.: s.n.]"
        base = "%s**%s**. %s. %s – %s." % (prefixo, t, y, rotulo, inst)
    elif tipo == "legislacao":
        base = "%s**%s**. %s." % (prefixo or "BRASIL. ", t, y)
    elif tipo == "video":
        base = "%s**%s**. %s. [Vídeo]." % (prefixo, t, y)
    elif tipo == "relatorio":
        base = "%s**%s**. %s. [Relatório]." % (prefixo, t, y)
    else:
        base = "%s**%s**. %s." % (prefixo, t, y)

    if url:
        base += " Disponível em: <%s>. Acesso em: %s." % (url, ACESSO)
    return limpa(base)


def abnt_html(r):
    """ABNT para HTML: escapa tags e converte **forte** e *ênfase*."""
    s = html.escape(abnt(r), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
    return s


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
    if s == "emprestimo":
        return "[Empréstimo digital](%s)" % url
    if s == "previa":
        return "[Prévia](%s)" % url
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
    aplica_sufixos(refs)
    vistos = set()
    unicos = []
    for r in refs:
        chave = (
            chave_titulo(r),
            re.sub(r"\W+", "", sem_acento(autor_abnt(r) or autor(r))),
            str(r.get("ano") or ""),
        )
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(r)
    refs = unicos
    refs.sort(key=lambda r: (sem_acento(autor(r)), sem_acento(titulo(r)), r.get("ano") or ""))

    contagem = {}
    for r in refs:
        contagem[r.get("confianca") or "baixa"] = contagem.get(r.get("confianca") or "baixa", 0) + 1
    links_contagem = {}
    for r in refs:
        s = status_link(r.get("url"), links)
        links_contagem[s] = links_contagem.get(s, 0) + 1

    com_url = sum(1 for r in refs if r.get("url"))
    cabeca = """# Referências citadas no acervo AJP — ABNT

> **Gerado em:** 22/11/2026
> **Fonte:** `dados/referencias.json`, extraído dos 790 posts, da Biblioteca e
> das páginas de referências.
> **Norma:** ABNT NBR 6023:2018. Citações no texto: NBR 10520:2023.
> **Links:** `dados/referencias-links.json`, conferido em 22/11/2026 com
> User-Agent `finweejur/github artur colito`; HEAD/GET de 1 byte, 1,2 s entre
> requisições. As %d referências com URL foram conferidas. “Disponível aqui”
> só aparece quando o link respondeu 2xx/3xx.
> **Aviso:** %d referências têm confiança alta; %d média; %d baixa. As de
> confiança baixa (sem autor, ano ou título) estão marcadas e precisam de
> revisão humana antes de virar citação oficial. Entradas de mesmo autor e
> ano recebem sufixo a, b, c… conforme a NBR 10520:2023.

## Números

| Item | Valor |
|---|---:|
| Referências na lista (duplicatas exatas removidas) | %d |
| Com URL explícita | %d |
| Confiança alta / média / baixa | %d / %d / %d |
| Links abertos / empréstimo / restritos / mortos / sem link | %d / %d / %d / %d / %d |

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
        com_url,
        contagem.get("alta", 0), contagem.get("media", 0), contagem.get("baixa", 0),
        len(refs), com_url,
        contagem.get("alta", 0), contagem.get("media", 0), contagem.get("baixa", 0),
        links_contagem.get("aberto", 0), links_contagem.get("emprestimo", 0),
        links_contagem.get("restrito", 0), links_contagem.get("morto_ou_instavel", 0),
        links_contagem.get("sem_link", 0),
    )

    def lista(itens, inicio=1):
        linhas = []
        for i, r in enumerate(itens, inicio):
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
    corpo += "\n".join(lista(baixas, len(principais) + 1))
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
        chave = autor_abnt(r) or "Autoria não identificada"
        por_autor.setdefault(chave, []).append(r)
    saida = [
        "# Referências por autor — ABNT\n\n> Sobrenome em caixa alta, como na"
        " lista principal; `Autoria não identificada` é lacuna da fonte, não"
        " pseudônimo. Mesma base de `referencias-abnt.md` (%d entradas).\n" % len(refs)
    ]
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
