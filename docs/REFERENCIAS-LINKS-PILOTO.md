# Piloto de resolução de links — referências AJP

> **Data:** 22/11/2026  
> **Saída:** `dados/referencias-resolvidas-piloto.json`  
> **Insumos:** `dados/referencias.json` (606 referências) e `dados/referencias-links.json` (leitura)  
> **Escopo:** 40 referências de `confianca: "alta"` e `url` vazio  
> **Rede:** consultas públicas a Open Library, Crossref e Internet Archive; sem login, sem paywall, sem API paga.  
> **Regra:** este piloto **não** altera `dados/referencias-links.json`, HTML, CSS, JS, `_indice.json` nem `docs/referencias-abnt.md`.

---

## 1. Resultado em números

Das 606 referências, **213** são de confiança alta e não tinham URL. Foram selecionadas 40 para o piloto (26 livros, 8 artigos, 4 dissertações, 1 tese e 1 monografia).

| Medida | Valor |
|---|---:|
| Referências na amostra | 40 |
| Com URL localizada | **17 (42,5%)** |
| Correspondência exata | 16 |
| Correspondência provável | 1 |
| Sem correspondência | 23 |
| Acesso aberto | 4 |
| Empréstimo digital | 1 |
| Acesso restrito (metadado/paywall) | 12 |
| Não encontrado | 23 |

Por fonte que forneceu o link: Open Library **12**, Crossref **4**, SciELO **1**. Internet Archive, BDTD e Planalto não forneceram link nesta amostra. A soma fecha 17 — 16 exatos e 1 provável (Lyra Filho 1974/1976).

Leitura rápida: o piloto resolveu **42,5%** da amostra, mas só **5 itens (12,5%)** têm texto integral imediato (4 abertos + 1 empréstimo). Os outros 12 links são registros de catálogo ou páginas restritas — úteis para identificação bibliográfica, não para leitura.

---

## 2. Método

### 2.1 Seleção

1. Leu `dados/referencias.json` e filtrou `confianca == "alta"` **e** `url` vazio: 213 candidatas.
2. Selecionou 40 com diversidade de tipo e com maior chance de registro público (título e autoria limpos), mantendo 6 teses/monografias para testar o limite dos repositórios.
3. Não usou `dados/referencias-links.json` para herdar links: ele só foi lido para confirmar que o piloto não o altera.

### 2.2 Consultas

Para cada item, três consultas independentes:

- **Open Library** — `https://openlibrary.org/search.json?title=...&author=...&limit=5`, com `fields=key,title,author_name,first_publish_year,edition_count,ebook_access,ia,isbn,publisher,language`. Quando a busca com autor zerava, repetia só com o título.
- **Crossref** — `https://api.crossref.org/works?query.bibliographic=...&rows=5` (depois `rows=10` e `query.title` no prefixo UnB `10.26512`), com `select=DOI,title,author,issued,container-title,type,URL,license,publisher`.
- **Internet Archive** — `https://archive.org/advancedsearch.php?q=title:(...) AND creator:(...)&output=json`, com `identifier,title,creator,date,year,access-restricted-item,mediatype`.

Para os links aceitos, houve uma segunda rodada de verificação:

- `https://openlibrary.org/works/{key}.json` para conferir título e autoria da obra;
- `https://archive.org/metadata/{identifier}` para separar empréstimo legítimo de upload comunitário;
- `https://doi.org/{doi}` (HEAD/GET) para verificar para onde o DOI resolve e se o texto é aberto.

Total: **183 requisições** em cerca de 10 minutos, com pausa de 1,5–2,0 s e User-Agent `finweejur/github artur colito`.

### 2.3 Critério de correspondência

Normalização antes de comparar: minúsculas, remoção de acentos, pontuação e espaços repetidos. Depois:

- **exato** — título e autoria conferem. Para obra no Open Library, a URL é a *work* (agnóstica de edição); edição/ano diferentes ficam na observação. Para DOI, exige mesma publicação (ano/veículo compatíveis).
- **provável** — título e autoria conferem, mas a edição ou o veículo diverge. A URL é registrada como candidata e a observação diz o que conferir.
- **nenhum** — não há correspondência segura. **Não foi inventada URL.**

### 2.4 Classificação de acesso

