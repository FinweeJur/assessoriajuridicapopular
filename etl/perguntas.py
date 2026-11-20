"""Perguntas e respostas curadas do acervo."""
import io
import json

PERGUNTAS = [
    {
        "id": "ajp",
        "pergunta": "O que é assessoria jurídica popular?",
        "resposta": "É o trabalho de advogados, advogadas, estudantes e educadores com movimentos sociais: orientação jurídica, educação popular e organização. Não é caridade nem assistência gratuita — o protagonismo é de quem vive o conflito.",
        "links": [
            {"texto": "Texto de 2009", "url": "o-que-e-assessoria-juridica-popular.html"},
            {"texto": "Seção AJP", "url": "assessoria-juridica-popular.html"},
        ],
    },
    {
        "id": "anos",
        "pergunta": "Quantos textos tem o acervo e de que anos?",
        "resposta": "São 713 textos publicados entre 2009 e 2024. 2010 e 2011 concentram 450; 2014 não tem publicação; depois de 2016 são 22 textos, mais de memória e balanço do que de notícia.",
        "links": [
            {"texto": "Ver o acervo", "url": "acervo.html"},
            {"texto": "Blog por ano", "url": "blog.html"},
            {"texto": "Linha do tempo", "url": "linha-do-tempo.html"},
        ],
    },
    {
        "id": "tipos",
        "pergunta": "Que tipos de publicação existem?",
        "resposta": "Textos formativos (362), eventos (135), resenhas (111), poesias (42), notícias (37) e documentos (26). O filtro de tipo fica no topo do acervo.",
        "links": [{"texto": "Filtrar por tipo", "url": "acervo.html"}],
    },
    {
        "id": "autores",
        "pergunta": "Quem escreve no acervo?",
        "resposta": "29 pessoas assinam os 713 textos. Entre elas, Luiz Otávio Ribas, Ricardo Prestes Pazello, Assis Oliveira e muitos militantes e pesquisadores. “Redação da Página” reúne as assinaturas genéricas do blog.",
        "links": [
            {"texto": "Todos os autores", "url": "autores.html"},
            {"texto": "Ribas", "url": "autor-luiz-otavio-ribas.html"},
            {"texto": "Pazello", "url": "autor-ricardo-prestes-pazello.html"},
        ],
    },
    {
        "id": "secoes",
        "pergunta": "Quais são as seções e quantos textos cada uma tem?",
        "resposta": "Assessoria jurídica popular (97), direitos humanos (76), movimentos sociais (170), memória e cultura (30), teoria crítica (182) e educação popular (158).",
        "links": [
            {"texto": "Assessoria jurídica popular", "url": "assessoria-juridica-popular.html"},
            {"texto": "Direitos humanos", "url": "direitos-humanos.html"},
            {"texto": "Movimentos sociais", "url": "movimentos-sociais.html"},
            {"texto": "Teoria crítica", "url": "teoria-critica.html"},
        ],
    },
    {
        "id": "citar",
        "pergunta": "Como citar um texto do acervo?",
        "resposta": "Cada página traz autor, data, link para o original e data de captura. O botão “Copiar citação ABNT” monta a referência com “Disponível em” e “Acesso em”.",
        "links": [{"texto": "Ver um exemplo", "url": "o-que-e-assessoria-juridica-popular.html"}],
    },
    {
        "id": "teoria",
        "pergunta": "Como o blog dialoga com a teoria crítica?",
        "resposta": "A página do comparado organiza quatro perspectivas: assessoria jurídica popular, direito insurgente, direito achado na rua e uso tático do direito. Cada uma responde a uma pergunta diferente, e a página mostra como se combinam na prática.",
        "links": [{"texto": "Direito crítico comparado", "url": "assessoria-juridica-popular-no-mundo.html"}],
    },
    {
        "id": "poemas",
        "pergunta": "O que é o Caderno de Poesias?",
        "resposta": "Uma antologia de 2010 organizada por Cleber Mori. O site publica 135 poemas: 20 em domínio público e 115 por autorização do responsável. Maiakovski ficou de fora porque as traduções têm direitos próprios; João Cabral não tem poema no caderno.",
        "links": [
            {"texto": "Ler os poemas", "url": "poemas.html"},
            {"texto": "Índice do caderno", "url": "caderno-de-poesias.html"},
        ],
    },
    {
        "id": "dados",
        "pergunta": "Que dados cada página traz?",
        "resposta": "Autor, data de publicação, link do original, data de captura, tema principal, palavras-chave e, quando existe, crédito da imagem. É o suficiente para conferir a fonte e citar.",
        "links": [{"texto": "Abrir o acervo", "url": "acervo.html"}],
    },
    {
        "id": "buscar",
        "pergunta": "Como buscar por tema, autor ou ano?",
        "resposta": "Na página Acervo, use a busca por título, autor ou palavra-chave; os chips de tipo; o filtro de ano; o filtro de palavra-chave; e a ordem (recente, antigo ou título).",
        "links": [{"texto": "Ir para a busca", "url": "acervo.html"}],
    },
    {
        "id": "renap",
        "pergunta": "O que é a RENAP?",
        "resposta": "A Rede Nacional de Advogados e Advogadas Populares articula profissionais do direito comprometidos com as lutas populares desde 1995. É uma das parcerias deste acervo.",
        "links": [{"texto": "Site da RENAP", "url": "https://www.renap.org.br/"}],
    },
    {
        "id": "ia",
        "pergunta": "O acervo usa inteligência artificial?",
        "resposta": "O chatbot é uma busca local nos 713 textos: devolve trechos com autor, ano e link, sem modelo generativo. As perguntas curadas têm resposta fixa e revisada. Quando não encontra, indica a busca do acervo.",
        "links": [{"texto": "Buscar no acervo", "url": "acervo.html"}],
    },
]

p = r"X:\DevCoder\assessoriajuridicapopular\dados\perguntas.json"
io.open(p, "w", encoding="utf-8", newline="\n").write(
    json.dumps(PERGUNTAS, ensure_ascii=False, indent=1))
print("perguntas:", len(PERGUNTAS))
