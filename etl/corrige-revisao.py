"""Atende a revisão: comparado sem duplicata, mística resumida, caderno só índice,
citações corrigidas e medida de leitura."""
import importlib.util
import io
import os
import re

from pypdf import PdfReader

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

TOPO = ms.topo("texto")
RODAPE = ms.rodape()
BASE = "https://finweejur.github.io/assessoriajuridicapopular"


def template(titulo, olho, lead, corpo, arquivo, autor="Acervo AJP", data="2026-11-20", fonte_url="", fonte="Acervo AJP"):
    return ("""<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>%s · AJP — Assessoria Jurídica Popular</title>
  <link rel="stylesheet" href="fontes/fontshare.css?v=2" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=9" />
  <link rel="stylesheet" href="reveal.css?v=9" />
  <link rel="stylesheet" href="componentes/radio.css" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
%s
<main id="conteudo">
  <nav class="migalha" aria-label="Você está em">
    <a href="index.html">Acervo</a> <span aria-hidden="true">/</span>
    <a href="memoria-e-cultura.html">Memória e cultura</a> <span aria-hidden="true">/</span>
    <span aria-current="page">%s</span>
  </nav>
  <article data-revelar-grupo class="pagina">
    <header>
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>%s</p>
      <h1 id="titulo">%s</h1>
      <p class="lead">%s</p>
    </header>
    %s
    <section class="compartilhar" data-compartilhar
             data-url="%s/%s" data-titulo="%s" data-autor="%s" data-data="%s"
             data-fonte-url="%s" data-fonte="%s"
             data-citacao="%s">
      <h2>Compartilhar e citar</h2>
      <div class="compartilhar__botoes">
        <button type="button" data-acao="whatsapp">WhatsApp</button>
        <button type="button" data-acao="telegram">Telegram</button>
        <button type="button" data-acao="instagram">Instagram</button>
        <button type="button" data-acao="copiar-texto">Copiar texto</button>
        <button type="button" data-acao="copiar-citacao">Copiar citação ABNT</button>
      </div>
      <p class="compartilhar__status" data-status role="status" aria-live="polite" data-visivel="false"></p>
    </section>
  </article>
</main>
%s
<script src="compartilhar.js" defer></script>
<script src="casca.js?v=2" defer></script>
<script src="site.js?v=2" defer></script>
<script src="reveal.js" defer></script>
<script src="componentes/radio.js" defer></script>
</body>
</html>
""" % (ms.esc(titulo), TOPO, ms.esc(titulo), ms.esc(olho), ms.esc(titulo), ms.esc(lead), corpo,
       BASE, arquivo, ms.esc(titulo), ms.esc(autor), data, ms.esc(fonte_url), ms.esc(fonte),
       ms.esc(autor + ". " + titulo + ". " + fonte + ", 2026. Disponível em: " + BASE + "/" + arquivo +
              ". Acesso em: 20 nov. 2026."), RODAPE))


