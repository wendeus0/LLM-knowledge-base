# Protótipo — pilha de verificação de resposta

> Throwaway, fora de `kb/`. Existe para responder *"esta arquitetura funciona?"* antes de virar feature com SPEC. Dois estágios confirmados, um não.

## A ideia

Três modelos pequenos, três perguntas diferentes, cada um cobrindo o ponto cego do outro.

| Estágio | Pergunta | Modelo | Ponto cego |
|---|---|---|---|
| **1 — cobertura** | o acervo tem material? | embedding (nomic, `:1234`) | não vê negação |
| **2 — ancoragem** | a afirmação decorre do contexto? | cosseno **seleciona** + NLI **julga** | não vê ausência |
| **3 — consistência** | as gerações concordam? | gerador (`:8081`), N vezes | não separou nada |

O estágio 1 roda antes de responder; o 2 depois; o 3 só desempataria a faixa ambígua do 1.

## Resultados

### Estágio 1 — cobertura: **funciona**

| Conjunto | coberto | ambíguo | lacuna | mediana |
|---|---:|---:|---:|---:|
| golden (152, tem resposta) | 97 | 43 | 12 | 0,492 |
| lacuna distante (8) | **0** | 0 | **8** | 0,253 |
| lacuna adjacente (8) | 1 | 3 | 4 | 0,361 |

Nenhuma lacuna distante declarada como coberta. Uma de 8 adjacentes escapou.

O centroide do tema é o que faz funcionar: comparar com o **artigo mais próximo** dá 100% de detecção mas só 67% de preservação, porque o vizinho pode ser acidental — pergunta sobre parser recursivo trouxe "árvore binária de busca" a 0,53. Contra o centroide, cai para 0,39.

### Estágio 2 — ancoragem: **funciona, e o parâmetro que decide é o tamanho da premissa**

| Deriva sutil (negação, número trocado, inversão) | 5/6 |
| Fabricações injetadas | **12/12 (100%)** |

O NLI é categórico onde o cosseno é cego: *"o circuit breaker **NÃO** abre após falhas"* tem cosseno **0,786** — passaria como ancorada — e contradição **0,998** no NLI.

**O parâmetro crítico é quantas sentenças formam uma premissa**, e errar nele custa mais que trocar de modelo:

| Sentenças por premissa | Legítimas ancoradas | Fabricadas detectadas |
|---:|---:|---:|
| 1 | 18% | — |
| 4 | 49% | 100% |
| 6 | 56% | 100% |
| **12** | **72%** | **100%** |
| 16 | 70% | 100% |

Uma afirmação de artigo sintetiza um parágrafo da fonte; julgada contra **uma** sentença, o veredito correto é `neutral`. Com premissa de 1 sentença a mediana de entailment é 0,067; com 12, é 0,755.

A detecção não cede em nenhuma faixa — afirmação inventada é estranha ao contexto inteiro, não só à sentença vizinha.

### Estágio 3 — consistência: **sem sinal**

| | Veredito | Concordância |
|---|---|---:|
| TEM — circuit breaker | estável | 1,000 |
| **TEM — prática espaçada** | **instável** | **0,636** |
| NÃO — TLS handshake | instável | **0,707** |
| NÃO — diafragma | instável | 0,637 |

A ordenação está invertida no par que importa: pergunta com resposta teve concordância **menor** que uma lacuna.

**Duas armadilhas atravessadas até chegar a este número**, e ambas eram erro de medição, não da técnica:

1. A primeira rodada deu **1,000 nos quatro casos** porque reusei `kb.rerank._call_llm`, que fixa o perfil `deterministic` — temperatura 0 gera N respostas idênticas e a concordância é trivialmente perfeita. Corrigido com geração própria a 0,7.
2. A concordância é medida por cosseno entre respostas inteiras, o que é grosseiro. Concordância por NLI (as gerações se implicam?) seria mais fina e não foi testada.

Com 4 perguntas não dá para cravar que a consistência não serve — dá para dizer que **não apareceu sinal**, e que é o estágio mais caro (24–38s contra milissegundos dos outros).

## Como rodar

O NLI exige `torch` e `transformers`, que **não estão no venv do projeto** de propósito — são dependência de protótipo, não do `kb`.

```bash
python3 -m venv /tmp/venv-nli
/tmp/venv-nli/bin/pip install torch transformers sentencepiece protobuf openai python-dotenv typer rich pyyaml

/tmp/venv-nli/bin/python prototypes/answer-verification/medir.py 1,2   # rápido
/tmp/venv-nli/bin/python prototypes/answer-verification/medir.py 3     # lento
/tmp/venv-nli/bin/python prototypes/answer-verification/medir.py todos
```

Requer os servidores locais em `:1234` (embeddings) e `:8081` (gerador, só para o estágio 3), e o vault em `KB_DATA_DIR`. Somente leitura do corpus.

## Limitações

- **Só 8 pares artigo↔fonte.** A proveniência não existe (`manifest.json` nunca materializado); o casamento é pelo campo `source` do frontmatter contra `wiki/_sources/`, e quase todos os pares caem no domínio IA/LLM.
- **Todos os limiares foram ajustados nos dados de avaliação.** Não há conjunto de validação separado — os números são teto otimista.
- **Os conjuntos negativos são pequenos:** 8 lacunas distantes, 8 adjacentes, 4 perguntas no estágio 3.
- **As fabricações são fáceis.** Frases deliberadamente estranhas ao contexto. Deriva sutil está coberta pelos 6 pares de negação/inversão, mas é amostra mínima.
- **72% de preservação ainda é 28% de falso alarme.** Bom o suficiente para decidir a arquitetura, não para ligar em produção sem calibrar melhor.

## Se virar feature

Precisa de SPEC (regra 2 do `AGENTS.md`). O que a medição já entrega para ela:

- os dois estágios que valem, e o que cada um mede;
- o tamanho de premissa (12 sentenças) e a faixa de cobertura (0,36 / 0,46), com a curva que os justifica;
- a decisão de composição — o cosseno seleciona, o NLI julga, e trocar um pelo outro é erro de arquitetura;
- o estágio 3 como não-confirmado, com o caminho anotado (amostra maior, concordância por NLI).

Contexto e medições anteriores em `docs/research/2026-07-30-politica-de-corpus/ESTUDO-DETECCAO-DE-LACUNA.md` e `ESTADO-DA-ARTE-GROUNDING.md`.
