"""Extrai referências citadas do corpo dos posts do acervo AJP (piloto).

Lê apenas HTML local. Não acessa a rede, não baixa nada e não altera os
arquivos de conteúdo: a saída é um JSON novo e, quando pedido, um relatório.

O corpo do post é o `<div class="cartao corpo">` dentro de `<article>`. Desse
bloco saem dois tipos de evidência:

1. **Padrão bibliográfico** — parágrafos (ou sequências autor / título /
   imprenta) com cara de referência ABNT: SOBRENOME, Nome. Título. Local:
   Editora, ano; artigo com revista/volume/página; tese/dissertação;
   relatório; legislação; lista "Título", de Autor.
2. **Link explícito** — href com texto âncora e contexto, excluindo o próprio
   blog, redes sociais, imagens, rodapé, botões e navegação.

Cada registro sai com:
    id, tipo, titulo, autor, ano, veiculo, url, fonte_slug, fonte_titulo,
    trecho, confianca, metodo, motivo

`metodo` diz se veio de `padrao` ou `link`; `motivo` registra por que a
confiança não é alta. Nada é inventado: campo sem evidência fica vazio e a
confiança cai para "baixa".

Uso:
    python etl/extrai-referencias.py                    # piloto (20 páginas)
    python etl/extrai-referencias.py --tudo             # acervo inteiro
    python etl/extrai-referencias.py --debug            # mostra candidatos
"""
import argparse
import hashlib
import html
import io
import json
import os
import random
import re
import sys
import unicodedata
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
SAIDA_PADRAO = os.path.join(RAIZ, "dados", "referencias-piloto.json")
SEMENTE = 20261122

TIPOS = (
    "livro", "capitulo", "artigo", "tese", "dissertacao", "monografia",
    "relatorio", "legislacao", "video", "documento", "site", "obra",
)

# Páginas de bibliografia que precisam entrar no piloto: são o caso mais denso
# e o que mais interessa para a futura busca de link gratuito.
DIRIGIDAS = (
    "biblioteca-digital",
    "biblioteca-ajup-rj",
    "biblioteca-roberto-lyra-filho",
    "biblioteca-miguel-lanzellotti-baldez",
    "biblioteca-joaquin-herrera-flores",
    "biblioteca-digital-da-filosofia-latino-americana",
    "referencias",
)

PARTICULAS = {
    "de", "da", "do", "das", "dos", "e", "del", "la", "las", "los", "van",
    "von", "di", "du", "der", "ter", "y", "a", "o", "as", "os", "em", "para",
}

PALAVRAS_INSTITUICAO = {
    "INSTITUTO", "UNIVERSIDADE", "FACULDADE", "ESCOLA", "CENTRO", "NUCLEO",
    "NÚCLEO", "COMISSAO", "COMISSÃO", "CONSELHO", "FUNDACAO", "FUNDAÇÃO",
    "ASSOCIACAO", "ASSOCIAÇÃO", "ORGANIZACAO", "ORGANIZAÇÃO", "MOVIMENTO",
    "COLETIVO", "REDE", "RENAP", "RENAJU", "AJUP", "SAJU", "NAJUP", "IPDMS",
    "MINISTERIO", "MINISTÉRIO", "SECRETARIA", "REVISTA", "BOLETIM", "CADERNOS",
    "EDITORA", "CPT", "CIMI", "MST", "MTST", "OAB", "ABA", "ANPED",
    "SINDICATO", "PARTIDO", "FORUM", "FÓRUM", "ARTICULACAO", "ARTICULAÇÃO",
}

# Editoras e instituições que ajudam a reconhecer imprenta.
EDITORAS = re.compile(
    r"\b(Editora|Ed\.|Editor|Imprensa|Brasiliense|Boitempo|Lumen Juris|"
    r"Forense|Saraiva|Revista dos Tribunais|Almedina|Vozes|Civilização "
    r"Brasileira|Companhia das Letras|Companhia Editora Nacional|Atica|Ática|"
    r"Sergio Antonio Fabris|Fabris|UnB|Unicamp|USP|UFSC|UFPR|UFRJ|UFBA|"
    r"PUC|Loyola|Vozes|Graal|Paz e Terra|Expressão Popular|Expressao Popular|"
    r"Consequência|Elefante|Autonomia Literária|Hucitec|UNESP|Fiocruz|"
    r"Fundação|Fundacao|Instituto|Centro|Conselho|Secretaria|Ministério|"
    r"Ministerio|AJUP|FASE|CPT|CDDH|CEDECA|MST)\b"
)

MARCA_TIPO = re.compile(
    r"\b(Tese|Dissertação|Dissertacao|Monografia|Relatório|Relatorio|"
    r"Trabalho de Conclusão|TCC|Pesquisa|Diagnóstico|Diagnostico)\b",
    re.I,
)

MARCA_PERIODICO = re.compile(
    r"\b(Revista|Boletim|Cadernos?|Journal|Anuário|Anuario|Kriterion|Doxa|"
    r"Revista de|Revista da|Revista do)\b"
)

MARCA_LEI = re.compile(
    r"^(BRASIL|ESTADO|MUNICÍPIO|MUNICIPIO|UNIÃO|UNIAO)\b|"
    r"\b(Lei|Decreto|Constituição|Constituicao|Medida Provisória|"
    r"Medida Provisoria|Portaria|Resolução|Resolucao|Emenda Constitucional)\b"
    r"\s*(n[ºo°.]?\s*)?[\d.]",
    re.I,
)

MARCA_CAPITULO = re.compile(r"\b(Em|In)\s*:?\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]")

ANO_RE = re.compile(r"\b(1[5-9]\d{2}|20[0-2]\d)[a-z]?\b")

GENERICOS = {
    "ver o vídeo no original", "ver o video no original",
    "ler no blog original", "ver o cartaz no blog original",
    "ver o cartaz no original", "ver o vídeo", "ver o video",
    "fotos", "ver aqui", "ver aqui o índice geral", "ver aqui o indice geral",
    "site oficial", "letra", "clique aqui", "saiba mais", "leia mais",
    "ver mais", "assista aqui", "página oficial", "pagina oficial",
    "blog", "blogue", "twitter", "facebook", "instagram", "youtube",
    "compartilhar", "voltar", "início", "inicio", "paginação da tese",
    "paginacao da tese", "índice geral", "indice geral",
}

REDES = {
    "facebook.com", "www.facebook.com", "twitter.com", "x.com",
    "instagram.com", "www.instagram.com", "linkedin.com", "wa.me",
    "whatsapp.com", "t.me", "telegram.me", "tiktok.com", "pinterest.com",
    "snapchat.com", "mastodon.social", "threads.net",
}

SELF_HOSTS = {
    "assessoriajuridicapopular.blogspot.com",
    "assessoriajuridicapopular.blogspot.com.br",
    "finweejur.github.io",
}

