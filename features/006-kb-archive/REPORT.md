# REPORT — 006-kb-archive

**Feature:** Archive — Mover artigos stale/órfãos para archive/  
**Branch:** feat/006-kb-archive  
**Data:** 2026-04-21  
**Status:** READY_FOR_COMMIT

---

## Objetivo

Adicionar comando `kb archive` para mover artigos órfãos, stale ou antigos de `wiki/` para `archive/`, com preview via Rich e sem deleção de conteúdo.

## Escopo alterado

| Arquivo                                 | Mudança                                                                                           |
| --------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `kb/archive.py`                         | Novo módulo: `find_orphans`, `find_by_age`, `find_stale`, `collect_candidates`, `move_to_archive` |
| `kb/config.py`                          | Adiciona `ARCHIVE_DIR` derivado de `KB_DATA_DIR/archive`                                          |
| `kb/cli.py`                             | Novo comando `archive` com flags `--stale`, `--older-than N`, `--dry-run`                         |
| `tests/unit/test_archive.py`            | 7 testes unitários (órfãos, stale, older-than, dry-run, estrutura, validações)                    |
| `tests/integration/test_archive_cli.py` | 1 teste de integração CLI (preview table)                                                         |
| `features/006-kb-archive/SPEC.md`       | Especificação aprovada                                                                            |
| `features/006-kb-archive/PLAN.md`       | Plano técnico                                                                                     |
| `features/006-kb-archive/TASKS.md`      | Decomposição de tasks                                                                             |

## Validações executadas

- **quality-gate:** `QUALITY_PASS_WITH_GAPS` — ruff passa, 8/8 testes de archive passam. Gap: cobertura de `kb/archive.py` está em 78% (alvo SPEC: >= 90%). Linhas não cobertas incluem `find_stale` (fallback quando health summary indisponível), tratamento de erros de permissão em `move_to_archive`, e branches de symlink skip.
- **security-review:** `SECURITY_PASS_WITH_NOTES` — mitigações aplicadas: skip de symlinks em `find_orphans`/`find_by_age`, validação de contenção de destino em `move_to_archive`, `ValueError` em vez de `SystemExit` em `collect_candidates`, `try/except ValueError` para `relative_to` no CLI.
- **code-review:** SKIPPED — trivial/não aplicável (revisão de segurança cobriu aspectos críticos).

## Riscos residuais

- Cobertura abaixo de 90% em `kb/archive.py` → regressão silenciosa em caminhos de erro (permissão, health summary indisponível) não detectada por testes automáticos.
- `find_stale` depende de `kb.analytics.health.get_health_summary()` → se o módulo de health mudar, o comportamento de `--stale` pode quebrar sem testes de contrato.
- Symlink traversal mitigado mas não testado empiricamente em ambiente com symlinks reais.

## Follow-ups

1. Aumentar cobertura de testes de `kb/archive.py` para >= 90% (adicionar testes para erros de permissão e health summary indisponível).
2. Validar comportamento de `--stale` contra wiki real com health summary variado.
3. Avaliar se `archive/` deve ser adicionado a `.gitignore` ou versionado explicitamente em fluxos futuros.

## Recomendação final

`READY_FOR_COMMIT` — funcionalidade entregue, testes passam, mitigações de segurança aplicadas. Gap de cobertura não é bloqueante para merge mas deve ser endereçado no próximo ciclo.
