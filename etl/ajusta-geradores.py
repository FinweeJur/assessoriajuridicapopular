"""Mantém os geradores alinhados às correções editoriais."""
import io

RAIZ = r"X:\DevCoder\assessoriajuridicapopular"


def ler(rel):
    with io.open(RAIZ + "\\" + rel, encoding="utf-8") as f:
        return f.read()


def gravar(rel, t):
    with io.open(RAIZ + "\\" + rel, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)


p = "etl/glossario-linha.py"
t = ler(p)
t = t.replace('"https://www.controlepopular.com.br/jurisprudencia/"',
              '"assessoria-juridica-popular-no-mundo.html"')
t = t.replace('"coracao-sem-medo.html"', '""')

velho = '''linhas = "\\n".join(
    '        <li><b>%s</b> — %s <a href="%s"%s>ver</a></li>'
    % (ms.esc(termo), ms.esc(definicao), url,
       ' target="_blank" rel="noopener"' if url.startswith("http") else "")
    for termo, definicao, url in TERMOS)'''
novo = '''def linha_termo(termo, definicao, url):
    if not url:
        return '        <li><b>%s</b> — %s</li>' % (ms.esc(termo), ms.esc(definicao))
    externo = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
    return '        <li><b>%s</b> — %s <a href="%s"%s>ver</a></li>' % (
        ms.esc(termo), ms.esc(definicao), url, externo)


linhas = "\\n".join(linha_termo(termo, definicao, url) for termo, definicao, url in TERMOS)'''
if velho in t:
    t = t.replace(velho, novo, 1)
gravar(p, t)
print("glossario gen:", "linha_termo" in t)

p = "etl/paginas-extras.py"
t = ler(p)
linha = '<li><span class="emoji" aria-hidden="true">📰</span><b>Boletim Tricontinental</b> — análises do Sul global.</li>'
if linha in t:
    t = t.replace(linha, "", 1)
    t = t.replace(
        '<li><span class="emoji" aria-hidden="true">📚</span><b>Textos marxistas sobre cultura</b> — seleção de leitura.</li>',
        linha + '\n        <li><span class="emoji" aria-hidden="true">📚</span><b>Textos marxistas sobre cultura</b> — seleção de leitura.</li>',
        1)
    gravar(p, t)
print("extras tricontinental:", t.find("Boletim Tricontinental") > t.find("Política e cultura"))