VEICULOS = {
    "youtube.com": "YouTube", "www.youtube.com": "YouTube", "youtu.be": "YouTube",
    "vimeo.com": "Vimeo", "www.vimeo.com": "Vimeo",
    "planalto.gov.br": "Planalto", "www.planalto.gov.br": "Planalto",
    "camara.gov.br": "Câmara dos Deputados",
    "www.camara.gov.br": "Câmara dos Deputados",
    "senado.leg.br": "Senado Federal", "www12.senado.leg.br": "Senado Federal",
    "scribd.com": "Scribd", "www.scribd.com": "Scribd", "pt.scribd.com": "Scribd",
    "issuu.com": "Issuu", "drive.google.com": "Google Drive",
    "repositorio.ufsc.br": "Repositório UFSC",
    "acervodigital.ufpr.br": "Acervo Digital UFPR",
    "bdtd.ibict.br": "BDTD",
    "seer.franca.unesp.br": "Seer UNESP",
    "ihu.unisinos.br": "IHU Unisinos",
    "www.ihu.unisinos.br": "IHU Unisinos",
    "brasildefato.com.br": "Brasil de Fato",
    "www.brasildefato.com.br": "Brasil de Fato",
    "terradedireitos.org.br": "Terra de Direitos",
    "mst.org.br": "MST", "www.mst.org.br": "MST",
    "jornada.unam.mx": "La Jornada", "www.jornada.unam.mx": "La Jornada",
}


# ----------------------------------------------------------------------------
# Leitura do HTML
# ----------------------------------------------------------------------------

class CorpoParser(HTMLParser):
    """Extrai blocos de texto e links de dentro de <article> .corpo."""

    BLOCO = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6",
             "blockquote", "figcaption", "figure", "dt", "dd", "td", "th"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocos = []
        self.tem_artigo = False
        self.tem_corpo = False
        self._artigo = False
        self._captura = False
        self._div = 0
        self._ignorar = 0
        self._bloco = None
        self._ancora = None

    # -- helpers
    def _abre_bloco(self, tag):
        self._fecha_bloco()
        self._bloco = {"tag": tag, "partes": [], "links": []}

    def _fecha_bloco(self):
        if not self._bloco:
            return
        texto = normaliza_espacos("".join(self._bloco["partes"]))
        if texto:
            self.blocos.append({
                "tag": self._bloco["tag"],
                "texto": texto,
                "links": [l for l in self._bloco["links"] if l["href"]],
            })
        self._bloco = None

    def _fecha_ancora(self):
        if not self._ancora:
            return
        texto = normaliza_espacos("".join(self._ancora["partes"]))
        link = {"href": self._ancora["href"], "texto": texto}
        if self._bloco is not None:
            self._bloco["links"].append(link)
        self._ancora = None

    # -- parser
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article":
            self._artigo = True
            self.tem_artigo = True
            return
        if tag == "div":
            classes = (a.get("class") or "").split()
            if not self._captura and self._artigo and "corpo" in classes:
                self._captura = True
                self.tem_corpo = True
                self._div = 1
                return
            if self._captura:
                self._div += 1
            return
        if not self._captura:
            return
        if tag in ("script", "style", "template"):
            self._ignorar += 1
            return
        if self._ignorar:
            return
        if tag in self.BLOCO:
            self._abre_bloco(tag)
            return
        if tag == "a":
            self._fecha_ancora()
            self._ancora = {"href": a.get("href") or "", "partes": []}
            return
        if tag == "br":
            if self._bloco is not None:
                self._bloco["partes"].append("\n")

    def handle_startendtag(self, tag, attrs):
        if not self._captura or self._ignorar:
            return
        if tag == "br" and self._bloco is not None:
            self._bloco["partes"].append("\n")

    def handle_endtag(self, tag):
        if tag == "article":
            self._artigo = False
            return
        if tag == "div":
            if self._captura:
                self._div -= 1
                if self._div <= 0:
                    self._fecha_ancora()
                    self._fecha_bloco()
                    self._captura = False
            return
        if not self._captura:
            return
        if tag in ("script", "style", "template"):
            self._ignorar = max(0, self._ignorar - 1)
            return
        if self._ignorar:
            return
        if tag == "a":
            self._fecha_ancora()
            return
        if tag in self.BLOCO:
            self._fecha_ancora()
            self._fecha_bloco()

    def handle_data(self, data):
        if not self._captura or self._ignorar:
            return
        if self._bloco is not None:
            self._bloco["partes"].append(data)
        if self._ancora is not None:
            self._ancora["partes"].append(data)

    def close(self):
        super().close()
        self._fecha_ancora()
        self._fecha_bloco()


# ----------------------------------------------------------------------------
# Texto e heurísticas
# ----------------------------------------------------------------------------

def normaliza_espacos(t):
    t = (t or "").replace("\xa0", " ")
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r" *\n *", " ", t)
    return t.strip()


def sem_acento(t):
    return unicodedata.normalize("NFD", t or "").encode("ascii", "ignore").decode()


def chave(t):
    t = sem_acento(t or "").lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def limpa_rotulo(t):
    """Tira numeração e marcadores de lista, preservando o texto."""
    t = normaliza_espacos(t)
    while True:
        antes = t
        t = re.sub(r"^(?:\[\s*\d{1,3}\s*\]|\(\s*\d{1,3}\s*\)|\d{1,3}\s*[).])\s*", "", t)
        t = re.sub(r"^(?:[-–—•*·]\s*|Resenha\s*[-–—:]\s*)", "", t, flags=re.I)
        t = re.sub(r"^(?:Fonte|Endere[çc]o|Local|Publicado em)\s*:\s*", "", t, flags=re.I)
        t = t.strip()
        if t == antes:
            return t


def autor_embutido(t):
    """Autor colado no começo do título por falha de pontuação do original."""
    # "SOBRENOME, Nome." / "SOBRENOME, Nome," / "Lyra Filho, Roberto, \"Título\""
    m = re.match(
        r"^([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ'’-]*(?:\s+(?:d[aeo]s?|"
        r"[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ'’-]*)){0,5},\s*"
        r"[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ'’]*(?:\s+[\wÀ-ÿ'’]+){0,4})"
        r"(?=\.\s|,\s*[\"“”]|\s+[\"“]|$)",
        t,
    )
    if m:
        return m.group(1).strip(), t[m.end():].lstrip(" .,")
    # "Pedro Demo. Título" (nome natural, 2–4 palavras) antes de ponto.
    m = re.match(
        r"^([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ'’]+(?:\s+"
        r"(?:d[aeo]s?|[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\wÀ-ÿ'’]+)){1,3})\.\s+(.{10,})$",
        t,
    )
    if m and parece_autor(m.group(1)):
        return m.group(1).strip(), m.group(2).strip()
    return "", t


def extrai_ano(texto):
    if not texto:
        return ""
    # Descarta anos de acesso e de intervalos que não são publicação.
    t = re.sub(r"Acesso em[^.]{0,30}", " ", texto, flags=re.I)
    t = re.sub(r"Dispon[íi]vel em[^.]{0,120}", " ", t, flags=re.I)
    anos = ANO_RE.findall(t)
    if not anos:
        return ""
    # "1788: lutas..." / "2001: uma odisseia..." — ano do título, não da edição.
    if len(anos) == 1:
        m = ANO_RE.search(t)
        if m and m.start() <= 30 and t[m.end():m.end() + 1] == ":":
            return ""
    return anos[-1]


