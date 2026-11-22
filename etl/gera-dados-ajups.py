"""Gera `dados/ajups.json` a partir do mapeamento histórico e da pesquisa de 2026.

Fonte histórica: post "Mapeamento" (2011), lista em
`docs/mapeamento-ajups-2011.md`.
Pesquisa de 2026: `docs/redes-2026-11-22.json` e sites oficiais.

Regra: não inventar perfil. Onde o site morreu e o perfil não foi confirmado,
`status` fica `site_fora_do_ar` ou `nao_verificado`.
"""
import io
import json
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "dados", "ajups.json")
FONTE = "https://assessoriajuridicapopular.blogspot.com/2011/10/mapeamento.html"
VERIFICADO = "2026-11-22"


def item(nome, sigla, tipo, uf, cidade, site=None, instagram=None, facebook=None,
         youtube=None, repositorio=None, status="nao_verificado", fonte=FONTE,
         observacao=""):
    return {
        "nome": nome, "sigla": sigla, "tipo": tipo, "uf": uf, "cidade": cidade,
        "site": site, "instagram": instagram, "facebook": facebook,
        "youtube": youtube, "repositorio": repositorio,
        "status": status, "fonte": fonte, "verificado_em": VERIFICADO,
        "observacao": observacao,
    }


redes = [
    item("Rede Nacional de Advogados e Advogadas Populares", "RENAP", "rede", "BR", "",
         "https://www.renap.org.br/", "https://www.instagram.com/renapbrasil/",
         None, None, "https://www.renap.org.br/publicacoes", "ativo",
         "https://www.renap.org.br/",
         "Site oficial; Instagram @RenapBrasil; Cadernos 1-6 e Defensoria 1-2."),
    item("Rede Nacional de Assessoria Jurídica Universitária / AJUPs", "RENAJU/AJUPs",
         "rede", "BR", "", None, "https://www.instagram.com/ajupsbrasil/", None, None,
         None, "informado_pelo_dono", "https://www.instagram.com/ajupsbrasil/",
         "renaju.org.br fora do ar; perfil informado pelo dono, confirmar manualmente."),
    item("Instituto de Pesquisa, Direitos e Movimentos Sociais", "IPDMS", "rede", "BR", "",
         "https://ipdms.org.br/", None, "https://www.facebook.com/Ipdms/", None,
         "https://ipdms.org.br/publicacoes/", "ativo", "https://ipdms.org.br/",
         "Biblioteca, Revista InSURgência, Cadernos Insurgentes e anais."),
]

