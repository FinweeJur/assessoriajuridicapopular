# Revisão ABNT das referências de confiança alta

> **Data:** 22/11/2026
> **Objeto:** `docs/referencias-abnt.md` (606 registros), com conferência em
> `dados/referencias.json`, `docs/referencias-por-tema.md`,
> `docs/referencias-por-autor.md` e `docs/REFERENCIAS-PILOTO.md`.
> **Normas:** ABNT NBR 6023:2018 (referências) e NBR 10520:2023 (citações).
> **Gerador avaliado:** `etl/monta-referencias-abnt.py` (função `abnt()`,
> linhas 58–90).
> **Escopo desta revisão:** 30 referências de confiança `alta` (amostra
> estratificada), mais medições automáticas nos 221 registros `alta`.
> **Nada foi alterado** em `docs/referencias-abnt.md`, nos JSON de `dados/`
> nem no gerador. Sem commit.

---

## 1. Resumo

1. **Nenhuma das 30 referências da amostra está conforme a NBR 6023:2018.**
   16 delas (53,3%) têm defeito grave — autoria, título, tipo ou placeholder
   que impede identificar a obra.
2. O defeito dominante é de **imprenta**: o gerador imprime `[s.l.]` em 76
   referências cujo próprio `trecho` registra o local e a editora
   (`Rio de Janeiro: Paz e Terra, 1983`). Isso não é lacuna da fonte — é
   descarte de dado que já estava extraído.
3. **Imprenta, páginas, volume, número, edição e instituição nunca chegam à
   saída.** Dos 221 registros `alta`: 59 têm `p.` no `trecho` e nenhum traz
   página; 30 artigos têm `v.`/`n.` e nenhum traz volume; 15 trabalhos de
   pós-graduação citam a universidade no `trecho` e os 15 saem como
   `[instituição não identificada]`.
4. **A lista não está em ordem alfabética utilizável.** 48 registros `alta`
   têm nome pessoal em ordem natural (`Roberto Lyra Filho`) e 101 pertencem a
   variantes do mesmo nome (`LYRA FILHO, Roberto` / `Lyra Filho, Roberto` /
   `Roberto Lyra Filho`), o que espalha o mesmo autor por duas ou três letras.
5. O gerador **não implementa a NBR 10520:2023**: não há sufixo `a`/`b` para
   autor+ano repetido (21 grupos, 64 registros em `alta`), usa
   `AUTOR NÃO IDENTIFICADO` (proibido: a entrada começa pelo título) e não
   oferece a forma de citação no texto.
6. O **cabeçalho do documento não bate com o corpo**: anuncia
   “57 abertos / 0 restritos / 40 mortos / 83 não verificados”, mas o corpo
   tem 102 “Disponível aqui”, 4 “Link restrito”, 74 “link não respondeu” e
   zero “não verificado”. A frase “106 de 177 URLs” também não fecha com as
   180 referências com URL.

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

A confiança é heurística do extrator, não revisão humana (`REFERENCIAS-PILOTO.md`,
seção 5). Por isso a amostra foi tirada **só** de `alta`: é o subconjunto que
o próprio documento apresenta como pronto para citar.

### 2.2. Desenho da amostra

Amostra estratificada por `tipo`, com seleção aleatória dentro de cada estrato
e semente fixa `20261122` (reprodutível). Cotas proporcionais ao peso de cada
tipo em `alta`, com piso de 1 para tipos pequenos:

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
| obra | 1 | 0 (fora da amostra) |
| **Total** | **221** | **30** |

Cada item foi conferido em três níveis: (a) a linha publicada em
`docs/referencias-abnt.md`; (b) os campos `autor`, `titulo`, `ano`,
`veiculo`, `url`, `tipo` no JSON; (c) o `trecho`, que é a evidência textual
do post. A correção proposta usa **apenas o que está no `trecho`**; quando o
`trecho` não tem o dado (por exemplo, a data do Decreto nº 11.995/2024), a
correção fica marcada como pendente de conferência, sem invenção.

Conferi também que a linha publicada é exatamente o que a função `abnt()`
produz hoje: 370 linhas numeradas do corpo, 0 divergências. O que está no
arquivo é o que o código gera.

### 2.3. Códigos de defeito

| Código | Defeito |
|---|---|
| **A** | Autoria: não invertida, malformada, autor que não é autor, autor apenas inferido |
| **T** | Título: absorveu imprenta/evento/editora, é parágrafo, truncado ou tem resíduo de marcação |
| **P** | Tipo/suporte errado (artigo × capítulo × livro × evento) ou item que não é referência bibliográfica |
| **I** | Imprenta: local/editora/instituição omitidos apesar de constarem no `trecho`; local na vaga da editora |
| **D** | Dados complementares omitidos: páginas, volume, número, edição, coleção, curso, tradução |
| **H** | Placeholder interno: `[obra coletiva]`, `[periódico não identificado]`, `[instituição não identificada]` |
| **F** | Forma: pontuação, caixa, destaque (negrito/itálico), espaço colado, truncamento, sufixo `a`/`b` do ano |

**Grave** = A, T, P ou H. **Não grave** = I, D, F.

### 2.4. Limites

- Não abri os HTML originais nem a fonte externa: a conferência é
  documento × JSON × `trecho`.
- A NBR 6023:2018 e a NBR 10520:2023 foram aplicadas de memória técnica, sem
  consulta ao texto pago da norma; onde a redação admite mais de uma prática
  (por exemplo, indicar ou não a primeira edição), a revisão registra a
  divergência em vez de decretar erro.
- Amostra de 30 sobre 221: as porcentagens têm margem ampla (ordem de ±15
  pontos). As medições automáticas da seção 4.2 não têm essa margem, porque
  cobrem os 221.

---

## 3. As 30 referências comentadas

O bloco “como está” reproduz a linha do documento (negrito e itálico
preservados). O número é o **número da entrada em `docs/referencias-abnt.md`**
— atenção: o apêndice de confiança baixa reinicia a numeração em 1, então
“#52” e “#52 do apêndice” são coisas diferentes.

### 3.1. Artigo (6)

