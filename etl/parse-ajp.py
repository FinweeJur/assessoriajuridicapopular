#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Converte o HTML do blog Assessoria Jurídica Popular em JSON de blocos tipados.

**Fonte oficial:** <https://assessoriajuridicapopular.blogspot.com> — blog
hospedado no Blogger, template *Simple*, lido com User-Agent
`finweejur/github artur colito`. Nenhuma requisição de rede acontece aqui:
o módulo só lê os arquivos que `etl/baixa-ajp.py` já gravou em
`G:\\Meu Drive\\RENAP-AJP\\`.

**Por que existe:** é a etapa `transform` do plano
`docs/PLANO-ETL-ASSESSORIA-JURIDICA-POPULAR.md` (seção 4.2). Ele transforma
página HTML em blocos tipados (`paragrafo`, `titulo`, `citacao`, `lista`,
`imagem`, `video`, `link`), com o schema da seção 5. Nada de HTML cru sai
daqui: quem publica recebe texto, origem e hash, e pode citar com prova.

**Decisões que valem a leitura:**

1. **Duas fontes, uma saída.** O HTML da página do post (`.post-body`) é a
   fonte preferida, porque é o que o leitor vê. O feed Atom só entra quando a
   página ainda não foi baixada ou veio truncada; nesse caso o campo
   `fonte.origem_html` diz `feed`, para o revisor saber.
2. **A grafia é do autor.** Não corrigimos "idéia", "contingenciamentos" nem
   concordância. Só normalizamos espaços, entidades (`&nbsp;`), aspas curvas e
   quebras de linha do HTML — o texto segue palavra por palavra.
3. **Rabicho do Blogger é lixo.** "Mapeamento", "Colunistas", "Postado por",
   "Tecnologia do Blogger", contagem de comentários e o rodapé
   `blogger-post-footer` são descartados, como manda a tabela 4.2. Comentários
   de leitor não são lidos nem citados: nada de nome de comentarista.
4. **Imagem sem licença não é arquivo.** O bloco guarda a URL de origem e
   `licenca: "link"`; o arquivo só entra depois da decisão jurídica (seção 3).
5. **O robô sugere, o humano decide.** `resumo`, `temas` e `revisao.notas` são
   propostas automáticas; `revisao.estado` nasce `pendente` e a lista de
   pendências vai no `_relatorio.json`.

Uso:
    python etl/parse-ajp.py --limite 20
    python etl/parse-ajp.py --posts "G:\\Meu Drive\\RENAP-AJP\\posts" --saida ...\\staging
    python etl/parse-ajp.py --fonte feed --limite 5      # só o Atom, sem página
    python etl/parse-ajp.py --todos                     # acervo inteiro
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
import urllib.parse
from typing import Any

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString, Tag

# --------------------------------------------------------------------------
# Caminhos e constantes de fonte
# --------------------------------------------------------------------------

RAIZ_DADOS = r"G:\Meu Drive\RENAP-AJP"
PADRAO_POSTS = os.path.join(RAIZ_DADOS, "posts")
PADRAO_FEED = os.path.join(RAIZ_DADOS, "feed")
PADRAO_SAIDA = os.path.join(RAIZ_DADOS, "staging")

UA = "finweejur/github artur colito"
SITE = "Assessoria Jurídica Popular"
URL_BLOG = "https://assessoriajuridicapopular.blogspot.com"
BLOG_ID_PADRAO = "8502620451751951542"
HOST_VALIDO = "assessoriajuridicapopular.blogspot.com"

# Licença padrão de toda captura: citação com crédito e link até haver
# autorização escrita do autor (cenário B do plano, seção 3).
LICENCA_PADRAO = "citacao"

TAMANHO_MINIMO_PAGINA = 2000  # arquivo menor que isso é download pela metade
SLUG_MAX = 60

TIPOS_BLOCO = ("paragrafo", "titulo", "citacao", "lista", "imagem", "video", "link")

# Vocabulário fechado de temas (plano 4.2, regra 5).
VOCABULARIO_TEMAS = (
    "assessoria-juridica-popular",
    "educacao-popular",
    "movimentos-sociais",
    "direitos-humanos",
    "memoria",
    "teoria-critica",
)

# Palavras-chave por tema, já sem acento e em minúsculas. O peso diz quanto
# cada termo empurra o tema: título e categoria valem mais que o corpo.
REGRAS_TEMA: dict[str, tuple[tuple[str, int], ...]] = {
    "assessoria-juridica-popular": (
        ("assessoria juridica popular", 5),
        ("assessoria juridica universitaria", 4),
        ("assessoria popular", 3),
        ("advocacia popular", 3),
        ("advogado popular", 3),
        ("advogados populares", 3),
        ("ajup", 4),
        ("najup", 4),
        ("saju", 3),
        ("geajup", 3),
        ("pratica juridica", 2),
        ("extensao popular", 2),
        ("assistencia juridica", 2),
        ("acesso a justica", 2),
        ("direito insurgente", 2),
    ),
    "educacao-popular": (
        ("educacao popular", 5),
        ("educacao juridica", 4),
        ("educacao em direitos", 3),
        ("formacao", 2),
        ("oficina", 3),
        ("minicurso", 3),
        ("curso", 2),
        ("ensino juridico", 3),
        ("universidade popular", 3),
        ("paulo freire", 3),
        ("conscientizacao", 2),
        ("metodologia", 1),
    ),
    "movimentos-sociais": (
        ("movimento social", 5),
        ("movimentos sociais", 5),
        ("movimento popular", 4),
        ("mst", 4),
        ("mtst", 4),
        ("ocupacao", 3),
        ("luta pela terra", 4),
        ("reforma agraria", 3),
        ("sem-teto", 3),
        ("sindicato", 2),
        ("greve", 2),
        ("mobilizacao", 2),
        ("quilombola", 3),
        ("assentamento", 2),
        ("movimento estudantil", 3),
        ("luta popular", 2),
    ),
    "direitos-humanos": (
        ("direitos humanos", 5),
        ("direito humano", 3),
        ("violencia", 2),
        ("criminalizacao", 3),
        ("tortura", 3),
        ("perseguicao", 2),
        ("preso politico", 3),
        ("prisao", 2),
        ("etnocidio", 3),
        ("genocidio", 3),
        ("feminicidio", 3),
        ("mulheres", 2),
        ("indigena", 2),
        ("povos indigenas", 3),
        ("crianca e adolescente", 2),
        ("racismo", 3),
        ("lgbt", 3),
        ("refugiado", 2),
        ("moradia", 2),
        ("meio ambiente", 2),
    ),
    "memoria": (
        ("memoria", 4),
        ("ditadura", 4),
        ("1964", 3),
        ("anistia", 3),
        ("comissao da verdade", 3),
        ("justica de transicao", 3),
        ("historia", 2),
        ("historico", 1),
        ("arquivo", 2),
        ("homenagem", 2),
        ("luto", 2),
        ("falecimento", 3),
        ("biografia", 2),
        ("registro historico", 3),
        ("tribunal do juri", 1),
    ),
    "teoria-critica": (
        ("teoria critica", 5),
        ("teorias criticas", 4),
        ("critica do direito", 4),
        ("marxismo", 4),
        ("marxista", 3),
        ("pachukanis", 4),
        ("lyra filho", 4),
        ("pluralismo juridico", 3),
        ("direito alternativo", 3),
        ("filosofia", 2),
        ("epistemologia", 2),
        ("descolonial", 3),
        ("pesquisa", 1),
        ("metodo", 1),
        ("totalidade", 1),
    ),
}

