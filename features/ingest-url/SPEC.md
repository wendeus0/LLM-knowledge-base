---
title: kb ingest — Ingestão de URLs via scraping Python
epic: compile
status: draft
pr:
---

# kb ingest — Ingestão de URLs via Scraping Python

## Objetivo

Hoje `kb ingest` aceita apenas arquivos locais. O usuário precisa copiar manualmente conteúdo de URLs para `raw/`. O sistema deve suportar `kb ingest <url>` para raspar o conteúdo de páginas web e salvá-lo automaticamente em `raw/`.

## Avaliação de dependências

**byterover-cli** foi avaliado e descartado: é uma camada de memória persistente para agentes (context tree, cloud sync), não um scraper.

**agent-browser** (Vercel Labs) foi descartado: dependência npm fora do ecossistema Python do projeto.

**Solução adotada:** Python nativo com `requests` + `html2text` como extra opcional `.[web]`, mantendo o ecossistema homogêneo.

## Requisitos funcionais

- [ ] `kb ingest <url>` detecta automaticamente se o argumento é URL (começa com `http://` ou `https://`)
- [ ] Faz download do HTML da página via `requests`
- [ ] Converte HTML para Markdown limpo via `html2text`
- [ ] Salva o arquivo em `raw/<slugified-title>.md` com frontmatter: `source_url`, `ingested_at`, `title`
- [ ] Exibe progresso via Rich: `Baixando...`, `Convertendo...`, `Salvo em raw/<arquivo>.md`
- [ ] Se a URL falhar (timeout, 4xx, 5xx): exibe erro descritivo e encerra sem criar arquivo
- [ ] Se `.[web]` não estiver instalado: mensagem clara `pip install -e .[web]` e encerra
- [ ] `kb ingest <url> --no-commit` suprime o commit automático (consistente com restante do CLI)
- [ ] `kb ingest <url> --compile` ingere e dispara `kb compile` em seguida (atalho conveniente)
- [ ] Múltiplas URLs em sequência: `kb ingest url1 url2 url3`

## Requisitos técnicos

- Novo módulo `kb/web_ingest.py` com função `ingest_url(url) -> Path`
- Detecção de URL em `cli.py`: `ingest` já existente recebe `url_or_path`; se `url_or_path.startswith("http")`, roteia para `web_ingest.ingest_url()`
- Naming: `slugify(title)[:80] + ".md"` onde `title` vem do `<title>` da página; fallback: `slugify` da URL sem protocolo, truncado a 40 chars (ex: `https://example.com/page` → `example-com-page`)
- Frontmatter gerado:
  ```yaml
  ---
  source_url: <url>
  ingested_at: <ISO datetime>
  title: <title da página>
  ---
  ```
- Timeout: 15s por request; User-Agent: `Mozilla/5.0` para evitar bloqueios simples
- `html2text` configurado: `ignore_links=False`, `ignore_images=True`, `body_width=0`
- `pyproject.toml`: novo extra `[web]` com `requests>=2.31`, `html2text>=2024.1`

## Limitações aceitas nesta versão

- Não suporta páginas JavaScript-heavy (single-page apps, lazy loading)
- Não suporta páginas atrás de login/auth
- Sem retry automático em falha de rede
- Esses casos permanecem como ingestão manual — documentar no `--help`

## Mudanças de API

```bash
# Já existente (sem mudança):
kb ingest ~/Downloads/artigo.md

# Novo:
kb ingest https://example.com/artigo        # salva em raw/artigo.md
kb ingest https://url1.com https://url2.com # múltiplas URLs
kb ingest https://url.com --compile         # ingere e compila
kb ingest https://url.com --no-commit       # sem commit automático
```

## Testes

- **Unit:** `test_web_ingest.py` — `ingest_url()` com mock de `requests.get`: testa naming, frontmatter, fallback de título, erro HTTP, timeout
- **Integration:** `kb ingest https://example.com` cria arquivo em `raw/` (requer rede)
- **Manual:** ingerir artigo real e confirmar legibilidade do markdown gerado

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 3h |
| Bloqueador | não |
| Risk | baixa |

## Dependências

- `outputs-store` não é pré-requisito
- `.[web]` extra deve ser adicionado ao `pyproject.toml`

## Notas

- Páginas JavaScript-heavy podem ser incorporadas no futuro via `playwright` como extra `.[web-js]` — não bloqueia esta SPEC
- `html2text` é leve (~150KB), sem sub-dependências pesadas
- O módulo `web_ingest.py` é isolado — não toca em `compile.py`, `qa.py` ou `heal.py`
