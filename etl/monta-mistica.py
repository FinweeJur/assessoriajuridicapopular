"""Monta a página da mística com textos integrais, memória cultural, poesia e calendário.

A página funciona como hub de cultura de resistência:

1. card “Mística do dia” (mesmo componente da home);
2. texto completo da equipe do 3º Acampamento do Levante (2023);
3. texto completo de Ademar Bogo, “A mística: parte da vida e da luta”;
4. memória e cultura: homenagens, crônicas, arte e datas que a rede celebra;
5. “Poesia crítica do direito” + todas as poesias do portal;
6. calendário histórico dos trabalhadores.

O script preserva o topo, o rodapé, o rádio e os scripts da página atual:
troca apenas o miolo do `<article>` e insere o card inicial. Assim um rebuild
não perde o que já foi padronizado no restante do site.
"""
import html
import importlib.util
import io
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = os.path.join(RAIZ, "fontes-textos")
POEMAS = os.path.join(RAIZ, "dados", "poemas.json")
CALENDARIO = os.path.join(RAIZ, "dados", "calendario.json")
INDICE = os.path.join(RAIZ, "_indice.json")
PAGINA = os.path.join(RAIZ, "mistica.html")

DOC_MISTICA = (
    "https://docs.google.com/document/d/"
    "1hxF-AgZYoka9yU0PLZ0MDCqWvpGq0UFnthlDXSP1W_w/edit"
)
DOC_BOGO = (
    "https://docs.google.com/document/d/"
    "1RMnMFcnBsUKNji-1z7j1jH9dNulNUSkG/edit"
)

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def esc(t):
    return html.escape(str(t or ""), quote=False)


def sem_acento(t):
    return unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode()


def blocos(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        texto = f.read().lstrip("\ufeff").replace("\r\n", "\n")
    partes = [re.sub(r"[ \t]+", " ", p).strip() for p in re.split(r"\n\s*\n", texto)]
    partes = [p for p in partes if p]
    if len(partes) < 3:
        partes = [re.sub(r"[ \t]+", " ", p).strip() for p in texto.split("\n")]
        partes = [p for p in partes if p]
    return partes


TITULO_RE = re.compile(r"^(\d+\.\s+)?[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9 ,.ºª\-—:()]{8,90}$")


def texto_integral(partes):
    """Parágrafos, subtítulos e listas do texto original, sem reescrever."""
    saida = []
    lista = []

    def fecha_lista():
        if lista:
            saida.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in lista))
            lista.clear()

    for p in partes:
        limpo = p.strip()
        if not limpo or re.fullmatch(r"p[áa]g(ina)?", limpo, re.I):
            continue
        linhas = limpo.split("\n")
        tem_marcador = any(l.strip().startswith(("* ", "- ")) for l in linhas)
        if tem_marcador:
            for linha in linhas:
                linha = linha.strip()
                if not linha or re.fullmatch(r"p[áa]g(ina)?", linha, re.I):
                    continue
                if linha.startswith(("* ", "- ")):
                    lista.append(esc(linha[2:].strip()))
                else:
                    fecha_lista()
                    saida.append("<p>%s</p>" % esc(linha))
            continue
        fecha_lista()
        if len(limpo) < 95 and TITULO_RE.match(limpo) and not limpo.endswith("."):
            saida.append("<h3>%s</h3>" % esc(limpo))
        else:
            saida.append("<p>%s</p>" % esc(limpo).replace("\n", "<br />"))
    fecha_lista()
    return "\n        ".join(saida)


def poema_html(texto):
    linhas = [esc(l) for l in (texto or "").split("\n")]
    return "<br />".join(linhas)


