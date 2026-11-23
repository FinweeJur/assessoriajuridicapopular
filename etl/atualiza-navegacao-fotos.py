"""Atualiza links do bento e do rodapé e aplica as fotos originais do blogue.

- bento da home: 14 cartões, com as páginas novas (Autores, Biblioteca,
  Referências citadas, Rede/AJUPs) e contagens do manifest.
- rodapé: 4 colunas canónicas, aplicadas em todas as páginas.
- hero das páginas principais: foto de evento do próprio blogue.
- home: faixa de fotos de eventos + tira de pessoas recortadas.
- CSS: estilos das recortadas e suporte a fundo de página (.com-foto).

Idempotente: pode rodar de novo sem duplicar.
"""
import io
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 1. Bento ───────────────────────────────────────────────────────────────
ICONES = {
    "livro": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    "balanca": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "predio": '<line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/>',
    "pessoas": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "ideia": '<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2Z"/>',
    "relogio": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "formatura": '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
    "jornal": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/>',
    "dicionario": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/><path d="m8 13 4-7 4 7"/><path d="M9.1 11h5.7"/>',
    "colunas": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18"/><path d="M17 3v18"/>',
    "pena": '<path d="M12.67 19a2 2 0 0 0 1.416-.588l6.154-6.172a6 6 0 0 0-8.49-8.49L5.586 9.914A2 2 0 0 0 5 11.328V18a1 1 0 0 0 1 1z"/><path d="M16 8 2 22"/><path d="M17.5 15H9"/>',
}

BENTO = [
    # href, etiqueta, titulo, conta, icone, classe
    ("acervo.html#lista-acervo", "Acervo completo", "790 textos transcritos", "Busca por palavra-chave, tipo, ano e ordem. Cada texto com autor, data e link para o original.", "livro", "bento__item--grande"),
    ("assessoria-juridica-popular.html", "Seção", "Assessoria jurídica popular", "186 textos", "balanca", ""),
    ("direitos-humanos.html", "Seção", "Direitos humanos", "136 textos", "predio", ""),
    ("movimentos-sociais.html", "Seção", "Movimentos sociais", "218 textos", "pessoas", ""),
    ("teoria-critica.html", "Seção", "Teoria crítica", "114 textos", "ideia", ""),
    ("blog.html", "Em ordem", "Blog", "790 textos em 15 anos", "jornal", "bento__item--largo"),
    ("educacao-popular.html", "Seção", "Educação popular", "136 textos", "formatura", ""),
    ("mistica.html", "Mística", "Textos, memória e poesia", "38 memórias · 135 poemas", "pena", ""),
    ("biblioteca.html", "Biblioteca", "Acervos, obras e dossiês", "18 coleções", "livro", ""),
    ("autores.html", "Quem escreve", "Autores", "30 pessoas", "pessoas", ""),
    ("referencias-citadas.html", "Pesquisa", "Referências citadas", "524 fichas", "dicionario", ""),
    ("rede.html", "Rede", "Parceiros e mapeamento", "40 AJUPs", "colunas", ""),
    ("ia.html", "Pesquisa", "IA aplicada à AJP", "8 sínteses", "ideia", ""),
    ("poemas.html", "Antologia", "Poemas e Caderno", "135 poemas", "pena", ""),
]


def ico(nome):
    return ('<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">%s</svg>'
            % ICONES[nome])


def cartao_bento(item, indice):
    href, etiqueta, titulo, conta, icone, classe = item
    if classe == "bento__item--grande":
        return '''        <a class="bento__item bento__item--grande" href="%s" style="--i:%d">
          <span class="bento__ico">%s</span>
          <span class="bento__etiqueta">%s</span>
          <b class="bento__numero">790</b>
          <span class="bento__titulo">textos transcritos</span>
          <p>%s</p>
          <span class="bento__seta">Explorar o acervo ↓</span>
        </a>''' % (href, indice, ico(icone), etiqueta, conta)
    return '''        <a class="bento__item %s" href="%s" style="--i:%d">
          <span class="bento__ico">%s</span>
          <span class="bento__etiqueta">%s</span>
          <h3 class="bento__titulo">%s</h3>
          <span class="bento__conta">%s</span>
        </a>''' % (classe, href, indice, ico(icone), etiqueta, titulo, conta)