**1. #341 · `ref-5eeef921ef11` · defeitos: A, I, D, F**
- Como está: `Roberto Lyra Filho. **Normas jurídicas e outras normas sociais**. *Revista Direito e Avesso*, 1982.`
- Trecho: `Normas jurídicas e outras normas sociais, Revista Direito e Avesso, n. 1, Brasília, 1982, p. 49-60.`
- Problemas: autor em ordem natural (não alfabetiza em L); `Brasília`, `n. 1` e `p. 49-60` existem no trecho e desapareceram; negrito no título do artigo (o destaque deve recair sobre o periódico).
- Correção: `LYRA FILHO, Roberto. Normas jurídicas e outras normas sociais. Revista Direito e Avesso, Brasília, n. 1, p. 49-60, 1982.`

**2. #291 · `ref-6b9154d2ebd9` · defeitos: A, T, P**
- Como está: `O Conselho Editorial. **REVISTA DO SAJU - EDITAL DE CHAMADA DE ARTIGOS. O Serviço de Assessoria Jurídica da Universidade Federal do Rio Grande do Sul (SAJU-UFRGS) vem informar que está aberto o período de seleção…**. *[periódico não identificado]*, 2012.`
- Problemas: não é artigo, é edital de chamada; “O Conselho Editorial” é órgão, não autor; o título é o texto do edital inteiro; autoria institucional disponível no próprio trecho foi descartada.
- Correção: retirar da lista de referências (vai para “documentos e comunicações”) ou, se mantido: `SERVIÇO DE ASSESSORIA JURÍDICA (UFRGS). Edital de chamada de artigos para o v. 7, n. 2. Porto Alegre, 2012.`

**3. #263 · `ref-7bdc688ec44b` · defeitos: T, P, I**
- Como está: `KOPITTKE, Alberto Liebling. **Introdução a teoria e prática dialética no direito brasileiro: a experiência da Renap**. *Renap. São Paulo*, 2010.`
- Trecho: `… São Paulo: Expressão Popular, 2010, p. 21.`
- Problemas: é livro, não artigo; `Renap. São Paulo` virou “periódico” — é título de livro + cidade colados; local e editora (`São Paulo: Expressão Popular`) estão no trecho e foram perdidos.
- Correção: `KOPITTKE, Alberto Liebling. Introdução à teoria e prática dialética no direito brasileiro: a experiência da Renap. São Paulo: Expressão Popular, 2010.` (o “a teoria” do original parece erro de digitação da fonte; registrar, não corrigir em silêncio).

**4. #239 · `ref-7f7c87daffec` · defeitos: I, D, F**
- Como está: `INSTITUTO APOIO JURÍDICO POPULAR. **Boletim Informativo do Instituto Apoio Jurídico Popular - Responsabilidade de quem? (ação de responsabilidade civil)**. *Boletim Informativo do Instituto Apoio Jurídico Popular - Responsabilidade de quem? (ação de resp*, 1992.`
- Trecho: `… Rio de Janeiro, n.4, Coletivo de Juristas Populares, jul.-ago. 1992.`
- Problemas: o mesmo texto aparece como título e como veículo; o veículo está **truncado no meio de “resp”** (limite do regex `[^,.]{0,90}` no extrator); `n. 4`, `jul.-ago.` e a editora foram perdidos.
- Correção: `Responsabilidade de quem? (ação de responsabilidade civil). Boletim Informativo do Instituto Apoio Jurídico Popular, Rio de Janeiro, n. 4, jul.-ago. 1992.` (artigo não assinado: a entrada começa pelo título).

**5. #231 · `ref-b061f28b2214` · defeitos: T, P, D, H**
- Como está: `HERRERA FLORES, Joaquín. **Reflexión en torno al concepto de derechos humanos. Jornadas Internacionales sobre derechos humanos, 5-7 dez. 1998, Granada, Asociación Pro Derechos Humanos de Andalucía, 1999**. *[periódico não identificado]*, 1999.`
- Problemas: é trabalho em evento, não artigo de periódico; o título absorveu nome do evento, datas, cidade, editora e ano; páginas `11-35` ignoradas.
- Correção: `HERRERA FLORES, Joaquín. Reflexión en torno al concepto de derechos humanos. In: JORNADAS INTERNACIONALES SOBRE DERECHOS HUMANOS, 1998, Granada. [Anais…]. Granada: Asociación Pro Derechos Humanos de Andalucía, 1999. p. 11-35.`

**6. #298 · `ref-f074f6a25055` · defeitos: D, F**
- Como está: `PAZELLO, Ricardo Prestes. **Teorias críticas do direito e assessoria jurídica popular**. *Revista Direitos Humanos e Sociedade*, 2019.`
- Trecho: `… v. 2, p. 141-161, 2019.`
- Problemas: único defeito é o volume e as páginas terem sido descartados; e o negrito no título do artigo (dupla marcação com o periódico em itálico).
- Correção: `PAZELLO, Ricardo Prestes. Teorias críticas do direito e assessoria jurídica popular. Revista Direitos Humanos e Sociedade, v. 2, p. 141-161, 2019.`
- **É a referência mais próxima do correto em toda a amostra** — e ainda assim falha em dois pontos.

### 3.2. Capítulo (4)

**7. #277 · `ref-4b6d1484cbf9` · defeitos: T, P, D, F**
- Como está: `Lyra Filho, Roberto. **Introdução ao Direito como ciência social", In: Revista brasileira de filosofia**. In: [obra coletiva], 1973.`
- Problemas: é artigo de periódico, não capítulo; o título carrega `", In: Revista brasileira de filosofia` — resíduo de HTML/citação; `v. 23, n. 90, p. 180-185` ignorados; `In: [obra coletiva]` não é referência.
- Correção: `LYRA FILHO, Roberto. Introdução ao Direito como ciência social. Revista Brasileira de Filosofia, v. 23, n. 90, p. 180-185, abr./jun. 1973.`

**8. #222 · `ref-955b140f5945` · defeitos: I, D, H**
- Como está: `HERRERA FLORES, Joaquín. **La fundamentación de los derechos humanos desde la Escuela de Budapest**. In: [obra coletiva], 1995.`
- Trecho: `Em: THEOTONIO, Vicente; PRIETO, Fernando (Coord.). Los Derechos Humanos: una reflexión interdisciplinar: Seminário de Investigación Francisco Suárez. Córdoba: Etea, 1995, p. 23-56.`
- Problemas: organizadores, título do livro, local, editora e páginas estavam todos no trecho e foram trocados por um placeholder.
- Correção: `HERRERA FLORES, Joaquín. La fundamentación de los derechos humanos desde la Escuela de Budapest. In: THEOTONIO, Vicente; PRIETO, Fernando (coord.). Los Derechos Humanos: una reflexión interdisciplinar. Córdoba: Etea, 1995. p. 23-56.`

