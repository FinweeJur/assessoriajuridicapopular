"""Monta as páginas do acervo a partir do JSON do parser.

Entrada:  G:\\Meu Drive\\RENAP-AJP\\staging\\*.json  (um post por arquivo)
Modelo:   _modelo.html
Saída:    <slug>.html na raiz do projeto e _indice.json

Regras (plano, seções 6 e 11):
  - citação direta, sem reescrever;
  - bloco de destaque sai do corpo (não repete);
  - imagem sem licença entra como link, não como arquivo;
  - cada página mostra autor, data, fonte e data de captura.

Uso:
  python etl/monta-paginas.py
  python etl/monta-paginas.py --limite 20
"""
import argparse
import glob
import html
import io
import json
import os
import re
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.path.join(RAIZ, "_modelo.html")
STAGING = r"G:\Meu Drive\RENAP-AJP\staging"

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

TEMAS_LEGIVEIS = {
    "assessoria-juridica-popular": "Assessoria jurídica popular",
    "educacao-popular": "Educação popular",
    "movimentos-sociais": "Movimentos sociais",
    "direitos-humanos": "Direitos humanos",
    "memoria": "Memória",
    "teoria-critica": "Teoria crítica",
}


def esc(t):
    return html.escape(t or "", quote=False)


def data_legivel(iso):
    if not iso or len(iso) < 10:
        return ""
    ano, mes, dia = iso[:10].split("-")
    return "%d de %s de %s" % (int(dia), MESES[int(mes) - 1], ano)


def slug_de(texto):
    sem = unicodedata.normalize("NFD", texto or "")
    sem = "".join(c for c in sem if unicodedata.category(c) != "Mn")
    sem = re.sub(r"[^a-zA-Z0-9]+", "-", sem).strip("-").lower()
    return sem[:60] or "texto"


def bloco_para_html(b):
    tipo = b.get("tipo")
    if tipo == "paragrafo":
        return "<p>%s</p>" % esc(b.get("texto"))
    if tipo == "titulo":
        nivel = 3 if str(b.get("nivel")) == "3" else 2
        return "<h%d>%s</h%d>" % (nivel, esc(b.get("texto")), nivel)
    if tipo == "citacao":
        return "<blockquote><p>%s</p></blockquote>" % esc(b.get("texto"))
    if tipo == "lista":
        tag = "ol" if b.get("ordenada") else "ul"
        itens = "".join("<li>%s</li>" % esc(i) for i in b.get("itens", []))
        return "<%s>%s</%s>" % (tag, itens, tag)
    if tipo == "imagem":
        src = b.get("href") or b.get("src")
        legenda = b.get("legenda") or b.get("alt")
        if b.get("licenca") == "link" or not b.get("credito"):
            # Reprodução com aviso: sem crédito declarado, o titular pede retirada.
            return ('<figure class="reproducao"><img src="%s" alt="%s" loading="lazy" />'
                    '<figcaption>%s<span class="reproducao__aviso">Imagem sem crédito declarado no original. '
                    'Se você é titular e quer a retirada, escreva para '
                    '<a href="mailto:artur.colito@ufvjm.edu.br">artur.colito@ufvjm.edu.br</a>.</span>'
                    '</figcaption></figure>'
                    % (esc(src), esc(b.get("alt") or legenda or "Imagem do texto"),
                       (esc(legenda) + " — ") if legenda else ""))
        return ('<figure><img src="%s" alt="%s" loading="lazy" />'
                '<figcaption>%s%s</figcaption></figure>'
                % (esc(src), esc(b.get("alt") or legenda), esc(legenda),
                   (" · " + esc(b.get("credito"))) if b.get("credito") else ""))
    if tipo == "link":
        return '<p><a href="%s" target="_blank" rel="noopener">%s</a></p>' % (
            esc(b.get("url")), esc(b.get("texto") or b.get("url")))
    if tipo == "video":
        return ('<p class="video"><a href="%s" target="_blank" rel="noopener">'
                'Ver o vídeo no original<span class="sr-only"> (abre em outra aba)</span></a></p>'
                % esc(b.get("url")))
    return ""


SECOES = {
    "assessoria-juridica-popular": ("assessoria-juridica-popular", "Assessoria jurídica popular"),
    "direitos-humanos": ("direitos-humanos", "Direitos humanos"),
    "movimentos-sociais": ("movimentos-sociais", "Movimentos sociais"),
    "memoria": ("memoria-e-cultura", "Memória e cultura"),
    "teoria-critica": ("teoria-critica", "Teoria crítica do direito"),
    "educacao-popular": ("educacao-popular", "Educação popular"),
}


def slug_autor(nome):
    sem = unicodedata.normalize("NFD", nome or "")
    sem = "".join(c for c in sem if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-zA-Z0-9]+", "-", sem).strip("-").lower()[:60] or "redacao"


