"""Gera folhas de contato para escolher as fotos da home."""
import glob
import io
import os
import re
import urllib.request

from PIL import Image, ImageDraw

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
TMP = r"C:\Users\teste\AppData\Local\Temp\opencode"
os.makedirs(TMP, exist_ok=True)
UA = "finweejur/github artur colito"

paginas = [
    "10-anos-do-cajuina.html",
    "80-anos-do-miguel-baldez.html",
    "a-licao-de-juruti-velho.html",
    "3-anos-de-nepe-14-anos-do-massacre.html",
]
paginas += [os.path.basename(p) for p in glob.glob(RAIZ + r"\a-primeira-turma-de-pos-graduacao*.html")]
paginas += [os.path.basename(p) for p in glob.glob(RAIZ + r"\a-assessoria-juridica-popular-no-1o-encontro*.html")]
paginas += [os.path.basename(p) for p in glob.glob(RAIZ + r"\a-primeira-turma*.html")]

urls = []
for p in paginas:
    caminho = os.path.join(RAIZ, p)
    if not os.path.exists(caminho):
        continue
    t = io.open(caminho, encoding="utf-8").read()
    for m in re.finditer(r'<figure[^>]*>.*?<img[^>]+src="([^"]+)"', t, re.S):
        u = m.group(1)
        if u.startswith("http") and u not in urls:
            urls.append(u)
        break

print("blog urls:", len(urls))
thumbs = []
for i, u in enumerate(urls[:8]):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA})
        dados = urllib.request.urlopen(req, timeout=30).read()
        im = Image.open(io.BytesIO(dados)).convert("RGB")
        im.thumbnail((300, 200))
        thumbs.append((i, im))
    except Exception as e:
        print("erro", i, e)

if thumbs:
    folha = Image.new("RGB", (4 * 310, 2 * 230), "white")
    d = ImageDraw.Draw(folha)
    for i, im in thumbs:
        x = (i % 4) * 310 + 5
        y = (i // 4) * 230 + 5
        folha.paste(im, (x, y))
        d.text((x + 4, y + 204), str(i), fill="black")
    folha.save(os.path.join(TMP, "blog-fotos.jpg"), quality=80)
    print("folha blog:", os.path.join(TMP, "blog-fotos.jpg"))

# Seminário
pasta = r"C:\Users\teste\Downloads\LOGOS RENAP"
nomes = [
    "IMG_9341.jpg", "IMG_9367.jpg",
    "WhatsApp Image 2026-11-12 at 09.44.00.jpeg",
    "WhatsApp Image 2026-11-13 at 18.41.18.jpeg",
    "WhatsApp Image 2026-11-14 at 14.19.41.jpeg",
    "WhatsApp Image 2026-11-18 at 08.59.00.jpeg",
    "WhatsApp Image 2026-11-13 at 20.29.19.jpeg",
    "WhatsApp Image 2026-11-14 at 14.19.45.jpeg",
]
thumbs = []
for i, n in enumerate(nomes):
    caminho = os.path.join(pasta, n)
    if not os.path.exists(caminho):
        continue
    im = Image.open(caminho).convert("RGB")
    im.thumbnail((300, 200))
    thumbs.append((i, im))

if thumbs:
    folha = Image.new("RGB", (4 * 310, 2 * 230), "white")
    d = ImageDraw.Draw(folha)
    for i, im in thumbs:
        x = (i % 4) * 310 + 5
        y = (i // 4) * 230 + 5
        folha.paste(im, (x, y))
        d.text((x + 4, y + 204), "%d %s" % (i, nomes[i][:22]), fill="black")
    folha.save(os.path.join(TMP, "seminario-fotos.jpg"), quality=80)
    print("folha seminario:", os.path.join(TMP, "seminario-fotos.jpg"))