advocacias = [
    item("Acesso — Cidadania e Direitos Humanos", "Acesso", "advocacia", "RS", "Porto Alegre",
         None, None, None, None, None, "site_fora_do_ar", observacao="acesso.org.br não resolve em 2026."),
    item("Associação de Advogados de Trabalhadores Rurais no Estado da Bahia", "AATR-BA",
         "advocacia", "BA", "Salvador", "https://www.aatr.org.br/",
         "https://www.instagram.com/aatrba", "https://www.facebook.com/aatrba/",
         "https://www.youtube.com/channel/UCG81NgFRlWOZvcHATrzo7ww",
         "https://www.aatr.org.br/acervo", "ativo", "https://www.aatr.org.br/",
         "Link antigo http://www.aatr.org.br/site/ falhou; usar HTTPS."),
    item("Centro de Assessoria Jurídica Popular Mariana Criola", "Mariana Criola",
         "advocacia", "RJ", "Rio de Janeiro", None, None, None, None, None,
         "site_fora_do_ar", observacao="marianacriola.org.br não resolve em 2026."),
    item("Dignitatis — Assessoria Técnica Popular", "Dignitatis", "advocacia", "PB", "",
         "http://dignitatis-assessoria.blogspot.com/", None, None, None, None,
         "ativo", "http://dignitatis-assessoria.blogspot.com/",
         "Blogspot ativo; não foi localizado perfil social no site."),
    item("Escritório de Assessoria Jurídica Popular Frei Tito de Alencar", "Frei Tito",
         "advocacia", "CE", "Fortaleza", None, None, None, None, None,
         "site_fora_do_ar", observacao="escritoriofreitito.org.br não resolve em 2026."),
    item("Gabinete de Assessoria Jurídica às Organizações Populares", "GAJOP-PE",
         "advocacia", "PE", "Recife", None, None, None, None, None,
         "site_fora_do_ar", observacao="gajop.org.br não resolve em 2026."),
    item("Instituto Apoio Jurídico Popular", "AJUP-RJ", "advocacia", "RJ",
         "Rio de Janeiro", "instituto-apoio-juridico-popular-ajup.html", None, None,
         None, None, "historico", "instituto-apoio-juridico-popular-ajup.html",
         "Página do acervo; o site institucional não foi confirmado."),
    item("Sociedade Maranhense de Direitos Humanos", "SMDH-MA", "advocacia", "MA",
         "São Luís", "https://smdh.org.br/", "https://www.instagram.com/smdhvida/",
         "https://www.facebook.com/smdh.vida/", "https://www.youtube.com/user/SMDHVida",
         "https://smdh.org.br/publicacoes/", "ativo", "https://smdh.org.br/"),
    item("Terra de Direitos — Organização de Direitos Humanos", "Terra de Direitos",
         "advocacia", "PR", "Curitiba", "https://terradedireitos.org.br/",
         "https://www.instagram.com/terradedireitos",
         "https://www.facebook.com/terradedireitos",
         "https://www.youtube.com/channel/UCkdy0w7C6RAAYXRn9gZIxUQ",
         "https://terradedireitos.org.br/biblioteca/publicacoes", "ativo",
         "https://terradedireitos.org.br/"),
]