| Valor | Significado |
|---|---|
| `aberto` | Texto integral público, sem login. |
| `emprestimo` | Empréstimo digital (Internet Archive/Open Library). |
| `previa` | Visualização parcial ou só resumo. |
| `restrito` | Apenas metadado de catálogo ou página com paywall. |
| `nao_encontrado` | Nenhuma URL segura. |

---

## 3. Itens resolvidos (17)

| ID | Título | Autor | URL | Fonte | Acesso | Match |
|---|---|---|---|---|---|---|
| `ref-6d9a3c02f4ac` | Direito e luta de classes: teoria geral do direito | STUCKA, Petr Ivanovich | <https://openlibrary.org/works/OL46046079W> | openlibrary | restrito | exato |
| `ref-7a341b172a2a` | El processo cultural: materiales para la creatividad humana | HERRERA FLORES, Joaquín | <https://openlibrary.org/works/OL34923246W> | openlibrary | restrito | exato |
| `ref-f3d538700052` | Introdução ao pensamento jurídico crítico | WOLKMER, Antonio Carlos | <https://openlibrary.org/works/OL42844007W> | openlibrary | restrito | exato |
| `ref-7f4c306df651` | Karl, meu amigo: diálogo com Marx sobre o Direito | Roberto Lyra Filho | <https://openlibrary.org/works/OL4851915W> | openlibrary | restrito | exato |
| `ref-77a0e723eaa2` | Los derechos humanos desde la escuela de Budapeste | HERRERA FLORES, Joaquín | <https://openlibrary.org/works/OL4186187W> | openlibrary | restrito | exato |
| `ref-75e06d79110c` | Magia e técnica, arte e política. Ensaios sobre a literatura e história da cultura | BENJAMIN, Walter | <https://openlibrary.org/works/OL19885070W> | openlibrary | restrito | exato |
| `ref-b11dc3592dd4` | O Cativeiro da Terra | MARTINS, José de Souza | <https://openlibrary.org/works/OL15417275W> | openlibrary | restrito | exato |
| `ref-adbf87db1072` | O Ícaro da modernidade: direito e política em Max Weber | ARGÜELLO, Katie Silene Cáceres | <https://openlibrary.org/works/OL45522294W> | openlibrary | restrito | exato |
| `ref-cce56d173208` | Pedagogia da autonomia: saberes necessários à prática educativa | FREIRE, Paulo | <https://openlibrary.org/works/OL26415542W> | openlibrary | restrito | exato |
| `ref-0bb524e3e61d` | Pedagogia do oprimido | FREIRE, Paulo | <https://openlibrary.org/works/OL1870556W> | openlibrary | restrito | exato |
| `ref-7b72ed72d9ba` | Socioambientalismo e novos direitos | SANTILI, Juliana | <https://openlibrary.org/works/OL12273795W> | openlibrary | emprestimo | exato |
| `ref-3f0e5edf81e1` | Teologia política | SCHMITT, Carl | <https://openlibrary.org/works/OL1157163W> | openlibrary | restrito | exato |
| `ref-bf96bf6445d2` | Direito insurgente: fundamentações marxistas desde a América Latina | PAZELLO, Ricardo Prestes | <https://doi.org/10.1590/2179-8966/2018/36564> | scielo | aberto | exato |
| `ref-82d04e4ed9ff` | Filosofia, teologia e experiência mística | Roberto Lyra Filho | <https://doi.org/10.5840/icp819742116> | crossref | restrito | provavel |
| `ref-7d81d6d42ece` | Reflexos do discurso liberal do direito de propriedade nas decisões judiciais proferidas em ações de desapropriação agrária | FIDELES, Junior Divino | <https://doi.org/10.25109/2525-328x.v.13.n.41.2014.426> | crossref | aberto | exato |
| `ref-10b93a97352d` | Justiça de transição: perdão ou desculpa em nome do Estado brasileiro? | Sueli Aparecida Bellato | <https://doi.org/10.26512/2014.11.d.17858> | crossref | aberto | exato |
| `ref-d6f2b2078570` | Sem porta-voz na rua, sem dono em casa: as lutas do movimento de mulheres camponesas (MMC Brasil) pelo direito a uma vida sem violência | MELO PEREIRA, Diana | <https://doi.org/10.26512/2015.04.d.18885> | crossref | aberto | exato |

### 3.1 Observações dos itens resolvidos

