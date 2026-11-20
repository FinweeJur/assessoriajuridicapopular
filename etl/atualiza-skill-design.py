"""Atualiza a skill design com o repertório do Acervo AJP."""
import io

p = r"C:\Users\teste\.claude\skills\design\SKILL.md"
t = io.open(p, encoding="utf-8").read()

EXTRA = """

## 10. Preferências do Acervo AJP (2026)

Aplicar quando o projeto for o acervo `assessoriajuridicapopular` ou pedir o mesmo repertório.

### Tipografia e tema

- **Títulos:** Cabinet Grotesk (Fontshare), fallback Clash Display.
- **Texto:** Switzer (Fontshare), fallback General Sans.
- **Tema padrão:** Pequi. A escolha fica em `localStorage` e é aplicada antes do CSS (`data-tema-cedo`); não pisca.
- **Tokens:** `--font-display`, `--font-body`, `--cp-primary`, `--cp-surface`, `--borda`, `--raio`; nada de hex solto nos componentes.

### Cards do acervo

- Borda fina, sem fundo pesado; hover levanta 5 px, acende a borda e ganha glow.
- Título maior que o corpo: `clamp(1.12rem, .35vw + 1.02rem, 1.3rem)`.
- Texto corrido em `1rem`, entrelinha 1.55, limite de 4 linhas.
- Tags menores (`.66rem`) dentro de um cartão de borda leve; não usar texto solto com “·”.
- Figuras sem crédito: **sem legenda e sem aviso repetido**. O contato de retirada fica só no rodapé.

### Efeitos que ficaram

- **Grade interativa de fundo:** quadrados de 14 px (10 px no celular), brilho do ponteiro 40% menor (raio 102 px, alpha 0.3); fixa, atrás de `main`/`footer`; `body` transparente e `html` com a cor do tema.
- **Estrelas de rolagem:** poucas estrelas no mesmo canvas; esticam conforme a velocidade do scroll; sem movimento em `prefers-reduced-motion`.
- **Magic card:** holofote radial de 240 px seguindo o ponteiro em cards, bento e destaques (7% da cor primária).
- **Bento assimétrico:** 4 colunas `.85fr 1.45fr 1.45fr .85fr`; card grande no centro; no celular vira **pilha de cartões sticky** (`top: 96px + i*6px`, fundo sólido, sem colunas implícitas).
- **Electro border:** copiar o filtro do Lightswind, não inventar. Quatro `feTurbulence` (`baseFrequency 0.02`, `numOctaves 2`, seeds 1/2), offsets animados 460/336 em 6 s, `feComposite`, `feBlend color-dodge` e `feDisplacementMap scale=30` (R/B). Borda de 2 px laranja + aura em duas camadas (`blur(2px)` e `blur(7px)`). Máximo 2 por página; versão estática para movimento reduzido.
- **Navegação:** pílula dinâmica + tubelight seguindo o item ativo/hover no desktop; no celular, barra em duas linhas com busca, tema, A+ e hambúrguer.
- **Speed dial:** um botão abre Topo, Descer e Buscar/Compartilhar/Acervo com stagger.
- **Busca expansível:** `flex-basis` cresce no foco, botão de limpar e navegação para `acervo.html` quando não há lista na página.
- **Carrossel 3D:** três cards das referências em cilindro (`translateZ 260px`, 120°), arrasto com momento, auto-órbita no desktop e pausa em movimento reduzido.
- **Falling sections:** seções entram com `translateY(46px) rotateX(-11deg)`, uma vez, via IntersectionObserver.
- **Meteoros:** SVG com curvas de Bézier entre Blog original → OpenCode → GitHub; `animateMotion` + faíscas no impacto; no celular os caminhos viram verticais.
- **Chatbot:** busca local nos 713 textos + **perguntas curadas em botões**; na home, uma conversa aberta no fim com as mesmas perguntas e respostas com link.

### Regras de página

- **Home é apresentação:** hero, faixa infinita de fotos, bento de páginas, referências, fluxo e conversa. **Acervo é lista:** filtros, busca, 713 cartões e paginação em `acervo.html`.
- **Rodapé:** quatro colunas (Acervo, Seções, Fonte, Parcerias), “GT do IPDMS · Coord. Luiz Otávio Ribas” na mesma linha, “Artur Colito” antes do e-mail e aviso de rascunho de IA em linha inteira.
- **Mobile:** testar 390 px (sem rolagem lateral), 1024 px (bento em 2 colunas) e 1280 px (4 colunas). Alvos ≥44 px; texto selecionável (`user-select: auto`); animações pausam em `prefers-reduced-motion`.
"""

if "Preferências do Acervo AJP" not in t:
    t = t.rstrip() + EXTRA
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("skill:", "Preferências do Acervo AJP" in io.open(p, encoding="utf-8").read())
