"""Rastreia artigos e obras de todos os autores do acervo AJP.

Fontes gratuitas, sem login, sem paywall:
  * OpenAlex   — trabalhos por autor
  * Crossref   — obras por nome de autor
  * Google Books — livros e coletâneas

Cada obra recebe pontuação de domínio (universo AJP: direito crítico,
movimentos sociais, educação popular...). Obras sem relação temática são
marcadas `relevante=False` para revisão, e não contam como achado.

Saída incremental (JSONL): dados/autores-artigos.jsonl

Uso:
    python etl/rastreia-autores.py --limite 5
    python etl/rastreia-autores.py
    python etl/rastreia-autores.py --slug ribas
"""
import argparse
import io
import json
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
SAIDA = os.path.join(RAIZ, "dados", "autores-artigos.jsonl")
UA = "finweejur/github artur colito (pesquisa de acervo; contato: finweejur@proton.me)"
MAILTO = "finweejur%40proton.me"

# apelidos/pseudônimos -> nome civil para busca acadêmica (chaves livres; a
# comparação em analisa() é feita normalizada dos dois lados).
ALIAS = {
    "o que eu não vi hoje? (Humberto Góes)": "Humberto Góes",
}

TERMOS_DOMINIO = [
    # português — direito e afins
    "direito", "jurídic", "justiça", "judici", "lei ", "legisla", "constitui",
    "estado", "cidadan", "democrac", "polític", "poder", "autoridade",
    "assessoria", "advocacia", "advoga", "defensoria", "promotoria", "juízo",
    "litígio", "processo", "tribunal", "norma", "doutrina", "dogmátic",
    "crítica", "teoria", "filosofia", "sociologia", "ciência política",
    "movimento", "ativismo", "mobilizaç", "manifestaç", "protesto", "greve",
    "sindical", "organizaç", "popular", "comunidade", "coletivo", "assembleia",
    "educacao popular", "educação popular", "formação", "pedagogi", "ensino",
    "alfabetiza", "conscientiza", "participaç", "autogest",
    "terra", "agrári", "campesin", "camponês", "agricult", "rural",
    "quilombola", "quilombo", "indígena", "indio", "aborígene",
    "moradia", "urbano", "cidade", "periferia", "favela", "ocupação",
    "barragem", "atingido", "água", "ambiental", "ecolog",
    "gênero", "genero", "mulher", "feminis", "femina", "machismo",
    "raça", "raca", "racial", "negro", "preto", "racismo", "discrimina",
    "intolerância", "religião", "religios", "candomblé", " umbanda",
    "saúde", "sus", "epidemia", "hiv", "droga", "antiproibicion",
    "menor", "criança", "adolescente", "jovem", "juventude",
    "violência", "tortura", "encarcera", "prisional", "penal", "criminolog",
    "abuso", "impunidad", "desaparecid", "ditadura", "memória",
    "globaliza", "neolibera", "capitalis", "imperial", "colônia", "colonial",
    "dependência", "subdesenvolvimento", "periferia mundial",
    "liberdade", "emancipa", "igualdade", "fraternidade",
    "utopia", "revolu", "socialis", "marx", "gramsci", "freire", "lyra",
    "achado na rua", "insurgente", "insurrei",
    "bolivar", "latino-americ", "mercosul", "brics",
    "constituinte", "plebiscit", "referend", "eleiç", "parlament",
    "representaç", "crise", "exceção", "golpe", "autoritar",
    "privatiza", "empresaria", "corporativa",
    "consumidor", "familia", "sucess", "contrato", "propriedade",
    "trabalho", "emprego", "precariz", "uberiz",
    "assistência", "benefício", "seguridade", "previdên",
    "refugiad", "migrante", "estrangeiro",
    "cultu", "folclore", "identidade", "alteridade",
    # inglês (obras comparadas)
    "law", "legal", "juris", "justice", "rights", "citizen", "democracy",
    "social movement", "populist", "critical legal", "legal pluralism",
    "insurgent", "emancipat", "subaltern", "decolonial", "postcolonial",
    "human rights", "land conflict", "housing", "slum", "urban",
    "gender", "feminis", "racial", "inequality", "poverty", "power",
    "politics", "political", "state", "constitution", "court", "litigation",
    "activism", "protest", "strike", "union", "organized", "collective",
    "education", "pedagog", "knowledge", "epistemolog", "methodology",
    "field", "peasant", "rural", "farm", "agriculture",
    "quilombo", "afro", "indigenous", "aboriginal",
    "water", "dam", "environment", "ecological",
    "memory", "dictatorship", "transition", "amnesty", "truth",
    "archive", "bibliotec", "bibliograf",
]


