"""Coleta metadados das referências do dossiê LeapSpace (Crossref + Unpaywall).

Gera dados/leapspace-refs.json com acesso aberto, idioma e veículo de cada DOI.
Respeita o ritmo de 1 requisição por vez, com pausa curta, e UA honesto.
Cache em dados/leapspace-meta.json é reaproveitado nas execuções seguintes.
"""
import io
import json
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request

import docx

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = r"C:\Users\teste\Downloads\AJP Brasil Leapspace.docx"
EXTRAS = os.path.join(RAIZ, "dados", "leapspace-extra-refs.json")
META = os.path.join(RAIZ, "dados", "leapspace-meta.json")
EMAIL = "colito2023@gmail.com"
UA = "finweejur/github artur colito"

# Referências específicas de cada eixo do panorama (ids do LeapSpace)
EIXOS_POR_ID = {
    "ajup": {"3", "35", "49", "50", "51", "52", "53", "54", "55", "61"},
    "direito-achado-na-rua": {"3", "55", "56", "57", "58", "59", "60", "61",
                              "62", "63", "64", "65", "66", "67"},
    "direito-insurgente": {"55", "68", "69", "70", "71", "72", "73", "74", "75",
                           "76", "77", "78", "79", "80", "81", "82", "83", "84",
                           "85", "86", "87"},
    "uso-tatico": {"55", "56", "68", "70", "99", "100", "101", "102", "103",
                   "104", "105", "106", "107", "108", "109", "110", "111",
                   "112", "113"},
    "positivismo-de-combate": {"88", "89", "90", "91", "92", "93", "94", "95",
                               "96", "97", "98"},
    "advocacia-popular": ({"3", "8", "35", "42", "43", "55", "58", "61"}
                          | {str(n) for n in range(114, 139)}),
    "pesquisa-socialmente-orientada": {"p%d" % n for n in range(1, 17)},
}

STOP_PT = {
    "o", "a", "os", "as", "de", "da", "do", "das", "dos", "e", "em", "para", "por",
    "com", "na", "no", "nas", "nos", "um", "uma", "ao", "à", "às", "aos", "sobre",
    "entre", "como", "não", "sem", "pela", "pelo", "que", "seu", "sua", "seus", "suas",
    "mais", "num", "numa",
}
STOP_ES = {
    "el", "la", "los", "las", "de", "del", "para", "por", "con", "en", "un", "una",
    "unos", "unas", "como", "que", "su", "sus", "más", "sin", "entre", "sobre", "al",
    "se", "y", "es", "son",
}


def norm(t):
    return unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode().lower()


def pega_doi(url):
    m = re.search(r"doi\.org/(10\.[^\s?#]+)", url or "")
    return m.group(1).rstrip(".,;") if m else ""


def do_docx():
    d = docx.Document(DOCX)
    refs, on = [], False
    for p in d.paragraphs:
        t = p.text.strip()
        if t.lower() == "references":
            on = True
            continue
        if on and t:
            m = re.search(r"https?://\S+", t)
            if not m:
                continue
            refs.append({"id": "", "titulo": t[: m.start()].strip(" ."),
                         "url": m.group(0).rstrip(".,;")})
    return refs


def do_extras():
    try:
        return json.load(io.open(EXTRAS, encoding="utf-8"))
    except FileNotFoundError:
        return []


def base():
    tudo, vistos = [], {}
    for r in do_extras() + do_docx():
        chave = (pega_doi(r["url"]) or r["url"]).lower().rstrip("/")
        if chave in vistos:
            if r.get("id") and not vistos[chave].get("id"):
                vistos[chave]["id"] = r["id"]
            continue
        item = {"id": r.get("id", ""), "titulo": r["titulo"], "url": r["url"]}
        vistos[chave] = item
        tudo.append(item)
    return tudo


