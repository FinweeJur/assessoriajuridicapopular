"""Monta o dossiê LeapSpace: página própria, resumo no comparado e arquivos .md.

Entrada: dados/leapspace-refs.json (etl/coleta-refs.py).
Saídas:
  - dossie-leapspace.html
  - dados/dossie-leapspace.md
  - dados/leapspace/advocacia-popular.md
  - dados/leapspace/pesquisa-socialmente-orientada.md
  - resumo com link dentro de assessoria-juridica-popular-no-mundo.html
"""
import html
import importlib.util
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = os.path.join(RAIZ, "dossie-leapspace.html")
MUNDO = os.path.join(RAIZ, "assessoria-juridica-popular-no-mundo.html")
REFS = os.path.join(RAIZ, "dados", "leapspace-refs.json")
MD = os.path.join(RAIZ, "dados", "dossie-leapspace.md")

spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)


def esc(t):
    return html.escape(t or "", quote=False)


def carrega_refs():
    if os.path.exists(REFS):
        return json.load(io.open(REFS, encoding="utf-8"))
    return []


TABELA_ACHADOS = [
    ("Campo híbrido", "Defensorias, assistência municipal, extensão e clínicas universitárias, ONGs e assessorias de movimentos — sem arquitetura nacional integrada.",
     "Populações de baixa renda, periferias, territórios rurais e remotos.", "Alta"),
    ("Defensorias desiguais", "A expansão pós-1988 variou entre estados por causa de arranjos anteriores com advocacia privada e Procuradorias-Gerais.",
     "Desigualdades federativas e regionais.", "Alta"),
    ("Gargalo de capacidade", "Recursos, coordenação interna, monitoramento, parceria com a sociedade civil e financiamento estável condicionam cobertura e qualidade.",
     "Defensorias, clínicas, projetos locais e triagens multidisciplinares.", "Alta"),
    ("Acesso territorializado", "Periferias, áreas rurais, Amazônia e comunidades ribeirinhas enfrentam distância, transporte precário, baixa presença estatal e exclusão digital.",
     "Populações negras, pobres, periféricas, indígenas e ribeirinhas.", "Alta"),
    ("Mobilização e repressão", "Em terra, moradia e trabalho, o uso do direito amplia reivindicações, mas também pode gerar criminalização e tratamento judicial hostil.",
     "Trabalhadores rurais, movimentos de moradia, trabalhadoras domésticas.", "Alta"),
    ("Resultados pouco medidos", "A literatura descreve serviços e arranjos com mais frequência do que mede duração processual, êxito, cumprimento de decisões ou reconhecimento de direitos.",
     "Todo o campo de acesso à justiça.", "Alta"),
]

TABELA_AJUP = [
    ("Clínicas jurídicas", "Serviço jurídico com formação prática e foco em justiça social.",
     "Forma mais próxima da assessoria jurídica universitária popular."),
    ("Clínicas de direitos humanos", "Mapeiam implementação e resultados em universidades brasileiras.",
     "Ligam formação jurídica, direitos humanos e prática social."),
    ("Extensão em direito com a comunidade", "Atividades extensionistas de consciência cidadã e acesso à justiça.",
     "Aproximam universidade e população em chave emancipatória."),
    ("Educação jurídica popular", "Alfabetização jurídica, participação e fortalecimento comunitário.",
     "Eixo central da AJUP, sobretudo no trabalho territorial."),
    ("Inspiração freireana e Direito Achado na Rua", "Relação horizontal entre academia e comunidade.",
     "Base pedagógica e política mais compatível com a AJUP."),
]

TABELA_INSURGENTE = [
    ("Movimentos sociais", "MST, ocupações urbanas e lutas por moradia combinam disputa territorial, reivindicação de direitos e judicialização seletiva.",
     "O conflito social é espaço de produção de legitimidade, não só de infração."),
    ("Educação jurídica crítica", "Redemocratização e Constituição de 1988 abrem espaço a pedagogias emancipadoras e ao Direito Achado na Rua.",
     "O saber jurídico passa a ser situado, dialogado e comprometido com a emancipação."),
    ("Pluralismo jurídico", "Práticas normativas comunitárias, jurisdições indígenas e quilombolas, arranjos comunitários.",
     "Existem normatividades não redutíveis ao monismo estatal."),
]