- **Direito e luta de classes: teoria geral do direito** — Work OL46046079W: 'Direito e luta de classes', Petr Ivanovich Stucka (trad. Soveral Martins), edição registrada de 1976; a referência cita a ed. Acadêmica de 1988. Mesma obra, edição distinta.
- **El processo cultural: materiales para la creatividad humana** — Work OL34923246W: 'El proceso cultural', Joaquín Herrera Flores, 2005 (mesmo ano). A 1ª consulta deu timeout e foi repetida. Sem ebook.
- **Introdução ao pensamento jurídico crítico** — Work OL42844007W: 'Introdução ao pensamento jurídico crítico', Antônio Carlos Wolkmer, 1991 (mesmo ano da referência). Sem ebook.
- **Karl, meu amigo: diálogo com Marx sobre o Direito** — Work OL4851915W: 'Karl, meu amigo', Roberto Lyra Filho, 1983 (mesmo ano); o registro traz só o título principal. Sem ebook.
- **Los derechos humanos desde la escuela de Budapeste** — Work OL4186187W: 'Los derechos humanos desde la Escuela de Budapest', Joaquín Herrera Flores, 1989 (mesmo ano). Sem ebook.
- **Magia e técnica, arte e política. Ensaios sobre a literatura e história da cultura** — Work OL19885070W: 'Magia e tecnica, arte e politica', Walter Benjamin, edição registrada de 1989; a referência cita a 7ª ed. de 1994. Mesma obra, edição distinta. Sem ebook.
- **O Cativeiro da Terra** — Work OL15417275W: 'O cativeiro da terra', José de Souza Martins, edição registrada de 2010; a 9ª ed. de 2021 (Contexto) não está digitalizada. Cópia comunitária no IA não vinculada.
- **O Ícaro da modernidade: direito e política em Max Weber** — Work OL45522294W: 'O Icaro da modernidade', Katie Argüello, edição registrada de 1996; a referência cita 1997. Sem ebook.
- **Pedagogia da autonomia: saberes necessários à prática educativa** — Work OL26415542W: 'Pedagogia da Autonomia - Edicao especial' (2019), Paulo Freire; mesma obra, com qualificador de edição no título. Sem ebook.
- **Pedagogia do oprimido** — Work OL1870556W: 'Pedagogia do Oprimido', Paulo Freire, 19 edições, 1ª de 1967. A 12ª ed. de 1983 (Paz e Terra) não tem ebook; acesso só para leitores com deficiência de impressão (printdisabled).
- **Socioambientalismo e novos direitos** — Work OL12273795W: 'Socioambientalismo e novos direitos', Juliana Santilli, 2005 (mesmo ano). Empréstimo digital (borrowable); cópia IA em inlibrary/printdisabled.
- **Teologia política** — Work OL1157163W: 'Teologia politica', Carl Schmitt, edição registrada de 1996; a referência cita a ed. Del Rey de 2006. Título e autor conferem; sem ebook.
- **Direito insurgente: fundamentações marxistas desde a América Latina** — DOI 10.1590/2179-8966/2018/36564; Revista Direito e Práxis, 2018; texto integral no SciELO (acesso aberto).
- **Filosofia, teologia e experiência mística** — DOI 10.5840/icp819742116: 'Filosofia, teologia e experiência mística', Lyra Filho, 1974 (anais do VIII Congresso); a referência cita 1976 (Kriterion). Título e autoria conferem, edição/veículo diferem; landing page responde 403 (paywall).
- **Reflexos do discurso liberal do direito de propriedade nas decisões judiciais proferidas em ações de desapropriação agrária** — DOI 10.25109/2525-328x.v.13.n.41.2014.426; Revista da AGU, v.13 n.41, 2014; PDF público na SEER da AGU, sem login.
- **Justiça de transição: perdão ou desculpa em nome do Estado brasileiro?** — DOI 10.26512/2014.11.d.17858; dissertação UnB, 2014; resolve para o handle 10482/17858, texto integral público.
- **Sem porta-voz na rua, sem dono em casa: as lutas do movimento de mulheres camponesas (MMC Brasil) pelo direito a uma vida sem violência** — DOI 10.26512/2015.04.d.18885; dissertação UnB, 2015; resolve para o handle 10482/18885, texto integral público.

---

## 4. Itens não encontrados (23)