**9. #273 · `ref-af0626a77fe1` · defeitos: T, P, D, F**
- Como está: `Lyra Filho, Roberto. **Acriminologia Dialética em ação", In: Notícia do Direito Brasileiro**. In: [obra coletiva], 1971.`
- Trecho: `"Acriminologia Dialética em ação", In: Notícia do Direito Brasileiro, p. 193-198 1971.`
- Problemas: mesmo padrão do item 7; “Acriminologia” parece “A criminologia” com o artigo colado no A.
- Correção: `LYRA FILHO, Roberto. A criminologia dialética em ação. Notícia do Direito Brasileiro, p. 193-198, 1971.` (confirmar o título na fonte antes de publicar).

**10. #184 · `ref-cd72d4852aa1` · defeitos: A, I, D, H**
- Como está: `BONILLA, Victor D; CASTILLO, Gonzalo; BORDA, Orlando Fals; LIBREROS, Augusto. **Causa popular, ciência popular. Uma metodologia…**. In: [obra coletiva], 1999.`
- Trecho: `In: BRANDÃO, Carlos Rodrigues. Repensando a pesquisa militante. São Paulo: Brasiliense, 1999.`
- Problemas: `BORDA, Orlando Fals` — o sobrenome composto é **Fals Borda** (inversão errada); organizador, livro, local e editora no trecho e descartados; o original separa título e subtítulo por ponto, e a NBR usa dois-pontos.
- Correção: `BONILLA, Victor D.; CASTILLO, Gonzalo; FALS BORDA, Orlando; LIBREROS, Augusto. Causa popular, ciência popular: uma metodologia do conhecimento científico através da ação. In: BRANDÃO, Carlos Rodrigues. Repensando a pesquisa militante. São Paulo: Brasiliense, 1999.`

### 3.3. Dissertação (2)

**11. #207 · `ref-a2b260b2f81d` · defeitos: I, D, H, F**
- Como está: `GÓES JUNIOR, José Humberto de. **Da pedagogia do oprimido ao direito do oprimido…**. 2008. Dissertação – [instituição não identificada], [s.l.].`
- Trecho: `… Dissertação (Mestrado em Ciências Jurídicas) – Universidade Federal da Paraíba, João Pessoa, 2008, 189 p.`
- Problemas: curso, instituição, cidade e páginas constavam e viraram placeholder; o ano aparece duas vezes (aceitável na NBR, mas só se a segunda vier acompanhada de instituição e local).
- Correção: `GÓES JUNIOR, José Humberto de. Da pedagogia do oprimido ao direito do oprimido: uma noção de direitos humanos na obra de Paulo Freire. 2008. 189 f. Dissertação (Mestrado em Ciências Jurídicas) – Universidade Federal da Paraíba, João Pessoa, 2008.`

**12. #202 · `ref-bf0edf80d1cc` · defeitos: A, I, D, H**
- Como está: `Flávia Carlet. **Advocacia popular…**. 2010. Dissertação – [instituição não identificada], [s.l.].`
- Trecho: `… Dissertação (Mestrado em Direito) - UnB, Brasília, 2010.`
- Problemas: autora em ordem natural; UnB e Brasília no trecho e descartados; curso omitido.
- Correção: `CARLET, Flávia. Advocacia popular: práticas jurídicas e sociais no acesso ao direito e à justiça aos movimentos sociais de luta pela terra. 2010. Dissertação (Mestrado em Direito) – Universidade de Brasília, Brasília, 2010.`

### 3.4. Monografia (1)

**13. #259 · `ref-29ac5a98fcaa` · defeitos: A, I, D, H**
- Como está: `Ivan Furmann. **Da Utopia estudantil a Ação Política**. 2003. Monografia – [instituição não identificada], [s.l.].`
- Trecho: `Ivan Furmann Da Utopia estudantil a Ação Política Monografia de Conclusão de Curso - Direito UFPR 2003`
- Problemas: nome natural; UFPR e o curso (`Direito`) estão no trecho; a cidade não está (não inventar).
- Correção: `FURMANN, Ivan. Da utopia estudantil à ação política. 2003. Monografia (Graduação em Direito) – Universidade Federal do Paraná, [s.l.], 2003.` — ou `Curitiba`, se confirmado na fonte.

### 3.5. Tese (1)

**14. #262 · `ref-3f7fc449f6a0` · defeitos: A, I, D, H**
- Como está: `José Geraldo de Sousa Júnior. **Direito como liberdade…**. 2008. Tese – [instituição não identificada], [s.l.].`
- Trecho: `… Tese (Doutorado em Direito) - UnB, Brasília, 2008.`
- Correção: `SOUSA JÚNIOR, José Geraldo de. Direito como liberdade: o Direito Achado na Rua: experiências populares emancipatórias de criação do Direito. 2008. Tese (Doutorado em Direito) – Universidade de Brasília, Brasília, 2008.`

### 3.6. Legislação (1)

**15. #52 · `ref-7f06cbfefccd` · defeitos: T, D, F**
- Como está: `BRASIL. **Decreto nº 11.995/2024**. 2024. Disponível em: <https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/decreto/d11995.htm>. Acesso em: 22 nov. 2026.`
- Problemas: `nº 11.995/2024` não é o título oficial — falta a data (“de 25 de outubro de 2024”) e a ementa; o ano aparece dentro do título e solto depois; o trecho só tem `Decreto nº 11.995/2024`, então data e ementa **precisam ser conferidas no link**, não deduzidas.
- Correção: `BRASIL. Decreto nº 11.995, de 25 de outubro de 2024. [Ementa oficial]. Brasília, DF: Presidência da República, 2024. Disponível em: <…>. Acesso em: 22 nov. 2026.` (data e ementa pendentes de conferência).

### 3.7. Relatório (1)

