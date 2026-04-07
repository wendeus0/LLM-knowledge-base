# SECURITY_AUDIT_REPORT.md

Última auditoria: 2026-04-07 (sprint: validação operacional + fix code fence + import EPUB real)

---

## Auditoria 2026-04-07 — Escopo: `compile.py` e `guardrails.py`

### `_strip_outer_fence()` em `compile.py`
Operação de string pura (splitlines + slice). Sem I/O, sem execução de código. Seguro.

### Padrão `api_key` em `guardrails.py` — Falso positivo (LOW, pré-existente)
`(?i)(api[_-]?key\s*[:=]\s*|sk-[a-z0-9]{10,})` corresponde a nomes de variável como `OPENAI_API_KEY = "..."` em exemplos de código de livros técnicos. Não é vulnerabilidade — é falso positivo que degrada usabilidade. Mitigação documentada em `docs/SENSITIVE_CONTENT_POLICY.md`. Refinamento aguarda próximo sprint.

### Superfície de prompt injection via `compile.py:103`
`prompt = f"Documento: {raw_path.name}\n\n{content}"` — conteúdo de `raw/` incluído diretamente. Risco aceitável: knowledge base pessoal, entrada controlada pelo owner. Guardrails filtram credenciais reais antes do envio.

**Veredito desta auditoria incremental:** Nenhum achado novo de severidade MEDIUM ou superior. Achados anteriores (M1, M2, M3, L1–L4) permanecem abertos.

---

Última auditoria: 2026-04-06 (sprint: outputs-store + ingest-url + wikilink-traversal + rich-book-import-metadata)

---

## 1. Superfície de ataque mapeada

| Superfície | Módulo | Tipo de input |
|------------|--------|---------------|
| CLI local | `cli.py` | argumentos, flags, arquivos locais |
| URL fetch | `web_ingest.py` | URL arbitrária fornecida pelo usuário |
| EPUB/PDF parse | `book_import_core.py` | arquivo local (potencialmente externo) |
| LLM provider | `client.py` | resposta HTTP externa (OpenAI-compatible) |
| Git local | `git.py` | mensagens de commit geradas internamente |
| Wiki read/write | `compile.py`, `heal.py`, `qa.py`, `outputs.py` | sistema de arquivos local |
| Wikilink graph | `graph.py` | conteúdo de arquivos wiki locais |
| Variáveis de env | `config.py` | `.env` via `python-dotenv` |

Integrações externas: provider LLM (OpenCode Go / Ollama), git local.

---

## 2. Achados por severidade

### CRITICAL

Nenhum.

---

### HIGH

Nenhum.

---

### MEDIUM

#### M1. SSRF via URL fetch irrestrito em `web_ingest.py`
- **Onde:** `web_ingest.py:56` — `requests.get(url, timeout=15, ...)`
- **Risco:** o usuário pode passar qualquer URL, incluindo `http://localhost/`, `http://169.254.169.254/latest/meta-data/` (AWS metadata), ou serviços internos
- **Contexto:** ferramenta local; o usuário controla o input — risco real baixo em uso pessoal, mas relevante se a CLI for exposta via script automatizado ou agent
- **Mitigação sugerida:** validar scheme (`https://` apenas ou allowlist explícita); rejeitar IPs privados via `urllib.parse + ipaddress`
- **Skill para correção:** `fix-feature`

#### M2. `source_url` sem quoting em frontmatter YAML (`web_ingest.py`)
- **Onde:** `web_ingest.py:86` — `f"source_url: {url}\n"`
- **Risco:** URLs com `#` (âncora) são interpretadas como comentário YAML, truncando o valor; URLs com `:` em posição ambígua podem quebrar parsers YAML
- **Impacto:** integridade do frontmatter comprometida; artigos com URL fonte inválida perdem rastreabilidade
- **Mitigação sugerida:** envolver `url` com `_yaml_quote(url)` — função já disponível no módulo
- **Skill para correção:** `fix-feature`

#### M3. Política operacional de conteúdo sensível ainda não formalizada
- **Onde:** `compile`, `qa`, `heal`, `lint` com `--allow-sensitive`
- **Risco:** uso inconsistente pode gerar envio acidental de dados sensíveis ao provider externo
- **Status:** mantido do sprint anterior (2026-04-03)
- **Próximo passo:** documentar regra por tipo de conteúdo; considerar política por diretório (`raw/private/`)

---

### LOW

