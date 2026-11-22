# Piloto de extração de referências — Acervo AJP

> **Data:** 22/11/2026
> **Script:** `etl/extrai-referencias.py`
> **Saída:** `dados/referencias-piloto.json`
> **Escopo:** 27 páginas (20 da amostra + 7 páginas de bibliografia/referências)
> **Rede:** nenhuma. O piloto lê apenas HTML local; não baixa, não valida DOI,
> não altera posts, `_indice.json` nem `dados/*.json` existentes.
> **Estado do acervo na execução:** `_indice.json` com 790 entradas; 27/27
> páginas da amostra tinham `<article>` e `.corpo`.

---

## 1. O que o piloto faz

1. Abre o HTML de cada página e isola o corpo real do post
   (`<article>` → `<div class="cartao corpo">`). Ficam de fora cabeçalho,
   ficha de origem, botões, rodapé, redes sociais, links internos e a seção
   de posts relacionados.
2. Extrai **links explícitos** do corpo com `href`, texto âncora e parágrafo
   de contexto. Descarta o próprio blog, `blogspot` do acervo, redes,
   imagens, `mailto:`, notas de rodapé do Blogger e rótulos genéricos
   ("Ver o vídeo no original", "Ler no blog original", "Fotos").
3. Detecta **padrões bibliográficos** no texto:
   - `SOBRENOME, Nome. Título. Local: Editora, ano.`
   - artigo com revista, volume, número, página ou DOI;
   - tese, dissertação, monografia, relatório;
   - capítulo com `Em:` / `In:`;
   - legislação (lei, decreto, constituição);
   - lista curta `"Título", de Autor`;
   - blocos quebrados em autor / título / imprenta e entradas com travessão
     (`______.`) que herdam o autor anterior.
4. Grava cada referência com o schema abaixo e uma `confianca` explícita.
5. Deduplica por título + autor + ano, inclusive entre páginas. Quando a
   mesma obra aparece em mais de um post, mantém uma ocorrência e registra
   `ocorrencias`.

### Schema do registro

| Campo | Conteúdo |
|---|---|
| `id` | hash estável de `slug + tipo + título + autor + ano` |
| `tipo` | `livro`, `capitulo`, `artigo`, `tese`, `dissertacao`, `monografia`, `relatorio`, `legislacao`, `video`, `documento`, `site`, `obra` |
| `titulo` | título como está no original (sem inventar) |
| `autor` | autor(es) como estão no original; vazio quando não há evidência |
| `ano` | ano de publicação; vazio quando só há `[s.d.]` ou ano de título |
| `veiculo` | revista, editora, instituição, site ou plataforma |
| `url` | link explícito associado à referência, quando existe |
| `fonte_slug` | slug do post onde a referência foi encontrada |
| `fonte_titulo` | título do post |
| `trecho` | parágrafo(s) original(is) que sustentam a extração |
| `confianca` | `alta`, `media` ou `baixa` |
| `metodo` | `padrao` (texto) ou `link` (âncora explícita) |
| `motivo` | por que a confiança é alta/média/baixa |
| `ocorrencias` | quantas páginas citam a mesma obra (após dedup) |

`alta` = autor, título, ano e imprenta/veículo reconhecidos.
`media` = referência plausível, mas falta ano, imprenta ou o texto do link é
curto.
`baixa` = falta autor, ano ou título, ou o texto é um rótulo; revisar antes
de usar em ABNT.

---

## 2. Números

| Conjunto | Páginas | Referências | `alta` | `media` | `baixa` | Com URL |
|---|---:|---:|---:|---:|---:|---:|
| Amostra base (10 primeiras + 10 aleatórias) | 20 | **29** | 23 | 5 | 1 | 11 |
| Páginas dirigidas de bibliografia | 7 | **216** | 120 | 16 | 80 | 22 |
| **Total do piloto** | **27** | **245** | **143** | **21** | **81** | **33** |

