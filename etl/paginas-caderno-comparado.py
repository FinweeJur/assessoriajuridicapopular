"""Índice do Caderno de Poesias (CMM) e página do comparado internacional."""
import importlib.util
import io
import os
import re

from pypdf import PdfReader

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

MODELO = io.open(os.path.join(RAIZ, "etl", "paginas-extras.py"), encoding="utf-8").read()


def escreve(arquivo, titulo, descricao, olho, lead, corpo, autor, data_iso, fonte_url, fonte_nome):
    modelo = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>@@TITULO@@ · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="@@DESCRICAO@@" />
  <link rel="stylesheet" href="fontes/fontshare.css?v=2" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=7" />
  <link rel="stylesheet" href="reveal.css?v=7" />
  <link rel="stylesheet" href="componentes/radio.css" />
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
@@TOPO@@
<main id="conteudo">
  <nav class="migalha" aria-label="Você está em">
    <a href="index.html">Acervo</a> <span aria-hidden="true">/</span>
    <a href="memoria-e-cultura.html">Memória e cultura</a> <span aria-hidden="true">/</span>
    <span aria-current="page">@@TITULO@@</span>
  </nav>
  <article data-revelar-grupo class="pagina">
    <header>
      <p class="olho"><span class="olho__ponto" aria-hidden="true"></span>@@OLHO@@</p>
      <h1 id="titulo">@@TITULO@@</h1>
      <p class="lead">@@LEAD@@</p>
    </header>
    @@CORPO@@
    <section class="compartilhar" data-compartilhar
             data-url="https://finweejur.github.io/assessoriajuridicapopular/@@ARQUIVO@@"
             data-titulo="@@TITULO@@" data-autor="@@AUTOR@@" data-data="@@DATA@@"
             data-fonte-url="@@FONTE_URL@@" data-fonte="@@FONTE@@">
      <h2>Compartilhar e citar</h2>
      <div class="compartilhar__botoes">
        <button type="button" data-acao="whatsapp"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 21l2.2-5.3A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8.5 10.5c.5 2 2 3.5 4 4l1.5-1.5 2 1"/></svg> WhatsApp</button>
        <button type="button" data-acao="telegram"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="m22 3-9.5 18-2-7.5L3 11l19-8Z"/><path d="m10.5 13.5 3-3"/></svg> Telegram</button>
        <button type="button" data-acao="instagram"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8"/></svg> Instagram</button>
        <button type="button" data-acao="copiar-texto"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg> Copiar texto</button>
        <button type="button" data-acao="copiar-citacao"><svg class="ico" aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16M4 12h10M4 17h7"/><path d="m17 15 3 2-3 2"/></svg> Copiar citação ABNT</button>
      </div>
      <p class="compartilhar__status" data-status role="status" aria-live="polite" data-visivel="false"></p>
    </section>
  </article>
</main>
@@RODAPE@@
<script src="compartilhar.js" defer></script>
<script src="site.js?v=2" defer></script>
<script src="reveal.js" defer></script>
<script src="componentes/radio.js" defer></script>
<script src="casca.js?v=2" defer></script>
</body>
</html>
"""
    html = modelo.replace("@@TOPO@@", ms.topo("texto")).replace("@@RODAPE@@", ms.rodape())
    html = html.replace("@@CORPO@@", corpo)
    for chave, valor in {
        "@@TITULO@@": ms.esc(titulo), "@@DESCRICAO@@": ms.esc(descricao),
        "@@OLHO@@": ms.esc(olho), "@@LEAD@@": ms.esc(lead),
        "@@ARQUIVO@@": arquivo, "@@AUTOR@@": ms.esc(autor),
        "@@DATA@@": data_iso, "@@FONTE_URL@@": ms.esc(fonte_url), "@@FONTE@@": ms.esc(fonte_nome),
    }.items():
        html = html.replace(chave, valor)
    with io.open(os.path.join(RAIZ, arquivo), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("ok:", arquivo)


# ── 1. Índice do Caderno de Poesias ────────────────────────────────────────
caminho = os.path.join(RAIZ, "fontes-textos", "Poesias e Crônicas-20261120T070851Z-1-001",
                       "Poesias e Crônicas", "CADERNO DE POESIAS - CMM.pdf")
indice = []
if os.path.exists(caminho):
    leitor = PdfReader(caminho)
    sumario = leitor.pages[0].extract_text() or ""
    # O sumário vem em pares: AUTOR e títulos com número de página.
    linhas = [l.strip() for l in sumario.splitlines() if l.strip()]
    for linha in linhas[3:]:
        if re.match(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ\s\.\(\)0-9\-]{2,}$", linha):
            indice.append(("autor", linha.title()))
        elif re.match(r"^.{2,60}\s\d{1,3}$", linha):
            indice.append(("poema", linha))

itens = []
for tipo, valor in indice[:160]:
    if tipo == "autor":
        itens.append('        <li class="poeta"><b>%s</b></li>' % ms.esc(valor))
    else:
        itens.append('        <li>%s</li>' % ms.esc(valor))

corpo = """    <p class="aviso-lote"><b>Índice, não reprodução.</b> O <i>Caderno de Poesias</i> (CMM, 2010)
    é uma coletânea com 272 páginas e dezenas de autores. Aqui ficam os nomes e os títulos, para
    orientar a leitura — o texto dos poemas continua no caderno original, pelos direitos de cada autor.</p>
    <section class="secao" aria-labelledby="sumario-caderno">
      <div class="secao__cabeca"><h2 id="sumario-caderno">Sumário</h2>
      <p class="secao__nota">Autores e títulos, na ordem do caderno</p></div>
      <ul class="indice-poetas">