**16. #252 · `ref-fd13093af167` · defeitos: I, F**
- Como está: `INSTITUTO APOIO JURÍDICO POPULAR. **Relatório 1992-1993**. 1993. [Relatório].`
- Trecho: `… Rio de Janeiro: AJUP, 1993.`
- Problemas: local e editora no trecho e perdidos; `[Relatório]` é redundante quando o título já diz “Relatório”.
- Correção: `INSTITUTO APOIO JURÍDICO POPULAR. Relatório 1992-1993. Rio de Janeiro: AJUP, 1993.`

### 3.8. Documento (1)

**17. #59 · `ref-0e6a0c487e2e` · defeitos: A, P**
- Como está: `AUTOR NÃO IDENTIFICADO. **EDITAL DE INSCRIÇÃO, SELEÇÃO E MATRÍCULA - N. 013/2013**. 2013. Disponível em: <https://www.goias.ufg.br/…>. Acesso em: 22 nov. 2026.`
- Problemas: `AUTOR NÃO IDENTIFICADO` não é forma aceita — sem autor, a entrada começa pelo título; sendo edital, a autoria é institucional (o host e o caminho indicam UFG, mas isso é inferência: confirmar); o título é o assunto do edital, não o título do documento.
- Correção: `UNIVERSIDADE FEDERAL DE GOIÁS. Edital de inscrição, seleção e matrícula n. 013/2013. Goiânia, 2013. Disponível em: <…>. Acesso em: 22 nov. 2026.` (confirmar autoria e cidade).

### 3.9. Livro (13)

**18. #260 · `ref-08419286e0ba` · defeitos: I, D, F**
- Como está: `JEAMMAUD, Antoine. **Proposta para uma compreensãomaterialista do direito do trabalho**. [s.l.: s.n.], 1985.`
- Trecho: `… Rio de Janeiro: CPT-RJ, jan.-abr.1985. Coleção Seminários, n. 4`
- Problemas: `[s.l.: s.n.]` falso — o trecho tem local e editora; “compreensão materialista” está colado; coleção omitida.
- Correção: `JEAMMAUD, Antoine. Proposta para uma compreensão materialista do direito do trabalho. Rio de Janeiro: CPT-RJ, 1985. (Coleção Seminários, 4).`

**19. #205 · `ref-0bb524e3e61d` · defeitos: I, D**
- Como está: `FREIRE, Paulo. **Pedagogia do oprimido**. [s.l.]: Paz e Terra, 1983.`
- Trecho: `12. ed. Rio de Janeiro: Paz e Terra, 1983.`
- Problemas: `[s.l.]` falso; a edição (`12. ed.`) existe e foi descartada. É o caso clássico: o gerador só sabe preencher a vaga da editora.
- Correção: `FREIRE, Paulo. Pedagogia do oprimido. 12. ed. Rio de Janeiro: Paz e Terra, 1983.`

**20. #233 · `ref-121b7ea6dfb8` · defeitos: I, D, F**
- Como está: `HERRERA RIVAS, Alícia. **Crise da JustiçaJudiciária**. [s.l.: s.n.], 1984.`
- Trecho: `Rio de Janeiro: CPT-RJ, jan.-abr.1984. Coleção Seminários, n. 1`
- Correção: `HERRERA RIVAS, Alícia. Crise da Justiça Judiciária. Rio de Janeiro: CPT-RJ, 1984. (Coleção Seminários, 1).`

**21. #280 · `ref-257cff7f87fb` · defeitos: I, D**
- Como está: `MALHEIRO, Bruno; PORTO-GONÇALVES, Carlos Walter; MICHELOTTI, Fernando. **Horizontes amazônicos…**. [s.l.]: Fundação Rosa Luxemburgo; Expressão Popular, 2021.`
- Trecho: `1a. São Paulo: Fundação Rosa Luxemburgo; Expressão Popular, 2021.`
- Problemas: `[s.l.]` falso; `1a.` deveria ser `1. ed.` — e, pela NBR, a primeira edição não precisa ser indicada.
- Correção: `MALHEIRO, Bruno; PORTO-GONÇALVES, Carlos Walter; MICHELOTTI, Fernando. Horizontes amazônicos: para repensar o Brasil e o mundo. São Paulo: Fundação Rosa Luxemburgo; Expressão Popular, 2021.`

**22. #357 · `ref-3f0e5edf81e1` · defeitos: I**
- Como está: `SCHMITT, Carl. **Teologia política**. [s.l.]: Del Rey, 2006.`
- Trecho: `Belo Horizonte: Del Rey, 2006.`
- Correção: `SCHMITT, Carl. Teologia política. Belo Horizonte: Del Rey, 2006.`

**23. #363 · `ref-6d9a3c02f4ac` · defeitos: I, D**
- Como está: `STUCKA, Petr Ivanovich. **Direito e luta de classes: teoria geral do direito**. [s.l.]: Acadêmica, 1988.`
- Trecho: `Tradução de Sílvio Donizete Chagas. São Paulo: Acadêmica, 1988, 176 p.`
- Problemas: local e tradutor descartados — a tradução é elemento obrigatório quando indicada na fonte.
- Correção: `STUCKA, Petr Ivanovich. Direito e luta de classes: teoria geral do direito. Tradução de Sílvio Donizete Chagas. São Paulo: Acadêmica, 1988. 176 p.`

**24. #228 · `ref-77a0e723eaa2` · defeitos: I**
- Como está: `HERRERA FLORES, Joaquín. **Los derechos humanos desde la escuela de Budapeste**. [s.l.]: Tecnos, 1989.`
- Trecho: `Madrid: Tecnos, 1989.`
- Correção: `HERRERA FLORES, Joaquín. Los derechos humanos desde la escuela de Budapeste. Madrid: Tecnos, 1989.`

**25. #166 · `ref-8144ecaea7fd` · defeitos: I, F**
- Como está: `BALDEZ, Miguel Lanzellotti. **Conselhos Populares e usucapião especial urbano**. [s.l.]: Centro de Direitos Humanos, 1991.`
- Trecho: `Petrópolis: Centro de Direitos Humanos, 1991b.`
- Problemas: local perdido; **o `b` do ano desapareceu** — sem ele, esta obra colide com as outras de BALDEZ em 1991 e a citação no texto fica ambígua.
- Correção: `BALDEZ, Miguel Lanzellotti. Conselhos Populares e Usucapião Especial Urbano. Petrópolis: Centro de Direitos Humanos, 1991b.` (o sufixo só vale se existir `1991a` do mesmo autor; o dado está no trecho e foi descartado).

