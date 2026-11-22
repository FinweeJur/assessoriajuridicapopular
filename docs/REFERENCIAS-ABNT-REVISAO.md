# Revisão ABNT das referências de confiança alta

> **Data:** 22/11/2026
> **Estado auditado:** `docs/referencias-abnt.md` e
> `etl/monta-referencias-abnt.py` no commit `6ede6d048` (“Ajusta imprenta,
> autoria e numeração do documento ABNT”). O documento foi regerado depois
> das correções de imprenta/autoria; portanto esta revisão descreve **esse**
> estado, não o anterior.
> **Reprodutibilidade:** conferida no commit: gerador + `dados/referencias.json`
> daquele estado reproduzem as 606 linhas do documento, 0 divergências.
> **Normas:** ABNT NBR 6023:2018 (referências) e NBR 10520:2023 (citações).
> **Escopo:** 30 referências de confiança `alta` (amostra estratificada) mais
> medições automáticas nos 221 registros `alta`.
> **Nada foi alterado** no documento, nos JSON de `dados/` nem no gerador.
> Sem commit.

---

## 1. Resumo

1. **A amostra melhorou, mas 27 das 30 referências ainda têm defeito.**
   Só 3 estão conformes; 12 (40%) têm defeito grave (autoria, título, tipo ou
   placeholder).
2. **A correção de imprenta introduziu um bug visível:** o local com partícula
   é cortado. “Rio de Janeiro” sai como **“Janeiro”** em 20 entradas (14 em
   `alta`), e “San Cristóbal de Las Casas” sai como “Las Casas”. A causa é a
   regex de `dados_trecho()`, que não aceita `de/da/do` dentro do local.
3. **`[s.l.]` caiu de 92 para 51 registros em `alta`**, mas ainda há **35
   falsos** — o `trecho` tem local e editora e a regex não os lê. O motivo mais
   comum é o mês antes do ano (`Rio de Janeiro: CPT-RJ, jan.-abr.1985`).
4. **Capítulo continua quebrado por construção:** 39 de 39 saem como
   `In: [coletânea], ano.` — sem organizador, livro, local, editora e páginas.
   Antes o placeholder era `[obra coletiva]`; trocou o rótulo, não a regra.
5. **Dados complementares continuam fora:** dos 59 `trechos` de `alta` com
   página, 27 não chegam à saída; das 8 edições, 7 se perdem; dos 5 anos com
   sufixo `a`/`b`, nenhum sobrevive — e isso impede a citação da NBR 10520.
6. **Pós-graduação:** 6 dos 15 trabalhos perdem a instituição que está no
   `trecho` porque a regex só reconhece `Universidade…`, `UFxx` e `PUC`;
   `UnB` não casa e vira `[s.l.: s.n.]`.
7. **Novos erros de inversão de nome:** `JÚNIOR, José Geraldo de Sousa`
   (o correto é `SOUSA JÚNIOR, José Geraldo de`) e
   `SALAZAR, Carlos Derpic` (o correto é `DERPIC SALAZAR, Carlos`).
8. O que **foi corrigido** e deve ser preservado: numeração contínua
   (1–606), autor invertido na maioria, título primeiro quando não há autor,
   local/editora em parte dos livros, e cabeçalho coerente com o corpo
   (102 abertos / 4 restritos / 74 mortos / 0 não verificados).

---

## 2. Metodologia

### 2.1. Base

| Item | Valor |
|---|---:|
| Referências em `dados/referencias.json` | 606 |
| Confiança `alta` | 221 |
| Confiança `média` | 149 |
| Confiança `baixa` | 236 |
| Sem autor | 250 |
| Sem ano (`[s.d.]`) | 284 |
| Com URL | 180 (177 distintas) |
| Entradas no documento | 606 (1–606, sem reinício) |

A confiança é heurística do extrator, não revisão humana
(`REFERENCIAS-PILOTO.md`, seção 5). Por isso a amostra saiu **só** de `alta`:
é o subconjunto que o documento apresenta como pronto para citar.

### 2.2. Desenho da amostra

Amostra estratificada por `tipo`, seleção aleatória dentro de cada estrato,
semente fixa `20261122` (reprodutível):

| Tipo | Em `alta` | Na amostra |
|---|---:|---:|
| livro | 124 | 13 |
| artigo | 42 | 6 |
| capítulo | 30 | 4 |
| dissertação | 7 | 2 |
| monografia | 7 | 1 |
| legislação | 6 | 1 |
| tese | 1 | 1 |
| relatório | 2 | 1 |
| documento | 1 | 1 |
| obra | 1 | 0 |
| **Total** | **221** | **30** |

Cada item foi conferido em três níveis: a linha publicada, os campos do JSON
(`autor`, `titulo`, `ano`, `veiculo`, `tipo`, `url`) e o `trecho`, que é a
evidência textual do post. A correção proposta usa **apenas o que está no
`trecho`**; quando ele não basta (por exemplo, a data do Decreto nº
11.995/2024), a correção fica marcada como pendente, sem invenção.

Como o gerador reproduz o documento exatamente, a linha publicada e a saída
de `abnt()` são a mesma coisa — o que se lê aqui é o que o código faz.

### 2.3. Códigos de defeito

| Código | Defeito |
|---|---|
| **A** | Autoria: não invertida, invertida errado, autor que não é autor, autor apenas inferido |
| **T** | Título: absorveu imprenta/evento/editora, é parágrafo, truncado ou tem resíduo de marcação |
| **P** | Tipo/suporte errado (artigo × capítulo × livro × evento) ou item que não é referência |
| **I** | Imprenta: local/editora/instituição omitidos ou truncados apesar de constarem no `trecho` |
| **D** | Dados complementares omitidos: páginas, volume, número, edição, coleção, curso, tradução |
| **H** | Placeholder interno: `[coletânea]`, `*[periódico]*`, `[s.l.: s.n.]` quando o dado existe |
| **F** | Forma: pontuação, caixa, destaque, espaço colado, truncamento, sufixo `a`/`b` |

**Grave** = A, T, P ou H. **Não grave** = I, D, F.

### 2.4. Limites

- Não abri os HTML originais nem fonte externa: a conferência é
  documento × JSON × `trecho`.
- NBR 6023:2018 e NBR 10520:2023 foram aplicadas de memória técnica, sem
  consulta ao texto pago. Onde a norma admite mais de uma prática (indicar ou
  não a primeira edição), registro a divergência em vez de decretar erro.