%s
      </ul>
    </section>
    <section class="secao" aria-labelledby="direitos">
      <div class="secao__cabeca"><h2 id="direitos">Direitos e citação</h2></div>
      <p class="folha">MORI, Cleber (org.). <i>Caderno de Poesias</i>. 2010.</p>
      <p class="secao__nota">Para publicar um poema inteiro, é preciso autorização do autor ou do organizador.
      Trechos curtos podem ser citados com crédito, como na página de Itamar Vieira Junior.</p>
    </section>""" % "\n".join(itens)

escreve("caderno-de-poesias.html", "Caderno de Poesias: índice",
        "Índice do Caderno de Poesias (CMM, 2010): autores e títulos.",
        "Poesia · 2010",
        "Uma coletânea de 272 páginas. Aqui está o mapa: quem escreve e o que escreve.",
        corpo, "Cleber Mori (org.)", "2010-01-01", "", "Caderno de Poesias")

# ── 2. Comparado internacional (resumo das três análises) ──────────────────
corpo = """    <p class="aviso-lote"><b>Análise secundária.</b> Esta página resume três revisões de literatura
    feitas no Consensus (2026) e compara com o que dizem os textos deste acervo. Para citar em trabalho
    acadêmico, use os artigos originais — os principais estão na lista ao fim.</p>

    <section class="secao"><div class="secao__cabeca"><h2>1. No mundo: dois modelos e evidência frágil</h2></div>
      <p>A assessoria jurídica é tratada como acesso à justiça, ancorado em direitos humanos e igualdade
      perante a lei. A escala é grande: cerca de 5 bilhões de pessoas sem acesso fundamental à justiça;
      92% dos americanos de baixa renda sem assistência adequada em questões civis.</p>
      <div class="tabela cartao"><table>
        <caption>Modelos de prestação</caption>
        <thead><tr><th>Modelo</th><th>Prestador</th><th>Financiamento</th><th>Público</th></tr></thead>
        <tbody>
          <tr><td>Estatal</td><td>NALSA e defensorias</td><td>Orçamento público</td><td>Sem recursos</td></tr>
          <tr><td>ONG</td><td>LBH, clínicas, voluntários</td><td>Voluntário</td><td>Pobres, refugiados, minorias</td></tr>
          <tr><td>Pro bono</td><td>Advogados e escritórios</td><td>Não remunerado</td><td>Litigantes carentes</td></tr>
          <tr><td>Defensoria (EUA)</td><td>Defensores públicos</td><td>Público</td><td>Réus criminais</td></tr>
        </tbody></table></div>
      <p>Evidência mista: avaliação randomizada em seguro-desemprego não achou efeito na vitória, mas
      atrasou processos em duas semanas; programas de <i>right to counsel</i> em Nova York contiveram
      despejos. Barreiras: falta de informação, financiamento curto, distância e burocracia.</p>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>2. No Brasil: Constituição forte, cobertura curta</h2></div>
      <p>A Constituição de 1988 constitucionalizou a assistência integral e gratuita; a Emenda 45/2004
      deu autonomia à Defensoria. A expansão não acompanhou a demanda.</p>
      <div class="tabela cartao"><table>
        <caption>Capacidade e limites</caption>
        <thead><tr><th>Dimensão</th><th>Achado</th></tr></thead>
        <tbody>
          <tr><td>Cobertura</td><td>Defensores crescem abaixo da população-alvo</td></tr>
          <tr><td>Déficit</td><td>Falta de cobertura limita o papel de ombudsman</td></tr>
          <tr><td>IDH</td><td>Maior IDH, maior litigiosidade</td></tr>
          <tr><td>Tutela coletiva</td><td>ACPs ampliaram direitos, com cautela do Judiciário</td></tr>
        </tbody></table></div>
      <p>A advocacia popular rompeu com o modelo individualista; a RENAP articula advogados, professores,
      estudantes e defensores há três décadas, com 18 estados no encontro de 2024. As AJUP formam
      estudantes mais sensíveis às lutas sociais.</p>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>3. América Latina: ecologia plural, autonomia desigual</h2></div>
      <p>A região adotou Defensorias Públicas, mas a mesma nomenclatura esconde instituições distintas.
      Serviços jurídicos alternativos nasceram nos anos 1970-80, contra ditaduras, e cruzaram com a
      práxis dos advogados populares brasileiros.</p>
      <div class="tabela cartao"><table>
        <caption>Panorama regional</caption>
        <thead><tr><th>Dimensão</th><th>Achado</th></tr></thead>
        <tbody>
          <tr><td>Autonomia</td><td>16 Defensorias com níveis desiguais</td></tr>
          <tr><td>Modelo</td><td>Sem padrão; advocacia dativa coexiste</td></tr>
          <tr><td>Demanda</td><td>Assistência pública é a 4ª opção buscada</td></tr>
          <tr><td>Barreiras</td><td>Raça, território, deficiência e desinformação</td></tr>
        </tbody></table></div>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>O que isso muda para o acervo</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">🧭</span><b>Definição:</b> a literatura confirma o texto de 2009 — assessoria é acesso à justiça, não caridade.</li>
        <li><span class="emoji" aria-hidden="true">🏛️</span><b>Modelo:</b> o Brasil tem o arranjo mais institucionalizado da região, com déficit de cobertura.</li>
        <li><span class="emoji" aria-hidden="true">📊</span><b>Evidência:</b> falta medir resultado; relatos de caso e séries históricas ajudam.</li>
        <li><span class="emoji" aria-hidden="true">🌎</span><b>Comparação:</b> o pluralismo jurídico latino-americano dialoga com o direito insurgente do acervo.</li>
      </ul>
    </section>

    <section class="secao"><div class="secao__cabeca"><h2>Referências principais</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://doi.org/10.1108/ijpsm-09-2020-0241" target="_blank" rel="noopener">Buta (2021) — autonomia das Defensorias na América Latina</a></li>
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://doi.org/10.12957/dep.2015.15409" target="_blank" rel="noopener">Carlet (2015) — advocacia popular no Brasil</a></li>
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://doi.org/10.1257/rct.1677" target="_blank" rel="noopener">Greiner et al. (2017) — avaliação randomizada em assistência jurídica</a></li>
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://doi.org/10.26512/revistainsurgncia.v11i2.58335" target="_blank" rel="noopener">Maldonado et al. (2025) — RENAP, 30 anos</a></li>
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://doi.org/10.26512/revistainsurgncia.v11i2.59635" target="_blank" rel="noopener">Ordóñez Gómez (2025) — advocacia popular na América Latina</a></li>
        <li><span class="emoji" aria-hidden="true">📄</span><a href="https://doi.org/10.24305/cadecs.v4i2.2016.17344" target="_blank" rel="noopener">Pazello (2017) — práxis da assessoria jurídica popular</a></li>
      </ul>
    </section>"""

escreve("assessoria-juridica-popular-no-mundo.html",
        "Assessoria jurídica popular no mundo: três leituras",
        "Comparação entre mundo, Brasil e América Latina na literatura sobre assistência jurídica gratuita.",
        "Pesquisa · comparação",
        "O que a literatura diz sobre assessoria jurídica popular, o que o Brasil tem de diferente e o que falta na América Latina.",
        corpo, "Acervo AJP", "2026-11-20", "https://consensus.app/", "Consensus")
