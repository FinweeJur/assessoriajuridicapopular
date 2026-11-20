"""Prepara as fotos da faixa da home: 6 do seminário IPDMS + 2 de posts do blog."""
import io
import os
import urllib.request

from PIL import Image, ImageOps

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
SEM = r"C:\Users\teste\Downloads\LOGOS RENAP"
UA = "finweejur/github artur colito"

os.makedirs(RAIZ + r"\fotos\seminario", exist_ok=True)
os.makedirs(RAIZ + r"\fotos\blog", exist_ok=True)


def salva(im, destino, largura=1400, qualidade=80):
    im = ImageOps.exif_transpose(im).convert("RGB")
    if im.width > largura:
        altura = round(im.height * largura / im.width)
        im = im.resize((largura, altura), Image.LANCZOS)
    im.save(destino, "JPEG", quality=qualidade, optimize=True, progressive=True)
    print(os.path.basename(destino), im.width, "x", im.height, os.path.getsize(destino))


seminario = [
    ("IMG_9341.jpg", "seminario-01.jpg"),
    ("IMG_9367.jpg", "seminario-02.jpg"),
    ("WhatsApp Image 2026-11-13 at 18.41.18.jpeg", "seminario-03.jpg"),
    ("WhatsApp Image 2026-11-14 at 14.19.41.jpeg", "seminario-04.jpg"),
    ("WhatsApp Image 2026-11-18 at 08.59.00.jpeg", "seminario-05.jpg"),
    ("WhatsApp Image 2026-11-13 at 20.29.19.jpeg", "seminario-06.jpg"),
]
for origem, destino in seminario:
    salva(Image.open(os.path.join(SEM, origem)),
          os.path.join(RAIZ, "fotos", "seminario", destino))

blog = [
    ("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjrPIeOxLzM3T3qhR-TtsRLF588bmAA-H_uJge7ZzDE42YYOJA2x6Rmf53KbFWDwk_4-JUpYxxWJdi5yxeJU0plWiGcVYeHbGWRvPoyyU4xsRqpfoxw88gq3sessk-mEyoF1RNC6IOMmxgS/s1600/MG-+Norte.JPG", "blog-01.jpg"),
    ("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiC9P2uRvx9s_gKcXAiX614W94z6PeTk-Qa0q2AzBTmoTXeOB3bOXOzKPvxM6_0JZcTnIFcGhBNcY7fnMMKMLHAIkbvHAZMizaChf1x7iRVsmxhl4fN3nzAvbnHV1LieozV3o9VZd9R2PCl/s1600/P%C3%B3s+UFG.JPG", "blog-02.jpg"),
    ("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi2FcW0QZEqSVIysLLc_6FYZoXHAh9Ml554Rfk6rgdWE2Lnw7it0iVcG1ft2UyADvHDadF4ATrq5Jq8Hn18dDTRR8H9czVHPOHwBqTF94IHmzikDSQkqTFnU9ULiX_ij1xLCj0gPvoJHzY/s1600/chocolatao+a+toga.JPG", "blog-03.jpg"),
]
for url, destino in blog:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    dados = urllib.request.urlopen(req, timeout=45).read()
    salva(Image.open(io.BytesIO(dados)),
          os.path.join(RAIZ, "fotos", "blog", destino), largura=1200)