- Amostra de 30 sobre 221: margem ampla (ordem de ±15 pontos). As medições
  automáticas da seção 4.2 cobrem os 221 e não têm essa margem.
- O repositório estava em movimento durante a revisão (commits `de30ee58f`,
  `5b1b8ce1e` e `6ede6d048` no mesmo dia). Tudo aqui se refere a
  `6ede6d048`; uma nova rodada pode alterar os números. Na última conferência,
  a árvore de trabalho já tinha ~72 linhas de diferença no documento e links
  novos no JSON, feitos por outra sessão — não afetam a amostra nem os totais
  acima, mas quem for aplicar as correções deve começar pelo estado atual.

---

## 3. As 30 referências comentadas

O bloco “como está” reproduz a linha do documento (negrito e itálico
preservados); títulos muito longos aparecem abreviados com `…`. O número é o
da entrada em `docs/referencias-abnt.md`, que agora vai de 1 a 606 sem
reinício.

### 3.1. Artigo (6)

**1. #341 · `ref-5eeef921ef11` · defeitos: F**
- Como está: `LYRA FILHO, Roberto. **Normas jurídicas e outras normas sociais**. *Revista Direito e Avesso*, Brasília, n. 1, p. 49-60, 1982.`
- Problema: só o destaque. Há negrito no título do artigo **e** itálico no periódico — dois padrões na mesma referência. Pela NBR, o destaque recai sobre o título da publicação (o periódico), não sobre o título do artigo.
- Correção: `LYRA FILHO, Roberto. Normas jurídicas e outras normas sociais. *Revista Direito e Avesso*, Brasília, n. 1, p. 49-60, 1982.`

**2. #291 · `ref-6b9154d2ebd9` · defeitos: A, T, P, H**
- Como está: `O Conselho Editorial. **REVISTA DO SAJU - EDITAL DE CHAMADA DE ARTIGOS. O Serviço de Assessoria Jurídica da Universidade Federal do Rio Grande do Sul (SAJU-UFRGS) vem informar que está aberto o período de seleção…**. *[periódico]*, 2012.`
- Problemas: não é artigo, é edital de chamada; “O Conselho Editorial” é órgão, não autor; o título é o texto do edital inteiro; placeholder `*[periódico]*`.
- Correção: retirar da lista de referências. Se mantido: `SERVIÇO DE ASSESSORIA JURÍDICA (UFRGS). Edital de chamada de artigos para o v. 7, n. 2. Porto Alegre, 2012.`

**3. #263 · `ref-7bdc688ec44b` · defeitos: T, P, I**
- Como está: `KOPITTKE, Alberto Liebling. **Introdução a teoria e prática dialética no direito brasileiro: a experiência da Renap**. *Renap. São Paulo*, São Paulo, p. 21, 2010.`
- Trecho: `… São Paulo: Expressão Popular, 2010, p. 21.`
- Problemas: é livro, não artigo; `Renap. São Paulo` virou “periódico” (é o título + a cidade); a cidade aparece duas vezes e a editora (`Expressão Popular`) desapareceu.
- Correção: `KOPITTKE, Alberto Liebling. Introdução à teoria e prática dialética no direito brasileiro: a experiência da Renap. São Paulo: Expressão Popular, 2010.` (o “a teoria” do original parece erro de digitação da fonte; registrar, não corrigir em silêncio).

**4. #239 · `ref-7f7c87daffec` · defeitos: I, D, F**
- Como está: `INSTITUTO APOIO JURÍDICO POPULAR. **Boletim Informativo do Instituto Apoio Jurídico Popular - Responsabilidade de quem? (ação de responsabilidade civil)**. *Boletim Informativo do Instituto Apoio Jurídico Popular - Responsabilidade de quem? (ação de resp*, n. 4, 1992.`
- Trecho: `… Rio de Janeiro, n.4, Coletivo de Juristas Populares, jul.-ago. 1992.`
- Problemas: o mesmo texto é título e veículo; o veículo está **truncado no meio de “resp”** (limite `[^,.]{0,90}` no extrator); local, editora e mês perdidos.
- Correção: `Responsabilidade de quem? (ação de responsabilidade civil). *Boletim Informativo do Instituto Apoio Jurídico Popular*, Rio de Janeiro, n. 4, jul.-ago. 1992.`

**5. #231 · `ref-b061f28b2214` · defeitos: T, P, D, H**
- Como está: `HERRERA FLORES, Joaquín. **Reflexión en torno al concepto de derechos humanos. Jornadas Internacionales sobre derechos humanos, 5-7 dez. 1998, Granada, Asociación Pro Derechos Humanos de Andalucía, 1999**. *[periódico]*, p. 11-35, 1999.`
- Problemas: é trabalho em evento, não artigo de periódico; o título absorveu evento, datas, cidade, editora e ano; `*[periódico]*` é placeholder.
- Correção: `HERRERA FLORES, Joaquín. Reflexión en torno al concepto de derechos humanos. In: JORNADAS INTERNACIONALES SOBRE DERECHOS HUMANOS, 1998, Granada. [Anais…]. Granada: Asociación Pro Derechos Humanos de Andalucía, 1999. p. 11-35.`

**6. #298 · `ref-f074f6a25055` · defeitos: F**
- Como está: `PAZELLO, Ricardo Prestes. **Teorias críticas do direito e assessoria jurídica popular**. *Revista Direitos Humanos e Sociedade*, v. 2, p. 141-161, 2019.`
- Problema: só o destaque duplo (negrito no artigo + itálico no periódico).
- Correção: `PAZELLO, Ricardo Prestes. Teorias críticas do direito e assessoria jurídica popular. *Revista Direitos Humanos e Sociedade*, v. 2, p. 141-161, 2019.`

### 3.2. Capítulo (4)

**7. #277 · `ref-4b6d1484cbf9` · defeitos: T, P, D, F**
- Como está: `Lyra Filho, Roberto. **Introdução ao Direito como ciência social", In: Revista brasileira de filosofia**. In: [coletânea], 1973.`
- Problemas: é artigo de periódico, não capítulo; o título carrega `", In: Revista brasileira de filosofia`; `v. 23, n. 90, p. 180-185` ignorados; `In: [coletânea]` não é referência; sobrenome em caixa mista, diferente das outras entradas do mesmo autor.
- Correção: `LYRA FILHO, Roberto. Introdução ao Direito como ciência social. *Revista Brasileira de Filosofia*, v. 23, n. 90, p. 180-185, abr./jun. 1973.`

