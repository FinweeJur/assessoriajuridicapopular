# Plano de navegação — aproximar o site do blog original

> **Pedido (22/11/2026):** quem foi usuário do blog
> `assessoriajuridicapopular.blogspot.com` precisa repetir os mesmos
> movimentos, com mouse ou toque, para achar o que procurava. Sem perder as
> animações, os nove temas, a busca, o rádio, o chatbot e os componentes novos.
>
> **Regra:** não copiar a estética de 2011; reconstruir os **pontos de
> acesso** e a **hierarquia** com a identidade atual.

---

## 1. Como o blog original se organizava

### 1.1 Topo

- título do blog, à esquerda;
- **pesquisa** no topo;
- páginas fixas em linha: **Quem somos · Como postar · Bibliotecas ·
  Cadernos insurgentes · Colunas**;
- login do Blogger.

### 1.2 Coluna da direita (o “mapa” do blog)

A sidebar era o principal mapa de navegação. Ordem observada:

1. **Páginas** (as cinco acima);
2. **Pesquisar este blog**;
3. **Tema** (nuvem de marcadores: AJP, direitos humanos, movimentos, poesia,
   educação, teoria etc.);
4. **Biblioteca digital da assessoria jurídica popular**;
5. **Blogues parceiros** (21 links);
6. **Entidades Parceiras** (12 links);
7. **Arquivo do blog** (por ano e mês);
8. **Postagens em debate**;
9. **Leitores**;
10. **Inscrever-se / assinar**;
11. **Tradutor**;
12. blocos fixos: “Nosso mestre Roberto Lyra Filho”, “Jacques Alfonsin nosso
    colunista”, “A arte na educação popular”, “O caráter revolucionário da
    educação para a libertação”, “América Latina”, “Acessos”.

### 1.3 Corpo

- posts em ordem cronológica inversa;
- rótulos/temas no rodapé de cada post;
- “Postado por”, comentários, “Postagens mais antigas”;
- páginas estáticas no mesmo espaço do corpo (Bibliotecas, Colunas, Quem
  somos, Como postar, Cadernos).

### 1.4 O que o usuário antigo fazia sem pensar

| Movimento | Onde clicava |
|---|---|
| “Quem escreve isso?” | **Quem somos** no topo |
| “Como publico?” | **Como postar** no topo |
| “Onde estão os livros?” | **Bibliotecas** no topo/sidebar |
| “Quem são os parceiros?” | **Blogues parceiros** na sidebar |
| “Quais entidades apoiam?” | **Entidades Parceiras** na sidebar |
| “Onde tem AJUP perto de mim?” | **Mapeamento** (página “Quem somos” ou link) |
| “Quero ler por tema” | nuvem **Tema** na sidebar |
| “Quero ler por ano” | **Arquivo do blog** |
| “Quero poesia” | **Poesia crítica do direito** em Bibliotecas |
| “Quero uma coluna” | **Colunas** no topo |

---

## 2. Como o site novo se organiza hoje

- topo com **Home · Acervo · Biblioteca · Mística · IA**;
- busca expansível no topo; tema, A−/A+, Ouvir;
- subnavs de Acervo (Todos, Por ano, Autores, seções) e Biblioteca (Acervos,
  Obras, Formação, Teses, IPDMS, RENAP, Citações, Recomendações, Glossário);
- home com “Mapa do site” e “Referências e parceiros”;
- rodapé com Acervo, Seções, Fonte, Parcerias;
- menu flutuante “+” com Buscar, Rádio, Perguntar;
- páginas de texto com ficha de origem, citação, corpo, relacionados.

**O que ficou de fora:** Quem somos, Como postar, Blogues parceiros, Entidades
Parceiras, Mapeamento de AJUPs, arquivo por ano/mês na lateral e a nuvem de
temas no mesmo lugar. O usuário antigo não reconhece o caminho.

---

## 3. Princípios do meio-termo

1. **Manter as cinco portas conceituais** (Home, Acervo, Biblioteca, Mística,
   IA) e acrescentar **uma porta de utilidade: “Rede”**. No topo, ela é um
   sexto item; no conceito, não é uma sexta categoria de conteúdo — é a antiga
   sidebar reorganizada.
2. **O topo continua sendo o lugar dos comandos primários:** busca, tema,
   leitura, navegação. O “+” continua para ações rápidas, mas nada essencial
   pode existir só nele.
3. **A sidebar não volta como coluna fixa.** Ela vira uma página `rede.html`
   com âncoras e cartões. No desktop, um resumo de 3–4 links pode aparecer no
   rodapé da home; no celular, tudo entra no menu.
4. **O post não ganha botões grandes.** O link do original fica na ficha de
   origem, na linha “Blog”, no mesmo tamanho do texto; o “Sobre autor” sai e
   fica só “Todos os textos de …”.
5. **A nuvem de temas continua no Acervo**, mas ganha um atalho “Temas” no topo
   da página de rede e no menu mobile.
6. **O arquivo por ano continua em “Por ano”** (`blog.html`), com link no topo
   do Acervo e no rodapé.
7. **Nada de esconder o que o antigo usuário procurava:** “Quem somos”, “Como
   postar”, “Bibliotecas”, “Blogues parceiros”, “Entidades” e “Mapeamento”
   precisam estar a no máximo **dois cliques** de qualquer página.

