---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estado global

Atualizada: 2026-07-31

- **Branch:** `main` @ `6cd8d88` — PR #46 (`feat/compile-output-gate`) mergeado; CI verde em 3.11/3.12/3.13
- **Sprint atual:** política de corpus — wayfinder aberto em `docs/research/2026-07-30-politica-de-corpus/`, 8 tickets, 002 e 003 resolvidos
- **Gate novo:** `_validate_output` barra seção declarada e vazia e placeholder do template não substituído. Calibrado contra o corpus: 1 reprovado em 1.039 (0,10%)
- **Tests:** `608 passed` — cobertura 91%, `kb/compile.py` em 92%. Uma falha **local** em `test_diff::..._escape_rich_markup` que **passa no CI** (renderização do Rich dependente de TTY)
- **Decisão registrada:** ADR-0017 supera o ADR-0004; `stable_decisions.md` D16 supera D4. O ADR da política de corpus é o ticket 008 e depende de 004/005/006/007
- **Features abertas:** só `010-multi-vault-foundation` (`draft`); 008/009 e 011–022 arquivadas
- **Servidores locais:** `:1234` (LM Studio, embeddings `nomic-embed-text-v2-moe`) e `:8081` (`llama-server`, `bonsai-27b-1bit`). O `:8081` roda **fora do launchd** apesar de `KeepAlive` — processo órfão
- **Infra local ajustada e medida em 2026-07-31:** `start-bonsai-server.sh` passou a usar `-ctk q8_0 -ctv q8_0` e `--ctx-size 65536`. Footprint 9.609 MB → 3.178 MB **com 4× o contexto**; velocidade inalterada (17,6 → 16,6 tok/s); o compile de documento de 11k tokens deixou de falhar. Backups `.bak-20260731-{kvquant,ctx16k}`. Repo `local-ai-lab`, não versionado
- **Vault versionado:** `~/vault` é repo git desde 2026-07-30; `library/` (869 fontes, 185 MB) segue **fora do git**
- **Lint:** ruff `kb` clean

### O que o sprint estabeleceu sobre o corpus

A pergunta que abriu a sessão — "usar o KB ou refazer o vault?" — foi respondida com medição, e a resposta é **nenhum dos dois**:

| Achado | Número |
|---|---|
| Corpus **não** é raso | mediana de **10 headings** por artigo; 93% com ≥5; nenhum sem heading |
| Mas não segue o template atual | mediana de **1** seção com nome do template |
| Sem bibliografia | **1.035 de 1.037** artigos com zero referências |
| Near-duplicates reais | **59 pares** com cosseno ≥ 0,95 |
| Proveniência perdida | `manifest.json` nunca materializado — recompile **duplica** (provado: o mesmo doc OWASP virou 2 artigos) |
| Erro de compile chega ao leitor | `"filetype: Concorda apenas um tipo de arquivo"` íntegro nas 2 respostas do `qa` medidas |

O gargalo não é o retrieval (medido e consertado no sprint anterior) nem o corpus: é a **camada de compilação**.

### Retrieval — números medidos (golden de 152 casos, corpus de 1.033 artigos)

| Configuração | recall@5 | MRR |
|---|---|---|
| lexical (keyword + densidade + BM25) | 0,230 | 0,127 |
| híbrido (+ canal semântico) | 0,414 | 0,242 |
| híbrido + rerank 20 @ temp 0,8 | 0,467 | 0,299 |
| **híbrido + rerank 20 @ temp 0** | **0,467** | **0,343** |

Do lexical puro à melhor configuração: **recall dobrou** (0,230 → 0,467) e **MRR quase triplicou** (0,127 → 0,343). `recall@20 = 0,720` é o teto ainda disponível para ordenação.

**Config vencedora:** `KB_RERANK_MODEL=bonsai-27b-1bit` local (porta 8081) com perfil `deterministic`. O `granite4:tiny-h` da VM é 13× mais rápido e **pior que não reordenar** (0,388).

### Corpus real (medido)

