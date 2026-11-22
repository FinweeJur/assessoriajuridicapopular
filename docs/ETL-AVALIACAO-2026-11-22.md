# Avaliação crítica do ETL — Acervo AJP

> **Data:** 22/11/2026
> **Escopo:** repositório `X:\DevCoder\assessoriajuridicapopular`, blog
> `assessoriajuridicapopular.blogspot.com` e sites institucionais das redes.
> **Estado do site:** commit `d04ac0e7d`, publicado em
> <https://finweejur.github.io/assessoriajuridicapopular/>.
> **Método:** leitura do feed Atom, do `sitemap.xml`, do `robots.txt` e das
> páginas públicas com User-Agent `finweejur/github artur colito`, 1,2–2 s entre
> requisições. Instagram e Facebook **não** foram raspados: os robots/termos da
> Meta proíbem coleta automatizada. Os perfis sociais registrados são os que os
> sites oficiais publicam — mais o `@ajupsbrasil`, informado pelo dono.

---

## Resumo em uma frase

O ETL entregou um acervo estático bonito, pesquisável e com RAG extrativo, mas
**não está completo nem é reproduzível**: faltam 78 dos 790 posts (2014 inteiro),
há uma colisão de slug que contaminou o RAG, e a camada comunitária do blog
(blogues parceiros, entidades, mapeamento de AJUPs, quem somos, como postar)
ficou fora do site.

### Números de controle

| Item | Medido em 22/11/2026 |
|---|---:|
| Posts declarados pelo blog | **790** |
| Posts entregues pelo feed baixado | 713 |
| Entradas no `_indice.json` | 713 |
| Páginas de post com `canonical` para o blog | **712** |
| Páginas HTML no repositório | 765 |
| Seções editoriais | 5 |
| Cartões na Biblioteca | 18 (7 categorias originais + 11 obras) |
| Poemas no Caderno | 135 |
| Blogues parceiros no blog original | 21 |
| Entidades parceiras no blog original | 12 |
| Organizações no mapeamento de 2011 | 40 (12 advocacias + 25 AJUPs + 3 movimentos) |
| Posts do blog sem página local | **78** |
| Posts regulares perdidos na paginação | **73** |
| Post perdido por colisão de slug | **1** |
| Posts que eram páginas/gadgets | **4** |
| RAG | 713 registros |
| Perguntas curadas do chatbot | 16 |
| Rádio | 52 estações |

---

## 1. O que fizemos

### 1.1 Pipeline

```
feed Atom + HTML dos posts (G:\Meu Drive\RENAP-AJP)
        │
        ├─ extract ............ 713 posts baixados de 790
        ├─ parse .............. título, data, autor, corpo, resumo, tema, tipo
        ├─ classificação ...... 5 seções, temas secundários, palavras-chave
        ├─ load ............... _indice.json + 1 página HTML por post
        ├─ enriquecimento ..... autores, biblioteca, poemas, RAG, sitemap
        └─ publicação ......... GitHub Pages, 765 HTML, sem framework
```

### 1.2 O que o site tem hoje

- **Cinco portas:** Home, Acervo, Biblioteca, Mística e IA.
- **713 entradas** no índice, distribuídas em cinco seções:
  Movimentos 194 · AJP 169 · Educação 128 · Direitos humanos 119 · Teoria 103.
  A soma dá 713 porque uma entrada é, na verdade, uma página de seção
  (ver §3.2).
- **712 posts reais** com `canonical` para o original.
- Busca filtrável por texto, ano, tipo, palavra-chave, rede e ordem.
- Páginas de autor, coleções, glossário, linha do tempo, memória e cultura.
- **Biblioteca** com 18 cartões: Biblioteca digital, AJUP-RJ, Roberto Lyra
  Filho, Miguel Lanzellotti Baldez, Joaquín Herrera Flores, Filosofia
  latino-americana, Monografias, Referências, Poesia crítica do direito,
  teses, livros e o dossiê comparado.
- **Caderno de Poesias** com 135 poemas e 42 posts de poesia do blog.
- **RAG local** (`dados/rag.json`) com 713 registros e resposta extrativa, sem
  geração livre; 16 perguntas curadas.
