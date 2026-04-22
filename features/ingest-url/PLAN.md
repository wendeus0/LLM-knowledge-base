# PLAN — Ingestão de URLs via Scraping Python

**Branch:** feat/ingest-url
**Data:** 2026-04-21
**Spec:** features/ingest-url/SPEC.md
**MVP scope:** Critérios de aceite P1 (detecção, download, conversão, salvamento, erro, frontmatter)

## Contexto técnico

| Campo                   | Valor                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------- |
| Linguagem/versão        | Python 3.11+                                                                       |
| Dependências principais | requests>=2.31, html2text>=2024.1 (extra `.[web]`), Typer, Rich                    |
| Storage                 | Sistema de arquivos (`KB_DATA_DIR/raw/`)                                           |
| Estratégia de testes    | Unit com mock de requests; integration opcional com rede real                      |
| Plataforma alvo         | CLI local (Linux/macOS/WSL)                                                        |
| Tipo de projeto         | Engine de knowledge base mantida por LLM                                           |
| Constraints             | Não toca em compile.py/qa.py/heal.py; write local por padrão; `--commit` explícito |

## Arquitetura escolhida

A feature estende o comando `kb ingest` existente sem redefini-lo:

- **Módulo existente:** `kb/web_ingest.py` — função `ingest_url(url, no_commit=True) -> Path`
- **Integração existente:** `kb/cli.py` — comando `ingest` já detecta URLs via `startswith("http")` e roteia para `web_ingest.ingest_url()`
- **Fluxo:** URL → requests.get() → html2text → frontmatter YAML → salva em `raw/<slug>.md`
- **Frontmatter raw/:** `title`, `source_url`, `ingested_at` (específico de raw/; wiki compilada usa `source`/`reviewed_at`)

## Decisões técnicas

- **Decisão:** Manter `web_ingest.py` isolado (não mesclar com `compile.py`). **Motivo:** Separação de responsabilidades; ingestão é I/O simples, compilação é LLM-heavy.
- **Decisão:** Usar `slugify(title)[:80]` com fallback `slugify(url_without_protocol)[:40]`. **Motivo:** Nomes legíveis e seguros para filesystem; truncamento evita paths excessivamente longos.
- **Decisão:** `html2text` com `ignore_links=False, ignore_images=True, body_width=0`. **Motivo:** Preserva links úteis; ignora imagens (fora de escopo); sem quebra de linha forçada para markdown limpo.
- **Decisão:** Timeout 15s + User-Agent `Mozilla/5.0`. **Motivo:** Equilíbrio entre tolerância a latência e evitar bloqueios simples de bots.
- **Decisão:** Extra `[web]` em `pyproject.toml`. **Motivo:** Mantém a base leve; quem precisa de scraping instala opcionalmente.

## Constitution check

- Alinhado com `CONTEXT.md`: separação engine/corpus preservada (dados vão para `raw/` em `KB_DATA_DIR`).
- Alinhado com `AGENTS.md`: nenhuma mudança arquitetural profunda; apenas extensão de CLI existente.
- Alinhado com convenção de commit: `no_commit=True` por padrão, `--commit` explícito.

## Dependências entre componentes

1. `pyproject.toml` com extra `[web]` → deve existir antes de qualquer teste de importação
2. `kb/web_ingest.py` → já existe; precisa de validação de contrato
3. `kb/cli.py` → já integra URLs; precisa de teste de roteamento
4. `tests/unit/test_web_ingest.py` → testa `ingest_url()` isoladamente
