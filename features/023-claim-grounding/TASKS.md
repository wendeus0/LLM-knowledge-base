# TASKS — 023-claim-grounding

**Spec:** `features/023-claim-grounding/SPEC.md`
**Plan:** `features/023-claim-grounding/PLAN.md`
**MVP:** tasks `priority: P1` completas com `state: passing`

## Fase 1 — Setup

```yaml
- id: T-001
  priority: P1
  parallel: false
  depends_on: []
  ac_ref: AC-01
  tag: AFK
  vertical_slice: spike
  behavior: "O cliente consegue provar, com HTTP simulado, que o serviço local anuncia o modelo NLI e respeita o contrato de classificação."
  verify: "python -m pytest tests/unit/test_grounding.py -k 'probe or httpcontract'"
  state: passing
  worktree: worktrees/023-claim-grounding/T-001
```

Definir e documentar o contrato `GET /v1/models` e `POST /v1/nli`, as variáveis `KB_GROUNDING_*` e a fronteira HTTP simulável, sem adicionar torch ou transformers ao pacote base.

## Fase 2 — Foundational (P1)

```yaml
- id: T-002
  priority: P1
  parallel: false
  depends_on: [T-001]
  ac_ref: AC-01
  tag: AFK
  vertical_slice: yes
  behavior: "Cada afirmação elegível recebe ancorada, contradita ou sem apoio a partir de três premissas de 12 sentenças sobrepostas."
  verify: "python -m pytest tests/unit/test_grounding.py -k 'windows or verdict or negation'"
  state: not_started
  worktree: worktrees/023-claim-grounding/T-002
```

Implementar a fatia domínio+teste: extração de afirmações, janelas, seleção por cosseno e decisão NLI. O teste de negação impede que cosseno seja usado como veredito.

```yaml
- id: T-003
  priority: P1
  parallel: false
  depends_on: [T-002]
  ac_ref: AC-02
  tag: AFK
  vertical_slice: yes
  behavior: "Uma resposta longa executa no máximo 24 julgamentos de pares e declara as afirmações que não couberam no orçamento."
  verify: "python -m pytest tests/unit/test_grounding.py -k 'budget or limit'"
  state: not_started
  worktree: worktrees/023-claim-grounding/T-003
```

Acrescentar orçamento configurável, arredondamento por grupos de três e metadados de omissão, sem confundir omissão com `sem apoio`.

```yaml
- id: T-004
  priority: P1
  parallel: false
  depends_on: [T-003]
  ac_ref: AC-03
  tag: AFK
  vertical_slice: yes
  behavior: "Falha ou resposta inválida do NLI preserva a resposta de QA e emite um único aviso em stderr."
  verify: "python -m pytest tests/unit/test_grounding.py tests/unit/test_qa.py -k 'grounding and degraded'"
  state: not_started
  worktree: worktrees/023-claim-grounding/T-004
```

Integrar o resultado em `kb.qa` com degradação não bloqueante e testar timeout, modelo ausente e payload inválido sem rede real.

## Fase 3 — User stories (P1 → P2 → P3)

```yaml
- id: T-005
  priority: P1
  parallel: false
  depends_on: [T-004]
  ac_ref: AC-04
  tag: AFK
  vertical_slice: yes
  behavior: "O usuário vê os vereditos no terminal, recebe JSON parseável com --json e encontra a anotação no file-back."
  verify: "python -m pytest tests/integration/test_qa_grounding_cli.py -k 'human or json or file_back'"
  state: not_started
  worktree: worktrees/023-claim-grounding/T-005
```

Conectar o resultado de QA aos três adaptadores de saída, mantendo stdout exclusivo para JSON e movendo progresso/avisos para stderr nesse modo.

```yaml
- id: T-006
  priority: P2
  parallel: true
  depends_on: [T-004]
  ac_ref: AC-05
  tag: AFK
  vertical_slice: yes
  behavior: "Vereditos negativos permanecem avisos e --no-grounding preserva o QA sem chamar o serviço NLI."
  verify: "python -m pytest tests/integration/test_qa_grounding_cli.py -k 'nonblocking or no_grounding'"
  state: not_started
  worktree: worktrees/023-claim-grounding/T-006
```

Fechar a compatibilidade observável: nenhuma anotação negativa bloqueia resposta ou file-back; a opção de custo zero não toca a fronteira HTTP.

## Fase 4 — Polish

```yaml
- id: T-007
  priority: P2
  parallel: false
  depends_on: [T-005, T-006]
  ac_ref: "Métricas de sucesso"
  tag: HITL
  vertical_slice: yes
  behavior: "A validação manual no servidor local registra os resultados de deriva sutil, fabricação, preservação e latência sem transformar a medição em bloqueio."
  verify: "python -m pytest tests/unit/test_grounding.py tests/integration/test_qa_grounding_cli.py && ruff check kb tests"
  state: not_started
```

Executar a amostra medida com o modelo real em ambiente local, comparar com a linha de base do protótipo e registrar limites/latência para a aprovação humana.

---

## Matriz de dependências

| Task | Depende de | Pode ser paralela com |
|---|---|---|
| T-001 | — | — |
| T-002 | T-001 | — |
| T-003 | T-002 | — |
| T-004 | T-003 | — |
| T-005 | T-004 | T-006 |
| T-006 | T-004 | T-005 |
| T-007 | T-005, T-006 | — |
| T-008 | T-004 | — |

## Fase 6 — Compatibilidade dos chamadores (P1)

```yaml
- id: T-008
  priority: P1
  parallel: false
  depends_on: [T-004]
  ac_ref: AC-01
  tag: AFK
  vertical_slice: no
  behavior: "Os chamadores atuais de kb.qa.answer() continuam recebendo o texto da resposta, e a suíte existente passa sem edição de asserção."
  verify: "python -m pytest tests/unit/test_qa_rerank.py tests/unit/test_qa_claims.py tests/unit/test_qa_cmds.py tests/unit/test_untrusted_prompt_boundary.py tests/unit/test_sensitive_execution_controls.py -q"
  state: not_started
  worktree: worktrees/023-claim-grounding/T-008
```

O PLAN prevê que `answer()` passe a devolver estrutura em vez de string, com adaptadores preservando os chamadores. Cinco arquivos de teste dependem do contrato atual (`test_qa_rerank`, `test_qa_claims`, `test_qa_cmds`, `test_untrusted_prompt_boundary`, `test_sensitive_execution_controls`), além de `kb/qa.py:141` e `kb/cmds/qa/run.py:27,42`. Sem task própria, a promessa de compatibilidade fica só na prosa do PLAN — e é assim que ela quebra.

Se a compatibilidade exigir alterar asserção de teste existente, isso é sinal de que o adaptador não está preservando o contrato: corrigir o adaptador, não o teste.

## Definition of Done

Uma task com `state: passing` significa:
1. `verify` rodou e passou.
2. Código revisado quando `tag: HITL`.
3. Critério de aceite (`ac_ref`) demonstrado.

MVP completo quando: todas as tasks `priority: P1` têm `state: passing` e o ciclo `test-design` conclui seus gates, incluindo o `RED_OK` de `test-red`.

## Loop autônomo

Tasks com `tag: AFK`, `state: not_started` e sem `depends_on` pendente são elegíveis para execução autônoma no worktree indicado. `T-007` é `HITL` porque exige interpretar uma medição feita contra o modelo e serviço reais.
