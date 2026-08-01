---
feature: 023-claim-grounding
status: validated
validated_at: 2026-08-01
validated_by: orquestrador (Opus 5) — SPEC e PLAN redigidos por GPT 5.6 Terra, revisados zero-trust
---

# CONTRACT — 023-claim-grounding

Checklist de premissas técnicas e de produto entre planejamento e execução. Cada item foi verificado no repositório ou no ambiente, não assumido.

## Premissas técnicas verificadas

| # | Premissa | Verificação | Estado |
|---|---|---|---|
| 1 | `kb qa` não tem `--json` hoje | `kb qa --help` lista `--allow-sensitive --commit --deep --depth --file-back --no-commit --no-rerank --no-traverse --to-wiki --top-k`; ausência de `--json` confirmada | **confirmado** — adição nova, não quebra parser existente |
| 2 | `--file-back` e `--to-wiki` existem | mesmo `--help` | **confirmado** |
| 3 | Porta 1235 livre para o serviço NLI | `lsof -nP -iTCP:1235 -sTCP:LISTEN` sem resultado | **confirmado** — `:1234` é embeddings, `:8081` é rerank |
| 4 | `torch`/`transformers` fora do `pyproject.toml` | `pip list` no venv do projeto não os lista; extras declarados são `llm`, `web`, `pdf`, `ocr`, `dev` | **confirmado** — a decisão de serviço HTTP separado preserva isso |
| 5 | Existe padrão de servidor local com probe e degradação | `kb/embed_server.py` (probe), `kb/search.py:_warn_semantic_degraded` (aviso único em stderr) | **confirmado** — o contrato novo reusa o padrão, não inventa |
| 6 | Feature 014 é `embed-server-autostart` | `features/_archived/014-embed-server-autostart` | **confirmado** — referência do PLAN correta |
| 7 | Chamadores de `kb.qa.answer()` | `kb/qa.py:141`, `kb/cmds/qa/run.py:27,42`, mais 5 arquivos de teste | **confirmado** — coberto pela task T-008, acrescentada na análise |
| 8 | O modelo NLI roda e responde em português | medido no protótipo: 12/12 em pares de deriva sutil em português técnico | **confirmado** |

## Premissas de produto

| # | Premissa | Estado |
|---|---|---|
| 9 | A verificação **nunca bloqueia** a resposta | **acordado** — 28% de falso alarme medido torna bloqueio inaceitável (RF-06) |
| 10 | Detecção de lacuna fica **fora** desta feature | **acordado** — depende do reagrupamento por tema do ticket 006; declarado em `## Fora de escopo` |
| 11 | O usuário provisiona o serviço NLI fora do pacote | **acordado** — sem servidor, a feature degrada e o `qa` segue funcionando (RF-04) |
| 12 | Os números do protótipo são viabilidade, não meta de aceite | **acordado** — a SPEC declara 72% como linha de base, não como gate |

## Riscos aceitos

| Risco | Mitigação acordada |
|---|---|
| **28% de falso alarme** | Anotação não-bloqueante em todas as superfícies; revisão humana decide |
| **Limiares ajustados nos dados de avaliação**, sem validação separada | Declarado na SPEC e no PLAN; corrigir limiar com holdout está em `## Fora de escopo` desta feature |
| **8 pares artigo↔fonte na medição**, quase todos IA/LLM | Aceito para MVP; ampliar a amostra é trabalho posterior |
| **Dependência operacional** do serviço local | Degradação por stderr, uma vez por execução; a resposta nunca depende dele |
| **`answer()` muda de contrato interno** | T-008 trava a compatibilidade por teste; alterar asserção existente é sinal de adaptador errado, não de teste errado |

## Gate de TDD

Duas condições binárias de risco marcadas no PLAN:

- **output estrutural estável** — `--json` cria schema público e o file-back ganha seção persistida;
- **contrato HTTP entre serviços** — `GET /v1/models` e `POST /v1/nli`.

Portanto o fluxo é **`test-design`**, com `test-red` como camada base (`RED_OK` segue sendo o gate canônico). Testes de contrato HTTP e de estabilidade do JSON são obrigatórios antes do GREEN.

## Fora deste contrato

- Consistência entre gerações e verbalização de confiança: medidos e reprovados (`ESTUDO-DETECCAO-DE-LACUNA.md`).
- Calibração com conjunto de validação separado.
- Conversão do modelo para ONNX.
- Bloqueio, edição ou regeneração de resposta por veredito negativo.

## Referências

- `features/023-claim-grounding/SPEC.md` — `SPEC_VALID` em 2026-08-01
- `features/023-claim-grounding/PLAN.md` — arquitetura e condições de risco
- `prototypes/answer-verification/` — protótipo medido (PR #60)
- `docs/adr/0018-corpus-policy-theme-articles-over-chapter-articles.md` — ADR que pediu este trabalho (chega com o PR #59)
