"""Mede a pilha de verificação ponta a ponta.

Cada estágio tem seu próprio conjunto, porque cada um mede coisa diferente:

  estágio 1 (cobertura)     golden 152 · lacunas distantes 20 · adjacentes 16
  estágio 2 (ancoragem)     pares de deriva sutil + fabricação em artigo real
  estágio 3 (consistência)  amostra pequena — é o estágio caro (N gerações)

Uso:
    venv-com-torch/bin/python medir.py [estagios]
    estagios: 1, 2, 3 ou "todos" (default: 1,2 — o 3 é lento)
"""

import json
import pathlib
import statistics
import sys
import time

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1]))

from pilha import (  # noqa: E402
    avaliar_ancoragem,
    avaliar_cobertura,
    avaliar_consistencia,
    carregar_nli,
    centroides_de_tema,
)

VAULT = pathlib.Path.home() / "vault"

LACUNAS_DISTANTES = [
    "como faço um risoto de cogumelos cremoso",
    "quais os sintomas de deficiência de vitamina B12",
    "o que é campo harmônico maior na música",
    "como escolher a abertura do diafragma para retrato",
    "como a fotossíntese converte luz em energia",
    "quais foram as causas da revolução francesa",
    "como plantar tomate em vaso pequeno",
    "qual a rega ideal para suculentas",
]

LACUNAS_ADJACENTES = [
    "como funciona o aperto de mão do protocolo TLS com certificados",
    "qual a diferença entre TLS 1.2 e TLS 1.3 no estabelecimento de sessão",
    "como um compilador analisa a sintaxe do código fonte",
    "qual a diferença entre análise léxica e análise sintática",
    "como estender o kubernetes com um controlador customizado",
    "o que é um custom resource definition e quando criar um",
    "como o escalonador do sistema operacional decide qual processo roda",
    "qual a diferença entre memória virtual e memória física",
]

# (contexto, afirmação, ancorada?) — uma mudança por deriva
DERIVAS = [
    (
        "O circuit breaker abre após um número configurável de falhas consecutivas e "
        "permanece aberto por um intervalo antes de permitir uma chamada de teste.",
        "O circuit breaker abre após um número configurável de falhas consecutivas.",
        True,
    ),
    (
        "O circuit breaker abre após um número configurável de falhas consecutivas e "
        "permanece aberto por um intervalo antes de permitir uma chamada de teste.",
        "O circuit breaker NÃO abre após falhas consecutivas.",
        False,
    ),
    (
        "O índice acelera consultas de leitura, mas torna as escritas mais lentas porque "
        "cada inserção precisa atualizar a estrutura.",
        "O índice torna as escritas mais lentas.",
        True,
    ),
    (
        "O índice acelera consultas de leitura, mas torna as escritas mais lentas porque "
        "cada inserção precisa atualizar a estrutura.",
        "O índice torna as escritas mais rápidas.",
        False,
    ),
    (
        "A prática espaçada distribui os estudos ao longo do tempo e produz retenção "
        "superior à prática massificada, embora pareça mais difícil durante o aprendizado.",
        "A prática espaçada parece mais difícil durante o aprendizado.",
        True,
    ),
    (
        "A prática espaçada distribui os estudos ao longo do tempo e produz retenção "
        "superior à prática massificada, embora pareça mais difícil durante o aprendizado.",
        "A prática massificada produz retenção superior à prática espaçada.",
        False,
    ),
]

FABRICADAS = [
    "O protocolo exige exatamente sete etapas de validação antes de qualquer escrita.",
    "Estudos de 2019 mostraram que a técnica reduz o custo operacional em 43 por cento.",
    "A especificação proíbe o uso desse mecanismo em ambientes com mais de doze nós.",
]


def carregar_indice():
    caminho = VAULT / "kb_state/embeddings.json"
    return json.loads(caminho.read_text(encoding="utf-8"))


def pares_artigo_fonte(limite=8):
    """(artigo, texto, fonte, conteúdo) casando o `source` do frontmatter."""
    wiki = VAULT / "wiki"
    fontes = {}
    for arquivo in (wiki / "_sources").rglob("*.md"):
        fontes.setdefault(arquivo.name, arquivo)

    pares = []
    for md in sorted(wiki.rglob("*.md")):
        if any(p.startswith(("_", ".")) for p in md.relative_to(wiki).parts):
            continue
        texto = md.read_text(encoding="utf-8", errors="replace")
        nome = next(
            (linha.split(":", 1)[1].strip()
             for linha in texto[:600].splitlines()
             if linha.startswith("source:")),
            None,
        )
        if not nome or nome not in fontes:
            continue
        conteudo = fontes[nome].read_text(encoding="utf-8", errors="replace")
        if len(conteudo) < 1500:
            continue
        pares.append((md, texto, fontes[nome], conteudo))
        if len(pares) >= limite:
            break
    return pares


