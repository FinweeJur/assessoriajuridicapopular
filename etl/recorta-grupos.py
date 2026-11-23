"""Recorta pessoas de fotos de evento em alta resolução (modelo u2net)."""
import os

from PIL import Image
from rembg import new_session, remove

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
DEST = os.path.join(RAIZ, "fotos", "recortes")
os.makedirs(DEST, exist_ok=True)

ALVOS = [
    ("fotos/eventos/2012-carta-dos-enamorados-do-neda-062.jpg", "grupo-neda"),
    ("fotos/eventos/2017-fortalecimento-da-renaju-em-uma-conjuntura-d-007.jpg", "grupo-renaju"),
    ("fotos/eventos/2014-minicurso-em-advocacia-popular-na-uem-024.jpg", "minicurso-uem"),
    ("fotos/eventos/2013-cadernos-insurgentes-e-oficina-do-geap-029.jpg", "oficina-geap"),
    ("fotos/autores/miguel-baldez.jpg", "miguel-baldez-u2"),
    ("fotos/autores/ricardo-pazello.jpg", "ricardo-pazello-u2"),
]

sessao = new_session("u2net")
for rel, nome in ALVOS:
    origem = os.path.join(RAIZ, rel)
    if not os.path.exists(origem):
        print("falta", rel)
        continue
    im = Image.open(origem).convert("RGB")
    if max(im.size) > 1100:
        f = 1100 / max(im.size)
        im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    saida = remove(im, session=sessao, alpha_matting=True,
                   alpha_matting_foreground_threshold=250,
                   alpha_matting_background_threshold=15,
                   alpha_matting_erode_size=8)
    caixa = saida.getbbox()
    if caixa:
        saida = saida.crop(caixa)
    destino = os.path.join(DEST, nome + ".png")
    saida.save(destino, "PNG", optimize=True)
    print("%-22s %sx%s %dKB" % (nome, saida.width, saida.height,
                                os.path.getsize(destino) // 1024))
