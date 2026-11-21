"""Revisão editorial do acervo AJP com Maritaca S5#flex.

Uso:
  python etl/revisa-maritaca.py --dry-run
  python etl/revisa-maritaca.py

O script:
  1. lê _indice.json e o texto dos 713 HTMLs;
  2. monta lotes de ~70 posts;
  3. envia cada lote ao S5 com service_tier=flex;
  4. salva respostas brutas e um CSV por post;
  5. faz uma chamada de síntese e grava o relatório da taxonomia.

Não altera nenhum HTML do site.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICE = os.path.join(RAIZ, "_indice.json")
SAIDA = os.path.join(RAIZ, "dados", "revisao-maritaca")
LOTES = os.path.join(SAIDA, "lotes")
API = "https://chat.maritaca.ai/api/chat/completions"
MODELO = "S5-nano"
PRECO_IN = 0.05 / 1_000_000   # R$/token, S5-nano batch
PRECO_OUT = 0.30 / 1_000_000  # R$/token, S5-nano batch
TETO = 0.60
PRECO_IN_S5 = 0.25 / 1_000_000
PRECO_OUT_S5 = 1.25 / 1_000_000
MODELO_SINTESE = "S5"

TEMAS = [
    ("assessoria-juridica-popular", "Assessoria jurídica popular",
     "advocacia popular, assessoria/assistência jurídica, AJP/AJUP/SAJU, acesso à justiça, prática extensionista."),
    ("educacao-popular", "Educação popular",
     "formação, oficinas, cursos, extensão universitária, educação jurídica, Paulo Freire, metodologia."),
    ("movimentos-sociais", "Movimentos sociais",
     "MST/MTST, ocupações, reforma agrária, sindicatos, greves, quilombos, movimento estudantil, lutas populares."),
    ("direitos-humanos", "Direitos humanos",
     "violações, criminalização, violência, feminicídio, racismo, povos indígenas, LGBT, moradia, meio ambiente."),
    ("memoria", "Memória e cultura",
     "história, ditadura, anistia, justiça de transição, arquivo, homenagens, obituários, biografias, cultura."),
    ("teoria-critica", "Teoria crítica do direito",
     "teoria crítica, marxismo, Pachukanis, Lyra Filho, pluralismo jurídico, direito alternativo, epistemologia."),
]
TIPOS = [
    ("formativo", "Texto formativo"), ("evento", "Evento"),
    ("resenha", "Resenha e livro"), ("poesia", "Poesia"),
    ("notícia", "Notícia"), ("documento", "Documento"),
]
FLAGS = [
    "reclassificar", "ambiguo", "duplicado_provavel", "texto_curto",
    "fora_do_tema", "evento_desatualizado", "homenagem", "sem_palavras",
]


def ler_json(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return json.load(f)


def gravar_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def texto_do_post(slug: str) -> str:
    caminho = os.path.join(RAIZ, slug + ".html")
    if not os.path.exists(caminho):
        return ""
    t = io.open(caminho, encoding="utf-8").read()

    # Prefere o corpo do artigo.
    m = re.search(
        r'<div[^>]*class="[^"]*\bcorpo\b[^"]*"[^>]*>(.*?)</div>\s*(?:<section|<footer|</article>)',
        t, re.S,
    )
    corpo = m.group(1) if m else t

    corpo = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<noscript\b.*?</noscript>", " ", corpo, flags=re.S | re.I)
    corpo = re.sub(r"<(nav|aside|footer|header)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
    corpo = re.sub(r"<figure\b.*?</figure>", " ", corpo, flags=re.S | re.I)
    corpo = re.sub(r"<[^>]+>", " ", corpo)
    corpo = html.unescape(corpo)
    corpo = re.sub(r"\s+", " ", corpo).strip()

    if len(corpo) > 12000:
        corpo = corpo[:12000].rsplit(" ", 1)[0] + " [...]"
    return corpo


def formata_post(r, texto):
    temas = ", ".join(r.get("temas") or [])
    palavras = ", ".join(r.get("palavras") or [])
    return (
        "### POST %s\n"
        "TÍTULO: %s\nDATA: %s\nAUTOR: %s\n"
        "SEÇÃO ATUAL: %s\nTEMAS ATUAIS: %s\nTIPO ATUAL: %s\nPALAVRAS ATUAIS: %s\n"
        "TEXTO:\n%s\n"
    ) % (
        r["slug"], r.get("titulo") or "", r.get("data") or "", r.get("autor") or "",
        r.get("tema_principal") or "", temas, r.get("tipo") or "", palavras,
        texto or "(sem corpo extraído)",
    )


def monta_lotes(registros):
    lotes, atual, chars = [], [], 0
    for r in registros:
        texto = texto_do_post(r["slug"])
        bloco = formata_post(r, texto)
        if atual and (len(atual) >= 50 or chars + len(bloco) > 170000):
            lotes.append(atual)
            atual, chars = [], 0
        atual.append({"slug": r["slug"], "bloco": bloco})
        chars += len(bloco)
    if atual:
        lotes.append(atual)
    return lotes


SISTEMA = """Você é editor sênior do acervo Assessoria Jurídica Popular (AJP).
Sua tarefa é revisar a categorização de posts do blog, sem inventar conteúdo.
Responda SOMENTE com JSON válido, sem markdown, sem comentários.