def parece_autor(s):
    s = normaliza_espacos(s).rstrip(".")
    if not (3 <= len(s) <= 150):
        return False
    if any(x in s for x in ('"', "“", "”", ":", "http", "@")):
        return False
    if s[0].islower():
        return False
    if ANO_RE.search(s) or re.search(r"\d", s):
        return False
    if re.search(r"\.\s+[a-záàâãéêíóôõúç]", s):
        return False
    if re.search(r"\s[-–]\s+[a-záàâãéêíóôõúç]", s):
        return False  # "Nome - advogada popular..."
    if re.match(r"^(Por|By)\s", s):
        return False  # byline
    if re.match(r"^(Agradecemos|Agradeço|Queremos|Destacamos|Ressaltamos|"
                r"Vale|Confira|Veja|Vejam|Trata-se|Saiba|Leia|Acesse)\b", s, re.I):
        return False  # frase, não autor
    limpo = re.sub(r"\((?:Org|org|Coord|coord|Ed|ed|Comp|comp)\.?\)", "", s)
    tokens = re.findall(r"[^\W\d_]+(?:'’\-][^\W\d_]+)*", limpo, re.UNICODE)
    if not (2 <= len(tokens) <= 16):
        return False
    significativas = [t for t in tokens if t.lower() not in PARTICULAS]
    if not significativas:
        return False
    cap = sum(1 for t in significativas if t[0].isupper()) / len(significativas)
    todo_caps = sum(1 for t in significativas if t.isupper()) / len(significativas)
    tem_virgula = "," in limpo
    primeiras = [sem_acento(t).upper() for t in tokens[:2]]
    instituicao = any(p in primeiras for p in PALAVRAS_INSTITUICAO)
    if instituicao:
        return True
    if todo_caps >= 0.8 and len(significativas) >= 2:
        return True
    if tem_virgula and cap == 1.0:
        return True
    # Nome próprio sem vírgula: no máximo 4 palavras significativas. Isso
    # evita títulos e frases ("Teorias Críticas do Direito e Assessoria...").
    if cap == 1.0 and not tem_virgula and len(significativas) <= 4:
        return True
    return False


def parece_titulo(s):
    s = normaliza_espacos(s)
    if not (10 <= len(s) <= 500):
        return False
    if s[0].isdigit():
        return False
    if s.endswith(":") or s.lower().startswith(("http", "disponível em", "disponivel em")):
        return False
    if ANO_RE.search(s) and re.match(r"^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\w\s\.]{1,45}:\s", s):
        return False  # imprenta: "São Paulo: Boitempo, 2004."
    if re.match(r"^(Disponível|Disponivel|Acesso|ISBN|DOI)\b", s):
        return False
    palavras = re.findall(r"[\wÁÀÂÃÉÊÍÓÔÕÚÇáàâãéêíóôõúç'’\-]+", s)
    if len(palavras) < 3 and not s.startswith(('"', "“")):
        return False
    if all(p.isupper() for p in palavras if len(p) > 1):
        return False
    return True


def parece_imprenta_titulo(t):
    """'São Paulo: Boitempo, 2004' é imprenta; 'La vida: ensayo' é título."""
    m = re.match(
        r"^([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\w\s\.]{1,40}):\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]", t or ""
    )
    if not m:
        return False
    local = m.group(1).strip()
    palavras = local.split()
    if len(palavras) > 4:
        return False
    return all(
        p.lower() in PARTICULAS or p[0].isupper()
        for p in palavras
    )


def nome_solto(t):
    t = (t or "").strip()
    if t.isupper() and len(t.split()) >= 2:
        return True
    if re.match(
        r"^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,})*,\s*"
        r"[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+",
        t,
    ) and len(t.split()) <= 6:
        return True
    return False


ABERTURAS_NARRATIVAS = re.compile(
    r"^(?:N[óo]s|Eu|Est[ãa]o|Estamos|Publicamos|Escrevi|Escrevemos|Foi|Fui|"
    r"Sou|Somos|Ainda|H[áa]\s|Hoje|Em\s+\d{4}|Em\s+[a-zç]+(?:\s+de)?\s+\d{4}|"
    r"Aqui|Este post|Neste|Nesta|Confira|Acesse|Leia|Veja|Vejam|Trata-se|"
    r"Vale|Destacamos|Ressaltamos|Queremos|Agradecemos|Participamos|"
    r"Participei|Durante|Quando|Ap[óo]s|Depois|Recentemente|Ontem|"
    r"Naquela|Naquele|Tivemos|Recebemos|Divulgamos|Compartilhamos|"
    r"Endere[çc]o|Avenida|Rua)\b"
)


RUIDO_TITULO = re.compile(
    r'^(?:Rede["”]?\s*:|aluno\s*\(|Fonte\s*:|\d{1,3},\s|'
    r"\d{1,2}\s+de\s+[\wÀ-ÿ]+\s+a\s+.*\b\d{4}\b)"
)


def ruido_narrativo(titulo, trecho):
    """Frase do post não é referência, mesmo que cite um ano."""
    t = normaliza_espacos(titulo)
    if not t or RUIDO_TITULO.match(t):
        return True
    if len(t) > 150:
        return True
    if len(t.split()) > 28:
        return True
    if ABERTURAS_NARRATIVAS.match(t):
        return True
    if t.endswith("...") or t.endswith("…"):
        return True
    # Parágrafo com várias orações seguidas de ano costuma ser narrativa.
    if t.count(". ") >= 3 and not re.search(r":\s*[^,]{2,50},\s*(?:19|20)\d{2}", trecho or ""):
        return True
    return False


def titulo_narrativo(t):
    if re.match(
        r"^(?:Professor|Professora|Pesquisador|Pesquisadora|Advogado|Advogada|"
        r"Jornalista|Coordenador|Coordenadora|Assessor|Assessora|Mestre|"
        r"Doutor|Doutora|Estudante)\b",
        t, re.I,
    ):
        return True
    return bool(re.match(
        r"^(?:A|O|As|Os|Um|Uma|Este|Esta|Esse|Essa|No|Na|Nos|Nas|Hoje|"
        r"Segundo|Para|Quando|Durante|Após|Depois|Aqui|Trata-se|"
        r"Ver aqui|Ver também|Ver tambem|Confira|Leia|Acesse|Saiba|Vejam)\s+"
        r"[a-záàâãéêíóôõúç]",
        t,
    ))


def tem_imprenta(t):
    if EDITORAS.search(t) or MARCA_TIPO.search(t) or MARCA_PERIODICO.search(t):
        return True
    if MARCA_CAPITULO.search(t):
        return True
    return bool(re.search(r":\s*[^,]{2,60},\s*(?:19|20)\d{2}", t))


