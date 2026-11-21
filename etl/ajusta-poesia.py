import io
import re

p = "poemas.html"
t = io.open(p, encoding="utf-8").read()
t = t.replace("Poemas do Caderno e poesia do blog — AJP · Assessoria Jurídica Popular",
              "Caderno de Poesias e poesia do blog · AJP — Assessoria Jurídica Popular")
t = t.replace('data-titulo="Poemas do Caderno e poesia do blog"',
              'data-titulo="Caderno de Poesias e poesia do blog"')
t = t.replace("Poemas do Caderno e poesia do blog", "Caderno de Poesias e poesia do blog")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print(re.search(r"<title>(.*?)</title>", t, re.S).group(1))

for p in ["etl/caderno-sumario.py", "etl/liga-poemas.py"]:
    s = io.open(p, encoding="utf-8").read()
    s = s.replace("caderno-de-poesias.html", "poemas.html")
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(p, "->", "poemas.html" in s)