Taxonomia atual:
- 6 temas: assessoria-juridica-popular; educacao-popular; movimentos-sociais;
  direitos-humanos; memoria; teoria-critica.
- 6 tipos: formativo; evento; resenha; poesia; notícia; documento.

Critérios:
- tema_principal: eixo central do texto, um dos 6.
- temas_secundarios: no máximo 3, só quando o tema aparece de forma real.
- tipo: formato editorial predominante, não assunto.
- palavras: 4 a 6 termos livres, minúsculos, específicos.
- grupo: rótulo curto de similaridade (ex.: "caso judicial", "homenagem",
  "formação", "evento", "memória da ditadura", "teoria marxista").
- similar_a: slugs do MESMO lote que tratam do mesmo assunto/caso, se houver.
- confianca: 0 a 1.
- flags: subconjunto de reclassificar, ambiguo, duplicado_provavel, texto_curto,
  fora_do_tema, evento_desatualizado, homenagem, sem_palavras.
- justificativa: até 25 palavras.

Formato exato:
{"posts":[{"slug":"...","tema_principal":"...","temas_secundarios":["..."],
"tipo":"...","palavras":["..."],"grupo":"...","similar_a":["..."],
"confianca":0.0,"flags":["..."],"justificativa":"..."}],
"observacoes_lote":["..."]}
"""


def pedido(mensagens, max_tokens=16000, modelo=None):
    chave = os.environ.get("MARITACA_API_KEY")
    if not chave:
        raise SystemExit("MARITACA_API_KEY ausente")
    corpo = {
        "model": modelo or MODELO,
        "messages": mensagens,
        "max_tokens": max_tokens,
        "reasoning_effort": "low",
        "service_tier": "flex",
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Authorization": "Bearer " + chave, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.load(resp)


def com_retry(mensagens, max_tokens=16000, modelo=None):
    espera = 20
    for tentativa in range(1, 7):
        try:
            return pedido(mensagens, max_tokens, modelo)
        except urllib.error.HTTPError as e:
            corpo = e.read().decode("utf-8", "replace")[:800]
            if e.code in (429, 500, 502, 503, 504) and tentativa < 6:
                print("  HTTP %s; aguardando %ss" % (e.code, espera), flush=True)
                time.sleep(espera)
                espera = min(espera * 2, 300)
                continue
            raise RuntimeError("HTTP %s: %s" % (e.code, corpo))
        except Exception as e:
            if tentativa < 6:
                print("  erro %s; aguardando %ss" % (type(e).__name__, espera), flush=True)
                time.sleep(espera)
                espera = min(espera * 2, 300)
                continue
            raise


def extrai_json(texto):
    s = (texto or "").strip()
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.I)
    s = re.sub(r"\s*```$", "", s)
    i, j = s.find("{"), s.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("resposta sem JSON")
    return json.loads(s[i:j + 1])


def usa_tokens(resp):
    u = resp.get("usage") or {}
    return int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)



def _texto_arquivo(resp):
    txt = getattr(resp, "text", None)
    if txt:
        return txt
    return resp.content.decode("utf-8")


def _jsonl_lotes(lotes, caminho):
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        for i, lote in enumerate(lotes, 1):
            conteudo = "".join(p["bloco"] for p in lote)
            usuario = (
                "Revise os %d posts abaixo. Devolva exatamente o JSON pedido, "
                "com um item para cada slug, na mesma ordem.\n\n%s"
            ) % (len(lote), conteudo)
            body = {
                "model": MODELO,
                "messages": [
                    {"role": "system", "content": SISTEMA},
                    {"role": "user", "content": usuario},
                ],
                "max_tokens": 24000,
                "reasoning_effort": "low",
            }
            linha = {
                "custom_id": "lote-%02d" % i,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": body,
            }
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return caminho


def executa_batch(lotes):
    """Envia o lote pela Batch API e devolve (resultados, custo)."""
    from openai import OpenAI

    cliente = OpenAI(
        api_key=os.environ["MARITACA_API_KEY"],
        base_url="https://chat.maritaca.ai/api",
        timeout=600.0,
        max_retries=2,
    )
    os.makedirs(LOTES, exist_ok=True)
    jsonl = os.path.join(LOTES, "entrada-batch.jsonl")
    _jsonl_lotes(lotes, jsonl)
    print("batch: %d requisições, %.1f KB" % (
        len(lotes), os.path.getsize(jsonl) / 1024), flush=True)

    estado_path = os.path.join(LOTES, "batch.json")
    lote_id = None
    if os.path.exists(estado_path):
        estado = ler_json(estado_path)
        lote_id = estado.get("id")
        print("batch existente:", lote_id, flush=True)

    if not lote_id:
        arquivo = None
        for tentativa in range(1, 5):
            try:
                with open(jsonl, "rb") as f:
                    arquivo = cliente.files.create(file=f, purpose="batch")
                break
            except Exception as e:
                print("upload tentativa %d falhou: %s" % (tentativa, type(e).__name__), flush=True)
                if tentativa == 4:
                    raise
                time.sleep(15 * tentativa)
        lote = cliente.batches.create(
            input_file_id=arquivo.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"descricao": "revisao editorial do acervo AJP"},
        )
        lote_id = lote.id
        gravar_json(estado_path, {"id": lote_id, "status": lote.status,
                                  "input_file_id": arquivo.id})
        print("batch criado:", lote_id, lote.status, flush=True)

    while True:
        lote = cliente.batches.retrieve(lote_id)
        print("batch status:", lote.status, getattr(lote, "request_counts", ""), flush=True)
        if lote.status in ("completed", "failed", "expired", "cancelled"):
            break
        time.sleep(45)

    estado = ler_json(estado_path)
    estado["status"] = lote.status
    estado["output_file_id"] = getattr(lote, "output_file_id", None)
    estado["error_file_id"] = getattr(lote, "error_file_id", None)
    gravar_json(estado_path, estado)

    if not getattr(lote, "output_file_id", None):
        if getattr(lote, "error_file_id", None):
            erros = _texto_arquivo(cliente.files.content(lote.error_file_id))
            with io.open(os.path.join(LOTES, "erros-batch.jsonl"), "w",
                         encoding="utf-8", newline="\n") as f:
                f.write(erros)
            print(erros[:2000], flush=True)
        raise SystemExit("Batch terminou como %s" % lote.status)

    saida = _texto_arquivo(cliente.files.content(lote.output_file_id))
    with io.open(os.path.join(LOTES, "saida-batch.jsonl"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write(saida)

    resultados = {}
    erros = []
    total_in = total_out = 0
    for linha in saida.splitlines():
        if not linha.strip():
            continue
        obj = json.loads(linha)
        cid = obj.get("custom_id") or ""
        corpo = (obj.get("response") or {}).get("body") or {}
        conteudo = ((corpo.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        uso = corpo.get("usage") or {}
        total_in += int(uso.get("prompt_tokens") or 0)
        total_out += int(uso.get("completion_tokens") or 0)
        try:
            dados = extrai_json(conteudo)
            for p in dados.get("posts", []):
                resultados[p["slug"]] = p
        except Exception as e:
            erros.append({"custom_id": cid, "erro": str(e), "trecho": (conteudo or "")[:500]})
            print("erro no", cid, ":", e, flush=True)

    custo = total_in * PRECO_IN + total_out * PRECO_OUT
    gravar_json(os.path.join(SAIDA, "uso-batch.json"), {
        "input_tokens": total_in, "output_tokens": total_out,
        "custo_estimado_brl": round(custo, 4), "erros": erros,
    })
    print("batch concluído: %d posts, entrada %d, saída %d, R$ %.4f" % (
        len(resultados), total_in, total_out, custo), flush=True)
    return resultados, custo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch", action="store_true")
    args = ap.parse_args()

    os.makedirs(LOTES, exist_ok=True)
    registros = ler_json(INDICE)
    registros.sort(key=lambda r: (r.get("data") or "", r["slug"]))
    lotes = monta_lotes(registros)

    total_chars = sum(len(p["bloco"]) for lote in lotes for p in lote)
    print("posts:", len(registros))
    print("lotes:", len(lotes), "| maior lote:", max(len(l) for l in lotes), "posts")
    print("caracteres:", total_chars, "| tokens aprox:", round(total_chars / 3.6))
    if args.dry_run:
        for i, lote in enumerate(lotes, 1):
            print("  lote %02d: %d posts, %d chars" % (i, len(lote), sum(len(p["bloco"]) for p in lote)))
        return

    if args.batch:
        resultados, custo = executa_batch(lotes)
    else:
        custo = 0.0
        resultados = {}
        brutos = {}
        for i, lote in enumerate(lotes, 1):
            arq = os.path.join(LOTES, "lote-%02d.json" % i)
            if os.path.exists(arq):
                dados = ler_json(arq)
                for p in dados.get("posts", []):
                    resultados[p["slug"]] = p
                print("lote %02d: cache" % i, flush=True)
                continue

            if custo >= TETO:
                print("TETO DE CUSTO ATINGIDO: R$ %.4f" % custo, flush=True)
                break

            conteudo = "".join(p["bloco"] for p in lote)
            usuario = (
                "Revise os %d posts abaixo. Devolva exatamente o JSON pedido, "
                "com um item para cada slug, na mesma ordem.\n\n%s"
            ) % (len(lote), conteudo)
            print("lote %02d: %d posts, %d chars..." % (i, len(lote), len(conteudo)), flush=True)
            resp = com_retry([
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": usuario},
            ])
            texto = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "")
            dados = extrai_json(texto)
            dados["_raw_usage"] = resp.get("usage") or {}
            gravar_json(arq, dados)
            brutos[i] = texto
            for p in dados.get("posts", []):
                resultados[p["slug"]] = p

            pin, pout = usa_tokens(resp)
            custo += pin * PRECO_IN + pout * PRECO_OUT
            print("  ok: entrada %d, saída %d, custo acumulado R$ %.4f" % (pin, pout, custo), flush=True)

    gravar_json(os.path.join(SAIDA, "posts.json"), list(resultados.values()))

    # CSV por post
    csv_path = os.path.join(SAIDA, "revisao-posts.csv")
    with io.open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "slug", "titulo", "data", "autor",
            "tema_atual", "temas_atuais", "tipo_atual", "palavras_atuais",
            "tema_sugerido", "temas_sugeridos", "tipo_sugerido", "palavras_sugeridas",
            "grupo", "similar_a", "confianca", "flags", "justificativa",
        ])
        for r in registros:
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

    # Síntese global
    if not resultados:
        raise SystemExit("Nenhum resultado para sintetizar")
    compacto = []
    for r in registros:
        p = resultados.get(r["slug"])
        if not p:
            continue
        compacto.append({
            "slug": r["slug"], "titulo": r.get("titulo"),
            "atual": {
                "tema": r.get("tema_principal"), "temas": r.get("temas"),
                "tipo": r.get("tipo"), "palavras": r.get("palavras"),
            },
            "sugerido": {
                "tema": p.get("tema_principal"), "temas": p.get("temas_secundarios"),
                "tipo": p.get("tipo"), "palavras": p.get("palavras"),
                "grupo": p.get("grupo"), "confianca": p.get("confianca"),
                "flags": p.get("flags"),
            },
        })

    prompt_sintese = """Você é o editor-chefe do acervo AJP. Recebeu a revisão post a post
