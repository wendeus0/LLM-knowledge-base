---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estrutura

Atualizada: 2026-04-08

```text
kb/
├── kb/               ← pacote Python
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py
│   ├── router.py, state.py, guardrails.py, jobs.py, git.py, cli.py, config.py
│   ├── book_import.py, book_import_core.py, graph.py, outputs.py, web_ingest.py
├── tests/            ← suíte unit + integration (223 passando)
├── docs/adr/         ← ADRs 0001–0007, 0010
├── docs/SENSITIVE_CONTENT_POLICY.md ← política operacional de sensibilidade
├── features/         ← SPECs de implementação
├── pyproject.toml    ← pytest-cov configurado; 96% cobertura real da suíte completa
├── memory/           ← memória distribuída
└── .git/             ← branch atual `feat/test-coverage-90`, alinhada a `origin/main` e com diff local da frente

<KB_DATA_DIR>/
├── raw/              ← documentos fonte
│   └── books/        ← livros importados em capítulos markdown + metadata.json
├── wiki/             ← markdown compilado
│   ├── _index.md
│   ├── summaries/
│   ├── ai/           ← 14 artigos (12 de EPUB "Building Applications with AI Agents")
│   ├── cybersecurity/, python/, typescript/
└── kb_state/         ← manifesto + stores knowledge/learnings
```

## Status

**Estado atual:** 2026-04-08 — frente `test-coverage-90` concluída localmente e pronta para fechamento documental

- ✅ frente `test-coverage-90` levou a suíte para `223` testes passando
- ✅ cobertura real total em `96%`
- ✅ módulos-alvo encerrados acima do limiar: `kb/cli.py` `98%`, `kb/client.py` `97%`, `kb/git.py` `100%`, `kb/book_import_core.py` `97%`
- ✅ quality gate local: `QUALITY_PASS`
- ✅ security review local: `SECURITY_PASS`
- ⚠️ fechamento Git ainda depende apenas dos gates finais de escopo/workflow antes de commit/PR

## Branches

`feat/test-coverage-90` — branch dedicada criada a partir de `main`; `origin/main...HEAD = 0/0` com diff local ainda não commitado.

## Marcos (Milestones)

1. **Baseline do produto** ✅
2. **Integração de livros** ✅
3. **Fundação inspirada em Pal** ✅
4. **Controles explícitos de execução sensível** ✅
5. **Expansão funcional** ✅ (outputs store, URL ingest, wikilink traversal, rich book metadata)
6. **Validação operacional real** ✅ (smoke test real, política sensibilidade, cobertura)
7. **Qualidade de output LLM** ✅ (fix code fence, 25 artigos restaurados, ADR-0010)
8. **Compile paralelo seguro** ✅ (geração paralela, persistência serial, batch seguro para `import-book --compile`)
9. **Cobertura orientada a risco** ✅ (`223` testes, `96%` total, contratos de EPUB/PDF/CLI/git/provider cobertos)

## Próximo marco sugerido

10. **Entrega Git limpa da frente atual** — rerodar gates de escopo/workflow e só então commitar/abrir PR