def secao_poemas(poemas):
    publicos = [p for p in poemas if p.get("dominio")]
    autorizados = [p for p in poemas if not p.get("dominio")]

    def grupo(itens):
        itens = sorted(itens, key=lambda p: (sem_acento(p.get("autor") or ""),
                                             sem_acento(p.get("titulo") or "")))
        partes = []
        for p in itens:
            partes.append(
                '<details class="acordeao acordeao--poema">\n'
                "  <summary><b>%s</b> — %s</summary>\n"
                '  <div class="poema"><p>%s</p></div>\n'
                "</details>" % (
                    esc(p.get("titulo") or "Sem título"),
                    esc(p.get("autor") or "Autoria não identificada"),
                    poema_html(p.get("texto")),
                )
            )
        return "\n".join(partes)

    return """
    <section class="secao" id="poesia-critica">
      <div class="secao__cabeca"><h2>Poesia crítica do direito</h2></div>
      <p>A poesia como parte da mística e da crítica ao direito: versos de
      advogadas, advogados, estudantes e poetas populares reunidos pelo portal.
      A coletânea original, com os links para cada poema no blogue, está em
      <a href="poesia-critica-do-direito.html">Poesia crítica do direito</a>.</p>
      <p class="hero__acoes"><a class="botao secundario" href="poesia-critica-do-direito.html">Ler a coletânea de poesia crítica</a></p>
    </section>

    <section class="secao" id="poesias">
      <div class="secao__cabeca"><h2>Todas as poesias do portal</h2>
        <p class="secao__nota">%d poemas no Caderno de Poesias e na poesia do blogue.
        Abra o título para ler o texto integral.</p></div>
      <h3 class="grupo-titulo">Domínio público (%d)</h3>
      %s
      <h3 class="grupo-titulo">Por autorização do responsável pelo site (%d)</h3>
      %s
    </section>""" % (
        len(poemas), len(publicos), grupo(publicos),
        len(autorizados), grupo(autorizados),
    )


def secao_calendario(eventos):
    eventos = sorted(eventos, key=lambda e: (e.get("diaMes") or "", e.get("ano") or ""))
    partes = []
    for e in eventos:
        dia = e.get("diaMes") or ""
        try:
            d, m = dia.split("-")
            data = "%s/%s" % (d, m)
        except Exception:
            data = dia
        titulo = re.sub(r"\s+", " ", e.get("titulo") or "").strip()
        resumo = re.sub(r"\s+", " ", e.get("resumo") or "").strip()
        autor = re.sub(r"\s+", " ", e.get("autor") or "").strip()
        partes.append(
            '<details class="acordeao acordeao--calendario">\n'
            "  <summary><b>%s</b> · %s — %s</summary>\n"
            '  <div class="calendario__texto"><p>%s</p>%s%s</div>\n'
            "</details>" % (
                esc(data), esc(e.get("ano") or "s.d."),
                esc(titulo[:150] + ("…" if len(titulo) > 150 else "")),
                esc(resumo or titulo),
                ("<p><b>Fonte:</b> %s</p>" % esc(autor)) if autor else "",
                ('<p class="secao__nota">%s</p>' % esc(titulo)) if resumo and titulo else "",
            )
        )
    return """
    <section class="secao" id="calendario">
      <div class="secao__cabeca"><h2>Calendário histórico dos trabalhadores</h2>
        <p class="secao__nota">%d datas de lutas, greves, massacres e conquistas.
        Abra uma data para ler o registro.</p></div>
      %s
    </section>""" % (len(eventos), "\n".join(partes))


GRUPOS_MEMORIA = [
    ("homenagens", "Homenagens e presenças",
     "Gente que fez a AJP e segue presente na memória da rede.", [
        "homenagens-ao-advogado-eugenio-lyra", "poemas-em-homenagem-a-eugenio-lyra",
        "companheiro-baldez-presente", "companheiro-baldez-presente-2",
        "companheiro-lavratti-presente", "thomaz-miguel-pressburger-presente",
        "morreu-lia-pires-e-com-ele-a-advocacia", "com-tristeza-luis-adeus",
        "falece-herrera-flores", "tres-anos-sem-caju-sepe-tiaraju",
        "adeus-sete-quedas-adeus-ivo-rodrigues", "80-anos-do-miguel-baldez",
     ]),
    ("cronicas", "Crônicas e relatos",
     "O conflito, o cotidiano e a resistência contados por quem viveu.", [
        "imbituba-cronica-de-um-mandado-de-despejo", "relato-em-praca-de-guerra",
        "o-dia-9-o-dia-10-o-dia-11-e-o-dia-12", "microconto",
        "uma-sensacao", "auto-retrato", "carta-do-ano-que-nao-terminou",
        "advocacia-delirante-parte-i", "advocacia-delirante-parte-ii",
     ]),
    ("arte", "Arte, música e imagem",
     "Teatro do oprimido, cinema, música e o fazer cultural na AJP.", [
        "o-teatro-e-o-ensino-do-direito-1", "o-teatro-e-o-ensino-do-direito-2",
        "o-teatro-e-o-ensino-do-direito-3", "cultura-negra-historia-e-musica",
        "cineclube-ajp-narradores-de-jave", "cinema-e-luta-no-campo",
        "documentario-o-cinema-libertario", "papo-de-cinema",
        "mercedes-sosa-e-sebastiao-salgado", "coraje-e-musica",
        "quem-planta-cultura-colhe-revolucao", "quem-planta-cultura-colhe-revolucao-2",
     ]),
    ("datas", "Datas que a rede celebra",
     "Março das mulheres, primeiro de maio, natal dos sem, ano novo.", [
        "08-de-marco-dia-de-luta-das-mulheres-estudantes", "dia-internacional-da-mulher",
        "mais-sobre-o-dia-da-mulher-e-o-feminismo", "maio-mes-do-trabalho",
        "o-natal-dos-sem-no-brasil", "presente-de-ano-novo",
     ]),
]


