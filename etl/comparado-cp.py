"""Bloco de referências vivas do Controle Popular na página do comparado."""
import io
import os
import re

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
PAGINA = os.path.join(RAIZ, "assessoria-juridica-popular-no-mundo.html")

LINKS = [
    ("Jurisprudência por tema",
     "Decisões sobre desastres, conflitos ambientais, terra e direitos humanos.",
     "https://www.controlepopular.com.br/jurisprudencia"),
    ("Relatórios de Direitos Humanos",
     "Dados e relatórios sobre violações, conflitos e populações afetadas.",
     "https://www.controlepopular.com.br/ambiental/direitos-humanos"),
    ("Legislação e precedentes por tema",
     "Normas e julgados organizados por assunto.",
     "https://www.controlepopular.com.br/ambiental/legislacao"),
    ("Direitos Globais",
     "O debate internacional de direitos humanos.",
     "https://www.controlepopular.com.br/direitos-globais"),
    ("Direitos Comparados",
     "Comparação entre sistemas jurídicos e experiências nacionais.",
     "https://www.controlepopular.com.br/direitos-comparados"),
    ("Decisões LAI",
     "Pedidos de acesso à informação e as decisões sobre eles.",
     "https://www.controlepopular.com.br/ambiental/decisoes-lai"),
    ("Como denunciar — Direitos em Movimento",
     "O caminho para registrar e encaminhar uma violação de direitos.",
     "https://www.controlepopular.com.br/direitos-em-movimento/denuncia"),
    ("Europa: legislação transnacional",
     "Normas europeias que alcançam casos e empresas brasileiras.",
     "https://www.controlepopular.com.br/europa/legislacao-transnacionais"),
]

cartoes = "\n".join(
    '''        <article class="cartao cp-cartao">
          <h3>%s</h3>
          <p>%s</p>
          <a class="botao secundario" href="%s" target="_blank" rel="noopener">Abrir no Controle Popular</a>
        </article>''' % (t, d, u)
    for t, d, u in LINKS)

SECAO = '''    <section class="secao" id="controle-popular"><div class="secao__cabeca">
      <h2>5. O que existe no Controle Popular</h2>
      <p class="secao__nota">Portal parceiro, com %d portas de entrada</p></div>
      <p>O <b>Controle Popular</b> é um portal parceiro deste acervo. Reúne e organiza
      <b>dados públicos</b> sobre jurisprudência, legislação, relatórios de direitos humanos,
      decisões de acesso à informação e caminhos de denúncia. Não é um blog de opinião: é uma
      base de consulta, com link para a fonte de cada item. Cada cartão abre a página
      correspondente, em outra aba.</p>
      <div class="grade-cp">
%s
      </div>
      <p class="secao__nota">Sugestão de uso: comece pela jurisprudência do tema que você pesquisa,
      confira a legislação e os relatórios aplicáveis e só então volte ao comparado para situar o
      caso no debate internacional.</p>
    </section>

''' % (len(LINKS), cartoes)

with io.open(PAGINA, encoding="utf-8") as f:
    t = f.read()

t = re.sub(r'    <section class="secao" id="controle-popular">.*?\n    </section>\n', "", t, count=1, flags=re.S)

marcador = '    <section class="secao"><div class="secao__cabeca"><h2>O que isso muda para o acervo</h2></div>'
if marcador not in t:
    raise SystemExit("nao achei o marcador")
t = t.replace(marcador, SECAO + marcador, 1)

with io.open(PAGINA, "w", encoding="utf-8", newline="\n") as f:
    f.write(t)

print("controle popular:", t.count('id="controle-popular"'), "| cartoes:", t.count("cp-cartao"))
