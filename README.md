# Assessoria Jurídica Popular — acervo

Site do acervo de textos sobre **assessoria jurídica popular**, publicado com
citação direta, crédito, link canônico e botão para o original e para o autor.

**Publicação:** `assessoriajuridicapopular.pages.dev` (Cloudflare Pages, site
estático, sem build).

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

1. Cloudflare Pages → projeto `assessoriajuridicapopular`.
2. Build command: *(vazio)*. Output directory: `/`.
3. Domínio provisório: `assessoriajuridicapopular.pages.dev`.

## Regras

- Citação direta, sem reescrever a grafia do autor.
- Toda página tem: autor, data, link do original e data de captura.
- Bloco de citação com `blockquote cite=` e dois botões (original e autor).
- Fonte mínima 12 px; 390 px sem rolagem lateral; contraste medido.
- Nada de conteúdo copiado sem licença: imagem sem crédito entra como link.

## Estado

- [x] Estrutura do site e primeira página
- [x] Faixa de parcerias com as três logos
- [ ] 790 textos do blog (download e parser em andamento)
- [ ] busca, temas e páginas de autor
- [ ] PDF do acervo
