"""Resgata os posts que ficaram sem JSON no lote S5-nano e refaz a síntese no S5."""
import importlib.util
import io
import json
import os
import sys
from collections import Counter

from json_repair import repair_json

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "dados", "revisao-maritaca")
LOTES = os.path.join(SAIDA, "lotes")
INDICE = os.path.join(RAIZ, "_indice.json")

spec = importlib.util.spec_from_file_location("rev", os.path.join(RAIZ, "etl", "revisa-maritaca.py"))
rev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rev)


def le_json(p):
    return json.load(io.open(p, encoding="utf-8"))


def parse_posts(txt):
    try:
        d = json.loads(txt)
    except Exception:
        d = repair_json(txt, return_objects=True)
    if isinstance(d, list):
        posts = d
    elif isinstance(d, dict):
        posts = d.get("posts", [])
    else:
        posts = []
    return [p for p in posts if isinstance(p, dict) and p.get("slug")]


def carrega_resultados():
    out = {}
    p = os.path.join(LOTES, "saida-batch.jsonl")
    if not os.path.exists(p):
        return out
    for line in io.open(p, encoding="utf-8"):
        o = json.loads(line)
        body = (o.get("response") or {}).get("body") or {}
        ch = (body.get("choices") or [{}])[0]
        msg = (ch.get("message") or {}).get("content") or ""
        for x in parse_posts(msg):
            out[x["slug"]] = x
    return out


def main():
    regs = le_json(INDICE)
    resultados = carrega_resultados()
    faltam = [r for r in regs if r["slug"] not in resultados]
    print("recuperados:", len(resultados), "| faltam:", len(faltam), flush=True)

    # Lotes pequenos: saída segura e JSON completo.
    lotes = [faltam[i:i + 25] for i in range(0, len(faltam), 25)]
    total_in = total_out = 0
    for n, lote in enumerate(lotes, 1):
        conteudo = "".join(rev.formata_post(r, rev.texto_do_post(r["slug"])) for r in lote)
        usuario = (
            "Revise os %d posts abaixo. Devolva exatamente o JSON pedido, "
            "com um item para cada slug, na mesma ordem.\n\n%s"
        ) % (len(lote), conteudo)
        print("resgate %02d/%02d: %d posts" % (n, len(lotes), len(lote)), flush=True)
        resp = rev.com_retry([
            {"role": "system", "content": rev.SISTEMA},
            {"role": "user", "content": usuario},
        ], max_tokens=14000, modelo="S5-nano")
        ch = (resp.get("choices") or [{}])[0]
        msg = (ch.get("message") or {}).get("content") or ""
        posts = parse_posts(msg)
        if not posts:
            print("  sem posts no resgate", n, "finish", ch.get("finish_reason"), flush=True)
        for x in posts:
            resultados[x["slug"]] = x
        uso = resp.get("usage") or {}
        total_in += int(uso.get("prompt_tokens") or 0)
        total_out += int(uso.get("completion_tokens") or 0)
        json.dump(posts, io.open(os.path.join(LOTES, "resgate-%02d.json" % n), "w",
                                 encoding="utf-8"), ensure_ascii=False, indent=1)

    faltam2 = [r["slug"] for r in regs if r["slug"] not in resultados]
    custo_resgate = total_in * rev.PRECO_IN + total_out * rev.PRECO_OUT
    print("resgate: %d posts, %d faltando, R$ %.4f" % (len(resultados), len(faltam2), custo_resgate), flush=True)

    json.dump(list(resultados.values()), io.open(os.path.join(SAIDA, "posts.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=1)

    # CSV
    import csv
    with io.open(os.path.join(SAIDA, "revisao-posts.csv"), "w",
                 encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["slug", "titulo", "data", "autor", "tema_atual", "temas_atuais",
                    "tipo_atual", "palavras_atuais", "tema_sugerido", "temas_sugeridos",
                    "tipo_sugerido", "palavras_sugeridas", "grupo", "similar_a",
                    "confianca", "flags", "justificativa"])
        for r in regs:
            p = resultados.get(r["slug"], {})
            w.writerow([
                r["slug"], r.get("titulo") or "", r.get("data") or "", r.get("autor") or "",
                r.get("tema_principal") or "", " | ".join(r.get("temas") or []),
                r.get("tipo") or "", " | ".join(r.get("palavras") or []),
                p.get("tema_principal") or "", " | ".join(p.get("temas_secundarios") or []),
                p.get("tipo") or "", " | ".join(p.get("palavras") or []),
                p.get("grupo") or "", " | ".join(p.get("similar_a") or []),
                p.get("confianca", ""), " | ".join(p.get("flags") or []),
                p.get("justificativa") or "",
            ])

    # Síntese compacta no S5, para caber no teto.
    resumo = []
    for r in regs:
        p = resultados.get(r["slug"])
        if not p:
            continue
        resumo.append("%s | atual=%s/%s | sug=%s/%s | grupo=%s | flags=%s" % (
            r["slug"], r.get("tema_principal"), r.get("tipo"),
            p.get("tema_principal"), p.get("tipo"), p.get("grupo") or "",
            ",".join(p.get("flags") or [])))
    prompt = """Você é o editor-chefe do acervo AJP. Analise a revisão de 713 posts
e produza um relatório em Markdown, em português, com: mapa atual x sugerido,
sobreposições e ambiguidades, clusters de similaridade, tipos, palavras-chave,
posts mal categorizados, definições operacionais dos 6 temas e regras de migração.
Seja específico com slugs. Responda SOMENTE JSON:
{"relatorio_md":"...", "mapa_atual":{}, "mapa_sugerido":{}, "clusters":[],
 "problemas":[], "migracao":[]}
Dados:
%s
""" % "\n".join(resumo)
    resp = rev.com_retry([{"role": "system", "content": prompt}],
                         max_tokens=12000, modelo="S5")
    ch = (resp.get("choices") or [{}])[0]
    msg = (ch.get("message") or {}).get("content") or ""
    try:
        sintese = json.loads(msg)
    except Exception:
        sintese = repair_json(msg, return_objects=True)
        if not isinstance(sintese, dict):
            sintese = {"relatorio_md": msg}
    json.dump(sintese, io.open(os.path.join(SAIDA, "sintese.json"), "w",
              encoding="utf-8"), ensure_ascii=False, indent=1)
    io.open(os.path.join(SAIDA, "relatorio-taxonomia.md"), "w",
            encoding="utf-8", newline="\n").write(sintese.get("relatorio_md") or "")
    uso = resp.get("usage") or {}
    custo_sintese = (int(uso.get("prompt_tokens") or 0) * rev.PRECO_IN_S5 +
                     int(uso.get("completion_tokens") or 0) * rev.PRECO_OUT_S5)
    print("sintese R$ %.4f | total resgate R$ %.4f" % (custo_sintese, custo_resgate + custo_sintese), flush=True)


if __name__ == "__main__":
    main()