- **12 das 27 páginas** tiveram alguma referência. As outras 15 são posts
  narrativos, notícias, poemas ou chamadas, sem bloco bibliográfico.
- **217** referências vieram de padrão textual; **28** vieram de link
  explícito (15 documentos/PDF, 7 sites, 5 legislações, 1 vídeo).
- **96** referências estão sem ano e **31** sem autor. A maior parte da
  lacuna vem da lista de `referencias.html` (61 obras de leitura, sem dados
  de publicação), não de falha de leitura.
- **4 obras** aparecem em mais de uma página e foram contadas uma vez no
  total. A soma por página no JSON é anterior a essa deduplicação.

### Por tipo

| Tipo | Quantidade |
|---|---:|
| livro | 74 |
| obra (lista sem imprenta) | 67 |
| artigo | 36 |
| capítulo | 18 |
| documento (PDF/link) | 15 |
| dissertação | 10 |
| monografia | 7 |
| site | 7 |
| legislação | 5 |
| tese | 3 |
| relatório | 2 |
| vídeo | 1 |

### Onde estão as referências

| Página | Refs |
|---|---:|
| `programacao-da-oficina-direito-pra-quem` | 20 |
| `oficina-de-introducao-as-teorias-criticas-e-ajp` | 2 |
| `catalogo-da-editora-sergio-antonio-fabris` | 1 |
| `o-abismo-entre-o-asfalto-e-a-favela` | 3 |
| `os-instrumentos-do-direito-servem-para-quem` | 1 |
| `levante-sua-voz` | 2 |
| `helio-bicudo-sobre-o-mst` | 2 |
| `biblioteca-digital` | 41 |
| `biblioteca-ajup-rj` | 45 |
| `biblioteca-roberto-lyra-filho` | 32 |
| `biblioteca-miguel-lanzellotti-baldez` | 17 |
| `biblioteca-joaquin-herrera-flores` | 22 |
| `referencias` | 61 |

As 7 páginas dirigidas concentram **216 das 245** referências. O piloto
confirma que a bibliografia do acervo está menos nos posts e mais nas
páginas de biblioteca.

---

## 3. Exemplos de boa extração

| Referência extraída | Onde | Confiança |
|---|---|---|
| BALDEZ, Miguel Lanzellotti. *Notas sobre a democratização do processo*. Revista de Direito da Defensoria Pública, v. 10, n. 12, 1998, p. 13–23. | biblioteca-miguel | alta |
| PAZELLO, Ricardo Prestes. *Teorias críticas do direito e assessoria jurídica popular*. Revista Direitos Humanos e Sociedade, v. 2, p. 141-161, 2019. | programacao | alta |
| MOREIRA, Maira de Souza. *Do Direito à Política Pública...*. Dissertação (Mestrado), 2017. | programacao | alta |
| ROCHA, Ibraim; TRECCANI, Girolamo Domenico; BENATTI, José Heder; HABER, Lilian Mendes; CHAVES, Rogério Arthur Friza. *Manual de Direito Agrário Constitucional*. Belo Horizonte: Fórum, 2019. | programacao | alta |
| KRENAK, Ailton. "A União das Nações Indígenas". In: COHN, Sergio (Org.). *Encontros: Ailton Krenak*. Rio de Janeiro: Azougue, 2015. | programacao | alta |
| CAPPELLETTI, Mauro; GARTH, Bryan. *Acesso à Justiça*. Tradução Ellen Gracie Northfleet, 1988. | o-abismo | alta |
| SOUSA JUNIOR, José Geraldo de. *Direito como liberdade...*. Tese (Doutorado), UnB, 2008. | biblioteca-digital | alta |
| `Decreto nº 4.887/2003` — URL do Planalto | programacao | alta |
| LYRA FILHO, Roberto. *Criminologia Dialética*. Rio de Janeiro: Borsoi, 1972. | biblioteca-roberto | alta |
| HERRERA FLORES, Joaquín. *Cultura y derechos humanos desde el Mediterráneo*. 2007. | biblioteca-joaquin | alta |