#### L1. Fallback para `xml.etree.ElementTree` vulnerável a XXE (`book_import_core.py`)
- **Onde:** `book_import_core.py:13-20` — fallback quando `defusedxml` não está instalado
- **Risco:** `defusedxml` está nas dependências principais (não opcional), mas se removido manualmente o fallback ativa XML inseguro
- **Impacto:** XXE em EPUB malicioso processado localmente
- **Mitigação sugerida:** trocar `pass` por `raise ImportError` explícito em produção, bloqueando o fallback

#### L2. Guardrails sem cobertura para formatos modernos de secrets
- **Onde:** `guardrails.py:9-15`
- **Risco:** padrões atuais cobrem `api_key`, `token`, `password`, `secret`, `private_key` e `sk-*` — mas não cobrem AWS access keys (`AKIA[A-Z0-9]{16}`), GitHub tokens (`ghp_`, `github_pat_`), GitLab tokens (`glpat-`), nem Bearer headers
- **Impacto:** documentos com credenciais cloud modernas podem passar sem detecção
- **Mitigação sugerida:** adicionar padrões para os formatos ausentes em `SENSITIVE_PATTERNS`

#### L3. LLM output escrito diretamente em wiki sem sanitização de frontmatter
- **Onde:** `compile.py:116` — `out.write_text(response, ...)`
- **Risco:** LLM comprometido ou com output malicioso podendo gerar `title` com path traversal (`../../etc/passwd`); mitigado por `_wiki_path` que limita a 60 chars e substitui `/` por `-`, mas não valida completamente
- **Impacto:** baixo — path traversal limitado ao `WIKI_DIR`

#### L4. `--no-commit` reduz rastreabilidade de auditoria
- **Status:** mantido do sprint anterior (2026-04-03) — ainda sem política operacional formal

---

## 3. Gestão de secrets

| Item | Status |
|------|--------|
| `.env` no `.gitignore` | ✓ confirmado |
| `.env.example` sem segredos reais | ✓ confirmado |
| `KB_API_KEY` apenas via env var | ✓ sem hardcode |
| Secrets nos logs do git (`commit()`) | ✓ mensagens geradas internamente, não incluem key |
| `outputs/` com QA data | ⚠ sem redação automática — pode conter respostas sensíveis commitadas |

---

## 4. Dependências e supply chain

| Pacote | Versão mínima | CVE conhecido | Observação |
|--------|---------------|---------------|------------|
| `defusedxml` | 0.7 | Nenhum | XML seguro |
| `typer` | 0.12 | Nenhum | — |
| `rich` | 13.0 | Nenhum | — |
| `python-dotenv` | 1.0 | Nenhum | — |
| `openai` | 1.0 | Nenhum | — |
| `requests` | 2.31 | Nenhum | — |
| `html2text` | 2024.1 | Nenhum | — |

> Auditoria manual. Recomenda-se `pip-audit` periódico para cobertura automatizada de CVEs.

---

## 5. CI/CD e automações

Sem CI/CD formal (sem `.github/workflows/`). Automações limitadas a commit git local via `kb/git.py`. Sem risco de pipeline injection.

---

## 6. Recomendações priorizadas

| Prioridade | Achado | Ação |
|------------|--------|------|
| P1 | M2: `source_url` sem quoting | `fix-feature` — 1 linha: `_yaml_quote(url)` |
| P1 | M3: política de sensibilidade | formalizar documento operacional |
| P1 | M1: SSRF via URL irrestrita | `fix-feature` — validar scheme + rejeitar IPs privados |
| P2 | L2: guardrails incompletos | `fix-feature` — adicionar padrões AWS/GitHub/GitLab |
| P2 | L1: fallback XML inseguro | `fix-feature` — substituir fallback por raise explícito |
| P2 | L4: `--no-commit` sem política | documentar como exceção operacional |

---

## 7. Próximos passos

- `fix-feature` para M2 (source_url quoting) — risco imediato baixo mas trivial de corrigir
- `fix-feature` para M1 (SSRF validation) — relevante se a CLI for usada em contextos automatizados
- abrir PENDING_LOG para L2 (guardrails modernos) se o uso de cloud credentials for esperado nos docs
- executar `pip-audit` para cobertura automatizada de CVEs

---

**Veredito:** `SECURITY_PASS_WITH_NOTES` — sem achados CRITICAL/HIGH; dois MEDIUM de baixo esforço para corrigir; postura de segurança melhorada em relação ao sprint anterior.
