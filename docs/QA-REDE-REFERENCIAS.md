# QA — Rede, Mapeamento de AJUPs e Referências citadas
> **Correções aplicadas depois deste QA:** Markdown escapado e convertido em
> HTML nas fichas; URLs visíveis; botões “×” parasitas removidos; links de
> autor corrigidos; `scroll-padding-top`; impressão sem opacidade 0; filtros
> com contagem recalculada, estado vazio e busca sem acento; formulário de
> busca do topo abaixo da barra; placeholder de cidade corrigido.

**Data:** 22/11/2026
**Servidor:** `http://127.0.0.1:4348` (HTTP 200 nas três páginas)
**Páginas:** `rede.html`, `mapeamento-ajups.html`, `referencias-citadas.html`
**Viewports:** 390×844, 768×1024, 1440×900 (emulação de dispositivo)
**Ferramenta:** Brave + extensão `browse` (CDP), medições por `getBoundingClientRect` / `getComputedStyle`
**Natureza:** QA somente leitura. Nenhum HTML, CSS, JS ou dado do site foi alterado. Nada foi commitado.

---

## 1. Resumo

| Página | Overflow horizontal | Menu (6 itens) | Foco visível | Contraste | Links internos |
|---|---|---|---|---|---|
| `rede.html` | 0 em 390/768/1440 | OK (hambúrguer ≤1080px) | OK | OK | **3 quebrados (404)** |
| `mapeamento-ajups.html` | 0 | OK | OK | OK | 21/21 OK |
| `referencias-citadas.html` | 0 | OK | OK | OK | 192/192 OK |

Contagem e estados conferem: **40 registros** no mapeamento e **606 referências** em 192 grupos.
Os problemas graves estão em conteúdo renderizado (ABNT) e em efeitos/JS genéricos, não no layout base.

**Achados por severidade:** 3 P1 · 7 P2 · 9 P3.

---

## 2. Achados P1 (quebram o conteúdo ou a leitura)

### P1-1. `referencias-citadas.html` — Markdown cru em **606 de 606** fichas ABNT
Toda ficha exibe `**` e `*` literais:

> AUTOR NÃO IDENTIFICADO. \*\*Artigo a respeito da Comissão da Verdade publicado no Brasil de Fato\*\*. \*Brasil de Fato\*, [s.d.]. Disponível em: . Acesso em: 22 nov. 2026.

Origem: `etl/monta-referencias-abnt.py:133-163` gera `**título**` e `*periódico*`, e `etl/monta-referencias-pagina.py:67` injeta o texto sem escapar/renderizar.
O `.md` (`docs/referencias-abnt.md`) está correto; o HTML não.

### P1-2. `referencias-citadas.html` — 180 URLs invisíveis (“Disponível em: .”)
As URLs são escritas como `<https://…>` (sem escape) e o parser HTML as consome como **tag**:

```html
<p class="ref-cit__abnt">… Disponível em: <https: www.brasildefato.com.br="" node="" 6877="">. Acesso em: 22 nov. 2026.</https:></p>
```

Resultado medido: **180 fichas** com elemento fantasma `<https:>`; o texto renderizado fica `Disponível em: .` (endereço some) e o link da ficha é o único acesso.
Distribuição: 102 “Disponível aqui” + 73 “Link não respondeu” + 4 “Link restrito” + 1 avulsa = 180.
Correção: escapar (`&lt;…&gt;`) ou trocar por `<a href>` real; também corrigir `abnt()` para não montar tags.

### P1-3. `referencias-citadas.html` — 192 botões “×” soltos dentro dos grids
`casca.js:710` usa o seletor genérico `[data-busca]` para achar o campo de busca. Nesta página (e em toda ficha) `data-busca` é atributo de `<article class="ref-cit">`, então o botão “Limpar a busca” é inserido **depois de cada primeiro artigo de grupo**:

- **192 botões** `.busca__limpar`, 1 por `.grade-3`;
- visual: círculo “×” flutuando sobre o 2º card (ver `docs/qa/refs-1440-cards.png`);
- teclado: **1.138 paradas de Tab**, das quais **192** são “Limpar a busca” que não limpam nada (chamam `campo.value=''` no `<article>`);
- clicar não altera o filtro (testado: contador continua “11 referências”, campo continua “freire”).

Correção: usar seletor específico (`.busca__campo input[type=search], input[data-busca]`) ou renomear o atributo dos cards.

---

