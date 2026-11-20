"""Quatro páginas de conteúdo: Itamar, comparado mundial, citações e recomendações."""
import importlib.util
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

spec = importlib.util.spec_from_file_location("ms", os.path.join(RAIZ, "etl", "monta-secoes.py"))
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)

MODELO = """<!DOCTYPE html>
<html lang="pt-BR" data-theme="pequi">
<head>
  <script data-tema-cedo>try{var t=localStorage.getItem('renap-tema');if(t){document.documentElement.dataset.theme=t;}}catch(e){}</script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>@@TITULO@@ · AJP — Assessoria Jurídica Popular</title>
  <meta name="description" content="@@DESCRICAO@@" />
  <link rel="stylesheet" href="fontes/fontshare.css?v=3" />
  <link rel="stylesheet" href="temas/temas.css" />
  <link rel="stylesheet" href="temas/renap.css" />
  <link rel="stylesheet" href="acervo.css?v=36" />
  <link rel="stylesheet" href="reveal.css?v=36" />
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
<script src="casca.js?v=6" defer></script>
<script src="fundo-grade.js?v=3" defer></script>
</body>
</html>
"""


def escreve(arquivo, titulo, descricao, olho, lead, corpo, autor, data_iso, fonte_url, fonte_nome):
    html = MODELO.replace("@@TOPO@@", ms.topo("texto")).replace("@@RODAPE@@", ms.rodape())
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


def figura(trecho, autor, obra, ano, editora="", extra=""):
    return """    <figure class="cartao citacao">
      <blockquote><p>%s</p></blockquote>
      <figcaption><b>%s</b>%s%s</figcaption>
    </figure>""" % (ms.esc(trecho), ms.esc(autor),
                    (", em <i>%s</i>" % obra) if obra else "",
                    (". %s%s" % (editora, ", " + str(ano)) if ano else "") + extra)


# ── 1. Itamar ──────────────────────────────────────────────────────────────
TRECHOS = [
    "Então, ela arrasta com mais força e a lâmina encontra a terra, mas também encontra pequenas rochas, faíscas surgem e se extinguem. Ela deita sementes para morrerem ou brotarem. Ela semeia sonhos na esperança de ver germinar sobrevivência.",
    "Acreditar num mundo mais justo, que talvez não desponte pleno nesta geração ou na seguinte, mas que algum dia desabrochará, assim como tudo o que é semeado. Um mundo que não se pareça com o sonho dos alienados, mas que possa mais unir do que dividir.",
    "Quando nos alcançaram tínhamos apenas os saberes sobre o mundo — o ciclo das chuvas; o ciclo da terra; os dons; a criação; histórias contadas por gerações — de um lado a outro do mar. Atravessaram terra e mar […]",
    "Nos códigos genéticos, nos traços remotos a nos constituírem humanos, nas paisagens que habitamos — as árvores plantadas e as retiradas; as construções revelando as camadas de tempo de uma cidade; a terra arada, revolvida, exaurida, de onde vem o metal, o minério, de onde vem o alimento a nos manter de pé; a terra e o asfalto onde correm o sangue, mas também brota a vida.",
    "Qualquer vida poderia ter um sentido notável, não apenas as privilegiadas por livros e enciclopédias, por escritores e historiadores.",
    "Tornou-se sons, palavras, conhecimentos, cantos, movimentos. Arou e semeou o chão. Retirou do profundo da terra o que nomearam riqueza. Ergueu grandes e pequenas cidades, fronteiras e nações. Recriou mundos e deu sentido ao que parecia não ter rumo.",
    "A cadeia de produção se repete tantas vezes que ninguém mais se pergunta de onde vem o alimento até chegar ao prato. Em particular, o ciclo da semeadura, da colheita, da distribuição nunca se finda, e as pessoas não pensam no que comem por estarem imersas nos próprios desafios cotidianos.",
    "É tomada por sentimentos contraditórios de indignação e de afeto, conversa com o filho ausente como se conversasse com os santos; promete-lhe justiça numa dimensão da vida em que a lei é tudo o que sente.",
    "O ciclo da semeadura, da colheita, da distribuição nunca se finda, e as pessoas não pensam no que comem por estarem imersas nos próprios desafios cotidianos. […]",
    "Não existe mais a roça sem árvores, sem casas, sem gente, o verde e um grão para o qual sua avó não tinha receita. O solo exposto como a terra de uma cova recém-aberta.",
    "Mulheres cavavam covas e lançavam sementes com a mesma fé que seus antepassados tiveram na colheita. Com a mesma expectativa, Rita e Fátima experimentavam os condimentos, o sal, para que a comida fosse agradável ao paladar de quem se alimentaria dela. A fé movia as nuvens e a chuva, que fariam o grão crescer forte. Movia também os braços de Rita e Fátima picando cebolas, tomates, coentro, esmagando os dentes de alho, mexendo o fundo da panela […]",
    "Mas ela desobedece. Descobriu que nascera para desobedecer. E finge que não está impedida de se aproximar da autoridade pelos homens de sua segurança. Meu filho, as palavras ecoam sob a tenda, meu filho foi raptado pela polícia, governador. Vim saber o que o senhor vai fazer. Quero que me tragam ele vivo, como ele foi retirado de mim. Mas, se por acaso a polícia matou ele, me digam onde […]",
    "Olhando a paisagem, ela não pensa naqueles que carregaram as pedras em todos os tempos para construir essa fração de mundo, fascinante e violenta, tornando-a o lugar de pessoas como ela. Também não imagina que seus pés se encontram sobre o chão onde se levantou um antecessor distante de sua linhagem, vindo do oceano, desembarcando sem bagagem, carregando coisas belas e tristes em seu peito, sonhos e desejos, revolta e medo, a herança que ela revive sem saber que lhe pertence.",
    "Rita não fazia nada diferente do que outros, que perderam seus filhos, maridos e irmãos, tivessem feito. Paravam o trânsito, incendiavam pneus, iam para todo canto carregando a fotografia dos desaparecidos em cartazes e roupas. Duda precisa entender que as estratégias de justiça são muitas e não estão apenas nos códigos legais dominados pelos advogados. Passam pela subjetividade das vítimas, à espera de respostas […]",
    "E contava também das histórias de tristeza e desencanto da bisavó. Um banzo de outros tempos, de perdas acumuladas por muitas vias e razões: ser desgarrado da terra, perder os parentes e a […]",
    "Olhos vivos de dor e de sangue. A terra, motivo de cobiça e de luta; a terra enlouquecendo Carmelita, que despeja sal nela para torná-la infértil; a terra pela qual tantos caíram e sobre a qual poucos triunfaram.",
]