TABELA_TATICO = [
    ("Litigação estratégica", "Movimentos feministas, ambientais e de direitos sociais recorrem aos tribunais para ampliar oportunidades políticas e produzir mudança institucional.",
     "O direito é ferramenta de pressão e de abertura de espaço político, não apenas de ganhar a causa."),
    ("Alianças e enquadramento", "Organizações adaptam frames, constroem alianças com atores jurídicos e mobilizam recursos legais e discursivos.",
     "O uso tático depende da leitura de contexto, do enquadramento e da capacidade de coalizão."),
    ("Judiciário como arena", "Mobilizações usam a corte mesmo com chance incerta de vitória, porque ela dá visibilidade e legitimação.",
     "O tribunal é arena tática para sinalizar resistência e forçar resposta institucional."),
    ("Limites e riscos", "O uso do direito pode gerar criminalização, respostas hostis, captura institucional ou resultados parciais e lentos.",
     "Escolher quando recorrer ao direito sabendo que ele é ambivalente."),
]

TABELA_POSITIVISMO = [
    ("Positivismo jurídico", "Define o direito a partir de normas postas pelo Estado, separando-o da moral e de outras ordens normativas.",
     "Vira alvo de crítica quando reduzido a formalismo ou mecanicismo."),
    ("Positivismo crítico", "Reconhece o contexto político e socioeconômico das regras sem abandonar parâmetros descritivos controláveis.",
     "Uso mais próximo de um positivismo “de combate”: não abandona o positivismo, mobiliza-o contra a norma cega."),
    ("Crítica ao formalismo", "Autores brasileiros criticam a versão legalista e defendem sua reformulação ou superação parcial.",
     "O combate se dirige ao formalismo, não ao direito posto em si."),
]

TABELA_ADVOCACIA = [
    ("Base política", "Liga-se a movimentos sociais, participação popular e lutas por cidadania.",
     "O direito amplia voz e poder coletivo, não só resolve casos individuais."),
    ("Forma de atuação", "Reúne litígio estratégico, assessoria comunitária, educação jurídica popular e trabalho territorial.",
     "A advocacia é mista: jurídica, pedagógica e organizativa."),
    ("Públicos prioritários", "Grupos vulnerabilizados, periferias, populações pobres, comunidades em conflito fundiário, ambiental e de moradia.",
     "O foco está em desigualdades concretas de acesso à justiça."),
    ("Método", "Valoriza clientes mobilizados, advocacia integrada e participação de base.",
     "O protagonismo fica com os sujeitos coletivos afetados, com apoio técnico-jurídico."),
]

TABELA_PESQUISA = [
    ("Parceria e coprodução", "Pesquisadores e comunidade compartilham decisão, conhecimento e responsabilidade.", "Alta"),
    ("Orientação para ação social", "A pesquisa busca gerar transformação, não só descrição.", "Alta"),
    ("Redução de desigualdades", "É usada para enfrentar iniquidades, vulnerabilidade e marginalização.", "Alta"),
    ("Processo flexível e iterativo", "O desenho é adaptável, com planejamento, replanejamento e reflexão contínua.", "Alta"),
    ("Ênfase ética e poder", "Exige atenção a consentimento, assimetria de poder e relação com a comunidade.", "Alta"),
]