**26. #348 · `ref-93defba6bce0` · defeitos: A**
- Como está: `Roberto Lyra Filho. **Problemas atuais do ensino jurídico**. [s.l.]: Obreira, 1981.`
- Trecho: `Problemas atuais do ensino jurídico. Brasília: Obreira, 1981.`
- Problemas: ordem natural; e **o autor não está no trecho** — foi inferido do título da página (“Lista de textos de Roberto Lyra Filho”). O `REFERENCIAS-PILOTO.md` documenta essa inferência, mas ela precisa aparecer na entrada.
- Correção: `LYRA FILHO, Roberto. Problemas atuais do ensino jurídico. Brasília: Obreira, 1981.` + nota de rodapé “autoria atribuída pela lista da página de origem”.

**27. #194 · `ref-a0c16ed4dd65` · defeitos: I**
- Como está: `CHAGAS, Sílvio Donizete (org.). **Lições de direito civil alternativo**. [s.l.]: Acadêmica, 1994.`
- Trecho: `São paulo: Acadêmica, 1994, 164 p.`
- Problemas: local perdido; “São paulo” com caixa errada na fonte; páginas omitidas.
- Correção: `CHAGAS, Sílvio Donizete (org.). Lições de direito civil alternativo. São Paulo: Acadêmica, 1994. 164 p.`

**28. #189 · `ref-a2f0966a0b4a` · defeitos: A, I**
- Como está: `Carlos Derpic Salazar. **El derecho del poder contra el poder…**. [s.l.]: Educación para las Ciencias en Chiapas, 2013.`
- Trecho: `Aguascalientes: Centro de Estudios Jurídicos y Sociales Mispat; San Luis Potosí: Universidad Autónoma de San Luis Potosí; San Cristóbal de Las Casas: Educación para las Ciencias en Chiapas, 2013.`
- Problemas: nome natural (sobrenome composto: Derpic Salazar); três pares local/editora viraram um só, sem local.
- Correção: `DERPIC SALAZAR, Carlos. El derecho del poder contra el poder: alternativas para afrontar los vicios de la (in)justicia en Bolivia. Aguascalientes: Centro de Estudios Jurídicos y Sociales Mispat; San Luis Potosí: Universidad Autónoma de San Luis Potosí; San Cristóbal de Las Casas: Educación para las Ciencias en Chiapas, 2013.`

**29. #247 · `ref-a9f1cd5a546e` · defeitos: I, D**
- Como está: `INSTITUTO APOIO JURÍDICO POPULAR. **Discriminatória de terras públicas**. [s.l.]: AJUP/FASE, 1986.`
- Trecho: `Rio de Janeiro: AJUP/FASE, 1986. Coleção "Socializando conhecimentos" n. 1`
- Correção: `INSTITUTO APOIO JURÍDICO POPULAR. Discriminatória de terras públicas. Rio de Janeiro: AJUP/FASE, 1986. (Socializando conhecimentos, 1).`

**30. #2 · `ref-ce3f5e70ea32` · defeitos: I, D, F**
- Como está: `AGUIRRE, Francisco Ballón; BORRERO, Camilo. **Qualdireito?**. [s.l.: s.n.], 1991.`
- Trecho: `Qualdireito?. Rio de Janeiro: AJUP/FASE, set. 1991. Coleção Seminários, n. 16`
- Problemas: o mais grave — o trecho tem **local e editora** e a saída diz `[s.l.: s.n.]`: o gerador não errou por falta de dado, errou por não olhar; título colado; a interrogação recebe um ponto depois (`?**.`).
- Correção: `AGUIRRE, Francisco Ballón; BORRERO, Camilo. Qual direito? Rio de Janeiro: AJUP/FASE, 1991. (Coleção Seminários, 16).` (o original escreve “Qualdireito?”; separar e registrar).

### 3.10. Placar da amostra

| Resultado | Itens | % |
|---|---:|---:|
| Conforme a NBR 6023:2018 | 0 | 0,0 |
| Com ao menos um defeito | 30 | 100,0 |
| Com defeito grave (A/T/P/H) | 16 | 53,3 |
| Só com defeito de imprenta/dados/forma | 14 | 46,7 |

---

## 4. Taxa de erro por tipo de defeito

### 4.1. Na amostra (n = 30)

| Código | Defeito | Itens | % |
|---|---|---:|---:|
| I | Imprenta (local/editora/instituição) | 22 | 73,3 |
| D | Páginas, volume, número, edição, curso, tradução | 20 | 66,7 |
| F | Forma (pontuação, caixa, destaque, espaço, `a`/`b`) | 12 | 40,0 |
| A | Autoria | 8 | 26,7 |
| H | Placeholder (`[obra coletiva]` etc.) | 7 | 23,3 |
| T | Título | 6 | 20,0 |
| P | Tipo/suporte | 6 | 20,0 |

Um item pode acumular vários códigos; a soma não dá 100%.

**Por tipo de publicação** (defeito grave / itens do tipo na amostra):

| Tipo | Graves | Total | % |
|---|---:|---:|---:|
| Capítulo | 4 | 4 | 100 |
| Dissertação | 2 | 2 | 100 |
| Monografia | 1 | 1 | 100 |
| Tese | 1 | 1 | 100 |
| Legislação | 1 | 1 | 100 |
| Documento | 1 | 1 | 100 |
| Artigo | 4 | 6 | 66,7 |
| Livro | 2 | 13 | 15,4 |
| Relatório | 0 | 1 | 0 |

Leitura: **livro é o formato em melhor estado** (o defeito é quase sempre só a
imprenta); **capítulo, pós-graduação e legislação estão quebrados por
construção** — o gerador não tem código que produza o formato correto.

### 4.2. No conjunto `alta` (n = 221, medição automática)