universitarias = [
    item("AIDH — Assessoria Interdisciplinar e Intercultural em Direitos Humanos",
         "AIDH", "universitaria", "PA", "Altamira",
         "https://assessoriajuridicapopular.blogspot.com/2011/03/carta-de-divulgacao-do-nascimento-de.html",
         status="historico"),
    item("CAJU — Centro de Assessoria Jurídica Universitária", "CAJU", "universitaria",
         "CE", "Fortaleza", status="nao_verificado"),
    item("CAJUÍNA — Centro de Assessoria Jurídica Universitária Popular de Teresina",
         "CAJUÍNA", "universitaria", "PI", "Teresina", status="nao_verificado"),
    item("CAJUP — Centro de Assessoria Jurídica Universitária Popular Mandacaru",
         "CAJUP", "universitaria", "PI", "Teresina", status="nao_verificado"),
    item("CORAJE — Corpo de Assessoria Jurídica Estudantil", "CORAJE",
         "universitaria", "PI", "Teresina", status="nao_verificado"),
    item("NAJUC — Núcleo de Assessoria Jurídica Comunitária", "NAJUC",
         "universitaria", "CE", "Fortaleza", status="nao_verificado"),
    item("NAJUC — Núcleo de Assessoria Jurídica Universitária Comunitária Justiça e Atitude",
         "NAJUC", "universitaria", "PI", "Teresina", status="nao_verificado"),
    item("NAJUP — Núcleo de Assessoria Jurídica Popular", "NAJUP", "universitaria",
         "RS", "Porto Alegre", "http://najup.wordpress.com/", status="historico"),
    item("NAJUP — Núcleo de Assessoria Jurídica Popular Direito nas Ruas", "NAJUP",
         "universitaria", "PE", "Recife", status="nao_verificado"),
    item("NAJUP — Núcleo de Assessoria Jurídica Universitária Popular", "NAJUP",
         "universitaria", "GO", "Goiânia", status="nao_verificado"),
    item("NAJUP Cabano", "NAJUP Cabano", "universitaria", "PA", "Santarém",
         "http://www.facebook.com/profile.php?id=100002995853439", status="historico"),
    item("NAJUPI — Núcleo de Assessoria Jurídica Universitária Popular Roda Viva",
         "NAJUPI", "universitaria", "RS", "Caxias do Sul",
         "http://najupi.blogspot.com/", status="historico"),
    item("NAJUP — Núcleo de Assessoria Jurídica Universitária Popular Isa Cunha",
         "NAJUP Isa Cunha", "universitaria", "PA", "Belém", status="nao_verificado"),
    item("NAJUP — Núcleo de Assessoria Jurídica Universitária Popular Negro Cosme",
         "NAJUP Negro Cosme", "universitaria", "MA", "São Luís",
         "http://najupnegrocosme.blogspot.com/", status="historico"),
    item("NAJUPAK — Núcleo de Assessoria Jurídica Universitária Popular Aldeia Kaiapó",
         "NAJUPAK", "universitaria", "PA", "Belém",
         "http://najupak-belem.blogspot.com/", status="historico"),
    item("NIJUC — Núcleo de Interação Jurídica Comunitária", "NIJUC",
         "universitaria", "RS", "Santa Maria", status="nao_verificado"),
    item("P@JE — Programa de Assessoria Jurídica Estudantil", "P@JE",
         "universitaria", "CE", "Juazeiro do Norte",
         "http://paje-cariri.blogspot.com/", status="historico"),
    item("PAJUP — Programa de Assessoria Jurídica Universitária Popular", "PAJUP",
         "universitaria", "MA", "São Luís", "http://pajup-undb.blogspot.com/",
         status="historico"),
    item("Projeto Estação de Direitos", "Estação de Direitos", "universitaria",
         "RN", "Natal", status="nao_verificado"),
    item("SAJU — Serviço de Assessoria Jurídica Popular", "SAJU UNIFOR",
         "universitaria", "CE", "Fortaleza", "http://sajuceara.wordpress.com/",
         status="historico"),
    item("SAJU — Serviço de Assessoria Jurídica Universitária", "SAJU USP",
         "universitaria", "SP", "São Paulo", "http://sajusp.blogspot.com/",
         status="historico"),
    item("SAJU — Serviço de Assessoria Jurídica Universitária", "SAJU UFRGS",
         "universitaria", "RS", "Porto Alegre", "http://www.ufrgs.br/saju/",
         status="historico"),
    item("SAJU — Serviço de Assessoria Jurídica Universitária", "SAJU UFBA",
         "universitaria", "BA", "Salvador", "http://sajubahia.blogspot.com/",
         status="historico"),
    item("SAJUP — Serviço de Assessoria Jurídica Universitária Popular", "SAJUP UFPR",
         "universitaria", "PR", "Curitiba", status="nao_verificado"),
    item("SURJA — Serviço Universitário de Resistência e Justiça para Autonomia",
         "SURJA", "universitaria", "RS", "Pelotas",
         "http://surjaufpel.blogspot.com/", status="historico"),
]

movimentos = [
    item("Levante Popular da Juventude", "Levante", "movimento", "BR", "",
         "http://levantepopulardajuventude.blogspot.com.br/", status="historico",
         observacao="Link de 2011; confirmar site/perfil atual."),
    item("Movimento dos Trabalhadores Rurais Sem-Terra", "MST", "movimento", "BR", "",
         "https://mst.org.br/", status="ativo", fonte="https://mst.org.br/"),
    item("Resistência Popular", "Resistência Popular", "movimento", "BR", "",
         "http://resistenciapopular.blogspot.com/", status="historico",
         observacao="Link de 2011; confirmar site/perfil atual."),
]

dados = {
    "gerado_em": VERIFICADO,
    "fonte_historica": FONTE,
    "metodo": "Lista de 2011 confrontada com sites oficiais em 22/11/2026. "
              "Instagram/Facebook não foram raspados; links sociais são os publicados "
              "pelos sites oficiais ou informados pelo dono.",
    "redes": redes,
    "advocacias": advocacias,
    "universitarias": universitarias,
    "movimentos": movimentos,
}
io.open(SAIDA, "w", encoding="utf-8", newline="\n").write(
    json.dumps(dados, ensure_ascii=False, indent=1) + "\n"
)
print("ajups:", len(redes) + len(advocacias) + len(universitarias) + len(movimentos),
      "| redes", len(redes), "advocacias", len(advocacias),
      "universitarias", len(universitarias), "movimentos", len(movimentos))
