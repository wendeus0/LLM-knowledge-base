# TASKS — Plataforma de estudos web

**Spec:** `features/026-plataforma-de-estudos/SPEC.md`
**Plan:** `features/026-plataforma-de-estudos/PLAN.md`
**Entrega real desta branch:** F0 como gate, F1–F2 (`T-001` a `T-010`) e também F3–F5 (`T-011` a `T-013`), todas com `state: passing`. O corte original previa F3–F5 para depois; elas entraram na mesma branch assim que o leitor foi validado (ver `REPORT.md`). `T-009` e `T-010` são `HITL`: o `verify` cobre o que é automatizável e a aparência foi validada em tela renderizada, com a evidência registrada no `REPORT.md`.

## Fase 1 — Setup

```yaml
- id: T-001
  priority: P1
  parallel: false
  depends_on: []
  ac_ref: AC-05
  tag: AFK
  vertical_slice: spike
  behavior: "A identidade rel_slug e a resolução determinística de wikilinks, inclusive stems duplicados, estão provadas antes de expor URLs do leitor."
  verify: "python -m pytest tests/unit/test_article_identity.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-001
```

F0 já possui testes na branch; esta task é o gate de regressão. Se falhar, a correção de identidade precede qualquer rota ou template.

```yaml
- id: T-002
  priority: P1
  parallel: false
  depends_on: [T-001]
  ac_ref: AC-01
  tag: AFK
  vertical_slice: spike
  behavior: "A aplicação FastAPI inicia em loopback e health responde sucesso sem serializar configuração nem paths locais."
  verify: "python -m pytest tests/integration/test_api_health.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-002
```

Criar a fundação mínima de `kb/api/`, schemas serializáveis e fixtures que isolam wiki, `kb_state` e banco futuro.

## Fase 2 — Foundational (P1)

```yaml
- id: T-003
  priority: P1
  parallel: false
  depends_on: [T-002]
  ac_ref: AC-01, AC-04
  tag: AFK
  vertical_slice: yes
  behavior: "GET /article/{slug:path} devolve artigo e metadados por rel_slug, rejeita traversal com 400 e responde 404 sem vazar Path."
  verify: "python -m pytest tests/integration/test_api_article.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-003
```

Esta fatia inclui validação de slug, adaptação segura do artigo e teste de serialização sem `Path`.

```yaml
- id: T-004
  priority: P1
  parallel: true
  depends_on: [T-002]
  ac_ref: AC-01, AC-02
  tag: AFK
  vertical_slice: yes
  behavior: "GET /search preserva a ordenação da busca híbrida e do rerank da engine e identifica cada resultado por rel_slug."
  verify: "python -m pytest tests/integration/test_api_search.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-004
```

O teste compara API e engine com a mesma consulta/configuração, sem criar canal de busca alternativo.

```yaml
- id: T-005
  priority: P1
  parallel: true
  depends_on: [T-002]
  ac_ref: AC-03, AC-04
  tag: AFK
  vertical_slice: yes
  behavior: "POST /qa devolve literalmente o schema de kb qa --json com saved_path nulo e converte conteúdo sensível em HTTP 409 sem prompt."
  verify: "python -m pytest tests/integration/test_api_qa.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-005
```

O contrato de resposta é comparado campo a campo, incluindo grounding, e a fronteira de guardrail é exercitada offline.

```yaml
- id: T-006
  priority: P1
  parallel: true
  depends_on: [T-002]
  ac_ref: AC-01
  tag: AFK
  vertical_slice: yes
  behavior: "GET /stats devolve somente métricas agregadas que a engine já expõe e não altera corpus ou estado."
  verify: "python -m pytest tests/integration/test_api_stats.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-006
```

## Fase 3 — User stories (P1)

```yaml
- id: T-007
  priority: P1
  parallel: false
  depends_on: [T-003]
  ac_ref: AC-05
  tag: AFK
  vertical_slice: yes
  behavior: "O renderer do leitor transforma Markdown e wikilinks qualificados para URLs por rel_slug, expõe backlinks e não escolhe destino para stem ambíguo."
  verify: "python -m pytest tests/unit/test_study_render.py tests/integration/test_study_article.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-007
```

O cliente de `study/` consulta `kb/api/` por HTTP; templates não importam `kb.search`, `kb.graph` ou `kb.qa` diretamente.

```yaml
- id: T-008
  priority: P1
  parallel: true
  depends_on: [T-004, T-005]
  ac_ref: RF-08
  tag: AFK
  vertical_slice: yes
  behavior: "As caixas do leitor exibem resultados de busca e resposta de QA da API, incluindo o estado e os avisos de grounding."
  verify: "python -m pytest tests/integration/test_study_queries.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-008
```

```yaml
- id: T-009
  priority: P1
  parallel: false
  depends_on: [T-007]
  ac_ref: AC-09
  tag: HITL
  vertical_slice: yes
  behavior: "Em tela larga, a página renderizada mostra sidebar de trilha e progresso à esquerda, artigo à direita e temas claro bege e escuro com acento laranja."
  verify: "python -m pytest tests/integration/test_study_article.py -q"
  state: passing
```

