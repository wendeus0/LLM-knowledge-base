# PLAN — QA: verificação de ancoragem por afirmação

**Branch:** `proto/answer-verification` (existente; não criar outra)
**Data:** 2026-08-01
**Spec:** `features/023-claim-grounding/SPEC.md`
**MVP scope:** critérios [P1] da SPEC

## Contexto técnico

| Campo | Valor |
|---|---|
| Linguagem/versão | Python 3.11+ |
| Dependências principais | Typer, Rich, OpenAI SDK opcional; `urllib` da stdlib para o novo cliente HTTP |
| Storage | `outputs/` para file-back; sem escrita nova em `kb_state/` |
| Estratégia de testes | `test-design`, com `test-red` como base, mocks de geração/embeddings/NLI e integração pela CLI |
| Plataforma alvo | CLI local; serviço NLI somente em loopback |
| Tipo de projeto | Engine de knowledge base, corpus externo em `KB_DATA_DIR` |
| Constraints | Não adicionar torch/transformers ao pacote base; resposta nunca é bloqueada; máximo padrão de 24 inferências NLI por resposta |

## Arquitetura escolhida

Um módulo novo, `kb/grounding.py`, recebe a resposta já gerada e o `full_context` que `kb.qa.answer()` enviou ao LLM. Ele extrai afirmações elegíveis, divide o contexto em janelas de 12 sentenças com passo seis, obtém embeddings para selecionar as três melhores premissas por afirmação e pede ao serviço NLI o julgamento dos pares. O resultado é um objeto estruturado interno que preserva contagens, evidência curta, probabilidades, estado (`verified`, `skipped` ou `degraded`) e itens omitidos por orçamento.

```text
router.build_context() → kb.qa monta full_context → client.chat() → resposta
                                                          ↓
                                kb.grounding.verify(response, full_context)
                                  ├─ embeddings: top 3 premissas/afirmação
                                  └─ HTTP NLI local: entailment/contradiction/neutral
                                                          ↓
                 QA result estruturado → CLI humano | --json | file-back anotado
```

`kb.qa` deixa de transportar somente uma string internamente: uma estrutura de resultado contém a resposta e a anotação de grounding. Adaptadores preservam a compatibilidade dos chamadores atuais que esperam o texto da resposta. `answer_and_file()` acrescenta a anotação ao artigo antes de escrevê-lo; não cria estado paralelo.

O módulo verifica no máximo `floor(KB_GROUNDING_MAX_PAIRS / 3)` afirmações, com default `24`, isto é, oito. O contador é de inferências de pares, mesmo que o cliente envie vários pares em uma só requisição HTTP. Afirmações posteriores não recebem veredito; entram em `unverified_due_to_limit` para não confundir custo interrompido com falta de apoio.

## Contrato do serviço NLI local

O serviço é um processo separado, limitado a `127.0.0.1`, por padrão `http://localhost:1235/v1`. Ele carrega `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` com torch/transformers fora do ambiente normal de `kb`.

| Operação | Request | Response exigida |
|---|---|---|
| Probe | `GET /v1/models` | `data[].id`, incluindo o modelo configurado |
| Classificar | `POST /v1/nli` com `{model, pairs:[{premise,hypothesis}]}` | `{data:[{entailment, contradiction, neutral}]}` na mesma ordem dos pares |

`KB_GROUNDING_BASE_URL`, `KB_GROUNDING_MODEL`, `KB_GROUNDING_API_KEY`, `KB_GROUNDING_TIMEOUT` e `KB_GROUNDING_MAX_PAIRS` governam o cliente. Falha no probe ou na classificação vira `GroundingUnavailable`; o adaptador de QA captura-a, emite uma vez `aviso: verificação de ancoragem indisponível (...) — resposta exibida sem verificação` em stderr e continua.

## Decisões técnicas

1. **Decisão:** serviço HTTP NLI local separado, não `kb[grounding]` nem ONNX. **Motivo:** `torch` + `transformers` e pesos (~2 GB) não entram no caminho de instalação/memória de todo usuário. O projeto já isola embeddings atrás de servidor local HTTP, com probe e degradação. ONNX exigiria conversão e validação próprias, sem evidência de ganho para este modelo.
2. **Decisão:** cosseno seleciona, NLI julga. **Motivo:** embeddings encontram premissas candidatas; NLI mede entailment de premissa para hipótese. O caso “NÃO abre” teve cosseno 0,786 e contradição 0,998, portanto similaridade não decide o veredito.
3. **Decisão:** janelas de 12 sentenças, passo seis, três candidatas. **Motivo:** é o platô medido: 72% de preservação e entailment mediano 0,755; uma sentença caiu para 18% e 0,067. Três pares por afirmação limitam custo sem julgamento quadrático.
4. **Decisão:** anotação não bloqueante, visível em todas as superfícies. **Motivo:** a preservação de 72% ainda produz 28% de falso alarme. O valor imediato é transparência para revisão, não um gate que silencie respostas legítimas.
5. **Decisão:** CLI humano recebe bloco por afirmação; `--json` recebe o objeto completo e exclusivo; file-back persiste a seção Markdown equivalente. **Motivo:** humano precisa ler o aviso perto da resposta, automação precisa schema estável, e a anotação precisa sobreviver no artefato que será relido. Em `--json`, progresso e avisos vão para stderr para não contaminar stdout.
6. **Decisão:** ao ultrapassar 24 pares, parar no limite e declarar omissão. **Motivo:** uma resposta com N afirmações custa `3N` julgamentos; ocultar o teto criaria latência/custo imprevisível, enquanto chamar omissão de `sem apoio` seria semanticamente falso.
7. **Decisão:** degradação uma vez por execução, em stderr. **Motivo:** segue `kb.search._warn_semantic_degraded`; o NLI é observabilidade adicional, não pré-requisito da resposta.

