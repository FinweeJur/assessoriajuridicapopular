"""Seção 'Direito crítico popular' na página do comparado.

Compara as quatro perspectivas pedidas: assessoria jurídica popular,
direito insurgente, direito achado na rua e uso tático do direito.
Roda quantas vezes quiser: substitui a seção inteira pelo id.
"""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
PAGINA = os.path.join(RAIZ, "assessoria-juridica-popular-no-mundo.html")

SECAO = '''    <section class="secao" id="direito-critico"><div class="secao__cabeca">
      <h2>1. Direito crítico popular: quatro perspectivas</h2>
      <p class="secao__nota">AJP, direito insurgente, direito achado na rua e uso tático — o que cada um responde</p></div>
      <p>As quatro perspectivas não são sinônimos. Cada uma responde a uma pergunta diferente:
      <b>como fazer</b> (AJP), <b>de onde vem o direito</b> (achado na rua), <b>a que preço se usa o
      direito do Estado</b> (insurgente) e <b>quando vale entrar no Judiciário</b> (uso tático).</p>

      <div class="tabela cartao">
        <table class="tabela--cinco">
          <caption>Os quatro conceitos em perspectiva</caption>
          <thead><tr>
            <th scope="col">Dimensão</th>
            <th scope="col">AJP</th>
            <th scope="col">Direito insurgente</th>
            <th scope="col">Direito achado na rua</th>
            <th scope="col">Uso tático</th>
          </tr></thead>
          <tbody>
            <tr><th scope="row">Natureza</th><td>Prática política e pedagógica</td><td>Teoria crítica marxista</td><td>Escola teórica pluralista</td><td>Conceito estratégico</td></tr>
            <tr><th scope="row">Origem</th><td>Brasil, anos 1960 — FASE, AJUP, RENAP</td><td>Brasil, anos 1980–90 — AJUP/FASE, Pressburger</td><td>UnB, anos 1980 — Lyra Filho, NELJB</td><td>Sociologia jurídica e <i>cause lawyering</i></td></tr>
            <tr><th scope="row">Base</th><td>Paulo Freire, educação popular</td><td>Marxismo, Pachukanis, crítica descolonial</td><td>Pluralismo jurídico, humanismo</td><td>Lênin, advocacia de causa</td></tr>
            <tr><th scope="row">Relação com o direito</th><td>Disputa e questiona</td><td>Crítica estrutural</td><td>Amplia as fontes</td><td>Usa instrumentalmente</td></tr>
            <tr><th scope="row">Horizonte</th><td>Emancipação popular</td><td>Superação do capitalismo e da forma jurídica</td><td>Democracia radical</td><td>Ganhos concretos</td></tr>
            <tr><th scope="row">Força</th><td>Protagonismo dos assessorados</td><td>Normatividade dos movimentos</td><td>Sujeitos coletivos de direito</td><td>Resposta urgente</td></tr>
            <tr><th scope="row">Limite</th><td>Risco de assistencialismo</td><td>Alta abstração teórica</td><td>Pode diluir o conflito de classe</td><td>Sem horizonte emancipatório próprio</td></tr>
            <tr><th scope="row">Tensão</th><td>Demanda imediata × formação política</td><td>Teoria × prática</td><td>Amplitude × conflito</td><td>Usar o direito sem ser usado por ele</td></tr>
          </tbody>
        </table>
      </div>
      <p class="tabela__dica">Arraste a tabela para o lado para ver as quatro colunas →</p>

      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">🤝</span><b>Assessoria jurídica popular (AJP).</b>
        Prática política e pedagógica de advogadas, advogados e estudantes junto a movimentos sociais.
        O traço central é a recusa ao assistencialismo: o saber popular é válido, e o conhecimento se
        constrói em conjunto. Referências: Paulo Freire, RENAP (1995) e os NAJUPs.
        <a href="assessoria-juridica-popular.html">Ver os textos da seção</a>.</li>

        <li><span class="emoji" aria-hidden="true">🔥</span><b>Direito insurgente.</b>
        O direito produzido pelas próprias classes subalternas em suas lutas — não o direito do Estado
        a serviço dos oprimidos. Tem dupla natureza: norma (cria obrigações dentro dos movimentos) e
        fato social (nasce de práticas concretas). Formulado por Miguel Pressburger e sistematizado por
        Ricardo Prestes Pazello, dialoga com Pachukanis e com a crítica descolonial.
        <a href="teoria-critica.html">Ver a seção de teoria</a>.</li>

        <li><span class="emoji" aria-hidden="true">🛣️</span><b>Direito achado na rua.</b>
        O direito legítimo não está só nos códigos e tribunais: emerge das ruas, das lutas e das práticas
        coletivas. O pluralismo jurídico reconhece múltiplas ordens normativas legítimas. Nasce na UnB,
        com Roberto Lyra Filho e a Nova Escola Jurídica Brasileira (NELJB), continuada por José Geraldo
        de Sousa Junior; a noção de <b>sujeitos coletivos de direito</b> é central.
        <a href="o-que-e-assessoria-juridica-popular.html">Ver o que é AJP</a>.</li>

        <li><span class="emoji" aria-hidden="true">🎯</span><b>Uso tático do direito.</b>
        Usar normas, processos e instituições como ferramenta de luta, sem ilusão de neutralidade.
        A distinção entre tática e estratégia é decisiva: taticamente se usa o que existe; estrategicamente
        se reconhece que o direito não é o terreno decisivo da transformação. A juridicização pode
        proteger no curto prazo e neutralizar no longo prazo.
        <a href="citacoes.html">Ver citações</a>.</li>
      </ul>

      <h3>Como se combinam na prática</h3>
      <p>Na prática, as quatro entram juntas. A <b>AJP</b> organiza o método: formação, linguagem
      acessível e protagonismo de quem vive o conflito. O <b>direito achado na rua</b> amplia o que
      conta como direito: normas comunitárias, usos, territórios e modos de vida que não cabem nos
      códigos. O <b>direito insurgente</b> lembra que assembleias, regulamentos internos e decisões
      coletivas valem sem homologação judicial. O <b>uso tático</b> decide quando entrar no Judiciário:
      ação civil pública, <i>habeas corpus</i>, bloqueio de bens, denúncia internacional — sem confundir
      vitória judicial com vitória política.</p>

      <h3>Onde ler no acervo</h3>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">📚</span><a href="assessoria-juridica-popular.html">Assessoria jurídica popular</a> — 97 textos sobre a prática.</li>
        <li><span class="emoji" aria-hidden="true">🧠</span><a href="teoria-critica.html">Teoria crítica</a> — 182 textos de crítica do direito.</li>
        <li><span class="emoji" aria-hidden="true">🌎</span><a href="assessoria-juridica-popular-no-mundo.html#referencias">Referências do comparado</a> — os artigos com DOI.</li>
      </ul>
    </section>
'''