def busca(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def consulta(doi, cache):
    dado = dict(cache.get(doi) or {})
    if dado.get("_cv") != 2:
        try:
            c = busca("https://api.crossref.org/works/%s?mailto=%s" % (
                urllib.parse.quote(doi, safe="/"), EMAIL))["message"]
            dado["idioma_crossref"] = (c.get("language") or "").lower()[:2]
            titulos = c.get("title") or []
            dado["titulo_original"] = (titulos[0] if titulos else "")[:400]
            dado["veiculo"] = (c.get("container-title") or [""])[0]
            dado["editora"] = c.get("publisher") or ""
            for campo in ("published-print", "published-online", "issued"):
                if c.get(campo, {}).get("date-parts"):
                    dado["ano"] = str(c[campo]["date-parts"][0][0])
                    break
            dado["_cv"] = 2
        except Exception as e:  # noqa: BLE001
            dado["erro_crossref"] = type(e).__name__
        time.sleep(0.35)
    if "aberto" not in dado:
        try:
            u = busca("https://api.unpaywall.org/v2/%s?email=%s" % (
                urllib.parse.quote(doi, safe="/"), EMAIL))
            dado["aberto"] = bool(u.get("is_oa"))
            dado["status_oa"] = u.get("oa_status") or ""
            local = u.get("best_oa_location") or {}
            dado["url_aberta"] = local.get("url") or ""
        except Exception as e:  # noqa: BLE001
            dado["erro_unpaywall"] = type(e).__name__
        time.sleep(0.35)
    cache[doi] = dado
    return dado


def detecta_idioma(texto):
    """Distingue português e espanhol pelo vocabulário e por marcas gráficas."""
    if not texto:
        return ""
    bruto = texto.lower()
    if "ñ" in bruto:
        return "es"
    tokens = set(re.findall(r"[a-zà-ÿ]+", norm(texto)))
    pt = len(tokens & STOP_PT)
    es = len(tokens & STOP_ES)
    if "ã" in bruto or "õ" in bruto or "ç" in bruto:
        pt += 2
    if pt >= 2 and pt >= es:
        return "pt"
    if es >= 2 and es > pt:
        return "es"
    return ""


def autores_e_ano(titulo):
    m = re.match(r"^(.*?\(\d{4}[a-z]?\))", titulo)
    return m.group(1).strip() if m else ""


def slug(texto):
    sem = unicodedata.normalize("NFD", texto or "")
    sem = "".join(c for c in sem if unicodedata.category(c) != "Mn")
    sem = re.sub(r"[^a-zA-Z0-9]+", "-", sem).strip("-").lower()
    return sem[:60] or "autor"


def autores_do_acervo():
    indice = json.load(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8"))
    mapa = {}
    for r in indice:
        nome = (r.get("autor") or "").strip()
        if not nome or len(nome) < 5:
            continue
        partes = norm(nome).replace("-", " ").split()
        if len(partes) < 2:
            continue
        chave = (partes[-1], partes[0][0])
        registro = mapa.setdefault(chave, {"nome": nome, "slug": slug(nome), "textos": 0})
        registro["textos"] += 1
    return mapa


def casa_autoria(titulo, mapa):
    trecho = autores_e_ano(titulo)
    if not trecho:
        return None
    trecho = re.sub(r"\(\d{4}[a-z]?\)", "", trecho)
    for bruto in re.split(r"[;]", trecho):
        bruto = bruto.strip(" .,")
        if not bruto:
            continue
        if "," in bruto:
            sobrenome, resto = bruto.split(",", 1)
            sobrenome = sobrenome.strip()
            inicial = re.sub(r"[^A-Za-zÀ-ÿ]", "", resto)[:1].lower()
        else:
            partes = norm(bruto).replace("-", " ").split()
            if len(partes) < 2:
                continue
            sobrenome, inicial = partes[-1], partes[0][0]
        chave = (norm(sobrenome).strip(), inicial)
        if chave in mapa:
            return mapa[chave]
    return None


def main():
    refs = base()
    cache = {}
    if os.path.exists(META):
        try:
            cache = json.load(io.open(META, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            cache = {}

    print("referências:", len(refs), "| DOIs:", sum(1 for r in refs if pega_doi(r["url"])))

    for i, r in enumerate(refs, 1):
        doi = pega_doi(r["url"])
        if not doi:
            continue
        consulta(doi, cache)
        if i % 20 == 0:
            json.dump(cache, io.open(META, "w", encoding="utf-8", newline="\n"),
                      ensure_ascii=False, indent=1)
            print("  ...", i)

    final = []
    mapa = autores_do_acervo()
    try:
        urls_docx = {r["url"].lower().rstrip("/") for r in do_docx()}
    except Exception:  # noqa: BLE001
        urls_docx = set()
    for r in refs:
        doi = pega_doi(r["url"])
        d = cache.get(doi, {}) if doi else {}
        original = d.get("titulo_original", "")
        idioma = (detecta_idioma(original) or d.get("idioma_crossref")
                  or detecta_idioma(r["titulo"]) or "en")
        aberto = d.get("aberto")
        if aberto is None:
            aberto = bool(re.search(r"scopus|scielo|revistas?\.|\.emnuvens", r["url"]))
        titulo = r["titulo"]
        if idioma == "pt" and original and norm(original)[:60] != norm(titulo)[:60]:
            prefixo = autores_e_ano(titulo)
            if prefixo:
                titulo = prefixo + " " + original.strip().rstrip(".") + "."
        autor = casa_autoria(r["titulo"], mapa)
        veiculo = d.get("veiculo", "")
        if veiculo:
            v = norm(veiculo).strip(" .")
            if v and norm(titulo).strip(" .").endswith(v):
                titulo = titulo[: len(titulo) - len(veiculo.strip(" ."))].rstrip(" .,;:")
        final.append({
            "id": r.get("id", ""),
            "titulo": titulo,
            "titulo_original": original,
            "url": r["url"],
            "doi": doi,
            "aberto": bool(aberto),
            "status_oa": d.get("status_oa", ""),
            "url_aberta": d.get("url_aberta", ""),
            "idioma": idioma,
            "veiculo": d.get("veiculo", ""),
            "ano": d.get("ano", ""),
            "acervo_autor": (autor or {}).get("nome", ""),
            "acervo_url": ("autor-%s.html" % autor["slug"]) if autor else "",
            "eixos": (["ajp-brasil"]
                      if r["url"].lower().rstrip("/") in urls_docx else [])
                     + [eixo for eixo, ids in EIXOS_POR_ID.items()
                        if r.get("id") in ids],
        })

    ordem_idioma = {"pt": 0, "es": 1}
    final.sort(key=lambda x: (
        not x["aberto"],
        ordem_idioma.get(x["idioma"], 2),
        not x["acervo_autor"],
        norm(x["titulo"]),
    ))

    json.dump(cache, io.open(META, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)
    json.dump(final, io.open(os.path.join(RAIZ, "dados", "leapspace-refs.json"),
                             "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)

    abertos = sum(1 for x in final if x["aberto"])
    pt = sum(1 for x in final if x["idioma"] == "pt")
    print("total %d | abertos %d | em português %d" % (len(final), abertos, pt))


if __name__ == "__main__":
    main()