CONTEUDO = [
    {
        "id": "ajp-brasil",
        "titulo": "AJP no Brasil: um campo plural, não uma instituição única",
        "resumo": "Defensoria, municípios, extensão, clínicas, ONGs e movimentos sociais compõem um ecossistema fragmentado.",
        "paras": [
            "No Brasil, a assessoria jurídica popular aparece menos como instituição única e mais como um ecossistema "
            "fragmentado: Defensoria Pública, assistência jurídica municipal, extensão universitária e clínicas, "
            "escritórios-modelo, ONGs e assessorias ligadas a movimentos sociais. O que a evidência sustenta com mais "
            "força é que o desempenho do campo depende de quatro fatores: capacidade institucional, enraizamento "
            "territorial, financiamento e parcerias estáveis, e articulação com demandas coletivas reais.",
            "Os efeitos mais bem documentados estão em três frentes: ampliação procedimental do acesso por serviços "
            "próximos, itinerantes ou simplificados; formação profissional orientada ao interesse público; e apoio à "
            "mobilização por terra, moradia e trabalho — esta última sob risco de repressão judicial e criminalização.",
            "A literatura descreve arranjos, barreiras territoriais e mobilização jurídica com muito mais força do que "
            "mede resultados jurídicos finais em escala nacional. A desigualdade federativa e territorial — periferias, "
            "ruralidade e Amazônia — segue sendo o principal limite.",
        ],
        "tabela": (("Achado", "O que a evidência indica", "Grupos e territórios", "Confiança"), TABELA_ACHADOS,
                   "Tabela original do dossiê LeapSpace, resumida."),
        "nota": "Confiança alta na conclusão central: há convergência entre estudos históricos, institucionais e territoriais.",
    },
    {
        "id": "ajup",
        "titulo": "AJUP e extensão universitária popular",
        "resumo": "Um campo de práticas extensionistas — clínicas, SAJU, NAJUP, AJUP, CORAJE —, não um modelo único.",
        "paras": [
            "AJUP e RENAJU designam um campo de práticas extensionistas, não um modelo único. As formas mais próximas "
            "são clínicas jurídicas, clínicas de direitos humanos, extensão jurídica comunitária, educação popular em "
            "direitos e projetos inspirados em Paulo Freire e no Direito Achado na Rua. Cada grupo tem nome próprio — "
            "SAJU, NAJUP, AJUP, CORAJE, entre outros — e combina formação discente, serviço à comunidade e compromisso "
            "com justiça social.",
            "O ponto forte é a ligação entre universidade e território. O ponto fraco recorrente é a dependência de "
            "recursos, apoio institucional e continuidade. A pesquisa sobre clínicas brasileiras ainda descreve mais "
            "formatos e objetivos do que resultados de larga escala.",
        ],
        "tabela": (("Tipo de projeto", "O que faz", "Por que se conecta à AJUP"), TABELA_AJUP, None),
        "nota": "Confiança alta sobre a existência do campo; média sobre resultados em larga escala.",
    },
    {
        "id": "direito-achado-na-rua",
        "titulo": "Direito Achado na Rua",
        "resumo": "O direito também nasce das lutas sociais, das experiências coletivas e da mobilização popular.",
        "paras": [
            "É uma corrente crítico-emancipatória que entende o direito como construção das lutas sociais, das "
            "experiências coletivas e das práticas de mobilização popular — não apenas como produto do Estado ou dos "
            "tribunais. A formulação ganha força na redemocratização e na Constituição de 1988, junto com pedagogias "
            "emancipatórias e o debate sobre a função social da universidade e do ensino jurídico.",
            "A proposta parte da noção de que as demandas sociais concretas podem produzir sentido jurídico e "
            "influenciar a interpretação do direito, sobretudo quando grupos marginalizados usam o repertório jurídico "
            "para reivindicar direitos, reconhecimento e transformação institucional.",
            "Ela se conecta a três frentes: movimentos sociais e mobilização jurídica, educação jurídica crítica e "
            "direitos humanos e lutas por reconhecimento. Em uma frase: o direito também é produzido “na rua”, na "
            "experiência coletiva e na disputa política por justiça.",
        ],
        "tabela": None,
        "nota": "Confiança alta: as fontes convergem sobre a ligação com redemocratização, mobilização social e educação jurídica crítica.",
    },
    {
        "id": "direito-insurgente",
        "titulo": "Direito insurgente",
        "resumo": "A produção jurídica “de baixo para cima”, em tensão com o direito estatal hegemônico.",
        "paras": [
            "É uma vertente crítica que vê a produção jurídica “de baixo para cima”, a partir de lutas sociais, "
            "coletividades marginalizadas e práticas de resistência, em tensão com o direito estatal hegemônico. Nas "
            "fontes, a formulação aparece como insurgent legality, hermenêutica dos oprimidos e pluralismo jurídico "
            "transformador.",
            "O ponto central é que a resistência não é só reação política: pode funcionar como fundamento de uma ordem "
            "jurídica emergente. No Brasil, isso se aproxima dos movimentos por terra e moradia, da educação jurídica "
            "crítica e das normatividades indígenas, quilombolas e comunitárias.",
        ],
        "tabela": (("Frente", "O que aparece", "Sentido para o direito insurgente"), TABELA_INSURGENTE, None),
        "nota": "Confiança alta: convergência sobre movimentos sociais, pluralismo jurídico e produção normativa “de baixo”.",
    },
    {
        "id": "uso-tatico",
        "titulo": "Uso tático do direito",
        "resumo": "O direito como recurso político, combinado com mobilização coletiva — não como substituto dela.",
        "paras": [
            "É o uso estratégico e situado de instrumentos jurídicos — ações judiciais, amicus curiae, litígio "
            "estratégico, audiências e outras vias institucionais — para avançar objetivos políticos, sociais ou de "
            "direitos, geralmente combinado com mobilização coletiva mais ampla, e não como substituto dela.",
            "A formulação mais próxima nas fontes é a de mobilização jurídica estratégica: os movimentos não tratam o "
            "direito como esfera neutra, mas como recurso político acionado dentro de estruturas de oportunidade legais "
            "e institucionais. Isso dialoga com o Direito Achado na Rua e com o horizonte do direito insurgente.",
        ],
        "tabela": (("Dimensão", "Como aparece nas fontes", "Sentido para o uso tático"), TABELA_TATICO, None),
        "nota": "O termo exato “uso tático do direito” não aparece como definição estabilizada nas fontes recuperadas; "
                "a síntese é uma aproximação a partir de litígio estratégico, enquadramento e mobilização jurídica.",
    },
    {
        "id": "positivismo-de-combate",
        "titulo": "Positivismo de combate e pluralismo jurídico",
        "resumo": "Usar o direito posto contra o formalismo, sem ignorar as ordens jurídicas que existem ao lado dele.",
        "paras": [
            "“Positivismo de combate” não aparece como termo definido nas fontes. O sentido mais defensável é o de um "
            "uso crítico e estratégico do positivismo para confrontar formalismo rígido, decisões arbitrárias e "
            "leituras dogmáticas fechadas do direito — preservando a disciplina da análise jurídica, mas contra o "
            "legalismo estreito e a cegueira institucional diante da realidade social.",
            "Em chave pluralista, a disputa pela norma convive com outras ordens jurídicas: práticas comunitárias, "
            "jurisdições indígenas e quilombolas, arranjos de justiça populares. Reconhecer esse pluralismo não dispensa "
            "o direito estatal — desloca o monopólio estatal da produção jurídica.",
        ],
        "tabela": (("Noção", "O que indica", "Como se relaciona ao “combate”"), TABELA_POSITIVISMO, None),
        "nota": "Confiança média: há base sólida para o sentido inferido, mas o termo exato não foi encontrado nas fontes.",
    },
    {
        "id": "advocacia-popular",
        "titulo": "Advocacia popular",
        "resumo": "Prática jurídica comprometida com movimentos e sujeitos coletivos, entre a técnica e a organização.",
        "paras": [
            "Advocacia popular é uma forma de atuação jurídica orientada por direitos, movimentos sociais e "
            "transformação social, na qual o direito é usado como recurso de organização, reivindicação e disputa "
            "política, e não apenas como prestação técnica individual. No Brasil, ela aparece sobretudo em articulação "
            "com a assessoria jurídica popular universitária (AJUP), clínicas jurídicas, educação popular em direitos e "
            "experiências próximas ao Direito Achado na Rua.",
            "A advocacia popular tende a traduzir conflitos sociais em linguagem jurídica para fortalecer "
            "reivindicações coletivas; ampliar acesso à justiça com proximidade territorial; formar juridicamente "
            "estudantes e profissionais em chave crítica; e articular direitos e democracia como parte de processos de "
            "participação popular.",
        ],
        "tabela": (("Dimensão", "O que aparece nas fontes", "Implicação"), TABELA_ADVOCACIA, None),
        "lista": ("O que ela não é", [
            "Não é apenas assistência jurídica individual tradicional: as fontes distinguem essa lógica de modelos "
            "voltados à transformação social e à mobilização coletiva.",
            "Não depende de uma única instituição: no Brasil, aparece em universidades, organizações da sociedade "
            "civil, movimentos sociais e serviços jurídicos públicos, com formatos variados.",
            "Não é só litígio: o uso do direito é mais eficaz quando combinado com educação, organização comunitária e "
            "ação política mais ampla.",
        ]),
        "nota": "Confiança alta: as fontes convergem sobre a dimensão coletiva, pedagógica e político-transformadora, "
                "embora os formatos institucionais variem bastante.",
    },
    {
        "id": "pesquisa-socialmente-orientada",
        "titulo": "Pesquisa socialmente orientada",
        "resumo": "Pesquisa participativa em que a comunidade é parceira e coprodutora do conhecimento.",
        "paras": [
            "Pesquisa socialmente orientada é uma pesquisa voltada para mudança social, engajamento comunitário e "
            "coprodução de conhecimento, em que comunidades deixam de ser apenas “objetos” de estudo e passam a atuar "
            "como parceiras e co-pesquisadoras ao longo do processo investigativo. Na literatura, isso aparece como "
            "community-based participatory research (CBPR), community-engaged research ou pesquisa-ação participativa.",
            "A abordagem serve para melhorar a relevância da pesquisa para problemas reais da comunidade, fortalecer "
            "capacidades locais e influenciar políticas e práticas, especialmente em saúde pública, educação, trabalho "
            "social e desenvolvimento comunitário.",
        ],
        "tabela": (("Característica", "O que implica", "Evidência"), TABELA_PESQUISA, None),
        "nota": "Confiança alta: revisões, capítulos e estudos conceituais convergem na definição e nos traços centrais.",
    },
]

