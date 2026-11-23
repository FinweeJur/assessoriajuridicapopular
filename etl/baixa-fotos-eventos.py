"""Baixa as fotos de evento escolhidas em alta resolução e registra créditos."""
import io
import json
import os
import re
import time
import unicodedata
import urllib.request

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
DEST = os.path.join(RAIZ, "fotos", "eventos")
UA = "finweejur/github artur colito (reuso de fotos do proprio acervo)"
ESCOLHIDAS = ["003", "007", "009", "010", "020", "021", "022", "023", "024", "025",
              "026", "029", "035", "036", "038", "039", "046", "048", "056", "057",
              "062", "063", "065"]

os.makedirs(DEST, exist_ok=True)


def slug(s, n=44):
    t = unicodedata.normalize("NFD", s or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:n] or "foto"


def alta(src):
    novo, k = re.subn(r"/(s\d+|w\d+|h\d+)(-[^/]*)?/", "/s1600/", src, count=1)
    if k:
        return novo
    m = re.search(r"=s\d+", src)
    if m:
        return src[:m.start()] + "=s1600"
    return src


d = json.load(io.open(os.path.join(RAIZ, "dados", "fotos-thumbs.json"), encoding="utf-8"))
por_num = {f["arquivo"].split("_")[0]: f for f in d}

creditos = []
for num in ESCOLHIDAS:
    f = por_num.get(num)
    if not f:
        print("sem metadado", num)
        continue
    ano = (f.get("data") or "0000")[:4]
    nome = "%s-%s-%s.jpg" % (ano, slug(f.get("titulo")), num)
    destino = os.path.join(DEST, nome)
    if os.path.exists(destino) and os.path.getsize(destino) > 20000:
        creditos.append({"arquivo": "fotos/eventos/" + nome, **{k: f.get(k) for k in
                         ("post", "titulo", "data", "tema", "tipo", "src")}})
        continue
    try:
        req = urllib.request.Request(alta(f["src"]), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=90) as r:
            dados = r.read()
        if len(dados) < 20000:
            print(num, "pequena", len(dados))
            continue
        io.open(destino, "wb").write(dados)
        creditos.append({"arquivo": "fotos/eventos/" + nome, **{k: f.get(k) for k in
                         ("post", "titulo", "data", "tema", "tipo", "src")}})
        print(num, "->", nome, len(dados) // 1024, "KB")
    except Exception as e:
        print(num, "erro", str(e)[:90])
    time.sleep(1.3)

json.dump(creditos, io.open(os.path.join(DEST, "creditos.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("total:", len(creditos))
