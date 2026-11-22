import io

# atualiza-indice.py
p = "etl/atualiza-indice.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('''    tags = ""
    if palavras_tags:
        tags = '<span class="item__tags">%s</span>' % "".join(
            '<span class="item__tag">%s</span>' % esc(p) for p in palavras_tags)''',
'''    tags = ""
    if palavras_tags:
        tags = '<span class="item__tags">%s</span>' % "".join(
            '<span class="item__tag">%s</span>' % esc(p) for p in palavras_tags)
    redes = registro.get("redes") or []
    rotulos = {"renap": "RENAP", "ipdms": "IPDMS", "renaju-ajup": "RENAJU/AJUPs"}
    redes_tags = ""
    if redes:
        redes_tags = '<span class="item__redes">%s</span>' % "".join(
            '<span class="item__rede">%s</span>' % rotulos[r] for r in redes if r in rotulos)''', 1)
s = s.replace('data-palavras="%s">', 'data-palavras="%s" data-redes="%s">', 1)
s = s.replace('''          %s
          <span class="item__ficha">%s · %s</span>''',
'''          %s
          %s
          <span class="item__ficha">%s · %s</span>''', 1)
s = s.replace('''        esc(" ".join(registro.get("palavras") or [])),
        esc(registro["slug"]),''',
'''        esc(" ".join(registro.get("palavras") or [])),
        esc(" ".join(registro.get("redes") or [])),
        esc(registro["slug"]),''', 1)
s = s.replace('''        tags, esc(registro.get("autor")), esc(data_curta(registro.get("data"))))''',
'''        tags, redes_tags, esc(registro.get("autor")), esc(data_curta(registro.get("data"))))''', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# monta-secoes.py
p = "etl/monta-secoes.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('''    tags = ""
    if palavras:
        tags = '<span class="item__tags">%s</span>' % "".join(
            '<span class="item__tag">%s</span>' % esc(p) for p in palavras)''',
'''    tags = ""
    if palavras:
        tags = '<span class="item__tags">%s</span>' % "".join(
            '<span class="item__tag">%s</span>' % esc(p) for p in palavras)
    redes = registro.get("redes") or []
    rotulos = {"renap": "RENAP", "ipdms": "IPDMS", "renaju-ajup": "RENAJU/AJUPs"}
    redes_tags = ""
    if redes:
        redes_tags = '<span class="item__redes">%s</span>' % "".join(
            '<span class="item__rede">%s</span>' % rotulos[r] for r in redes if r in rotulos)''', 1)
s = s.replace('data-palavras="%s">', 'data-palavras="%s" data-redes="%s">', 1)
s = s.replace('''          %s
          <span class="item__ficha">%s · %s</span>''',
'''          %s
          %s
          <span class="item__ficha">%s · %s</span>''', 1)
s = s.replace('''        esc(" ".join(registro.get("palavras") or [])),
        esc(registro["slug"]),''',
'''        esc(" ".join(registro.get("palavras") or [])),
        esc(" ".join(registro.get("redes") or [])),
        esc(registro["slug"]),''', 1)
s = s.replace('''        tags,
        esc(registro.get("autor")), esc(data_curta(registro.get("data"))))''',
'''        tags, redes_tags,
        esc(registro.get("autor")), esc(data_curta(registro.get("data"))))''', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("cards de redes atualizados")