def carrega_indice():
    try:
        with io.open(os.path.join(RAIZ, "_indice.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def liga_paginas(post, indice):
    """Migalha, link do autor e 'Leia também'."""
    temas = post.get("temas") or ["assessoria-juridica-popular"]
    secao = SECOES.get(temas[0], SECOES["assessoria-juridica-popular"])
    autor = (post.get("autor") or {}).get("nome") or "Redação do blog"
    titulo = esc(post.get("titulo"))

    migalha = ('<nav class="migalha" aria-label="Você está em">'
               '<a href="index.html">Acervo</a> <span aria-hidden="true">/</span> '
               '<a href="%s.html">%s</a> <span aria-hidden="true">/</span> '
               '<span aria-current="page">%s</span></nav>'
               % (secao[0], secao[1], titulo))

    autor_link = ('<p class="autor-link">Todos os textos de '
                  '<a href="autor-%s.html">%s</a></p>' % (slug_autor(autor), esc(autor)))

    ano = (post.get("data") or "")[:4]
    pontuados = []
    for outro in indice:
        if outro.get("slug") == post.get("slug"):
            continue
        nota = 3 if set(outro.get("temas") or []) & set(post.get("temas") or []) else 0
        nota += 2 if (outro.get("autor") or "") == autor else 0
        nota += 1 if (outro.get("data") or "")[:4] == ano else 0
        if nota:
            pontuados.append((nota, outro))
    pontuados.sort(key=lambda x: (-x[0], x[1].get("data") or ""))
    escolhidos = [o for _, o in pontuados[:6]]

    relacionados = ""
    if escolhidos:
        cartoes = "\n".join(
            '<li class="item"><a class="item__link" href="%s.html">'
            '<span class="etiqueta">%s · %s</span><h3>%s</h3>'
            '<span class="item__ficha">%s</span></a></li>'
            % (esc(r["slug"]), esc(r.get("tema")), esc(r.get("ano")),
               esc(r.get("titulo")), esc(r.get("autor")))
            for r in escolhidos)
        relacionados = ('<section class="secao relacionados" aria-labelledby="relacionados">'
                        '<div class="secao__cabeca"><h2 id="relacionados">Leia também</h2>'
                        '<p class="secao__nota">Mesmo tema, mesmo autor ou mesmo ano</p></div>'
                        '<ul class="lista-acervo" data-revelar-grupo>%s</ul></section>' % cartoes)

    return migalha, autor_link, relacionados


def monta(post, modelo, indice=None):
    blocos = post.get("blocos", [])
    destaque = ""
    indice_destaque = -1
    for i, b in enumerate(blocos):
        if b.get("tipo") == "paragrafo":
            texto = b.get("texto") or ""
            if len(texto) > len(destaque) and len(texto) >= 160:
                destaque, indice_destaque = texto, i
    if not destaque:
        for b in blocos:
            if b.get("tipo") == "paragrafo":
                destaque = b.get("texto") or ""
                break

    corpo = [bloco_para_html(b) for i, b in enumerate(blocos) if i != indice_destaque]
    fonte = post.get("fonte", {})
    autor = post.get("autor", {}) or {}
    temas = post.get("temas") or []
    tema = TEMAS_LEGIVEIS.get(temas[0], "Assessoria jurídica popular") if temas else "Assessoria jurídica popular"
    data = post.get("data", "")

    valores = {
        "TITULO": esc(post.get("titulo")),
        "DATA": data_legivel(data),
        "DATA_ISO": data[:10],
        "AUTOR": esc(autor.get("nome") or "Redação do blog"),
        "AUTOR_URL": esc(autor.get("url") or "https://assessoriajuridicapopular.blogspot.com/"),
        "FONTE_URL": esc(fonte.get("url")),
        "CAPTURA": data_legivel(fonte.get("capturado_em", "")) or "20 de novembro de 2026",
        "CAPTURA_ISO": (fonte.get("capturado_em") or "2026-11-20")[:10],
        "ANO": (data or "")[:4],
        "TEMA": esc(tema),
        "RESUMO": esc(post.get("resumo") or destaque[:180]),
        "DESTAQUE": esc(destaque),
        "TEXTO": "\n      ".join(corpo),
        "SITE_URL": "https://finweejur.github.io/assessoriajuridicapopular/" + (post.get("slug") or slug_de(post.get("titulo"))) + ".html",
    }

    migalha, autor_link, relacionados = liga_paginas(post, indice or [])
    valores["MIGALHA"] = migalha
    valores["AUTOR_LINK"] = autor_link
    valores["RELACIONADOS"] = relacionados

    saida = modelo
    for chave, valor in valores.items():
        saida = saida.replace("{{%s}}" % chave, valor)
    return saida, valores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonte", default=STAGING)
    ap.add_argument("--limite", type=int, default=0)
    args = ap.parse_args()

    modelo = io.open(MODELO, encoding="utf-8").read()
    arquivos = [a for a in sorted(glob.glob(os.path.join(args.fonte, "*.json")))
                if not os.path.basename(a).startswith("_")]
    if args.limite:
        arquivos = arquivos[: args.limite]

    indice_ref = carrega_indice()
    indice = []
    for caminho in arquivos:
        post = json.loads(io.open(caminho, encoding="utf-8").read())
        slug = post.get("slug") or slug_de(post.get("titulo"))
        pagina, valores = monta(post, modelo, indice_ref)
        destino = os.path.join(RAIZ, slug + ".html")
        with io.open(destino, "w", encoding="utf-8", newline="\n") as f:
            f.write(pagina)
        indice.append({
            "slug": slug,
            "titulo": post.get("titulo"),
            "data": post.get("data"),
            "autor": valores["AUTOR"],
            "resumo": post.get("resumo") or "",
            "temas": post.get("temas") or [],
            "tema": valores["TEMA"],
            "ano": valores["ANO"],
        })

    indice.sort(key=lambda i: i.get("data") or "", reverse=True)
    with io.open(os.path.join(RAIZ, "_indice.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(indice, f, ensure_ascii=False, indent=1)

    print("páginas:", len(indice))
    return indice


if __name__ == "__main__":
    main()
