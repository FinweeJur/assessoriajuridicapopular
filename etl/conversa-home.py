"""Barra de conversa com perguntas curadas no fim da home."""
import io

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

CONVERSA = """  <section class="conversa" aria-labelledby="conversa-titulo">
    <div class="miolo">
      <div class="secao__cabeca">
        <h2 id="conversa-titulo">Pergunte ao acervo</h2>
        <p class="secao__nota">Respostas rápidas, com fonte e link</p>
      </div>
      <div class="conversa__caixa" data-conversa>
        <div class="conversa__topo">
          <span class="conversa__avatar" aria-hidden="true">AJP</span>
          <div><b>Assistente do acervo</b><small>perguntas frequentes</small></div>
          <span class="conversa__status">aberto</span>
        </div>
        <div class="conversa__corpo" data-conversa-corpo>
          <p class="conversa__fala conversa__fala--bot">Olá! Escolha uma pergunta abaixo ou
          escreva a sua. As respostas curadas têm link para o texto original.</p>
        </div>
        <div class="conversa__perguntas" data-conversa-perguntas></div>
        <form class="conversa__form" data-conversa-form>
          <label class="sr-only" for="conversa-campo">Sua pergunta</label>
          <input id="conversa-campo" type="search" placeholder="Ou digite sua pergunta" autocomplete="off" />
          <button type="submit">Perguntar</button>
        </form>
      </div>
    </div>
  </section>

"""

p = RAIZ + r"\index.html"
t = io.open(p, encoding="utf-8").read()
if "class=\"conversa\"" not in t:
    i = t.rfind("</main>")
    t = t[:i] + CONVERSA + t[i:]
    if "conversa.js" not in t:
        t = t.replace("</body>", '<script src="conversa.js?v=1" defer></script>\n</body>', 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("conversa:", "class=\"conversa\"" in t)

# CSS: limita a lista de perguntas do painel flutuante
p = RAIZ + r"\acervo.css"
css = io.open(p, encoding="utf-8").read()
if ".assistente__curadas {" in css and "max-height: 190px" not in css:
    css = css.replace(".assistente__curadas { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 10px; }",
                      ".assistente__curadas { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 10px; max-height: 190px; overflow-y: auto; }", 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(css)
print("css curadas:", "max-height: 190px" in io.open(p, encoding="utf-8").read())
