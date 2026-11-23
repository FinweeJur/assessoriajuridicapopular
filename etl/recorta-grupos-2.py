"""Segunda passada de recortes: corrige marca d'água e tenta fotos de evento."""
import os

from PIL import Image
from rembg import new_session, remove

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
DEST = os.path.join(RAIZ, "fotos", "recortes")

sessao = new_session("u2net")


def recorta(rel, nome, cortar_baixo=0.0):
    im = Image.open(os.path.join(RAIZ, rel)).convert("RGB")
    if cortar_baixo:
        im = im.crop((0, 0, im.width, int(im.height * (1 - cortar_baixo))))
    if max(im.size) > 1100:
        f = 1100 / max(im.size)
        im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    out = remove(im, session=sessao, alpha_matting=True,
                 alpha_matting_foreground_threshold=240,
                 alpha_matting_background_threshold=20,
                 alpha_matting_erode_size=6)
    caixa = out.getbbox()
    if caixa:
        out = out.crop(caixa)
    out.save(os.path.join(DEST, nome + ".png"), "PNG", optimize=True)
    print("%-22s %sx%s" % (nome, out.width, out.height))


recorta("fotos/autores/miguel-baldez.jpg", "miguel-baldez-u2", cortar_baixo=0.10)
recorta("fotos/eventos/2012-coluna-direitos-das-marias-iv-encontro-de-mu-038.jpg", "mulher-microfone")
recorta("fotos/eventos/2014-sustentacao-oral-no-caso-vanderley-no-ceara-026.jpg", "dupla-audiencia")
recorta("fotos/eventos/2017-jornada-universitaria-em-fortaleza-010.jpg", "plenaria-fortaleza")

# remove o recorte falho
falho = os.path.join(DEST, "grupo-renaju.png")
if os.path.exists(falho):
    os.remove(falho)
    print("removido grupo-renaju.png")