**8. #222 · `ref-955b140f5945` · defeitos: I, D, H**
- Como está: `HERRERA FLORES, Joaquín. **La fundamentación de los derechos humanos desde la Escuela de Budapest**. In: [coletânea], 1995.`
- Trecho: `Em: THEOTONIO, Vicente; PRIETO, Fernando (Coord.). Los Derechos Humanos: una reflexión interdisciplinar: Seminário de Investigación Francisco Suárez. Córdoba: Etea, 1995, p. 23-56.`
- Problemas: organizadores, título do livro, local, editora e páginas estavam no trecho e viraram placeholder.
- Correção: `HERRERA FLORES, Joaquín. La fundamentación de los derechos humanos desde la Escuela de Budapest. In: THEOTONIO, Vicente; PRIETO, Fernando (coord.). *Los Derechos Humanos: una reflexión interdisciplinar*. Córdoba: Etea, 1995. p. 23-56.`

**9. #273 · `ref-af0626a77fe1` · defeitos: T, P, D, F**
- Como está: `Lyra Filho, Roberto. **Acriminologia Dialética em ação", In: Notícia do Direito Brasileiro**. In: [coletânea], 1971.`
- Problemas: mesmo padrão do item 7; “Acriminologia” parece “A criminologia” com o artigo colado.
- Correção: `LYRA FILHO, Roberto. A criminologia dialética em ação. *Notícia do Direito Brasileiro*, p. 193-198, 1971.` (confirmar o título na fonte antes de publicar).

**10. #184 · `ref-cd72d4852aa1` · defeitos: A, D, H**
- Como está: `BONILLA, Victor D; CASTILLO, Gonzalo; BORDA, Orlando Fals; LIBREROS, Augusto. **Causa popular, ciência popular. Uma metodologia…**. In: [coletânea], 1999.`
- Trecho: `In: BRANDÃO, Carlos Rodrigues. Repensando a pesquisa militante. São Paulo: Brasiliense, 1999.`
- Problemas: `BORDA, Orlando Fals` — o sobrenome composto é **Fals Borda**; organizador, livro, local e editora descartados; o original separa título e subtítulo por ponto, e a NBR usa dois-pontos.
- Correção: `BONILLA, Victor D.; CASTILLO, Gonzalo; FALS BORDA, Orlando; LIBREROS, Augusto. Causa popular, ciência popular: uma metodologia do conhecimento científico através da ação. In: BRANDÃO, Carlos Rodrigues. *Repensando a pesquisa militante*. São Paulo: Brasiliense, 1999.`

### 3.3. Dissertação (2)

**11. #207 · `ref-a2b260b2f81d` · defeitos: D**
- Como está: `GÓES JUNIOR, José Humberto de. **Da pedagogia do oprimido ao direito do oprimido…**. 2008. Dissertação – Universidade Federal da Paraíba.`
- Trecho: `… Dissertação (Mestrado em Ciências Jurídicas) – Universidade Federal da Paraíba, João Pessoa, 2008, 189 p.`
- Problemas: a instituição apareceu (bom), mas o curso, a cidade, as páginas e o ano final sumiram. `Tipo – Instituição` sem local não fecha a referência.
- Correção: `GÓES JUNIOR, José Humberto de. Da pedagogia do oprimido ao direito do oprimido: uma noção de direitos humanos na obra de Paulo Freire. 2008. 189 f. Dissertação (Mestrado em Ciências Jurídicas) – Universidade Federal da Paraíba, João Pessoa, 2008.`

**12. #202 · `ref-bf0edf80d1cc` · defeitos: D, H**
- Como está: `CARLET, Flávia. **Advocacia popular…**. 2010. Dissertação – [s.l.: s.n.].`
- Trecho: `… Dissertação (Mestrado em Direito) - UnB, Brasília, 2010.`
- Problemas: **UnB e Brasília estão no trecho e não foram lidos** — a regex de instituição não reconhece `UnB`. A referência regrediu em relação à versão anterior.
- Correção: `CARLET, Flávia. Advocacia popular: práticas jurídicas e sociais no acesso ao direito e à justiça aos movimentos sociais de luta pela terra. 2010. Dissertação (Mestrado em Direito) – Universidade de Brasília, Brasília, 2010.`

### 3.4. Documento (1)

**13. #59 · `ref-0e6a0c487e2e` · defeitos: A, P**
- Como está: `**EDITAL DE INSCRIÇÃO, SELEÇÃO E MATRÍCULA - N. 013/2013**. 2013. Disponível em: <https://www.goias.ufg.br/…>. Acesso em: 22 nov. 2026.`
- Problemas: começar pelo título é o correto sem autor, mas o documento é institucional (o host e o caminho indicam UFG — confirmar); o título é o assunto do edital; falta local.
- Correção: `UNIVERSIDADE FEDERAL DE GOIÁS. Edital de inscrição, seleção e matrícula n. 013/2013. Goiânia, 2013. Disponível em: <…>. Acesso em: 22 nov. 2026.`

### 3.5. Tese (1)

**14. #262 · `ref-3f7fc449f6a0` · defeitos: A, I, D**
- Como está: `JÚNIOR, José Geraldo de Sousa. **Direito como liberdade…**. 2008. Tese – [s.l.: s.n.].`
- Trecho: `… Tese (Doutorado em Direito) - UnB, Brasília, 2008.`
- Problemas: **a inversão tratou “Júnior” como sobrenome** — o correto é `SOUSA JÚNIOR, José Geraldo de`; e a instituição se perdeu pelo mesmo problema de `UnB`.
- Correção: `SOUSA JÚNIOR, José Geraldo de. Direito como liberdade: o Direito Achado na Rua: experiências populares emancipatórias de criação do Direito. 2008. Tese (Doutorado em Direito) – Universidade de Brasília, Brasília, 2008.`

### 3.6. Legislação (1)

**15. #52 · `ref-7f06cbfefccd` · defeitos: T, D, F**
- Como está: `BRASIL. **Decreto nº 11.995/2024**. 2024. Disponível em: <https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/decreto/d11995.htm>. Acesso em: 22 nov. 2026.`
- Problemas: `nº 11.995/2024` não é o título oficial — falta a data (“de 25 de outubro de 2024”) e a ementa; o ano aparece dentro do título e solto depois. O trecho só traz o número, então data e ementa **precisam ser conferidas no link**.
- Correção: `BRASIL. Decreto nº 11.995, de 25 de outubro de 2024. [Ementa oficial]. Brasília, DF: Presidência da República, 2024. Disponível em: <…>. Acesso em: 22 nov. 2026.` (pendente de conferência).

