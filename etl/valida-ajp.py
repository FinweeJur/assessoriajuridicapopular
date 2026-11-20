#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Valida os JSON do acervo da Assessoria Jurídica Popular contra o schema do plano.

**Fonte oficial:** o schema está em
`docs/PLANO-ETL-ASSESSORIA-JURIDICA-POPULAR.md`, seção 5 (modelo de dados) e
seção 4.2 (tabela de blocos e tipos permitidos).

**Por que existe:** o parser é tolerante de propósito — ele não pode perder um
post por causa de HTML quebrado. A tolerância fica ali; a régua fica aqui. Este
módulo não corrige nada: ele lê, compara com o contrato e diz o que quebrou,
para o revisor humano decidir antes de a carga entrar no build.

**O que ele confere:**

- campos obrigatórios e tipos (`id`, `slug`, `titulo`, `data`, `autor.nome`,
  `fonte.url`, `fonte.capturado_em`, `fonte.licenca`, `blocos`, `revisao.estado`);
- formato: data ISO real, slug sem acento e com até 60 caracteres, hash
  `sha256:` de 64 dígitos, licença dentro do vocabulário fechado, tema dentro
  dos seis do plano;
- blocos: tipo conhecido, texto não vazio, sem HTML cru sobrando, `lista` com
  itens, `imagem`/`video`/`link` com endereço, `titulo` com nível 2 a 4;
- privacidade: CPF válido por mod-11 é **erro**, e-mail e telefone são aviso —
  comentarista e terceiro não entram no acervo (regra 5.8);
- acervo: `id` e `slug` únicos, título+data repetido vira aviso de duplicata.

Uso:
    python etl/valida-ajp.py
    python etl/valida-ajp.py "G:\\Meu Drive\\RENAP-AJP\\staging"
    python etl/valida-ajp.py --json relatorio-validacao.json --quieto
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import io
import json
import os
import re
import sys
import unicodedata
from typing import Any

RAIZ_DADOS = r"G:\Meu Drive\RENAP-AJP"
PADRAO_STAGING = os.path.join(RAIZ_DADOS, "staging")

HOST_BLOG = "assessoriajuridicapopular.blogspot.com"
LICENCAS = {"autorizado", "citacao", "resumo"}
LICENCAS_IMAGEM = {"autorizado", "citacao", "link"}
ESTADOS_REVISAO = {"pendente", "aprovado", "rejeitado"}
PROVEDORES_VIDEO = {"youtube", "vimeo", "externo"}

TEMAS = {
    "assessoria-juridica-popular",
    "educacao-popular",
    "movimentos-sociais",
    "direitos-humanos",
    "memoria",
    "teoria-critica",
}

CAMPOS_OBRIGATORIOS = (
    "id", "slug", "titulo", "data", "autor", "fonte", "blocos", "revisao",
)
CAMPOS_OPCIONAIS = {"resumo", "temas", "imagens", "categorias_blogger", "descartes"}
CAMPOS_FONTE = {"site", "url", "capturado_em", "licenca", "hash_html"}
CAMPOS_FONTE_EXTRAS = {"origem_html", "user_agent"}

TIPOS_BLOCO = {"paragrafo", "titulo", "citacao", "lista", "imagem", "video", "link"}

RE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RE_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_HTTP = re.compile(r"^https?://\S+$", re.IGNORECASE)
RE_ESQUEMA = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):")
# Tag de verdade: nome, depois espaço, '/' ou '>'. Isso poupa a citação em
# estilo ABNT "<http://exemplo.com>" que o autor escreveu à mão.
RE_TAG = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s[^<>]*)?/?>")
RE_ENTIDADE = re.compile(r"&(?:nbsp|amp|lt|gt|quot|#\d+);")
RE_CONTROLE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
RE_TELEFONE = re.compile(r"(?:\(?\d{2}\)?[\s-]?)?9?\d{4}[\s-]?\d{4}\b")
RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")

# Frases que já deveriam ter sido descartadas pelo parser (tabela 4.2).
LIXO_PROIBIDO = (
    "tecnologia do blogger",
    "postado por ",
    "postar coment",
    "mapeamento",
    "colunistas",
)


