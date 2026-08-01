# REPORT — 023-claim-grounding

**Branch:** `feat/023-claim-grounding`
**Data:** 2026-08-01
**Estado:** `DONE_WITH_CONCERNS`

## Contexto

`kb qa` respondia sem indicar quais afirmações decorriam do contexto recuperado. Esta feature acrescenta, depois da geração, uma verificação por afirmação com três vereditos — `ancorada`, `contradita`, `sem apoio` — que **nunca bloqueia a resposta**.

O trabalho saiu de um protótipo medido (PR #60). O que ele estabeleceu e esta feature implementa: **o cosseno seleciona a premissa, o NLI julga**. Trocar os papéis é erro de arquitetura — o caso didático é "o circuit breaker NÃO abre", com cosseno 0,786 (passaria como ancorada) e contradição NLI 0,998.

## Mudanças

| Arquivo | O quê |
|---|---|
| `kb/grounding.py` | Novo. Contrato HTTP do serviço NLI, janelas deslizantes, seleção por cosseno, mapeamento de vereditos, orçamento |
| `kb/config.py` | Cinco variáveis `KB_GROUNDING_*` com resolução e validação |
| `kb/qa.py` | `answer_with_grounding()` estruturado; `answer()` preservado; seção no file-back |
| `kb/cmds/qa/run.py`, `kb/cli.py` | Flags `--json` e `--no-grounding`; três adaptadores de saída |
| `tests/unit/test_grounding.py` | 60 testes: contrato HTTP, janelas, vereditos, orçamento, negação |
| `tests/integration/test_qa_grounding_cli.py` | 14 testes: humano, JSON, file-back, não-bloqueio, `--no-grounding` |

**Decisão que diverge do PLAN, para melhor:** o PLAN previa `answer()` mudando de tipo com adaptadores preservando os chamadores. Em vez disso, `answer_with_grounding()` devolve a estrutura e `answer()` delega a ela devolvendo `str`. A compatibilidade passa a ser **por construção**, não por adaptador — os 32 testes dos cinco arquivos dependentes passam sem uma linha alterada.

## Validação

| Gate | Resultado |
|---|---|
| Suíte | **819 passed** (era 739 antes da feature) |
| `ruff check kb tests` | limpo |
| Cobertura | `kb/grounding.py` 94%, `kb/qa.py` 100% |
| T-008 (compatibilidade) | 32 passed nos cinco arquivos dependentes |
| Smoke real da CLI | `--json` parseável com o schema do PLAN; modo humano com veredito negativo sai em exit 0 |

**Conteúdo sensível não escapa pelo canal novo.** `assert_safe_for_provider` roda em `kb/qa.py:126`, antes de `grounding.verify` em `:163`. O que chega ao serviço NLI já passou pelo gate — diferente dos canais de embedding e rerank, onde o achado F-03 do `PENDING_LOG` continua aberto.

**Guard de loopback.** A RT-02 diz que o serviço é local. `_is_loopback` faz o cliente recusar `base_url` fora de loopback, em `probe` e em `classify`. Sem isso, `KB_GROUNDING_BASE_URL` apontando para fora vazaria a api key (no `probe`, que manda `Authorization`) e trecho de artigo (no `classify`).

## O que o review pegou

Três defeitos corrigidos com teste antes da correção:

1. **Seleção por produto escalar em vez de cosseno.** Sem normalizar, uma janela de vetor grande e direção errada vence uma janela alinhada. O teste constrói o caso: `delta` tem produto 5,0 e cosseno 0,447; `alfa` tem produto 1,0 e cosseno 1,0.
2. **Evidência incoerente com o veredito.** A evidência era sempre a candidata de maior entailment, inclusive em `contradita` — o usuário veria o rótulo negativo ao lado de pontuações mostrando entailment alto.
3. **Bloco humano vazio.** O cabeçalho "Verificação de ancoragem" era impresso mesmo sem afirmação alguma; resposta sem contexto ou serviço degradado exibia seção vazia. Pego pelo smoke da CLI, não pelos testes.

## Riscos e dívida

| Item | Estado |
|---|---|
| **Falso alarme de 28%, parte como contradição confiante** | `EVALS.md` E-SIN-001: síntese fiel recebeu contradição 0,953. Mitigado por anotação não-bloqueante e por evidência coerente com o veredito |
| **Comparação numérica não é detectada** | E-CMP-001: 70% vs 72% dá contradição 0,377, abaixo do corte. O NLI não faz aritmética. Declarado no CONTRACT |
| **Holdout com zero pares** | `EVAL_DESIGN_PARTIAL`. Todos os limiares foram ajustados nos dados de avaliação; os números são teto otimista. Mínimo viável: 12 pares novos congelados |
| **T-007 bloqueada** | Validação manual exige o serviço NLI em `:1235`, que a SPEC coloca fora do pacote. É P2; o MVP são as P1, todas `passing` |
| **`verify` chama `classify` uma vez por afirmação** | Até 8 requisições de 3 pares em vez de 1 de 24. Permitido pela RT-03; é round-trip a loopback |

## Próximos passos

1. Provisionar o serviço NLI em `:1235` e destravar a T-007.
2. Coletar os 12 pares mínimos do holdout e congelá-los antes de qualquer recalibração.
3. Estágio 1 (cobertura por centroide de tema) espera o reagrupamento do ticket 006.