| Achado | Registros | % de 221 |
|---|---:|---:|
| `[s.l.]` impresso apesar de local no `trecho` | 76 | 34,4 |
| Local na vaga da editora (`[s.l.]: Rio de Janeiro`) | 10 | 4,5 |
| Páginas no `trecho`, ausentes na saída | 59 | 26,7 |
| Volume/número no `trecho`, ausentes na saída | 30 | 13,6 |
| Edição no `trecho`, ausente ou fora de lugar | 8 | 3,6 |
| Capítulo com `[obra coletiva]` | 30 | 13,6 (100% dos capítulos) |
| Pós-graduação com `[instituição não identificada]` apesar da universidade no `trecho` | 15 | 6,8 (100% dos 15) |
| Autor pessoal em ordem natural | 48 | 21,7 |
| Autor = “Nome, em DD de mês de AAAA” | 11 | 5,0 |
| Autor = nome + cargo/biografia | 2 | 0,9 |
| Registro em variante de nome do mesmo autor | 101 | 45,7 |
| Colisão (autor, ano) sem `a`/`b` | 64 | 29,0 |
| Duplicata exata (título+autor+ano) | 6 | 2,7 |
| Quase-duplicata (similaridade ≥ 0,85) | ≥12 | ≥5,4 |
| Palavra colada (“compreensãomaterialista”) | ≥21 | ≥9,5 |
| Título com mais de 90 caracteres | 39 | 17,6 |
| Título com mais de 150 caracteres | 13 | 5,9 |
| Título cortado em 500 caracteres | 3 | 1,4 |
| Veículo cortado no meio da palavra | 3 | 1,4 |
| Artigo sem periódico (`[periódico não identificado]`) | 8 | 19,0 dos 42 artigos |
| Artigo com veículo = título | 4 | 9,5 dos 42 artigos |
| Artigo com veículo = cidade (`Bilbao`, `Cochabamba`) | 3 | 7,1 dos 42 artigos |

---

## 5. O que o gerador faz de errado (com a linha do código)

A função `abnt()` (linhas 58–90) monta a referência com uma string fixa por
tipo. O problema não é pontual: são as regras.

| Linha | Código | Efeito |
|---:|---|---|
| 44–46 | `autor()` devolve `AUTOR NÃO IDENTIFICADO` | entrada não começa pelo título quando não há autor, como a NBR 6023 exige |
| 49–51 | `ano()` aceita só `\d{4}` | perde `1991b`, `1989a` — quebra a NBR 10520 |
| 67–71 | livro: `"[s.l.]: %s" % veiculo` | `veiculo` é editora **ou** cidade **ou** as duas coisas; local nunca é usado e cidade vira editora |
| 72–73 | capítulo: `"In: [obra coletiva], %s."` | descarta organizador, livro, local, editora e páginas; `veiculo` já preenchido em 19 dos 30 capítulos é ignorado |
| 74–75 | artigo: `"*%s*, %s."` | sem `v.`, `n.`, `p.`; aceita cidade como periódico; negrito no título do artigo |
| 76–78 | tese/dissertação/monografia: `"[instituição não identificada], [s.l.]"` | instituição e local existem no `trecho`; falta o curso; ano repetido sem os complementos |
| 80 | legislação: `"%s. **%s**. %s."` | falta data, ementa e veículo oficial; título com `/ano` |
| 88–89 | `Disponível em` + `Acesso em` | data de acesso única e global (`ACESSO`, linha 23) para 180 referências, inclusive as de link morto |
| 125 | `sort(key=autor)` | ordena pela string crua: “Roberto Lyra Filho” vai para R, “LYRA FILHO, Roberto” para L |
| 181–192 | `lista()` numera de 1 | o apêndice reinicia a numeração: 606 linhas com números repetidos de 1 a 236 |

Duas consequências que valem destaque:

- **`[s.l.]` e `[s.n.]` estão sendo usados como tapa-buraco, não como
  lacuna.** O documento afirma “nada é inventado”, e de fato não inventa —
  mas **descarta** o dado que o extrator já tinha. `[s.l.: s.n.]` só pode
  aparecer quando o dado não existe na fonte.
- **O `trecho` é a prova e não é consultado.** Ele contém local, editora,
  páginas, edição, curso, instituição e coleção em centenas de registros. O
  gerador ignora esse campo por completo.

---

## 6. Duplicatas e referências que não deveriam estar na lista

### 6.1. Duplicatas exatas em `alta` (3 grupos, 6 registros)

| Obra | Registros | Problema |
|---|---|---|
| HERRERA FLORES, *Los derechos humanos como productos culturales* (2005) | 2 | mesma obra, editoras grafadas “Catarata” e “Libros de la Catarata” |
| PRESSBURGER, *Terras devolutas: o que fazer com elas?* (1990) — #308 e #309 | 2 | uma com “com elas”, outra com “comelas” — a chave de dedup por título não pegou |
| CAMPILONGO; PRESSBURGER, *Discutindo a assessoria popular* (1991) — #186 e #187 | 2 | “aassessoria” vs “a assessoria”. Há ainda #361 e #362, “Discutindo a assessoria popular – II” (1992), duplicados entre si: são 4 registros para 2 volumes |

### 6.2. Quase-duplicatas (≥ 6 pares) que precisam de decisão humana

| Par | Situação |
|---|---|
| *Serviço de Apoio Jurídico – SAJU* (2003) | 2 registros: um com autor invertido, outro natural — mesma monografia |
| *Esquemas de Direito Processual Penal: Introdução* (1961) | 2 registros; em um deles o autor virou “Roberto. Esquemas de Direito Processual Penal” |
| *Filosofia jurídica: pequena bibliografia…* (2002) | 2 registros do mesmo artigo, com autor grafado de dois jeitos |
| *Da Utopia estudantil a Ação Política* / *Assessoria jurídica universitária popular: da utopia estudantil à ação política* (2003) | provável mesma monografia de Ivan Furmann, com dois títulos |
| *Anotações sobre Direito Insurgente* (1994) vs *… direito insurgente* (2010) | mesmo título em anos diferentes: reedição ou erro de ano — decidir |
| *Sobre o papel do direito na sociedade capitalista* (1989, 2 registros) | subtítulos diferentes (`ocupações coletivas - direito insurgente` vs `direito insurgente`); provavelmente duas obras, mas colidem na citação |
| *Discriminatória de terras públicas* (1984 e 1986) | edições diferentes, ambas de AJUP/FASE; manter as duas, corrigir “Discriminatóriade” |
| *Solo urbano: propostas para a Constituinte* (1986 e 1996) | idem; corrigir “propostapara” |

