---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F1–F6: Validação operacional, política sensibilidade, pytest-cov, book2md, smoke test, EPUB

**Status:** Todas concluídas (2026-04-07)

**Resultado resumido:**
- F1 (smoke test): `search`, `lint`, `qa`, `heal`, `import-book --compile` OK com OpenCode Go
- F2 (política sensibilidade): `docs/SENSITIVE_CONTENT_POLICY.md` criado
- F3 (book2md): A3 rejeitada em ADR-0001; núcleo em `kb/book_import_core.py`
- F4 (merge PRs #14 e #15): mergeados conforme confirmação do usuário
- F5 (pytest-cov): 80% cobertura baseline; HTML em `htmlcov/`
- F6 (EPUB): "Building Applications with AI Agents" importado → 12 artigos em `wiki/ai/`

---

## Frentes abertas para próxima sessão

### F7: Corrigir 8 testes falhando em `test_web_ingest.py`

**Status:** Aberto

**Problema:** `AttributeError: None does not have the attribute 'get'` — mock setup com `patch.object` retornando `None` quando o target é um objeto sem atributo

**Impacto:** 8 testes falham; módulo `web_ingest.py` com 27% de cobertura

**Próximo passo:** corrigir fixture de mock em `tests/unit/test_web_ingest.py`

**Por que agora:** pre-existente, mas degrada confiança na suíte; resolver antes de adicionar nova feature

---

### F8: Merge PR#19 (feat/wikilink-traversal)

**Status:** Aguardando merge pelo usuário

**Branch:** `feat/wikilink-traversal`

---

## Decisões abertas

### Q1: O fluxo de livro importado deve sempre passar por `compile`?

**Estado:** mantido como `--compile` opcional; padrão operacional recomendado = com `--compile` para livros técnicos.

### Q2: `--no-commit` por comando ou política configurável?

**Estado:** mantido por comando nesta fase.

### Q3: Quando promover `book2md` a distribuição formal?

**Estado:** encerrado; sem demanda. Critério de reabertura: necessidade real de instalar fora do workspace.
