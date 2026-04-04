---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estrutura

Criada: 2026-04-03

```
kb/
├── raw/              ← documentos fonte
├── wiki/             ← markdown compilado
│   ├── _index.md
│   ├── cybersecurity/, ai/, python/, typescript/
├── kb/               ← pacote Python
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py, git.py, cli.py, config.py
├── .pi/              ← manifesto Pi (manifest.yaml)
├── pyproject.toml
├── .env.example
├── CLAUDE.md, AGENTS.md, ERROR_LOG.md, PENDING_LOG.md
├── memory/           ← memória distribuída
└── .git/             ← versionado
```

## Status

**Fase 1 — base funcional: COMPLETA**
- ✓ Módulos Python (client, compile, qa, search, heal, lint, git, cli)
- ✓ CLI funcionando (kb ingest, compile, qa, search, heal, lint)
- ✓ Git automático em todo write
- ✓ Stochastic heal + file-back
- ✓ Testes: 40/40 passing, 73% cobertura
- ✓ .env configurado (kimi-k2.5)
- ✓ Pipeline testado end-to-end (ingest → compile → qa → file-back)

## Branches

- `main` — estável, baseline verde
- `feat/book-import` — importação de EPUB/PDF para capítulos Markdown (WIP, sem SPEC)

## Marcos

1. **Setup completo** — ✓ DONE
2. **Testes** — ✓ DONE (40/40, 73% coverage)
3. **Book import** — WIP (branch feat/book-import, precisa SPEC)
4. **Obsidian** — futuro (P2)
5. **Embeddings + RAG** — futuro (P2)
