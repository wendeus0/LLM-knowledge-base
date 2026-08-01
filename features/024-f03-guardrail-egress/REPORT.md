# REPORT — 024-f03-guardrail-egress

**Estado:** `DONE`
**Branch:** `fix/f03-guardrail-egress`

## Contexto

Achado F-03 da auditoria de segurança de 2026-07-31, aberto como P1: `assert_safe_for_provider` cobria compile/qa/heal/lint mas **não** os dois canais de egresso criados pelas features de retrieval. `embed_texts` mandava o texto integral de cada artigo para `KB_EMBED_BASE_URL`; o rerank mandava pergunta + snippets para `KB_RERANK_BASE_URL`. Ambos com host vindo de env sem validação. `--allow-sensitive` tinha deixado de ser o gate único de egresso.

O canal NLI da feature 023 nasceu coberto — gate antes do `verify`, guard de loopback no cliente. Isto alinha os dois antigos.

## Mudanças

| Arquivo | O quê |
|---|---|
| `kb/guardrails.py` | `is_loopback()` (extraído de `grounding.py`, agora único) e `assert_egress_allowed()` — a política |
| `kb/embeddings.py` | gate antes do POST, `source="embeddings"` |
| `kb/rerank.py` | gate antes do POST, `source="rerank"`; `rerank_base_url()` passa a devolver o endpoint efetivo |
| `kb/grounding.py` | passa a importar o helper único, sem duplicar |
| `tests/unit/test_egress_guardrails.py` | 9 testes |

## A política

| Endpoint | Comportamento |
|---|---|
| Esquema ≠ http/https | recusa sempre (`file://`, `ftp://`) |
| Loopback **sem proxy aplicável** | passa sem gate — o conteúdo não sai da máquina |
| Loopback **com proxy que o rotearia** | tratado como remoto (o payload sai) |
| Remoto | passa por `assert_safe_for_provider`; sem `KB_EGRESS_REMOTE_OK=1`, um aviso por processo |

Loopback não gateia por desenho: o gate de sensível existe contra egresso para provider **externo**. Aplicá-lo a `localhost:1234` bloquearia o uso normal do vault sem proteger nada.

## O P0 que o review pegou

A premissa "loopback não sai da máquina" era **falsa sob proxy**. Medido com httpx: com `HTTP_PROXY` setado e sem `NO_PROXY` cobrindo o host, `http://localhost:1234` é roteado pelo proxy — payload e credencial saem. É a mesma classe do vazamento por redirect corrigido no canal NLI, por outro transporte: **o guard valida a URL, não o caminho**.

Corrigido em duas camadas: `_proxy_would_route()` faz o loopback perder a isenção quando um proxy se aplicaria, e `local_http_client()` constrói os clientes de loopback com `trust_env=False`, para que proxy de ambiente nunca os alcance. Endpoints remotos seguem confiando no env (proxy corporativo é legítimo lá) e já passam pelo gate.

## Validação

- **856 passed** (eram 847), `ruff` limpo, gate de test-appeasement exit 0
- **Prova comportamental executada**, não só testes: defaults `:1234`/`:8081` com segredo → silenciosos; `file://`/`ftp://` → bloqueados; remoto + limpo → permitido com um aviso; **remoto + segredo sem allow → bloqueado**; com allow → permitido; aviso uma vez por processo

## Nota de review

`rerank_base_url()` mudou de `os.getenv("KB_BASE_URL", "")` para cair em `config.BASE_URL`. Parecia escopo extra, mas está correto: a função não alimenta o cliente (o caminho dedicado lê o env direto; sem ele o tráfego vai por `chat()` → `config.BASE_URL`). Gatear contra `""` recusaria o caminho default. A mudança alinha o valor gateado com o endpoint real.

## Dívida remanescente

`--allow-sensitive` não alcança estes dois canais: a cadeia `compile → refresh_embeddings_index → build_index → embed_texts` não carrega o parâmetro. Até carregar, o opt-in é `KB_EGRESS_ALLOW_SENSITIVE=1` — declarado e testado, não silencioso. Bloqueio sem escapatória seria pior.

`SENSITIVE_PATTERNS` não cobre chave AWS/GitHub/JWT (F-11, aberto desde abril): um teste meu usou `AKIA...` como fixture e passou sem bloquear, expondo o buraco. Trocado por padrão coberto; o F-11 segue no `PENDING_LOG`.


`_remote_egress_warned` é global ao processo, como `_grounding_warned` e `_warn_semantic_degraded` — consistente com o padrão do repo, mesma ressalva já registrada no `PENDING_LOG`.