class Relatorio:
    """Acumula erros e avisos por arquivo."""

    def __init__(self) -> None:
        self.arquivos = 0
        self.ok = 0
        self.com_erro = 0
        self.com_aviso = 0
        self.erros: list[dict[str, str]] = []
        self.avisos: list[dict[str, str]] = []
        self.por_tipo: dict[str, int] = {}
        self.por_tema: dict[str, int] = {}

    def erro(self, arquivo: str, campo: str, mensagem: str) -> None:
        self.erros.append({"arquivo": arquivo, "campo": campo, "mensagem": mensagem})

    def aviso(self, arquivo: str, campo: str, mensagem: str) -> None:
        self.avisos.append({"arquivo": arquivo, "campo": campo, "mensagem": mensagem})


def sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in decomposto if not unicodedata.combining(c)).lower()


def cpf_valido(digitos: str) -> bool:
    """Mod-11 do CPF: só conta o que é CPF de verdade, não qualquer número."""
    numeros = [int(d) for d in digitos if d.isdigit()]
    if len(numeros) != 11 or len(set(numeros)) == 1:
        return False
    for corte in (9, 10):
        soma = sum(n * p for n, p in zip(numeros[:corte], range(corte + 1, 1, -1)))
        digito = (soma * 10 % 11) % 10
        if digito != numeros[corte]:
            return False
    return True


def texto_suspeito(rel: Relatorio, arquivo: str, campo: str, texto: str) -> None:
    """Varre o texto: CPF é erro, e-mail e telefone são aviso."""
    if not texto:
        return
    for achado in RE_CPF.findall(texto):
        if cpf_valido(achado):
            rel.erro(arquivo, campo, "CPF válido no texto — dado pessoal não entra no acervo")
            break
    for email in RE_EMAIL.findall(texto):
        rel.aviso(arquivo, campo, "e-mail no texto (%s): conferir se é institucional" % email)
        break
    for telefone in RE_TELEFONE.findall(texto):
        if len(re.sub(r"\D", "", telefone)) in (10, 11) and not re.search(r"[./-]\d{2}$", telefone):
            rel.aviso(arquivo, campo, "número com cara de telefone (%s): conferir" % telefone)
            break


def url_aceita(valor: Any) -> bool:
    """http(s) e mailto são endereço; outro esquema é pendência, não erro."""
    texto = str(valor or "")
    return bool(RE_HTTP.match(texto)) or texto.startswith("mailto:")


def url_de_outro_esquema(valor: Any) -> str | None:
    casamento = RE_ESQUEMA.match(str(valor or ""))
    if not casamento:
        return None
    esquema = casamento.group(1).lower()
    if esquema in ("http", "https", "mailto"):
        return None
    return esquema


def valida_data(valor: Any) -> bool:
    if not isinstance(valor, str) or not RE_DATA.match(valor):
        return False
    try:
        dt.date.fromisoformat(valor)
    except ValueError:
        return False
    return True


