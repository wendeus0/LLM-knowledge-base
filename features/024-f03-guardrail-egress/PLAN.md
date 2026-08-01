# PLAN — fix F-03: guardrail de conteúdo sensível nos canais de embedding e rerank

**Variante:** fix-feature (achado F-03 da auditoria de segurança 2026-07-31; sem SPEC nova)
**Branch:** fix/f03-guardrail-egress

## O defeito

`assert_safe_for_provider` cobre compile/qa/heal/lint mas **não** os dois canais novos de egresso:
- `kb/embeddings.py` — `embed_texts` manda o texto integral de cada artigo para `KB_EMBED_BASE_URL`
- `kb/rerank.py` — manda pergunta + snippets para `KB_RERANK_BASE_URL`

Ambos os URLs vêm de env sem validação de host/esquema. `--allow-sensitive` deixou de ser o gate único de egresso. O canal NLI da 023 nasceu coberto (gate antes do verify + guard de loopback) — os dois antigos não.

## Decisões

1. **Gate de sensível**: `assert_safe_for_provider` nos dois canais, com `source="embeddings"` / `source="rerank"`. Exceção: quando o endpoint é loopback, o egresso não sai da máquina — o gate de sensível não se aplica (mesma razão pela qual o NLI local não passa por ele; o compile/qa gateiam porque falam com provider REMOTO).
2. **Validação de host**: host não-loopback exige opt-in explícito `KB_EGRESS_REMOTE_OK=1` OU passa pelo gate de sensível. Esquema restrito a http/https (reusar o padrão `_is_loopback` de `kb/grounding.py` — extrair para helper comum se preciso, sem duplicar).
3. Falha do gate degrada como cada canal já degrada (embeddings → lexical; rerank → ordem original), nunca derruba o comando.

## Condições binárias de risco

Nenhuma marcada → test-red direto (RED_OK como gate).

## Módulos

| Arquivo | Mudança |
|---|---|
| `kb/embeddings.py` | gate antes do POST em `embed_texts` |
| `kb/rerank.py` | gate antes do POST |
| `kb/guardrails.py` ou helper | política de egresso (loopback vs remoto) |
| `tests/unit/test_egress_guardrails.py` | novo |
