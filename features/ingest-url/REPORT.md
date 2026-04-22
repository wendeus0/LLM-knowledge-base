# REPORT — ingest-url

**Objetivo:** Estabilizar e documentar o suporte a URLs no comando `kb ingest`, que já existia na codebase mas sem cobertura de testes e com contrato implícito.

**Escopo alterado:**

- `kb/web_ingest.py` — refatorado: constantes extraídas, funções auxiliares isoladas (`_build_frontmatter`, `_html_to_markdown`), estrutura em 6 etapas comentadas
- `tests/unit/test_web_ingest.py` — +2 testes (REQ-7 dependências ausentes, REQ-10 múltiplas URLs)
- `tests/unit/test_cli.py` — +1 teste (múltiplas URLs via CLI)
- `features/ingest-url/SPEC.md` — clarificada vs. código existente
- `CLAUDE.md` — contexto técnico atualizado

**Validações:**

- **quality-gate:** `QUALITY_PASS_WITH_GAPS` — 16/16 testes da feature passando; 4 falhas pré-existentes fora do escopo (heal, git, jobs)
- **security-review:** `EXECUTED (SECURITY_PASS_WITH_NOTES)` — SSRF mitigado via `_BLOCKED_NETWORKS`, `_resolve_and_validate()` e redirect pinning em `_follow_redirects()`; `_yaml_quote` manual de baixo risco; `RequestException` capturada em `ingest_url()`
- **code-review:** `EXECUTED (REVIEW_OK_WITH_NOTES)` — cobertura de exception `RequestException` não testada; teste `test_should_ingest_multiple_urls` não valida confirmação "Adicionado:"

**Riscos residuais:**

- `kb/web_ingest.py` `_follow_redirects()` → SSRF mitigado: hostname resolvido via `_resolve_and_validate()`, IP validado contra `_BLOCKED_NETWORKS`, redirect com IP pinado e Host header preservado
- `kb/web_ingest.py` `_yaml_quote()` → escape manual de `\` e `"` — não cobre caracteres YAML especiais (`:`, `#`, newlines) em títulos
- `tests/unit/test_web_ingest.py` → `RequestException` capturada em `ingest_url()` (linhas 159-160) mas sem teste dedicado → regressão silenciosa em erros de rede não-HTTP/timeout

**Follow-ups:**

- Substituir `_yaml_quote` por `yaml.safe_dump` ou `json.dumps` para serialização robusta
- Completar cobertura de `RequestException` com mock de `ConnectionError`

**Recomendação:** `READY_FOR_COMMIT`
