"""Classifica os 790 textos por temas transversais (filtros do Blog).

Os temas são independentes das cinco seções: um texto sobre Belo Monte entra em
"Barragens", "Socioambiental" e "Povos indígenas", sem deixar de ser da seção
Movimentos sociais.

Para não estourar (termos comuns como "trabalho"), cada tema declara o escopo:
  * curto — título + resumo + palavras-chave;
  * longo — também o corpo do texto (temas específicos: barragem, mineração...).

Saída: dados/temas-blog.json
"""
import html
import io
import json
import os
import re
import unicodedata
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
SAIDA = os.path.join(RAIZ, "dados", "temas-blog.json")

# (slug, rótulo, escopo, padrões)
TEMAS = [
    ("terra", "Luta pela terra", "curto", [
        r"reforma agraria", r"questao agraria", r"sem[- ]terra", r"\bmst\b",
        r"assentament", r"acampament", r"latifundi", r"agrari[ao]s?",
        r"posseir", r"desapropriac", r"luta pela terra", r"trabalhadores rurais",
        r"campesin", r"agricultura familiar",
    ]),
    ("moradia", "Moradia", "curto", [
        r"moradia", r"habitac", r"despejo", r"sem[- ]teto", r"cortico",
        r"ocupac(ao|oes) (urbana|de imovel|de terra)", r"favela",
        r"estatuto da cidade", r"aluguel", r"direito a cidade",
        r"reintegracao de posse", r"remocao de famílias|remocao de familias",
    ]),
    ("barragens", "Barragens", "longo", [
        r"barrage", r"hidreletr", r"usina hidreletr", r"belo monte",
        r"atingid[oa]s? por barrage", r"rompimento", r"rio doce", r"samarco",
        r"brumadinho", r"itaparica", r"sobradinho", r"tucurui",
        r"barragem de", r"reservatorio",
    ]),
    ("socioambiental", "Socioambiental", "longo", [
        r"socioambiental", r"meio ambiente", r"ecolog", r"ambiental",
        r"mudanca do clima|mudancas climaticas", r"biodivers", r"agrotoxico",
        r"desmatament", r"poluic", r"contaminac", r"justica ambiental",
        r"conflito ambiental", r"licenciamento ambiental",
    ]),
    ("mineracao", "Mineração", "longo", [
        r"minerac", r"garimpo", r"minerio", r"mineradora", r"samarco",
        r"brumadinho", r"bauxita", r"carajas", r"manganes",
        r"companhia vale", r"vale do rio doce", r"empreendimento miner",
        r"extracao mineral",
    ]),
    ("indigenas", "Povos indígenas e originários", "longo", [
        r"indigena", r"originari", r"aldeia", r"funai", r"demarcac",
        r"guarani", r"kaingang", r"xavante", r"yanomami", r"munduruku",
        r"tupinamba", r"povos originarios", r"terras indigenas", r"pajé|paje",
    ]),
    ("quilombola", "Quilombolas", "curto", [
        r"quilombola", r"quilombo", r"remanescent", r"comunidades tradicionais",
    ]),
    ("racismo", "Racismo", "longo", [
        r"racismo", r"racista", r"branquitude", r"genocidio da juventude negra",
        r"discriminac.*racial", r"populacao negra", r"movimento negro",
        r"negritude", r"cotas raciais",
    ]),
    ("mulheres", "Mulheres e gênero", "curto", [
        r"mulher", r"feminis", r"genero", r"machismo", r"patriarcado",
        r"8 de marco", r"violencia domestica", r"direitos das marias",
        r"igualdade de genero",
    ]),
    ("lgbt", "LGBTQIA+", "curto", [
        r"lgbt", r"homossex", r"travesti", r"transexual", r"transgener",
        r"diversidade sexual", r"orientacao sexual", r"identidade de genero",
    ]),
    ("trabalho", "Trabalho", "curto", [
        r"trabalhador", r"sindical", r"greve", r"uberiz", r"precariz",
        r"terceiriz", r"\bclt\b", r"reforma trabalhista", r"desemprego",
        r"direitos trabalhistas", r"mundo do trabalho",
    ]),
    ("ditadura", "Ditadura e memória", "curto", [
        r"ditadura", r"golpe (de|militar)", r"anistia", r"tortura",
        r"comissao da verdade", r"regime militar", r"ditadura militar",
        r"memoria da ditadura", r"1964",
    ]),
    ("criminalizacao", "Criminalização", "curto", [
        r"criminalizac", r"encarcera", r"prisao", r"violencia policial",
        r"execucao sumaria", r"abolicionismo penal", r"seletividade penal",
        r"mandado de busca", r"presos politicos",
    ]),
    ("educacao", "Educação e formação", "curto", [
        r"educacao popular", r"educacao juridica", r"escola", r"universidade",
        r"ensino juridico", r"estudant", r"\benem\b", r"cotas?",
        r"formacao juridica", r"pedagogia", r"extensao universitaria",
    ]),
    ("saude", "Saúde", "longo", [
        r"\bsus\b", r"saude publica", r"epidemia", r"pandemia", r"hospital",
        r"medicament", r"saude mental", r"vacina",
    ]),
    ("cidade", "Cidade e periferia", "curto", [
        r"cidade", r"urbano", r"periferia", r"metro", r"transporte",
        r"mobilidade", r"urbanizac", r"metroviari", r"onibus",
    ]),
    ("agua", "Água", "curto", [
        r"\bagua\b", r"bacia hidrografica", r"saneamento", r"nascente",
        r"aquifero", r"abastecimento", r"rio sao francisco", r"rio doce",
        r"recurso hidrico",
    ]),
    ("comunicacao", "Comunicação", "curto", [
        r"comunicac", r"midia", r"imprensa", r"jornal", r"radio",
        r"internet", r"redes sociais", r"liberdade de expressao",
    ]),
    ("assessoria", "Assessoria e advocacia popular", "curto", [
        r"assessoria juridica", r"\bajup\b", r"advocacia popular",
        r"advogad[oa] popular", r"pratica juridica", r"assistencia juridica",
        r"defensoria publica",
    ]),
    ("teoria", "Teoria crítica e direito", "curto", [
        r"direito achado na rua", r"direito insurgente", r"pluralismo juridico",
        r"teoria critica", r"marxis", r"pachukanis", r"lyra filho",
        r"critica do direito", r"filosofia do direito",
    ]),
    ("religiao", "Religiosidade", "curto", [
        r"religia", r"igreja", r"candomble", r"umbanda", r"espiritual",
        r"teologia", r"catolic", r"evangelic", r"pastoral",
    ]),
    ("arte", "Arte e cultura", "curto", [
        r"poesia", r"poema", r"musica", r"cinema", r"teatro", r"literatura",
        r"\barte\b", r"cultura", r"documentario", r"fotografia",
    ]),
    ("migracao", "Migração", "curto", [
        r"migra", r"imigra", r"refugiad", r"estrangeir", r"haitian",
        r"bolivian", r"fronteira",
    ]),
    ("infancia", "Infância e juventude", "curto", [
        r"crianc", r"adolescent", r"infancia", r"juvenil", r"juventude",
        r"jovens?",
    ]),
    ("alimentacao", "Alimentação", "curto", [
        r"alimentac", r"fome", r"agroecolog", r"soberania alimentar",
        r"transgenic", r"agricultura",
    ]),
]