## Módulos e pontos de integração

| Arquivo | Mudança planejada |
|---|---|
| `kb/grounding.py` | Novo: segmentação, janelas, embeddings/cosseno, cliente/probe NLI, normalização do payload, orçamento e objeto de resultado. |
| `kb/config.py` | Resolução e validação leve das variáveis `KB_GROUNDING_*`. |
| `kb/qa.py` | Após `chat()`, chamar a verificação com a resposta e `full_context`; preservar a resposta em falhas; adicionar anotação no file-back. |
| `kb/cmds/qa/run.py` | Propagar flags e devolver resultado estruturado sem acoplar Typer ao domínio. |
| `kb/cli.py` | Adicionar `--no-grounding` e `--json`; renderizar bloco humano ou serializar o contrato JSON sem logs em stdout. |
| `docs/` | Instrução de provisionamento do serviço local, variáveis e contrato `/v1/nli`; não instalar dependência pesada no projeto. |
| `tests/unit/test_grounding.py` | Casos puros e fronteira HTTP simulada. |
| `tests/integration/test_qa_grounding_cli.py` | Fluxos de CLI, JSON, file-back, teto e degradação, com rede simulada. |

## Saída e compatibilidade

No modo normal a resposta mantém o texto atual e ganha, depois dela, `## Verificação de ancoragem` com uma linha por afirmação. Vereditos negativos usam aviso, nunca modificam a prosa. O file-back contém `## Verificação de ancoragem da resposta`; essa seção declara que verifica a resposta de QA antes da expansão editorial usada pelo formato atual de file-back.

No modo JSON, a forma mínima estável é:

```json
{
  "answer": "...",
  "grounding": {
    "status": "verified|skipped|degraded",
    "checked_claims": 0,
    "unverified_due_to_limit": 0,
    "claims": [
      {"claim": "...", "verdict": "ancorada|contradita|sem apoio", "evidence": "...", "scores": {"entailment": 0.0, "contradiction": 0.0, "neutral": 0.0}}
    ]
  },
  "saved_path": null
}
```

## Condições binárias de risco

| Condição | Marca | Por quê |
|---|---|---|
| Endpoint HTTP público | não | O serviço deve bindar somente em loopback; não há API exposta fora da máquina. |
| I/O em DB real / migration / query não-trivial | não | A feature não cria persistência em banco nem altera `kb_state/`; file-back é a escrita Markdown já existente. |
| UI com estado interativo | não | A superfície é CLI linear, sem estado de UI. |
| Output estrutural estável | **sim** | `--json` introduz schema público parseável e o file-back ganha seção Markdown com estrutura persistida. |
| Contrato HTTP entre serviços | **sim** | O cliente `kb` depende do contrato local `GET /v1/models` e `POST /v1/nli`. |
| Contrato frontend↔backend | não | Não há frontend. |
| Fluxo E2E multi-página/browser real | não | Não há browser. |

Com duas condições marcadas, o fluxo de TDD é **`test-design`**, que inclui `test-red` como camada base; os testes de contrato HTTP e de saída JSON são obrigatórios antes do GREEN.

## Success metric

```yaml
success_metric:
  name: "cobertura de verificação e sinalização de deriva no conjunto manual"
  target: "máximo de 24 pares por resposta; evidência reproduzível de 5/6 derivas sutis e 12/12 fabricações"
  observable_at: "relatório manual da feature e testes de integração da CLI"
  measure_window: "execução de validação antes de aprovar a feature"
  baseline: "72% de preservação; 5/6 derivas; 12/12 fabricações no protótipo"
```

## Constitution check

O plano respeita a separação engine/corpus: pesos e runtime pesados ficam no serviço local, e a engine não persiste um novo estado do usuário. Ele segue o padrão de degradação explícita em stderr de `search.py` e não modifica `wiki/` manualmente. Não introduz detecção de lacuna, alinhado ao ADR-0018. O contrato HTTP e a saída JSON requerem `test-design`; nenhum `CONTRACT.md` é criado nesta etapa, pois é gate posterior do orquestrador e está fora do escopo solicitado.

## Dependências entre componentes

1. A especificação documentada do serviço e a resolução de configuração habilitam o cliente HTTP testável.
2. O cliente e a seleção de premissas habilitam a verificação pura por afirmação e o teto de custo.
3. O resultado estruturado habilita a integração em `kb.qa` sem reexecutar retrieval ou geração.
4. A integração em QA habilita os três adaptadores de apresentação: CLI humano, JSON e file-back.
5. A validação manual contra o servidor real só ocorre após os testes isolados, pois a suíte não pode fazer chamadas de rede reais.

## Limitações e riscos residuais

- Os limiares foram ajustados nos próprios dados de avaliação; não existe conjunto de validação separado.
- A medição usou somente oito pares artigo↔fonte, quase todos no domínio IA/LLM, e conjuntos negativos pequenos.
- A anotação no file-back avalia a resposta original, não cada possível afirmação adicionada pela expansão editorial posterior; a revisão desse fluxo é trabalho futuro.
- Disponibilidade do serviço e a latência do modelo são dependências operacionais. A degradação protege o QA, mas reduz transparência naquela execução.