| ID | Título | Autor | Motivo resumido |
|---|---|---|---|
| `ref-4042c6418f7e` | A (re)invenção dos direitos humanos | HERRERA FLORES, Joaquín | Open Library: 0 com e sem parênteses no título; Crossref: artigos sobre Herrera Flores, não a obra; Internet Archive: 0. |
| `ref-11e1a191ad69` | Acesso à Justiça | CAPPELLETTI, Mauro; GARTH, Bryan | Open Library: 57 registros com o título, nenhum de Cappelletti/Garth; Crossref: só artigos sobre a obra; Internet Archive: apenas cópia não autorizada (upload com marca z-lib), não vinculada. |
| `ref-213a041625e5` | Criminologia Crítica e Critica do Direito Penal. 3 ed., Rio de Janeiro: Ed. Revan, 1999 | BARATTA, Alessandro | Open Library: registro de título sem autor (/works/OL13403395M, 2002) e busca por Baratta retorna 0; Internet Archive: upload comunitário de obra protegida, não vinculado; Crossref: só artigos sobre a obra. |
| `ref-4f5671ece160` | Crítica da violência: crítica do poder | BENJAMIN, Walter | Open Library: 0; Crossref: artigos sobre o ensaio, não a edição brasileira; Internet Archive: 0. |
| `ref-1ee7bfc76f16` | Democracia e Revolução | LABICA, Georges | Open Library: 6 obras homônimas de outros autores; Crossref: 0; Internet Archive: 0. |
| `ref-a8cab838863a` | Educação como prática da liberdade | FREIRE, Paulo | Open Library: 0 com título+autor; Crossref: apenas resenhas e artigos sobre a obra; Internet Archive: 0. |
| `ref-9db0391a1477` | Ensino jurídico: saber e poder | RODRIGUES, Horácio Wanderlei | Open Library: 0 com título+autor; Crossref: 0 para a obra; Internet Archive: 0. |
| `ref-a6cb1bbe0a69` | Estado de Exceção | AGAMBEN, Giorgio | Open Library: 9 registros com o título, nenhum de Agamben; Crossref: artigos sobre o conceito; Internet Archive: 0. A ed. Boitempo de 2004 não foi localizada. |
| `ref-257cff7f87fb` | Horizontes amazônicos: para repensar o Brasil e o mundo | MALHEIRO, Bruno; PORTO-GONÇALVES, Carlos Walter; MICHELOTTI, Fernando | Open Library: só obra homônima de 2011, de outros autores; Crossref: resenha de Barata Teixeira (2021), não o livro; Internet Archive: 0. |
| `ref-161fd28a9d98` | Los derechos humanos como productos culturales: crítica del humanismo abstracto | HERRERA FLORES, Joaquín | Open Library: 0; Crossref: capítulos de obra coletiva homônima, não este livro; Internet Archive: 0. |
| `ref-f6149f369cd8` | Manual de Direito Agrário Constitucional: Lições de Direito Agroambiental | ROCHA, Ibraim, TRECCANI, Girolamo Domenico, BENATTI, José Heder, HABER, Lilian Mendes, CHAVES, Rogério Arthur Friza | Open Library: 0; Crossref: 0 para a obra; Internet Archive: 0. |
| `ref-185af71f40c3` | O Direito que se ensina errado | Roberto Lyra Filho | Open Library: 0; Crossref: só artigos sobre o tema; Internet Archive: 0. |
| `ref-4b43824634ef` | Origem do drama barroco | BENJAMIN, Walter | Open Library: 0; Crossref: artigos sobre a obra; Internet Archive: 0. A ed. Brasiliense de 1984 não foi localizada. |
| `ref-348a77809115` | Teoria geral do direito e marxismo | PACHUKANIS, Evgeny Bronislavovich | Open Library: 0 com título+autor; Crossref: só resenhas e artigos sobre Pachukanis; Internet Archive: 0. A ed. Acadêmica de 1988 não foi localizada. |
| `ref-5a179a10ccb3` | Anotações sobre Direito Insurgente | BALDEZ, Miguel Lanzellotti | Crossref: 10 resultados, nenhum correspondente; Open Library e Internet Archive: 0. |
| `ref-ecc39f33c6f2` | Aproximação ao Direito Alternativo na Ibero-América. Juízes para a democracia | HERRERA FLORES, Joaquín; SÁNCHEZ RUBIO, David | Crossref: 10 resultados, nenhum correspondente; Open Library e Internet Archive: 0. |
| `ref-bffe332d2aa0` | Crítica Jurídica y Estudios de Derecho | HERRERA FLORES, Joaquín | Crossref: 0; Open Library: 0; Internet Archive: 0. |
| `ref-d0f6a9312b58` | Direito insurgente e pluralismo jurídico: assessoria jurídica de movimentos populares em Porto Alegre e no Rio de Janeiro (1960-2000) | RIBAS, Luiz Otávio | Crossref: 10 resultados, nenhum correspondente; Open Library e Internet Archive: 0. Texto provavelmente em anais/repositório, sem URL pública localizada. |
| `ref-f074f6a25055` | Teorias críticas do direito e assessoria jurídica popular | PAZELLO, Ricardo Prestes | Crossref: 10 resultados, nenhum com título e autoria correspondentes; periódico não indexado para este artigo. |
| `ref-3f7fc449f6a0` | Direito como liberdade: o Direito Achado na Rua: experiências populares emancipatórias de criação do Direito | José Geraldo de Sousa Júnior | Crossref: só capítulos do livro de 2021 'O Direito achado na rua', não a tese de 2008; BDTD e busca do repositório UnB bloqueadas por robots. |
| `ref-bf0edf80d1cc` | Advocacia popular: práticas jurídicas e sociais no acesso ao direito e à justiça aos movimentos sociais de luta pela terra | Flávia Carlet | Crossref: só o artigo derivado de 2015 ('Advocacia Popular...', 10.12957/dep.2015.15409), não a dissertação; prefixo UnB 10.26512 não retorna a dissertação; BDTD e busca do repositório UnB bloqueadas por robots. |
| `ref-a2b260b2f81d` | Da pedagogia do oprimido ao direito do oprimido: uma noção de direitos humanos na obra de Paulo Freire | GÓES JUNIOR, José Humberto de | Crossref: 10 resultados, nenhum correspondente; BDTD e busca do repositório UFPB bloqueadas por robots; Open Library e Internet Archive: 0. |
| `ref-29ac5a98fcaa` | Da Utopia estudantil a Ação Política | Ivan Furmann | Crossref, Open Library e Internet Archive: 0; busca do acervo UFPR desautorizada por robots (/rest/, /xmlui/search), sem outra via pública de busca. |