RE = [(s, r, esc, [re.compile(p) for p in pats]) for s, r, esc, pats in TEMAS]


def norm(s):
    t = unicodedata.normalize("NFD", s or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t).lower()


def texto_post(slug):
    """Corpo do texto, sem cabeçalho, ficha, navegação nem rodapé."""
    p = os.path.join(RAIZ, slug + ".html")
    if not os.path.exists(p):
        return ""
    bruto = io.open(p, encoding="utf-8").read()
    m = re.search(r"<article\b[^>]*>(.*?)</article>", bruto, re.S)
    if not m:
        return ""
    corpo = m.group(1)
    # corta a ficha de origem (fica antes do fim do header do artigo)
    if "</header>" in corpo:
        corpo = corpo.split("</header>", 1)[1]
    corpo = re.sub(r"<script.*?</script>|<style.*?</style>", " ", corpo, flags=re.S)
    corpo = re.sub(r"<nav\b.*?</nav>", " ", corpo, flags=re.S)
    corpo = re.sub(r"<figcaption\b.*?</figcaption>", " ", corpo, flags=re.S)
    corpo = re.sub(r"<dl\b[^>]*ficha[^>]*>.*?</dl>", " ", corpo, flags=re.S)
    corpo = re.sub(r'<section class="compartilhar".*?</section>', " ", corpo, flags=re.S)
    corpo = re.sub(r"<[^>]+>", " ", corpo)
    return norm(html.unescape(corpo))