# Categoria do Blogger que já aponta direto para um tema do vocabulário.
CATEGORIA_PARA_TEMA = {
    "assessoria juridica popular": "assessoria-juridica-popular",
    "assessoria juridica": "assessoria-juridica-popular",
    "assessoria popular": "assessoria-juridica-popular",
    "advocacia popular": "assessoria-juridica-popular",
    "ajup": "assessoria-juridica-popular",
    "educacao popular": "educacao-popular",
    "educacao juridica popular": "educacao-popular",
    "educacao juridica": "educacao-popular",
    "extensao popular": "educacao-popular",
    "movimentos sociais": "movimentos-sociais",
    "movimentos populares": "movimentos-sociais",
    "movimento popular": "movimentos-sociais",
    "direitos humanos": "direitos-humanos",
    "direito insurgente": "teoria-critica",
    "teoria critica": "teoria-critica",
    "teoria critica do direito": "teoria-critica",
    "marxismo": "teoria-critica",
    "memoria": "memoria",
    "registro historico": "memoria",
    "direito a memoria e a verdade": "memoria",
}

# Tags que nunca viram conteúdo.
TAGS_DESCARTE = {"script", "style", "noscript", "link", "meta", "base", "template"}

# Tags de bloco: marcam fronteira de parágrafo mesmo quando só embrulham texto.
TAGS_QUEBRA = {
    "p", "div", "center", "section", "article", "header", "footer", "main",
    "aside", "nav", "form", "fieldset", "address", "dl", "dt", "dd", "figure",
    "figcaption", "li", "td", "th", "tr", "tbody", "thead", "tfoot", "caption",
    "output", "details", "summary",
}
TAGS_TITULO = {"h1", "h2", "h3", "h4", "h5", "h6"}
TAGS_MIDIA = {"iframe", "object", "embed", "video", "audio", "param"}

# Textos que são cromo do Blogger, não conteúdo (tabela 4.2 do plano).
LIXO_EXATO = {
    "mapeamento",
    "colunistas",
    "postado por",
    "tecnologia do blogger",
    "postagem mais recente",
    "postagens mais recentes",
    "postagem mais antiga",
    "postagens mais antigas",
    "pagina inicial",
    "compartilhar",
    "comentarios",
    "postar comentarios",
    "assinar: postagens (atom)",
    "blogueassessoriajuridicapopular@googlegroups.com",
}

MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}

AUTORES_GENERICOS = {"unknown", "anonymous", "anônimo", "anonimo", "admin", "adm"}

# --------------------------------------------------------------------------
# Texto: normalização que não mexe na grafia do autor
# --------------------------------------------------------------------------

_ESPACOS = re.compile(r"[ \t\r\f\v]+")
_VAZIAS = re.compile(r"\n{2,}")


def sem_acento(texto: str) -> str:
    """Minúsculas sem acento — só para comparar palavra-chave, nunca para exibir."""
    decomposto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def normaliza(texto: str) -> str:
    """Limpa entidades, aspas curvas e espaços duplos. Preserva as palavras."""
    if not texto:
        return ""
    t = texto.replace("\xa0", " ").replace("\u200b", "").replace("\ufeff", "")
    # Aspas curvas viram retas: portabilidade do JSON e busca previsível.
    for antes, depois in (("\u201c", '"'), ("\u201d", '"'), ("\u201e", '"'),
                          ("\u2013", "–"), ("\u2014", "—"),
                          ("\u2018", "'"), ("\u2019", "'")):
        t = t.replace(antes, depois)
    t = _ESPACOS.sub(" ", t)
    linhas = [linha.strip() for linha in t.split("\n")]
    t = "\n".join(linhas)
    t = _VAZIAS.sub("\n", t)
    # NFC: "c" + cedilha vira "ç" de novo. É forma Unicode, não grafia —
    # o original às vezes vem decomposto (colado do Word) e quebra a busca.
    return unicodedata.normalize("NFC", t.strip())


def tem_conteudo(texto: str) -> bool:
    """Só pontuação/espaço não é bloco: exige ao menos uma letra ou número."""
    return bool(re.search(r"\w", texto or ""))


def eh_externo(url: str) -> bool:
    return bool(url) and HOST_VALIDO not in url


def https(url: str) -> str:
    """O blog ainda publica links em http; guardamos sempre https."""
    if not url:
        return url
    return re.sub(r"^http://", "https://", url.strip())


# Esquemas que não são endereço público: `javascript:` e `file:///C:/Users/...`
# vêm de marcação de editor e de nota de rodapé do Word. O texto fica, o link sai.
ESQUEMAS_DESCARTADOS = {"javascript", "file", "data", "vbscript", "mhtml"}


def resolve_url(href: str | None, base: str | None) -> str | None:
    """Transforma o href do original em endereço absoluto e seguro.

    O Blogger antigo usa `//host/arquivo` (sem esquema) e âncoras de nota
    (`#_ftn1`). O leitor precisa de link clicável: resolvemos contra a URL
    canônica do post.
    """
    if not href:
        return None
    valor = href.strip()
    if not valor:
        return None
    if valor.startswith("#"):
        return (base or "").rstrip("/") + valor if base else None
    if valor.startswith("//"):
        return "https:" + valor
    esquema = re.match(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):", valor)
    if esquema:
        nome = esquema.group(1).lower()
        if nome in ESQUEMAS_DESCARTADOS:
            return None
        if nome == "http":
            return "https://" + valor[7:]
        return valor
    if valor.startswith("/") and base:
        raiz = re.match(r"^(https?://[^/]+)", base)
        return (raiz.group(1) + valor) if raiz else valor
    if re.match(r"^www\.", valor, re.IGNORECASE):
        return "https://" + valor
    if base:
        return urllib.parse.urljoin(base, valor)
    return valor


# --------------------------------------------------------------------------
# Lixo do Blogger
# --------------------------------------------------------------------------

def limpa_soup(sopa: BeautifulSoup) -> None:
    """Remove o que nunca é conteúdo: scripts, rodapé do post, comentários."""
    for tag in sopa.find_all(list(TAGS_DESCARTE)):
        tag.decompose()
    for seletor in (
        "div.blogger-post-footer",
        "div#comments",
        "div.comments",
        "div.comment-form",
        "div.post-share-buttons",
        "div#blog-pager",
        "div.post-footer",
        "div.feed-links",
    ):
        for tag in sopa.select(seletor):
            tag.decompose()
    for comentario in sopa.find_all(string=lambda s: isinstance(s, Comment)):
        comentario.extract()