def eh_linha_auxiliar(t):
    t = sem_acento(t).strip().lower()
    return bool(re.match(
        r"^(varias autorias|varios autores|outros|org\.?|organizacao|coord\.?|"
        r"professor(?:\s|$)|professora(?:\s|$)|advogad[oa]\b|"
        r"pesquisador[ao]?(?:\s|$)|assessor(?:\s|$)|assessora(?:\s|$)|"
        r"mestre\b|doutor[ao]?(?:\s|$)|estudante\b|jornalista\b|"
        r"assessora universitaria|assessor universitario)",
        t,
    ))


def separa_autor(texto):
    """Devolve (autor, resto). Usa o primeiro corte crível em '. '."""
    # Autor com marcador de organização sem ponto: "SOBRENOME, Nome (Org.) Título"
    m = re.match(r"^(.{2,120}?\((?:Org|org|Coord|coord)\.\))\s+(.+)$", texto)
    if m and parece_autor(m.group(1)):
        return m.group(1).strip(), m.group(2).strip()
    limite = min(len(texto), 190)
    for m in re.finditer(r"\.\s*", texto[:limite]):
        esq = texto[:m.start()].strip()
        dir_ = texto[m.end():].strip()
        if len(dir_) < 8:
            continue
        if re.search(
            r"(?:\b(?:n|v|p|ed|jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez|"
            r"trad|org|coord|vol|pág|pag))\.$",
            esq, re.I,
        ):
            continue  # abreviação, não fim de autor
        if not parece_autor(esq):
            continue
        if re.search(r"\b[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]$", esq):
            continue  # inicial: "Sonia H." não é fim de autor
        if len(esq.split()) > 24:
            continue
        return esq, dir_
    return "", texto


CIDADES = (
    "Rio de Janeiro", "São Paulo", "Sao Paulo", "Brasília", "Brasilia",
    "Belo Horizonte", "Porto Alegre", "Salvador", "Recife", "Fortaleza",
    "Curitiba", "Florianópolis", "Florianopolis", "Belém", "Belem", "Manaus",
    "Goiânia", "Goiania", "Campinas", "São Luís", "Sao Luis", "Maceió",
    "Maceio", "Natal", "João Pessoa", "Joao Pessoa", "Teresina", "Aracaju",
    "Vitória", "Vitoria", "Campo Grande", "Cuiabá", "Cuiaba", "Palmas",
    "Boa Vista", "Macapá", "Macapa", "Rio Branco", "Porto Velho",
    "Petrópolis", "Petropolis", "Juiz de Fora", "Londrina", "Maringá",
    "Maringa", "Santos", "Ribeirão Preto", "Ribeirao Preto", "Uberlândia",
    "Uberlandia", "Pelotas", "Caxias do Sul", "Chapecó", "Chapeco",
)
CIDADE_RE = "|".join(re.escape(c) for c in CIDADES)


IMPRENTA_RE = re.compile(
    r"\.\s+(?=(?:Em:|In:|Tese\b|Disserta|Monografia\b|Relatório\b|Relatorio\b|"
    r"Artigo\b|Revista\b|Boletim\b|Cadernos?\b|Coleção\b|Colecao\b|Série\b|"
    r"Serie\b|In\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]|\(Tradu|\(Trad\.|Tradução\b|"
    r"Traducao\b|Trad\.\s|(?:%s)\s*[,:]|"
    r"[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\w\s\.]{1,40}:\s))" % CIDADE_RE
)


def extrai_titulo(resto):
    resto = normaliza_espacos(resto)
    if not resto:
        return ""
    # Título entre aspas logo no começo: "Introdução: ..." / "Direitos ...".
    m = re.match(r'^[“"]([^”"]{4,300})[”"]', resto)
    if m:
        return m.group(1).strip()[:500]
    # Corrige ausência de espaço depois do ponto antes de imprenta/edição
    # ("Brasil.Rio de Janeiro:"), só para leitura; o trecho guarda o original.
    resto = re.sub(r"\.(?=[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\w\s\.]{1,32}:)", ". ", resto)
    resto = re.sub(r"\.(?=\d+[ªa]?\s*(?:ed|Ed)\b)", ". ", resto)
    m = IMPRENTA_RE.search(resto)
    if m:
        titulo = resto[:m.start()]
    else:
        m2 = re.search(
            r",\s*(?:v\.\s*\d|n\.\s*\d|p\.\s*\d)|"
            r",\s*(?:Revista|Boletim|Cadernos|Journal|Kriterion|Doxa)\b",
            resto,
        )
        titulo = resto[:m2.start()] if m2 else resto
    titulo = titulo.strip(" .;–-")
    titulo = re.sub(r"^\d{4}\.\s*", "", titulo)  # ano repetido no começo
    # Autores repetidos no começo do "título" por falha de pontuação do original.
    while re.match(
        r"^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,})*"
        r",\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.;]{1,70}\.\s+",
        titulo,
    ):
        titulo = re.sub(
            r"^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,})*"
            r",\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.;]{1,70}\.\s+",
            "", titulo, count=1,
        )
    titulo = re.sub(r"\s*\((?:Org|org|Coord|coord|Ed|ed)\.?\)\s*$", "", titulo)
    titulo = re.sub(r"\.\s*\d+\.?\s*ed\.?\s*$", "", titulo)
    titulo = re.sub(
        r"\.\s*\d+[ªa]?(?:\s*,\s*\d+[ªa]?)?\s*(?:ed\.?|reimpress[aã]o)?\s*$",
        "", titulo, flags=re.I,
    )
    titulo = re.sub(
        r"\.\s*\d+[ªa]?\s*(?:ed(?:ição|icao)?|Ed\.?)\s*$", "", titulo, flags=re.I
    )
    titulo = re.sub(r"\s*\[(?:Mimeo|mimeo|No prelo|no prelo)\]\s*$", "", titulo)
    titulo = re.sub(r"\.\s*(?:19|20)\d{2}\.?\s*$", "", titulo)
    if len(titulo) < 4:
        return ""
    titulo = titulo.strip('"“” ').strip()
    return titulo[:500].strip()


def ano_lei(texto):
    m = re.search(r"n[ºo°.]?\s*[\d.]+\s*/\s*(\d{2,4})", texto or "")
    if not m:
        return ""
    a = m.group(1)
    if len(a) == 2:
        a = ("19" if int(a) >= 50 else "20") + a
    return a


def autores_extras(resto):
    """Coautores escritos como 'SOBRENOME, Nome.' antes do título."""
    out = []
    txt = resto
    padrao = re.compile(
        r"^([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,}(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ]{2,})*,\s*"
        r"[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.;]{1,70})\.\s+"
    )
    while True:
        m = padrao.match(txt)
        if not m:
            break
        out.append(m.group(1).strip())
        txt = txt[m.end():]
    return out