def valida_bloco(rel: Relatorio, arquivo: str, posicao: int, bloco: Any, imagens_listadas: set[str]) -> str | None:
    campo = "blocos[%d]" % posicao
    if not isinstance(bloco, dict):
        rel.erro(arquivo, campo, "bloco não é objeto")
        return None
    tipo = bloco.get("tipo")
    if tipo not in TIPOS_BLOCO:
        rel.erro(arquivo, campo + ".tipo", "tipo desconhecido: %r" % (tipo,))
        return None

    def exige_texto(chave: str = "texto", minimo: int = 1) -> str:
        valor = bloco.get(chave)
        if not isinstance(valor, str) or len(valor.strip()) < minimo:
            rel.erro(arquivo, campo + "." + chave, "texto vazio ou ausente")
            return ""
        if RE_TAG.search(valor):
            rel.erro(arquivo, campo + "." + chave, "HTML cru no texto")
        if RE_ENTIDADE.search(valor):
            rel.erro(arquivo, campo + "." + chave, "entidade HTML não resolvida")
        if RE_CONTROLE.search(valor):
            rel.erro(arquivo, campo + "." + chave, "caractere de controle no texto")
        return valor

    if tipo in ("paragrafo", "titulo", "citacao"):
        texto = exige_texto()
        baixo = sem_acento(texto)
        for proibido in LIXO_PROIBIDO:
            if baixo.startswith(proibido) or baixo == proibido.strip():
                rel.erro(arquivo, campo + ".texto", "cromo do Blogger não descartado (%r)" % proibido.strip())
                break
        if tipo == "titulo":
            nivel = bloco.get("nivel")
            if nivel not in (2, 3, 4):
                rel.erro(arquivo, campo + ".nivel", "nível de título fora de 2..4: %r" % (nivel,))
        if tipo == "paragrafo" and len(texto) > 8000:
            rel.aviso(arquivo, campo, "parágrafo muito longo (%d caracteres): conferir quebra" % len(texto))
        texto_suspeito(rel, arquivo, campo + ".texto", texto)
        for i, link in enumerate(bloco.get("links") or []):
            if not isinstance(link, dict):
                rel.erro(arquivo, campo + ".links[%d]" % i, "link não é objeto")
                continue
            if not url_aceita(link.get("url")):
                esquema = url_de_outro_esquema(link.get("url"))
                if esquema:
                    rel.aviso(arquivo, campo + ".links[%d].url" % i, "link com esquema '%s': conferir se abre" % esquema)
                else:
                    rel.erro(arquivo, campo + ".links[%d].url" % i, "URL inválida: %r" % (link.get("url"),))
            if not str(link.get("texto") or "").strip():
                rel.erro(arquivo, campo + ".links[%d].texto" % i, "link sem texto")

    elif tipo == "lista":
        itens = bloco.get("itens")
        if not isinstance(itens, list) or not itens:
            rel.erro(arquivo, campo + ".itens", "lista sem itens")
        else:
            for i, item in enumerate(itens):
                if not isinstance(item, str) or not item.strip():
                    rel.erro(arquivo, campo + ".itens[%d]" % i, "item vazio")
                elif RE_TAG.search(item):
                    rel.erro(arquivo, campo + ".itens[%d]" % i, "HTML cru no item")
        if not isinstance(bloco.get("ordenada"), bool):
            rel.aviso(arquivo, campo + ".ordenada", "campo 'ordenada' deveria ser booleano")

    elif tipo == "imagem":
        src = bloco.get("src")
        if not isinstance(src, str) or not RE_HTTP.match(src):
            rel.erro(arquivo, campo + ".src", "imagem sem URL http(s)")
        elif src not in imagens_listadas:
            rel.erro(arquivo, campo + ".src", "imagem do bloco não está na lista `imagens`")
        if bloco.get("licenca") not in LICENCAS_IMAGEM:
            rel.erro(arquivo, campo + ".licenca", "licença de imagem fora do vocabulário: %r" % (bloco.get("licenca"),))
        for chave in ("alt", "legenda", "credito"):
            if bloco.get(chave) is not None and not isinstance(bloco.get(chave), str):
                rel.erro(arquivo, campo + "." + chave, "deveria ser texto ou nulo")
        if not bloco.get("credito"):
            rel.aviso(arquivo, campo, "imagem sem crédito: exibir como link e pedir crédito")

    elif tipo == "video":
        if bloco.get("provedor") not in PROVEDORES_VIDEO:
            rel.erro(arquivo, campo + ".provedor", "provedor desconhecido: %r" % (bloco.get("provedor"),))
        if not bloco.get("id") and not bloco.get("url"):
            rel.erro(arquivo, campo, "vídeo sem id e sem URL")
            if bloco.get("url") and not url_aceita(bloco["url"]):
                if url_de_outro_esquema(bloco["url"]):
                    rel.aviso(arquivo, campo + ".url", "vídeo servido por '%s' (fora da web): o original já estava morto" % url_de_outro_esquema(bloco["url"]))
                else:
                    rel.erro(arquivo, campo + ".url", "URL de vídeo inválida")

    elif tipo == "link":
        url = str(bloco.get("url") or "")
        if not url_aceita(url):
            esquema = url_de_outro_esquema(url)
            if esquema:
                rel.aviso(arquivo, campo + ".url", "link com esquema '%s': conferir se abre" % esquema)
            else:
                rel.erro(arquivo, campo + ".url", "URL inválida: %r" % (url or None,))
        exige_texto()
        if not isinstance(bloco.get("externo"), bool):
            rel.aviso(arquivo, campo + ".externo", "campo 'externo' deveria ser booleano")
    return tipo