### 6.3. O que não é referência bibliográfica

Na amostra: **#291** (edital de chamada de artigos) e **#59** (edital de
matrícula) não são obras citadas; são documentos administrativos. No conjunto
`alta` há ainda:

- **#296** `PAULO ARANTES. 15/10 – Faculdade de Direito da USP. "1964-2011` — registro de evento, com título quebrado.
- **#261** `Joaquim das Neves Norte. (Advogado, 40 anos, pai de 4 filhos… assassinado… no dia 12 de junho de 1981)` — a “obra” é uma nota biográfica/homenagem.
- **#287** `MIGUEL BALDEZ. Procurador do Estado do RJ Aposentado…` — idem, mini-biografia truncada em 500 caracteres.
- **#316** `REVISTA DA AATR. Política. [s.l.]: Ática, 1982` — três campos colados sem sentido.
- **#234** e **#291** `REVISTA DO SAJU. O Conselho Editorial…` — comunicados editoriais.

Esses registros deveriam sair da lista de referências (ou ir para “fontes
consultadas”), não ser formatados como livro.

### 6.4. Autor confundido com data, frase ou biografia

Este é um erro de extração que contamina a lista inteira, não só a amostra:

| Tipo | Registros | Exemplos |
|---|---:|---|
| Autor = “Nome, em DD de mês de AAAA” | 11 | `Roberta Cunha, em 21 de janeiro de 2010`; `Luiz Otávio Ribas, em 1 de janeiro de 2010`; `Ricardo Pazello, em 3 de julho de 2010` |
| Autor = nome + cargo/biografia | 2 | `Marcus Orioni, Professor Livre Docente da Faculdade de Direito da Universidade de São Paulo.` (#282); `MIGUEL BALDEZ. Procurador do Estado do RJ Aposentado…` (#287) |
| Título = parágrafo do post | 13 títulos > 150 caracteres | #198 abre com `I. Em meia hora a reunião começaria…`; #269 e #296 são o primeiro parágrafo inteiro do texto |
| Autor = fragmento de frase | 1 | `À Classe Trabalhadora, e` (apêndice #1) |

As 11 datas são a assinatura de post do Blogspot (“Por Fulano, em 21 de
janeiro de 2010”) lida como se fosse o campo autor. O conserto é no extrator:
rejeitar `,\s*em\s+\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\s*$` no `separa_autor` e
usar a data como indício de post, não de publicação da obra.

---

## 7. NBR 10520:2023 — o que falta para citar

A lista existe para sustentar citação no texto. Hoje ela não sustenta:

1. **Sem `a`/`b` para autor+ano repetido.** 21 grupos e 64 registros em
   `alta`. Exemplo real: BALDEZ tem três obras em 1989 e duas em 1991; a
   citação `(BALDEZ, 1989)` não identifica qual. O próprio `trecho` já traz
   `1991b`, `1989a`, `1989f` — e o campo `ano` só guarda o número.
2. **`AUTOR NÃO IDENTIFICADO` não pode ser citado.** Pela NBR 10520, a
   citação usa a primeira palavra do título em maiúsculas:
   `(EDITAL DE INSCRIÇÃO…, 2013)`. São 250 registros sem autor (7 em `alta`:
   1 documento e 6 legislações).
3. **`[s.d.]` sem regra de citação.** 284 registros sem ano; a citação
   correta é `(AUTOR, [s.d.])`, e isso precisa estar escrito no documento.
4. **Sem páginas, não há citação direta.** 59 registros `alta` têm página no
   `trecho` e nenhum na saída. Citação direta exige `(AUTOR, ano, p. X)`.
5. **Sem forma de citação publicada.** O documento não diz como citar; um
   leitor que use `Roberto Lyra Filho. **…**` vai citar
   `(ROBERTO LYRA FILHO, 1982)` — errado, porque o sobrenome é Lyra Filho.
6. **Mais de três autores.** A NBR 6023 admite `et al.`; a NBR 10520 usa
   `et al.` na citação. A lista traz todos os autores em alguns casos
   (#5, com 6 autores; #184, com 4) e nomes incompletos em outros
   (`PRESSUBURGER, T. Miguel`), sem critério declarado.
7. **Legislação na citação.** `(BRASIL, 2024)` não distingue os decretos
   listados; a prática é citar pelo número (`Decreto nº 11.995/2024`) ou
   adotar `2024a`, `2024b`. O documento precisa escolher e declarar.

---

## 8. Recomendações para `etl/monta-referencias-abnt.py`

### P0 — corrige a maior parte dos defeitos

1. **Separar `local` e `editora`.** Enquanto `veiculo` for um campo só, o
   gerador não tem como acertar. Duas saídas:
   - curto prazo: extrair do `trecho` com regex
     `(?P<local>[A-ZÁÉÍÓÚÂÊÔÃÕÇ][^:]{2,40}):\s*(?P<editora>[^,]{2,60}),\s*(?:19|20)\d{2}`
     e usar `veiculo` só como desempate;
   - definitivo: schema v2 com `local`, `editora`, `paginas`, `volume`,
     `numero`, `edicao`, `instituicao`, `curso`, `colecao`.
2. **Nunca preencher a vaga da editora com cidade.** Se o valor casar com
   uma lista de municípios/capitais, ele é `local`. Casos atuais: 10.
3. **Capítulo:** montar
   `AUTOR. Título do capítulo. In: ORGANIZADOR (org.). Título do livro. Local: Editora, ano. p. x-y.`
   usando `veiculo` + `trecho`; se faltar o livro, escrever
   `In: [título do livro não identificado]` — **nunca** `[obra coletiva]`.
4. **Pós-graduação:** `Ano. Tipo (Curso) – Instituição, Local, ano.` com
   `veiculo` (universidade) e local do `trecho`. `[instituição não
   identificada]` só quando não houver nem no `trecho`.
5. **Autoria:** inverter nomes pessoais (`ROBERTO LYRA FILHO` →
   `LYRA FILHO, Roberto`) com lista de partículas (`de, da, do, das, dos,
   e`) e regra de sobrenome composto (`Fals Borda`, `Derpic Salazar`,
   `Lyra Filho`). Não inverter instituições. Se o campo tiver mais de 5
   palavras ou casar com
   `(?i)professor|advogad|mestrand|doutorand|pesquisador|anos,|pai de`,
   **rebaixar para `baixa`** em vez de publicar.
6. **Chave canônica de ordenação e agrupamento:**
   `chave = sem_acento(sobrenome) + "|" + sem_acento(nome)`, com tabela de
   aliases (`BALDÉZ`→`BALDEZ`, `PRESSUBURGER`→`PRESSBURGER`) e merge por
   similaridade ≥ 0,92. Sem isso, 101 registros continuam fora de lugar.
7. **Sufixo `a`/`b`:** detectar colisão em `(chave_autor, ano)` e sufixar
   por ordem de título; emitir também o par `autor, ano` para a citação.
   Recuperar o sufixo do `trecho` quando existir (`1991b`).
8. **Dedup por chave sem espaços:** comparar
   `re.sub(r"[^a-z0-9]", "", sem_acento(titulo+autor+ano))`. É o que pega
   “comelas/com elas” e “aassessoria/a assessoria”. Duplicata só é removida
   automaticamente quando autor **e** ano coincidem; o resto vai para uma
   lista “revisar”.
9. **Título:** cortar imprenta colada (`\s+\d+\s*ed\.,`, `,\s*[A-Z][a-z]+:`),
   remover ponto final quando o título já termina em `?` ou `!`, e não usar
   como título nada com mais de ~200 caracteres (hoje 13 passam de 150 e 3
   foram cortados no meio da palavra em 500).
10. **Destaque:** um único padrão por referência. Negrito no título do livro;
    itálico no título do periódico; **nada** no título do artigo ou do
    capítulo. Hoje há negrito no artigo **e** itálico no periódico.
11. **Numeração:** o apêndice continua a série (371–606) ou usa `B1…B236`;
    reiniciar em 1 cria 236 números duplicados no mesmo arquivo.
12. **`Acesso em`:** guardar a data por referência, não uma constante
    global; e não imprimir “Acesso em” para link que a conferência marcou
    como morto (74 casos).

### P1 — consistência editorial

- Normalizar `n.` → `nº` e número de lei com separador de milhar
  (`Lei n. 8629/93` → `Lei nº 8.629, de 25 de fevereiro de 1993`).
- Padronizar `Em:` → `In:` (o extrator aceita os dois).
- Corrigir ou sinalizar palavras coladas (≥21 registros): a origem é a
  junção de nós de texto no extrator, não o gerador.
- Remover resíduos: `*` depois do nome (`Luísa Saraiva*`), `(Org.)` vs
  `(org.)`, `[Relatório]` redundante.
- Separar “Referências” de “Fontes e documentos consultados” (editais,
  blogs, páginas institucionais).
- Emitir, ao lado de cada entrada, a forma de citação
  `(SOBRENOME, ano)` ou `(SOBRENOME, ano, p. X)`.

### P2 — qualidade do documento

- Índice por letra e âncoras estáveis (`#lyra-filho-roberto`), para o mesmo
  autor não aparecer em duas letras.
- Quadro de números recalculado na mesma execução do corpo (hoje o cabeçalho
  está velho: 57/0/40/83 contra 102/4/74/0 do corpo).
- Relatório de QA no fim do arquivo: quantos `[s.l.]`, quantos `[s.n.]`,
  quantos `a`/`b`, quantas duplicatas sugeridas.

### Correções no extrator (`etl/extrai-referencias.py`) que alimentam o gerador

| Onde | Problema | Correção |
|---|---|---|
| linha 563 `titulo[:500]` | corta no meio da palavra (3 casos) | cortar em limite de frase e rebaixar a confiança |
| linha 621 `[^,.]{0,90}` em `extrai_veiculo` | veículo cortado em “resp”, “Legislativ”, “Minas Ge” | parar em limite de palavra e não truncar |
| linhas 193/205 `"".join(partes)` | palavras coladas (“JustiçaJudiciária”) | juntar nós inline com separador de espaço e colapsar |
| `separa_autor` | aceita byline (“… em 21 de janeiro de 2010”) | rejeitar autor com data/cargo |
| `tenta_ref` | aceita parágrafo narrativo como título (13 casos > 150 chars) | exigir título ≤ 200 chars e rejeitar início “I.”, “Reunidos…” |
| `extrai_veiculo` | cidade vira periódico (`Bilbao`, `Cochabamba`) | lista de cidades → campo `local` |

---

## 9. Como revalidar (proposta de verificação determinística)

Sugiro um `etl/audita-referencias-abnt.py` (não criado nesta revisão) que
leia o Markdown gerado e o JSON e falhe com código ≠ 0 quando:

| Verificação | Limite aceitável |
|---|---|
| `[s.l.]` com local presente no `trecho` | 0 |
| `[s.l.: s.n.]` com editora presente no `trecho` | 0 |
| capítulo com `[obra coletiva]` | 0 |
| pós-graduação sem instituição quando o `trecho` tem | 0 |
| `trecho` com `p.` e saída sem `p.` | 0 |
| autor pessoal sem vírgula (ordem natural) | 0 |
| mesmo nome em mais de uma grafia | 0 |
| (autor, ano) repetido sem sufixo | 0 |
| título > 200 caracteres | 0 |
| título com palavra colada | 0 |
| duplicata por título+autor+ano (sem espaços) | 0 |
| números de entrada repetidos no arquivo | 0 |
| números do cabeçalho × corpo | iguais |

Enquanto esses limites não forem zero, o documento não deve ser apresentado
como “referências em ABNT”: são **pistas de referência** para revisão humana.
Se o objetivo é publicar já, a única fatia aproveitável sem retrabalho é a de
livros com imprenta completa — e mesmo ela precisa da correção de local.

---

## 10. O que esta revisão não fez

- Não editou `docs/referencias-abnt.md`, `docs/referencias-por-tema.md`,
  `docs/referencias-por-autor.md`, `dados/*.json` nem o gerador.
- Não conferiu autoria, data ou editora em fonte externa (catálogo, Open
  Library, Planalto). As correções usam o `trecho` como prova; onde ele não
  basta, o item está marcado como pendente.
- Não julgou os 236 registros de confiança baixa nem os 149 de média, além
  do que apareceu por contaminação (duplicatas e variantes de nome).
- Não mediu tempo de execução nem custo: a revisão é local e de custo zero.