## 3. Achados P2 (atrapalham o uso)

### P2-1. `rede.html` — 3 links para autor dão 404
`rede.html:107` (seção Colunas):

| Link no HTML | Status | Arquivo correto |
|---|---|---|
| `autor-autor-tchenna-maso.html.html` | 404 | `autor-tchenna-maso.html` |
| `autor-autor-luiz-otavio-ribas.html.html` | 404 | `autor-luiz-otavio-ribas.html` |
| `autor-autor-ricardo-prestes-pazello.html.html` | 404 | `autor-ricardo-prestes-pazello.html` |

Sufixo `.html` duplicado. Não há outra ocorrência de `.html.html` no repositório.

### P2-2. `rede.html` — âncoras escondem o título atrás do cabeçalho
Os 8 atalhos (`#quem-somos` … `#bibliotecas`) existem e rolam, mas o `<h2>` do destino fica em `top: 0` com o cabeçalho fixo ocupando 65 px (medido em 390 e 1440). Não há `scroll-margin-top` para seções; só `#lista-acervo` tem (`acervo.css:1246`).
Sugestão: `:target, .secao, .ref-fonte { scroll-margin-top: 80px; }` ou `html { scroll-padding-top: 80px; }`.

### P2-3. Impressão/PDF perde metade da página
As seções usam revelação por rolagem (`.cai`, `acervo.css:1658-1665`). Em `@media print` as não reveladas continuam `opacity: 0` — medido em `rede.html`: **4 de 8 seções invisíveis** na impressão. O mesmo efeito deixa buracos em captura de página inteira (`docs/qa/rede-1440.png`).
Sugestão: `@media print { .cai { opacity: 1 !important; transform: none !important; } }`.

### P2-4. `mapeamento-ajups.html` — filtro deixa seções vazias e contagens contraditórias
Com `najup` + `PA` (3 resultados, todos em “Assessorias universitárias”), a tela mostra:

```
Redes ..................... 3 registros   (0 cards)
Advocacias populares ...... 9 registros   (0 cards)
Assessorias universitárias  25 registros  (3 cards)
```

- `secao__nota` é estática (`mapeamento-ajups.html:74, 96, 154, 308`), não acompanha o filtro;
- seções sem resultado não são ocultadas (diferente de `referencias-citadas.html`, que faz certo em `g.hidden`);
- sem estado “nenhum resultado”: busca `zzzz` → só “0 registros” e 4 títulos vazios.
Prints: `docs/qa/mapeamento-filtro-najup-pa.png`, `docs/qa/mapeamento-390-vazio.png`.

### P2-5. Busca dos dois filtros é sensível a acento
| Termo | Resultado |
|---|---|
| `cajuina` | 0 |
| `cajuína` | 1 (CAJUÍNA) |
| `sergio` | 1 referência |
| `sérgio` | 5 referências |

`mapeamento-ajups.html:342` e `referencias-citadas.html:3271` comparam `indexOf` puro. Sugestão: normalizar (`normalize('NFD').replace(/\p{Diacritic}/gu,'')`) nos dois lados — o próprio repositório já tem `sem_acento()` no ETL.

### P2-6. `mapeamento-ajups.html` — placeholder promete busca por cidade que não existe
O campo diz “Buscar por nome, sigla ou cidade” (`:64`), mas o filtro só olha `data-nome` (`:342`) e **nenhum card tem município** nos dados (só `data-uf`). “Teresina” só funciona porque está no nome do CAJUÍNA; “Curitiba”, “Porto Alegre”, “Recife” retornam 0.
Ou incluir cidade nos dados/`data-busca`, ou trocar o placeholder.

### P2-7. Barra de busca do topo cobre o menu em telas largas
Ao abrir a lupa em 1440px, o formulário (`position: absolute`, `z-index: auto`) ocupa x=519→855 e passa por cima de **5 dos 6 itens** do menu (Acervo, Biblioteca, Rede, Mística, IA). Ver `docs/qa/rede-busca-topo.png`.

---

## 4. Achados P3 (polimento e consistência)