def valida_registro(rel: Relatorio, arquivo: str, dado: Any) -> tuple[str | None, str | None, str | None, str | None]:
    """Valida um post. Devolve (id, slug, titulo, data) para checar duplicata."""
    if not isinstance(dado, dict):
        rel.erro(arquivo, "-", "JSON raiz não é objeto")
        return None, None, None, None

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in dado:
            rel.erro(arquivo, campo, "campo obrigatório ausente")
    extras = set(dado) - set(CAMPOS_OBRIGATORIOS) - CAMPOS_OPCIONAIS
    for extra in sorted(extras):
        rel.aviso(arquivo, extra, "campo fora do schema")

    identificador = dado.get("id")
    if not isinstance(identificador, str) or not identificador.startswith("tag:blogger.com"):
        rel.erro(arquivo, "id", "id fora do padrão Atom do Blogger")

    slug = dado.get("slug")
    if not isinstance(slug, str) or not RE_SLUG.match(slug):
        rel.erro(arquivo, "slug", "slug inválido: %r" % (slug,))
        slug = None
    elif len(slug) > 60:
        rel.erro(arquivo, "slug", "slug com %d caracteres (máximo 60)" % len(slug))

    titulo = dado.get("titulo")
    if not isinstance(titulo, str) or not titulo.strip():
        rel.erro(arquivo, "titulo", "título vazio")
    elif len(titulo) > 300:
        rel.aviso(arquivo, "titulo", "título com %d caracteres" % len(titulo))
    elif RE_TAG.search(titulo) or RE_ENTIDADE.search(titulo):
        rel.erro(arquivo, "titulo", "HTML cru no título")
    if isinstance(titulo, str):
        texto_suspeito(rel, arquivo, "titulo", titulo)

    data = dado.get("data")
    if not valida_data(data):
        rel.erro(arquivo, "data", "data inválida ou fora do formato AAAA-MM-DD: %r" % (data,))
    else:
        ano = int(data[:4])
        if not (2003 <= ano <= dt.date.today().year + 1):
            rel.erro(arquivo, "data", "ano fora da faixa do blog: %s" % data)

    autor = dado.get("autor")
    if not isinstance(autor, dict):
        rel.erro(arquivo, "autor", "autor precisa ser objeto")
    else:
        nome = autor.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            rel.erro(arquivo, "autor.nome", "nome do autor vazio")
        elif len(nome) > 120:
            rel.aviso(arquivo, "autor.nome", "nome com %d caracteres" % len(nome))
        url_autor = autor.get("url")
        if url_autor is not None and not url_aceita(url_autor):
            rel.erro(arquivo, "autor.url", "URL de autor inválida: %r" % (url_autor,))

    fonte = dado.get("fonte")
    if not isinstance(fonte, dict):
        rel.erro(arquivo, "fonte", "fonte precisa ser objeto")
    else:
        for campo in CAMPOS_FONTE:
            if campo not in fonte:
                rel.erro(arquivo, "fonte." + campo, "campo obrigatório ausente")
        for extra in sorted(set(fonte) - CAMPOS_FONTE - CAMPOS_FONTE_EXTRAS):
            rel.aviso(arquivo, "fonte." + extra, "campo fora do schema")
        url = fonte.get("url")
        if not isinstance(url, str) or not RE_HTTP.match(url):
            rel.erro(arquivo, "fonte.url", "URL de origem inválida: %r" % (url,))
        elif HOST_BLOG not in url:
            rel.erro(arquivo, "fonte.url", "URL fora do blog de origem: %s" % url)
        if not valida_data(fonte.get("capturado_em")):
            rel.erro(arquivo, "fonte.capturado_em", "data de captura inválida: %r" % (fonte.get("capturado_em"),))
        if fonte.get("licenca") not in LICENCAS:
            rel.erro(arquivo, "fonte.licenca", "licença fora do vocabulário (%s): %r" % ("/".join(sorted(LICENCAS)), fonte.get("licenca")))
        if not RE_HASH.match(str(fonte.get("hash_html") or "")):
            rel.erro(arquivo, "fonte.hash_html", "hash não é sha256:…")
        if not str(fonte.get("site") or "").strip():
            rel.erro(arquivo, "fonte.site", "nome do site vazio")

    resumo = dado.get("resumo")
    if resumo is not None:
        if not isinstance(resumo, str) or not resumo.strip():
            rel.erro(arquivo, "resumo", "resumo vazio")
        else:
            if len(resumo) < 40:
                rel.aviso(arquivo, "resumo", "resumo curto (%d caracteres)" % len(resumo))
            if len(resumo) > 400:
                rel.aviso(arquivo, "resumo", "resumo longo (%d caracteres)" % len(resumo))
            if RE_TAG.search(resumo):
                rel.erro(arquivo, "resumo", "HTML cru no resumo")
            texto_suspeito(rel, arquivo, "resumo", resumo)

    temas = dado.get("temas")
    if not isinstance(temas, list) or not temas:
        rel.erro(arquivo, "temas", "temas precisa ser lista com 1 a 4 itens")
    else:
        if len(temas) > 4:
            rel.erro(arquivo, "temas", "mais de 4 temas (%d)" % len(temas))
        if len(set(temas)) != len(temas):
            rel.erro(arquivo, "temas", "tema repetido")
        for tema in temas:
            if tema not in TEMAS:
                rel.erro(arquivo, "temas", "tema fora do vocabulário do plano: %r" % (tema,))

    imagens = dado.get("imagens")
    imagens_listadas: set[str] = set()
    if imagens is not None:
        if not isinstance(imagens, list):
            rel.erro(arquivo, "imagens", "imagens precisa ser lista")
        else:
            for i, imagem in enumerate(imagens):
                campo = "imagens[%d]" % i
                if not isinstance(imagem, dict):
                    rel.erro(arquivo, campo, "imagem não é objeto")
                    continue
                origem = imagem.get("origem")
                if not isinstance(origem, str) or not RE_HTTP.match(origem):
                    rel.erro(arquivo, campo + ".origem", "origem inválida: %r" % (origem,))
                else:
                    imagens_listadas.add(origem)
                if imagem.get("licenca") not in LICENCAS_IMAGEM:
                    rel.erro(arquivo, campo + ".licenca", "licença fora do vocabulário: %r" % (imagem.get("licenca"),))

    blocos = dado.get("blocos")
    tipos: list[str] = []
    if not isinstance(blocos, list) or not blocos:
        rel.erro(arquivo, "blocos", "blocos precisa ser lista com pelo menos 1 item")
    else:
        anterior = None
        for posicao, bloco in enumerate(blocos):
            tipo = valida_bloco(rel, arquivo, posicao, bloco, imagens_listadas)
            if tipo:
                tipos.append(tipo)
                rel.por_tipo[tipo] = rel.por_tipo.get(tipo, 0) + 1
            texto = (bloco.get("texto") if isinstance(bloco, dict) else None) or ""
            if texto and texto == anterior:
                rel.aviso(arquivo, "blocos[%d]" % posicao, "parágrafo repetido em sequência")
            anterior = texto or None
        if tipos and all(t in ("imagem", "video", "link") for t in tipos):
            rel.aviso(arquivo, "blocos", "post só de mídia: conferir se o texto ficou de fora")

    revisao = dado.get("revisao")
    if not isinstance(revisao, dict):
        rel.erro(arquivo, "revisao", "revisao precisa ser objeto")
    else:
        if revisao.get("estado") not in ESTADOS_REVISAO:
            rel.erro(arquivo, "revisao.estado", "estado fora de %s: %r" % ("/".join(sorted(ESTADOS_REVISAO)), revisao.get("estado")))
        if revisao.get("em") is not None and not valida_data(revisao.get("em")):
            rel.erro(arquivo, "revisao.em", "data de revisão inválida")
        if revisao.get("estado") == "aprovado" and not str(revisao.get("por") or "").strip():
            rel.erro(arquivo, "revisao.por", "aprovado sem assinatura de quem revisou")

    for tema in temas or []:
        if isinstance(tema, str):
            rel.por_tema[tema] = rel.por_tema.get(tema, 0) + 1

    return (
        identificador if isinstance(identificador, str) else None,
        slug,
        titulo if isinstance(titulo, str) else None,
        data if isinstance(data, str) else None,
    )


