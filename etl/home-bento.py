"""Home nova: grade interativa de fundo, bento grid das principais páginas,
título sem 'em citação direta' e referências no fim, acima do rodapé."""
import io

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
PAGINA = RAIZ + r"\index.html"

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


def ico(nome):
    return ('<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">%s</svg>'
            % ICONES[nome])


CARTÕES = [
    ("assessoria-juridica-popular.html", "Seção", "Assessoria jurídica popular", "97 textos", "balanca", ""),
    ("direitos-humanos.html", "Seção", "Direitos humanos", "76 textos", "predio", ""),
    ("movimentos-sociais.html", "Seção", "Movimentos sociais", "170 textos", "pessoas", ""),
    ("teoria-critica.html", "Seção", "Teoria crítica", "182 textos", "ideia", ""),
    ("blog.html", "Em ordem", "Blog", "713 textos em 12 anos", "jornal", "bento__item--largo"),
    ("memoria-e-cultura.html", "Seção", "Memória e cultura", "30 textos", "relogio", ""),
    ("educacao-popular.html", "Seção", "Educação popular", "158 textos", "formatura", ""),
    ("glossario.html", "Consulta", "Glossário", "18 verbetes", "dicionario", ""),
    ("linha-do-tempo.html", "Série histórica", "Linha do tempo", "2009–2024", "relogio", ""),
    ("assessoria-juridica-popular-no-mundo.html", "Pesquisa", "Direito comparado", "4 perspectivas", "colunas", ""),
    ("poemas.html", "Antologia", "Poemas", "135 poemas", "pena", ""),
]


def cartao(item, indice):
    href, etiqueta, titulo, conta, icone, classe = item
    return '''        <a class="bento__item %s" href="%s" style="--i:%d">
          <span class="bento__ico">%s</span>
          <span class="bento__etiqueta">%s</span>
          <h3 class="bento__titulo">%s</h3>
          <span class="bento__conta">%s</span>
        </a>''' % (classe, href, indice, ico(icone), etiqueta, titulo, conta)


cartoes = "\n".join(cartao(c, i + 1) for i, c in enumerate(CARTÕES))

INICIO = '''  <section class="inicio">
    <canvas class="grade-interativa" data-grade aria-hidden="true"></canvas>
    <div class="inicio__conteudo">
      <div class="porta">
        <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>Acervo</p>
        <h1 id="titulo-acervo">Assessoria Jurídica Popular</h1>
        <p class="resumo">
          Textos publicados no blog <b>Assessoria Jurídica Popular</b> desde 2009,
          com autor, data, link para o original e crédito de cada parceria.
        </p>
        <p class="resumo resumo--nota">
          <b>Em uma frase:</b> é o trabalho de advogados, estudantes e educadores
          com movimentos sociais para realizar direitos — e a porta de entrada é
          esta coleção.
        </p>
        <p class="inicio__acoes">
          <a class="botao" href="#lista-acervo">Explorar o acervo</a>
          <a class="botao secundario" href="o-que-e-assessoria-juridica-popular.html">O que é AJP</a>
        </p>
      </div>

      <div class="miolo">
        <div class="bento" data-bento>
        <a class="bento__item bento__item--grande" href="#lista-acervo" style="--i:0">
          <span class="bento__ico">%s</span>
          <span class="bento__etiqueta">Acervo completo</span>
          <b class="bento__numero">713</b>
          <span class="bento__titulo">textos em citação direta</span>
          <p>Busca por palavra-chave, tipo, ano e ordem. Cada texto com autor, data e link para o original.</p>
          <span class="bento__seta">Explorar o acervo ↓</span>
        </a>
%s
        </div>
      </div>
    </div>
  </section>

''' % (ico("livro"), cartoes)

with io.open(PAGINA, encoding="utf-8") as f:
    t = f.read()

if 'class="inicio"' in t:
    print("home ja esta no formato novo; nada a fazer")
    raise SystemExit(0)

porta = t.find('  <section class="porta"')
fita = t.find('  <section class="fita-secao"')
chips = t.find('  <nav class="chips"')
refs = t.find('  <section class="referencias"')
lista = t.find('  <section aria-labelledby="titulo-lista">')
main_end = t.find("</main>")

if min(porta, fita, chips, refs, lista, main_end) < 0:
    raise SystemExit("nao achei todos os marcadores da capa")

antes = t[:porta]
bloco_fita = t[fita:chips]
bloco_lista = t[lista:main_end]
bloco_refs = t[refs:lista]
depois = t[main_end:]

novo = antes + INICIO + bloco_fita + bloco_lista + bloco_refs + depois

with io.open(PAGINA, "w", encoding="utf-8", newline="\n") as f:
    f.write(novo)

print("home bento:", len(novo), "bytes")
print("h1 sem citacao:", "Assessoria Jurídica Popular</h1>" in novo)
