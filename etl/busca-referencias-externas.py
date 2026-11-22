"""Completa autoria, ano e imprenta das referências por busca externa gratuita.

Fontes: Google Books (feed GData, sem chave), Crossref (artigos) e Internet
Archive (livros digitalizados). Sem login, sem API paga, sem paywall.
User-Agent `finweejur/github artur colito`, 1,5 s entre requisições.

O script **não inventa**: só aceita candidato com título muito parecido e, se
já houver autor, com sobrenome compatível. Tudo que é aceito guarda a
evidência (`fonte_dado`, `evidencia_url`, `match_titulo`).

Uso:
    python etl/busca-referencias-externas.py            # consulta e grava candidatas
    python etl/busca-referencias-externas.py --aplicar  # grava também em referencias.json
    python etl/busca-referencias-externas.py --limite 20
"""
import argparse
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
CACHE = os.path.join(RAIZ, "dados", "referencias-externas.json")
UA = "finweejur/github artur colito"
PAUSA = 1.5

NS = {
    "a": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/terms",
    "openSearch": "http://a9.com/-/spec/opensearchrss/1.0/",
}

TIPOS = {"livro", "artigo", "capitulo", "tese", "dissertacao", "monografia",
         "relatorio"}

PARADAS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "para",
    "por", "com", "um", "uma", "ao", "aos", "na", "no", "nas", "nos", "the",
    "of", "and", "in", "on", "to", "for", "la", "el", "los", "las", "del",
}


def sem_acento(t):
    return unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode()


def tokens(t):
    return [x for x in re.findall(r"[a-z0-9]+", sem_acento(t).lower()) if x not in PARADAS]


def limpa_titulo(t):
    t = re.sub(r"\*\*|__|`", "", t or "")
    t = re.sub(r"^\[\d+\]\s*", "", t)
    t = re.sub(r"\s*\((?:19|20)\d{2}\)\s*$", "", t)
    t = re.sub(r",\s*(?:19|20)\d{2}\s*$", "", t)
    t = re.sub(r"\.\s*\d+\s*(?:ed|Ed)\.?.*$", "", t)
    t = re.sub(r",\s*\d+\s*(?:ed|Ed)\.?.*$", "", t)
    t = re.sub(r"\s*\[(?:Mimeo|mimeo|No prelo)\]\s*$", "", t)
    t = t.strip(" .,;:-\"'“”")
    return re.sub(r"\s+", " ", t)


def consulta_google(titulo):
    t = limpa_titulo(titulo)
    palavras = t.split()
    if len(palavras) > 9:
        t = " ".join(palavras[:9])
    if len(t) <= 55:
        return 'intitle:"%s"' % t.replace('"', "")
    return " ".join(palavras[:8])