def valida_pasta(pasta: str) -> Relatorio:
    rel = Relatorio()
    arquivos = sorted(
        f for f in glob.glob(os.path.join(pasta, "*.json"))
        if not os.path.basename(f).startswith("_")
    )
    if not arquivos:
        rel.erro(pasta, "-", "nenhum JSON de post encontrado")
        return rel

    vistos_id: dict[str, str] = {}
    vistos_slug: dict[str, str] = {}
    vistos_titulo: dict[tuple[str, str], str] = {}

    for caminho in arquivos:
        nome = os.path.basename(caminho)
        rel.arquivos += 1
        antes_erros, antes_avisos = len(rel.erros), len(rel.avisos)
        try:
            with io.open(caminho, encoding="utf-8") as f:
                dado = json.load(f)
        except json.JSONDecodeError as erro:
            rel.erro(nome, "-", "JSON inválido: %s" % erro)
            rel.com_erro += 1
            continue
        except OSError as erro:
            rel.erro(nome, "-", "não consegui ler: %s" % erro)
            rel.com_erro += 1
            continue

        identificador, slug, titulo, data = valida_registro(rel, nome, dado)

        if identificador:
            if identificador in vistos_id:
                rel.erro(nome, "id", "id repetido (já em %s)" % vistos_id[identificador])
            else:
                vistos_id[identificador] = nome
        if slug:
            if slug in vistos_slug:
                rel.erro(nome, "slug", "slug repetido (já em %s)" % vistos_slug[slug])
            else:
                vistos_slug[slug] = nome
            if os.path.splitext(nome)[0] != slug:
                rel.erro(nome, "slug", "nome do arquivo não bate com o slug")
        if titulo and data:
            chave = (titulo.strip().lower(), data)
            if chave in vistos_titulo:
                rel.aviso(nome, "titulo", "mesmo título e data de %s: possível duplicata" % vistos_titulo[chave])
            else:
                vistos_titulo[chave] = nome

        if len(rel.erros) > antes_erros:
            rel.com_erro += 1
        elif len(rel.avisos) > antes_avisos:
            rel.com_aviso += 1
        else:
            rel.ok += 1
    return rel


