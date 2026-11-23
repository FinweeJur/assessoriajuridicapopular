"""Recorta o fundo das fotos de pessoas (rembg) e salva PNG com transparência."""
import io
import os

from PIL import Image
from rembg import remove, new_session

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
DEST = os.path.join(RAIZ, "fotos", "recortes")
os.makedirs(DEST, exist_ok=True)

ALVOS = [
    ("fotos/autores/jacques-alfonsin.jpg", "jacques-alfonsin"),
    ("fotos/autores/luiz-otavio-ribas.jpg", "luiz-otavio-ribas"),
    ("fotos/autores/miguel-baldez.jpg", "miguel-baldez"),
    ("fotos/autores/ricardo-pazello.jpg", "ricardo-pazello"),
    ("fotos/autores/tchenna-maso.jpg", "tchenna-maso"),
]

sessao = new_session("u2netp")
for rel, nome in ALVOS:
    origem = os.path.join(RAIZ, rel)
    if not os.path.exists(origem):
        print("falta", rel)
        continue
    im = Image.open(origem).convert("RGB")
    if max(im.size) > 900:
        f = 900 / max(im.size)
        im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    saida = remove(im, session=sessao, alpha_matting=False,
                   post_process_mask=True)
    # apara as bordas transparentes
    caixa = saida.getbbox()
    if caixa:
        saida = saida.crop(caixa)
    destino = os.path.join(DEST, nome + ".png")
    saida.save(destino, "PNG", optimize=True)
    print("%-24s %sx%s  %dKB" % (nome, saida.width, saida.height,
                                 os.path.getsize(destino) // 1024))