def ata_bento(t):
    inicio = t.find('<div class="bento"')
    if inicio < 0:
        return t, False
    fim = t.find('</div>\n      </div>', inicio)
    if fim < 0:
        return t, False
    novo = ('<div class="bento" data-bento>\n'
            + "\n".join(cartao_bento(c, i + 1) for i, c in enumerate(BENTO))
            + '\n        ')
    return t[:inicio] + novo + t[fim:], True


# ── 2. Rodapé ──────────────────────────────────────────────────────────────
RODAPE = '''<footer class="rodape">
  <div class="rodape__topo">
    <p class="rodape__marca"><span class="ponto" aria-hidden="true"></span> AJP · Assessoria Jurídica Popular</p>
  </div>
  <div class="rodape__interno rodape__interno--linha">
    <div>
      <h2>Acervo</h2>
      <ul>
        <li><a href="acervo.html">Todos os textos</a></li>
        <li><a href="blog.html">Blog, em ordem</a></li>
        <li><a href="autores.html">Autores</a></li>
        <li><a href="biblioteca.html">Biblioteca</a></li>
        <li><a href="referencias-citadas.html">Referências citadas</a></li>
        <li><a href="glossario.html">Glossário</a></li>
        <li><a href="o-que-e-assessoria-juridica-popular.html">O que é AJP</a></li>
      </ul>
    </div>
    <div>
      <h2>Seções</h2>
      <ul>
        <li><a href="assessoria-juridica-popular.html">Assessoria jurídica popular</a></li>
        <li><a href="direitos-humanos.html">Direitos humanos</a></li>
        <li><a href="movimentos-sociais.html">Movimentos sociais</a></li>
        <li><a href="teoria-critica.html">Teoria crítica</a></li>
        <li><a href="educacao-popular.html">Educação popular</a></li>
        <li><a href="formacao.html">Formação</a></li>
      </ul>
      <h2>Mística</h2>
      <ul>
        <li><a href="mistica.html">Mística</a></li>
        <li><a href="cultura.html">Cultura</a></li>
        <li><a href="poemas.html">Poemas e Caderno</a></li>
      </ul>
    </div>
    <div>
      <h2>Rede e pesquisa</h2>
      <ul>
        <li><a href="rede.html">Rede e parceiros</a></li>
        <li><a href="mapeamento-ajups.html">Mapeamento de AJUPs</a></li>
        <li><a href="memoria.html">Memória da AJP e da RENAP</a></li>
        <li><a href="memoria.html#linha-do-tempo">Linha do tempo</a></li>
        <li><a href="ia.html">IA aplicada à pesquisa</a></li>
        <li><a href="rede.html#quem-somos">Quem somos</a></li>
        <li><a href="rede.html#como-postar">Como postar</a></li>
      </ul>
    </div>
    <div>
      <h2>Fonte e parcerias</h2>
      <p>Acervo montado a partir do blog
      <a href="https://assessoriajuridicapopular.blogspot.com/" target="_blank" rel="noopener">Assessoria Jurídica Popular</a>
      e de fontes parceiras, com autor, data e link. Captura em 20/11/2026.</p>
      <ul class="parcerias__lista">
        <li><a href="https://www.renap.org.br/" target="_blank" rel="noopener"><img src="logos/renap.png" alt="RENAP" loading="lazy" /></a></li>
        <li><a href="https://ipdms.org.br/" target="_blank" rel="noopener"><img src="logos/ipdms.png" alt="IPDMS" loading="lazy" /></a></li>
        <li><a href="https://mab.org.br/" target="_blank" rel="noopener"><img class="mab-preto" src="logos/mab-simples-preto.png" alt="MAB" loading="lazy" /><img class="mab-branco" src="logos/mab-simples-branco.png" alt="MAB" loading="lazy" /></a></li>
      </ul>
      <p>GT de Assessoria Jurídica Popular do IPDMS · Coord. Luiz Otávio Ribas</p>
      <p>Desenvolvimento e retirada de imagens ou conteúdo: Artur Colito —
      <a href="mailto:artur.colito@ufvjm.edu.br">artur.colito@ufvjm.edu.br</a></p>
    </div>
  </div>
  <p class="rodape__ia">Rascunho feito com IA - Inteligência Artificial (Programa OpenCode,
  Modelo Deepseek V4.1 Flash), podendo contar com erros e ainda em revisão. Verifique as informações.</p>
</footer>'''


def ata_rodape(t):
    inicio = t.find('<footer class="rodape">')
    if inicio < 0:
        return t, False
    fim = t.find("</footer>", inicio)
    if fim < 0:
        return t, False
    return t[:inicio] + RODAPE + t[fim + len("</footer>"):], True