def imprime(rel: Relatorio, pasta: str, maximo: int = 20, quieto: bool = False) -> None:
    print("validação do acervo: %s" % pasta)
    print("arquivos: %d | sem apontamento: %d | com erro: %d | só com aviso: %d" % (
        rel.arquivos, rel.ok, rel.com_erro, rel.com_aviso))
    print("blocos por tipo:", dict(sorted(rel.por_tipo.items(), key=lambda par: -par[1])))
    print("temas:", dict(sorted(rel.por_tema.items(), key=lambda par: -par[1])))
    print("erros: %d | avisos: %d" % (len(rel.erros), len(rel.avisos)))
    if quieto:
        return

    if rel.erros:
        print("\nanálise dos erros por campo:")
        contagem: dict[str, int] = {}
        for erro in rel.erros:
            contagem[erro["campo"]] = contagem.get(erro["campo"], 0) + 1
        for campo, total in sorted(contagem.items(), key=lambda par: -par[1]):
            print("  %-24s %d" % (campo, total))
        print("\nprimeiros %d erros:" % min(maximo, len(rel.erros)))
        for erro in rel.erros[:maximo]:
            print("  ✗ %s [%s] %s" % (erro["arquivo"], erro["campo"], erro["mensagem"]))
    if rel.avisos:
        print("\nprimeiros %d avisos:" % min(maximo, len(rel.avisos)))
        for aviso in rel.avisos[:maximo]:
            print("  ! %s [%s] %s" % (aviso["arquivo"], aviso["campo"], aviso["mensagem"]))


def main(argv: list[str] | None = None) -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="Valida os JSON do acervo contra o schema do plano.")
    ap.add_argument("pasta", nargs="?", default=PADRAO_STAGING, help="pasta com os JSON do parser")
    ap.add_argument("--json", dest="saida_json", help="grava o relatório completo em JSON")
    ap.add_argument("--maximo", type=int, default=20, help="quantos itens listar por seção")
    ap.add_argument("--quieto", action="store_true", help="só o resumo, sem listar itens")
    args = ap.parse_args(argv)

    rel = valida_pasta(args.pasta)
    imprime(rel, args.pasta, args.maximo, args.quieto)

    if args.saida_json:
        with io.open(args.saida_json, "w", encoding="utf-8") as f:
            json.dump({
                "pasta": args.pasta,
                "validado_em": dt.datetime.now().isoformat(timespec="seconds"),
                "arquivos": rel.arquivos,
                "sem_apontamento": rel.ok,
                "com_erro": rel.com_erro,
                "so_com_aviso": rel.com_aviso,
                "blocos_por_tipo": rel.por_tipo,
                "temas": rel.por_tema,
                "total_erros": len(rel.erros),
                "total_avisos": len(rel.avisos),
                "erros": rel.erros,
                "avisos": rel.avisos,
            }, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("\nrelatório gravado em: %s" % args.saida_json)

    return 1 if rel.erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