de 713 textos e deve produzir um diagnóstico da taxonomia. Responda SOMENTE JSON:
{
 "mapa_atual": {"tema": n, ...},
 "mapa_sugerido": {"tema": n, ...},
 "problemas": [{"tipo":"...","descricao":"...","exemplos":["slug"]}],
 "clusters": [{"grupo":"...","posts":n,"slugs":["..."],"recomendacao":"..."}],
 "tipos": {"ambiguidades":["..."],"recomendacoes":["..."]},
 "palavras_chave": {"recorrentes":["..."],"lacunas":["..."],"recomendacoes":["..."]},
 "definicoes": {"tema":"definição curta e operacional", ...},
 "migracao": ["regra prática 1", "..."],
 "relatorio_md": "relatório em Markdown, até 2500 palavras"
}
Não invente slugs. Use os dados abaixo.
"""
    resp = com_retry([
        {"role": "system", "content": prompt_sintese},
        {"role": "user", "content": json.dumps(compacto, ensure_ascii=False)},
    ], max_tokens=24000, modelo=MODELO_SINTESE)
    texto = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "")
    sintese = extrai_json(texto)
    gravar_json(os.path.join(SAIDA, "sintese.json"), sintese)
    with io.open(os.path.join(SAIDA, "relatorio-taxonomia.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sintese.get("relatorio_md") or "# Relatório\n")
    pin, pout = usa_tokens(resp)
    custo += pin * PRECO_IN_S5 + pout * PRECO_OUT_S5

    gravar_json(os.path.join(SAIDA, "uso.json"), {
        "modelo_lotes": MODELO, "modelo_sintese": MODELO_SINTESE, "service_tier_sintese": "flex",
        "custo_estimado_brl": round(custo, 4), "teto_brl": TETO,
        "posts": len(resultados), "lotes": len(lotes),
    })
    print("FIM | posts revisados: %d | custo estimado: R$ %.4f" % (len(resultados), custo))


if __name__ == "__main__":
    main()