blocos = [figura(t, "Itamar Vieira Junior", "Coração sem medo", 2025, "Rio de Janeiro: Todavia") for t in TRECHOS]
corpo = """    <p class="aviso-lote"><b>Trechos transcritos</b> de <i>Coração sem medo</i> (Todavia, 2025).
    A paginação será confirmada na edição impressa. Cada trecho é curto e vem com autor, livro,
    editora e ano — citação, não reprodução da obra.</p>

%s

    <section class="secao" aria-labelledby="como-citar-itamar">
      <div class="secao__cabeca"><h2 id="como-citar-itamar">Como citar</h2></div>
      <p class="folha">VIEIRA JUNIOR, Itamar. <i>Coração sem medo</i>. Rio de Janeiro: Todavia, 2025.</p>
      <p class="secao__nota">Para um trecho: “(VIEIRA JUNIOR, 2025, p. __)”, com a página da edição impressa.</p>
    </section>""" % "\n\n".join(blocos)

escreve("coracao-sem-medo.html", "Coração sem medo: trechos escolhidos",
        "Trechos de Coração sem medo, de Itamar Vieira Junior: terra, semente, luto e justiça.",
        "Literatura · 2025",
        "Dezesseis passagens sobre a terra, o trabalho, o luto e as estratégias de justiça que não cabem nos códigos.",
        corpo, "Itamar Vieira Junior", "2025-01-01", "https://www.todavia.com.br/", "Todavia")

# ── 2. Citações ────────────────────────────────────────────────────────────
CITACOES = [
    ("O escravo que mata o senhor, seja em que circunstância for, mata sempre em legítima defesa.",
     "Luís Gama", "", 1830, "", "Advogado, jornalista e abolicionista (1830–1882)."),
    ("O Brasil precisa ser dirigido por uma pessoa que já passou fome. A fome também é professora.",
     "Carolina Maria de Jesus", "Quarto de despejo", 1960, "São Paulo: Francisco Alves"),
    ("Quem não conhece a fome há de dizer: “Quem escreve isto é louco”. Mas quem passa fome há de dizer: muito bem, Carolina. Os gêneros alimentícios devem ser ao alcance de todos.",
     "Carolina Maria de Jesus", "Quarto de despejo", 1960, "São Paulo: Francisco Alves"),
    ("Quem governa o nosso país é quem tem dinheiro, quem não sabe o que é fome, a dor e a aflição do pobre. Se a maioria revoltar-se, o que pode fazer a minoria? Eu estou ao lado do pobre.",
     "Carolina Maria de Jesus", "Quarto de despejo", 1960, "São Paulo: Francisco Alves"),
    ("O que me revolta é contra a ganância dos homens que espremem uns aos outros como se espremessem uma laranja.",
     "Carolina Maria de Jesus", "Quarto de despejo", 1960, "São Paulo: Francisco Alves"),
    ("Privatizaram sua vida, seu trabalho, sua hora de amar e seu direito de pensar. É da empresa privada o seu passo em frente, seu pão e seu salário. E agora, não contente, querem privatizar o conhecimento, a sabedoria, o pensamento, que só à humanidade pertence.",
     "Bertolt Brecht", "", 0, "", "Poeta e dramaturgo alemão (1898–1956)."),
    ("Para quem tem uma boa posição social, falar de comida é coisa baixa. É compreensível: eles já comeram.",
     "Bertolt Brecht", "", 0, "", "Poeta e dramaturgo alemão (1898–1956)."),
    ("Temam menos a morte e mais a vida insuficiente.",
     "Bertolt Brecht", "", 0, "", "Poeta e dramaturgo alemão (1898–1956)."),
]

