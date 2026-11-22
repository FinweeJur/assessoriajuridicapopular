# Busca externa das referências — o que foi feito e o que ficou

> **Data:** 22/11/2026
> **Entrada:** `dados/referencias.json` (790 posts lidos)
> **Saída:** `dados/referencias-externas.json` (candidatas e evidências)
> **Scripts:** `etl/busca-referencias-externas.py` e ajustes em
> `etl/extrai-referencias.py`
> **Custo:** zero. Nenhuma API paga, nenhum login, nenhum paywall.

## 1. A pergunta

“Como assim confiança baixa? Como assim sem autor identificado, no blog
original não tem?”

A resposta curta: **na maioria dos casos o blog original não trazia aquele
dado no trecho citado — e uma parte do que aparecia como ‘sem autor’ nem era
referência, era frase do post.** O extrator estava errado em três pontos, e
foi corrigido.

## 2. O que estava errado no extrator

| Defeito | Exemplo | Correção |
|---|---|---|
| Marcador de lista virava parte do autor | `[1] BOAL, Augusto. Teatro do oprimido…` | `limpa_rotulo` remove `[1]`, `(1)`, `1)` e `Resenha -` |
| Autor colado no título | `LÖWY, Michael. "Introdução…` | `autor_embutido` separa `SOBRENOME, Nome` antes do título |
| Autor depois do título | `"Perspectivas…", de Autor, em 21 de janeiro de 2010` | a data vira ano e o autor sai limpo |
| Frase do post lida como referência | `Nós somos os colaboradores do blogue…` | `ruido_narrativo` descarta abertura de frase, endereço, programação e nota de rodapé |
| Nome com acento estrangeiro | `LÖWY`, `CLÈVE` | tokenização Unicode, não só o alfabeto português |
| Site sem autor | links para Brasil de Fato, IHU, Google Drive | **autoria institucional**: a organização responsável pela página |
| Link institucional duplicando referência com autor | mesmo título em link e em citação | fica a versão com autor pessoal |

## 3. Números antes e depois

| Medida | Antes | Depois |
|---|---:|---:|
| Referências extraídas | 606 | 524 |
| Sem autor | 250 | **35** |
| Com autoria institucional | 0 | 143 |
| Confiança alta | 221 | 225 |
| Confiança média | 149 | 153 |
| Confiança baixa | 236 | 146 |
| Entradas únicas na lista ABNT | 599 | 515 |

Das 35 sem autor que restaram:

- **19 são vídeos** (YouTube/Vimeo). A ABNT aceita entrada por título:
  `TÍTULO. YouTube, ano.` — não falta autor, falta a regra de autoria pessoal.
- **7 são legislação**. A ABNT usa `BRASIL. Lei n. …` — o gerador já faz isso.
- **9 são lacunas reais**: 4 artigos, 2 livros, 2 monografias e 1 tese.

## 4. Fontes consultadas

| Fonte | Situação | Uso |
|---|---|---|
| Google Books (feed GData) | funcionou | títulos, autores, editora, ano |
| Crossref | funcionou | artigos e teses com DOI |
| OpenAlex | funcionou; 429 após ~140 consultas seguidas | teses e artigos com DOI/repositório |
| Internet Archive (advancedsearch) | funcionou | livros digitalizados |
| Open Library | inacessível por timeout nesta rede | — |
| Google Books API v1 | cota diária esgotada (429) | — |
| SciELO e Library of Congress | 403 | — |
| BDTD | `robots.txt` bloqueia a busca | não usado |
| CAPES | exige login | não usado |

Regras seguidas: User-Agent `finweejur/github artur colito`, 1,5 s entre
requisições, nenhuma tentativa de contornar bloqueio, `robots.txt` respeitado.

## 5. O que a busca externa acrescentou

Foram consultadas 35 referências com lacuna de autor ou ano. Quatro foram
completadas com evidência:

| Referência | Complemento | Evidência |
|---|---|---|
| Advocacia popular: utopia e ação política | André Luiz Conrado Mendes, 2011, PUC-Rio | DOI 10.17771/pucrio.acad.38673 |
| Da pedagogia do oprimido ao direito do oprimido | José Humberto de Góes, 2008, UFPB | repositório.ufpb.br/handle/123456789/33448 |
| Sem porta-voz na rua, sem dono em casa… | Diana Melo Pereira, 2015, UnB | DOI 10.26512/2015.04.d.18885 |
| Filosofia, teologia e experiência mística | Roberto Lyra Filho, 1974, Instituto Brasileiro de Filosofia | Crossref |

Cada uma guarda `autor_fonte`, `evidencia_url` e `match_titulo` no JSON. Nada
foi completado por memória ou por semelhança frouxa: o aceite exige F1 alto
entre os títulos e, quando já havia autor, sobrenome compatível.

## 6. Por que 31 não foram encontradas

- **Não são referências bibliográficas**: endereço de sede, programação de
  seminário, título de revista citado como link, chamada de matéria. O filtro
  novo já remove a maior parte; os poucos que sobraram ficam visíveis para
  revisão.
- **Teses e monografias brasileiras antigas**: não estão no Google Books nem
  no Crossref; estão no BDTD e nos repositórios institucionais, cuja busca
  automatizada é bloqueada por `robots.txt` ou exige login.
- **Obras raras da assessoria jurídica popular** (anos 1980–1990): muitas só
  existem em acervo físico, sem registro em catálogo online aberto.
- **Posts do próprio blogue**: já entram com autor e data; quando o texto não
  trazia ano, a ABNT usa `[s.d.]`, que é lacuna da fonte, não falha de leitura.

## 7. Como ler os rótulos agora

A página e o documento passaram a dizer o que o rótulo mede:

| Rótulo | Significado |
|---|---|
| **Referência completa** | autoria, título, ano e imprenta/veículo reconhecidos no texto |
| **Referência parcial** | autoria e título reconhecidos; falta ano, imprenta ou veículo |
| **Dados incompletos** | o post original não trazia o dado suficiente |

Nenhum rótulo diz que a obra não existe. “Dados incompletos” é uma medida de
**extração**, não de qualidade da obra.

## 8. Como repetir

```bash
python etl/extrai-referencias.py --tudo --saida dados/referencias.json
python etl/busca-referencias-externas.py            # consulta e grava candidatas
python etl/busca-referencias-externas.py --aplicar  # aplica só o que passou no teste
python etl/monta-referencias-abnt.py
python etl/monta-referencias-pagina.py
python etl/marca-referencias-post.py
python etl/audita-referencias-abnt.py
```

O auditor falha se voltar a aparecer `[s.l.]` falso, autoria quebrada,
duplicata, sufixo ausente ou contagem divergente.
