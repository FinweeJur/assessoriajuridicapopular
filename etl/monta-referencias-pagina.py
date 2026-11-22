"""Monta `referencias-citadas.html` a partir de `dados/referencias.json`.

A página é agrupada pela obra que cita, para o botão “Referências citadas”
de cada post poder apontar para `#fonte-<slug>`. Cada ficha mostra a referência
em ABNT, a confiança e o botão “Disponível aqui” quando o link foi confirmado.
"""
import html
import importlib.util
import io
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(RAIZ, "dados", "referencias.json")
LINKS = os.path.join(RAIZ, "dados", "referencias-links.json")
INDICE = os.path.join(RAIZ, "_indice.json")

spec = importlib.util.spec_from_file_location("mr", os.path.join(RAIZ, "etl", "monta-rede.py"))
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)
spec2 = importlib.util.spec_from_file_location("ab", os.path.join(RAIZ, "etl", "monta-referencias-abnt.py"))
ab = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(ab)


def esc(t):
    return html.escape(str(t or ""), quote=True)


def carrega(p, padrao):
    try:
        return json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return padrao


def main():
    dados = carrega(REF, {})
    refs = dados.get("referencias", []) if isinstance(dados, dict) else dados
    ab.aplica_sufixos(refs)
    links = carrega(LINKS, {})
    indice = {r["slug"]: r for r in carrega(INDICE, [])}

    grupos = {}
    for r in refs:
        grupos.setdefault(r.get("fonte_slug") or "sem-fonte", []).append(r)

    blocos = []
    for slug in sorted(grupos, key=lambda s: ab.sem_acento(indice.get(s, {}).get("titulo") or s)):
        refs_g = sorted(grupos[slug], key=lambda r: (ab.sem_acento(ab.autor(r)), ab.sem_acento(ab.titulo(r))))
        post = indice.get(slug, {})
        titulo = post.get("titulo") or slug
        cards = []
        for r in refs_g:
            url = (r.get("url") or "").strip()
            s = ab.status_link(url, links)
            if s == "aberto":
                acao = '<a class="botao secundario" href="%s" target="_blank" rel="noopener">Disponível aqui</a>' % esc(url)
            elif s == "emprestimo":
                acao = '<a class="botao secundario" href="%s" target="_blank" rel="noopener">Empréstimo digital</a>' % esc(url)
            elif s == "previa":
                acao = '<a class="botao secundario" href="%s" target="_blank" rel="noopener">Prévia</a>' % esc(url)
            elif s == "restrito":
                acao = '<span class="ref-status">Link restrito</span>'
            elif s == "morto_ou_instavel":
                acao = '<span class="ref-status">Link não respondeu</span>'
            else:
                acao = '<span class="ref-status">Sem link localizado</span>'
            busca = " ".join([r.get("titulo") or "", r.get("autor") or "", r.get("ano") or "", titulo])
            cards.append("""<article class="cartao ref-cit" id="ref-%s" data-fonte="%s" data-busca="%s">
  <p class="ref-cit__abnt">%s</p>
  <p class="ref-cit__fonte">Citada em <a href="%s.html">%s</a> · confiança <b>%s</b></p>
  <p class="ref-cit__acao">%s</p>
</article>""" % (
                esc(r.get("id")), esc(slug), esc(busca.lower()), ab.abnt_html(r), esc(slug), esc(titulo),
                esc(r.get("confianca") or "baixa"), acao))
        blocos.append("""<section class="secao ref-fonte" id="fonte-%s" data-fonte="%s">
  <div class="secao__cabeca"><h2><a href="%s.html">%s</a></h2><p class="secao__nota">%d %s</p></div>
  <div class="grade-3">%s</div>
</section>""" % (esc(slug), esc(slug), esc(slug), esc(titulo), len(refs_g), "referência" if len(refs_g) == 1 else "referências", "".join(cards)))

    corpo = """
<section class="hero hero--texto">
  <div class="hero__interno">
    <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Biblioteca</p>
    <h1>Referências citadas no acervo</h1>
    <p class="lead">%d referências extraídas de %d páginas. “Disponível aqui” só aparece quando o link respondeu; link restrito e link morto ficam visíveis.</p>
  </div>
</section>
<div class="miolo">
  <section class="fita-secao" aria-label="Buscar referência">
    <div class="fita">
      <label class="sr-only" for="busca-ref">Buscar referência</label>
      <input id="busca-ref" type="search" placeholder="Buscar por autor, título, ano ou post" data-ref-busca />
      <span class="fita__conta" id="conta-ref" role="status" aria-live="polite">%d referências</span>
    </div>
  </section>
  <p class="colecao__nota">Documento completo em ABNT: <a href="docs/referencias-abnt.md">docs/referencias-abnt.md</a> · por tema: <a href="docs/referencias-por-tema.md">temas</a> · por autor: <a href="docs/referencias-por-autor.md">autores</a>.</p>
  <div id="lista-refs">%s</div>
</div>
<script>
(function () {
  var campo = document.querySelector('[data-ref-busca]');
  var conta = document.getElementById('conta-ref');
  var cards = [].slice.call(document.querySelectorAll('.ref-cit'));
  var grupos = [].slice.call(document.querySelectorAll('.ref-fonte'));
  function filtra() {
    var q = (campo.value || '').toLowerCase().trim();
    var n = 0;
    cards.forEach(function (c) {
      var ok = !q || (c.dataset.busca || '').indexOf(q) > -1;
      c.hidden = !ok; if (ok) n++;
    });
    grupos.forEach(function (g) {
      g.hidden = !g.querySelector('.ref-cit:not([hidden])');
    });
    conta.textContent = n + (n === 1 ? ' referência' : ' referências');
  }
  if (campo) { campo.addEventListener('input', filtra); }
})();
</script>
""" % (len(refs), len(grupos), len(refs), "\n".join(blocos))

    texto = mr.shell("Referências citadas", "Referências citadas no acervo AJP, em ABNT, com link de acesso quando disponível.", corpo, sem_busca=True)
    io.open(os.path.join(RAIZ, "referencias-citadas.html"), "w", encoding="utf-8", newline="\n").write(texto)
    print("referencias-citadas.html", len(texto), "| refs", len(refs), "| grupos", len(grupos))


if __name__ == "__main__":
    main()
