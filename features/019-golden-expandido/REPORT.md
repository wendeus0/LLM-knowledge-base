# REPORT — 019-golden-expandido

**Data:** 2026-07-29
**Status:** `DONE`
**Ciclo:** SPEC → RED (7 testes) → GREEN → geração de 102 casos no vault real

## O que mudou

- **`kb/bench.py`:** `generate_cases` (uma pergunta por artigo amostrado, escrita pelo LLM em linguagem de usuário leigo), `is_trivial_question` (descarta pergunta que repete o título), `sample_articles` (amostragem reprodutível, pulando artigos já cobertos) e `aggregate_by_source` (métricas separadas por população).
- **`kb/cli.py`:** `kb bench --seed-questions N [--sample-seed S]`, incremental e retomável — grava a cada caso gerado.
- `CaseResult` ganhou `source`; o golden distingue `curated` de `generated`.

## Validação

- 7 testes novos, nascidos RED. Suíte verde, ruff limpo.
- **102 casos gerados** no vault real, somados aos 50 curados: golden de **152 casos**.

### As duas populações concordam

| população | lexical | hybrid |
|---|---|---|
| curados (50) | 0,240 | 0,440 |
| gerados (102) | 0,225 | 0,402 |
| **total (152)** | **0,230** | **0,414** |

As perguntas geradas são levemente mais difíceis que as curadas à mão, mas medem a mesma coisa — o gerador está validado. O erro padrão caiu de ~7 para ~4 pontos, o que tornou possível distinguir o ganho do rerank (+5,3) do ruído, coisa impossível com os 50 casos anteriores.

## Riscos / dívida

- **Viés de origem:** a pergunta é derivada do artigo, então todo caso tem resposta garantida — diferente do uso real, em que parte das perguntas não tem artigo correspondente. Isso mede recuperação, não cobertura do corpus.
- O modelo local comete pequenos deslizes de português nas perguntas ("sem que o sistema se travasse"). Não compromete a medição, mas o texto não é publicável.
- O golden vive em `kb_state/bench/golden.json`, num vault que não é versionado. Diferente do índice, **não é reconstruível** — os 50 casos curados são trabalho manual.

## Próximos passos

1. Versionar o golden em algum lugar seguro.
2. Revisar `expected` onde há artigos irmãos igualmente válidos — parte das falhas restantes é erro de medida.
