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
o-que-e-assessoria-juridica-popular.html   primeiro texto publicado
_modelo.html                   gabarito para as próximas páginas
acervo.css                     estilos do acervo
reveal.css / reveal.js         entrada dos blocos ao rolar (sem biblioteca)
fontes/                        Clash Display, General Sans, Satoshi, Fraunces…
temas/                          nove temas de cor
logos/                         RENAP, IPDMS e MAB
etl/                           download e parser do blog original
docs/                          plano de ETL e reformulação
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
- Bloco de citação com `blockquote cite=` e dois botões (original e autor).
- Fonte mínima 12 px; 390 px sem rolagem lateral; contraste medido.
- Nada de conteúdo copiado sem licença: imagem sem crédito entra como link.

## Estado em 22/11/2026

- [x] Estrutura em cinco portas: Home, Acervo, Biblioteca, Mística e IA
- [x] Faixa de parcerias com as três logos
- [x] Busca, temas, autores, coleções e páginas de texto
- [x] Biblioteca, caderno de poesias, rádio e RAG local
- [x] **712 dos 790 posts** do blog com página e `canonical`
- [ ] 78 posts ainda sem página: 2014 inteiro, parte de 2011/2013/2015 e
      quatro páginas/gadgets (ver `docs/etl-lacunas-2026-11-22.csv`)
- [ ] Blogues parceiros, entidades parceiras, mapeamento de AJUPs,
      “Quem somos” e “Como postar”
- [ ] Autorização jurídica registrada em `docs/autorizacoes/`
- [ ] PDF do acervo

> A avaliação crítica do ETL, com causas, números e próximos passos, está em
> [`docs/ETL-AVALIACAO-2026-11-22.md`](docs/ETL-AVALIACAO-2026-11-22.md).
> A pesquisa de redes está em
> [`docs/redes-2026-11-22.json`](docs/redes-2026-11-22.json).