blocos = []
for item in CITACOES:
    texto, autor, obra, ano, editora, nota = (list(item) + [""] * 6)[:6]
    rodape = ", em <i>%s</i>" % obra if obra else ""
    if ano:
        rodape += ". %s, %s" % (editora, ano)
    if nota:
        rodape += ". " + nota
    blocos.append(figura(texto, autor, obra, ano, editora, (". " + nota) if nota else ""))

corpo = """    <p class="aviso-lote"><b>Citações</b> de Luís Gama, Carolina Maria de Jesus e Bertolt Brecht.
    Cada uma vem com autor e obra. Onde a edição não foi conferida, a nota diz isso.</p>

%s

    <section class="secao" aria-labelledby="como-citar-citacoes">
      <div class="secao__cabeca"><h2 id="como-citar-citacoes">Como citar</h2></div>
      <p class="folha">JESUS, Carolina Maria de. <i>Quarto de despejo: diário de uma favelada</i>. São Paulo: Francisco Alves, 1960.</p>
      <p class="folha">BRECHT, Bertolt. <i>Poemas</i>. Seleção e tradução conforme a edição consultada.</p>
    </section>""" % "\n\n".join(blocos)

escreve("citacoes.html", "Citações: Gama, Carolina e Brecht",
        "Citações de Luís Gama, Carolina Maria de Jesus e Bertolt Brecht sobre fome, terra e dignidade.",
        "Citações",
        "Oito frases sobre fome, terra e dignidade — de um abolicionista, de uma catadora e de um dramaturgo.",
        corpo, "Luís Gama, Carolina Maria de Jesus, Bertolt Brecht", "1960-01-01",
        "https://www.controlepopular.com.br/", "Acervo AJP")

# ── 3. Recomendações ───────────────────────────────────────────────────────
corpo = """    <section class="secao" aria-labelledby="livros">
      <div class="secao__cabeca"><h2 id="livros">Livros</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">📕</span><b>A montanha é mais que uma imensa estepe verde</b>, de Omar Cabezas (Expressão Popular) — história da Revolução Nicaraguense.</li>
        <li><span class="emoji" aria-hidden="true">📗</span><b>Mayombe</b>, de Pepetela — história da Revolução Angolana.</li>
        <li><span class="emoji" aria-hidden="true">📘</span><b>Torto Arado</b>, de Itamar Vieira Junior — a luta pela terra do povo negro no Brasil.</li>
        
      </ul>
    </section>
    <section class="secao" aria-labelledby="filmes">
      <div class="secao__cabeca"><h2 id="filmes">Filmes</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">🎬</span><b>Judas e o Messias Negro</b> (Netflix) — história dos Panteras Negras.</li>
        <li><span class="emoji" aria-hidden="true">🎬</span><b>Marighella</b> — resistência à ditadura militar.</li>
      </ul>
    </section>
    <section class="secao" aria-labelledby="musicas">
      <div class="secao__cabeca"><h2 id="musicas">Músicas</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">🎧</span><b>BaianaSystem</b> — “Sulamericano”.</li>
        <li><span class="emoji" aria-hidden="true">🎧</span><b>Calle 13</b> — “Latinoamérica”.</li>
        <li><span class="emoji" aria-hidden="true">🎧</span><b>Racionais MC’s</b> — “Mil faces de um homem leal”.</li>
      </ul>
    </section>
    <section class="secao" aria-labelledby="politica">
      <div class="secao__cabeca"><h2 id="politica">Política e cultura</h2></div>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">✊</span><b>#LevanteNoConune</b> — resistir e indignar.</li>
        <li><span class="emoji" aria-hidden="true">🎤</span><b>RAP RESISTÊNCIA</b> — coletânea de rap político.</li>
        <li><span class="emoji" aria-hidden="true">📰</span><b>Boletim Tricontinental</b> — análises do Sul global.</li>
        <li><span class="emoji" aria-hidden="true">📚</span><b>Textos marxistas sobre cultura</b> — seleção de leitura.</li>
      </ul>
    </section>"""

escreve("recomendacoes.html", "Recomendações: livros, filmes e músicas",
        "Lista de livros, filmes e músicas indicados para estudar assessoria jurídica popular e lutas populares.",
        "Recomendações",
        "Uma estante de entrada: revoluções, terra, raça e cultura popular.",
        corpo, "Acervo AJP", "2026-11-20",
        "https://www.controlepopular.com.br/", "Acervo AJP")