- **Rádio** com 52 estações do Controle Popular, índice em duas colunas,
  bandeiras, logos, volume com líquido e dica de 1 s.
- **IA** com comparado, panorama de referências e prompt anti-alucinação.
- **Nove temas**, responsividade 390/768/1440, alto contraste e foco visível.

### 1.3 O que funcionou bem

1. **Citação com proveniência:** cada página tem autor, data, link canônico e
   “capturado em”.
2. **RAG extrativo:** o chatbot devolve trechos com link em vez de inventar.
3. **Classificação útil:** o rebalanceamento de 294 posts deixou as cinco
   seções mais equilibradas e a navegação por tema ficou legível.
4. **Biblioteca e poesia:** o acervo não ficou só em “posts”; há curadoria de
   obras, teses, cadernos e poemas.
5. **Site estático:** rápido, portátil, sem dependência de runtime e fácil de
   publicar no GitHub Pages.

---

## 2. O que ficou pendente

### 2.1 Lacuna de extração: 78 posts

O blog declara **790** posts no feed. O download gravou **713**. A diferença
não é editorial: é um **bug de paginação**.

`etl/baixa-ajp.py` pede `max-results=150` e avança `indice += 150`, mas o feed
devolveu:

| Arquivo | Entradas | Primeiro post | Último post |
|---|---:|---|---|
| `feed-0001.json` | 100 | 2024-07-12 | 2015-03-24 |
| `feed-0002.json` | 123 | 2013-09-06 | 2011-12-20 |
| `feed-0003.json` | 150 | 2011-10-11 | 2011-05-08 |
| `feed-0004.json` | 150 | 2011-05-04 | 2010-09-14 |
| `feed-0005.json` | 150 | 2010-09-14 | 2009-12-23 |
| `feed-0006.json` | 40 | 2009-12-22 | 2009-08-16 |

Quando a página 1 devolveu 100 (e não 150), o código pulou o intervalo
101–150. Quando a página 2 devolveu 123, pulou 274–300. Resultado: **2014
inteiro ficou de fora** e boa parte de 2011, 2013 e 2015 também.

| Ano | Blog | Local | Falta |
|---|---:|---:|---:|
| 2009 | 43 | 43 | 0 |
| 2010 | 202 | 201 | 1 |
| 2011 | 275 | 248 | 27 |
| 2012 | 91 | 91 | 0 |
| 2013 | 35 | 29 | 6 |
| 2014 | 35 | 0 | **35** |
| 2015 | 59 | 50 | 9 |
| 2016–2024 | 50 | 50 | 0 |
| **Total** | **790** | **712** | **78** |

A lista completa está em `docs/etl-lacunas-2026-11-22.csv`.

**Correção:** pedir `max-results=100`, avançar `start-index += len(entradas)` e
repetir até `totalResults` ou lista vazia. Depois, rebaixar os 78, rodar o
parser, regenerar `_indice.json`, páginas, seções, RAG e sitemap. O aceite é
`790` URLs do sitemap cobertas ou uma justificativa explícita por exceção.

### 2.2 Colisão de slug e RAG contaminado

Há um caso que resume o risco de gerar HTML em vez de manter conteúdo
normalizado:

- O post **“Assessoria Jurídica Popular”**, de Betânia Alfonsin (2010-04-26),
  tem slug `assessoria-juridica-popular`.
- A seção **“O que é assessoria jurídica popular”** usa o mesmo slug em
  `etl/monta-secoes.py`.
- A página da seção sobrescreveu a página do post.
- O `_indice.json` continua listando o post; o `rag.json` do slug
  `assessoria-juridica-popular` contém o texto da **seção**, não o do post.
- A página `assessoria-juridica-popular.html` não tem `canonical`.

Impacto: busca, RAG e contagem mentem sobre esse registro. O leitor que procura
o texto de Betânia encontra a seção. **Prioridade máxima.**

**Correção:** reservar slugs de seção no parser; dar sufixo ao post
(`assessoria-juridica-popular-2010`); reconstruir o RAG a partir do conteúdo
normalizado (não do HTML renderizado); adicionar `canonical` ao post.