def extrai_tipo(texto):
    if MARCA_LEI.match(texto[:160]):
        return "legislacao"
    if re.search(r"\bTese\b|\bDoutorado\b", texto, re.I):
        return "tese"
    if re.search(r"\bDisserta", texto, re.I):
        return "dissertacao"
    if re.search(r"\bMonografia\b|\bTrabalho de Conclusão\b|\bTCC\b", texto, re.I):
        return "monografia"
    if re.search(r"\bRelatório\b|\bRelatorio\b|\bDiagnóstico\b", texto, re.I):
        return "relatorio"
    if re.search(r"Dispon[íi]vel em\s*:?\s*https?://", texto, re.I):
        return "site"
    if MARCA_CAPITULO.search(texto) or re.search(r"\bPrefácio\b|\bPosfácio\b", texto, re.I):
        return "capitulo"
    if MARCA_PERIODICO.search(texto) or re.search(
        r",\s*(?:v\.|p\.)\s*\d|DOI|doi\.org", texto
    ) or re.search(r"\bRevista\b[^.]{0,80},\s*n\.\s*\d", texto):
        return "artigo"
    if EDITORAS.search(texto) or re.search(r":[^,]{2,60},\s*(?:19|20)\d{2}", texto):
        return "livro"
    return "obra"


def extrai_veiculo(texto, tipo):
    if tipo == "artigo":
        m = re.search(
            r"(?:[.,]\s+|^)((?:Revista|Boletim|Cadernos?|Journal|Anuário|Anuario|"
            r"Kriterion|Doxa|Educação & Sociedade)[^,.]{0,90})",
            texto,
        )
        if m:
            return normaliza_espacos(m.group(1))[:120]
    if tipo in ("tese", "dissertacao", "monografia", "relatorio"):
        m = re.search(
            r"(?:Universidade|Faculdade|Instituto|Centro|UnB|UF[A-Z]{2}|"
            r"PUC|USP|Unicamp|Unisinos)[^,.;]{0,100}",
            texto,
        )
        if m:
            return normaliza_espacos(m.group(0))[:120]
    if tipo == "livro":
        m = re.search(r":\s*([^:,.]{2,60}),\s*(?:19|20)\d{2}", texto)
        if m:
            return normaliza_espacos(m.group(1))[:120]
    m = re.search(r"([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][\w\s&\.]{2,50}):\s*[^,]{2,60},\s*(?:19|20)\d{2}", texto)
    if m:
        return normaliza_espacos(m.group(1))[:120]
    return ""


def tenta_ref(texto, links=None):
    """Tenta ler um bloco como referência. Devolve dict parcial ou None."""
    original = normaliza_espacos(texto)
    t = limpa_rotulo(original)
    if len(t) < 25 or len(t) > 900:
        return None
    if t.count(" ") < 4:
        return None
    if re.match(r"^\(Outra vers", t, re.I):
        return None
    if re.match(r"^Tradu[çc][ãa]o de\s", t, re.I):
        return None  # crédito de tradução, não obra assinada

    autor, resto = separa_autor(t)
    if not autor:
        autor, resto = autor_embutido(t)
    if autor:
        extras = autores_extras(resto)
        if extras:
            autor = "; ".join([autor] + extras)
    ano = extrai_ano(t)
    titulo = ""
    tipo = "obra"

    # Legislação: o ano está no próprio número (ex.: Lei n. 8.629/93).
    if MARCA_LEI.search(t[:160]):
        tipo = "legislacao"
        a = ano_lei(t)
        if a:
            ano = a
        elif links:
            for l in links:
                a = extrai_ano(l.get("texto", ""))
                if a:
                    ano = a
                    break

    # Lista curta: "Título", de Autor; "Título", Autor; "Título", organizado por.
    m = re.match(r'^[“"]([^”"]{3,300})[”"]\s*,?\s*(?:de|por)\s+(.{2,140})$', t)
    if not m:
        m = re.match(r'^[“"]([^”"]{3,300})[”"]\s+organizado por\s+(.{2,140})$', t, re.I)
    if not m:
        m = re.match(r'^[“"]([^”"]{3,300})[”"]\s*,\s*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ].{2,140})$', t)
    if not m:
        m = re.match(r'^[“"](.{3,250}),\s*(?:de|por)\s+(.{2,140})$', t)
    if m:
        titulo = normaliza_espacos(m.group(1))
        autor = normaliza_espacos(m.group(2)).rstrip(".")
        if ruido_narrativo(titulo, t):
            return None
        # Post de blogue: "Título", de Autor, em 21 de janeiro de 2010.
        d = re.match(
            r"^(.+?),\s*em\s+\d{1,2}\s+de\s+[\wÀ-ÿ]+\s+de\s+(\d{4})$",
            autor, re.I,
        )
        confianca = "media"
        motivo = "autoria e título reconhecidos; sem dados de publicação"
        if d:
            autor = d.group(1).strip()
            ano = d.group(2)
            confianca = "media"
            motivo = "post de blogue com autor, título e data"
        return {
            "tipo": "obra", "titulo": titulo, "autor": autor, "ano": ano,
            "veiculo": "", "trecho": original[:600], "confianca": confianca,
            "metodo": "padrao", "motivo": motivo,
            "_links": links or [],
        }

    if autor:
        titulo = extrai_titulo(resto)
        if parece_imprenta_titulo(titulo):
            autor = ""  # o "autor" era, na verdade, a imprenta
    if autor:
        tipo = tipo if tipo == "legislacao" else extrai_tipo(t)
        if not titulo:
            return None
        if titulo_narrativo(titulo) or ruido_narrativo(titulo, t):
            return None
        # Evita transformar uma frase narrativa em título.
        if len(titulo.split()) < 3 and tipo == "obra":
            return None
        if not ano:
            # Sem ano só entra autor inequívoco ("SOBRENOME, Nome") ou
            # referência acadêmica com tipo explícito (tese/dissertação).
            if "," not in autor and not MARCA_TIPO.search(t):
                return None
            confianca = "media"
            motivo = "autoria e título reconhecidos; sem ano de publicação"
        else:
            confianca = "media"
            motivo = "autor, título e ano reconhecidos"
            if tem_imprenta(t) or re.search(r",\s*(v\.|n\.|p\.)\s*\d", t):
                confianca = "alta"
                motivo = "autor, título, ano e imprenta/veículo reconhecidos"
        if titulo.strip(" .").lower() in (
            "prefácio", "prefacio", "apresentação", "apresentacao",
            "introdução", "introducao", "posfácio", "posfacio",
        ):
            confianca = "baixa"
            motivo = "título genérico (prefácio/apresentação); conferir no original"
        return {
            "tipo": tipo, "titulo": titulo, "autor": autor, "ano": ano,
            "veiculo": extrai_veiculo(t, tipo), "trecho": original[:600],
            "confianca": confianca, "metodo": "padrao", "motivo": motivo,
            "_links": links or [],
        }

    # Sem autor reconhecido: exige imprenta/tipo e ano, para não virar título
    # de seção ou frase solta.
    if not ano or "|" in t:
        return None
    if not (MARCA_TIPO.search(t) or MARCA_PERIODICO.search(t)
            or MARCA_CAPITULO.search(t)
            or re.search(r":\s*[^,]{2,60},\s*(?:19|20)\d{2}", t)):
        return None
    titulo = extrai_titulo(t)
    if not titulo or len(titulo.split()) < 2:
        return None
    if titulo_narrativo(titulo) or ruido_narrativo(titulo, t):
        return None
    if parece_imprenta_titulo(titulo):
        return None  # só a imprenta sobrou; o título ficou no bloco anterior
    if nome_solto(titulo):
        return None
    if re.match(r"^(Monografia|Dissertação|Dissertacao|Tese|Relatório|Relatorio)\b",
                titulo, re.I):
        return None
    tipo = extrai_tipo(t)
    return {
        "tipo": tipo, "titulo": titulo, "autor": "", "ano": ano,
        "veiculo": extrai_veiculo(t, tipo), "trecho": original[:600],
        "confianca": "baixa" if not ano else "baixa",
        "metodo": "padrao",
        "motivo": "referência sem autor identificável",
        "_links": links or [],
    }


