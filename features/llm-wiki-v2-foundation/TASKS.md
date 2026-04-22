# TASKS — Completar Fase 1 — Fundação claim-centric (audit + schema + contratos)

**Spec:** features/llm-wiki-v2-foundation/SPEC.md
**Plan:** features/llm-wiki-v2-foundation/PLAN.md
**MVP:** tasks [P1] completas

## Fase 1 — Setup

- [x] [T-001] [P1] Adicionar `AUDIT_PATH` em `kb/config.py` e garantir diretório `kb_state/audit/`

## Fase 2 — Foundational (P1)

- [x] [T-002] [P1] Criar `kb/audit.py` com funções `record_event`, `list_events`, `_read_events`, `_write_events`
- [x] [T-003] [P1] Criar `tests/unit/test_audit.py` com testes RED para audit log

## Fase 3 — User stories (P1→P2)

- [x] [T-004] [P1] [AC-ref: P1-1] Modificar `record_compiled_claims` em `kb/claims.py` para emitir `claim_created` via audit
- [x] [T-005] [P1] [AC-ref: P1-2] Modificar supersession em `kb/claims.py` para emitir `claim_superseded` via audit
- [x] [T-006] [P1] [AC-ref: P1-3] Modificar `apply_decay_cycle` em `kb/claims.py` para emitir `claim_status_changed` via audit ao marcar stale
- [x] [T-007] [P1] [AC-ref: P1-4] Modificar `run_contradiction_check` em `kb/claims.py` para emitir `claim_status_changed` via audit ao marcar disputed
- [x] [T-008] [P1] [AC-ref: P1-5, P1-6] Adicionar `schema_version: "1.0"` em claims escritos e fallback implícito na leitura
- [x] [T-009] [P1] [P] Atualizar `tests/unit/test_claims.py` para assertion de `schema_version` em claims
- [x] [T-010] [P2] [P] [AC-ref: P2-1] Verificar que job `decay` gera audit events (teste de integração leve em `test_jobs.py`)
- [x] [T-011] [P2] [P] [AC-ref: P2-2] Verificar que job `contradiction-check` gera audit events

## Fase 4 — Polish

- [x] [T-012] [P1] Rodar `python -m pytest tests/unit/test_claims*.py tests/unit/test_audit.py` e garantir pass
- [x] [T-013] [P1] Rodar `ruff check kb` e corrigir
- [x] [T-014] [P2] Revisar se `kb/jobs.py` precisa de ajuste (não deve, se audit for centralizado em claims)

---

## Matriz de dependências

| Task  | Depende de   | Pode ser paralela com      |
| ----- | ------------ | -------------------------- |
| T-001 | —            | —                          |
| T-002 | T-001        | —                          |
| T-003 | T-002        | —                          |
| T-004 | T-002        | T-005, T-006, T-007, T-008 |
| T-005 | T-002        | T-004, T-006, T-007, T-008 |
| T-006 | T-002        | T-004, T-005, T-007, T-008 |
| T-007 | T-002        | T-004, T-005, T-006, T-008 |
| T-008 | T-002        | T-004, T-005, T-006, T-007 |
| T-009 | T-008        | —                          |
| T-010 | T-006        | T-011                      |
| T-011 | T-007        | T-010                      |
| T-012 | T-003, T-009 | —                          |
| T-013 | T-012        | —                          |
| T-014 | T-012        | —                          |
