"""Pilha de verificação de resposta: cobertura, ancoragem e consistência.

Três modelos pequenos, três perguntas diferentes, cada um cobrindo o ponto
cego do outro. Todos os limiares vêm de medição registrada em
`docs/research/2026-07-30-politica-de-corpus/`.

    ESTÁGIO 1 — cobertura (antes de responder)
        "o acervo tem material sobre isto?"
        embedding da pergunta contra o centroide de cada tema
        mede: lacuna. Não vê negação.

    ESTÁGIO 2 — ancoragem (depois de responder)
        "cada afirmação decorre do contexto?"
        cosseno seleciona a premissa, NLI julga o entailment
        mede: deriva. Não vê ausência.

    ESTÁGIO 3 — consistência (no desempate)
        "as gerações concordam entre si?"
        N gerações, concordância entre elas
        mede: instabilidade. Não vê nem uma nem outra.

Por que cosseno E NLI no estágio 2, e não um ou outro: o NLI precisa de um par
premissa/hipótese, e é o retrieval por embedding que produz a premissa. Medido:
contra deriva sutil (negação, número trocado, comparação invertida) o cosseno
acerta 6/12 — chute num conjunto metade/metade — e o NLI acerta 12/12. Contra
fabricação grosseira o cosseno já ia bem (100%/87%). São complementares.

Por que consistência e não "pergunte ao modelo se ele tem confiança": a
verbalização foi medida aqui (83% de falso alarme) e na literatura (a pior das
três famílias de estimativa de incerteza). Consistência é a que funciona.
"""

import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# --- limiares medidos ---------------------------------------------------
# Estágio 1: faixa ambígua de `teste_2_dois_estagios`. Um limiar único resolve
# 98% das perguntas e deixa 10 de 16 lacunas adjacentes passarem; a faixa é o
# que compra precisão.
COBERTURA_ALTA = 0.46
COBERTURA_BAIXA = 0.36

# Estágio 2: o NLI decide por qual rótulo domina. O cosseno só seleciona a
# premissa, então não tem limiar de decisão — tem teto de candidatas.
PREMISSAS_POR_AFIRMACAO = 3

# Tamanho da premissa, em sentenças. É o parâmetro que mais importa e o mais
# fácil de errar: uma afirmação de artigo sintetiza várias sentenças da fonte,
# e julgada contra UMA sentença o veredito correto é `neutral` — não existe
# entailment de uma frase para um resumo de parágrafo.
#
# Medido em artigos reais contra suas fontes (preservação / detecção):
#    1 sentença   18% / —     (mediana de entailment 0,067)
#    4            49% / 100%
#    6            56% / 100%  (mediana 0,755)
#    8            59% / 100%
#   12            72% / 100%  <- platô
#   16            70% / 100%
#
# A detecção de fabricação não cede em nenhuma faixa: afirmação inventada é
# estranha ao contexto inteiro, não só à sentença vizinha. O risco de premissa
# grande diluir o sinal não se materializou neste intervalo.
SENTENCAS_POR_PREMISSA = 12

MODELO_NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"


def _normaliza(vetor):
    norma = math.sqrt(sum(x * x for x in vetor))
    return [x / norma for x in vetor] if norma else vetor