# ── 1. Comparado: Brasil → América Latina → mundo ─────────────────────────
CORPO = """    <p class="aviso-lote"><b>Levantamento exploratório</b>, não revisão sistemática: três consultas
    ao Consensus em novembro de 2026, com os artigos conferidos no Crossref. Para citar em trabalho
    acadêmico, use os originais listados ao fim.</p>

    <section class="secao"><div class="secao__cabeca"><h2>1. No Brasil: Constituição forte, cobertura curta</h2></div>
      <p>A Constituição de 1988 garantiu assistência jurídica integral e gratuita; a Emenda 45/2004 deu
      autonomia à Defensoria. A expansão não acompanhou a demanda: defensores crescem abaixo da
      população-alvo de até três salários mínimos (DE SOUZA, 2020).</p>
      <div class="tabela cartao"><table>
        <caption>Capacidade e limites da Defensoria Pública</caption>
        <thead><tr><th scope="col">Dimensão</th><th scope="col">Achado</th><th scope="col">Fonte</th></tr></thead>
        <tbody>
          <tr><td>Cobertura</td><td>Defensores abaixo do crescimento da população-alvo</td><td>De Souza (2020)</td></tr>
          <tr><td>Déficit</td><td>Falta de cobertura limita o papel de ombudsman</td><td>Madureira; De Lima (2024)</td></tr>
          <tr><td>IDH</td><td>Estados de maior IDH têm maior litigiosidade</td><td>De Souza (2020)</td></tr>
          <tr><td>Tutela coletiva</td><td>Ações civis públicas ampliaram direitos coletivos</td><td>Souza (2020)</td></tr>
        </tbody></table></div>
      <p>A advocacia popular rompeu com o modelo individualista (CARLET, 2015). A RENAP articula a rede
      desde 1995; o encontro de 2024 reuniu 18 das 27 unidades federativas (MALDONADO BRAVO; CARNEIRO;
      MOTA, 2025). As AJUP formam estudantes mais sensíveis às lutas sociais (DE SOUSA et al., 2019).</p>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>2. América Latina: ecologia plural, autonomia desigual</h2></div>
      <p>A região adotou Defensorias Públicas, mas a mesma nomenclatura esconde instituições distintas
      em escopo e prerrogativas (BUTA, 2021; DE JESUS; DE JESUS, 2023). Serviços jurídicos alternativos
      nasceram nos anos 1970-80, contra ditaduras (ORDÓÑEZ GÓMEZ, 2025).</p>
      <div class="tabela cartao"><table>
        <caption>Panorama regional</caption>
        <thead><tr><th scope="col">Dimensão</th><th scope="col">Achado</th><th scope="col">Fonte</th></tr></thead>
        <tbody>
          <tr><td>Autonomia</td><td>16 defensorias de países latino-americanos, com níveis desiguais</td><td>Buta (2021)</td></tr>
          <tr><td>Modelo</td><td>Sem padrão único; advocacia dativa coexiste</td><td>Dani (2025)</td></tr>
          <tr><td>Tutela coletiva</td><td>Depende de instituições fortes, como a Defensoria brasileira</td><td>Dani (2025)</td></tr>
          <tr><td>Barreiras</td><td>Raça, território, deficiência e desinformação</td><td>Mina-Bone; Vargas-Fonseca (2024)</td></tr>
        </tbody></table></div>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>3. No mundo: dois modelos e evidência frágil</h2></div>
      <p>A escala é grande: <b>5,1 bilhões</b> de pessoas sem acesso efetivo à justiça (TASK FORCE ON
      JUSTICE, 2019). Nos EUA, <b>92% dos problemas jurídicos civis</b> de pessoas de baixa renda recebem
      ajuda nenhuma ou insuficiente (LSC, 2022) — o percentual é de problemas, não de pessoas.</p>
      <div class="tabela cartao"><table>
        <caption>Modelos de prestação</caption>
        <thead><tr><th scope="col">Modelo</th><th scope="col">Prestador</th><th scope="col">Financiamento</th></tr></thead>
        <tbody>
          <tr><td>Estatal</td><td>NALSA e defensorias</td><td>Orçamento público</td></tr>
          <tr><td>ONG</td><td>LBH, clínicas, voluntários</td><td>Voluntário</td></tr>
          <tr><td>Pro bono</td><td>Advogados e escritórios</td><td>Não remunerado</td></tr>
        </tbody></table></div>
      <p>A evidência de efeito é mista: avaliação randomizada em seguro-desemprego não achou efeito na
      vitória, mas atrasou processos em duas semanas (GREINER; WELCH; GERAY, 2017).</p>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>O que isso muda para o acervo</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">🧭</span><b>Definição:</b> a literatura confirma o texto de 2009 — assessoria é acesso à justiça, não caridade.</li>
        <li><span class="emoji" aria-hidden="true">🏛️</span><b>Modelo:</b> o Brasil tem o arranjo mais institucionalizado da região, com déficit de cobertura.</li>
        <li><span class="emoji" aria-hidden="true">📊</span><b>Evidência:</b> falta medir resultado; relatos de caso e séries históricas ajudam.</li>
      </ul>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>Referências</h2></div>
      <ul class="linhas refs-doi">
        <li><span class="emoji" aria-hidden="true">📄</span>BUTA, Bernardo Oliveira. The autonomy of public defender’s offices. <i>International Journal of Public Sector Management</i>, v. 34, n. 5, p. 586-601, 2021. DOI: <a href="https://doi.org/10.1108/IJPSM-09-2020-0241" target="_blank" rel="noopener">10.1108/IJPSM-09-2020-0241</a>.</li>
        <li><span class="emoji" aria-hidden="true">📄</span>CARLET, Flávia. Advocacia popular. <i>Revista Direito e Práxis</i>, v. 6, n. 10, 2015. DOI: <a href="https://doi.org/10.12957/dep.2015.15409" target="_blank" rel="noopener">10.12957/dep.2015.15409</a>.</li>
        <li><span class="emoji" aria-hidden="true">📄</span>GREINER, D. James; WELCH, Keesler; GERAY, Jacob. Randomized evaluation in legal assistance. <i>AEA Randomized Controlled Trials</i>, 2017. DOI: <a href="https://doi.org/10.1257/rct.1677" target="_blank" rel="noopener">10.1257/rct.1677</a>.</li>
        <li><span class="emoji" aria-hidden="true">📄</span>MALDONADO BRAVO, Efendy Emiliano; CARNEIRO, Maria do Rosário de Oliveira; MOTA, Maria Solara Pontes. RENAP: 30 anos. <i>InSURgência</i>, v. 11, n. 2, p. 491-505, 2025. DOI: <a href="https://doi.org/10.26512/revistainsurgncia.v11i2.58335" target="_blank" rel="noopener">10.26512/revistainsurgncia.v11i2.58335</a>.</li>
        <li><span class="emoji" aria-hidden="true">📄</span>ORDÓÑEZ GÓMEZ, Freddy. Serviços jurídicos alternativos e advocacia popular na América Latina. <i>InSURgência</i>, v. 11, n. 2, p. 133-170, 2025. DOI: <a href="https://doi.org/10.26512/revistainsurgncia.v11i2.59635" target="_blank" rel="noopener">10.26512/revistainsurgncia.v11i2.59635</a>.</li>
        <li><span class="emoji" aria-hidden="true">📄</span>PAZELLO, Ricardo Prestes. A práxis da assessoria jurídica popular. <i>Caderno Eletrônico de Ciências Sociais</i>, v. 4, n. 2, p. 94-117, 2017. DOI: <a href="https://doi.org/10.24305/cadecs.v4i2.2016.17344" target="_blank" rel="noopener">10.24305/cadecs.v4i2.2016.17344</a>.</li>
      </ul>
    </section>"""

