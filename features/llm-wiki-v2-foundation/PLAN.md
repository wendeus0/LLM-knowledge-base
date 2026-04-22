# PLAN — Completar Fase 1 — Fundação claim-centric (audit + schema + contratos)

**Branch:** feat/llm-wiki-v2-foundation
**Data:** 2026-04-21
**Spec:** features/llm-wiki-v2-foundation/SPEC.md
**MVP scope:** critérios [P1] da SPEC

## Contexto técnico

| Campo                   | Valor                                                    |
| ----------------------- | -------------------------------------------------------- |
| Linguagem/versão        | Python 3.11+                                             |
| Dependências principais | typer, rich, openai SDK (client), pytest                 |
| Storage                 | JSONL append-only em `KB_DATA_DIR/kb_state/`             |
| Estratégia de testes    | pytest offline, mocks para I/O externo                   |
| Plataforma alvo         | Linux/local CLI                                          |
| Tipo de projeto         | CLI engine Python                                        |
| Constraints             | Sem chamadas de rede nos testes; separação engine/corpus |

## Arquitetura escolhida

### Novos módulos

- `kb/audit.py` — CRUD append-only de eventos de auditoria em `kb_state/audit/events.jsonl`
- `tests/unit/test_audit.py` — testes de audit log

### Módulos modificados

- `kb/claims.py` — adicionar `schema_version` em novos claims; invocar `audit.record_event` nas transições de status e supersession
- `kb/config.py` — adicionar `AUDIT_PATH = STATE_DIR / "audit" / "events.jsonl"`
- `kb/jobs.py` — jobs `decay` e `contradiction-check` já invocam claims; garantir que audit events sejam gerados via claims.py
- `tests/unit/test_claims.py` — assertions de `schema_version` nos claims criados

### Contratos

- Evento de audit:
  ```json
  {
    "schema_version": "1.0",
    "event_id": "evt_<uuid>",
    "event_type": "claim_created|claim_superseded|claim_status_changed",
    "claim_id": "clm_<uuid>",
    "payload": { "old_status": "active", "new_status": "stale" },
    "source": "compile|decay|contradiction-check",
    "timestamp": "2026-04-21T15:00:00Z"
  }
  ```

## Decisões técnicas

**Decisão:** Audit log é append-only síncrono (write no final da operação).  
**Motivo:** Simplicidade, consistência imediata, e volume baixo esperado. Se performance se tornar problema, podemos bufferizar futuramente.

**Decisão:** `schema_version` é string `"1.0"` e é adicionado apenas em writes novos; leitura faz fallback implícito.  
**Motivo:** Evita migração massiva de dados antigos; forward-compatible.

**Decisão:** `kb/audit.py` não levanta exceção em falha de escrita; loga warning e deixa a operação principal continuar.  
**Motivo:** Audit é observabilidade, não deve bloquear funcionalidade core.

**Decisão:** Jobs não chamam audit diretamente; audit é triggerado pelas funções de claims.py que os jobs utilizam.  
**Motivo:** Centraliza lógica de mutação em um só lugar, evitando duplicação.

## Constitution check

- Não conflita com `CONTEXT.md`: mantém separação engine/corpus (tudo em `KB_DATA_DIR`).
- Não conflita com `AGENTS.md`: segue snake_case, docstrings em pt-BR, sem type hints obrigatórios.
- ADR 0013 já aprovou a direção claim-centric.

## Dependências entre componentes

1. `config.py` (novo path de audit) deve existir antes de `audit.py`.
2. `audit.py` deve existir antes de modificar `claims.py` (claims depende de audit).
3. Modificações em `claims.py` são pré-requisito para testes de claims atualizados.
4. Jobs não precisam de mudança estrutural se `claims.py` já emitir audit.
