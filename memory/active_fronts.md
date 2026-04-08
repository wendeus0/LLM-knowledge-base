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

## Frentes concluídas nesta sessão

### F7: Hardening de compile paralelo seguro

**Status:** Concluído (2026-04-08)

**Resultado resumido:**

- `compile` agora separa geração e persistência (`compile_to_artifact` + `persist_artifact`)
- `compile_many()` faz geração paralela e persistência serial em ordem de entrada
- `kb compile` recebeu `--workers` e `--commit`
- `import-book --compile` reaproveita o mesmo modelo de lote seguro quando `workers > 1`
- suíte completa verde com cobertura real atualizada

---

## Frentes abertas para próxima sessão

### F8: Aumentar cobertura dos módulos mais fracos

**Status:** Aberto

**Problema:** a suíte está verde, mas a cobertura ainda está concentrada em poucos fluxos.

**Impacto:** `kb/cli.py` (`60%`), `kb/book_import_core.py` (`68%`) e `kb/git.py` (`31%`) continuam como gaps prioritários.

**Próximo passo:** atacar branches de erro, fallbacks e fluxos pouco exercitados nesses módulos.

**Por que agora:** a baseline está estável (`139` testes passando), então este é o momento de aumentar a proteção contra regressão.

---

### F9: Validar concorrência com provider real

**Status:** Aberto

**Problema:** a concorrência foi validada com mocks/interleaving controlado, mas não sob carga real do provider.

**Próximo passo:** rodar `kb compile --workers 4` contra um conjunto real pequeno e observar latência, estabilidade e ausência de corrupção de estado.

---

## Decisões abertas

### Q1: O fluxo de livro importado deve sempre passar por `compile`?

**Estado:** mantido como `--compile` opcional; padrão operacional recomendado = com `--compile` para livros técnicos.
**Atualização:** quando usado com `workers > 1`, o lote segue o mesmo contrato de `compile_many()`.

### Q2: `--no-commit` por comando ou política configurável?

**Estado:** segue por comando; `kb compile` já migrou para `--commit` explícito, mas outros comandos ainda usam `--no-commit` como opt-out.

### Q3: Quando promover `book2md` a distribuição formal?

**Estado:** encerrado; sem demanda. Critério de reabertura: necessidade real de instalar fora do workspace.