---

## 4. Arquitetura proposta

### 4.1 Topo desktop

```text
[AJP]   Home   Acervo   Biblioteca   Rede   Mística   IA      [busca] [tema] [A− A+] [Ouvir]
```

- “Rede” depois de Biblioteca: é o antigo bloco de páginas/sidebar.
- Em telas < 900 px, os seis itens entram no menu hambúrguer, na mesma ordem.
- A busca continua no topo, não no “+”.

### 4.2 Página `rede.html`

Uma página, seis âncoras:

```text
Rede e comunidade
  [Quem somos] [Como postar] [Blogues parceiros] [Entidades parceiras]
  [Mapeamento de AJUPs] [Movimentos sociais] [Colunas] [Cadernos] [Bibliotecas]

#quem-somos       texto curto + link para “O que é AJP” e “Como formar”
#como-postar      política editorial + e-mail + critérios
#blogues          21 links, status (ativo/fora do ar), data do teste
#entidades        12 links, site/redes, status
#mapeamento       resumo + link para mapeamento-ajups.html
#movimentos       diretório de movimentos (MST, MTST, Levante, MAB, MPA…)
#colunas          link para autores.html e os 5 colunistas
#cadernos         link para biblioteca.html#renap
#bibliotecas      link para biblioteca.html
```

Cada cartão tem: título, uma linha de descrição, link principal e “verificado
em”. O visual usa os mesmos cartões, bordas e temas do site.

### 4.3 `mapeamento-ajups.html`

- filtros por **tipo** (advocacia popular, universitária, movimento), **UF** e
  **rede** (RENAP, RENAJU/AJUPs, IPDMS);
- ficha: nome, sigla, tipo, UF/cidade, site, Instagram/Facebook/YouTube,
  repositório, status, `verificado_em`, fonte;
- busca por nome;
- botão “este link mudou?” (mailto) e “incluir organização”;
- nota de método: Instagram/Facebook não são raspados; links confirmados
  manualmente.

### 4.4 Home

No “Mapa do site”, acrescentar um bloco **Rede**:

```text
Rede
Quem somos · Como postar · Blogues parceiros · Entidades
Mapeamento de AJUPs · Movimentos sociais
```

No rodapé, em “ACERVO”, acrescentar “Rede e parceiros”.

### 4.5 Página de texto

```text
migalha
título
ficha: autor | publicado | blog + “Ler no blog original” | regime | capturado
citação
corpo
relacionados
```

Sem `acoes-fonte`; sem botão “Sobre autor”. O link “Todos os textos de …”
continua acima da citação.

---

## 5. Hierarquia visual

| Nível | Elemento | Onde |
|---|---|---|
| 1 | marca + navegação principal | topo fixo |
| 2 | busca, tema, leitura | topo, à direita |
| 3 | título da página | início do conteúdo |
| 4 | ficha de origem | abaixo do título |
| 5 | citação | bloco de destaque |
| 6 | corpo | leitura |
| 7 | relacionados e ações secundárias | fim do texto |
| 8 | rádio/chat | “+” flutuante |

- O “+” não substitui a navegação principal; ele é atalho.
- Em mobile, o menu hambúrguer tem a mesma ordem do desktop, com “Rede” antes
  de Mística.
- Alvos de toque ≥ 44 px; nada de link essencial só no hover.
- A página de rede não usa sidebar; usa grid de cartões (1 coluna em 390 px,
  2 em 768, 3 em 1440).

---

## 6. O que implementar, em ordem

1. `rede.html` com as seis âncoras e os cartões; link no topo, home e rodapé.
2. `mapeamento-ajups.html` com `dados/ajups.json` e filtros.
3. `blogues.html`/`entidades.html` ou seções de `rede.html` com os 21 + 12
   links e status.
4. Diretório de movimentos em `rede.html#movimentos`.
5. Links locais de Poesia/Referências na Biblioteca; `poesia-critica` como hub.
6. Aliases para os nomes antigos (`quem-somos.html`, `como-postar.html`,
   `blogues-parceiros.html`, `entidades-parceiras.html`, `mapeamento.html`)
   redirecionando para as âncoras novas.
7. Atualizar `topo()` em `etl/monta-secoes.py` e reinjetar o topo em todas as
   páginas; bump de `acervo.css`/`casca.js`.
8. Testar 390/768/1440, teclado, contraste e leitor de tela.

## 7. Critérios de aceite

- [ ] De qualquer página, “Quem somos” em ≤ 2 cliques.
- [ ] “Como postar” em ≤ 2 cliques.
- [ ] “Blogues parceiros” e “Entidades” em ≤ 2 cliques.
- [ ] “Mapeamento de AJUPs” em ≤ 2 cliques.
- [ ] “Bibliotecas” em 1 clique (topo).
- [ ] “Colunas” em ≤ 2 cliques.
- [ ] “Poesia crítica” em ≤ 2 cliques a partir da Biblioteca.
- [ ] Nenhum botão grande de fonte depois da citação.
- [ ] Link do original na ficha, no tamanho do texto.
- [ ] 390 px sem rolagem horizontal; menu mobile com os seis itens.
- [ ] O “+” continua funcionando e não é a única porta de nada essencial.
- [ ] Temas, animações e componentes atuais preservados.