### 3.7. Relatório (1)

**16. #252 · `ref-fd13093af167` · defeitos: I, F**
- Como está: `INSTITUTO APOIO JURÍDICO POPULAR. **Relatório 1992-1993**. 1993. [Relatório].`
- Trecho: `… Rio de Janeiro: AJUP, 1993.`
- Problemas: o ramo `relatorio` do gerador **não usa imprenta nenhuma** — local e editora são descartados por construção; `[Relatório]` é redundante.
- Correção: `INSTITUTO APOIO JURÍDICO POPULAR. Relatório 1992-1993. Rio de Janeiro: AJUP, 1993.`

### 3.8. Livro (13)

**17. #260 · `ref-08419286e0ba` · defeitos: I, D, F**
- Como está: `JEAMMAUD, Antoine. **Proposta para uma compreensãomaterialista do direito do trabalho**. [s.l.]: [s.n.], 1985.`
- Trecho: `… Rio de Janeiro: CPT-RJ, jan.-abr.1985. Coleção Seminários, n. 4`
- Problemas: `[s.l.: s.n.]` falso; o mês antes do ano (`jan.-abr.1985`) quebra a regex de ano, que exige `, AAAA`; “compreensão materialista” colado; coleção omitida.
- Correção: `JEAMMAUD, Antoine. Proposta para uma compreensão materialista do direito do trabalho. Rio de Janeiro: CPT-RJ, 1985. (Coleção Seminários, 4).`

**18. #205 · `ref-0bb524e3e61d` · defeitos: I, D, F**
- Como está: `FREIRE, Paulo. **Pedagogia do oprimido**. Janeiro: Paz e Terra, 1983.`
- Trecho: `12. ed. Rio de Janeiro: Paz e Terra, 1983.`
- Problemas: **“Janeiro” não é cidade** — o local foi cortado porque “Rio de Janeiro” tem a partícula “de”; e a edição (`12. ed.`) foi descartada.
- Correção: `FREIRE, Paulo. Pedagogia do oprimido. 12. ed. Rio de Janeiro: Paz e Terra, 1983.`

**19. #233 · `ref-121b7ea6dfb8` · defeitos: I, D, F**
- Como está: `HERRERA RIVAS, Alícia. **Crise da JustiçaJudiciária**. [s.l.]: [s.n.], 1984.`
- Trecho: `Rio de Janeiro: CPT-RJ, jan.-abr.1984. Coleção Seminários, n. 1`
- Correção: `HERRERA RIVAS, Alícia. Crise da Justiça Judiciária. Rio de Janeiro: CPT-RJ, 1984. (Coleção Seminários, 1).`

**20. #280 · `ref-257cff7f87fb` · defeitos: I, D**
- Como está: `MALHEIRO, Bruno; PORTO-GONÇALVES, Carlos Walter; MICHELOTTI, Fernando. **Horizontes amazônicos…**. [s.l.]: Fundação Rosa Luxemburgo; Expressão Popular, 2021.`
- Trecho: `1a. São Paulo: Fundação Rosa Luxemburgo; Expressão Popular, 2021.`
- Problemas: `[s.l.]` falso — a regex não aceita o prefixo `1a.` antes da cidade.
- Correção: `MALHEIRO, Bruno; PORTO-GONÇALVES, Carlos Walter; MICHELOTTI, Fernando. Horizontes amazônicos: para repensar o Brasil e o mundo. São Paulo: Fundação Rosa Luxemburgo; Expressão Popular, 2021.` (a primeira edição não precisa ser indicada).

**21. #357 · `ref-3f0e5edf81e1` · conforme**
- `SCHMITT, Carl. **Teologia política**. Belo Horizonte: Del Rey, 2006.`
- Nada a corrigir. É uma das 3 entradas conformes da amostra.

**22. #363 · `ref-6d9a3c02f4ac` · defeitos: D**
- Como está: `STUCKA, Petr Ivanovich. **Direito e luta de classes: teoria geral do direito**. São Paulo: Acadêmica, 1988.`
- Trecho: `Tradução de Sílvio Donizete Chagas. São Paulo: Acadêmica, 1988, 176 p.`
- Problemas: local e editora corretos; faltam o tradutor e as páginas.
- Correção: `STUCKA, Petr Ivanovich. Direito e luta de classes: teoria geral do direito. Tradução de Sílvio Donizete Chagas. São Paulo: Acadêmica, 1988. 176 p.`

**23. #228 · `ref-77a0e723eaa2` · conforme**
- `HERRERA FLORES, Joaquín. **Los derechos humanos desde la escuela de Budapeste**. Madrid: Tecnos, 1989.`
- Nada a corrigir.

**24. #166 · `ref-8144ecaea7fd` · defeitos: F**
- Como está: `BALDEZ, Miguel Lanzellotti. **Conselhos Populares e usucapião especial urbano**. Petrópolis: Centro de Direitos Humanos, 1991.`
- Trecho: `Petrópolis: Centro de Direitos Humanos, 1991b.`
- Problema: **o `b` do ano desapareceu**. Sem ele, esta obra colide com as outras de BALDEZ em 1991 e a citação fica ambígua.
- Correção: `BALDEZ, Miguel Lanzellotti. Conselhos Populares e Usucapião Especial Urbano. Petrópolis: Centro de Direitos Humanos, 1991b.`

**25. #348 · `ref-93defba6bce0` · conforme (com ressalva)**
- `LYRA FILHO, Roberto. **Problemas atuais do ensino jurídico**. Brasília: Obreira, 1981.`
- Formatação correta. Ressalva: o autor **não está no trecho** (`Problemas atuais do ensino jurídico. Brasília: Obreira, 1981.`) — foi atribuído pela lista da página de origem. A atribuição precisa constar como nota.

**26. #194 · `ref-a0c16ed4dd65` · defeitos: I, D**
- Como está: `CHAGAS, Sílvio Donizete (org.). **Lições de direito civil alternativo**. [s.l.]: Acadêmica, 1994.`
- Trecho: `São paulo: Acadêmica, 1994, 164 p.`
- Problemas: o local está em minúscula na fonte (`São paulo`) e a regex exige maiúscula depois do espaço; páginas omitidas.
- Correção: `CHAGAS, Sílvio Donizete (org.). Lições de direito civil alternativo. São Paulo: Acadêmica, 1994. 164 p.`