1. **“9 com site ativo” vs. 8 etiquetas** — `rede.html:90` diz “12 entidades; 9 com site ativo”; a lista tem 8 “link ativo” + 4 “verificar”.
2. **Blogues: 21 itens, 20 URLs** — “Diálogos Lyrianos” e “Direito achado na rua” apontam para `http://odireitoachadonarua.blogspot.com/`. A nota “21 links; 19 responderam” fica ambígua (19 etiquetas “link ativo”, mas 18 endereços distintos ativos).
3. **“38 organizações históricas + 2 redes atuais”** (`rede.html:100`) não bate com o mapeamento: 3 Redes + 9 Advocacias + 25 Universitárias + 3 Movimentos.
4. **Rótulo contraditório** no mapeamento: “**Não verificado** · verificado em 2026-11-22” (12 cards) e “**Site fora do ar** · verificado em 2026-11-22” (4 cards).
5. **Estados idênticos** em `referencias-citadas.html`: “Disponível aqui”, “Link restrito”, “Link não respondeu” e “Sem link localizado” têm o mesmo `<span class="ref-status">` 12,8px cinza — só o primeiro é botão. Não há ícone/cor que diferencie.
6. **4 links restritos sem endereço acessível** — fichas do `jornada.unam.mx` e `formad.org.br`: nem link, nem URL visível (por causa do P1-2). O usuário não tem como tentar depois.
7. **Gramática**: “1 referência(s)”, “3 referência(s)” nas notas de grupo (`monta-referencias-pagina.py:74`).
8. **Inconsistência de “limpar”**: `referencias-citadas.html` tem “×” (192, errados); `mapeamento-ajups.html` não tem nenhum.
9. **Console**: ao abrir `mapeamento-ajups.html`, 3 erros de rede do componente Rádio — favicons `autenticafavelafm106-7.com` (DNS), `radio.ufg.br` e `www.radioyaravi.com` (404). Nenhum erro de JS nas três páginas.

Extras observados: seletor de tema corta “Pequl” (Pequi) em 390px; botões flutuantes de rolagem sobrepõem o `<h2>` em 390px; card do MST tem `<p></p>` vazio (`rede.html:96`); página de referências tem 90.212 px de altura em 1440 (169.682 px em 390) e 1.138 paradas de Tab, sem paginação.

---

## 5. O que passou (checklist pedido)

**Overflow horizontal:** 0 elementos ultrapassando o viewport nas 3 páginas × 3 larguras (`scrollWidth == innerWidth` em 390).

**Menu hambúrguer (390 e 768):**
- botão `.topo__abrir` 44×44, `aria-expanded` alternando, `aria-label` “Abrir/Fechar o menu”, `aria-controls="menu-principal"`;
- 6 itens na ordem: Home, Acervo, Biblioteca, **Rede (aria-current="page")**, Mística, IA;
- itens com 370 px de largura e 44 px de altura (bom alvo de toque), painel com fundo sólido;
- Tab percorre botão → 6 itens → busca; **Esc** fecha; abertura por clique e por Enter funcionam.

**Foco por teclado:** anel `solid 2.4px rgb(176,0,32)` em 100% dos elementos testados (skip link “Pular para o conteúdo” → marca → hambúrguer → busca → tema → A+ → conteúdo nos três viewports).

**Contraste:** 0 falhas WCAG AA nos temas **pequi** (padrão), **claro** e **alto contraste**, em 845 amostras nas larguras 390/1440 (pequi) e 958 amostras por tema (claro e alto contraste). Mínimos medidos: corpo 17,37:1; texto suave 10,66:1; links 9,57:1; status 10,66:1. Nota: na página de referências a varredura cobriu as 40 primeiras fichas + cabeçalho/hero, por causa do tamanho da página.

**Mapeamento de AJUPs:**
- filtros de busca, tipo (5 opções) e **UF (14 opções = exatamente as 14 UFs dos dados)** visíveis e funcionais em 390/768/1440;
- 40 cards = 3 redes + 9 advocacias + 25 universitárias + 3 movimentos; “40 registros” correto e `aria-live`;
- 24 cards com link (7 ativo, 16 histórico, 1 informado pelo dono) e 16 sem link (12 não verificados, 4 fora do ar) — coerente;
- todos os links externos com `rel="noopener"`, todos os alvos ≥ 44 px, link interno do AJUP com 200.

**Referências citadas:**
- 606 fichas em 192 grupos; a soma das notas de grupo = 606, sem IDs duplicados;
- estados: **102 “Disponível aqui”**, **74 “Link não respondeu”**, **4 “Link restrito”**, **426 “Sem link localizado”** (total 606, todas com ação);
- busca por autor, título, ano e post funciona e **oculta os grupos vazios** corretamente;
- os 192 links de “Citada em” respondem 200.