def secao_memoria_cultura():
    """Homenagens, crônicas, arte e datas — a memória cultural dentro da Mística."""
    idx = json.load(io.open(INDICE, encoding="utf-8"))
    por_slug = {r["slug"]: r for r in idx}

    def cartao(slug, etiqueta):
        reg = por_slug.get(slug)
        if not reg:
            return ""
        titulo = reg.get("titulo") or slug
        resumo = (reg.get("resumo") or "").strip()
        if len(resumo) > 150:
            resumo = resumo[:150].rsplit(" ", 1)[0].rstrip(",.;:—–-") + "…"
        ano = (reg.get("data") or "")[:4]
        return ('<a class="cartao destaque colecao__post" href="%s.html">\n'
                '      <span class="etiqueta">%s · %s</span>\n'
                '      <h3>%s</h3>\n'
                '      <p>%s</p>\n'
                '    </a>') % (esc(slug), esc(etiqueta), esc(ano), esc(titulo), esc(resumo))

    blocos, atalhos = [], []
    for ident, titulo, nota, slugs in GRUPOS_MEMORIA:
        cartoes = "".join(cartao(s, titulo) for s in slugs)
        if not cartoes:
            continue
        atalhos.append('<a href="#%s">%s</a>' % (ident, esc(titulo.split(" e ")[0]
                                                    if ident != "arte" else "Arte")))
        blocos.append("""<section class="secao" id="%s" aria-labelledby="%s-titulo">
      <div class="secao__cabeca"><h2 id="%s-titulo">%s</h2>
      <p class="secao__nota">%s</p></div>
      <div class="grade-3">%s</div>
    </section>""" % (ident, ident, ident, esc(titulo), esc(nota), cartoes))

    if not blocos:
        return ""
    return """
    <section class="secao" id="memoria-e-cultura" aria-labelledby="memoria-titulo">
      <div class="secao__cabeca"><h2 id="memoria-titulo">Memória e cultura</h2>
      <p class="secao__nota">homenagens, crônicas, arte e datas da rede</p></div>
      <p class="colecao__nota">O que o acervo guarda da vida da AJP: quem fez a rede e
      segue presente, as crônicas do conflito, a arte e as datas que a luta celebra.
      A cronologia da rede está em <a href="memoria.html">Memória da AJP e da RENAP</a>.</p>
      <nav class="colecao__atalhos" aria-label="Memória e cultura">%s</nav>
      %s
    </section>""" % ("".join(atalhos), "\n".join(blocos))