def estagio_1(centroides):
    print("\n" + "=" * 72)
    print("ESTÁGIO 1 — cobertura (o acervo tem material?)")
    print("=" * 72)

    from kb.bench import golden_path, load_golden
    from kb.config import STATE_DIR

    casos = load_golden(golden_path(STATE_DIR))
    grupos = {
        "golden (tem resposta)": [c["question"] for c in casos],
        "lacuna distante": LACUNAS_DISTANTES,
        "lacuna adjacente": LACUNAS_ADJACENTES,
    }

    print(f"\n{'conjunto':24} {'coberto':>9} {'ambíguo':>9} {'lacuna':>9}  {'mediana':>9}")
    print("-" * 72)
    for nome, perguntas in grupos.items():
        vereditos, similaridades = [], []
        for pergunta in perguntas:
            r = avaliar_cobertura(pergunta, centroides)
            vereditos.append(r["veredito"])
            similaridades.append(r["similaridade"])
        print(
            f"{nome:24} {vereditos.count('coberto'):9} {vereditos.count('ambiguo'):9} "
            f"{vereditos.count('lacuna'):9}  {statistics.median(similaridades):9.4f}"
        )

    print("\nleitura: golden deve concentrar em 'coberto'; lacunas em 'lacuna'.")
    print("'ambíguo' é a faixa que o estágio 3 desempata.")


def estagio_2(nli):
    print("\n" + "=" * 72)
    print("ESTÁGIO 2 — ancoragem (a afirmação decorre do contexto?)")
    print("=" * 72)

    print("\n-- deriva sutil (negação, número trocado, comparação invertida) --")
    acertos = 0
    for contexto, afirmacao, ancorada in DERIVAS:
        resultado = avaliar_ancoragem(afirmacao, contexto, nli)
        if not resultado:
            continue
        veredito = resultado[0]["veredito"]
        certo = (veredito == "ancorada") == ancorada
        acertos += certo
        print(
            f"  {'OK ' if certo else 'ERRO'} esperado={'ancorada' if ancorada else 'deriva':9} "
            f"veredito={veredito:11} ent={resultado[0]['entailment']:.3f} "
            f"contra={resultado[0]['contradicao']:.3f}"
        )
    print(f"  acerto: {acertos}/{len(DERIVAS)}")

    print("\n-- artigo real: legítimas contra fabricadas injetadas --")
    pares = pares_artigo_fonte()
    print(f"  pares artigo↔fonte: {len(pares)}")
    if not pares:
        print("  sem pares — a proveniência não permite medir")
        return

    legitimas_ok = legitimas_total = 0
    for _md, texto, _, conteudo in pares[:4]:
        resultado = avaliar_ancoragem(texto, conteudo, nli)
        legitimas_total += len(resultado)
        legitimas_ok += sum(1 for r in resultado if r["veredito"] == "ancorada")
    if legitimas_total:
        print(
            f"  legítimas ancoradas: {legitimas_ok}/{legitimas_total} "
            f"({legitimas_ok / legitimas_total:.0%})  <- preservação"
        )

    detectadas = total = 0
    for _, _, _, conteudo in pares[:4]:
        for fabricada in FABRICADAS:
            resultado = avaliar_ancoragem(fabricada, conteudo, nli)
            if not resultado:
                continue
            total += 1
            detectadas += resultado[0]["veredito"] != "ancorada"
    if total:
        print(f"  fabricadas detectadas: {detectadas}/{total} ({detectadas / total:.0%})")


def estagio_3():
    print("\n" + "=" * 72)
    print("ESTÁGIO 3 — consistência (as gerações concordam?)")
    print("=" * 72)
    print("estágio caro: N gerações por pergunta. Amostra pequena de propósito.\n")

    from kb.search import search

    amostra = [
        ("o que é um circuit breaker", True),
        ("como funciona a prática espaçada no estudo", True),
        ("como funciona o aperto de mão do protocolo TLS", False),
        ("como escolher a abertura do diafragma para retrato", False),
    ]

    for pergunta, tem_resposta in amostra:
        resultados = search(pergunta, top_k=3, mode="hybrid")
        contexto = "\n\n".join(
            r["path"].read_text(encoding="utf-8", errors="replace")[:400] for r in resultados
        )
        inicio = time.perf_counter()
        r = avaliar_consistencia(pergunta, contexto, geracoes=3)
        print(
            f"  {'TEM ' if tem_resposta else 'NÃO '} {r['veredito']:12} "
            f"concordância={r['concordancia']:.3f}  ({time.perf_counter() - inicio:.0f}s)  {pergunta[:40]}"
        )

    print("\nleitura: se 'não tem' der instável e 'tem' der estável, o estágio serve.")
    print("se os dois derem igual, a consistência não separa e o estágio cai.")


def main():
    pedido = sys.argv[1] if len(sys.argv) > 1 else "1,2"
    estagios = {"1", "2", "3"} if pedido == "todos" else set(pedido.split(","))

    if "1" in estagios:
        print("montando centroides de tema a partir do índice ...")
        centroides = centroides_de_tema(carregar_indice())
        print(f"temas: {len(centroides)}")
        estagio_1(centroides)

    if "2" in estagios:
        print("\ncarregando NLI ...")
        estagio_2(carregar_nli())

    if "3" in estagios:
        estagio_3()


main()
