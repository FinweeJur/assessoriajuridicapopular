"""Recria o site inteiro na ordem certa.

A ordem importa: o índice é reescrito pelo gerador de páginas e depois recebe
tipo e palavras-chave. Rodar fora de ordem deixa cartão sem etiqueta.

Uso: python etl/tudo.py [--sem-paginas]
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ETL = os.path.join(RAIZ, "etl")


def roda(script, *args):
    caminho = os.path.join(ETL, script)
    print("\n▶", script, " ".join(args))
    subprocess.run([sys.executable, caminho, *args], cwd=RAIZ, check=True)


def main():
    sem_paginas = "--sem-paginas" in sys.argv
    if not sem_paginas:
        roda("alinha-modelo.py")
        roda("monta-paginas.py")
    roda("classifica.py")          # tipo de texto
    roda("palavras.py")            # palavras-chave
    roda("tema-principal.py")      # um tema por texto, sem duplicar seção
    roda("marca-redes.py")         # RENAP, IPDMS e RENAJU/AJUPs
    roda("monta-autores.py")       # páginas de autor
    roda("monta-secoes.py")        # 6 seções + blog
    roda("gera-dados-colecoes.py")  # dados de memória, trilhas, biblioteca e cultura
    roda("monta-colecoes.py")       # páginas das coleções
    roda("monta-leapspace.py")     # panorama no comparado
    roda("monta-indice.py")        # indice wiki do site
    roda("marca-subnavs.py")       # subnavegacao dos hubs (Blog, Autores, Poemas, Mística, Citações)
    roda("marca-teses.py")          # teses e dissertações do Catálogo CAPES
    roda("marca-publicacoes.py")    # IPDMS e Cadernos da RENAP
    roda("marca-autores.py")        # fotos dos colunistas
    roda("alinha-capa.py")         # topo e rodapé da capa
    roda("atualiza-indice.py")     # lista da capa
    print("\npronto")


if __name__ == "__main__":
    main()