def e_lixo(texto: str, url: str | None = None) -> bool:
    """Reconhece o rabicho do Blogger e a contagem de comentários."""
    chave = sem_acento(texto or "").strip(" .:;,-–—|\"'")
    if not chave:
        return False
    if chave in LIXO_EXATO:
        return True
    if chave.startswith("postado por"):
        return True
    if "tecnologia do blogger" in chave:
        return True
    if re.fullmatch(r"\d+\s+comentarios?", chave):
        return True
    if re.fullmatch(r"\d+\s+comentarios?\s*:?", chave):
        return True
    if url and "/search" in url:
        return True
    return False


# --------------------------------------------------------------------------
# Extração de texto e links de um trecho
# --------------------------------------------------------------------------

def _texto_inline(no: Any, links: list[dict[str, Any]], base: str | None = None) -> str:
    """Texto de um nó inline, guardando cada `<a>` encontrado."""
    if isinstance(no, NavigableString):
        return str(no)
    if not isinstance(no, Tag):
        return ""
    nome = (no.name or "").lower()
    if nome in TAGS_DESCARTE or nome in ("img",) or nome in TAGS_MIDIA:
        return ""
    if nome == "br":
        return "\n"
    if nome == "wbr":
        return ""
    if nome == "a":
        href = resolve_url(no.get("href"), base)
        interno = "".join(_texto_inline(f, links, base) for f in no.children)
        rotulo = normaliza(interno)
        if href and rotulo:
            links.append({"texto": rotulo, "url": href, "externo": eh_externo(href)})
        return interno
    return "".join(_texto_inline(f, links, base) for f in no.children)


def texto_de(no: Tag, links: list[dict[str, Any]] | None = None, base: str | None = None) -> str:
    links = links if links is not None else []
    return normaliza(_texto_inline(no, links, base))


# --------------------------------------------------------------------------
# Blocos de mídia
# --------------------------------------------------------------------------

_RE_YOUTUBE = re.compile(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|v/|watch\?v=)|youtu\.be/)([A-Za-z0-9_-]{11})")
_RE_YOUTUBE_THUMB = re.compile(r"/vi/([A-Za-z0-9_-]{11})/")
_RE_VIMEO = re.compile(r"vimeo\.com/(?:video/)?(\d+)")


def _url_da_midia(tag: Tag) -> str:
    for atributo in ("src", "data", "href"):
        valor = (tag.get(atributo) or "").strip()
        if valor:
            return valor
    for filho in tag.find_all(("param", "embed", "iframe")):
        for atributo in ("value", "src", "data"):
            valor = (filho.get(atributo) or "").strip()
            if valor:
                return valor
    return ""


def bloco_video(tag: Tag, base: str | None = None) -> dict[str, Any] | None:
    url = _url_da_midia(tag)
    thumb = tag.get("data-thumbnail-src") or ""
    provedor, ident = "externo", None
    achado = _RE_YOUTUBE.search(url) or _RE_YOUTUBE.search(thumb)
    if achado:
        provedor, ident = "youtube", achado.group(1)
    else:
        achado = _RE_VIMEO.search(url)
        if achado:
            provedor, ident = "vimeo", achado.group(1)
    if not url and not ident:
        return None
    if ident and provedor == "youtube":
        url = "https://www.youtube.com/watch?v=" + ident
    elif ident and provedor == "vimeo":
        url = "https://vimeo.com/" + ident
    url = resolve_url(url, base)
    return {
        "tipo": "video",
        "provedor": provedor,
        "id": ident,
        "url": url,
        "titulo": (tag.get("title") or "").strip() or None,
        "duracao": None,
    }


def _credito_por_legenda(texto: str) -> tuple[str | None, str | None]:
    """Separa 'FOTO: JVRibas' em crédito; devolve (legenda limpa, crédito)."""
    if not texto:
        return None, None
    casamento = re.search(
        r"(?i)\b(foto(?:grafia)?|imagem|cr[eé]dito|divulga[cç][aã]o)\s*[:\-–]\s*([^|;]+)",
        texto,
    )
    if not casamento:
        return texto.strip() or None, None
    credito = re.sub(r"\s+", " ", casamento.group(2)).strip(" .,;")
    legenda = (texto[: casamento.start()] + texto[casamento.end():]).strip(" .,;|")
    return (normaliza(legenda) or None), (credito[:80] or None)


def bloco_imagem(tag: Tag, legenda: str | None = None, base: str | None = None) -> dict[str, Any] | None:
    src = resolve_url(tag.get("src"), base)
    if not src:
        return None
    alt = normaliza(tag.get("alt") or "").strip() or None
    href = None
    pai_a = tag.find_parent("a")
    if pai_a is not None:
        href = resolve_url(pai_a.get("href"), base)
    legenda_limpa, credito = _credito_por_legenda(legenda or "")
    if not legenda_limpa and not alt and pai_a is not None:
        # Às vezes a legenda mora no atributo title do link.
        legenda_limpa, credito = _credito_por_legenda(pai_a.get("title") or "")
    bloco = {
        "tipo": "imagem",
        "src": src,
        "alt": alt,
        "legenda": legenda_limpa,
        "credito": credito,
        # Sem licença declarada a imagem entra como link, nunca como arquivo.
        "licenca": "link",
    }
    if href:
        bloco["href"] = https(href)
    largura = tag.get("data-original-width") or tag.get("width")
    altura = tag.get("data-original-height") or tag.get("height")
    if largura and str(largura).isdigit():
        bloco["largura"] = int(largura)
    if altura and str(altura).isdigit():
        bloco["altura"] = int(altura)
    return bloco


# --------------------------------------------------------------------------
# O conversor: HTML -> lista de blocos
# --------------------------------------------------------------------------

class Contexto:
    """Acumula pendências e estatísticas de um post."""

    def __init__(self) -> None:
        self.pendencias: list[dict[str, str]] = []
        self.imagens: list[dict[str, Any]] = []
        self.descartados = 0
        # URL canônica do post: resolve link relativo e âncora de nota.
        self.base: str | None = None

    def nota(self, tipo: str, detalhe: str) -> None:
        self.pendencias.append({"tipo": tipo, "detalhe": detalhe})

    def registra_imagem(self, bloco: dict[str, Any]) -> None:
        origem = bloco.get("src")
        if any(i.get("origem") == origem for i in self.imagens):
            return
        self.imagens.append({
            "origem": origem,
            "credito": bloco.get("credito"),
            "legenda": bloco.get("legenda"),
            "licenca": "link",
        })