**27. #189 · `ref-a2f0966a0b4a` · defeitos: A, I**
- Como está: `SALAZAR, Carlos Derpic. **El derecho del poder contra el poder…**. Las Casas: Educación para las Ciencias en Chiapas, 2013.`
- Trecho: `Aguascalientes: … Mispat; San Luis Potosí: …; San Cristóbal de Las Casas: …, 2013.`
- Problemas: sobrenome composto partido (`DERPIC SALAZAR, Carlos`); local truncado (`San Cristóbal de Las Casas`); dois pares local/editora desapareceram.
- Correção: `DERPIC SALAZAR, Carlos. El derecho del poder contra el poder: alternativas para afrontar los vicios de la (in)justicia en Bolivia. Aguascalientes: Centro de Estudios Jurídicos y Sociales Mispat; San Luis Potosí: Universidad Autónoma de San Luis Potosí; San Cristóbal de Las Casas: Educación para las Ciencias en Chiapas, 2013.`

**28. #247 · `ref-a9f1cd5a546e` · defeitos: I, D**
- Como está: `INSTITUTO APOIO JURÍDICO POPULAR. **Discriminatória de terras públicas**. Janeiro: AJUP/FASE, 1986.`
- Trecho: `Rio de Janeiro: AJUP/FASE, 1986. Coleção "Socializando conhecimentos" n. 1`
- Correção: `INSTITUTO APOIO JURÍDICO POPULAR. Discriminatória de terras públicas. Rio de Janeiro: AJUP/FASE, 1986. (Socializando conhecimentos, 1).`

**29. #2 · `ref-ce3f5e70ea32` · defeitos: I, D, F**
- Como está: `AGUIRRE, Francisco Ballón; BORRERO, Camilo. **Qualdireito?**. [s.l.]: [s.n.], 1991.`
- Trecho: `Qualdireito?. Rio de Janeiro: AJUP/FASE, set. 1991. Coleção Seminários, n. 16`
- Problemas: o trecho tem **local e editora** e a saída diz `[s.l.: s.n.]` — o `set.` antes do ano quebra a regex; título colado; a interrogação recebe ponto depois (`?**.`).
- Correção: `AGUIRRE, Francisco Ballón; BORRERO, Camilo. Qual direito? Rio de Janeiro: AJUP/FASE, 1991. (Coleção Seminários, 16).` (o original escreve “Qualdireito?”; separar e registrar).

### 3.9. Monografia (1)

**30. #259 · `ref-29ac5a98fcaa` · defeitos: D**
- Como está: `FURMANN, Ivan. **Da Utopia estudantil a Ação Política**. 2003. Monografia – UFPR.`
- Trecho: `… Monografia de Conclusão de Curso - Direito UFPR 2003`
- Problemas: instituição ok, mas sem local, sem curso e com o ano repetido sem os complementos.
- Correção: `FURMANN, Ivan. Da utopia estudantil à ação política. 2003. Monografia (Graduação em Direito) – Universidade Federal do Paraná, [s.l.], 2003.` — ou `Curitiba`, se confirmado na fonte.

### 3.10. Placar da amostra

| Resultado | Itens | % |
|---|---:|---:|
| Conforme a NBR 6023:2018 | 3 | 10,0 |
| Com ao menos um defeito | 27 | 90,0 |
| Com defeito grave (A/T/P/H) | 12 | 40,0 |
| Só com defeito de imprenta/dados/forma | 15 | 50,0 |

---

## 4. Taxa de erro por tipo de defeito

### 4.1. Na amostra (n = 30)

| Código | Defeito | Itens | % |
|---|---|---:|---:|
| D | Páginas, volume, número, edição, curso, tradução | 18 | 60,0 |
| I | Imprenta (local/editora/instituição) | 13 | 43,3 |
| F | Forma (pontuação, caixa, destaque, espaço, `a`/`b`) | 12 | 40,0 |
| T | Título | 6 | 20,0 |
| P | Tipo/suporte | 6 | 20,0 |
| A | Autoria | 5 | 16,7 |
| H | Placeholder | 5 | 16,7 |

Um item pode acumular códigos; a soma não dá 100%.

**Por tipo de publicação** (defeito grave / itens do tipo):

| Tipo | Graves | Total | % |
|---|---:|---:|---:|
| Capítulo | 4 | 4 | 100 |
| Tese | 1 | 1 | 100 |
| Legislação | 1 | 1 | 100 |
| Documento | 1 | 1 | 100 |
| Artigo | 3 | 6 | 50,0 |
| Dissertação | 1 | 2 | 50,0 |
| Livro | 1 | 13 | 7,7 |
| Monografia | 0 | 1 | 0 |
| Relatório | 0 | 1 | 0 |

Leitura: **livro é o formato em melhor estado** (o defeito restante é quase
sempre imprenta/dados); **capítulo continua 100% quebrado**; artigo e
pós-graduação dependem de o extrator ter classificado o tipo certo.

### 4.2. No conjunto `alta` (n = 221) e no documento (n = 606)

| Achado | Em `alta` | % de 221 | No doc | % de 606 |
|---|---:|---:|---:|---:|
| `[s.l.]` impresso | 51 | 23,1 | 202 | 33,3 |
| … desses, com local no `trecho` (falso) | 35 | 15,8 | — | — |
| `[s.l.]: [s.n.]` | 47 | 21,3 | 197 | 32,5 |
| Local truncado por partícula (“Janeiro”, “Las Casas”) | 15 | 6,8 | 22 | 3,6 |
| Local = título (“Direito Processual Penal”) | 2 | 0,9 | 2 | 0,3 |
| Capítulo com `In: [coletânea]` | 30 | 13,6 | 39 | 6,4 |
| Artigo com `*[periódico]*` | 8 | 19,0 dos 42 | 15 | 26,3 dos 57 |
| Pós-graduação com instituição no `trecho` e `[s.l.: s.n.]` | 6 | 40% dos 15 | 6 | — |
| `trecho` com `p.` e saída sem página | 27 | 45,8 dos 59 | — | — |
| `trecho` com edição e saída sem edição | 7 | 87,5 das 8 | — | — |
| `trecho` com ano `a`/`b` e saída sem sufixo | 5 | 100% dos 5 | — | — |
| Autor não invertido (`MIGUEL BALDEZ`, `INFORME…`) | 2 | 0,9 | 2 | 0,3 |
| Inversão errada de sobrenome composto (`JÚNIOR`, `SALAZAR`) | 3 | 1,4 | 3 | 0,5 |
| Sobrenome em caixa mista (`Lyra Filho, Roberto`) | 4 | 1,8 | 4 | 0,7 |
| Registro em variante de nome do mesmo autor | 101 | 45,7 | 140 | 23,1 |
| Colisão (autor, ano) sem `a`/`b` | 64 | 29,0 | 135 | 22,3 |
| Duplicata exata (título+autor+ano) | 6 | 2,7 | 6 | 1,0 |
| Quase-duplicata (similaridade ≥ 0,85) | ≥12 | ≥5,4 | ≥12 | ≥2,0 |
| Palavra colada (“compreensãomaterialista”) | ≥21 | ≥9,5 | ≥21 | ≥3,5 |
| Título com mais de 150 caracteres | 13 | 5,9 | 13 | 2,1 |