# ── 3. Fotos nas heroes ────────────────────────────────────────────────────
HERO_FOTOS = {
    "assessoria-juridica-popular.html": "2014-minicurso-em-advocacia-popular-na-uem-024.jpg",
    "direitos-humanos.html": "2012-coluna-direitos-das-marias-iv-encontro-de-mu-035.jpg",
    "movimentos-sociais.html": "2017-fortalecimento-da-renaju-em-uma-conjuntura-d-007.jpg",
    "teoria-critica.html": "2013-cadernos-insurgentes-e-oficina-do-geap-029.jpg",
    "educacao-popular.html": "2015-sustenta-a-pisada-na-ajp-021.jpg",
    "acervo.html": "2011-classe-trabalhadora-e-ajup-sajup-10-anos-063.jpg",
    "blog.html": "2012-nasce-a-coluna-direitos-das-marias-046.jpg",
    "autores.html": "2012-nasce-a-coluna-direitos-das-marias-046.jpg",
    "biblioteca.html": "2014-minicurso-em-advocacia-popular-na-uem-025.jpg",
    "cultura.html": "2011-companheiros-haitianos-presente-relato-de-um-065.jpg",
    "formacao.html": "2015-sustenta-a-pisada-na-ajp-022.jpg",
    "memoria.html": "2011-carta-dos-enamorados-do-neda-062.jpg",
    "mistica.html": "2012-poema-sobre-o-encontro-em-santarem-048.jpg",
    "rede.html": "2011-ajp-e-etnodesenvolvimento-056.jpg",
    "referencias-citadas.html": "2018-os-instrumentos-do-direito-servem-para-quem--003.jpg",
    "mapeamento-ajups.html": "2017-jornada-universitaria-em-fortaleza-010.jpg",
    "glossario.html": "2013-cadernos-insurgentes-e-oficina-do-geap-029.jpg",
    "linha-do-tempo.html": "2015-sobre-as-manifestacoes-de-hoje-a-importancia-020.jpg",
}

RE_HERO_FOTO = re.compile(
    r'<div class="hero__foto"\s+style="background-image:url\(\'[^\']+\'\)"\s+aria-hidden="true"></div>')
RE_VEU = re.compile(r'<div class="hero__veu"[^>]*></div>\s*')


def ata_hero(t, foto):
    url = "fotos/eventos/" + foto
    m = re.search(r'<section class="hero[^"]*">', t)
    if not m:
        return t, False
    fim = t.find("</section>", m.end())
    if fim < 0:
        return t, False
    bloco = t[m.end():fim]
    # remove qualquer foto/véu já existente no hero
    bloco = RE_HERO_FOTO.sub("", bloco)
    bloco = RE_VEU.sub("", bloco)
    novo_div = ('\n    <div class="hero__foto" style="background-image:url(\'%s\')" '
                'aria-hidden="true"></div>\n    <div class="hero__veu" aria-hidden="true"></div>'
                % url)
    return t[:m.end()] + novo_div + bloco.lstrip("\n") + t[fim:], True


# ── 4. Faixa de fotos e recortes na home ───────────────────────────────────
FAIXA_A = [
    ("2017-fortalecimento-da-renaju-em-uma-conjuntura-d-007.jpg", "Encontro da RENAJU, 2017"),
    ("2012-coluna-direitos-das-marias-iv-encontro-de-mu-036.jpg", "Encontro de mulheres do MPA, 2012"),
    ("2014-minicurso-em-advocacia-popular-na-uem-024.jpg", "Minicurso de advocacia popular na UEM, 2014"),
    ("2011-classe-trabalhadora-e-ajup-sajup-10-anos-063.jpg", "SAJUP 10 anos, 2011"),
    ("fotos/seminario/seminario-02.jpg", "Seminário do IPDMS, 2026"),
]
FAIXA_B = [
    ("2015-sustenta-a-pisada-na-ajp-022.jpg", "Oficina Sustenta a pisada na AJP, 2015"),
    ("2013-cadernos-insurgentes-e-oficina-do-geap-029.jpg", "Oficina do GEAP, 2013"),
    ("2011-companheiros-haitianos-presente-relato-de-um-065.jpg", "Formação com companheiros haitianos, 2011"),
    ("2012-poema-sobre-o-encontro-em-santarem-048.jpg", "Encontro em Santarém, 2012"),
    ("fotos/seminario/seminario-05.jpg", "Seminário do IPDMS, 2026"),
]