DITTO = re.compile(r"^_{3,}\s*\.\s*")


def extrai_pagina(slug, titulo_fonte):
    caminho = os.path.join(RAIZ, slug + ".html")
    if not os.path.exists(caminho):
        return None
    with io.open(caminho, encoding="utf-8") as fh:
        parser = CorpoParser()
        parser.feed(fh.read())
        parser.close()
    if not parser.tem_corpo:
        return None
    return parser.blocos


def eh_link_self(href):
    host = urlparse(href).netloc.lower()
    if host in SELF_HOSTS:
        return True
    if not host and href.lower().endswith(".html"):
        return True
    if host.endswith(".blogspot.com") and "assessoriajuridicapopular" in host:
        return True
    return False


def eh_link_social(host):
    host = host.lower()
    return any(host == d or host.endswith("." + d) for d in REDES)


def eh_imagem(href):
    h = href.lower().split("?")[0]
    return bool(re.search(r"\.(jpe?g|png|gif|webp|svg|bmp|tiff?)$", h)) or "picasaweb" in h


def texto_link_limpo(t):
    t = re.sub(r"\s*\((?:abre em outra aba|link externo|abre em nova aba)\)\s*", " ", t, flags=re.I)
    t = re.sub(r"\s*[»→→]\s*$", "", t)
    return normaliza_espacos(html.unescape(t)).strip(" .")


def link_generico(texto):
    t = sem_acento(texto).lower().strip(" .")
    if t in {sem_acento(g) for g in GENERICOS}:
        return True
    return bool(re.match(
        r"^(ver o v[ií]deo|ler no blog|ver o cartaz|assista|clique|leia|saiba|"
        r"fotos?\b|v[ií]deo\b|imagem\b|link\b|aqui\b)",
        t,
    ))


def tipo_link(href, texto):
    host = urlparse(href).netloc.lower()
    caminho = urlparse(href).path.lower()
    t = sem_acento(texto).lower()
    if "youtube" in host or "youtu.be" in host or "vimeo" in host:
        return "video"
    if any(x in host for x in ("planalto", "camara.gov", "senado", "alerj", "assembleia")):
        return "legislacao"
    if re.search(r"\b(tese|doutorado)\b", t):
        return "tese"
    if re.search(r"\b(disserta|mestrado)\b", t):
        return "dissertacao"
    if re.search(r"\b(monografia|tcc)\b", t):
        return "monografia"
    if re.search(r"\b(relatorio|relatório|diagnostico|diagnóstico)\b", t):
        return "relatorio"
    if re.search(r"\b(artigo|revista|paper)\b", t) or "doi.org" in host:
        return "artigo"
    if caminho.endswith(".pdf") or any(
        x in host for x in ("scribd", "issuu", "drive.google", "repositorio",
                            "acervodigital", "bdtd")
    ):
        return "documento"
    return "site"


def veiculo_link(href, tipo):
    host = urlparse(href).netloc.lower()
    if host in VEICULOS:
        return VEICULOS[host]
    if tipo == "video":
        return {"www.youtube.com": "YouTube", "youtube.com": "YouTube",
                "youtu.be": "YouTube", "vimeo.com": "Vimeo"}.get(host, host)
    if tipo == "legislacao":
        return "Planalto" if "planalto" in host else host
    return host.replace("www.", "") if host else ""


def monta_link(bloco, link):
    href = html.unescape(link["href"]).strip()
    if not href or href.startswith(("mailto:", "javascript:", "#")):
        return None
    host = urlparse(href).netloc.lower()
    if eh_link_self(href) or eh_link_social(host) or eh_imagem(href):
        return None
    if "blogger.com" in host:  # notas de rodapé do Blogger
        return None
    texto = texto_link_limpo(link["texto"])
    if not texto:
        return None
    if re.match(r"^https?://", texto, re.I) or texto == href:
        return None
    if link_generico(texto):
        return None
    if ruido_narrativo(texto, bloco["texto"]):
        return None
    if re.match(r"^(?:Artigo\s+(?:a respeito|sobre)|Mat[ée]ria\s+(?:a respeito|sobre))\b",
                texto, re.I):
        return None
    if len(texto.split()) < 2 and tipo_link(href, texto) != "legislacao":
        return None
    if len(texto) < 12 and tipo_link(href, texto) != "legislacao":
        return None
    tipo = tipo_link(href, texto)
    trecho = bloco["texto"]
    ano = extrai_ano(trecho)
    if tipo == "legislacao" and not ano:
        ano = extrai_ano(texto) or ano_lei(texto)
    if tipo == "video" and len(texto.split()) < 3 and not ano:
        return None  # nome de intérprete, não título de obra
    if tipo == "video" and not ano and re.match(
        r"^(?:[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+)(?:\s+[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][a-záàâãéêíóôõúç]+){2}$",
        texto,
    ):
        return None  # nome de pessoa (3 palavras), não título
    titulo = texto
    confianca = "media"
    motivo = "link com texto próprio, sem ano no contexto"
    if ano and tipo in ("legislacao", "artigo", "tese", "dissertacao", "monografia",
                        "relatorio", "documento"):
        confianca = "alta"
        motivo = "link com texto próprio e ano no contexto"
    elif tipo == "legislacao" and re.search(r"\d", texto):
        confianca = "media"
        motivo = "legislação citada pelo número, sem ano explícito"
    elif len(texto.split()) <= 3:
        confianca = "baixa"
        motivo = "texto do link curto; pode ser rótulo, não referência"
    veiculo = veiculo_link(href, tipo)
    autor = ""
    autor_tipo = ""
    # Página institucional: a organização responsável pelo site é a autoria
    # possível. Não se aplica a artigo/tese, cuja autoria é pessoal.
    if tipo in ("site", "documento", "relatorio") and veiculo:
        autor = veiculo
        autor_tipo = "institucional"
        motivo += "; autoria institucional pelo site"
    return {
        "tipo": tipo, "titulo": titulo, "autor": autor, "autor_tipo": autor_tipo,
        "ano": ano, "veiculo": veiculo, "url": href,
        "trecho": trecho[:600], "confianca": confianca,
        "metodo": "link", "motivo": motivo,
    }


def url_da_ref(links):
    for l in links or []:
        href = html.unescape(l["href"]).strip()
        if not href or href.startswith(("mailto:", "javascript:", "#")):
            continue
        host = urlparse(href).netloc.lower()
        if eh_link_self(href) or eh_link_social(host) or eh_imagem(href):
            continue
        if "blogger.com" in host:
            continue
        return href
    return ""