---

## 5. O que o gerador faz de errado (com a linha do código)

O gerador melhorou: há `autor_abnt()` (linhas 59–79) e `dados_trecho()`
(91–117), e o documento agora reproduz a saída. O problema está nas **regras
de leitura** e nos **ramos de tipo**.

### 5.1. `dados_trecho()` — a raiz dos erros de imprenta

| Linha | Regra atual | Efeito |
|---:|---|---|
| 95–97 | `([A-Z][\wÀ-ÿ]*(?:\s+[A-Z][\wÀ-ÿ]*){0,3}):\s*([^,;]{2,55}),\s*(\d{4})` | o local não aceita partícula: **“Rio de Janeiro” → “Janeiro”** (20 casos), “San Cristóbal de Las Casas” → “Las Casas” |
| 96 | a mesma regex pode começar no meio do título | **“Esquemas de Direito Processual Penal”** virou local em 2 entradas |
| 96–98 | exige `, AAAA` imediatamente após a editora | falha com mês (`jan.-abr.1985`, `set. 1991`): 35 falsos `[s.l.]` em `alta` |
| 100–101 | local/editora vêm do **último** par encontrado | em obra com três editoras, só a última sobrevive |
| 102–104 | fallback `,\s*([A-Z][\w .'-]{2,35}),\s*(\d{4})` | pega texto qualquer antes do ano; não valida contra lista de cidades |
| 105–106 | `p\.\s*([\d]+(?:[-–]\d+)?)` | ok para páginas simples; não pega `p. 23-56` com espaço (`p. 23 - 56`) |
| 108–113 | `v.` e `n.` | ok quando existem, mas só o ramo `artigo` usa |
| 114–116 | `Universidade…|UF[A-Z]{2}|PUC` | **não reconhece `UnB`** (6 de 15 pós-graduações perdem a instituição) |

### 5.2. Ramos de tipo em `abnt()`

| Linha | Ramo | Problema |
|---:|---|---|
| 131–133 | livro | usa local/editora do trecho; se o local falhar e o `veiculo` for cidade, a cidade cai na vaga da editora (a regra permite, embora hoje não ocorra) |
| 134–135 | capítulo | **placeholder fixo `In: [coletânea], %s.`** — descarta organizador, livro, local, editora e páginas; `veiculo` de 19 capítulos é ignorado |
| 136–148 | artigo | monta local/volume/número/páginas (bom), mas aceita cidade como periódico e mantém negrito no título do artigo |
| 149–152 | tese/dissertação/monografia | `%s – %s` com instituição e **sem local, sem curso, sem páginas**; `[s.l.: s.n.]` quando a regex falha |
| 153–154 | legislação | título com `/ano`, sem data, sem ementa, sem veículo oficial |
| 157–158 | relatório | **não usa imprenta nenhuma**; `[Relatório]` redundante |
| 162–163 | URL | `Acesso em` único e global (`ACESSO`, linha 23) para 180 referências, inclusive 74 com link morto |
| 199 | `sort()` | ordena pela string de autor: variantes (`BALDÉZ`/`BALDEZ`, `Roberto Lyra Filho`/`LYRA FILHO, Roberto`) espalham o mesmo autor |
| 254–256 | `lista()` | numeração contínua 1–606 — **corrigido**, preservar |

### 5.3. `autor_abnt()`

- `SUFIXOS` (linha 44) inclui `filho, neto, junior, sobrinho, segundo`, mas a
  regra (73–75) só junta as **duas últimas** palavras. Funciona para
  `LYRA FILHO, Roberto` e falha para `SOUSA JÚNIOR, José Geraldo de`, que
  virou `JÚNIOR, José Geraldo de Sousa` — a partícula “de Sousa” deveria
  ficar com o nome, não com o sobrenome.
- A regra não trata sobrenome composto sem sufixo: `Carlos Derpic Salazar`
  virou `SALAZAR, Carlos Derpic` (correto: `DERPIC SALAZAR, Carlos`).
- Nomes já invertidos com caixa mista (`Lyra Filho, Roberto`) passam
  intactos; convivem com `LYRA FILHO, Roberto` na mesma lista.
- `MIGUEL BALDEZ` (todo em maiúsculas) é devolvido como está (linha 71–72) —
  fica “BALDEZ” sem inversão e sem o prenome separado.

---

## 6. Duplicatas e referências que não deveriam estar na lista

### 6.1. Duplicatas exatas em `alta` (3 grupos, 6 registros)

| Obra | Entradas | Problema |
|---|---:|---|
| HERRERA FLORES, *Los derechos humanos como productos culturales* (2005) | #227 e #230 | mesma obra, editoras “Catarata” e “Libros de la Catarata” |
| PRESSBURGER, *Terras devolutas: o que fazer com elas?* (1990) | #308 e #309 | “com elas” vs “comelas” |
| CAMPILONGO; PRESSBURGER, *Discutindo a assessoria popular* (1991) | #186 e #187 | “aassessoria” vs “a assessoria”; há ainda #361 e #362 (“– II”, 1992), duplicados entre si |

### 6.2. Quase-duplicatas que precisam de decisão humana

