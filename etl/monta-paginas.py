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
            rotulo = esc(legenda) if legenda else "Ver a imagem no original"
            return ('<figure class="cartao imagem-link"><a href="%s" target="_blank" rel="noopener">'
                    '%s<span class="sr-only"> (abre em outra aba)</span></a>'
                    '<figcaption>Imagem do original, sem licença declarada.</figcaption></figure>'
                    % (esc(src), rotulo))
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


def monta(post, modelo):
    blocos = post.get("blocos", [])
    # Destaque: o parágrafo mais longo acima de 160 caracteres.
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
    }

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

    indice = []
    for caminho in arquivos:
        post = json.loads(io.open(caminho, encoding="utf-8").read())
        slug = post.get("slug") or slug_de(post.get("titulo"))
        pagina, valores = monta(post, modelo)
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