def _achata(no: Any, atomos: list[tuple[str, Any]]) -> None:
    """Percorre a árvore e alinha átomos: texto, quebra, imagem, mídia, bloco."""
    for filho in getattr(no, "children", []):
        if isinstance(filho, (Comment, Doctype)):
            continue
        if isinstance(filho, NavigableString):
            atomos.append(("texto", str(filho)))
            continue
        if not isinstance(filho, Tag):
            continue
        nome = (filho.name or "").lower()
        if nome in TAGS_DESCARTE:
            continue
        if nome == "br":
            atomos.append(("quebra", None))
        elif nome == "hr":
            atomos.append(("quebra", None))
        elif nome == "img":
            atomos.append(("img", filho))
        elif nome in TAGS_MIDIA:
            atomos.append(("midia", filho))
        elif nome in TAGS_TITULO:
            atomos.append(("titulo", filho))
        elif nome == "blockquote":
            atomos.append(("citacao", filho))
        elif nome in ("ul", "ol"):
            atomos.append(("lista", filho))
        elif nome == "table":
            atomos.append(("tabela", filho))
        elif nome == "pre":
            atomos.append(("pre", filho))
        elif nome == "a" and (filho.get("href") or "").strip():
            atomos.append(("ancora", filho))
        elif nome in TAGS_QUEBRA:
            atomos.append(("quebra", None))
            _achata(filho, atomos)
            atomos.append(("quebra", None))
        else:
            _achata(filho, atomos)


def _bloco_de_texto(buffer: list[Any], ctx: Contexto) -> list[dict[str, Any]]:
    """Fecha o buffer inline e devolve zero, um ou vários blocos."""
    if not buffer:
        return []
    partes: list[str] = []
    links: list[dict[str, Any]] = []
    for item in buffer:
        if isinstance(item, tuple):
            _, rotulo, url = item
            partes.append(rotulo)
            links.append({"texto": rotulo, "url": url, "externo": eh_externo(url)})
        else:
            partes.append(item)
    texto = normaliza("".join(partes))
    texto = " ".join(texto.split("\n"))  # quebra de linha já virou bloco
    if not tem_conteudo(texto):
        if texto:
            ctx.descartados += 1
        return []
    if links:
        ancoras = "".join(link["texto"] for link in links)
        resto = normaliza(texto.replace(ancoras, "", 1) if ancoras in texto else texto)
        if not tem_conteudo(resto) and len(links) >= 1:
            # O bloco inteiro é um link: vira bloco `link`, não parágrafo.
            return [
                {"tipo": "link", "texto": link["texto"], "url": link["url"], "externo": link["externo"]}
                for link in links
            ]
        return [{"tipo": "paragrafo", "texto": texto, "links": links}]
    return [{"tipo": "paragrafo", "texto": texto}]


def _bloco_legenda(no: Tag, ctx: Contexto) -> dict[str, Any] | None:
    """`table.tr-caption-container` = imagem com legenda."""
    img = no.find("img")
    if img is None:
        return None
    celula = no.select_one("td.tr-caption") or no.select_one("figcaption") or no.select_one(".caption")
    legenda = texto_de(celula, base=ctx.base) if celula is not None else ""
    return bloco_imagem(img, legenda, ctx.base)


def _bloco_lista(no: Tag, ctx: Contexto) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    itens: list[str] = []
    extras: list[dict[str, Any]] = []
    for item in no.find_all("li", recursive=False) or no.find_all("li"):
        texto = normaliza(item.get_text("\n", strip=True))
        texto = " ".join(parte for parte in texto.split("\n") if parte)
        if tem_conteudo(texto):
            itens.append(texto)
        for img in item.find_all("img"):
            bloco = bloco_imagem(img, texto, ctx.base)
            if bloco:
                ctx.registra_imagem(bloco)
                extras.append(bloco)
    if not itens:
        return None, extras
    return {"tipo": "lista", "ordenada": (no.name or "").lower() == "ol", "itens": itens}, extras


def _bloco_tabela(no: Tag, ctx: Contexto) -> list[dict[str, Any]]:
    classes = " ".join(no.get("class") or []).lower()
    if "tr-caption-container" in classes:
        bloco = _bloco_legenda(no, ctx)
        if bloco:
            ctx.registra_imagem(bloco)
            return [bloco]
    blocos: list[dict[str, Any]] = []
    linhas = no.find_all("tr")
    if not linhas:
        texto = texto_de(no, base=ctx.base)
        ctx.nota("tabela_achatada", "tabela sem linha legível virou parágrafo")
        return [{"tipo": "paragrafo", "texto": texto}] if tem_conteudo(texto) else []
    for linha in linhas:
        celulas = [texto_de(c, base=ctx.base) for c in linha.find_all(["td", "th"])]
        texto = " · ".join(c for c in celulas if c)
        if tem_conteudo(texto):
            blocos.append({"tipo": "paragrafo", "texto": texto})
    if blocos:
        ctx.nota("tabela_achatada", "tabela do original virou %d parágrafos" % len(blocos))
    return blocos


_RE_LEGENDA = re.compile(
    r"^(?:(?:esse|essa|este|esta|estes|estas)\s+"
    r"(?:cartaz|foto|fotografia|imagem|charge|v[ií]deo|mapa|gr[aá]fico|tabela|capa|logo|logomarca|"
    r"p[oô]ster|panfleto|livro|revista|documento|print|registro)\b)"
    r"|^(?:(?:foto|fotografia|imagem|legenda|cr[eé]dito|fonte|cartaz)\s*[:\-–])"
    r"|^(?:(?:a|o)\s+(?:foto|fotografia|imagem|cartaz|charge|v[ií]deo|mapa|gr[aá]fico)\b)",
    re.IGNORECASE,
)


def _junta_legenda_imagem(blocos: list[dict[str, Any]], ctx: Contexto) -> list[dict[str, Any]]:
    """Frase curta logo abaixo da imagem é legenda dela, não parágrafo solto.

    É o padrão do Blogger antigo: a imagem entra e a frase seguinte apresenta o
    cartaz ou a foto ("Esse cartaz é de um curso..."). O texto não se perde:
    vai para `legenda` do bloco de imagem, como pede a seção 7 do plano.
    """
    saida: list[dict[str, Any]] = []
    i = 0
    while i < len(blocos):
        bloco = blocos[i]
        seguinte = blocos[i + 1] if i + 1 < len(blocos) else None
        if (
            bloco["tipo"] == "imagem"
            and not bloco.get("legenda")
            and seguinte is not None
            and seguinte["tipo"] == "paragrafo"
            and len(seguinte["texto"]) <= 160
            and _RE_LEGENDA.match(seguinte["texto"])
        ):
            legenda, credito = _credito_por_legenda(seguinte["texto"])
            bloco["legenda"] = legenda
            if credito and not bloco.get("credito"):
                bloco["credito"] = credito
            for imagem in ctx.imagens:
                if imagem.get("origem") == bloco.get("src"):
                    imagem["legenda"] = legenda
                    imagem["credito"] = bloco.get("credito")
            saida.append(bloco)
            i += 2
            continue
        saida.append(bloco)
        i += 1
    return saida


