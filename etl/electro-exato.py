"""Copia o filtro elétrico do Lightswind: 4 camadas de turbulência + color-dodge + deslocamento 30."""
import io

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"

p = RAIZ + r"\casca.js"
js = io.open(p, encoding="utf-8").read()

inicio = js.find("if (!document.getElementById('electro-filtro'))")
fim = js.find("    if (window.matchMedia", inicio)
if inicio < 0 or fim < 0:
    raise SystemExit("nao achei o bloco do filtro")

FILTRO = """if (!document.getElementById('electro-filtro')) {
      var caixaFiltro = document.createElement('div');
      caixaFiltro.setAttribute('aria-hidden', 'true');
      caixaFiltro.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
      caixaFiltro.innerHTML =
        '<svg xmlns="http://www.w3.org/2000/svg">' +
        '<defs>' +
        '<filter id="electro-filtro" color-interpolation-filters="sRGB" x="-20%" y="-20%" width="140%" height="140%">' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise1" seed="1" />' +
        '<feOffset in="noise1" dx="0" dy="0" result="offsetNoise1"><animate attributeName="dy" values="460; 0" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise2" seed="1" />' +
        '<feOffset in="noise2" dx="0" dy="0" result="offsetNoise2"><animate attributeName="dy" values="0; -460" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise3" seed="2" />' +
        '<feOffset in="noise3" dx="0" dy="0" result="offsetNoise3"><animate attributeName="dx" values="336; 0" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise4" seed="2" />' +
        '<feOffset in="noise4" dx="0" dy="0" result="offsetNoise4"><animate attributeName="dx" values="0; -336" dur="6s" repeatCount="indefinite" calcMode="linear" /></feOffset>' +
        '<feComposite in="offsetNoise1" in2="offsetNoise2" result="part1" />' +
        '<feComposite in="offsetNoise3" in2="offsetNoise4" result="part2" />' +
        '<feBlend in="part1" in2="part2" mode="color-dodge" result="combinedNoise" />' +
        '<feDisplacementMap in="SourceGraphic" in2="combinedNoise" scale="30" xChannelSelector="R" yChannelSelector="B" />' +
        '</filter>' +
        '<filter id="electro-filtro-parado" color-interpolation-filters="sRGB" x="-20%" y="-20%" width="140%" height="140%">' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise1" seed="1" />' +
        '<feOffset in="noise1" dx="0" dy="0" result="offsetNoise1" />' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise2" seed="1" />' +
        '<feOffset in="noise2" dx="0" dy="0" result="offsetNoise2" />' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise3" seed="2" />' +
        '<feOffset in="noise3" dx="0" dy="0" result="offsetNoise3" />' +
        '<feTurbulence type="turbulence" baseFrequency="0.02" numOctaves="2" result="noise4" seed="2" />' +
        '<feOffset in="noise4" dx="0" dy="0" result="offsetNoise4" />' +
        '<feComposite in="offsetNoise1" in2="offsetNoise2" result="part1" />' +
        '<feComposite in="offsetNoise3" in2="offsetNoise4" result="part2" />' +
        '<feBlend in="part1" in2="part2" mode="color-dodge" result="combinedNoise" />' +
        '<feDisplacementMap in="SourceGraphic" in2="combinedNoise" scale="30" xChannelSelector="R" yChannelSelector="B" />' +
        '</filter>' +
        '</defs></svg>';
      document.body.appendChild(caixaFiltro);
    }
"""

js = js[:inicio] + FILTRO + js[fim:]

# Não pode sair antes de aplicar a classe no modo reduzido.
js = js.replace(
    "    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) { return; }\n"
    "    var alvos = document.querySelectorAll('.bento__item--grande, .mistica-cartao');",
    "    var alvos = document.querySelectorAll('.bento__item--grande, .mistica-cartao');", 1)

# Aura de brilho em camadas, como no componente original.
js = js.replace(
    "    Array.prototype.slice.call(alvos, 0, 2).forEach(function (el) {\n"
    "      el.classList.add('electro');\n"
    "    });",
    "    Array.prototype.slice.call(alvos, 0, 2).forEach(function (el) {\n"
    "      el.classList.add('electro');\n"
    "      var aura = document.createElement('span');\n"
    "      aura.className = 'electro__aura';\n"
    "      aura.setAttribute('aria-hidden', 'true');\n"
    "      el.appendChild(aura);\n"
    "    });", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(js)
print("filtro exato:", "color-dodge" in js and 'scale="30"' in js)
print("aura:", "electro__aura" in js)