### 2.3 Pipeline não reproduzível

Hoje o ETL é uma coleção de scripts de mutação:

- os originais estão em `G:\Meu Drive\RENAP-AJP`, fora do repositório;
- o índice vive na raiz (`_indice.json`), não em `dados/`;
- 765 HTML são reescritos no lugar por scripts diferentes;
- a ordem dos scripts importa e não está documentada em um `run`;
- não há teste de contagem, de canonical ou de link;
- rodar de novo em outra máquina não reproduz o site.

**Correção:** um `etl/run.py` com estágios (`extract`, `parse`, `classify`,
`build`, `enrich`, `validate`), checkpoint, `--dry-run`, `--only-missing`,
manifesto com hashes e um `make check` que falha se a contagem não fechar.

### 2.4 Autorização jurídica não documentada

O plano (`docs/PLANO-ETL-ASSESSORIA-JURIDICA-POPULAR.md`, §3) previa três
cenários: autorização, citação de até 30% ou resumo. O repositório **não tem**
`docs/autorizacoes/` nem registro de resposta dos autores. O site publica o
corpo integral com `canonical` para o original.

Isso é o risco jurídico nº 1. Antes de ampliar o acervo, é preciso:

1. arquivar autorização escrita por autor/coletivo; ou
2. reduzir o regime para citação, com o campo `licenca` no registro; ou
3. remover o que não tiver base.

A página deve se adaptar ao campo `licenca` (`autorizado`, `citacao`,
`resumo`), como o plano já previa.

### 2.5 Camada comunitária do blog ficou fora

O site reproduziu os **textos**, mas não a **rede** que dava sentido ao blog:

| Item do blog original | Estado no site | Evidência |
|---|---|---|
| Blogues parceiros (21) | **ausente** | 0 ocorrências de “Blogues parceiros” |
| Entidades parceiras (12) | **ausente** | 0 ocorrências de “Entidades parceiras” |
| Mapeamento de AJUPs (40) | **ausente como página** | o post de 2011 está entre os 78 perdidos |
| Movimentos sociais | **seção de textos** (194), não diretório | `movimentos-sociais.html` |
| Quem somos | **ausente** | sem `quem-somos.html` |
| Como postar | **ausente** | 0 ocorrências de “Como postar” |
| Colunistas | **reproduzido** como `autores.html` | 5 colunistas + autores |
| Cadernos insurgentes | **reproduzido** na Biblioteca | `biblioteca.html#renap` e seção IPDMS |
| Bibliotecas | **reproduzido** com 18 cartões | `biblioteca.html` |
| Poesia crítica do direito | **existe como página**, mas não como hub | `poesia-critica-do-direito.html` |
| Referências de AJP | **reproduzido** | `referencias.html` |

### 2.6 Poesia e bibliotecas: respostas diretas

**“Poesia crítica do direito entrou como uma página?”**

Sim. `poesia-critica-do-direito.html` existe, é um post de 2012 e aparece no
`poemas.html` como destaque. O `poemas.html` reúne 135 poemas e 42 posts de
poesia. O que falta:

- a página não é um **hub de seção**; é um post;
- o cartão da Biblioteca aponta para o Blogspot, não para a página local;
- não há ficha de “poesia crítica” com autores, período e critério de inclusão;
- o texto “Nova página Poesia crítica do direito” (2011) está entre os 78
  perdidos, então a história da seção não está no acervo.

**“As bibliotecas citadas?”**

As sete categorias da página
<https://assessoriajuridicapopular.blogspot.com/p/bibliotecas.html> estão no
`biblioteca.html` e no `dados/biblioteca.json`:

1. Biblioteca digital da assessoria jurídica popular;
2. Biblioteca AJUP-RJ;
3. Biblioteca Joaquín Herrera Flores;
4. Biblioteca Miguel Lanzellotti Baldez;
5. Biblioteca Roberto Lyra Filho;
6. Poesia crítica do direito;
7. Referências de assessoria jurídica popular.