| Par | Situação |
|---|---|
| *Serviço de Apoio Jurídico – SAJU* (2003) | #290 e #353: “Serviço” e “Serviçode”, mesma monografia da UFBA |
| *Esquemas de Direito Processual Penal: Introdução* (1961) | #275 e #333: linhas **idênticas**, duplicata que o dedup não pegou |
| *Filosofia jurídica: pequena bibliografia…* (2002) | #276 e #335, mesmo artigo com autor grafado de dois jeitos |
| *Da Utopia estudantil a Ação Política* / *Assessoria jurídica universitária popular…* (2003) | #206 e #259: provável mesma monografia de Ivan Furmann |
| *Anotações sobre Direito Insurgente* (1994) vs *… direito insurgente* (2010) | #163 e #164: reedição ou erro de ano — decidir |
| *Sobre o papel do direito na sociedade capitalista* (1989) | #173 (`BALDÉZ`), #174 (`BALDEZ`) e #143 (sem autor), subtítulos diferentes; colidem na citação |
| *Discriminatória de terras públicas* (1984 e 1986) | #247 e #248, edições diferentes; corrigir “Discriminatóriade” |
| *Solo urbano: propostas para a Constituinte* (1986 e 1996) | #175–#177; corrigir “propostapara” |

### 6.3. O que não é referência bibliográfica

- **#291** — edital de chamada de artigos da Revista do SAJU.
- **#59** — edital de matrícula (documento administrativo, não obra citada).
- **#296** `ARANTES, Paulo. 15/10 – Faculdade de Direito da USP. "1964-2011` — registro de evento com título quebrado.
- **#261** `NORTE, Joaquim das Neves. **(Advogado, 40 anos, pai de 4 filhos… assassinado… em 12 de junho de 1981)` — a “obra” é nota biográfica/homenagem.
- **#287** `MIGUEL BALDEZ. Procurador do Estado do RJ Aposentado…` — idem, mini-biografia truncada em 500 caracteres.
- **#316** `REVISTA DA AATR. Política. São Paulo: Ática, 1982` — três campos colados sem sentido.
- **#234** e **#291** — comunicados editoriais da Revista do SAJU.

### 6.4. Autor confundido com data, frase ou biografia