# ----------------------------------------------------------------------------
# Montagem da página
# ----------------------------------------------------------------------------

def referencias_da_pagina(slug, titulo_fonte, blocos):
    refs = []
    usados = set()
    ultimo_autor = ""
    autor_padrao = ""
    for b in blocos[:6]:
        m = re.match(r"^Lista de textos de (.+)$", b["texto"], re.I)
        if m:
            autor_padrao = m.group(1).strip()
            break

    for i, bloco in enumerate(blocos):
        if i in usados:
            continue
        texto = bloco["texto"]
        if not texto or len(texto) < 10:
            continue

        # Ditto: herda o autor da referência anterior.
        if DITTO.match(texto):
            if not ultimo_autor:
                if not autor_padrao:
                    continue
                ultimo_autor = autor_padrao
            texto = DITTO.sub("", texto, count=1)
            texto = ultimo_autor + ". " + texto
            ref = tenta_ref(texto, bloco["links"])
            if ref:
                ref["motivo"] += "; autor herdado de entrada anterior (travessão)"
                refs.append(ref)
                usados.add(i)
            continue

        ref = tenta_ref(texto, bloco["links"])
        if ref:
            if ref.get("autor"):
                ultimo_autor = ref["autor"]
            refs.append(ref)
            usados.add(i)
            continue

        # Autor em um parágrafo, título/imprenta nos seguintes.
        if parece_autor(texto):
            segs = []
            j = i + 1
            while j < len(blocos) and len(segs) < 4:
                t = blocos[j]["texto"]
                if t and not eh_linha_auxiliar(t):
                    segs.append((j, t))
                j += 1
            if segs:
                a2, _ = separa_autor(segs[0][1])
                if a2 and chave(a2) != chave(texto):
                    segs = []  # o próximo bloco já é outra referência
            ref = None
            consumidos = []
            if segs:
                composto = texto.rstrip(".") + ". " + segs[0][1]
                links = list(bloco["links"]) + list(blocos[segs[0][0]]["links"])
                consumidos = [i, segs[0][0]]
                candidatos = [composto]
                if len(segs) > 1:
                    candidatos.append(
                        composto.rstrip(".") + ". " + segs[1][1]
                    )
                for k, cand in enumerate(candidatos):
                    r = tenta_ref(cand, links if k == 0 else (
                        links + list(blocos[segs[1][0]]["links"])
                    ))
                    if r and (ANO_RE.search(cand) or MARCA_TIPO.search(cand)) and tem_imprenta(cand):
                        ref = r
                        if k == 1:
                            consumidos = [i, segs[0][0], segs[1][0]]
                        break
            if ref:
                ref["autor"] = texto
                pedacos = [texto] + [blocos[j]["texto"] for j in consumidos[1:]]
                ref["trecho"] = normaliza_espacos(" ".join(pedacos))[:600]
                refs.append(ref)
                usados.update(consumidos)
                ultimo_autor = texto
                continue

        # Título + tipo/ano sem autor (ex.: monografia listada pelo título).
        if parece_titulo(texto):
            j = i + 1
            while j < len(blocos) and not blocos[j]["texto"]:
                j += 1
            if j < len(blocos) and re.match(
                r"^(Tese|Dissertação|Dissertacao|Monografia|Relatório|Relatorio|"
                r"Trabalho de Conclusão|TCC)\b",
                blocos[j]["texto"], re.I,
            ):
                composto = texto.rstrip(".") + ". " + blocos[j]["texto"]
                ref = tenta_ref(composto, list(bloco["links"]) + list(blocos[j]["links"]))
                if ref:
                    ref["titulo"] = texto.strip('"“”')
                    ref["autor"] = ""
                    ref["confianca"] = "baixa"
                    ref["motivo"] = "título e tipo reconhecidos; autor ausente"
                    refs.append(ref)
                    usados.add(i)
                    usados.add(j)
                    continue

    # Links explícitos que não foram absorvidos por uma referência.
    absorvidos = set()
    for r in refs:
        for l in r.get("_links") or []:
            absorvidos.add(html.unescape(l["href"]).strip())
        u = r.get("url") or ""
        if u:
            absorvidos.add(u)

    for bloco in blocos:
        for link in bloco["links"]:
            href = html.unescape(link["href"]).strip()
            if href in absorvidos:
                continue
            ref = monta_link(bloco, link)
            if not ref:
                continue
            absorvidos.add(href)
            refs.append(ref)

    for r in refs:
        if (not r["autor"] and not r.get("autor_tipo") and autor_padrao
                and r["metodo"] == "padrao" and r["tipo"] != "site"):
            r["autor"] = autor_padrao
            r["motivo"] += "; autor indicado no título da lista"
            if r["ano"] and tem_imprenta(r["trecho"]):
                r["confianca"] = "alta"
            elif r["ano"]:
                r["confianca"] = "media"
        r["fonte_slug"] = slug
        r["fonte_titulo"] = titulo_fonte
        r.setdefault("url", "")
        if not r["url"]:
            r["url"] = url_da_ref(r.get("_links"))
        r.pop("_links", None)
        ident = "|".join((slug, r["tipo"], r["titulo"], r["autor"], r["ano"]))
        r["id"] = "ref-" + hashlib.sha1(ident.encode("utf-8")).hexdigest()[:12]

    # Dedup interno por título/autor/ano (ano vazio não diferencia).
    vistos = {}
    saida = []
    for r in refs:
        k = (chave(r["titulo"]), chave(r["autor"])[:40], r["ano"])
        if k in vistos:
            atual = vistos[k]
            if not atual["url"] and r["url"]:
                atual["url"] = r["url"]
            if ordem_confianca(r["confianca"]) > ordem_confianca(atual["confianca"]):
                atual["confianca"] = r["confianca"]
                atual["motivo"] = r["motivo"]
            continue
        # Mesma obra com ano vazio em uma das ocorrências.
        k2 = (chave(r["titulo"]), chave(r["autor"])[:40])
        gemeo = next((v for kk, v in vistos.items() if kk[:2] == k2), None)
        if gemeo is not None:
            if not gemeo["url"] and r["url"]:
                gemeo["url"] = r["url"]
            if not gemeo["ano"] and r["ano"]:
                gemeo["ano"] = r["ano"]
            if ordem_confianca(r["confianca"]) > ordem_confianca(gemeo["confianca"]):
                gemeo["confianca"] = r["confianca"]
                gemeo["motivo"] = r["motivo"]
            continue
        vistos[k] = r
        saida.append(r)
    return saida


def ordem_confianca(c):
    return {"baixa": 0, "media": 1, "alta": 2}.get(c, 0)


# ----------------------------------------------------------------------------
# Amostra e execução
# ----------------------------------------------------------------------------

def carrega_indice():
    with io.open(INDICE, encoding="utf-8") as fh:
        dados = json.load(fh)
    vistos = set()
    saida = []
    for r in dados:
        slug = r.get("slug") or ""
        if not slug or slug in vistos:
            continue
        if not os.path.exists(os.path.join(RAIZ, slug + ".html")):
            continue
        vistos.add(slug)
        saida.append({"slug": slug, "titulo": r.get("titulo") or slug})
    return saida