def blocos_de(no: Any, ctx: Contexto) -> list[dict[str, Any]]:
    """Converte um contêiner HTML em blocos tipados, na ordem do original."""
    atomos: list[tuple[str, Any]] = []
    _achata(no, atomos)

    saida: list[dict[str, Any]] = []
    buffer: list[Any] = []

    def fecha() -> None:
        if not buffer:
            return
        saida.extend(_bloco_de_texto(buffer, ctx))
        buffer.clear()

    for tipo, dado in atomos:
        if tipo == "texto":
            # Todo nó de texto entra: espaço entre spans inline também é texto.
            buffer.append(str(dado))
        elif tipo == "ancora":
            # Link dentro do parágrafo: o texto entra no lugar e a URL fica
            # registrada no bloco, para o leitor chegar ao original.
            href = resolve_url(dado.get("href"), ctx.base)
            rotulo = normaliza(_texto_inline(dado, [], ctx.base))
            imagens = dado.find_all("img")
            if rotulo:
                buffer.append(("link", rotulo, href) if href else rotulo)
            if imagens:
                fecha()
                for img in imagens:
                    bloco = bloco_imagem(img, base=ctx.base)
                    if bloco:
                        ctx.registra_imagem(bloco)
                        saida.append(bloco)
        elif tipo == "quebra":
            fecha()
        elif tipo == "img":
            fecha()
            bloco = bloco_imagem(dado, base=ctx.base)
            if bloco:
                ctx.registra_imagem(bloco)
                saida.append(bloco)
        elif tipo == "midia":
            fecha()
            nome = (dado.name or "").lower()
            if nome == "param":
                continue
            bloco = bloco_video(dado, ctx.base)
            if bloco:
                if bloco.get("id") is None:
                    ctx.nota("video_sem_id", "mídia sem identificador reconhecido: %s" % (bloco.get("url") or "")[:80])
                saida.append(bloco)
        elif tipo == "titulo":
            fecha()
            texto = texto_de(dado, base=ctx.base)
            if tem_conteudo(texto) and not e_lixo(texto):
                nivel = int((dado.name or "h2")[1])
                saida.append({"tipo": "titulo", "texto": texto, "nivel": 2 if nivel <= 2 else (3 if nivel == 3 else 4)})
            else:
                ctx.descartados += 1
        elif tipo == "citacao":
            fecha()
            internos = blocos_de(dado, ctx)
            paragrafos = [b for b in internos if b["tipo"] == "paragrafo"]
            outros = [b for b in internos if b["tipo"] != "paragrafo"]
            if paragrafos:
                texto = "\n\n".join(b["texto"] for b in paragrafos)
                if e_lixo(texto):
                    ctx.descartados += 1
                else:
                    bloco: dict[str, Any] = {"tipo": "citacao", "texto": texto}
                    if len(paragrafos) > 1:
                        bloco["paragrafos"] = [b["texto"] for b in paragrafos]
                    links = [l for b in paragrafos for l in (b.get("links") or [])]
                    if links:
                        bloco["links"] = links
                    if "twitter-tweet" in " ".join(dado.get("class") or []):
                        ctx.nota("citacao_de_rede", "citação embutida do Twitter: confira no original")
                    saida.append(bloco)
            saida.extend(outros)
        elif tipo == "lista":
            fecha()
            bloco, extras = _bloco_lista(dado, ctx)
            if bloco:
                saida.append(bloco)
            saida.extend(extras)
        elif tipo == "tabela":
            fecha()
            saida.extend(_bloco_tabela(dado, ctx))
        elif tipo == "pre":
            fecha()
            texto = normaliza(dado.get_text("\n", strip=False))
            if tem_conteudo(texto):
                ctx.nota("texto_pre_formatado", "bloco <pre> guardado como parágrafo")
                saida.append({"tipo": "paragrafo", "texto": texto})
    fecha()

    # Filtro final: rabicho do Blogger, duplicata de bloco vazio, etc.
    saida = _junta_legenda_imagem(saida, ctx)
    limpos: list[dict[str, Any]] = []
    for bloco in saida:
        texto = bloco.get("texto") or " ".join(bloco.get("itens") or [])
        if bloco["tipo"] in ("paragrafo", "titulo", "citacao", "link") and e_lixo(texto, bloco.get("url")):
            ctx.descartados += 1
            continue
        limpos.append(bloco)
    return limpos


# --------------------------------------------------------------------------
# Metadados: página do post e entrada do feed
# --------------------------------------------------------------------------

def _meta(sopa: BeautifulSoup, **kwargs: Any) -> str | None:
    tag = sopa.find("meta", attrs=kwargs)
    if tag is None:
        return None
    return (tag.get("content") or "").strip() or None


def data_pt_br(texto: str) -> str | None:
    """'domingo, 16 de agosto de 2009' -> '2009-08-16'."""
    casamento = re.search(r"(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})", (texto or "").lower())
    if not casamento:
        return None
    dia, mes_nome, ano = casamento.groups()
    mes = MESES_PT.get(mes_nome) or MESES_PT.get(sem_acento(mes_nome))
    if not mes:
        return None
    try:
        return dt.date(int(ano), int(mes), int(dia)).isoformat()
    except ValueError:
        return None