### 4.1 Agrupamento dos motivos

**Sem registro público localizado (Open Library, Crossref e Internet Archive sem correspondência) (14):** `ref-9db0391a1477`, `ref-348a77809115`, `ref-4f5671ece160`, `ref-4b43824634ef`, `ref-4042c6418f7e`, `ref-161fd28a9d98`, `ref-f6149f369cd8`, `ref-185af71f40c3`, `ref-1ee7bfc76f16`, `ref-f074f6a25055`, `ref-d0f6a9312b58`, `ref-ecc39f33c6f2`, `ref-bffe332d2aa0`, `ref-5a179a10ccb3`

**Só homônimos de outros autores (3):** `ref-11e1a191ad69`, `ref-a6cb1bbe0a69`, `ref-257cff7f87fb`

**Só resenhas ou artigos sobre a obra (2):** `ref-a8cab838863a`, `ref-213a041625e5`

**Tese/dissertação/monografia sem DOI e com busca de repositório bloqueada (4):** `ref-bf0edf80d1cc`, `ref-a2b260b2f81d`, `ref-3f7fc449f6a0`, `ref-29ac5a98fcaa`

---

## 5. O que falhou e por quê

1. **BDTD — bloqueada por robots.** `bdtd.ibict.br/robots.txt` tem `Disallow: /vufind/Search/` para todos os agentes. A API VuFind (`/vufind/api/v1/search`) respondeu 400, e o OAI-PMH não faz busca por palavra-chave. Resultado: 4 das 6 teses/monografias ficaram sem link (Carlet, Góes Junior, Sousa Júnior, Furmann).
2. **Repositório da UnB — busca desautorizada.** O `robots.txt` bloqueia `/simple-search` e `/discover`. O caminho que funcionou foi o DOI Crossref `10.26512/...`, que resolve para os handles 10482/17858 e 10482/18885 (Bellato e Pereira). Carlet e Sousa Júnior não têm DOI depositado com o título da tese.
3. **Repositório da UFPB — busca desautorizada.** `/jspui/simple-search` está no `Disallow`. Uma sondagem de status foi feita antes de ler o robots; nenhum dado dela foi usado.
4. **Acervo Digital da UFPR — busca e API desautorizadas.** O `robots.txt` bloqueia `/rest/` e `/xmlui/search` e pede `Crawl-delay: 5`. As 5 consultas de teste a `/rest/items` foram feitas antes da leitura do robots, retornaram resultados genéricos (a API ignorou o `query`) e **não foram aproveitadas**. Nenhuma coleta UFPR entrou no resultado.
5. **CAPES — sem acesso público.** O Portal de Periódicos exige login institucional para o conteúdo. Não foi consultado; não há como validar texto integral sem credencial.
6. **Planalto — não se aplica à amostra.** Nenhuma das 40 referências é do tipo `legislacao`; as 8 referências de legislação do acervo não entraram na seleção.
7. **Open Library — exceção de robots registrada.** O `robots.txt` tem `Disallow: /search`. O endpoint `search.json` foi usado porque a tarefa o autorizou explicitamente; o uso ficou limitado a esta amostra (66 consultas), com pausa e sem crawling de páginas.
8. **Internet Archive — uploads comunitários não foram vinculados.** Havia cópias de Baratta, Freire e José de Souza Martins em `booksbylanguage_portuguese` (uploads de usuários, obra ainda protegida), além de uma cópia com marca `z-lib` de Cappelletti/Garth. Por ética e por não serem empréstimo legítimo, não entraram. Só o item `inlibrary/printdisabled` de Santilli foi usado como evidência de empréstimo — e a URL gravada é a do Open Library.
9. **Ruído do Crossref.** Muitos resultados eram resenhas, capítulos sobre a obra ou homônimos. Exemplo: “Pedagogia do oprimido” retorna um capítulo alemão *sobre* Freire, não o livro. Todos foram rejeitados.
10. **Um provável.** O único `provavel` é Lyra Filho, “Filosofia, teologia e experiência mística”: o DOI aponta para os anais de 1974, e a referência cita o Kriterion de 1976. Título e autoria conferem; a edição não. O DOI responde 403 (paywall).
11. **Dois timeouts** na primeira rodada do Open Library (Baratta e Herrera Flores/El proceso cultural). O segundo foi recuperado na repetição; o primeiro continuou sem registro com autoria.
12. **Ano da edição ≠ ano da referência.** Em 7 obras do Open Library a edição registrada é anterior ou posterior à citada (ex.: Stucka 1976 vs. 1988; Benjamin 1989 vs. 1994). Como a URL é a *work*, o vínculo é com a obra, não com a edição — a observação de cada item diz isso.