Na lista de `referencias.html`, o piloto também leu o formato
`"Título", de Autor` e recuperou 61 obras, todas marcadas `baixa` por falta
de ano/editora. Exemplo: `"Pedagogia do oprimido", de Paulo Freire`.

---

## 4. Falsos positivos prováveis e erros de campo

A detecção é conservadora. Na amostra base há 29 registros e apenas 1
`baixa` (um link de página institucional); nenhuma obra foi inventada. Na
amostra dirigida, os erros se concentram em rótulos de link e em campos
incompletos.

| Caso | O que aconteceu | Confiança | Ação sugerida |
|---|---|---|---|
| `Jacques Távora Alfonsin` (PDF) | o texto âncora é um nome de pessoa, não um título | baixa | descartar ou renomear pelo conteúdo do PDF |
| `Sergio Antonio Fabris, editor` | link para o site da editora, não para uma obra | media | tratar como fonte institucional, fora da ABNT |
| `Página do MST` / `Blogue do Hélio Bicudo` | link de página institucional | baixa/media | manter como fonte de contexto, não como obra |
| `Batuqueiros e sua gente` | vídeo/música citado na programação | media | aceitável como fonte audiovisual |
| `Classe trabalhadora e AJUP` | apresentação em Slideshare | media | aceitável como apresentação, não como livro |
| `A Constituição e a Reforma Urbana. Seminário...` | o título absorveu o nome do evento | media | separar título e evento na revisão |
| `Direito e lei` | `veiculo` ficou "Introdução crítica ao direito. Brasília" | alta | cortar a cidade do veículo |
| `BoletimInformativo...` | o original não tem espaço em "BoletimInformativo"; virou livro | alta | corrigir o tipo na revisão |

**Falsos positivos de detecção: 1 a 2 de 245 (0,4% a 0,8%)** — o PDF
"Jacques Távora Alfonsin" e, no limite, "Página do MST"; ambos `baixa`.
Há ainda **6 rótulos de link** (2,4%) que são páginas institucionais ou
apresentações, não obras bibliográficas completas; todos `media` ou `baixa`.
Nenhuma referência `alta` sem autor é prosa: as cinco são legislação
(Decreto/Lei), em que o autor institucional ("BRASIL") será preenchido na
formatação ABNT.

### Erros de campo mais comuns

1. **Coautores separados por ponto no original** ("A. B. C. Título") podem
   ficar só no primeiro autor. O piloto já recupera coautores no formato
   `SOBRENOME, Nome.` antes do título, mas não todos os casos.
2. **Título com pedaço da imprenta** quando falta espaço/pontuação no
   original ("Brasil.Rio de Janeiro:", "Título.3ª Edição").
3. **`veiculo` de capítulo** às vezes inclui a cidade junto do livro.
4. **Tipo** de publicações seriadas com erro de digitação
   ("BoletimInformativo") cai em `livro`.
5. **Ano** de obra cujo único ano é o do título ("1788: ...") fica vazio,
   como deve, mas o registro continua `baixa`.

---

## 5. Limites do piloto

- **Só o corpo do post.** Links e citações que estejam no cabeçalho, na
  ficha de origem, no rodapé ou em "posts relacionados" não entram.
- **Sem rede.** Não há DOI, ISBN, Crossref, Open Library ou verificação de
  link. `url` é apenas o `href` que já existia no HTML.
- **Links genéricos de vídeo foram descartados.** "Ver o vídeo no original"
  não é título; por isso posts que são só um vídeo ficam sub-representados.
  O piloto prefere perder a inventar.
- **Agrupamento de até três parágrafos.** Entradas quebradas em quatro ou
  mais blocos, ou com linhas de metadados não previstas, podem ficar de fora.