NOTA_IA = ("Conteúdo gerado por IA (LeapSpace, 21/11/2026). Serve como mapa inicial de leitura: "
           "confira cada afirmação na referência original antes de citar.")


def tabela_html(cabecalho, linhas, dica=None):
    ths = "".join('<th scope="col">%s</th>' % esc(c) for c in cabecalho)
    trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in linha) for linha in linhas)
    dica_html = '<p class="tabela__dica">%s</p>' % esc(dica) if dica else ""
    return ('<div class="tabela cartao"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>%s'
            % (ths, trs, dica_html))


def tabela_md(cabecalho, linhas):
    out = ["| " + " | ".join(cabecalho) + " |", "|" + "|".join(["---"] * len(cabecalho)) + "|"]
    for linha in linhas:
        out.append("| " + " | ".join(c.replace("|", "/") for c in linha) + " |")
    return "\n".join(out)


def selos(r, com_acervo=True):
    out = ['<span class="selo selo--aberto">acesso aberto</span>' if r.get("aberto")
           else '<span class="selo selo--restrito">acesso restrito</span>']
    if r.get("idioma") == "pt":
        out.append('<span class="selo selo--pt">português</span>')
    elif r.get("idioma") == "es":
        out.append('<span class="selo selo--es">espanhol</span>')
    if com_acervo and r.get("acervo_autor"):
        out.append('<a class="selo selo--acervo" href="%s">%s no acervo</a>'
                   % (esc(r["acervo_url"]), esc(r["acervo_autor"].split()[0])))
    return "".join(out)