Antes do GREEN visual, executar `visual-direction` para fixar tokens; a task só passa após revisão humana de screenshot/URL renderizada, além do comando de teste. A parte automatizável é a estrutura da página (`test_study_article.py`); a aparência foi medida na tela e está registrada em `REPORT.md` (bege `rgb(239,231,218)` no claro, `rgb(25,23,21)` no escuro, sem flash de tema).

```yaml
- id: T-010
  priority: P1
  parallel: false
  depends_on: [T-008, T-009]
  ac_ref: AC-01, AC-05, AC-09
  tag: HITL
  vertical_slice: yes
  behavior: "O fluxo browser artigo → wikilink/backlink → busca ou pergunta preserva identidade, grounding e a superfície de leitura nos dois temas."
  verify: "python -m pytest tests/integration/test_study_article.py tests/integration/test_study_queries.py -q"
  state: passing
```

O checkpoint HITL exige evidência de browser real: aparência não é provada por leitura de template ou componente. O `verify` cobre identidade do wikilink/backlink e a preservação do grounding nos fragmentos de busca e pergunta; a leitura nos dois temas foi validada na tela e registrada em `REPORT.md`. Não existe suíte de browser automatizada nesta feature.

## Fase 4 — Polish

```yaml
- id: T-011
  priority: P1
  parallel: false
  depends_on: [T-010]
  ac_ref: AC-06
  tag: AFK
  vertical_slice: yes
  delivery: nesta entrega
  behavior: "Uma nota e um destaque ligados por rel_slug reaparecem no artigo sem modificar o Markdown compilado; âncora perdida vira orphaned preservado."
  verify: "python -m pytest tests/integration/test_study_annotations.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-011
```

F3 estava prevista para depois do MVP F1+F2 e acabou entrando na mesma branch. Esta fatia introduz o SQLite de estudo no padrão `_ensure_schema`, sem ORM nem migrations versionadas — implementado em `study/db.py` (`notes`, `highlights`, `cards`, `reviews`), não em `study/state.py` como o PLAN antecipava.

```yaml
- id: T-012
  priority: P1
  parallel: false
  depends_on: [T-011]
  ac_ref: AC-07
  tag: AFK
  vertical_slice: yes
  delivery: nesta entrega
  behavior: "Cartões gerados ficam em curadoria e só podem ser aceitos, editados ou descartados quando grounding.status permitir ancorada."
  verify: "python -m pytest tests/integration/test_study_flashcards.py -q"
  state: passing
  worktree: worktrees/026-plataforma-de-estudos/T-012
```

F4 também entrou nesta entrega e reutiliza provider/grounding da engine; `contradita`, `sem apoio`, `degraded` e `skipped` bloqueiam aceitação.

```yaml
- id: T-013
  priority: P1
  parallel: false
  depends_on: [T-012]
  ac_ref: AC-08
  tag: HITL
  vertical_slice: yes
  delivery: nesta entrega
  behavior: "Registrar rating 1–4 calcula a próxima data com FSRS, persiste revisão e mostra a fila devida sem campo de agendamento manual."
  verify: "python -m pytest tests/integration/test_study_reviews.py -q"
  state: passing
```

F5 também entrou nesta entrega. O comportamento de calendário e atalhos 1–4 requer prova renderizada e revisão humana, além do teste offline de cálculo e persistência.

---

## Matriz de dependências

| Task | Depende de | Pode ser paralela com |
|---|---|---|
| T-001 | — | — |
| T-002 | T-001 | — |
| T-003 | T-002 | T-004, T-005, T-006 |
| T-004 | T-002 | T-003, T-005, T-006 |
| T-005 | T-002 | T-003, T-004, T-006 |
| T-006 | T-002 | T-003, T-004, T-005 |
| T-007 | T-003 | T-008 |
| T-008 | T-004, T-005 | T-007 |
| T-009 | T-007 | — |
| T-010 | T-008, T-009 | — |
| T-011 | T-010 | — |
| T-012 | T-011 | — |
| T-013 | T-012 | — |

## Definition of Done

Uma task com `state: passing` significa:

1. `verify` rodou e passou.
2. Código e contrato foram revisados; tasks `HITL` também têm evidência de tela renderizada aprovada.
3. O critério de aceite (`ac_ref`) foi demonstrado.

A entrega fecha quando `T-001` a `T-013` estiverem `passing`, o ciclo `test-design` tiver orquestrado `test-red` e os riscos de contrato/browser tiverem suas evidências. `T-011` a `T-013` estavam previstas para depois e entraram nesta mesma branch, com a prioridade P1 que a SPEC já lhes dava.

## Loop autônomo

Tasks `AFK` com `state: not_started` e dependências concluídas são elegíveis para execução autônoma no worktree indicado. Tasks `HITL` sempre pausam para revisão humana; qualquer afirmação de aparência precisa de screenshot ou URL renderizada.
