import io
import re

p = "assessoria-juridica-popular-no-mundo.html"
t = io.open(p, encoding="utf-8").read()

# Texto geral
t = t.replace("O direito crítico popular em quatro perspectivas",
              "O direito crítico popular em cinco perspectivas")
t = t.replace("1. Direito crítico popular: quatro perspectivas",
              "1. Direito crítico popular: cinco perspectivas")
t = t.replace("AJP, direito insurgente, direito achado na rua e uso tático — o que cada um responde",
              "AJP, direito insurgente, direito achado na rua, uso tático, positivismo de combate e pluralismo jurídico — o que cada um responde")
t = t.replace("As quatro perspectivas não são sinônimos.",
              "As cinco perspectivas não são sinônimos.")
t = t.replace("(insurgente) e <b>quando vale entrar no Judiciário</b> (uso tático).",
              "(insurgente), <b>quando vale entrar no Judiciário</b> (uso tático) e <b>como disputar a norma sem abandonar o pluralismo</b> (positivismo de combate e pluralismo jurídico).")

# Tabela
t = t.replace('<table class="tabela--cinco">', '<table class="tabela--seis">', 1)
t = t.replace("<caption>Os quatro conceitos em perspectiva</caption>",
              "<caption>Os cinco conceitos em perspectiva</caption>", 1)
t = t.replace("""            <th scope="col">Uso tático</th>
          </tr></thead>""",
              """            <th scope="col">Uso tático</th>
            <th scope="col">Positivismo de combate / pluralismo</th>
          </tr></thead>""", 1)

# Uma célula nova por linha
linhas = {
    "Natureza": "Estratégia jurídica e teoria pluralista",
    "Origem": "Brasil, anos 1980–90 — AJUP/FASE, Pressburger; pluralismo jurídico",
    "Base": "Norma estatal como arma + ordens jurídicas plurais",
    "Relação com o direito": "Usa a norma e reconhece outras fontes",
    "Horizonte": "Transformação social e direito vivo",
    "Força": "Luta dentro e fora do Estado",
    "Limite": "Risco de formalismo ou de diluição",
    "Tensão": "Norma estatal × pluralismo",
}
for dimensao, valor in linhas.items():
    padrao = r'(<tr><th scope="row">%s</th>.*?)(</tr>)' % re.escape(dimensao)
    def add(m):
        return m.group(1) + "<td>" + valor + "</td>" + m.group(2)
    t, n = re.subn(padrao, add, t, count=1, flags=re.S)
    if n != 1:
        raise SystemExit("linha nao encontrada: " + dimensao)

t = t.replace("Arraste a tabela para o lado para ver as quatro colunas",
              "Arraste a tabela para o lado para ver as cinco colunas", 1)

# Quinto item na lista das teorias
alvo = """        <li><span class="emoji" aria-hidden="true">🎯</span><b>Uso tático do direito.</b>"""
if alvo not in t:
    raise SystemExit("item uso tatico nao encontrado")
quinto = """        <li><span class="emoji" aria-hidden="true">⚖️</span><b>Positivismo de combate e pluralismo jurídico.</b>
        O positivismo de combate usa a norma estatal como arma contra-hegemônica, sem confundi-la com
        neutralidade; o pluralismo jurídico reconhece outras ordens normativas legítimas — comunitárias,
        indígenas, camponesas e populares. Juntos, disputam o direito do Estado e ampliam o campo do jurídico.
        <a href="teoria-critica.html">Ver a seção de teoria</a>.</li>

"""
t = t.replace(alvo, quinto + alvo, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("comparado atualizado:", "tabela--seis" in t, "| cinco:", t.count("cinco"))