| Tipo | Registros | Exemplos |
|---|---:|---|
| Autor = “Nome, em DD de mês de AAAA” | 11 | `Roberta Cunha, em 21 de janeiro de 2010`; `Luiz Otávio Ribas, em 1 de janeiro de 2010` |
| Autor = nome + cargo/biografia | 2 | `Marcus Orioni, Professor Livre Docente…`; `MIGUEL BALDEZ. Procurador do Estado…` |
| Título = parágrafo do post | 13 títulos > 150 caracteres | #198 (`I. Em meia hora a reunião começaria…`) e #294 (`Reunidos nos dias 8 e 9 de dezembro de 2011…`) |
| Autor = fragmento de frase | 1 | `À Classe Trabalhadora, e` (hoje #371) |

As 11 datas são a assinatura de post do Blogspot (“Por Fulano, em 21 de
janeiro de 2010”) lida como campo autor. Correção no extrator: rejeitar
`,\s*em\s+\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s*$` em `separa_autor`.

---

## 7. NBR 10520:2023 — o que falta para citar

1. **Sem `a`/`b` para autor+ano repetido.** 21 grupos e 64 registros em
   `alta`; 135 no documento. BALDEZ tem três obras em 1989 e duas em 1991, e
   a citação `(BALDEZ, 1989)` não distingue. O `trecho` já traz `1989a`,
   `1991b`, `1989f`; o gerador descarta o sufixo (5 casos em `alta`).
2. **Citação sem autor.** O documento já começa pelo título (243 entradas) —
   está certo. Falta declarar a forma: `(EDITAL DE INSCRIÇÃO…, 2013)`.
3. **`[s.d.]` sem regra.** 284 registros sem ano; a citação correta é
   `(AUTOR, [s.d.])`, e isso precisa estar escrito.
4. **Sem páginas, não há citação direta.** 27 referências `alta` têm página
   no `trecho` e não na saída; citação direta exige `(AUTOR, ano, p. X)`.
5. **Sem forma de citação publicada.** Falta o par autor–ano ao lado de cada
   entrada; hoje o leitor não sabe se cita `LYRA FILHO, 1982` ou
   `ROBERTO LYRA FILHO, 1982`.
6. **Legislação.** `(BRASIL, 2024)` não distingue os decretos listados; a
   prática é citar pelo número (`Decreto nº 11.995/2024`) ou adotar
   `2024a`, `2024b`. O documento precisa escolher e declarar.
7. **Mais de três autores.** A NBR 6023 admite `et al.`; a NBR 10520 usa
   `et al.` na citação. A lista traz todos os autores em #5 (6 autores) e
   #184 (4), e nomes incompletos em outros (`PRESSUBURGER, T. Miguel`), sem
   critério declarado.

---

## 8. Recomendações para `etl/monta-referencias-abnt.py`

### P0 — corrige os defeitos que mais aparecem

1. **Local com partícula.** Trocar o grupo do local por algo que aceite
   `de/da/do/das/dos`:
   `([A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*(?:\s+(?:de|da|do|das|dos|e)?\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÀ-ÿ]*){0,4}):`.
   Sem isso, “Rio de Janeiro” continua saindo “Janeiro” (20 entradas).
2. **Ano com mês.** Aceitar `(?:[a-z]{3}\.?\s*-?\s*[a-z]{3}\.?)?\s*(\d{4})`
   depois da editora. Recupera os 35 falsos `[s.l.]` de `alta`.
3. **Validar o local contra lista de cidades/UF.** Se o candidato não estiver
   na lista (ou tiver cara de título, como “Esquemas de Direito Processual
   Penal”), descartar e usar `[s.l.]`. Melhor lacuna do que cidade inventada.
4. **Instituição:** ampliar a regex (linha 114) para
   `UnB|UF[A-Z]{2}|UFRJ|UFRGS|USP|Unicamp|Unesp|PUC[\w-]*|Universidade…|Faculdade…`.
   Hoje 6 de 15 pós-graduações perdem a instituição.
5. **Pós-graduação:** emitir
   `Ano. N f. Tipo (Curso) – Instituição, Local, ano.` usando páginas,
   curso e local do `trecho`. `Tipo – Instituição.` sem local não fecha.
6. **Capítulo:** montar
   `AUTOR. Título. In: ORGANIZADOR (org.). *Título do livro*. Local: Editora, ano. p. x-y.`
   a partir de `veiculo`/`trecho`. Se faltar o livro, `In: [título do livro
   não identificado].` — `[coletânea]` não identifica nada.
7. **Relatório:** usar imprenta como livro
   (`Local: Editora, ano`) e remover `[Relatório]` quando o título já diz.
8. **Páginas, volume, número, edição:** emitir sempre que existirem no
   `trecho` — inclusive no capítulo (27 páginas perdidas, 7 edições).
9. **Sufixo `a`/`b`:** ler do `trecho` (`1991b`) e, quando não houver,
   gerar por colisão de `(autor_normalizado, ano)` em ordem de título.
10. **Autoria:** corrigir a regra de sufixo (linha 73–75) para
    `SOUSA JÚNIOR, José Geraldo de`; tratar sobrenome composto
    (`Derpic Salazar`, `Fals Borda`, `Lyra Filho`); normalizar caixa do
    sobrenome (sempre maiúsculas) para `Lyra Filho, Roberto` e
    `Roberto Lyra Filho` caírem na mesma chave.
11. **Chave de ordenação canônica** (linha 199): ordenar por
    `sem_acento(sobrenome)+"|"+sem_acento(nome)`, com aliases
    (`BALDÉZ`→`BALDEZ`, `PRESSUBURGER`→`PRESSBURGER`). Sem isso, 101
    registros continuam fora de lugar e o mesmo autor em duas letras.
12. **Dedup por chave sem espaços:**
    `re.sub(r"[^a-z0-9]", "", sem_acento(titulo+autor+ano))`. É o que pega
    “comelas/com elas” e “aassessoria/a assessoria”. Só remover
    automaticamente quando autor **e** ano coincidirem; o resto vai para
    “revisar”.
13. **Destaque:** um padrão por referência. Negrito no título do livro;
    itálico no título do periódico; **nada** no título do artigo/capítulo.
14. **Título:** cortar imprenta colada (`\s+\d+\s*ed\.,`, `,\s*[A-Z][a-z]+:`),
    não terminar com ponto quando o título já termina em `?`/`!`, e recusar
    títulos com mais de ~200 caracteres (13 casos).
15. **`Acesso em`:** data por referência, não constante global; 74 links
    mortos carregam “Acesso em: 22 nov. 2026” como se tivessem sido abertos.

### P1 — consistência editorial

- Normalizar `n.` → `nº` na legislação e o número com separador de milhar
  (`Lei n. 8629/93` → `Lei nº 8.629, de 25 de fevereiro de 1993`).
- Padronizar `Em:` → `In:`.
- Corrigir ou sinalizar palavras coladas (≥21 registros) — a origem é a
  junção de nós de texto no extrator.
- Remover resíduos (`*` após nome, `(Org.)` vs `(org.)`).
- Separar “Referências” de “Fontes e documentos consultados” (editais,
  blogs, páginas institucionais).
- Emitir ao lado de cada entrada a forma de citação
  `(SOBRENOME, ano)` / `(SOBRENOME, ano, p. X)`.

### P2 — qualidade do documento

- Índice por letra e âncoras estáveis (`#lyra-filho-roberto`).
- Relatório de QA no fim do arquivo: quantos `[s.l.]`, `[s.n.]`,
  `[coletânea]`, `a`/`b`, duplicatas sugeridas.
- Recalcular o quadro de números na mesma execução do corpo (hoje está
  coerente; garantir que continue).

### Correções no extrator (`etl/extrai-referencias.py`)

| Onde | Problema | Correção |
|---|---|---|
| linha 563 `titulo[:500]` | corta no meio da palavra (3 casos) | cortar em limite de frase e rebaixar a confiança |
| linha 621 `[^,.]{0,90}` em `extrai_veiculo` | veículo cortado em “resp”, “Legislativ”, “Minas Ge” | parar em limite de palavra |
| linhas 193/205 `"".join(partes)` | palavras coladas (“JustiçaJudiciária”) | juntar nós inline com separador de espaço |
| `separa_autor` | aceita byline (“… em 21 de janeiro de 2010”) | rejeitar autor com data/cargo |
| `tenta_ref` | aceita parágrafo narrativo como título | exigir título ≤ 200 chars; rejeitar início “I.”, “Reunidos…” |
| `extrai_veiculo` | cidade vira periódico (`Bilbao`, `Cochabamba`) | lista de cidades → campo `local` |

---

## 9. Como revalidar (proposta de verificação determinística)

Sugiro um `etl/audita-referencias-abnt.py` (não criado nesta revisão) que
leia o Markdown e o JSON e falhe com código ≠ 0 quando:

| Verificação | Limite aceitável |
|---|---|
| cidade que é sufixo de um local maior (`Janeiro`, `Las Casas`) | 0 |
| `[s.l.]` com local presente no `trecho` | 0 |
| `[s.l.: s.n.]` com editora presente no `trecho` | 0 |
| capítulo com `[coletânea]` | 0 |
| pós-graduação sem instituição quando o `trecho` tem | 0 |
| `trecho` com `p.` e saída sem `p.` | 0 |
| `trecho` com edição e saída sem edição | 0 |
| `trecho` com `a`/`b` e saída sem sufixo | 0 |
| autor pessoal sem vírgula (não invertido) | 0 |
| inversão de sufixo (`JÚNIOR,` ou `NETO,` no início da entrada) | 0 |
| mesmo nome em mais de uma grafia | 0 |
| duplicata por título+autor+ano (sem espaços) | 0 |
| título > 200 caracteres | 0 |
| números de entrada repetidos | 0 |
| números do cabeçalho × corpo | iguais |

Enquanto esses limites não forem zero, o documento não deve ser apresentado
como “referências em ABNT”: são **pistas de referência** para revisão humana.
A fatia com menos retrabalho é a de livros cujo `trecho` traz local e editora
sem partícula no nome da cidade.

---

## 10. O que esta revisão não fez

- Não editou `docs/referencias-abnt.md`, `docs/referencias-por-tema.md`,
  `docs/referencias-por-autor.md`, `dados/*.json` nem o gerador.
- Não conferiu autoria, data ou editora em fonte externa (catálogo, Open
  Library, Planalto). As correções usam o `trecho` como prova; onde ele não
  basta, o item está marcado como pendente.
- Não julgou os 236 registros de confiança baixa nem os 149 de média, além do
  que apareceu por contaminação (duplicatas e variantes de nome).
- Não mediu tempo de execução nem custo: a revisão é local e de custo zero.