with io.open(os.path.join(RAIZ, "assessoria-juridica-popular-no-mundo.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(template("Assessoria jurídica popular: Brasil, América Latina e mundo",
                     "Pesquisa · comparação",
                     "O que a literatura diz sobre assessoria jurídica popular, começando pelo Brasil, "
                     "passando pela América Latina e chegando ao debate internacional.",
                     CORPO, "assessoria-juridica-popular-no-mundo.html"))
print("comparado: Brasil → América Latina → mundo")

# ── 2. Mística: resumo + 3 excertos ───────────────────────────────────────
t = io.open(os.path.join(RAIZ, "fontes-textos", "mistica.txt"), encoding="utf-8").read().lstrip("\ufeff")
paragrafos = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]
corpo_mistica = paragrafos[3:6] if len(paragrafos) > 6 else paragrafos[1:4]
excertos = "\n".join(
    '      <blockquote><p>%s</p></blockquote>' % ms.esc(p) for p in corpo_mistica)

CORPO = """    <p class="aviso-lote"><b>Resumo e excertos.</b> O texto completo está no documento original,
    linkado abaixo. Aqui ficam a ideia central e três passagens, com crédito.</p>

    <section class="secao"><div class="secao__cabeca"><h2>O que o texto diz</h2></div>
      <p>Mística não é enfeite de abertura de encontro: é a energia que sustenta a luta no dia a dia.
      O texto foi escrito por militantes de movimentos populares para a equipe de mística do 3º
      Acampamento Estadual do Levante Popular da Juventude, na UFJF, em 2023.</p>
      <div class="cartao citacao">%s</div>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>Do texto de Ademar Bogo</h2></div>
      <p>“A mística é muito mais. Ela é a motivação que nos faz viver a causa até o fim. É aquela
      energia que temos e que não nos deixa dizer não, quando nos solicitam ajuda.”</p>
      <p class="secao__nota"><b>Ademar Bogo</b>, em “A mística: parte da vida e da luta”,
      <a href="https://docs.google.com/document/d/1RMnMFcnBsUKNji-1z7j1jH9dNulNUSkG/edit" target="_blank" rel="noopener">documento original</a>.</p>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>Fonte</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://docs.google.com/document/d/1hxF-AgZYoka9yU0PLZ0MDCqWvpGq0UFnthlDXSP1W_w/edit" target="_blank" rel="noopener">Mística: acúmulos, aprendizados, saberes e apontamentos iniciais</a> (2023).</li>
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://docs.google.com/document/d/1RMnMFcnBsUKNji-1z7j1jH9dNulNUSkG/edit" target="_blank" rel="noopener">A mística: parte da vida e da luta</a>, de Ademar Bogo.</li>
      </ul>
    </section>""" % excertos