def lista_refs(refs):
    itens = []
    for r in refs:
        url = r.get("url_aberta") or r["url"]
        veiculo = (r.get("veiculo") or "").strip()
        ano = (r.get("ano") or "").strip()
        meta = ""
        if veiculo or ano:
            meta = '<span class="leapspace__veiculo">%s</span>' % esc(
                " · ".join(x for x in (veiculo, ano) if x))
        itens.append(
            '<li><span class="leapspace__ref-selos">%s</span>'
            '<a class="leapspace__ref-titulo" href="%s" target="_blank" rel="noopener">%s</a>%s</li>'
            % (selos(r), esc(url), esc(r["titulo"]), meta)
        )
    return "\n".join(itens)


def resumo_mundo(refs):
    total = len(refs)
    abertos = sum(1 for r in refs if r.get("aberto"))
    em_pt = sum(1 for r in refs if r.get("idioma") == "pt")
    return """<section class="secao" id="leapspace" aria-labelledby="leapspace-titulo">
      <div class="secao__cabeca"><h2 id="leapspace-titulo">LeapSpace: dossiê em oito sínteses</h2>
      <p class="secao__nota">Respostas geradas por IA em 21/11/2026 · revisão editorial pendente</p></div>
      <div class="leapspace__painel">
        <div><b>8</b><span>eixos de síntese</span></div>
        <div><b>%d</b><span>referências</span></div>
        <div><b>%d</b><span>em acesso aberto</span></div>
        <div><b>%d</b><span>em português</span></div>
      </div>
      <p>O dossiê reúne oito respostas do LeapSpace: AJP no Brasil, AJUP e extensão universitária, Direito Achado na
      Rua, direito insurgente, uso tático do direito, positivismo de combate e pluralismo jurídico, advocacia popular e
      pesquisa socialmente orientada. Cada eixo traz uma síntese, uma tabela e as referências que a sustentam.</p>
      <p>Todas as referências citadas foram mantidas e estão ordenadas por prioridade de acesso: primeiro as de
      <b>acesso aberto</b>, depois as de <b>acesso restrito</b>; dentro de cada grupo, <b>português</b>, <b>espanhol</b>
      e <b>inglês</b>. Quem assina texto no acervo ganha destaque e link direto.</p>
      <p class="colecao__nota">%s</p>
      <p><a class="botao" href="dossie-leapspace.html">Ler o dossiê completo e as %d referências</a>
      <a class="botao secundario" href="dados/dossie-leapspace.md">Baixar em Markdown</a></p>
    </section>""" % (total, abertos, em_pt, esc(NOTA_IA), total)