---

## 6. Recomendações para o próximo lote

1. **Separar o piloto em duas filas:** livros (Open Library rende bem) e teses (dependem de DOI/repositório). Misturar esconde que a taxa de sucesso é muito diferente.
2. **Teses:** tentar o OAI-PMH ou os sitemaps dos repositórios por *handle*, não a busca; ou obter a lista de handles por set. Respeitar `Crawl-delay` e `Disallow`. O caminho mais barato é o DOI `10.26512` para a UnB.
3. **Livros:** complementar o Open Library com catálogo da Biblioteca Nacional e páginas de editoras; o Open Library cobre bem Freire, Benjamin, Herrera Flores e a coleção Acadêmica, mas não cobre AJUP/FASE, Del Rey e Boitempo.
4. **Nunca gravar `restrito` como se fosse leitura.** O campo `tipo_acesso` já separa; a página pública deve mostrar “localizar em biblioteca” quando for `restrito`.
5. **Revisão humana do `provavel`** antes de promover a `exato`.
6. **Não promover nada para `dados/referencias-links.json`** sem decisão do dono: este arquivo é insumo de outro ETL e tem semântica de link testado (status HTTP, content-type).

---

## 7. Reprodutibilidade

Consultas-base usadas (substituir `{t}`, `{a}`, `{ano}`):

```text
https://openlibrary.org/search.json?title={t}&author={a}&limit=5
https://api.crossref.org/works?query.bibliographic={t}+{a}+{ano}&rows=5
https://archive.org/advancedsearch.php?q=title:({t})+AND+creator:({a})&output=json
https://openlibrary.org/works/{key}.json
https://archive.org/metadata/{identifier}
https://doi.org/{doi}
```

Arquivo de dados: `dados/referencias-resolvidas-piloto.json` (40 registros, um por item, com `id`, `titulo`, `autor`, `url_encontrada`, `fonte`, `tipo_acesso`, `match`, `observacao`, `verificado_em`).

**Nada foi commitado.** O piloto não toca nos dados existentes.
