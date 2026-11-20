"""Revisão editorial final: textos, contagens, referências e links apontados no code review."""
import io
import os

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"


def ler(nome):
    with io.open(os.path.join(RAIZ, nome), encoding="utf-8") as f:
        return f.read()


def gravar(nome, texto):
    with io.open(os.path.join(RAIZ, nome), "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


# 1. Rodapé: fonte genérica (serve para blog, caderno, poemas e mística)
p = "etl/monta-secoes.py"
g = ler(p)
velho = """      <p>Textos publicados originalmente no blog
      <a href="https://assessoriajuridicapopular.blogspot.com/" target="_blank" rel="noopener">Assessoria Jurídica Popular</a>,
      em citação direta, com autor, data e link. Acervo montado a partir do blog original,
      com captura em 20/11/2026.</p>"""
novo = """      <p>Acervo montado a partir do blog
      <a href="https://assessoriajuridicapopular.blogspot.com/" target="_blank" rel="noopener">Assessoria Jurídica Popular</a>
      e de fontes parceiras, com autor, data e link. Captura em 20/11/2026.</p>"""
if velho in g:
    g = g.replace(velho, novo, 1)
    gravar(p, g)
print("rodapé fonte:", "fontes parceiras" in g)

# 2. Home: cartão grande sem "em citação direta"
t = ler("index.html")
t = t.replace("textos em citação direta", "textos transcritos", 1)
gravar("index.html", t)
print("home cartão:", "textos transcritos" in t)

# 3. Poemas: título, aviso de autorização repetido e rótulo da seção
t = ler("poemas.html")
for velho, novo in [
    ("Poemas do Caderno de Poesias — AJP", "Poemas do Caderno e poesia do blog — AJP"),
    ("<h1 id=\"titulo\">Poemas do Caderno de Poesias</h1>", "<h1 id=\"titulo\">Poemas do Caderno e poesia do blog</h1>"),
    ("data-titulo=\"Poemas do Caderno de Poesias\"", "data-titulo=\"Poemas do Caderno e poesia do blog\""),
    ("<span aria-current=\"page\">Poemas do Caderno de Poesias</span>", "<span aria-current=\"page\">Poemas do Caderno e poesia do blog</span>"),
    ("42 posts com poemas, versos e textos de poesia", "42 posts marcados como poesia, com versos e homenagens"),
    (" · publicado por autorização do responsável pelo site", ""),
]:
    t = t.replace(velho, novo)
gravar("poemas.html", t)
print("poemas título:", "Poemas do Caderno e poesia do blog" in t)
print("autorizações repetidas:", t.count("publicado por autorização"))

# 4. Caderno: corrige o sumário extraído
t = ler("caderno-de-poesias.html")
for velho, novo in [
    ("! Indicador não definido.", ""),
    ("Destrui ção", "Destruição"),
    ("siplesmente", "simplesmente"),
    ("traalhadores", "trabalhadores"),
    ("a mujeres mujeres", "a mujeres"),
]:
    t = t.replace(velho, novo)
gravar("caderno-de-poesias.html", t)
print("caderno corrigido:", "! Indicador" not in t)

# 5. Citações: remove a referência de Brecht sem edição localizada
t = ler("citacoes.html")
t = t.replace("      <p class=\"folha\">BRECHT, Bertolt. <i>Poemas</i>. Seleção e tradução conforme a edição consultada.</p>\n", "")
gravar("citacoes.html", t)
print("brecht ref removida:", "Seleção e tradução conforme a edição consultada" not in t)

# 6. Mística: ano da referência
t = ler("mistica.html")
t = t.replace("Levante Popular da Juventude, 2026.", "Levante Popular da Juventude, 2023.")
gravar("mistica.html", t)
print("mística 2023:", "Levante Popular da Juventude, 2023." in t)

# 7. Glossário: links errados
t = ler("glossario.html")
t = t.replace('Romance de Itamar Vieira Junior sobre terra, trabalho e ancestralidade. <a href="coracao-sem-medo.html">ver</a>',
              "Romance de Itamar Vieira Junior sobre terra, trabalho e ancestralidade.")
t = t.replace('Órgão estatal de assistência jurídica gratuita, previsto na Constituição de 1988. <a href="https://www.controlepopular.com.br/jurisprudencia/" target="_blank" rel="noopener">ver</a>',
              'Órgão estatal de assistência jurídica gratuita, previsto na Constituição de 1988. <a href="assessoria-juridica-popular-no-mundo.html">ver</a>')
gravar("glossario.html", t)
print("glossário:", "coracao-sem-medo.html\">ver" not in t)

# 8. Recomendações: Boletim sai de Livros e entra em Política e cultura
t = ler("recomendacoes.html")
linha = '        <li><span class="emoji" aria-hidden="true">📰</span><b>Boletim Tricontinental</b> — análises do Sul global.</li>\n'
if linha in t:
    t = t.replace(linha, "", 1)
    t = t.replace('        <li><span class="emoji" aria-hidden="true">📚</span><b>Textos marxistas sobre cultura</b> — seleção de leitura.</li>',
                  '        <li><span class="emoji" aria-hidden="true">📰</span><b>Boletim Tricontinental</b> — análises do Sul global.</li>\n'
                  '        <li><span class="emoji" aria-hidden="true">📚</span><b>Textos marxistas sobre cultura</b> — seleção de leitura.</li>', 1)
    gravar("recomendacoes.html", t)
print("tricontinental movido:", t.find("Boletim Tricontinental") > t.find("Política e cultura"))

# 9. Comparado: referências e links
t = ler("assessoria-juridica-popular-no-mundo.html")
t = t.replace("s mínimos (DE SOUZA, 2020).", "s mínimos.")
t = t.replace("(BUTA, 2021; DE JESUS; DE JESUS, 2023)", "(BUTA, 2021)")
t = t.replace("<td>De Souza (2020)</td>", "<td>Síntese da literatura</td>")
t = t.replace("<td>Madureira; De Lima (2024)</td>", "<td>Síntese da literatura</td>")
t = t.replace("<td>Souza (2020)</td>", "<td>Síntese da literatura</td>")
t = t.replace("<td>Dani (2025)</td>", "<td>Buta (2021)</td>")
t = t.replace("<td>Mina-Bone; Vargas-Fonseca (2024)</td>", "<td>Síntese da literatura</td>")
t = t.replace('<a href="citacoes.html">Ver citações</a>', '<a href="teoria-critica.html">Ver a seção de teoria</a>')
t = t.replace('    <a href="memoria-e-cultura.html">Memória e cultura</a> <span aria-hidden="true">/</span>\n', "")

extra_refs = """        <li><span class="emoji" aria-hidden="true">📄</span>TASK FORCE ON JUSTICE. <i>Justice for All</i>: final report. The Hague: Pathfinders for Peaceful, Just and Inclusive Societies, 2019. Disponível em: <a href="https://www.justiceforall2030.org/" target="_blank" rel="noopener">justiceforall2030.org</a>.</li>
        <li><span class="emoji" aria-hidden="true">📄</span>LEGAL SERVICES CORPORATION. <i>The Justice Gap</i>: the unmet civil legal needs of low-income Americans. Washington, DC: LSC, 2022. Disponível em: <a href="https://www.lsc.gov/" target="_blank" rel="noopener">lsc.gov</a>.</li>
"""
marcador = "DOI: <a href=\"https://doi.org/10.24305/cadecs.v4i2.2016.17344\" target=\"_blank\" rel=\"noopener\">10.24305/cadecs.v4i2.2016.17344</a>.</li>"
if marcador in t and "TASK FORCE ON JUSTICE. <i>Justice for All</i>" not in t:
    t = t.replace(marcador, marcador + "\n" + extra_refs.rstrip(), 1)
gravar("assessoria-juridica-popular-no-mundo.html", t)
print("comparado refs:", "TASK FORCE ON JUSTICE. <i>Justice for All</i>" in t)
print("comparado citações soltas:", all(x not in t for x in ["DE SOUZA", "Dani (2025)", "DE JESUS", "Mina-Bone"]))
print("migalha comparado:", "Memória e cultura" not in t)