def figura(src, alt, oculto=False):
    return ('<figure class="foto-faixa__item"><img src="%s" alt="%s" loading="lazy" '
            'decoding="async" /></figure>' % (src, "" if oculto else alt))


def caminho_faixa(src):
    """Versão leve (720px) usada na faixa da home."""
    if src.startswith("fotos/seminario/"):
        base = src[len("fotos/seminario/"):]
        return "fotos/seminario/faixa/" + base.replace(".jpg", "-720.jpg")
    base = src if src.startswith("fotos/eventos/") else "fotos/eventos/" + src
    base = base[len("fotos/eventos/"):]
    return "fotos/eventos/faixa/" + base.replace(".jpg", "-720.jpg")


def grupo(itens, oculto=False):
    corpo = "".join(figura(caminho_faixa(s), a, oculto) for s, a in itens)
    return '<div class="foto-faixa__grupo"%s>%s</div>' % (
        ' aria-hidden="true"' if oculto else "", corpo)


def monta_faixa():
    return ('<div class="foto-faixa" aria-label="Fotos de eventos do acervo e do seminário do IPDMS">\n'
            '          <div class="foto-faixa__linha">\n'
            '            <div class="foto-faixa__trilho foto-faixa__trilho--a">%s%s</div>\n'
            '          </div>\n'
            '          <div class="foto-faixa__linha">\n'
            '            <div class="foto-faixa__trilho foto-faixa__trilho--b">%s%s</div>\n'
            '          </div>\n'
            '          <p class="foto-faixa__nota">Fotos de encontros, cursos e oficinas do blogue, '
            'e do seminário do IPDMS (2026)</p>\n'
            '        </div>') % (grupo(FAIXA_A), grupo(FAIXA_A, True),
                                grupo(FAIXA_B), grupo(FAIXA_B, True))


RECORTES = '''<div class="recortes" aria-hidden="true">
          <img src="fotos/recortes/ricardo-pazello-u2.png" alt="" loading="lazy" />
          <img src="fotos/recortes/miguel-baldez-u2.png" alt="" loading="lazy" />
          <img src="fotos/recortes/jacques-alfonsin.png" alt="" loading="lazy" />
        </div>'''


def ata_home(t):
    # faixa
    i = t.find('<div class="foto-faixa"')
    if i >= 0:
        j = t.find('<p class="foto-faixa__nota">', i)
        j = t.find("</p>", j) + 4
        k = t.find("</div>", j) + 6
        t = t[:i] + monta_faixa() + t[k:]
    # recortes: remove versão antiga e insere a atual
    m = re.search(r'\s*<div class="recortes" aria-hidden="true">.*?</div>', t, re.S)
    if m:
        t = t[:m.start()] + t[m.end():]
    m = re.search(r'(<p class="inicio__acoes">.*?</p>)', t, re.S)
    if m:
        t = t[:m.end()] + "\n        " + RECORTES + t[m.end():]
    return t


# ── 5. CSS ─────────────────────────────────────────────────────────────────
CSS_EXTRA = '''
/* ── Recortes de pessoas (PNG com transparência) ────────────────────────── */
.recortes {
  display: flex; align-items: flex-end; gap: clamp(4px, 1.2vw, 14px);
  margin: var(--e4) 0 0; padding: 0;
  filter: saturate(.9);
}
.recortes img {
  height: clamp(104px, 15vw, 168px); width: auto; display: block;
  filter: drop-shadow(0 12px 20px rgba(0, 0, 0, .3));
  opacity: .93;
}
.recortes img:nth-child(1) { height: clamp(112px, 16vw, 180px); }
.recortes img:nth-child(3) { height: clamp(92px, 13vw, 148px); }
@media (max-width: 620px) { .recortes { gap: 4px; } .recortes img { height: 88px; } }

/* ── Fundo de página opcional (desligado por omissão) ───────────────────── */
body.com-foto::before {
  content: ""; position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background-image: var(--fundo); background-size: cover; background-position: center;
  filter: brightness(.38) saturate(.9); opacity: .42;
}
[data-theme="light"] body.com-foto::before,
:root:not([data-theme]) body.com-foto::before { opacity: .28; filter: brightness(.9); }

/* No tema claro a foto do hero recua: contraste do texto em primeiro lugar. */
[data-theme="light"] .hero__foto,
:root:not([data-theme]) .hero__foto {
  opacity: .26; filter: grayscale(.35) brightness(.95) contrast(.9);
}
[data-theme="light"] .hero__veu,
:root:not([data-theme]) .hero__veu {
  background: linear-gradient(100deg,
    color-mix(in srgb, var(--cp-bg) 78%, transparent) 0%,
    color-mix(in srgb, var(--cp-bg) 66%, transparent) 55%,
    color-mix(in srgb, var(--cp-bg) 48%, transparent) 100%);
}

/* ── Faixa de fotos no topo de páginas sem hero ─────────────────────────── */
.faixa-pagina {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px; margin: var(--e4) 0 0;
}
.faixa-pagina figure {
  margin: 0; overflow: hidden; border-radius: var(--raio);
  border: 1px solid var(--borda); aspect-ratio: 4 / 3;
}
.faixa-pagina img {
  width: 100%; height: 100%; object-fit: cover; display: block;
  filter: saturate(.95);
}
@media (max-width: 620px) {
  .faixa-pagina { grid-template-columns: 1fr 1fr; }
  .faixa-pagina figure:last-child { display: none; }
}
'''