O site acrescentou 11 obras (teses, monografias, livros, filosofia
latino-americana e o dossiê comparado). O problema é de **ligação e estado**:
Poesia e Referências ainda apontam para o Blogspot; falta “fonte” e “última
verificação” em cada cartão; e não há uma página de bibliotecas parceiras
externas (por exemplo, a Biblioteca da RENAP e a do IPDMS).

### 2.7 Link rot

Dos 21 blogues parceiros, **19 responderam** ao teste de 22/11/2026; falharam
Agência Carta Maior e SAJU UFRGS. Das 12 entidades, **9 têm site ativo** (AATR
via HTTPS); não responderam Mariana Criola, GAJOP e SDDH-PA. O blogroll não pode
ser copiado de 2011 sem status e data.

### 2.8 Instagram e Facebook: o que foi possível

Os robots de Instagram e Facebook dizem explicitamente que a coleta automatizada
é proibida sem autorização. Por isso:

- **não** abri perfis, não listei posts e não coletei seguidores;
- registrei os links que os sites oficiais publicam;
- o `@ajupsbrasil` foi informado pelo dono e entra como **pendente de
  confirmação manual**;
- onde o site antigo morreu, o perfil não foi inventado.

Isso deve virar regra no mapa: cada ficha tem `fonte`, `verificado_em` e
`status`, e a verificação de Instagram/Facebook é manual, no app.

### 2.9 Documentação e contagem

O `README.md` ainda diz que o download está em andamento e que o deploy é
Cloudflare Pages. O site está no GitHub Pages e o acervo tem 713 entradas
(712 posts reais). O número “713 textos” precisa ser corrigido para “712 posts
+ 1 página de seção” até a importação dos 78; depois, 790.

### 2.10 RAG e busca

O RAG é lexical, sem embeddings, e foi construído a partir do **HTML
renderizado**. Isso o torna vulnerável a qualquer colisão de slug (ver §2.2) e
limita a recuperação semântica. Não há conjunto de avaliação com perguntas e
respostas esperadas. Recomendação: construir o RAG a partir do conteúdo
normalizado, criar 30–50 perguntas de avaliação, medir recall@4 e manter a
resposta extrativa.

---

## 3. O que ficou pendente, em ordem de prioridade

### P0 — corrigir a base (1–3 dias)

| # | Ação | Aceite |
|---|---|---|
| 1 | Corrigir a paginação do feed | 790 URLs baixadas; `feed-*.json` com 790 entradas; 0 lacuna por ano |
| 2 | Rebaixar e parsear os 78 | 78 páginas novas; `_indice.json` com 790 posts (ou 786 + 4 páginas) |
| 3 | Resolver a colisão `assessoria-juridica-popular` | post e seção em URLs distintas; `canonical` no post; RAG sem texto de seção |
| 4 | Reconstruir RAG, índice, seções e sitemap | contagens fecham; busca não mostra página errada |
| 5 | Decisão jurídica registrada | `docs/autorizacoes/` ou `licenca: citacao` aplicada |
| 6 | Manifesto e checagem | `dados/manifest.json`; `make check` falha se contagem/canonical/link quebrar |

### P1 — repor a camada comunitária (1–2 semanas)

1. **Criar `rede.html`** (sexta porta ou seção da Home) com:
   Quem somos · Como postar · Blogues parceiros · Entidades parceiras ·
   Movimentos sociais · Mapeamento de AJUPs · Colunistas · Cadernos.
2. **Mapeamento de AJUPs:** `dados/ajups.json` + `mapeamento-ajups.html`.
   Partir de `docs/mapeamento-ajups-2011.md`, preencher com
   `docs/redes-2026-11-22.json`, filtrar por tipo/UF/rede, mostrar
   “verificado em” e um caminho “este link mudou?”.
3. **Blogues parceiros:** página com os 21 links, status (ativo/fora do ar),
   data do teste e uma nota histórica. Revisar os 2 que falharam.
4. **Entidades parceiras:** página com as 12, site/redes e status; 3 estão sem
   site e precisam de confirmação manual.
5. **Movimentos sociais:** separar a **seção de textos** (194) de um
   **diretório de movimentos** (MST, MTST, Levante, MAB, MPA, etc.), com links
   oficiais e data.
