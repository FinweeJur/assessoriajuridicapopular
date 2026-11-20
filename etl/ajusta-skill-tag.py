import io

p = r"C:\Users\teste\.claude\skills\design\SKILL.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("Tags menores (`.66rem`)", "Tags menores (`.75rem`, 12 px)")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("skill tag:", "`.75rem`, 12 px" in io.open(p, encoding="utf-8").read())
