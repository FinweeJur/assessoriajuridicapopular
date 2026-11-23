"""Baixa miniaturas das fotos de evento para escolha visual."""
import io
import json
import os
import re
import time
import urllib.request

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"
THUMBS = os.path.join(RAIZ, "fotos", "_thumbs")
UA = "finweejur/github artur colito (reuso de fotos do proprio acervo)"

os.makedirs(THUMBS, exist_ok=True)


def url_mini(src, largura=420):
    # troca o segmento de tamanho do Blogger pela largura desejada
    novo, n = re.subn(r"/(s\d+|w\d+|h\d+)(-[^/]*)?/", "/s%d/" % largura, src, count=1)
    if n:
        return novo
    m = re.search(r"=s\d+", src)
    if m:
        return src[:m.start()] + "=s%d" % largura
    return src


d = json.load(io.open(os.path.join(RAIZ, "dados", "fotos-blog.json"), encoding="utf-8"))
eventos = [f for f in d["fotos"]
           if (f.get("tipo") or "").lower() == "evento"
           or re.search(r"encontro|semin[áa]rio|jornada|oficina|curso|erenaju|erenap|"
                        r"assembleia|marcha|\bato\b|festa|mostra|congresso|plenária|plenaria",
                        f.get("titulo") or "", re.I)]
# prioriza fotos de posts de evento e mais recentes
eventos.sort(key=lambda x: ((x.get("tipo") or "") != "evento", -(int((x.get("data") or "0000")[:4] or 0))))

alvo = eventos[:72]
baixados = []
for i, f in enumerate(alvo, 1):
    nome = "%03d_%s.jpg" % (i, re.sub(r"[^a-z0-9]+", "-", (f.get("titulo") or "")[:40].lower()).strip("-"))
    caminho = os.path.join(THUMBS, nome)
    if os.path.exists(caminho) and os.path.getsize(caminho) > 3000:
        baixados.append((nome, f))
        continue
    u = url_mini(f["src"])
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            dados = r.read()
        if len(dados) < 1200:
            print(i, "pequena demais, pulando")
            continue
        io.open(caminho, "wb").write(dados)
        baixados.append((nome, f))
        print(i, "ok", len(dados) // 1024, "KB")
    except Exception as e:
        print(i, "erro", str(e)[:80])
    time.sleep(1.2)

json.dump([{"arquivo": n, **f} for n, f in baixados],
          io.open(os.path.join(RAIZ, "dados", "fotos-thumbs.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("baixadas:", len(baixados))