6. **Poesia:** transformar `poesia-critica-do-direito.html` em hub (ou criar
   `poesia-critica.html`), ligar o cartão da Biblioteca à página local e listar
   os 135 poemas por autor/período.
7. **Bibliotecas:** ligar Poesia e Referências ao local; adicionar “fonte” e
   “última verificação”; criar uma seção de bibliotecas externas (RENAP, IPDMS).
8. **Quem somos / Como postar:** recuperar as duas páginas do blog (a de “Como
   postar” está fora do feed de posts; é página estática) e adaptar a política
   editorial ao site.

### P2 — tornar o ETL sustentável (2–4 semanas)

1. `etl/run.py` com estágios, checkpoint, `--dry-run`, `--only-missing`,
   `--validate`; `make` para os comandos.
2. Separar conteúdo normalizado (`content/*.json`) de apresentação
   (`public/*.html`); parar de reescrever 765 HTML no lugar.
3. Partial de topo/rodapé/rádio/chat para não injetar o mesmo bloco em 765
   arquivos.
4. Testes: contagem, canonical único, links internos, links externos, HTML
   válido, contraste, 390/768/1440.
5. RAG: 30–50 perguntas de avaliação, recall@4, limiar de “não achei” e
   reconstrução a partir do conteúdo, não do HTML.
6. Arquivar raw do feed e dos posts com hash (fora do repo ou em `raw/` com
   política de licença), para provar o que foi capturado.
7. Atualizar README, home e painel de estado com os números reais.
8. Registro de redes: data, fonte, status, responsável; nunca raspar Meta.

---

## 4. Pesquisa de redes e repositórios (22/11/2026)

### 4.1 Método

- Sites oficiais lidos com User-Agent identificado; `robots.txt` consultado.
- 1,2–2 s entre requisições.
- Instagram/Facebook **não** acessados por automação; links extraídos dos sites
  oficiais ou informados pelo dono.
- Onde o domínio não resolve, o status é `site_fora_do_ar`; não se inventa
  perfil.

### 4.2 Principais redes