def monta_pagina(refs):
    total = len(refs)
    abertos = sum(1 for r in refs if r.get("aberto"))
    em_pt = sum(1 for r in refs if r.get("idioma") == "pt")
    em_es = sum(1 for r in refs if r.get("idioma") == "es")
    no_acervo = sum(1 for r in refs if r.get("acervo_autor"))

    sumario = "".join(
        '<li><a href="#%s">%s</a> <span>%s</span></li>'
        % (esc(s["id"]), esc(s["titulo"]), esc(s["resumo"])) for s in CONTEUDO
    )

    secoes = []
    for s in CONTEUDO:
        corpo = ["<h3>%s</h3>" % esc(s["titulo"])]
        corpo += ["<p>%s</p>" % esc(p) for p in s["paras"]]
        if s.get("tabela"):
            cabecalho, linhas, dica = s["tabela"]
            corpo.append(tabela_html(cabecalho, linhas, dica))
        if s.get("lista"):
            titulo_lista, itens = s["lista"]
            corpo.append("<h4>%s</h4><ul>%s</ul>" % (esc(titulo_lista),
                                                     "".join("<li>%s</li>" % esc(i) for i in itens)))
        if s.get("nota"):
            corpo.append('<p class="colecao__nota">%s</p>' % esc(s["nota"]))
        secoes.append(
            '<details class="acordeao" id="%s"><summary><span class="acordeao__rotulo">%s</span>'
            '<span class="acordeao__dica">%s</span></summary>'
            '<div class="acordeao__corpo">%s</div></details>'
            % (esc(s["id"]), esc(s["titulo"]), esc(s["resumo"]), "".join(corpo))
        )

    corpo = """<section class="secao">
      <div class="secao__cabeca"><h2>Oito sínteses para começar</h2></div>
      <p class="colecao__nota">%s</p>
      <div class="leapspace__painel">
        <div><b>%d</b><span>referências</span></div>
        <div><b>%d</b><span>em acesso aberto</span></div>
        <div><b>%d</b><span>em português</span></div>
        <div><b>%d</b><span>autoria no acervo</span></div>
      </div>
      <p>A ordem de leitura sugerida é: o campo da AJP, a extensão universitária, as três teorias de base (Direito
      Achado na Rua, direito insurgente, positivismo de combate e pluralismo), o uso tático do direito e, por fim, a
      advocacia popular e a pesquisa socialmente orientada. Cada bloco abre em acordeão para não alongar a página.</p>
      <ul class="linhas">%s</ul>
    </section>

    <section class="secao" aria-labelledby="eixos-titulo">
      <div class="secao__cabeca"><h2 id="eixos-titulo">Os oito eixos</h2>
      <p class="secao__nota">Clique para abrir. Os acordeões aceitam link direto: #ajp-brasil, #ajup, #uso-tatico…</p></div>
      %s
    </section>

    <section class="secao" id="referencias-leapspace" aria-labelledby="refs-titulo">
      <div class="secao__cabeca"><h2 id="refs-titulo">Referências do dossiê</h2>
      <p class="secao__nota">%d no total · %d em acesso aberto · %d em português · %d em espanhol · %d com autoria no acervo</p></div>
      <p class="colecao__nota">A lista reúne <b>todas</b> as referências citadas nas oito respostas, sem exclusão.
      A ordem prioriza o que está em <b>acesso aberto</b> e, dentro de cada grupo, o que está em <b>português</b>,
      depois <b>espanhol</b> e <b>inglês</b>. Quem assina texto no acervo aparece com selo e link. O status de acesso foi
      consultado no Unpaywall em 21/11/2026 e pode mudar; quando o texto não está livre, o link leva ao DOI ou à página
      da editora.</p>
      <p class="leapspace__legenda"><span class="selo selo--aberto">acesso aberto</span>
      <span class="selo selo--restrito">acesso restrito</span>
      <span class="selo selo--pt">português</span><span class="selo selo--es">espanhol</span>
      <span class="selo selo--acervo">autoria no acervo</span></p>
      <details class="acordeao acordeao--refs">
        <summary><span class="acordeao__rotulo">Ver as %d referências</span>
        <span class="acordeao__dica">todas as citadas, inclusive as de acesso restrito</span></summary>
        <div class="acordeao__corpo"><ol class="leapspace__refs">%s</ol></div>
      </details>
      <p class="colecao__nota">Arquivos para reuso: <a href="dados/dossie-leapspace.md">dossiê completo em Markdown</a>,
      <a href="dados/leapspace/advocacia-popular.md">advocacia popular</a> e
      <a href="dados/leapspace/pesquisa-socialmente-orientada.md">pesquisa socialmente orientada</a>.</p>
    </section>""" % (esc(NOTA_IA), total, abertos, em_pt, no_acervo, sumario, "".join(secoes),
                    total, abertos, em_pt, em_es, no_acervo, total, lista_refs(refs))

    return """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dossiê LeapSpace: oito sínteses sobre AJP · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="Oito sínteses geradas por IA sobre AJP no Brasil, AJUP, Direito Achado na Rua, direito insurgente, uso tático, positivismo de combate, advocacia popular e pesquisa socialmente orientada, com as referências completas." />
  <link rel="icon" href="data:," />
  <link rel="stylesheet" href="fontes/fontshare.css?v=3" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=85" />
  <link rel="stylesheet" href="reveal.css?v=82" />
  <link rel="stylesheet" href="componentes/radio.css" />
  <link rel="stylesheet" href="leitura.css?v=1" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s
<main id="conteudo">
  <section class="hero hero--texto colecao-hero">
    <div class="hero__interno">
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Dossiê de leitura</p>
      <h1>LeapSpace: oito sínteses sobre AJP</h1>
      <p class="lead">AJP no Brasil, AJUP, Direito Achado na Rua, direito insurgente, uso tático, positivismo de
      combate, advocacia popular e pesquisa socialmente orientada — com as referências completas.</p>
    </div>
  </section>
  <div class="miolo">
%s
  </div>
</main>
%s
<script src="casca.js?v=27" defer></script>
<script src="leitura.js?v=3" defer></script>
<script src="reveal.js?v=75" defer></script>
<script src="fundo-grade.js?v=6" defer></script>
</body>
</html>
""" % (ms.topo("comparado"), corpo, ms.rodape())