def norm(s):
    t = unicodedata.normalize("NFD", s or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\s]", " ", t).lower().strip()


def stop_tokens(tok):
    return tok in {"de", "da", "do", "das", "dos", "e", "a", "o", "as", "os",
                   "em", "no", "na", "nos", "nas", "por", "para", "com", "que",
                   "the", "of", "and", "in", "on", "for", "with", "a", "an"}


def tokens_importantes(nome):
    toks = [t for t in norm(nome).split() if not stop_tokens(t)]
    # descarta monogramas/iniciais ("A.", "F.") — nunca ajudam a casar nome completo
    toks = [t for t in toks if len(t) > 1]
    return toks


def get_json(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# ---------------------------------------------------------------------------
# fontes
# ---------------------------------------------------------------------------
def busca_openalex(nome):
    q = urllib.parse.quote(nome)
    url = ("https://api.openalex.org/authors?search=%s&per-page=8&mailto=%s" % (q, MAILTO))
    try:
        d = get_json(url)
    except Exception as e:
        return {"erro": str(e)[:200], "candidatos": [], "obras": []}
    cands = d.get("results", [])
    if not cands:
        return {"candidatos": [], "obras": []}
    escolhido, pontuacao = escolhe_autor(nome, cands)
    chosen_id = (escolhido or {}).get("id", "").split("/")[-1]
    if not chosen_id:
        return {"candidatos": [{"id": c.get("id", "").split("/")[-1],
                                "nome": c.get("display_name"),
                                "works": c.get("works_count")} for c in cands],
                "obras": [], "score": pontuacao}
    works = varre_openalex("filter=author.id:%s" % chosen_id)
    # taxa temática: mede se o perfil escolhido é realmente do universo AJP.
    # Se quase nada casa com o vocabulário do acervo, é provável homônimo.
    tot_obras = len(works) or 1
    rel_count = 0
    for w in works[:60]:
        tt = norm((w.get("title") or "") + " " + " ".join(str(x) for x in (w.get("keywords") or [])))
        if any(termo in tt for termo in TERMOS_FORTES):
            rel_count += 1
    taxa_tematica = round(rel_count / tot_obras, 2)
    obras = []
    for w in works:
        ano = extrai_ano(w)
        loc = w.get("primary_location") or {}
        loc_url = loc.get("landing_page_url")
        urls_pdf = [l.get("pdf_url") for l in (w.get("locations") or []) if l.get("pdf_url")]
        oa = (w.get("oa_info") or {}).get("is_oa")
        titulos_s = "; ".join([str(x) for x in (w.get("title_originals") or [])][:2])
        obras.append({
            "titulo": (w.get("title") or titulos_s or "").strip(),
            "ano": str(ano) if ano else "",
            "tipo": w.get("type") or "",
            "doi": w.get("doi") or "",
            "url": loc_url or (urls_pdf[0] if urls_pdf else ""),
            "oa": bool(oa),
            "fonte": "openalex",
            "origem_dados": "obra %s" % w.get("id", ""),
        })
    # se o autor escolhido NÃO bate bem com o nome procurado, marcamos tudo como
    # incerto — evita contaminar a lista com homônimos
    alvo_tokens = set(tokens_importantes(nome))
    disp_tokens = set(norm((escolhido or {}).get("display_name") or "").split())
    cobertura = len(alvo_tokens & disp_tokens) / max(len(alvo_tokens), 1)
    # exige que TODOS os tokens do buscado estejam no nome exibido (evita
    # "Assis Oliveira" -> "Francisco de Assis de Oliveira", p.ex.)
    todos_presentes = bool(alvo_tokens) and alvo_tokens.issubset(disp_tokens)
    nome_certeiro = (
        cobertura >= 0.6 and len(alvo_tokens - disp_tokens) <= 1 and todos_presentes
    )
    # um perfil só é confiável se as obras dele conversam com o acervo AJP
    tema_ok = taxa_tematica >= 0.5
    return {
        "autor_id": chosen_id,
        "autor_nome": (escolhido or {}).get("display_name"),
        "instituicao": ((escolhido or {}).get("institution") or {}).get("display_name"),
        "works_count": (escolhido or {}).get("works_count"),
        "score": round(pontuacao, 2),
        "cobertura_nome": round(cobertura, 2),
        "nome_certeiro": nome_certeiro,
        "taxa_tematica": taxa_tematica,
        "tema_ok": tema_ok,
        "revisar": pontuacao < 12 or not nome_certeiro or not tema_ok,
        "candidatos": [{"id": c.get("id", "").split("/")[-1],
                        "nome": c.get("display_name"),
                        "works": c.get("works_count")} for c in cands],
        "obras": obras,
    }


def extrai_ano(w):
    for k in ("primary_date", "published_on_date"):
        v = w.get(k)
        if isinstance(v, str) and len(v) >= 4 and v[:4].isdigit():
            return int(v[:4])
    dobj = w.get("date") or {}
    if isinstance(dobj, dict) and dobj.get("year"):
        return int(dobj["year"])
    for k in ("created_date", "updated_date"):
        v = w.get(k)
        if isinstance(v, str) and len(v) >= 4 and v[:4].isdigit():
            return int(v[:4])
    return None


def varre_openalex(filtro):
    base = "https://api.openalex.org/works?" + filtro + "&per-page=200&mailto=" + MAILTO
    cursor, total = None, []
    while True:
        url = base + ("&cursor=%s" % urllib.parse.quote(cursor) if cursor else "")
        try:
            d = get_json(url)
        except Exception as e:
            print("    [openalex] erro: %s" % str(e)[:120])
            break
        total.extend(d.get("results", []))
        meta = d.get("meta", {})
        nxt = meta.get("next_cursor")
        if isinstance(nxt, dict):
            nxt = nxt.get("value")
        if not nxt:
            break
        cursor = nxt
        time.sleep(0.4)
    return total


def escolhe_autor(nome_busca, candidatos):
    """Escolhe o candidato cujo nome contém TODOS os tokens importantes."""
    alvo = tokens_importantes(nome_busca)
    melhor, pontuacao = None, -1
    for c in candidatos:
        disp = norm(c.get("display_name") or "")
        disp_set = set(disp.split())
        inter = sum(1 for t in alvo if t in disp_set)
        # precisa bater a maioria dos tokens principais
        proporcao = inter / max(len(alvo), 1)
        score = inter * 4 + proporcao * 10
        # bônus para quem tem mais obras (pesquisador produtivo costuma ser o alvo)
        score += min(c.get("works_count") or 0, 60) / 6.0
        if score > pontuacao:
            melhor, pontuacao = c, score
    return melhor, pontuacao


def busca_crossref(nome):
    q = urllib.parse.quote(nome)
    base = ("https://api.crossref.org/works?query.author=" + q +
            "&rows=60&mailto=" + MAILTO)
    try:
        d = get_json(base)
    except Exception as e:
        return {"erro": str(e)[:150], "obras": []}
    itens = d["message"].get("items", [])
    obras = []
    alvo = tokens_importantes(nome)
    alvo_set = set(alvo)
    for it in itens:
        aut_match = False
        atestado = False
        for au in (it.get("author") or []):
            full = norm(((au.get("given") or "") + " " + (au.get("family") or "")).strip())
            fs = set(full.split())
            # exige TODOS os tokens importantes num único autor
            if alvo_set and alvo_set.issubset(fs):
                aut_match = True
                atestado = len(alvo) >= 2
                break
            # sobrenomes compostos curtos (ex.: "Ribas", "Maso") exigem apoio do
            # prenome completo informado na própria fonte
            if len(alvo) <= 2 and alvo_set.intersection(fs) == alvo_set:
                aut_match = True
                break
        if not aut_match:
            continue
        titulos = it.get("title") or []
        titulo = re.sub(r"<[^>]+>", "", (titulos[0] if titulos else "")).strip()
        if not titulo:
            continue
        ano = ""
        for campo in ("published-print", "published-online", "created"):
            dp = (it.get(campo) or {}).get("date-parts", [[]])[0]
            if dp and dp[0]:
                ano = str(dp[0]); break
        recursos = []
        res = it.get("resource", "")
        if isinstance(res, dict):
            res = res.get("URL") or ""
        if isinstance(res, str) and res:
            recursos.append(res)
        links_raw = it.get("link") or []
        if isinstance(links_raw, dict):
            links_raw = [links_raw]
        for l in links_raw:
            if isinstance(l, dict) and l.get("URL"):
                recursos.append(l["URL"])
            elif isinstance(l, str) and l:
                recursos.append(l)
        links_ext = [u for u in recursos if isinstance(u, str) and u.startswith("http")]
        obras.append({
            "titulo": titulo[:300],
            "ano": ano,
            "tipo": it.get("type", ""),
            "doi": it.get("DOI", ""),
            "url": links_ext[0] if links_ext else "",
            "editor": (it.get("publisher") or "")[:120],
            "fonte": "crossref",
            "origem_dados": it.get("DOI", ""),
            "autor_atestado": atestado,
        })
    return {"obras": obras}


def busca_google_books(nome):
    q = urllib.parse.quote('inauthor:"%s"' % nome)
    url = "https://www.google.com/books/feeds/volumes?q=%s&max-results=40" % q
    try:
        raw = urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60
        ).read().decode("utf-8", "replace")
    except Exception as e:
        return {"erro": str(e)[:150], "obras": []}
    import xml.etree.ElementTree as ET
    NS = {"a": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/terms"}
    root = ET.fromstring(raw)
    obras = []
    for entry in root.findall(".//a:entry", NS):
        titulo = ""
        for x in entry.findall("{http://www.w3.org/2005/Atom}title"):
            titulo = (x.text or "").strip(); break
        if not titulo:
            continue
        autores = [t.text for t in entry.findall("{http://purl.org/dc/terms}creator") if t.text]
        data_el = entry.find("{http://purl.org/dc/terms/date}")
        ano = (data_el.text if data_el is not None and data_el.text else "")[:4]
        ident = ""
        for l in entry.findall("{http://www.w3.org/2005/Atom}link"):
            href = l.get("href") or ""
            if "books?id=" in href:
                ident = href; break
        obras.append({
            "titulo": titulo[:250],
            "ano": ano,
            "tipo": "livro",
            "doi": "",
            "url": ident,
            "autores": autores[:6],
            "fonte": "google_books",
            "origem_dados": "",
        })
    return {"obras": obras}


# ---------------------------------------------------------------------------
# relevância temática
# ---------------------------------------------------------------------------
TERMOS_FORTES = {
    "direito", "jurídic", "justiça", "judici", "constitui", "cidadan",
    "democrac", "polític", "poder", "estado", "autoridade", "assessoria",
    "advocacia", "advoga", "defensoria", "litígio", "tribunal", "norma",
    "doutrina", "dogmátic", "crítica", "teoria", "filosofia", "sociologia",
    "movimento", "ativismo", "mobilizaç", "manifestaç", "protesto", "sindical",
    "popular", "comunidade", "coletivo", "assembleia", "educação popular",
    "pedagogi", "formação", "participaç", "autogest", "terra", "agrári",
    "campesin", "camponês", "quilombola", "quilombo", "indígena", "moradia",
    "urbano", "cidade", "periferia", "favela", "ocupação", "barragem",
    "atingido", "ambiental", "gênero", "genero", "mulher", "feminis",
    "raça", "racial", "negro", "racismo", "discrimina", "religião", "religios",
    "saúde", "criança", "adolescente", "juventude", "violência", "tortura",
    "encarcera", "penal", "criminolog", "impunidad", "ditadura", "memória",
    "globaliza", "neolibera", "capitalis", "imperial", "colônia", "colonial",
    "liberdade", "emancipa", "igualdade", "utopia", "revolu", "socialis",
    "marx", "gramsci", "freire", "lyra", "achado na rua", "insurgente",
    "insurrei", "latino-americ", "constituinte", "golpe", "autoritar",
    "trabalho", "emprego", "precariz", "refugiad", "migrante",
    "law", "legal", "juris", "justice", "rights", "citizen", "democracy",
    "social movement", "critical legal", "legal pluralism", "insurgent",
    "emancipat", "subaltern", "decolonial", "human rights", "land conflict",
    "housing", "slum", "gender", "feminis", "inequality", "poverty",
    "political", "constitution", "court", "litigation", "activism",
    "protest", "education", "pedagog", "epistemolog", "field", "peasant",
    "quilombo", "afro", "indigenous", "dictatorship", "archive",
}


def pontua_dominio(obra):
    txt = norm((obra.get("titulo") or "") + " " + (obra.get("tipo") or ""))
    hits_fortes, hits_fracos = [], []
    for termo in TERMOS_DOMINIO:
        if termo in txt:
            if termo in TERMOS_FORTES:
                hits_fortes.append(termo)
            else:
                hits_fracos.append(termo)
    distinct_fortes = len(set(hits_fortes))
    return distinct_fortes + len(set(hits_fracos)), sorted(set(hits_fortes))


def dedup(obras):
    vistos, out = set(), []
    for o in obras:
        chave = (re.sub(r"\W", "", norm(o.get("titulo")))[:80], o.get("ano"))
        if chave in vistos:
            continue
        vistos.add(chave)
        out.append(o)
    return out


def analisa(nome):
    t0 = time.time()
    # apelidos aplicados por igual nos dois lados (case-insensitive e sem pontuação)
    busca_key = norm(ALIAS.get(norm(nome), norm(nome)))
    nomes_norm = {norm(k): v for k, v in ALIAS.items()}
    nome_busca = nomes_norm.get(busca_key, nome) if busca_key else nome
    oa = busca_openalex(nome_busca)
    cr = busca_crossref(nome_busca)
    gb = busca_google_books(nome_busca)
    # confiabilidade do PAREAMENTO do perfil internacional
    perfil_robusto = bool(oa.get("nome_certeiro")) and bool(oa.get("tema_ok")) and not oa.get("revisar", True)

    # reavalia cada obra por DUAS vias independentes: autoria atestada na fonte
    # (Crossref devolve o nome do autor registrado) OU perfil OpenAlex robusto.
    obras = dedup((oa.get("obras") or []) + (cr.get("obras") or []) + (gb.get("obras") or []))
    confirmadas, revisao = [], []
    for o in obras:
        sc, hits_fortes = pontua_dominio(o)
        o["score_dominio"] = sc
        o["termos_encontrados"] = hits_fortes
        tematica = bool(hits_fortes)
        autoria_fonte = bool(o.get("autor_atestado"))
        if tematica and (autoria_fonte or perfil_robusto):
            confirmadas.append(o)
        elif tematica:
            revisao.append(o)
    chave = (lambda x: (-x["score_dominio"],
                        -(int(x["ano"]) if str(x.get("ano") or "").isdigit() else 9999)))
    confirmadas.sort(key=chave)
    revisao.sort(key=chave)
    return {
        "nome_busca": nome_busca,
        "openalex": {k: v for k, v in oa.items() if k != "obras"},
        "fontes": {
            "openalex_erros": oa.get("erro"),
            "crossref_total": len(cr.get("obras", [])),
            "books_total": len(gb.get("obras", [])),
        },
        "confirmadas": confirmadas,
        "revisao": revisao,
        "total_obras": len(obras),
        "relevantes": len(confirmadas) + len(revisao),
        "nome_robusto": perfil_robusto,
        "segundos": round(time.time() - t0, 1),
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--slug", default="", help="busca por substring do nome")
    ap.add_argument("--saida", default=SAIDA)
    args = ap.parse_args()

    idx = json.load(io.open(INDICE, encoding="utf-8"))
    vistos_nomes, nomes = set(), []
    for r in idx:
        nm = (r.get("autor") or "").strip()
        if nm and nm not in vistos_nomes and nm != "Redação da Página":
            vistos_nomes.add(nm); nomes.append(nm)
    fila = nomes
    if args.slug:
        s = args.slug.lower()
        fila = [n for n in nomes if s in n.lower()]
    if args.limite:
        fila = fila[:args.limite]

    feitos = set()
    if os.path.exists(args.saida):
        for linha in io.open(args.saida, encoding="utf-8"):
            try:
                feitos.add(json.loads(linha)["nome"])
            except Exception:
                pass

    print("autores:", len(fila), "| já feitos:", len(feitos))
    erros = 0
    for i, nome in enumerate(fila, 1):
        if nome in feitos:
            continue
        try:
            res = analisa(nome)
        except Exception as e:
            erros += 1
            print("[%d/%d] %s ERRO %s" % (i, len(fila), nome[:40], str(e)[:120]))
            continue
        reg = {
            "nome": nome,
            "gerado_em": datetime.now().isoformat(timespec="seconds"),
            "nome_busca": res["nome_busca"],
            "openalex_meta": res["openalex"],
            "fontes_result": res["fontes"],
            "total_obras": res["total_obras"],
            "confirmadas": len(res["confirmadas"]),
            "revisao_count": len(res["revisao"]),
            "nome_robusto": res["nome_robusto"],
            "detalhe": res,
        }
        with io.open(args.saida, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
        print("[%d/%d] %-40s tot=%d rel=%d (%ss)" % (
            i, len(fila), nome[:40], res["total_obras"], res["relevantes"], res["segundos"]))
        time.sleep(0.6)
    print("terminou. erros:", erros)


if __name__ == "__main__":
    main()