- `~/vault/wiki`: **1.037 artigos** indexáveis, 4,26M palavras. Exclusões por convenção `_*`/`.*`: `_summaries/` (1.022), `_sources/` (712).
- `~/vault/library`: 869 fontes (800 md, 17 pdf, 6 epub), 4,79M palavras.
- Índice de embeddings: **148 MB**, formato 2 (chunking por seção), 8.685 chunks, `nomic-embed-text-v2-moe`.
- **Python:** 3.11+ (venv local Python 3.14, `.venv/`)
- **CI:** workflows atuais só rodam gates operacionais (`jobs gate`, `doc-gate`); pytest+ruff entram na Fase 1 do plano

## Estrutura do pacote

```text
kb/
├── kb/
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py
│   ├── router.py, state.py, guardrails.py, jobs.py, git.py, cli.py, config.py
│   ├── book_import.py, book_import_core.py, book_import_pdf.py
│   ├── graph.py, outputs.py, web_ingest.py, archive.py
│   ├── audit.py, claims.py, doc_gate.py, handoff.py
│   ├── cmds/{compile,qa,lint,search}/run.py
│   ├── core/{runner.py, tracking.py}
│   ├── analytics/{gain.py, health.py, history.py}
│   └── discover/{registry.py, rules.py}
├── tests/            ← 327 testes (unit + integration)
├── docs/adr/         ← ADRs 0001–0016
├── docs/superpowers/plans/ ← plano de robustez 2026-07-09
├── features/         ← 008/009 (SPEC draft); concluídas em _archived/
├── pyproject.toml
└── memory/           ← memória distribuída (este diretório)

<KB_DATA_DIR>/
├── raw/              ← documentos fonte + books/
├── wiki/             ← markdown compilado
├── outputs/          ← file-backs de QA
└── kb_state/         ← manifesto + stores knowledge/learnings
```

## ADRs

0001–0016. Destaques: ADR-0015 (runtime topic taxonomy), ADR-0016 (--commit explícito).

## Marcos (Milestones)

1–10 concluídos (baseline, livros, Pal, execução sensível, expansão funcional, validação real, qualidade de output, compile paralelo, cobertura, baseline green + SSRF).
11. **LLM Wiki v2 Foundation** ✅ (PR #35)
12. **Robustez do core + template de artigo** ← em execução (plano 2026-07-09)

## Snapshot 2026-07-16 (pós-sessão stack local)

- Features 011/012/013 DONE locais (noise filter, semantic retrieval, context budget) — SEM commit; 452 testes, 93% cobertura
- Stack: Bonsai 27B 1-bit (llama-server fork PrismML :8081) + Nomic v2-moe (LM Studio :1234); Ollama removido; `.env` → vault
- QA fast: ~1m15s–2m/pergunta (era ~5min); perfis fast/deep/paper/article prontos
- Vault: 2.059 artigos indexados; 74 artigos-ruído arquivados
- Watch cloud semanal vigia MLX 1-bit upstream (migração futura GGUF→MLX nativo)

## 2026-08-01

**Feature ativa:** `023-claim-grounding` — especificação completa, código não iniciado. `CONTRACT_VALID` + `EVAL_DESIGN_PARTIAL`. Entra por `test-design`.

**Política de corpus:** `WAYFINDER_CLEAR`, oito tickets fechados, consolidados no ADR-0018 (ainda no PR #59, não em `main`).

**Pilha de verificação de resposta:** três estágios medidos em protótipo throwaway (`prototypes/answer-verification/`, fora de `kb/`). Cobertura por centroide e ancoragem por NLI confirmados; consistência entre gerações não confirmado. Juiz LLM verbalizando confiança reprovado (83% de falso alarme).

**PRs abertos:** #59 (decisões da política de corpus), #60 (protótipo + spec da 023).

**Suíte:** 739 passed.

## 2026-08-01 (fim)

**Feature 023:** `DELIVERED` — 8/8 tasks. Serviço NLI em `:1235` no launchd; holdout de 12 pares congelado.
**F-03:** resolvido (PR #63). Nenhum P1 aberto no backlog de segurança.
**Novo no harness:** skill `test-appeasement-audit` (detector AST + gate de CI com ratchet), aplicada ao kb — baseline vazio.
**Novo no kb:** `scripts/appeasement_report.py` no CI, `docs/failures/test-appeasement-mock-shaped-production.md`.
**Suíte:** 869 passed. **PRs abertos:** nenhum.