| Rede | Site | Instagram | Facebook | YouTube | Repositório/publicações |
|---|---|---|---|---|---|
| RENAP | <https://www.renap.org.br/> | [@renapbrasil](https://www.instagram.com/renapbrasil/) | — | — | [Cadernos 1–6 + Defensoria](https://www.renap.org.br/publicacoes) |
| RENAJU/AJUPs | site antigo fora do ar | [@ajupsbrasil](https://www.instagram.com/ajupsbrasil/) *(informado pelo dono)* | — | — | mapeamento histórico de 25 grupos |
| IPDMS | <https://ipdms.org.br/> | — | [/Ipdms](https://www.facebook.com/Ipdms/) | — | [Publicações](https://ipdms.org.br/publicacoes/) · Biblioteca · InSURgência |
| Controle Popular | <https://www.controlepopular.com.br/> | — | — | — | [GitHub FinweeJur](https://github.com/FinweeJur) · Telegram |
| AATR-BA | <https://www.aatr.org.br/> | [@aatrba](https://www.instagram.com/aatrba) | [/aatrba](https://www.facebook.com/aatrba/) | [canal](https://www.youtube.com/channel/UCG81NgFRlWOZvcHATrzo7ww) | [Acervo](https://www.aatr.org.br/acervo) |
| Terra de Direitos | <https://terradedireitos.org.br/> | [@terradedireitos](https://www.instagram.com/terradedireitos) | [/terradedireitos](https://www.facebook.com/terradedireitos) | [canal](https://www.youtube.com/channel/UCkdy0w7C6RAAYXRn9gZIxUQ) | [Biblioteca](https://terradedireitos.org.br/biblioteca/publicacoes) |
| Themis | <https://themis.org.br/> | [@themis.org.br](https://www.instagram.com/themis.org.br/) | [/themis.org.br](https://www.facebook.com/themis.org.br) | [canal](https://youtube.com/@themisgenerojusticaedireit2128) | [Publicações](https://themis.org.br/publicacoes-e-obras/) |
| Justiça Global | <https://www.global.org.br/> | [@justicaglobal](https://www.instagram.com/justicaglobal/) | [/justicaglobal](https://www.facebook.com/justicaglobal) | [canal](https://www.youtube.com/user/JusticaGlobalBrasil) | [Publicações](https://www.global.org.br/publicacoes/) |
| Conectas | <https://www.conectas.org/> | [@conectas](https://www.instagram.com/conectas/) | [/conectas](https://www.facebook.com/conectas) | [canal](https://www.youtube.com/channel/UCem6mFvn8C3bHe04doW2h0w) | [Publicações](https://conectas.org/publicacoes/) |
| CLADEM | <https://www.cladem.org/> | [@clademregional](https://www.instagram.com/clademregional/) | [/REDCLADEM](https://www.facebook.com/REDCLADEM) | [canal](https://www.youtube.com/@CLADEMenvideo) | [Biblioteca](https://cladem.org/bibliotecas) |
| SMDH-MA | <https://smdh.org.br/> | [@smdhvida](https://www.instagram.com/smdhvida/) | [/smdh.vida](https://www.facebook.com/smdh.vida/) | [canal](https://www.youtube.com/user/SMDHVida) | [Publicações](https://smdh.org.br/publicacoes/) |
| ABIA | <https://abiaids.org.br/> | [@abia.abiaids](https://www.instagram.com/abia.abiaids/) | [/ABIAIDS](https://www.facebook.com/ABIAIDS/) | [canal](https://www.youtube.com/user/ABIAGAPW) | site |
| Dignitatis | [blogspot](http://dignitatis-assessoria.blogspot.com/) | — | — | — | — |

### 4.3 Onde o site antigo morreu

| Organização | Status em 22/11/2026 |
|---|---|
| Mariana Criola (RJ) | `marianacriola.org.br` não resolve; perfil não confirmado |
| GAJOP-PE | `gajop.org.br` não resolve; perfil não confirmado |
| SDDH-PA | `sddh.kit.net` não responde; perfil não confirmado |
| Acesso (RS) | `acesso.org.br` não resolve; perfil não confirmado |
| Frei Tito (CE) | `escritoriofreitito.org.br` não resolve; perfil não confirmado |
| RENAJU | `renaju.org.br` não resolve; usar o `@ajupsbrasil` informado pelo dono e confirmar manualmente |

### 4.4 Blogues parceiros (histórico)

Os 21 links estão em `docs/links-parceiros-2026-11-22.json`, com status e
título. Resumo: **19 responderam**; Agência Carta Maior e SAJU UFRGS falharam no
teste automatizado. A lista inclui Afroblogs, Carta Maior, Alexandre Morais da
Rosa, Blogue do Baldez, Café & Direito, Coletivo Sankofa, Combate Racismo
Ambiental, Diálogos Lyrianos, Direito Achado na Rua, Direito Público e
Diversidade, Em Crisálida, Mara Paula, Marxismo21, NAJUP Cabano, O caminho se
faz caminhando, O palco e o mundo, SAJU UFBA, SAJU UFRGS, Tânia Defensora, Vila
do Chocolatão e Vladimir Luz.

### 4.5 Entidades parceiras (histórico)

As 12 estão no mesmo JSON. **9 têm site ativo** em 22/11/2026: ABIA, AATR
(HTTPS), CLADEM, Conectas, Dignitatis, Justiça Global, SMDH, Terra de Direitos e
Themis. Sem site: Mariana Criola, GAJOP e SDDH-PA.

---

## 5. Respostas diretas às perguntas

**“Blogues parceiros?”**
Não foram reproduzidos. O site tem 0 ocorrências. Há 21 links históricos, 19
ativos; falta uma página com status, data e nota de que é um blogroll de época.

**“Movimentos sociais?”**
Existe como **seção de textos** (`movimentos-sociais.html`, 194 posts), mas não
como **diretório de movimentos**. O mapeamento de 2011 lista Levante Popular da
Juventude, MST e Resistência Popular. Falta uma página de organizações, com
links oficiais e data.

**“Mapeamento de AJUPs?”**
Não existe como página. O post “Mapeamento” (2011) é um dos 78 perdidos pela
paginação. O conteúdo histórico foi extraído para
`docs/mapeamento-ajups-2011.md` (12 advocacias + 25 AJUPs + 3 movimentos). O
mapa atual precisa de `dados/ajups.json` e de verificação manual.

**“Poesia crítica do direito entrou como uma página?”**
Sim, como post (`poesia-critica-do-direito.html`) e como destaque no
`poemas.html` (135 poemas). Não é um hub de seção; o cartão da Biblioteca ainda
aponta para o Blogspot. Falta amarrar a página local, os autores e a história da
seção.

**“As bibliotecas citadas?”**
As sete categorias originais estão no `biblioteca.html` e no
`dados/biblioteca.json`, com 18 cartões no total. Falta corrigir os links de
Poesia/Referências para o local, registrar fonte e última verificação e incluir
as bibliotecas externas (RENAP, IPDMS).

---

## 6. Artefatos desta auditoria

| Arquivo | O que contém |
|---|---|
| `docs/ETL-AVALIACAO-2026-11-22.md` | este relatório |
| `docs/etl-lacunas-2026-11-22.csv` | os 78 URLs do blog sem página canônica |
| `docs/links-parceiros-2026-11-22.json` | 21 blogues + 12 entidades, status e redes |
| `docs/redes-2026-11-22.json` | redes atuais, sites, Instagram/Facebook/YouTube e repositórios |
| `docs/mapeamento-ajups-2011.md` | lista histórica de 40 organizações, com links de 2011 |
| `etl/audita-acervo.py` | auditoria reprodutível: cobertura, lacunas, canonical e colisões (baixa o sitemap com UA se não houver cópia local) |
| `~/.config/opencode/skills/ajp/SKILL.md` | skill global `ajp` |
| `~/.config/opencode/command/ajp.md` | comando `/ajp` |

---

## 7. Comandos e ordem atual do ETL

```text
0. python etl/audita-acervo.py        # cobertura, lacunas, canonical, colisões
1. python etl/baixa-ajp.py feed       # grava G:\Meu Drive\RENAP-AJP\feed
2. python etl/baixa-ajp.py posts      # grava G:\Meu Drive\RENAP-AJP\posts
3. python etl/parse-ajp.py            # gera _indice.json / páginas
4. python etl/monta-paginas.py
5. python etl/monta-secoes.py
6. python etl/tema-principal.py       # rebalanceamento das 5 seções
7. python etl/monta-rag.py            # hoje lê o HTML renderizado
8. python etl/valida-ajp.py
```

Hoje o passo 0 termina com `ACERVO INCOMPLETO` e lista as 78 URLs. Essa ordem
não está automatizada. O próximo passo é substituí-la por `etl/run.py` com as
etapas e os testes do §3.

---

## 8. Fontes

- Blog: <https://assessoriajuridicapopular.blogspot.com/>
- Feed: <https://assessoriajuridicapopular.blogspot.com/feeds/posts/default?alt=json>
- Sitemap: <https://assessoriajuridicapopular.blogspot.com/sitemap.xml>
- Bibliotecas: <https://assessoriajuridicapopular.blogspot.com/p/bibliotecas.html>
- Mapeamento: <https://assessoriajuridicapopular.blogspot.com/2011/10/mapeamento.html>
- Quem somos: <https://assessoriajuridicapopular.blogspot.com/p/quem-somos.html>
- Como postar: <https://assessoriajuridicapopular.blogspot.com/p/como-postar.html>
- Site: <https://finweejur.github.io/assessoriajuridicapopular/>
- Repositório: <https://github.com/FinweeJur/assessoriajuridicapopular>
- RENAP: <https://www.renap.org.br/>
- IPDMS: <https://ipdms.org.br/>
- Controle Popular: <https://www.controlepopular.com.br/>

---

## 9. Nota sobre o que não foi feito

Não tentei “consertar” o acervo nesta auditoria. O objetivo foi medir, registrar
e priorizar. A importação dos 78, a página de rede e o mapa de AJUPs são
trabalho de implementação — e devem começar pelo P0, porque qualquer página
nova construída sobre 713 posts herdará a lacuna de 2014 e a colisão de slug.
