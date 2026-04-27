# TASKS — Ingestão de URLs via Scraping Python

**Spec:** features/ingest-url/SPEC.md
**Plan:** features/ingest-url/PLAN.md
**MVP:** tasks [P1] completas

## Fase 1 — Setup

- [T-001] [P1] Verificar extra `[web]` em `pyproject.toml` (requests, html2text)
- [T-002] [P1] Confirmar ambiente de teste: `pip install -e .[web]` funciona

## Fase 2 — Foundational (P1)

- [T-003] [P1] Validar contrato de `kb/web_ingest.py`: `ingest_url(url, no_commit=True) -> Path`
- [T-004] [P1] Validar tratamento de erro em `web_ingest.py`: timeout, HTTP 4xx/5xx, deps ausentes

## Fase 3 — User stories (P1→P2)

- [T-005] [P1] [P] Testar detecção automática de URL em `cli.py`: `startswith("http")` roteia corretamente
- [T-006] [P1] [P] Testar frontmatter gerado: `source_url`, `ingested_at`, `title` presentes e formatados
- [T-007] [P1] [P] Testar naming: slug derivado do `<title>` da página; fallback de URL sem título
- [T-008] [P1] [P] Testar comportamento `--commit` vs padrão write-local em ingestão de URL
- [T-009] [P2] [P] Testar múltiplas URLs: `kb ingest url1 url2 url3` processa todas sequencialmente
- [T-010] [P2] [P] Testar `--compile` após ingestão de URL: dispara compile corretamente
- [T-011] [P2] [P] Validar mensagem de erro quando `.[web]` não está instalado
- [T-012] [P2] Validar saída Rich manualmente: ao ingerir URL, o CLI exibe `[dim]Baixando {url}...[/]` e `[green]Adicionado:[/] {path}` (validação visual; não há "Convertendo..." no código atual)

## Fase 4 — Polish

- [T-013] [P3] Verificar cobertura de testes em `web_ingest.py` (meta: >=90%)
- [T-014] [P3] Revisar docstrings e `--help` do comando `ingest` para mencionar URLs
- [T-015] [P3] Atualizar `CHANGELOG.md` ou registro de entrega quando aprovado

---

## Matriz de dependências

| Task  | Depende de   | Pode ser paralela com |
| ----- | ------------ | --------------------- |
| T-001 | —            | T-002                 |
| T-002 | —            | T-001                 |
| T-003 | T-001, T-002 | T-004                 |
| T-004 | T-001, T-002 | T-003                 |
| T-005 | T-003        | T-006, T-007, T-008   |
| T-006 | T-003        | T-005, T-007, T-008   |
| T-007 | T-003        | T-005, T-006, T-008   |
| T-008 | T-003        | T-005, T-006, T-007   |
| T-009 | T-005        | T-010, T-011          |
| T-010 | T-005        | T-009, T-011          |
| T-011 | T-004        | T-009, T-010          |
| T-012 | T-003        | T-013                 |
| T-013 | T-005..T-012 | —                     |
| T-014 | T-005..T-012 | T-013                 |
| T-015 | T-013, T-014 | —                     |
