# TEST_COVERAGE_REPORT.md

## Sprint fechado em 2026-04-04

## Evidência

- suíte: **89 testes passando**
- cobertura total: **85%** (1019 stmts, 156 miss)
- ferramenta: `pytest-cov` instalado no venv

## Cobertura por módulo

| Módulo | Cobertura | Miss | Status |
|--------|-----------|------|--------|
| `kb/__init__.py` | 100% | 0 | ✓ |
| `kb/config.py` | 100% | 0 | ✓ |
| `kb/guardrails.py` | 100% | 0 | ✓ |
| `kb/lint.py` | 100% | 0 | ✓ |
| `kb/router.py` | 100% | 0 | ✓ |
| `kb/compile.py` | 97% | 2 | ✓ |
| `kb/qa.py` | 98% | 1 | ✓ |
| `kb/state.py` | 98% | 2 | ✓ |
| `kb/jobs.py` | 93% | 2 | ✓ |
| `kb/heal.py` | 89% | 6 | ✓ |
| `kb/search.py` | 91% | 3 | ✓ |
| `kb/book_import_core.py` | 84% | 62 | ✓ |
| `kb/book_import.py` | 77% | 3 | ⚠ abaixo de 80% |
| `kb/client.py` | 63% | 10 | ✗ gap crítico |
| `kb/cli.py` | 60% | 54 | ✗ gap crítico |
| `kb/git.py` | 31% | 11 | ✗ gap crítico |

## Módulos abaixo do limiar (80%)

| Módulo | Cobertura | Gap |
|--------|-----------|-----|
| `kb/git.py` | 31% | 11 linhas |
| `kb/cli.py` | 60% | 54 linhas |
| `kb/client.py` | 63% | 10 linhas |
| `kb/book_import.py` | 77% | 3 linhas |

## Top 3 gaps críticos

1. **`kb/git.py`** (31%) — linhas 9, 14-26: o caminho real de `commit()` com subprocess não é testado; apenas o caminho `enabled=False`. Gap de risco baixo (módulo simples), mas sem cobertura de regressão.

2. **`kb/cli.py`** (60%) — 54 linhas não cobertas incluem: comandos `ingest` (17-24), `import-book` (80-92), `compile` (123-148), `jobs` (182-211). CLI é a fronteira pública — gap de integração real.

3. **`kb/client.py`** (63%) — linhas 34-54: `get_client()` e `chat()` não são exercitados sem provider real. Esperado para suíte offline, mas sem fallback de test-double formal.

## Recomendação

- `kb/git.py`: adicionar teste que mocka `subprocess.run` e valida o caminho de commit com mudanças staged
- `kb/cli.py`: cobrir `ingest`, `import-book --compile`, `jobs list/run` via `typer.testing.CliRunner`
- `kb/client.py`: formalizar test-double (mock de `openai.OpenAI`) para `chat()` e `get_client()`

**Próximo sprint:** abrir itens de cobertura como P2 em `PENDING_LOG.md`.
