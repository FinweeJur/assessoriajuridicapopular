# Assessoria Jurídica Popular — acervo

Site do acervo de textos sobre **assessoria jurídica popular**, publicado com
citação direta, crédito, link canônico e botão para o original e para o autor.

**No ar:** <https://finweejur.github.io/assessoriajuridicapopular/>

**Publicação:** GitHub Pages, branch `master`, raiz do repositório, com
`.nojekyll`. O nome `assessoriajuridicapopular.pages.dev` fica como plano B
(Cloudflare Pages).

## O que tem aqui

```
index.html                     capa do acervo: busca, categorias e lista
acervo.html                    790 textos com busca e filtros
rede.html                      quem somos, como postar, blogues, entidades e movimentos
mapeamento-ajups.html          mapa histórico + verificação de 2026
referencias-citadas.html       referências em ABNT, com “Disponível aqui”
o-que-e-assessoria-juridica-popular.html   primeiro texto publicado
_modelo.html                   gabarito para as próximas páginas
acervo.css                     estilos do acervo
reveal.css / reveal.js         entrada dos blocos ao rolar (sem biblioteca)
fontes/                        Clash Display, General Sans, Satoshi, Fraunces…
temas/                          nove temas de cor
logos/                         RENAP, IPDMS e MAB
etl/                           download, parser, auditoria e geração
docs/                          plano, avaliação, referências e pesquisa de redes
```

## Parceria

Publicação e curadoria em parceria com o **IPDMS — GT de Assessoria Jurídica
Popular**, com **RENAP** e **MAB**. A parceria é de publicação e curadoria, não
de autoria: cada texto continua assinado por quem escreveu.

## Como publicar

1. GitHub Pages, branch `master`, pasta raiz, com `.nojekyll`.
2. Build command: *(vazio)*. Output directory: `/`.
3. Plano B: Cloudflare Pages, projeto `assessoriajuridicapopular`
   (`assessoriajuridicapopular.pages.dev`).

## Regras

- Citação direta, sem reescrever a grafia do autor.
- Toda página tem: autor, data, link do original e data de captura.
- Bloco de citação com `blockquote cite=` e “Ler no blog original” inline na
  ficha, no mesmo tamanho do texto; sem botões grandes depois da citação.
- Fonte mínima 12 px; 390 px sem rolagem lateral; contraste medido.
- Nada de conteúdo copiado sem licença: imagem sem crédito entra como link.

## Estado em 22/11/2026

- [x] Estrutura em cinco portas de conteúdo + **Rede**: Home, Acervo, Biblioteca,
      Rede, Mística e IA
- [x] Faixa de parcerias com as três logos
- [x] Busca, temas, autores, coleções e páginas de texto
- [x] Biblioteca, caderno de poesias, rádio e RAG local
- [x] **790 dos 790 posts** do blog com página e `canonical`
- [x] `rede.html`: Quem somos, Como postar, Blogues parceiros, Entidades,
      Movimentos, Mapeamento, Colunas e Bibliotecas
- [x] `mapeamento-ajups.html`: 38 organizações históricas + 2 redes atuais
- [x] `referencias-citadas.html`: 515 entradas únicas em ABNT (524 extraídas),
      102 links abertos, 4 restritos, 70 mortos, 337 sem link; 143 com
      autoria institucional e 4 completadas por busca externa
- [x] `python etl/audita-acervo.py` verde: 790/790, 0 lacunas, 0 duplicadas
- [ ] Autorização jurídica registrada em `docs/autorizacoes/`
- [ ] Revisão humana das 1.146 pendências do parser e dos links restritos/mortos
- [ ] PDF do acervo

> A avaliação crítica do ETL, com causas, números e próximos passos, está em
> [`docs/ETL-AVALIACAO-2026-11-22.md`](docs/ETL-AVALIACAO-2026-11-22.md).
> A pesquisa de redes está em
> [`docs/redes-2026-11-22.json`](docs/redes-2026-11-22.json).
> O plano de navegação está em
> [`docs/PLANO-NAVEGACAO-ORIGINAL.md`](docs/PLANO-NAVEGACAO-ORIGINAL.md).