def monta_artigo():
    mistica = blocos(os.path.join(FONTES, "mistica.txt"))
    bogo = blocos(os.path.join(FONTES, "citacao.txt"))
    poemas = json.load(io.open(POEMAS, encoding="utf-8"))
    calendario = json.load(io.open(CALENDARIO, encoding="utf-8"))

    # Títulos e créditos já aparecem no cabeçalho de cada seção.
    corpo_mistica = mistica[2:] if len(mistica) > 2 else mistica
    corpo_bogo = bogo[3:] if len(bogo) > 3 else bogo

    artigo = """
  <article data-revelar-grupo class="pagina" aria-labelledby="titulo">
    <header>
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Mística · 2023</p>
      <h1 id="titulo">Mística: o que sustenta a luta</h1>
      <p class="lead">Os dois textos integrais que fundamentam a mística nos
      movimentos populares, a memória cultural da rede, a poesia do portal e o
      calendário histórico dos trabalhadores.</p>
    </header>

    <section class="secao" id="texto-acampamento">
      <div class="secao__cabeca"><h2>Mística: acúmulos, aprendizados, saberes e apontamentos iniciais</h2>
        <p class="secao__nota">Escrito por militantes dos movimentos populares
        brasileiros para subsidiar a equipe de Mística do 3º Acampamento Estadual
        do Levante Popular da Juventude, na UFJF, em Juiz de Fora/MG, 2023.</p></div>
      <details class="acordeao" open>
        <summary>Ler o texto completo</summary>
        <div class="cartao corpo texto-integral">
        %s
        </div>
      </details>
      <p class="secao__nota">Fonte: <a href="%s" target="_blank" rel="noopener">documento original</a>.</p>
    </section>

    <section class="secao" id="texto-bogo">
      <div class="secao__cabeca"><h2>A mística: parte da vida e da luta</h2>
        <p class="secao__nota"><b>Ademar Bogo</b>. Texto completo, sem cortes.</p></div>
      <details class="acordeao" open>
        <summary>Ler o texto completo</summary>
        <div class="cartao corpo texto-integral">
        %s
        </div>
      </details>
      <p class="secao__nota">Fonte: <a href="%s" target="_blank" rel="noopener">documento original</a>.</p>
    </section>

    %s

    %s

    %s

    <section class="compartilhar" data-compartilhar
             data-url="https://finweejur.github.io/assessoriajuridicapopular/mistica.html"
             data-titulo="Mística: o que sustenta a luta"
             data-autor="Militantes dos movimentos populares; Ademar Bogo"
             data-data="2023-01-01" data-fonte-url="%s"
             data-fonte="Levante Popular da Juventude">
      <h2>Compartilhar e citar</h2>
      <div class="compartilhar__botoes">
        <button type="button" data-acao="whatsapp">WhatsApp</button>
        <button type="button" data-acao="telegram">Telegram</button>
        <button type="button" data-acao="instagram">Instagram</button>
        <button type="button" data-acao="copiar-texto">Copiar texto</button>
        <button type="button" data-acao="copiar-citacao">Copiar citação ABNT</button>
      </div>
      <p class="compartilhar__status" data-status role="status" aria-live="polite" data-visivel="false"></p>
    </section>
  </article>""" % (
        texto_integral(corpo_mistica), DOC_MISTICA,
        texto_integral(corpo_bogo), DOC_BOGO,
        secao_memoria_cultura(),
        secao_poemas(poemas),
        secao_calendario(calendario),
        DOC_MISTICA,
    )
    return artigo


CARD = """
  <section class="mistica-dia" aria-labelledby="mistica-titulo" hidden data-mistica>
    <div class="miolo">
      <div class="mistica-cartao">
        <canvas class="beam-canvas" aria-hidden="true"></canvas>
        <span class="beam-core" aria-hidden="true"></span>
        <h2 class="mistica__rotulo" id="mistica-titulo">Mística do dia</h2>
        <p class="mistica__data"></p>
        <h3 class="mistica__titulo"></h3>
        <p class="mistica__resumo"></p>
        <p class="mistica__fonte"></p>
      </div>
    </div>
  </section>
"""


def main():
    t = io.open(PAGINA, encoding="utf-8").read()
    artigo = monta_artigo()
    t = re.sub(r'<article[^>]*>.*?</article>', artigo, t, count=1, flags=re.S)

    # Remove o card antigo (de qualquer posição) e recoloca antes do artigo,
    # depois da migalha e da subnav.
    t = re.sub(r'\s*<section class="mistica-dia".*?</section>\s*', chr(10), t, count=1, flags=re.S)
    marca = t.find("<article")
    if marca >= 0:
        t = t[:marca] + CARD + t[marca:]

    if "mistica-dia.js" not in t:
        t = t.replace("</body>", '<script src="mistica-dia.js?v=2" defer></script>\n</body>', 1)

    io.open(PAGINA, "w", encoding="utf-8", newline="\n").write(t)
    print("mistica.html:", len(t), "bytes")


if __name__ == "__main__":
    main()