def ata_css():
    p = os.path.join(RAIZ, "acervo.css")
    css = io.open(p, encoding="utf-8").read()
    start = css.find("/* ── Recortes de pessoas")
    if start >= 0:
        css = css[:start].rstrip() + "\n"
    css = css.rstrip() + "\n" + CSS_EXTRA
    io.open(p, "w", encoding="utf-8", newline="\n").write(css)
    return True


FAIXAS_PAGINA = {
    "ia.html": [
        ("2013-cadernos-insurgentes-e-oficina-do-geap-029.jpg", "Oficina do GEAP, 2013"),
        ("2014-minicurso-em-advocacia-popular-na-uem-024.jpg", "Minicurso de advocacia popular na UEM, 2014"),
        ("2017-jornada-universitaria-em-fortaleza-010.jpg", "Jornada universitária em Fortaleza, 2017"),
    ],
    "poemas.html": [
        ("2012-poema-sobre-o-encontro-em-santarem-048.jpg", "Encontro em Santarém, 2012"),
        ("2011-companheiros-haitianos-presente-relato-de-um-065.jpg", "Formação com companheiros haitianos, 2011"),
        ("2015-sustenta-a-pisada-na-ajp-022.jpg", "Oficina Sustenta a pisada na AJP, 2015"),
    ],
}


def ata_faixa_pagina(t, fotos):
    if 'class="faixa-pagina"' in t:
        return t, False
    figs = "".join(
        '<figure><img src="fotos/eventos/%s" alt="%s" loading="lazy" decoding="async" /></figure>'
        % (arq, alt) for arq, alt in fotos)
    bloco = '\n    <div class="faixa-pagina" aria-hidden="false">%s</div>' % figs
    m = re.search(r'<p class="lead">.*?</p>', t, re.S)
    if not m:
        return t, False
    return t[:m.end()] + bloco + t[m.end():], True


# ── execução ───────────────────────────────────────────────────────────────
def main():
    p = os.path.join(RAIZ, "index.html")
    t = io.open(p, encoding="utf-8").read()
    t, ok_bento = ata_bento(t)
    t = ata_home(t)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("bento:", ok_bento, "| faixa:", 'foto-faixa__trilho' in t, "| recortes:", 'class="recortes"' in t)

    paginas = [f for f in os.listdir(RAIZ) if f.endswith(".html")]
    n_rod = n_hero = 0
    for f in paginas:
        caminho = os.path.join(RAIZ, f)
        try:
            t = io.open(caminho, encoding="utf-8").read()
        except Exception:
            continue
        original = t
        t, ok = ata_rodape(t)
        if ok:
            n_rod += 1
        if f in HERO_FOTOS:
            t, okh = ata_hero(t, HERO_FOTOS[f])
            if okh:
                n_hero += 1
        if f in FAIXAS_PAGINA:
            t, okf = ata_faixa_pagina(t, FAIXAS_PAGINA[f])
            if okf:
                print("faixa de página:", f)
        if t != original:
            io.open(caminho, "w", encoding="utf-8", newline="\n").write(t)
    print("rodapes atualizados:", n_rod, "| heroes com foto:", n_hero)
    print("css:", ata_css())


if __name__ == "__main__":
    main()