idx = json.load(io.open(INDICE, encoding="utf-8"))
por_slug = {}
cont = Counter()
for r in idx:
    slug = r.get("slug")
    if not slug:
        continue
    # palavras-chave automáticas são ruidosas: ficam fora do casamento
    curto = norm(" ".join([r.get("titulo") or "", r.get("resumo") or ""]))
    corpo = None
    achados = []
    for slug_tema, rotulo, escopo, regs in RE:
        bate = any(rx.search(curto) for rx in regs)
        if not bate and escopo == "longo":
            if corpo is None:
                corpo = texto_post(slug)
            # no corpo, exige repetição: menção solta em bibliografia não conta
            bate = any(len(rx.findall(corpo)) >= 2 for rx in regs)
        if bate:
            achados.append(slug_tema)
            cont[slug_tema] += 1
    por_slug[slug] = achados

temas = [{"slug": s, "rotulo": r, "total": cont[s]} for s, r, _, _ in TEMAS if cont[s] > 0]
temas.sort(key=lambda x: -x["total"])
sem_tema = sum(1 for v in por_slug.values() if not v)

json.dump({"gerado_em": "2026-11-23", "temas": temas, "por_slug": por_slug},
          io.open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── marcação das páginas ───────────────────────────────────────────────────
# Chips fixos (os temas que o dono pediu e os mais fortes) + select com o resto.
CHIPS = ["terra", "moradia", "barragens", "socioambiental", "mineracao",
         "indigenas", "quilombola", "racismo", "mulheres", "trabalho",
         "ditadura", "criminalizacao"]
MIN_CHIP = 6  # expõe tema com mais de 5 textos
rotulos = {t["slug"]: t["rotulo"] for t in temas}
totais = {t["slug"]: t["total"] for t in temas}


def chips_html():
    botoes = ['<button type="button" class="chip-f" data-tema-f="" aria-pressed="true">Todos os temas</button>']
    for slug in CHIPS:
        if totais.get(slug, 0) < MIN_CHIP:
            continue
        botoes.append('<button type="button" class="chip-f" data-tema-f="%s" aria-pressed="false">%s</button>'
                      % (slug, rotulos[slug]))
    grupo = ('<div class="fita__tipos fita__temas" role="group" aria-label="Tema do texto">%s</div>'
             % "".join(botoes))
    # select com os demais temas
    outros = [t for t in temas if t["slug"] not in CHIPS and t["total"] >= MIN_CHIP]
    opcoes = "".join('<option value="%s">%s (%d)</option>' % (t["slug"], t["rotulo"], t["total"])
                     for t in outros)
    select = ('<label class="sr-only" for="f-tema">Tema</label>'
              '<select id="f-tema" data-tema-select><option value="">Mais temas…</option>%s</select>'
              % opcoes)
    return grupo, select


def marca_pagina(f):
    p = os.path.join(RAIZ, f)
    if not os.path.exists(p):
        return 0
    t = io.open(p, encoding="utf-8").read()

    # remove a versão anterior dos controles de tema (permite reexecutar)
    t = re.sub(r'\s*<div class="fita__tipos fita__temas"[^>]*>.*?</div>', "", t, flags=re.S)
    t = re.sub(r'\s*<label class="sr-only" for="f-tema">Tema</label>'
               r'<select id="f-tema" data-tema-select>.*?</select>', "", t, flags=re.S)

    marcados = 0

    def troca(m):
        nonlocal marcados
        tag, corpo = m.group(1), m.group(2)
        if "data-tema-livre=" in tag:
            return m.group(0)
        h = re.search(r'class="[^"]*item__link[^"]*" href="([^"]+)\.html"', corpo)
        if not h:
            return m.group(0)
        temas_item = por_slug.get(h.group(1), [])
        if not temas_item:
            return m.group(0)
        marcados += 1
        return tag[:-1] + ' data-tema-livre="%s">%s' % (" ".join(temas_item), corpo)

    t = re.sub(r'(<li class="item"[^>]*>)(.*?</li>)', troca, t, flags=re.S)

    grupo, select = chips_html()
    m = re.search(r'<div class="fita__tipos"[^>]*>.*?</div>', t, re.S)
    if m:
        t = t[:m.end()] + "\n        " + grupo + "\n        " + select + t[m.end():]
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    return marcados


for pagina in ("blog.html", "acervo.html"):
    print("marcados em %s: %d" % (pagina, marca_pagina(pagina)))

sem_tema = sum(1 for v in por_slug.values() if not v)
print("textos:", len(por_slug), "| sem tema:", sem_tema)
for t in temas:
    print("  %-36s %3d" % (t["rotulo"], t["total"]))
