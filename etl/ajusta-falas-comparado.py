import io

p = "assessoria-juridica-popular-no-mundo.html"
t = io.open(p, encoding="utf-8").read()

# Recortes por rede depois de "Onde ler no acervo"
alvo = """      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">📚</span><a href="assessoria-juridica-popular.html">Assessoria jurídica popular</a> — 97 textos sobre a prática.</li>
        <li><span class="emoji" aria-hidden="true">🧠</span><a href="teoria-critica.html">Teoria crítica</a> — 182 textos de crítica do direito.</li>
        <li><span class="emoji" aria-hidden="true">🌎</span><a href="assessoria-juridica-popular-no-mundo.html#referencias">Referências do comparado</a> — os artigos com DOI.</li>
      </ul>"""
novo = alvo + """

      <h3>Recortes por rede</h3>
      <ul class="linhas">
        <li><span class="emoji" aria-hidden="true">🕸️</span><a href="acervo.html?rede=renap">RENAP</a> — 40 textos que mencionam a Rede Nacional de Advogadas e Advogados Populares.</li>
        <li><span class="emoji" aria-hidden="true">🔎</span><a href="acervo.html?rede=ipdms">IPDMS</a> — 12 textos ligados ao Instituto de Pesquisa, Direito e Movimentos Sociais.</li>
        <li><span class="emoji" aria-hidden="true">🎓</span><a href="acervo.html?rede=renaju-ajup">RENAJU/AJUPs</a> — 140 textos sobre assessorias jurídicas universitárias e populares, de SAJU a NAJUP, CORAJE e AJUP.</li>
      </ul>

      <h3>Definições e falas do acervo</h3>
      <p class="colecao__nota">Recortes literais de posts do acervo, com link para o texto completo.
      As definições da tabela são síntese editorial; as falas abaixo são a voz dos próprios textos.</p>

      <figure class="cartao citacao">
        <blockquote><p>“A assessoria jurídica popular é uma práxis acima de tudo política. Ela assume um lado
        da luta de classes – o lado d@s oprimid@s – e busca contribuir com as ferramentas que dispõe e tem
        procurado desenvolver (advocacia, orientação jurídico-política, educação popular, expressões
        artísticas etc) para fortalecer a luta por direitos…”</p></blockquote>
        <figcaption><b>Direito e conjuntura – nova coluna no blogue AJP</b> ·
        <a href="direito-e-conjuntura-nova-coluna-no-blogue-ajp.html">ler no acervo</a></figcaption>
      </figure>

      <figure class="cartao citacao">
        <blockquote><p>“O direito insurgente é uma ideia tão forte. Uma vez que alia a resistência por meio
        do positivismo de combate, com a radicalidade de um pluralismo insurgente e popular, em que as
        lutas políticas também buscam instaurar um novo direito.”</p></blockquote>
        <figcaption><b>Calourada do SAJU-SP e extensão</b> ·
        <a href="calourada-do-saju-sp-e-extensao.html">ler no acervo</a></figcaption>
      </figure>

      <figure class="cartao citacao">
        <blockquote><p>“O uso tático do direito não pode enfronhar-se na injustiça da desonestidade de quem
        não luta ‘com’, mas apenas ‘para’.”</p></blockquote>
        <figcaption><b>Justiça, uma canção de amor e liberdade</b> ·
        <a href="justica-uma-cancao-de-amor-e-liberdade.html">ler no acervo</a></figcaption>
      </figure>"""

if alvo not in t:
    raise SystemExit("bloco Onde ler nao encontrado")
t = t.replace(alvo, novo, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("falas e redes:", "Recortes por rede" in t, "Definições e falas" in t)