**Rede:**
- 8 âncoras com destino existente; link “Abrir o mapeamento” correto;
- 21 blogues, 12 entidades, 3 movimentos conferidos;
- 28 links internos, dos quais 25 OK e 3 com 404 (P2-1).

**Geral:** 1 `<h1>` por página, `lang="pt-BR"`, títulos únicos, nenhum `href="#"`, nenhum `target="_blank"` sem `noopener`, nenhum botão sem `type`.

---

## 6. Prints

Todos em `docs/qa/` (os arquivos já existiam no repositório e foram regerados idênticos nesta sessão; servem como evidência):

| Arquivo | Conteúdo |
|---|---|
| `rede-390.png`, `rede-768.png`, `rede-1440.png` | página inteira nas 3 larguras |
| `qa-rede-390-menu.png` | menu hambúrguer aberto em 390 |
| `rede-busca-topo.png` | busca do topo cobrindo 5 itens do menu (P2-7) |
| `mapeamento-390.png`, `mapeamento-768.png`, `mapeamento-1440.png` | página inteira |
| `mapeamento-filtro-najup-pa.png` | filtro aplicado: seções vazias com contagens antigas (P2-4) |
| `mapeamento-390-vazio.png` | busca sem resultado: 4 seções vazias (P2-4) |
| `refs-390.png`, `refs-768.png` | topo em telas menores |
| `refs-1440-freire.png` | busca “freire” + Markdown cru (P1-1) |
| `refs-1440-cards.png` | “×” solto sobre o card + `**` + “Disponível em: .” (P1-1/2/3) |

---

## 7. Lista priorizada de correções

**P1 — antes de publicar**
1. Renderizar o ABNT: escapar HTML e converter `**…**`/`*…*` em `<strong>`/`<em>` (ou emitir HTML do ETL). `monta-referencias-abnt.py:120-163` + `monta-referencias-pagina.py:67`.
2. Emitir URL como link (`&lt;url&gt;` ou `<a>`), eliminando as 180 tags `<https:>` fantasma.
3. Corrigir o seletor do botão limpar: `casca.js:710` → `input[type=search][data-busca], .busca__campo input[type=search]`; remove 192 botões.

**P2 — próxima rodada**
4. `rede.html:107`: corrigir os 3 links `autor-autor-*.html.html`.
5. Adicionar `scroll-padding-top`/`scroll-margin-top` (~80 px) global para âncoras.
6. `@media print`: forçar `.cai { opacity:1; transform:none }`.
7. Mapeamento: ocultar seções sem resultado, atualizar `secao__nota` no filtro e criar estado “nenhum resultado”.
8. Busca sem acento nas duas páginas (normalizar NFD).
9. Mapeamento: incluir cidade nos dados/`data-busca` ou ajustar o placeholder.
10. Busca do topo: não sobrepor `.topo__links` em ≥1081 px.

**P3 — polimento**
11. Corrigir contagens editoriais de `rede.html` (“9 com site ativo” → 8; “38+2” → 3 redes/37 organizações).
12. Deduplicar blogues ou explicitar que dois nomes usam o mesmo endereço.
13. Reescrever “Não verificado · verificado em …” e “Site fora do ar · verificado em …”.
14. Diferenciar visualmente os 4 estados de referência (ícone + texto).
15. Exibir a URL das 4 restritas e das 74 mortas como texto copiável.
16. “1 referência” (singular) nas notas de grupo; corrigir “confiança media” → “média”.
17. Botão de limpar também no mapeamento (ou remover o da página de referências).
18. Silenciar/adiar os favicons do rádio (3 erros de console).
19. Revisar truncamento do seletor de tema em 390 px, sobreposição dos botões flutuantes e o `<p></p>` vazio do MST.

---

## 8. Limites deste QA

- Só links **internos** foram testados (200/404). A vivacidade dos 41/44/107 links externos não foi verificada, para respeitar `robots.txt`, termos e ritmo de coleta.
- Contraste medido sobre cores computadas de fundo sólido; gradientes/imagens de fundo não entram na conta.
- Teclado simulado via CDP; uma particularidade (barra de espaço no hambúrguer não alternou) não foi reproduzida de forma confiável e ficou fora do relatório.
- O servidor em `127.0.0.1:4348` estava fora do ar no início da sessão e foi religado (estático) para o teste; depois foi reiniciado pelo dono. Nenhum arquivo do site foi tocado.