with io.open(os.path.join(RAIZ, "mistica.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(template("Mística: o que sustenta a luta", "Mística · 2023",
                     "Resumo e três passagens do texto dos movimentos populares, com citação de Ademar Bogo.",
                     CORPO, "mistica.html", autor="Militantes dos movimentos populares",
                     data="2023-01-01", fonte="Levante Popular da Juventude"))
print("mística: resumo + 3 excertos")

# ── 3. Caderno: só índice ─────────────────────────────────────────────────
caminho = os.path.join(RAIZ, "fontes-textos", "Poesias e Crônicas-20261120T070851Z-1-001",
                       "Poesias e Crônicas", "CADERNO DE POESIAS - CMM.pdf")
itens = []
if os.path.exists(caminho):
    leitor = PdfReader(caminho)
    sumario = leitor.pages[0].extract_text() or ""
    linhas = [l.strip() for l in sumario.splitlines() if l.strip()]
    for linha in linhas[3:120]:
        if re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ\s\.\(\)0-9\-]{2,}$", linha):
            itens.append('<li class="poeta"><b>%s</b></li>' % ms.esc(linha.title()))
        elif re.match(r"^.{2,60}\s\d{1,3}$", linha):
            itens.append("<li>%s</li>" % ms.esc(linha))

CORPO = """    <p class="aviso-lote"><b>Índice, não reprodução.</b> A Coletânea de Poesias (CMM, 2010) tem
    272 páginas e dezenas de autores com direitos próprios. Aqui ficam os nomes e os títulos; o texto
    dos poemas continua no caderno original. Pedidos de retirada: artur.colito@ufvjm.edu.br.</p>
    <section class="secao"><div class="secao__cabeca"><h2>Sumário</h2>
    <p class="secao__nota">Autores e títulos, na ordem do caderno</p></div>
    <ul class="indice-poetas">%s</ul></section>
    <section class="secao"><div class="secao__cabeca"><h2>Referência</h2></div>
      <p class="folha">MORI, Cleber (org.). <i>Coletânea de poesias</i>. [S. l.: s. n.], out. 2010. 272 p.</p>
    </section>""" % "\n".join(itens)

with io.open(os.path.join(RAIZ, "caderno-de-poesias.html"), "w", encoding="utf-8", newline="\n") as f:
    f.write(template("Caderno de Poesias: índice", "Poesia · 2010",
                     "O mapa da coletânea de 272 páginas: quem escreve e o que escreve.",
                     CORPO, "caderno-de-poesias.html", autor="Cleber Mori (org.)", data="2010-10-01",
                     fonte="Coletânea de poesias"))
print("caderno: índice")

# ── 4. Citações: Gama e Brecht ────────────────────────────────────────────
p = os.path.join(RAIZ, "citacoes.html")
t = io.open(p, encoding="utf-8").read()
t = re.sub(r'<figcaption><b>Luís Gama</b>\.\s*, 1830\.\s*Advogado, jornalista e abolicionista \(1830–1882\)\.</figcaption>',
           '<figcaption><b>Luís Gama</b> (1830–1882). Frase atribuída; fonte primária não localizada.</figcaption>', t)
t = t.replace("<b>Bertolt Brecht</b>. Poeta e dramaturgo alemão (1898–1956).",
              "<b>Bertolt Brecht</b> (1898–1956). Frase atribuída; edição não localizada.")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("citações: Gama e Brecht marcados")

# ── 5. Medida de leitura e tabelas ────────────────────────────────────────
css_path = os.path.join(RAIZ, "acervo.css")
css = io.open(css_path, encoding="utf-8").read()
extra = """
/* Medida de leitura: nada de linha com 120ch */
.citacao blockquote p, .aviso-lote, .linhas li, .corpo p { max-width: 65ch; }
.tabela table { min-width: 0; }
.tabela table:has(th:nth-child(3)) { min-width: 30rem; }
"""
if "Medida de leitura" not in css:
    io.open(css_path, "w", encoding="utf-8", newline="\n").write(css.rstrip() + "\n" + extra)
print("css: medida 65ch")
