"""Gera os dados das coleções: memória, trilhas, biblioteca e cultura."""
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")


def grava(nome, obj):
    with io.open(os.path.join(DADOS, nome), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


regs = json.load(io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8"))
by = {}
for r in regs:
    ano = (r.get("data") or "")[:4]
    if ano:
        by.setdefault(ano, []).append(r)
anos = []
for ano in sorted(by, reverse=True):
    itens = sorted(by[ano], key=lambda r: r.get("data") or "", reverse=True)
    anos.append({
        "ano": ano,
        "total": len(itens),
        "posts": [{
            "slug": r["slug"], "titulo": r.get("titulo"), "data": r.get("data"),
            "tipo": r.get("tipo"), "tema": r.get("tema"),
        } for r in itens[:4]],
    })
grava("memoria.json", {"anos": anos})

eventos = [
    {"ano": "1960", "titulo": "Surgem as primeiras assessorias jurídicas populares",
     "tipo": "marco",
     "descricao": "Práticas de advocacia junto a movimentos sociais e organizações populares começam a se articular no Brasil, com influência da educação popular e da crítica ao assistencialismo.",
     "fonte": "assessoria-juridica-popular-no-mundo.html",
     "fonte_label": "Dossiê: AJP, Brasil, América Latina e mundo"},
    {"ano": "1980", "titulo": "Direito Achado na Rua e crítica jurídica",
     "tipo": "marco",
     "descricao": "A Nova Escola Jurídica Brasileira e Roberto Lyra Filho formulam o direito achado na rua; o pluralismo jurídico e os sujeitos coletivos de direito entram no vocabulário da AJP.",
     "fonte": "assessoria-juridica-popular-no-mundo.html",
     "fonte_label": "Dossiê: AJP, Brasil, América Latina e mundo"},
    {"ano": "1995", "titulo": "Fundação da RENAP", "tipo": "marco",
     "descricao": "A Rede Nacional de Advogadas e Advogados Populares se constitui como articulação nacional da advocacia popular. A página Sobre da RENAP registra 1996; o 29º Encontro (2025) fala em 30 anos, o que recua a 1995.",
     "fonte": "https://www.renap.org.br/encontro-nacional",
     "fonte_label": "RENAP — 29º Encontro Nacional"},
    {"ano": "2001", "titulo": "Caderno RENAP n.1 — Alhandra", "tipo": "publicacao",
     "descricao": "A RENAP inicia a série de Cadernos com estudos de caso, peças e jurisprudência voltados à advocacia popular.",
     "fonte": "https://www.renap.org.br/publicacoes",
     "fonte_label": "RENAP — Publicações"},
    {"ano": "2009", "titulo": "Nasce o blogue AJP", "tipo": "publicacao",
     "descricao": "O blogue Assessoria Jurídica Popular começa a publicar notícias, textos de formação, memória e poesia. É a base deste acervo.",
     "fonte": "seis-anos-do-blogue-ajpopular.html",
     "fonte_label": "Seis anos do blogue AJPopular"},
    {"ano": "2010", "titulo": "Coletânea de Poesias (CMM)", "tipo": "publicacao",
     "descricao": "O Caderno de Poesias, organizado por Cleber Mori, reúne 272 páginas de autores brasileiros e estrangeiros. 135 poemas estão publicados no acervo.",
     "fonte": "poemas.html", "fonte_label": "Caderno de Poesias e poesia do blog"},
    {"ano": "2013", "titulo": "Defensoria Pública, AJP e movimentos sociais", "tipo": "publicacao",
     "descricao": "A RENAP publica o primeiro volume da série sobre Defensoria Pública, assessoria jurídica popular e movimentos sociais.",
     "fonte": "https://www.renap.org.br/publicacoes",
     "fonte_label": "RENAP — Publicações"},
    {"ano": "2015", "titulo": "RENAP: 20 anos de defesa gratuita", "tipo": "marco",
     "descricao": "A rede celebra duas décadas de articulação da advocacia popular.",
     "fonte": "uma-rede-com-20-anos-de-defesa-gratuita-dos-direitos-de.html",
     "fonte_label": "Uma rede com 20 anos de defesa gratuita"},
    {"ano": "2019", "titulo": "XXIV Encontro Nacional da RENAP", "tipo": "encontro",
     "descricao": "Belém (PA) recebe o primeiro encontro nacional da RENAP no Norte do país, com 23 estados e cerca de 130 participantes.",
     "fonte": "https://www.renap.org.br/encontro-nacional",
     "fonte_label": "RENAP — Encontro Nacional"},
    {"ano": "2025", "titulo": "XXIX Encontro Nacional da RENAP", "tipo": "encontro",
     "descricao": "Salvador (BA) reúne mais de 150 pessoas de 23 estados para os 30 anos da rede, com lançamento de livros e oficinas.",
     "fonte": "https://www.renap.org.br/encontro-nacional",
     "fonte_label": "RENAP — 29º Encontro Nacional"},
    {"ano": "2026", "titulo": "Publicação deste acervo digital", "tipo": "marco",
     "descricao": "O acervo AJP é reorganizado como site estático, com 713 textos, seções, coleções e linha do tempo.",
     "fonte": "acervo.html", "fonte_label": "Acervo AJP"},
]
grava("historia.json", eventos)

trilhas = [
    {"id": "o-que-e-ajp", "titulo": "O que é assessoria jurídica popular",
     "descricao": "Definição, história e prática: comece pelo texto de 2009 e siga pelas discussões sobre método e organização.",
     "nivel": "Introdutório", "posts": [
        "o-que-e-assessoria-juridica-popular", "assessoria-juridica-popular",
        "algumas-linhas-sobre-assessoria-juridica-popular-e",
        "por-uma-nova-articulacao-da-assessoria-juridica-popular",
        "como-formar-uma-ajup",
        "assessoria-juridica-popular-um-importante-marco-na-estrada"]},
    {"id": "direito-achado-insurgente", "titulo": "Direito Achado na Rua, insurgente e uso tático",
     "descricao": "Quatro perspectivas que não são sinônimos: de onde vem o direito, como usar o direito do Estado e a que preço.",
     "nivel": "Intermediário", "posts": [
        "o-direito-achado-na-rua-tambem-se-acha-na-teve-2-a-turma",
        "direito-insurgente-e-pluralismo-juridico-na-advocacia",
        "do-direito-a-insurgencia-ao-direito-insurgente-o-caso-do",
        "aborto-do-pluralismo-juridico-a-efetivacao-do-direito-a",
        "assessoria-juridica-popular-no-mundo", "o-que-e-o-direito"]},
    {"id": "educacao-popular", "titulo": "Educação popular e universidade",
     "descricao": "Formação, círculos de cultura, teatro do oprimido e o lugar da universidade na AJP.",
     "nivel": "Introdutório", "posts": [
        "circulo-de-cultura-de-paulo-freire",
        "teatro-do-oprimido-e-assessoria-juridica-popular-duas",
        "conscientizacao-de-direitos-pequena-tese",
        "fazer-a-universidade-ajup-e-educacao-juridica",
        "como-formar-uma-ajup"]},
    {"id": "terra-moradia", "titulo": "Terra, moradia e movimentos",
     "descricao": "Casos de despejo, ocupação, reforma agrária e organização popular — do conflito à estratégia jurídica.",
     "nivel": "Intermediário", "posts": [
        "pinheirinho", "ocupacao-28-de-maio-e-a-assessoria-juridica",
        "luta-pela-moradia-no-distrito-federal",
        "mobilizacao-indigena-paralisa-uhe-belo-monte",
        "a-repercussao-de-uma-vitoria-no-judiciario-o-caso-dos",
        "o-latifundio-matou-mais-um-trabalhador-sem-terra-no-para"]},
    {"id": "teoria-critica", "titulo": "Teoria crítica do direito",
     "descricao": "Marxismo, crítica da forma jurídica, pluralismo e os clássicos que sustentam a prática.",
     "nivel": "Avançado", "posts": [
        "marx-e-o-nao-direito-direito-e-marxismo",
        "a-desnecessidade-historica-do-direito", "o-que-e-o-direito",
        "os-instrumentos-do-direito-servem-para-quem"]},
    {"id": "memoria-ditadura", "titulo": "Memória, ditadura e justiça",
     "descricao": "O que a rede guarda sobre a ditadura, a anistia, os arquivos e as lutas por memória e verdade.",
     "nivel": "Intermediário", "posts": [
        "repatriacao-do-acervo-do-brasil-nunca-mais",
        "para-um-historico-da-advocacia-popular-no-brasil",
        "revisao-da-lei-de-anistia", "a-anistia-e-a-ajuris",
        "homenagens-ao-advogado-eugenio-lyra",
        "injustica-de-transicao-na-unb"]},
]
grava("trilhas.json", trilhas)

biblioteca = [
    {"tipo": "Acervo", "titulo": "Biblioteca digital", "url": "biblioteca-digital.html",
     "descricao": "Entrada para os acervos bibliográficos reunidos pela AJP."},
    {"tipo": "Acervo", "titulo": "Biblioteca AJUP-RJ", "url": "biblioteca-ajup-rj.html",
     "descricao": "Materiais da assessoria jurídica universitária do Rio de Janeiro."},
    {"tipo": "Acervo", "titulo": "Biblioteca Roberto Lyra Filho", "url": "biblioteca-roberto-lyra-filho.html",
     "descricao": "Obras e textos ligados ao direito achado na rua e à crítica jurídica."},
    {"tipo": "Acervo", "titulo": "Biblioteca Miguel Lanzellotti Baldez", "url": "biblioteca-miguel-lanzellotti-baldez.html",
     "descricao": "Acervo de referência sobre advocacia popular e direitos humanos."},
    {"tipo": "Acervo", "titulo": "Biblioteca Joaquín Herrera Flores", "url": "biblioteca-joaquin-herrera-flores.html",
     "descricao": "Direitos humanos, interculturalidade e crítica ao universalismo abstrato."},
    {"tipo": "Acervo", "titulo": "Biblioteca digital da filosofia latino-americana", "url": "biblioteca-digital-da-filosofia-latino-americana.html",
     "descricao": "Filosofia latino-americana e pensamento descolonial."},
    {"tipo": "Acervo", "titulo": "Monografias da AJP universitária", "url": "monografias-da-assessoria-juridica-popular-universitaria.html",
     "descricao": "Trabalhos de conclusão sobre assessoria jurídica popular universitária."},
    {"tipo": "Acervo", "titulo": "Referências", "url": "referencias.html",
     "descricao": "Bibliografia e fontes usadas no acervo.",
     "fonte": "https://assessoriajuridicapopular.blogspot.com/2012/07/referencias.html"},
    {"tipo": "Acervo", "titulo": "Poesia crítica do direito", "url": "poesia-critica-do-direito.html",
     "descricao": "Poemas de colunistas do blogue da assessoria jurídica popular.",
     "fonte": "https://assessoriajuridicapopular.blogspot.com/2012/07/poesia-critica-do-direito.html"},
    {"tipo": "Obra", "titulo": "Dissertação — Christianny Diógenes Maia", "url": "dissertacao-christianny-diogenes-maia.html",
     "descricao": "Pesquisa acadêmica sobre assessoria jurídica popular."},
    {"tipo": "Obra", "titulo": "Dissertação — Humberto Betinho Góes (UFPB, 2008)", "url": "dissertacao-humberto-betinho-goes-ufpb-2008.html",
     "descricao": "Dissertação sobre AJP e educação popular."},
    {"tipo": "Obra", "titulo": "Monografia — Andressa Chiamulera (UFPR, 2003)", "url": "monografia-andressa-chiamulera-ufpr-2003.html",
     "descricao": "Monografia sobre assessoria jurídica popular universitária."},
    {"tipo": "Obra", "titulo": "Monografia — Ivan Furmann (UFPR, 2003)", "url": "monografia-ivan-furmann-ufpr-2003.html",
     "descricao": "Monografia sobre crítica jurídica e AJP."},
    {"tipo": "Obra", "titulo": "Monografia — Murilo Sampaio Oliveira (UFBA, 2003)", "url": "monografia-murilo-sampaio-oliveira-ufba-2003.html",
     "descricao": "Monografia sobre assessoria jurídica popular."},
    {"tipo": "Obra", "titulo": "Livro — Advocacia popular e Lyra Filho", "url": "livro-sobre-advocacia-popular-e-lyra-filho.html",
     "descricao": "Livro sobre advocacia popular e o pensamento de Roberto Lyra Filho."},
    {"tipo": "Obra", "titulo": "Livro — Vladimir Luz", "url": "livro-vladimir-luz.html",
     "descricao": "Obra sobre direito, política e lutas populares."},
    {"tipo": "Obra", "titulo": "Livro — Justiça e direitos humanos", "url": "livro-justica-e-direitos-humanos-sobre-experiencias-de.html",
     "descricao": "Experiências de assessoria jurídica popular."},
    {"tipo": "Dossiê", "titulo": "Direito crítico comparado", "url": "assessoria-juridica-popular-no-mundo.html",
     "descricao": "AJP, direito insurgente, direito achado na rua e uso tático no Brasil, América Latina e mundo."},
]
grava("biblioteca.json", biblioteca)

cultura = [
    {"id": "poesia", "titulo": "Poesia", "descricao": "O Caderno de Poesias, os poemas do blog e as homenagens em verso.",
     "links": [("poemas.html", "Caderno de Poesias e poesia do blog"),
               ("acervo.html?tipo=poesia", "42 posts de poesia no acervo"),
               ("poesia-critica-do-direito.html", "Poesia crítica do direito"),
               ("poema-todas-as-mulheres.html", "Poema “Todas as mulheres”")]},
    {"id": "documentario", "titulo": "Documentários e vídeos", "descricao": "Filmes, vídeos-reportagem, palestras e registros de memória.",
     "links": [("documentario-nao-quero-falar-de-chacina.html", "Documentário: não quero falar de chacina"),
               ("documentario-o-cinema-libertario.html", "Documentário: o cinema libertário"),
               ("antropologia-juridica-videos-sobre-comunidades-tradicionais.html", "Vídeos sobre comunidades tradicionais"),
               ("os-quilombolas-e-o-estado-video-reportagem-sobre-o-quilombo.html", "Vídeo-reportagem: quilombo de São João"),
               ("registro-historico-e-ajp-um-video-de-coraje.html", "Registro histórico e AJP: CORAJE"),
               ("video-com-palestra-do-enrique-dussel.html", "Palestra de Enrique Dussel")]},
    {"id": "cinema-teatro-musica", "titulo": "Cinema, teatro e música", "descricao": "Cultura popular, cineclube, teatro do oprimido e música.",
     "links": [("cinema-e-luta-no-campo.html", "Cinema e luta no campo"),
               ("papo-de-cinema.html", "Papo de Cinema"),
               ("teatro-do-oprimido-e-assessoria-juridica-popular-duas.html", "Teatro do Oprimido e AJP"),
               ("relato-de-experiencia-com-o-teatro-do-oprimido.html", "Relato de experiência com Teatro do Oprimido"),
               ("coraje-e-musica.html", "CORAJE e música"),
               ("cultura-negra-historia-e-musica.html", "Cultura negra: história e música")]},
    {"id": "cronicas", "titulo": "Crônicas e narrativas", "descricao": "Textos que narram o conflito, o cotidiano e a resistência.",
     "links": [("imbituba-cronica-de-um-mandado-de-despejo.html", "Imbituba: crônica de um mandado de despejo"),
               ("relato-em-praca-de-guerra.html", "Relato em praça de guerra"),
               ("o-dia-9-o-dia-10-o-dia-11-e-o-dia-12.html", "O dia 9, o dia 10, o dia 11 e o dia 12"),
               ("justica-poetica.html", "Justiça poética")]},
]
grava("cultura.json", cultura)
print("dados das coleções gerados")