def md_texto(refs):
    linhas = [
        "# Dossiê LeapSpace: oito sínteses sobre assessoria jurídica popular",
        "",
        "> " + NOTA_IA,
        "",
        "Gerado por LeapSpace em 21/11/2026. Edição e curadoria: acervo AJP.",
        "",
    ]
    for s in CONTEUDO:
        linhas += ["## %s" % s["titulo"], "", "**%s**" % s["resumo"], ""]
        for p in s["paras"]:
            linhas += [p, ""]
        if s.get("tabela"):
            cabecalho, rows, dica = s["tabela"]
            linhas += [tabela_md(cabecalho, rows), ""]
            if dica:
                linhas += ["*%s*" % dica, ""]
        if s.get("lista"):
            titulo_lista, itens = s["lista"]
            linhas += ["### %s" % titulo_lista, ""]
            linhas += ["- %s" % i for i in itens]
            linhas += [""]
        if s.get("nota"):
            linhas += ["*%s*" % s["nota"], ""]

    linhas += ["## Referências", "",
               "Total: %d. A ordem prioriza acesso aberto e, dentro de cada grupo, português, espanhol e inglês."
               % len(refs), ""]
    for i, r in enumerate(refs, 1):
        estado = "acesso aberto" if r.get("aberto") else "acesso restrito"
        idioma = {"pt": "português", "es": "espanhol"}.get(r.get("idioma"), "inglês")
        extra = ""
        if r.get("acervo_autor"):
            extra = " — autoria no acervo: %s (%s)" % (r["acervo_autor"], r["acervo_url"])
        linhas.append("%d. %s — %s. %s, %s%s" % (i, r["titulo"], r.get("veiculo") or "sem veículo",
                                                  estado, idioma, extra))
        linhas.append("   <%s>" % (r.get("url_aberta") or r["url"]))
    linhas.append("")
    return "\n".join(linhas)