def le_pagina(html: str) -> tuple[dict[str, Any], Tag | None]:
    """Extrai metadados e o `.post-body` de uma página de post do Blogger.

    A ordem importa: título, autor e URL canônica moram no cabeçalho e no
    rodapé do post, que a limpeza remove. Lê primeiro, limpa depois.
    """
    sopa = BeautifulSoup(html, "lxml")
    dados: dict[str, Any] = {}

    titulo_tag = sopa.select_one("h1.post-title, h2.post-title, h3.post-title, .entry-title")
    dados["titulo"] = texto_de(titulo_tag) if titulo_tag is not None else None
    if not dados["titulo"]:
        dados["titulo"] = normaliza(_meta(sopa, property="og:title") or "") or None
    if not dados["titulo"] and sopa.title is not None:
        dados["titulo"] = normaliza(sopa.title.get_text()).split(":", 1)[-1].strip() or None

    canonical = sopa.find("link", rel=lambda v: v and "canonical" in v)
    dados["url"] = https(canonical.get("href")) if canonical and canonical.get("href") else None
    if not dados["url"]:
        dados["url"] = https(_meta(sopa, property="og:url") or "") or None

    publicado = sopa.select_one("abbr.published[title], time[datetime]")
    data = None
    if publicado is not None:
        bruto = publicado.get("title") or publicado.get("datetime") or ""
        data = bruto[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", bruto) else None
    if not data:
        cabecalho = sopa.select_one("h2.date-header")
        if cabecalho is not None:
            data = data_pt_br(cabecalho.get_text())
    if not data:
        data = (_meta(sopa, itemprop="datePublished") or "")[:10] or None
    dados["data"] = data

    autor_tag = sopa.select_one(".post-author .fn, .post-author [itemprop=name], .post-author a")
    dados["autor_nome"] = texto_de(autor_tag) if autor_tag is not None else None
    if not dados["autor_nome"]:
        texto_autor = texto_de(sopa.select_one(".post-author") or Tag(name="span"))
        dados["autor_nome"] = re.sub(r"(?i)^postado por\s+", "", texto_autor).strip() or None
    link_autor = sopa.select_one(".post-author a[href*='blogger.com/profile']")
    dados["autor_url"] = https(link_autor.get("href")) if link_autor is not None and link_autor.get("href") else None
    if not dados["autor_url"]:
        meta_url = sopa.select_one(".post-author meta[itemprop=url]")
        dados["autor_url"] = https(meta_url.get("content") or "") or None if meta_url is not None else None

    corpo = None
    for seletor in ("div.post-body", "div.entry-content", "div[itemprop=articleBody]", "article"):
        corpo = sopa.select_one(seletor)
        if corpo is not None:
            break
    if corpo is not None:
        # O rodapé do post costuma vir colado no fim do corpo: corta.
        for lixo in corpo.select("div.post-footer, div.blogger-post-footer"):
            lixo.decompose()
    return dados, corpo


def le_feed(caminho_pasta: str) -> tuple[list[dict[str, Any]], str]:
    """Lê as páginas do feed Atom e devolve as entradas e o id do blog."""
    entradas: list[dict[str, Any]] = []
    blog_id = BLOG_ID_PADRAO
    for caminho in sorted(glob.glob(os.path.join(caminho_pasta, "feed-*.json"))):
        with io.open(caminho, encoding="utf-8") as f:
            pagina = json.load(f)
        raiz = pagina.get("feed", {})
        identificador = (raiz.get("id") or {}).get("$t") or ""
        if "blog-" in identificador:
            blog_id = identificador.rsplit("blog-", 1)[-1]
        entradas.extend(raiz.get("entry") or [])
    return entradas, blog_id


def id_do_post(entrada: dict[str, Any]) -> str:
    return (entrada.get("id", {}).get("$t") or "").rsplit("-", 1)[-1]


def url_do_feed(entrada: dict[str, Any]) -> str | None:
    for link in entrada.get("link") or []:
        if link.get("rel") == "alternate" and link.get("href"):
            return https(link["href"])
    return None


def autor_do_feed(entrada: dict[str, Any]) -> tuple[str | None, str | None]:
    autor = (entrada.get("author") or [{}])[0]
    nome = normaliza((autor.get("name") or {}).get("$t") or "") or None
    url = (autor.get("uri") or {}).get("$t") or None
    return nome, https(url) if url else None


# --------------------------------------------------------------------------
# Slug, resumo e temas
# --------------------------------------------------------------------------

def slug_de(titulo: str, registrados: dict[str, int]) -> str:
    base = sem_acento(titulo or "")
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    if not base:
        base = "post-sem-titulo"
    if len(base) > SLUG_MAX:
        corte = base[:SLUG_MAX]
        if "-" in corte:
            corte = corte.rsplit("-", 1)[0]
        base = corte.strip("-")
    slug = base
    if slug in registrados:
        registrados[slug] += 1
        sufixo = "-%d" % registrados[slug]
        slug = base[: SLUG_MAX - len(sufixo)].rstrip("-") + sufixo
        while slug in registrados:
            registrados[base] += 1
            sufixo = "-%d" % registrados[base]
            slug = base[: SLUG_MAX - len(sufixo)].rstrip("-") + sufixo
        registrados[slug] = 1
    else:
        registrados[slug] = 1
    return slug


def resumo_de(blocos: list[dict[str, Any]], titulo: str = "", limite: int = 220) -> tuple[str, bool]:
    """Primeiro parágrafo útil, cortado em fim de frase. Devolve (texto, cortado)."""
    juntado = ""
    for bloco in blocos:
        if bloco["tipo"] not in ("paragrafo", "citacao"):
            continue
        if len(juntado) >= 90:
            break
        juntado = (juntado + " " + bloco["texto"]).strip()
    if not juntado:
        # Post só de mídia: a legenda ou o alt já dizem do que se trata.
        for bloco in blocos:
            if bloco["tipo"] == "lista" and bloco.get("itens"):
                juntado = bloco["itens"][0]
                break
            if bloco["tipo"] == "imagem" and (bloco.get("legenda") or bloco.get("alt")):
                juntado = bloco.get("legenda") or bloco.get("alt") or ""
                break
            if bloco["tipo"] == "link" and bloco.get("texto"):
                juntado = "Publicação indica %s." % bloco["texto"]
                break
            if bloco["tipo"] == "titulo":
                juntado = bloco["texto"]
                break
    if not juntado:
        juntado = titulo or ""
    if len(juntado) <= limite:
        return juntado, False
    corte = juntado[:limite]
    fim = max(corte.rfind(". "), corte.rfind("! "), corte.rfind("? "))
    if fim >= limite * 0.5:
        return corte[: fim + 1].strip(), True
    return corte.rsplit(" ", 1)[0].rstrip(",;:") + "…", True


def temas_de(titulo: str, blocos: list[dict[str, Any]], categorias: list[str]) -> tuple[list[str], bool]:
    """1 tema principal + até 3 secundários, por palavra-chave e categoria."""
    corpo = " ".join(
        (b.get("texto") or " ".join(b.get("itens") or [])) for b in blocos
    )
    titulo_n = sem_acento(titulo or "")
    corpo_n = sem_acento(corpo[:20000])
    cats_n = [sem_acento(c) for c in categorias]

    pontos: dict[str, int] = {tema: 0 for tema in VOCABULARIO_TEMAS}
    for tema, termos in REGRAS_TEMA.items():
        for termo, peso in termos:
            if termo in titulo_n:
                pontos[tema] += peso * 3
            if any(termo in c for c in cats_n):
                pontos[tema] += peso * 2
            ocorrencias = corpo_n.count(termo)
            if ocorrencias:
                pontos[tema] += peso * min(ocorrencias, 5)

    # Categoria explícita do Blogger manda mais que palavra solta no corpo.
    for cat in cats_n:
        alvo = CATEGORIA_PARA_TEMA.get(cat)
        if alvo:
            pontos[alvo] += 8

    ordenado = sorted(
        ((tema, nota) for tema, nota in pontos.items() if nota > 0),
        key=lambda par: (-par[1], par[0]),
    )
    if not ordenado or ordenado[0][1] < 3:
        return ["assessoria-juridica-popular"], True  # tema por padrão: revisar
    principal, nota_principal = ordenado[0]
    secundarios = [
        tema for tema, nota in ordenado[1:4]
        if nota >= 3 and nota >= nota_principal * 0.2
    ]
    return [principal] + secundarios, False


# --------------------------------------------------------------------------
# Montagem do registro
# --------------------------------------------------------------------------

def titulo_da_url(url: str | None) -> str | None:
    """Último recurso quando o feed e a página vêm sem título."""
    if not url:
        return None
    pedaco = url.rstrip("/").rsplit("/", 1)[-1]
    pedaco = re.sub(r"\.html?$", "", pedaco)
    pedaco = re.sub(r"[-_]+", " ", pedaco).strip()
    if not pedaco:
        return None
    return pedaco[:1].upper() + pedaco[1:]


def monta_registro(
    *,
    post_id: str,
    blog_id: str,
    dados_pagina: dict[str, Any] | None,
    corpo_html: str | None,
    entrada_feed: dict[str, Any] | None,
    hash_html: str | None,
    origem_html: str,
    capturado_em: str,
    registrados: dict[str, int],
) -> dict[str, Any] | None:
    titulo = (dados_pagina or {}).get("titulo") or None
    data = (dados_pagina or {}).get("data") or None
    url = (dados_pagina or {}).get("url") or None
    autor_nome = (dados_pagina or {}).get("autor_nome") or None
    autor_url = (dados_pagina or {}).get("autor_url") or None
    categorias: list[str] = []

    if entrada_feed is not None:
        titulo = titulo or normaliza((entrada_feed.get("title") or {}).get("$t") or "") or None
        publicado = (entrada_feed.get("published") or {}).get("$t") or ""
        data = data or (publicado[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", publicado) else None)
        url = url or url_do_feed(entrada_feed)
        nome_feed, url_feed = autor_do_feed(entrada_feed)
        autor_nome = autor_nome or nome_feed
        autor_url = autor_url or url_feed
        categorias = [normaliza((c.get("term") or "")) for c in (entrada_feed.get("category") or [])]

    if not corpo_html:
        return None

    ctx = Contexto()
    ctx.base = url
    sopa_corpo = BeautifulSoup(corpo_html, "lxml")
    limpa_soup(sopa_corpo)
    blocos = blocos_de(sopa_corpo, ctx)
    if not blocos:
        return None

    # Título vazio no feed: usa o endereço e avisa o revisor.
    titulo_por_url = False
    if not titulo:
        titulo = titulo_da_url(url)
        titulo_por_url = True
        if not titulo:
            return None

    resumo, resumo_cortado = resumo_de(blocos, titulo)
    temas, tema_por_padrao = temas_de(titulo, blocos, categorias)
    slug = slug_de(titulo, registrados)

    pendencias: list[dict[str, str]] = list(ctx.pendencias)
    notas: list[str] = []
    if origem_html == "feed":
        notas.append("conteúdo veio do feed Atom: a página do post ainda não estava baixada")
    if titulo_por_url:
        pendencias.append({"tipo": "titulo_ausente", "detalhe": "o original veio sem título; usei o endereço"})
        notas.append("título reconstruído a partir do endereço: confirmar no original")
    if autor_nome and sem_acento(autor_nome) in AUTORES_GENERICOS:
        pendencias.append({"tipo": "autor_generico", "detalhe": "o original assina como '%s'; confirmar autoria" % autor_nome})
    if tema_por_padrao:
        pendencias.append({"tipo": "tema_por_padrao", "detalhe": "nenhuma palavra-chave marcou tema; caiu no principal"})
    if resumo_cortado:
        notas.append("resumo cortado automaticamente em fim de frase")
    if len(resumo) < 60:
        pendencias.append({"tipo": "resumo_curto", "detalhe": "resumo automático com %d caracteres" % len(resumo)})
    if not any(b["tipo"] in ("paragrafo", "citacao", "lista", "titulo") for b in blocos):
        pendencias.append({"tipo": "post_so_midia", "detalhe": "post sem texto: só imagem, vídeo ou link"})
    for bloco in blocos:
        if bloco["tipo"] == "imagem" and not bloco.get("credito"):
            pendencias.append({"tipo": "imagem_sem_credito", "detalhe": (bloco.get("src") or "")[:90]})
            break
    tipografico = re.findall(r"(?i)\b(ver mais|see more)\b", json.dumps(blocos, ensure_ascii=False))
    if tipografico:
        pendencias.append({"tipo": "texto_cortado_na_origem", "detalhe": "texto de rede social com 'ver mais' no original"})

    registro: dict[str, Any] = {
        "id": "tag:blogger.com,1999:blog-%s.post-%s" % (blog_id, post_id),
        "slug": slug,
        "titulo": titulo,
        "data": data,
        "autor": {"nome": autor_nome, "url": autor_url},
        "fonte": {
            "site": SITE,
            "url": url,
            "capturado_em": capturado_em,
            "licenca": LICENCA_PADRAO,
            "hash_html": hash_html,
            "origem_html": origem_html,
            "user_agent": UA,
        },
        "resumo": resumo,
        "temas": temas,
        "blocos": blocos,
        "imagens": ctx.imagens,
        "categorias_blogger": categorias,
        # Quantos blocos o parser jogou fora (rabicho, parágrafo vazio, cromo).
        "descartes": ctx.descartados,
        "revisao": {"estado": "pendente", "notas": notas, "pendencias": pendencias},
    }
    return registro


def hash_de(texto: bytes) -> str:
    return "sha256:" + hashlib.sha256(texto).hexdigest()


def carrega_pagina(caminho: str) -> tuple[dict[str, Any], str, str | None] | None:
    """Lê a página baixada. Devolve (dados, html do corpo, hash) ou None."""
    with io.open(caminho, "rb") as f:
        bruto = f.read()
    if len(bruto) < TAMANHO_MINIMO_PAGINA:
        return None
    html = bruto.decode("utf-8", errors="replace")
    if "</html>" not in html.lower():
        return None  # download interrompido
    dados, corpo = le_pagina(html)
    if corpo is None:
        return None
    return dados, str(corpo), hash_de(bruto)


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def processa(
    *,
    pasta_posts: str,
    pasta_feed: str,
    pasta_saida: str,
    limite: int | None,
    capturado_em: str,
    fonte: str,
) -> dict[str, Any]:
    entradas, blog_id = le_feed(pasta_feed) if fonte in ("auto", "feed") else ([], BLOG_ID_PADRAO)
    por_id = {id_do_post(e): e for e in entradas}

    # Ordem de trabalho: a do feed (mais recente primeiro), igual à do download.
    fila: list[tuple[str, dict[str, Any] | None]] = []
    for entrada in entradas:
        fila.append((id_do_post(entrada), entrada))
    if not entradas:
        for caminho in sorted(glob.glob(os.path.join(pasta_posts, "*.html"))):
            fila.append((os.path.splitext(os.path.basename(caminho))[0], None))

    os.makedirs(pasta_saida, exist_ok=True)
    registrados: dict[str, int] = {}
    registros: list[dict[str, Any]] = []
    pulados: list[dict[str, str]] = []
    sem_pagina = 0
    usou_feed = 0

    for post_id, entrada in fila:
        if limite is not None and len(registros) >= limite:
            break

        dados_pagina = None
        corpo_html = None
        hash_html = None
        origem = "pagina"

        if fonte != "feed":
            caminho = os.path.join(pasta_posts, post_id + ".html")
            if os.path.exists(caminho):
                lido = carrega_pagina(caminho)
                if lido is not None:
                    dados_pagina, corpo_html, hash_html = lido
                else:
                    sem_pagina += 1

        if corpo_html is None and fonte != "pagina" and entrada is not None:
            conteudo = (entrada.get("content") or {}).get("$t") or ""
            if conteudo.strip():
                corpo_html = conteudo
                hash_html = hash_de(conteudo.encode("utf-8"))
                origem = "feed"
                usou_feed += 1

        if corpo_html is None:
            pulados.append({"id": post_id, "motivo": "sem HTML de página completo e sem conteúdo no feed"})
            continue

        registro = monta_registro(
            post_id=post_id,
            blog_id=blog_id,
            dados_pagina=dados_pagina,
            corpo_html=corpo_html,
            entrada_feed=entrada or por_id.get(post_id),
            hash_html=hash_html,
            origem_html=origem,
            capturado_em=capturado_em,
            registrados=registrados,
        )
        if registro is None:
            pulados.append({"id": post_id, "motivo": "corpo sem bloco aproveitável"})
            continue

        destino = os.path.join(pasta_saida, registro["slug"] + ".json")
        with io.open(destino, "w", encoding="utf-8") as f:
            json.dump(registro, f, ensure_ascii=False, indent=1)
            f.write("\n")
        registros.append(registro)

    relatorio = monta_relatorio(registros, pulados, capturado_em, sem_pagina, usou_feed)
    with io.open(os.path.join(pasta_saida, "_relatorio.json"), "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return relatorio


def monta_relatorio(
    registros: list[dict[str, Any]],
    pulados: list[dict[str, str]],
    capturado_em: str,
    sem_pagina: int,
    usou_feed: int,
) -> dict[str, Any]:
    por_tipo: dict[str, int] = {}
    temas: dict[str, int] = {}
    pendencias: dict[str, int] = {}
    itens_pendencia: list[dict[str, str]] = []
    total_imagens = 0
    total_links = 0
    total_externos = 0
    origens: dict[str, int] = {}
    total_descartes = 0
    vistos: dict[tuple[str, str], str] = {}
    duplicatas: list[dict[str, str]] = []

    for registro in registros:
        for bloco in registro["blocos"]:
            por_tipo[bloco["tipo"]] = por_tipo.get(bloco["tipo"], 0) + 1
            for link in bloco.get("links") or []:
                total_links += 1
                if link.get("externo"):
                    total_externos += 1
            if bloco["tipo"] == "link":
                total_links += 1
                if bloco.get("externo"):
                    total_externos += 1
        for tema in registro["temas"]:
            temas[tema] = temas.get(tema, 0) + 1
        total_imagens += len(registro["imagens"])
        total_descartes += int(registro.get("descartes") or 0)
        origens[registro["fonte"]["origem_html"]] = origens.get(registro["fonte"]["origem_html"], 0) + 1
        for pendencia in registro["revisao"]["pendencias"]:
            pendencias[pendencia["tipo"]] = pendencias.get(pendencia["tipo"], 0) + 1
            if len(itens_pendencia) < 200:
                itens_pendencia.append({
                    "slug": registro["slug"],
                    "tipo": pendencia["tipo"],
                    "detalhe": pendencia["detalhe"],
                })
        chave = (registro["titulo"], registro["data"] or "")
        if chave in vistos:
            duplicatas.append({"slug": registro["slug"], "igual_de": vistos[chave]})
        else:
            vistos[chave] = registro["slug"]

    return {
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "capturado_em": capturado_em,
        "user_agent": UA,
        "total_posts": len(registros),
        "origem_do_html": origens,
        "paginas_incompletas": sem_pagina,
        "posts_do_feed": usou_feed,
        "blocos_por_tipo": dict(sorted(por_tipo.items(), key=lambda par: -par[1])),
        "total_blocos": sum(por_tipo.values()),
        "descartes": total_descartes,
        "imagens": total_imagens,
        "links": total_links,
        "links_externos": total_externos,
        "temas": dict(sorted(temas.items(), key=lambda par: -par[1])),
        "pendencias": dict(sorted(pendencias.items(), key=lambda par: -par[1])),
        "total_pendencias": sum(pendencias.values()),
        "itens_pendencia": itens_pendencia,
        "duplicatas": duplicatas,
        "pulados": pulados,
        "posts": [
            {
                "slug": r["slug"],
                "titulo": r["titulo"],
                "data": r["data"],
                "autor": (r["autor"] or {}).get("nome"),
                "temas": r["temas"],
                "blocos": len(r["blocos"]),
                "imagens": len(r["imagens"]),
                "origem_html": r["fonte"]["origem_html"],
                "pendencias": len(r["revisao"]["pendencias"]),
            }
            for r in registros
        ],
    }


def main(argv: list[str] | None = None) -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Converte o HTML da Assessoria Jurídica Popular em blocos tipados.")
    ap.add_argument("--posts", default=PADRAO_POSTS, help="pasta com os HTMLs por post")
    ap.add_argument("--feed", default=PADRAO_FEED, help="pasta com feed-000N.json")
    ap.add_argument("--saida", default=PADRAO_SAIDA, help="pasta de destino do JSON")
    ap.add_argument("--limite", type=int, default=20, help="quantos posts processar (0 = todos)")
    ap.add_argument("--todos", action="store_true", help="processa o acervo inteiro")
    ap.add_argument("--fonte", choices=("auto", "pagina", "feed"), default="auto",
                    help="auto: página se existir, senão feed; pagina: exige página; feed: só Atom")
    ap.add_argument("--capturado-em", default=dt.date.today().isoformat(),
                    help="data da captura gravada em fonte.capturado_em")
    args = ap.parse_args(argv)

    limite = None if args.todos or args.limite == 0 else args.limite
    if not os.path.isdir(args.posts) and args.fonte != "feed":
        print("aviso: pasta de posts ausente (%s); vou usar o feed" % args.posts)
        args.fonte = "feed"

    relatorio = processa(
        pasta_posts=args.posts,
        pasta_feed=args.feed,
        pasta_saida=args.saida,
        limite=limite,
        capturado_em=args.capturado_em,
        fonte=args.fonte,
    )

    print("posts gravados: %d em %s" % (relatorio["total_posts"], args.saida))
    print("origem do HTML:", relatorio["origem_do_html"])
    print("blocos por tipo:", relatorio["blocos_por_tipo"])
    print("blocos descartados (cromo e vazios): %d" % relatorio["descartes"])
    print("imagens: %d | links: %d (externos: %d)" % (
        relatorio["imagens"], relatorio["links"], relatorio["links_externos"]))
    print("temas:", relatorio["temas"])
    print("pendências: %d %s" % (relatorio["total_pendencias"], relatorio["pendencias"]))
    if relatorio["pulados"]:
        print("pulados: %d" % len(relatorio["pulados"]))
    print("relatório:", os.path.join(args.saida, "_relatorio.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