def monta_amostra(registros, n, incluir_dirigidas=True, tudo=False):
    if tudo:
        return registros
    primeiras = registros[:10]
    resto = [r for r in registros if r not in primeiras]
    rnd = random.Random(SEMENTE)
    aleatorias = rnd.sample(resto, min(n - 10, len(resto))) if n > 10 else []
    amostra = primeiras + aleatorias
    if incluir_dirigidas:
        por_slug = {r["slug"]: r for r in registros}
        for slug in DIRIGIDAS:
            if slug in por_slug and por_slug[slug] not in amostra:
                amostra.append(por_slug[slug])
    return amostra


def resumo(refs, paginas):
    por_tipo = {}
    por_conf = {"alta": 0, "media": 0, "baixa": 0}
    por_metodo = {}
    com_url = 0
    com_autor = 0
    sem_ano = 0
    for r in refs:
        por_tipo[r["tipo"]] = por_tipo.get(r["tipo"], 0) + 1
        por_conf[r["confianca"]] = por_conf.get(r["confianca"], 0) + 1
        por_metodo[r["metodo"]] = por_metodo.get(r["metodo"], 0) + 1
        if r["url"]:
            com_url += 1
        if r["autor"]:
            com_autor += 1
        if not r["ano"]:
            sem_ano += 1
    return {
        "paginas": len(paginas),
        "referencias": len(refs),
        "com_url": com_url,
        "com_autor": com_autor,
        "sem_ano": sem_ano,
        "por_tipo": dict(sorted(por_tipo.items(), key=lambda x: (-x[1], x[0]))),
        "por_confianca": por_conf,
        "por_metodo": por_metodo,
        "paginas_com_referencia": len({r["fonte_slug"] for r in refs}),
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Extrai referências citadas do acervo AJP.")
    ap.add_argument("--tudo", action="store_true", help="processa o acervo inteiro")
    ap.add_argument("--amostra", type=int, default=20, help="tamanho da amostra (padrão: 20)")
    ap.add_argument("--sem-dirigidas", action="store_true",
                    help="não acrescenta as páginas de bibliografia/referências")
    ap.add_argument("--saida", default=SAIDA_PADRAO, help="arquivo JSON de saída")
    ap.add_argument("--debug", action="store_true", help="mostra cada referência encontrada")
    args = ap.parse_args()

    registros = carrega_indice()
    selecionadas = monta_amostra(
        registros, args.amostra, incluir_dirigidas=not args.sem_dirigidas, tudo=args.tudo
    )

    refs = []
    paginas = []
    sem_corpo = []
    for i, reg in enumerate(selecionadas, 1):
        blocos = extrai_pagina(reg["slug"], reg["titulo"])
        if blocos is None:
            sem_corpo.append(reg["slug"])
            continue
        achadas = referencias_da_pagina(reg["slug"], reg["titulo"], blocos)
        paginas.append({"slug": reg["slug"], "titulo": reg["titulo"],
                        "blocos": len(blocos), "referencias": len(achadas)})
        refs.extend(achadas)
        if args.debug:
            print("[%d/%d] %s: %d refs" % (i, len(selecionadas), reg["slug"], len(achadas)))
            for r in achadas:
                print("   %-6s %-12s %-5s %s | %s" % (
                    r["confianca"], r["tipo"], r["ano"], r["autor"][:35], r["titulo"][:80]))

    # Link institucional que duplica uma referência com autor pessoal: fica a
    # pessoal, que é mais informativa. O URL do link é aproveitado.
    por_titulo = {}
    for r in refs:
        if r.get("autor") and r.get("autor_tipo") != "institucional":
            por_titulo.setdefault(chave(r["titulo"]), r)
    filtrados = []
    for r in refs:
        if r.get("autor_tipo") == "institucional":
            dono = por_titulo.get(chave(r["titulo"]))
            if dono is not None and (
                not r["ano"] or not dono["ano"] or r["ano"] == dono["ano"]
            ):
                if not dono["url"] and r["url"]:
                    dono["url"] = r["url"]
                continue
        filtrados.append(r)
    refs = filtrados

    # Dedup global entre páginas (mesma obra citada em vários posts).
    unicos = {}
    for r in refs:
        k = (chave(r["titulo"]), chave(r["autor"])[:40], r["ano"])
        if k not in unicos:
            k2 = (k[0], k[1])
            gemeo = next((kk for kk in unicos if kk[:2] == k2), None)
            if gemeo is not None:
                atual = unicos[gemeo]
                atual["_ocorrencias"].append(r["fonte_slug"])
                if not atual["url"] and r["url"]:
                    atual["url"] = r["url"]
                if not atual["ano"] and r["ano"]:
                    atual["ano"] = r["ano"]
                continue
            r["_ocorrencias"] = [r["fonte_slug"]]
            unicos[k] = r
        else:
            atual = unicos[k]
            atual["_ocorrencias"].append(r["fonte_slug"])
            if not atual["url"] and r["url"]:
                atual["url"] = r["url"]
    finais = list(unicos.values())
    for r in finais:
        ocorrencias = r.pop("_ocorrencias")
        r["ocorrencias"] = len(ocorrencias)
    finais.sort(key=lambda r: (r["fonte_slug"], r["titulo"]))

    meta = {
        "gerado_em": date.today().isoformat(),
        "script": "etl/extrai-referencias.py",
        "versao": "piloto-1",
        "escopo": {
            "indice": len(registros),
            "selecionadas": len(selecionadas),
            "lidas": len(paginas),
            "sem_corpo": sem_corpo,
            "criterio": (
                "acervo inteiro" if args.tudo else
                "10 primeiras do índice + 10 aleatórias (semente %d) + %d páginas "
                "de bibliografia/referências" % (
                    SEMENTE, 0 if args.sem_dirigidas else len(DIRIGIDAS))
            ),
        },
        "aviso": (
            "Sem acesso à rede. Texto preservado do HTML local; campos vazios "
            "indicam ausência de evidência, não inferência."
        ),
        "tipos": list(TIPOS),
        "confianca": {
            "alta": "autor, título, ano e imprenta/veículo reconhecidos",
            "media": "referência plausível, falta ano ou imprenta",
            "baixa": "falta autor, ano ou título; revisar antes de usar",
        },
    }
    dados = {"meta": meta, "resumo": resumo(finais, paginas),
             "paginas": paginas, "referencias": finais}

    os.makedirs(os.path.dirname(args.saida), exist_ok=True)
    with io.open(args.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    r = dados["resumo"]
    print("páginas lidas: %d | referências: %d | com URL: %d" % (
        r["paginas"], r["referencias"], r["com_url"]))
    print("confiança:", r["por_confianca"])
    print("tipos:", r["por_tipo"])
    print("saída:", args.saida)
    if sem_corpo:
        print("sem corpo:", len(sem_corpo), "página(s)")


if __name__ == "__main__":
    main()
