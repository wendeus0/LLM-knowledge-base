---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estado global

Atualizada: 2026-07-30

- **Branch:** `main` @ `94459e3` — a `feat/semantic-retrieval-foundation` (16 commits) foi mergeada em `f694190` e publicada; CI verde
- **Retrieval na CLI:** `kb search --rerank N` (opt-in) e `kb qa` com rerank ligado por padrão. Até 2026-07-30 o ganho medido não alcançava comando nenhum
- **Decisão registrada:** ADR-0017 supera o ADR-0004; `stable_decisions.md` D16 supera D4
- **Tests:** `602 passed, 0 failed` ✅ — cobertura 92%
- **Features abertas:** só `010-multi-vault-foundation` (`draft`); 008/009 e 011–022 arquivadas em `features/_archived/`
- **Servidores locais:** LaunchAgents `com.wendeus.kb-embed` (:1234, watchdog 60s) e `com.wendeus.kb-rerank` (:8081, KeepAlive) sobem no login; logs em `~/Library/Logs/kb-*.log`
- **Vault versionado:** `~/vault` é repo git desde 2026-07-30 (commit 0160552, 4.281 arquivos); `kb/git.py` resolve o repo que contém cada arquivo — antes `--commit` era descartado em silêncio
- **Lint:** ruff `kb tests` clean
- **Módulos novos:** `sampling.py`, `rerank.py`, `query_expansion.py`, `bench.py`, `chunking.py`, `embed_server.py`, `embeddings.py`, `noise.py`

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