def _cosseno(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


# --- estágio 1: cobertura -----------------------------------------------


def centroides_de_tema(indice_embeddings, limiar_cluster=0.88):
    """Centroide de cada tema, a partir dos clusters do índice de embeddings.

    Depois do reagrupamento do ticket 006 os temas serão explícitos e este
    passo desaparece — o centroide sai do próprio artigo de tema.
    """
    artigos = {}
    for relpath, entrada in indice_embeddings["articles"].items():
        vetores = [c["vector"] for c in entrada.get("chunks", []) if c.get("vector")]
        if not vetores:
            continue
        dim = len(vetores[0])
        artigos[relpath] = _normaliza(
            [sum(v[i] for v in vetores) / len(vetores) for i in range(dim)]
        )

    chaves = list(artigos)
    pai = {k: k for k in chaves}

    def raiz(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for i, a in enumerate(chaves):
        va = artigos[a]
        for b in chaves[i + 1:]:
            if _cosseno(va, artigos[b]) >= limiar_cluster:
                ra, rb = raiz(a), raiz(b)
                if ra != rb:
                    pai[ra] = rb

    grupos = {}
    for k in chaves:
        grupos.setdefault(raiz(k), []).append(k)

    centroides = []
    for membros in grupos.values():
        if len(membros) < 2:
            continue
        dim = len(artigos[membros[0]])
        centro = [sum(artigos[m][i] for m in membros) / len(membros) for i in range(dim)]
        centroides.append({"centro": _normaliza(centro), "membros": membros})
    return centroides


def avaliar_cobertura(pergunta, centroides):
    """O acervo cobre o assunto? Devolve veredito e o tema mais próximo."""
    from kb.embeddings import _QUERY_PREFIX, embed_texts

    vetor = _normaliza(embed_texts([_QUERY_PREFIX + pergunta])[0])
    melhor, tema = 0.0, None
    for candidato in centroides:
        similaridade = _cosseno(vetor, candidato["centro"])
        if similaridade > melhor:
            melhor, tema = similaridade, candidato

    if melhor >= COBERTURA_ALTA:
        veredito = "coberto"
    elif melhor < COBERTURA_BAIXA:
        veredito = "lacuna"
    else:
        veredito = "ambiguo"

    return {
        "veredito": veredito,
        "similaridade": melhor,
        "tema": tema["membros"][:3] if tema else [],
    }


# --- estágio 2: ancoragem -----------------------------------------------


def dividir_afirmacoes(texto, minimo=40):
    """Frases com substância; heading, lista, fence e linha curta ficam fora."""
    corpo = re.sub(r"^---\n.*?\n---\n", "", texto, flags=re.S)
    corpo = re.sub(r"```.*?```", " ", corpo, flags=re.S)
    corpo = re.sub(r"\[\[([^\]]+)\]\]", r"\1", corpo)

    afirmacoes = []
    for linha in corpo.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith(("#", ">", "|", "-", "*")):
            continue
        for parte in re.split(r"(?<=[.!?])\s+", linha):
            parte = parte.strip()
            if len(parte) >= minimo:
                afirmacoes.append(parte)
    return afirmacoes


def dividir_contexto(texto, minimo=30, por_premissa=SENTENCAS_POR_PREMISSA):
    """Premissas por janela deslizante de sentenças, com sobreposição.

    A janela existe porque premissa de uma sentença não sustenta afirmação que
    sintetiza um parágrafo; a sobreposição existe para que a evidência não caia
    partida na fronteira entre duas janelas.
    """
    corpo = re.sub(r"```.*?```", " ", texto, flags=re.S)
    sentencas = [
        p.strip() for p in re.split(r"(?<=[.!?])\s+|\n{2,}", corpo) if len(p.strip()) >= minimo
    ]
    if por_premissa <= 1:
        return sentencas

    passo = max(1, por_premissa // 2)
    return [
        " ".join(sentencas[i:i + por_premissa])
        for i in range(0, max(1, len(sentencas) - passo + 1), passo)
    ]


def carregar_nli():
    """Cross-encoder de entailment. Multilíngue: o corpus é português."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizador = AutoTokenizer.from_pretrained(MODELO_NLI)
    modelo = AutoModelForSequenceClassification.from_pretrained(MODELO_NLI)
    modelo.eval()
    return tokenizador, modelo


def _julgar(nli, premissa, hipotese):
    import torch

    tokenizador, modelo = nli
    entrada = tokenizador(
        premissa, hipotese, return_tensors="pt", truncation=True, max_length=512
    )
    with torch.no_grad():
        probabilidades = modelo(**entrada).logits[0].softmax(-1).tolist()
    rotulos = [modelo.config.id2label[i].lower() for i in range(len(probabilidades))]
    return dict(zip(rotulos, probabilidades, strict=True))


def avaliar_ancoragem(texto_gerado, contexto, nli, lote=64):
    """Por afirmação: o contexto sustenta, contradiz ou nada diz?

    O cosseno seleciona as premissas candidatas — é o que ele sabe fazer — e o
    NLI julga cada par. Julgar toda afirmação contra toda sentença seria
    quadrático e desnecessário.
    """
    from kb.embeddings import _QUERY_PREFIX, embed_texts

    afirmacoes = dividir_afirmacoes(texto_gerado)
    sentencas = dividir_contexto(contexto)
    if not afirmacoes or not sentencas:
        return []

    def embutir(textos, prefixo=""):
        saida = []
        for i in range(0, len(textos), lote):
            saida += [
                _normaliza(v) for v in embed_texts([prefixo + t for t in textos[i:i + lote]])
            ]
        return saida

    vetores_afirmacao = embutir(afirmacoes, _QUERY_PREFIX)
    vetores_sentenca = embutir(sentencas)

    resultado = []
    for afirmacao, vetor in zip(afirmacoes, vetores_afirmacao, strict=True):
        ranking = sorted(
            zip(sentencas, (_cosseno(vetor, v) for v in vetores_sentenca), strict=True),
            key=lambda par: par[1],
            reverse=True,
        )[:PREMISSAS_POR_AFIRMACAO]

        melhor = {"entailment": 0.0, "contradiction": 0.0, "neutral": 1.0}
        evidencia = ""
        for premissa, _ in ranking:
            probabilidades = _julgar(nli, premissa, afirmacao)
            if probabilidades.get("entailment", 0) > melhor["entailment"]:
                melhor, evidencia = probabilidades, premissa

        contradiz = max(
            _julgar(nli, premissa, afirmacao).get("contradiction", 0)
            for premissa, _ in ranking
        )

        if melhor["entailment"] > max(melhor.get("contradiction", 0), melhor.get("neutral", 0)):
            veredito = "ancorada"
        elif contradiz > 0.5:
            veredito = "contradita"
        else:
            veredito = "sem apoio"

        resultado.append(
            {
                "afirmacao": afirmacao,
                "veredito": veredito,
                "entailment": melhor["entailment"],
                "contradicao": contradiz,
                "evidencia": evidencia[:160],
            }
        )
    return resultado


# --- estágio 3: consistência --------------------------------------------


def _gerar(mensagens, temperatura):
    """Geração com sampling explícito.

    Não reusa `kb.rerank._call_llm`: ele fixa o perfil `deterministic`
    (temperatura 0), e com temperatura 0 as N gerações são idênticas — a
    concordância dá 1,000 sempre e o estágio não mede nada. Foi exatamente o
    que aconteceu na primeira medição.
    """
    import os

    from openai import OpenAI

    cliente = OpenAI(
        api_key=os.getenv("KB_RERANK_API_KEY", "ollama"),
        base_url=os.getenv("KB_RERANK_BASE_URL", "http://localhost:8081/v1"),
    )
    resposta = cliente.chat.completions.create(
        model=os.getenv("KB_RERANK_MODEL", ""),
        messages=mensagens,
        temperature=temperatura,
        top_p=0.9,
    )
    return resposta.choices[0].message.content or ""


def avaliar_consistencia(pergunta, contexto, geracoes=3, temperatura=0.7):
    """As gerações concordam entre si?

    Verbalização — perguntar ao modelo se ele confia — foi medida e reprovada
    (83% de falso alarme). Consistência é a família que a literatura aponta
    como a que funciona: gerar N vezes e medir o quanto as respostas convergem.

    A hipótese é que sobre material que o acervo cobre o modelo converge, e
    sobre lacuna ele inventa coisas diferentes a cada vez. Exige temperatura
    acima de zero — senão não há o que divergir.
    """
    from kb.embeddings import embed_texts

    respostas = []
    for _ in range(geracoes):
        resposta = _gerar(
            [
                {
                    "role": "system",
                    "content": "Responda a pergunta usando apenas os trechos fornecidos. Seja breve.",
                },
                {"role": "user", "content": f"Pergunta: {pergunta}\n\nTrechos:\n{contexto}"},
            ],
            temperatura,
        )
        if resposta:
            respostas.append(resposta.strip())

    if len(respostas) < 2:
        return {"veredito": "indeterminado", "concordancia": 0.0, "geracoes": len(respostas)}

    vetores = [_normaliza(v) for v in embed_texts(respostas)]
    pares = [
        _cosseno(vetores[i], vetores[j])
        for i in range(len(vetores))
        for j in range(i + 1, len(vetores))
    ]
    concordancia = sum(pares) / len(pares)

    return {
        "veredito": "estavel" if concordancia >= 0.85 else "instavel",
        "concordancia": concordancia,
        "geracoes": len(respostas),
    }


# --- a pilha ------------------------------------------------------------


def verificar(pergunta, resposta, contexto, centroides, nli, usar_consistencia=True):
    """Roda a pilha inteira e devolve um veredito por estágio.

    A consistência só roda quando a cobertura ficou ambígua — é o estágio caro,
    e existe para desempatar, não para opinar sobre tudo.
    """
    cobertura = avaliar_cobertura(pergunta, centroides)
    ancoragem = avaliar_ancoragem(resposta, contexto, nli)

    consistencia = None
    if usar_consistencia and cobertura["veredito"] == "ambiguo":
        consistencia = avaliar_consistencia(pergunta, contexto)

    problemas = [a for a in ancoragem if a["veredito"] != "ancorada"]
    confiavel = (
        cobertura["veredito"] != "lacuna"
        and not problemas
        and (consistencia is None or consistencia["veredito"] == "estavel")
    )

    return {
        "confiavel": confiavel,
        "cobertura": cobertura,
        "ancoragem": {
            "total": len(ancoragem),
            "problemas": len(problemas),
            "detalhe": ancoragem,
        },
        "consistencia": consistencia,
    }