- **Autor implícito.** A página `biblioteca-roberto-lyra-filho` é uma lista
  intitulada "Lista de textos de Roberto Lyra Filho"; o piloto usa esse
  título como autor dos registros **sem autor explícito** e grava isso em
  `motivo`. É uma leitura do próprio HTML, não uma inferência externa.
- **Texto original preservado.** Erros de digitação do acervo
  ("sociedadecivil", "Discriminatóriade", "BoletimInformativo") não são
  corrigidos; `trecho` guarda a evidência.
- **`confianca` é heurística**, não revisão humana. 81 registros (33%) estão
  em `baixa` justamente para não serem publicados sem conferência.
- **Snapshot em movimento.** O `_indice.json` tinha 790 entradas e a
  importação dos 78 posts estava em curso. A amostra usou apenas páginas
  existentes; uma nova execução pode escolher outras "10 aleatórias" se o
  índice mudar.

---

## 6. Recomendação para a extração completa

1. **Esperar o acervo fechar em 790** e rodar:
   ```text
   python etl/extrai-referencias.py --tudo --saida dados/referencias.json
   ```
   O custo é local e zero. Estimativa: **1.200 a 1.500 referências**, sendo
   300–450 nas páginas de bibliografia. O piloto levou poucos segundos para
   27 páginas.
2. **Revisar em duas filas:** primeiro as `alta` (formatáveis em ABNT com
   conferência rápida), depois as `baixa`. As 61 de `referencias.html` e os
   15 documentos de `biblioteca-digital` são os maiores lotes de baixa.
3. **Deduplicar de novo no full run.** Já há 4 obras repetidas entre páginas
   na amostra; no acervo inteiro a repetição será maior. Chave:
   título normalizado + autor + ano; guardar todas as `fonte_slug` em uma
   lista `fontes` na versão 2 do schema.
4. **Enriquecer sem pagar:** Open Library/Google Books para ISBN, SciELO e
   BDTD para artigos/teses, Planalto para legislação, YouTube oEmbed para
   vídeos. Respeitar 1–2 s entre requisições, UA
   `finweejur/github artur colito`, cache local e a regra de autorização
   prévia para qualquer API cobrada.
5. **ABNT (NBR 6023:2018):** normalizar `SOBRENOME, Nome`; usar `BRASIL`
   como autor de legislação federal; separar título/subtítulo; tratar
   `Local: Editora, ano`; manter `trecho` como prova. Gerar o documento por
   tema e por autor a partir de `fonte_slug`/`tema` do `_indice.json`.
6. **"Disponível aqui":** só preencher depois de testar o link (HTTP 200,
   conteúdo compatível). O piloto não faz essa verificação.
7. **Não publicar** os registros `baixa` sem revisão. A página pública deve
   mostrar a fonte e o trecho, como o RAG já faz.

---

## 7. Como reproduzir

```text
# amostra do piloto (20 + 7 dirigidas)
python etl/extrai-referencias.py

# só a amostra base, sem as páginas de bibliografia
python etl/extrai-referencias.py --sem-dirigidas

# acervo inteiro
python etl/extrai-referencias.py --tudo --saida dados/referencias.json

# conferir cada referência no terminal
python etl/extrai-referencias.py --debug
```

A semente da amostra aleatória é `20261122`; as 10 primeiras vêm da ordem do
`_indice.json` (mais recentes primeiro).

---

## 8. Arquivos

| Arquivo | Estado |
|---|---|
| `etl/extrai-referencias.py` | novo; só lê HTML e grava o JSON de saída |
| `dados/referencias-piloto.json` | novo; 245 registros, ~152 KB, UTF-8 |
| `docs/REFERENCIAS-PILOTO.md` | este relatório |

Nada foi commitado, publicado ou alterado em HTML/CSS/JS, `_indice.json` ou
nos `dados/*.json` existentes.