def http(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def google_books(titulo):
    q = consulta_google(titulo)
    url = "https://books.google.com/books/feeds/volumes?q=" + urllib.parse.quote(q)
    try:
        raiz = ET.fromstring(http(url))
    except Exception as e:
        return [], "erro: %s" % str(e)[:120]
    saida = []
    for e in raiz.findall("a:entry", NS)[:8]:
        titulo_r = e.findtext("dc:title", namespaces=NS) or ""
        autores = [x.text.strip() for x in e.findall("dc:creator", NS) if x.text]
        data_r = e.findtext("dc:date", namespaces=NS) or ""
        editora = e.findtext("dc:publisher", namespaces=NS) or ""
        ident = ""
        for l in e.findall("a:link", NS):
            href = l.get("href") or ""
            m = re.search(r"[?&]id=([^&]+)", href)
            if m:
                ident = m.group(1)
                break
        saida.append({
            "fonte": "google_books",
            "titulo": titulo_r,
            "autores": autores,
            "ano": (re.match(r"(\d{4})", data_r).group(1) if re.match(r"(\d{4})", data_r) else ""),
            "editora": editora,
            "url": ("https://books.google.com/books?id=%s" % ident) if ident else "",
        })
    total = raiz.findtext("openSearch:totalResults", namespaces=NS) or "0"
    return saida, "ok (%s)" % total


def crossref(titulo):
    q = urllib.parse.quote(limpa_titulo(titulo))
    url = (
        "https://api.crossref.org/works?query.bibliographic=%s&rows=5"
        "&select=title,author,issued,container-title,publisher,URL,DOI" % q
    )
    try:
        dados = json.loads(http(url).decode("utf-8", "replace"))
    except Exception as e:
        return [], "erro: %s" % str(e)[:120]
    saida = []
    for it in dados.get("message", {}).get("items", []):
        autores = []
        for a in it.get("author") or []:
            nome = " ".join(x for x in (a.get("given"), a.get("family")) if x).strip()
            if nome:
                autores.append(nome)
        partes = (it.get("issued") or {}).get("date-parts") or []
        ano = str(partes[0][0]) if partes and partes[0] and partes[0][0] else ""
        saida.append({
            "fonte": "crossref",
            "titulo": " ".join(it.get("title") or []),
            "autores": autores,
            "ano": ano,
            "editora": it.get("publisher") or "",
            "veiculo": " ".join(it.get("container-title") or []),
            "url": ("https://doi.org/%s" % it["DOI"]) if it.get("DOI") else (it.get("URL") or ""),
        })
    return saida, "ok"


def openalex(titulo):
    """OpenAlex: artigos, teses e livros com DOI/coletânea, sem chave."""
    q = urllib.parse.quote(limpa_titulo(titulo))
    url = "https://api.openalex.org/works?search=%s&per-page=5" % q
    try:
        dados = json.loads(http(url).decode("utf-8", "replace"))
    except Exception as e:
        return [], "erro: %s" % str(e)[:120]
    saida = []
    for w in dados.get("results") or []:
        autores = [
            a.get("author", {}).get("display_name")
            for a in (w.get("authorships") or [])
            if a.get("author", {}).get("display_name")
        ]
        local = w.get("primary_location") or {}
        fonte_nome = (local.get("source") or {}).get("display_name") or ""
        url_item = w.get("doi") or local.get("landing_page_url") or ""
        saida.append({
            "fonte": "openalex",
            "titulo": w.get("display_name") or w.get("title") or "",
            "autores": autores,
            "ano": str(w.get("publication_year") or ""),
            "editora": "",
            "veiculo": fonte_nome,
            "url": url_item,
        })
    return saida, "ok (%s)" % (dados.get("meta") or {}).get("count", "?")


def internet_archive(titulo):
    q = urllib.parse.quote('title:"%s"' % limpa_titulo(titulo).replace('"', ""))
    url = (
        "https://archive.org/advancedsearch.php?q=%s"
        "&fl%%5B%%5D=identifier&fl%%5B%%5D=title&fl%%5B%%5D=creator"
        "&fl%%5B%%5D=year&fl%%5B%%5D=publisher&rows=5&output=json" % q
    )
    try:
        dados = json.loads(http(url).decode("utf-8", "replace"))
    except Exception as e:
        return [], "erro: %s" % str(e)[:120]
    saida = []
    for d in dados.get("response", {}).get("docs", []):
        criadores = d.get("creator") or []
        if isinstance(criadores, str):
            criadores = [criadores]
        saida.append({
            "fonte": "internet_archive",
            "titulo": d.get("title") if isinstance(d.get("title"), str) else " ".join(d.get("title") or []),
            "autores": criadores,
            "ano": str(d.get("year") or ""),
            "editora": d.get("publisher") if isinstance(d.get("publisher"), str) else " ".join(d.get("publisher") or []),
            "url": "https://archive.org/details/%s" % d.get("identifier", ""),
        })
    return saida, "ok"


def semelhanca(titulo_ref, titulo_res):
    """Fração dos tokens da referência presentes no resultado.

    Compara o título inteiro e o título principal (antes dos dois-pontos),
    porque catálogos costumam registrar só a primeira parte.
    """
    b = set(tokens(titulo_res))
    if not b:
        return 0.0
    inteiro = limpa_titulo(titulo_ref)
    principal = inteiro.split(":")[0]

    candidato_principal = limpa_titulo(titulo_res).split(":")[0]

    def f1(variante, alvo):
        a = set(tokens(variante))
        if not a:
            return 0.0
        inter = len(a & alvo)
        if not inter:
            return 0.0
        precisao = inter / len(a)
        recall = inter / len(alvo)
        return 2 * precisao * recall / (precisao + recall)

    # F1 simétrico: evita aceitar obra diferente que só repete as mesmas
    # palavras do título (ex.: "assessoria jurídica popular e direitos humanos").
    notas = [
        f1(rv, alvo)
        for rv in (inteiro, principal)
        for alvo in (b, set(tokens(candidato_principal)))
        if alvo
    ]
    return max(notas) if notas else 0.0


def sobrenome(nome):
    nome = limpa_titulo(nome)
    n = sem_acento(nome).upper()
    if "," in n:
        return n.split(",")[0].strip()
    partes = [p for p in re.split(r"\s+", n) if p]
    return partes[-1] if partes else ""


def autor_combina(autor_ref, candidatos):
    alvo = sobrenome(autor_ref)
    if not alvo:
        return True
    for c in candidatos:
        if alvo and alvo in sem_acento(c).upper():
            return True
    return False


def escolhe(ref, candidatos, exigencia):
    melhor = None
    for c in candidatos:
        nota = semelhanca(ref.get("titulo"), c.get("titulo") or "")
        if nota < exigencia:
            continue
        if ref.get("autor") and not autor_combina(ref["autor"], c.get("autores") or []):
            continue
        if not c.get("autores") and not (ref.get("autor") or "").strip():
            continue  # sem autor no resultado, não há o que completar
        c = dict(c)
        c["match_titulo"] = round(nota, 3)
        if melhor is None or c["match_titulo"] > melhor["match_titulo"]:
            melhor = c
    return melhor


def falta(r):
    # Só vale a pena buscar o que muda a citação: autoria e ano. Imprenta
    # ausente vira [s.n.] e não justifica consulta externa.
    return (not (r.get("autor") or "").strip() or not r.get("ano"))


def alvo(r):
    if r.get("tipo") not in TIPOS:
        return False
    if not falta(r):
        return False
    if "post de blogue" in (r.get("motivo") or ""):
        return False
    if len(limpa_titulo(r.get("titulo") or "")) < 8:
        return False
    if (r.get("titulo") or "").startswith(("http", "www.", "Por ")):
        return False
    return True


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--refazer", action="store_true")
    args = ap.parse_args()

    dados = json.load(io.open(REF, encoding="utf-8"))
    refs = dados["referencias"]
    cache = {}
    if os.path.exists(CACHE) and not args.refazer:
        cache = json.load(io.open(CACHE, encoding="utf-8"))

    fila = [r for r in refs if alvo(r)]
    if args.limite:
        fila = fila[: args.limite]
    print("referências com lacuna:", len(fila))

    consultas = 0
    for i, r in enumerate(fila, 1):
        rid = r.get("id")
        if rid in cache and cache[rid].get("status") == "ok" and not args.refazer:
            continue
        resultados = []
        log = []
        for funcao in (google_books, openalex, internet_archive):
            achados, estado = funcao(r.get("titulo"))
            consultas += 1
            log.append("%s: %s" % (funcao.__name__, estado))
            resultados.extend(achados)
            time.sleep(PAUSA)
        if not (r.get("autor") or "").strip() or not r.get("ano"):
            achados, estado = crossref(r.get("titulo"))
            consultas += 1
            log.append("crossref: %s" % estado)
            resultados.extend(achados)
            time.sleep(PAUSA)

        exigencia = 0.93 if not (r.get("autor") or "").strip() else 0.8
        melhor = escolhe(r, resultados, exigencia)
        cache[rid] = {
            "status": "ok" if melhor else "sem_match",
            "consulta": consulta_google(r.get("titulo")),
            "log": log,
            "candidato": melhor,
            "total_resultados": len(resultados),
            "verificado_em": date.today().isoformat(),
        }
        if melhor:
            print("[%d/%d] %s -> %s" % (
                i, len(fila), limpa_titulo(r.get("titulo"))[:55],
                (melhor.get("autores") or ["?"])[0] + " " + (melhor.get("ano") or "")))
        elif i % 10 == 0:
            print("[%d/%d] sem match até aqui" % (i, len(fila)))
        if i % 5 == 0:
            json.dump(cache, io.open(CACHE, "w", encoding="utf-8", newline="\n"),
                      ensure_ascii=False, indent=1)

    json.dump(cache, io.open(CACHE, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)

    aceitos = [v for v in cache.values() if v.get("status") == "ok"]
    print("consultas HTTP:", consultas, "| aceitos:", len(aceitos),
          "| sem match:", len(cache) - len(aceitos))

    if not args.aplicar:
        print("candidatas em", CACHE)
        return

    aplicados = 0
    for r in refs:
        c = (cache.get(r.get("id")) or {}).get("candidato")
        if not c:
            continue
        mudou = False
        if not (r.get("autor") or "").strip() and c.get("autores"):
            r["autor"] = c["autores"][0]
            r["autor_tipo"] = "pessoal"
            r["autor_fonte"] = c.get("fonte")
            r["evidencia_url"] = c.get("url") or ""
            mudou = True
        if not r.get("ano") and c.get("ano"):
            r["ano"] = c["ano"]
            r["ano_fonte"] = c.get("fonte")
            mudou = True
        if not (r.get("veiculo") or "").strip():
            veiculo = c.get("veiculo") or c.get("editora") or ""
            if veiculo:
                r["veiculo"] = veiculo
                r["veiculo_fonte"] = c.get("fonte")
                mudou = True
        if not mudou:
            continue
        r["match_titulo"] = c.get("match_titulo")
        r["dados_externos"] = c.get("fonte")
        if not r.get("url") and c.get("url"):
            r["url"] = c["url"]
            r["url_fonte_dado"] = c.get("fonte")
        tem_ano = bool(r.get("ano"))
        tem_imprenta = bool((r.get("veiculo") or "").strip())
        if r.get("autor") and tem_ano and tem_imprenta:
            r["confianca"] = "alta"
        elif r.get("autor") and tem_ano:
            r["confianca"] = "media"
        r["motivo"] = (r.get("motivo") or "") + "; completado por busca externa"
        aplicados += 1

    json.dump(dados, io.open(REF, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)
    print("referências completadas:", aplicados)


if __name__ == "__main__":
    main()