with io.open(PAGINA, encoding="utf-8") as f:
    t = f.read()

novo, n = re.subn(r'    <section class="secao" id="direito-critico">.*?\n    </section>\n',
                  SECAO, t, count=1, flags=re.S)
if n == 0:
    raise SystemExit("nao achei a secao direito-critico")

# Referências novas, no fim da lista
marcador = "DOI: <a href=\"https://doi.org/10.24305/cadecs.v4i2.2016.17344\" target=\"_blank\" rel=\"noopener\">10.24305/cadecs.v4i2.2016.17344</a>.</li>"
if marcador in novo and "FREIRE, Paulo" not in novo:
    extra = """
        <li><span class="emoji" aria-hidden="true">📘</span>FREIRE, Paulo. <i>Pedagogia do oprimido</i>. Rio de Janeiro: Paz e Terra, 1970.</li>
        <li><span class="emoji" aria-hidden="true">📘</span>LYRA FILHO, Roberto. <i>O que é direito</i>. São Paulo: Brasiliense, 1982.</li>
        <li><span class="emoji" aria-hidden="true">📘</span>SOUSA JUNIOR, José Geraldo de. <i>Direito como liberdade</i>: o direito achado na rua. Porto Alegre: Sergio Antonio Fabris, 2011.</li>"""
    novo = novo.replace(marcador, marcador + extra, 1)

with io.open(PAGINA, "w", encoding="utf-8", newline="\n") as f:
    f.write(novo)

print("secao 4 reescrita:", n == 1)
print("referencias novas:", "LYRA FILHO" in novo)