def md_secao(refs, secao_id, titulo, ids):
    s = next(x for x in CONTEUDO if x["id"] == secao_id)
    linhas = ["# %s" % titulo, "", "> " + NOTA_IA, "", "**%s**" % s["resumo"], ""]
    for p in s["paras"]:
        linhas += [p, ""]
    if s.get("tabela"):
        cabecalho, rows, dica = s["tabela"]
        linhas += [tabela_md(cabecalho, rows), ""]
        if dica:
            linhas += ["*%s*" % dica, ""]
    if s.get("lista"):
        titulo_lista, itens = s["lista"]
        linhas += ["## %s" % titulo_lista, ""] + ["- %s" % i for i in itens] + [""]
    if s.get("nota"):
        linhas += ["*%s*" % s["nota"], ""]
    citadas = [r for r in refs if r.get("id") in ids]
    linhas += ["## Referências citadas", ""]
    for r in citadas:
        estado = "acesso aberto" if r.get("aberto") else "acesso restrito"
        idioma = {"pt": "português", "es": "espanhol"}.get(r.get("idioma"), "inglês")
        linhas.append("- %s — %s (%s)" % (r["titulo"], estado, idioma))
        linhas.append("  <%s>" % (r.get("url_aberta") or r["url"]))
    linhas.append("")
    return "\n".join(linhas)


REFS_ADVOCACIA = {"3", "8", "35", "42", "43", "55", "58", "61"} | {str(n) for n in range(114, 139)}
REFS_PESQUISA = {"p%d" % n for n in range(1, 17)}


def main():
    refs = carrega_refs()
    io.open(PAGINA, "w", encoding="utf-8", newline="\n").write(monta_pagina(refs))

    io.open(MD, "w", encoding="utf-8", newline="\n").write(md_texto(refs))
    pasta = os.path.join(RAIZ, "dados", "leapspace")
    os.makedirs(pasta, exist_ok=True)
    io.open(os.path.join(pasta, "advocacia-popular.md"), "w", encoding="utf-8", newline="\n").write(
        md_secao(refs, "advocacia-popular", "Advocacia popular", REFS_ADVOCACIA))
    io.open(os.path.join(pasta, "pesquisa-socialmente-orientada.md"), "w", encoding="utf-8", newline="\n").write(
        md_secao(refs, "pesquisa-socialmente-orientada", "Pesquisa socialmente orientada", REFS_PESQUISA))

    t = io.open(MUNDO, encoding="utf-8").read()
    bloco = resumo_mundo(refs)
    i = t.find('<section class="secao" id="leapspace"')
    if i < 0:
        raise SystemExit("secao leapspace nao encontrada")
    j = t.find("<section", i + 10)
    t = t[:i] + bloco + "\n\n" + t[j:]
    io.open(MUNDO, "w", encoding="utf-8", newline="\n").write(t)

    print("pagina: %d refs | md: %d bytes" % (len(refs), len(io.open(MD, encoding="utf-8").read())))


if __name__ == "__main__":
    main()
