# kb — Engine de Knowledge Base mantida por LLM

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-223%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

Engine de knowledge base mantida por LLM. Ingesta documentos brutos, compila para wiki em markdown, responde perguntas contra a wiki, faz health checks e healing automático. Inspirado na [proposta de Andrej Karpathy](https://karpathy.ai/) sobre sistemas de conhecimento assistidos por IA.

> [English version](README.en.md)

> Este repositório contém a **engine** (`kb`), testes e documentação. O **corpus/vault do usuário** deve ficar fora daqui, em um diretório próprio apontado por `KB_DATA_DIR`.

## Visão Geral

O `kb` implementa um ciclo central de 4 etapas:

```
Ingest → Compile → Q&A / Search → Heal / Lint
```

- **Ingest** — coleta documentos e URLs para `raw/`
- **Compile** — transforma `raw/` em wiki estruturada via LLM
- **Q&A** — consulta a wiki com routing por fonte e traversal de wikilinks
- **Heal / Lint** — manutenção estocástica e auditoria automática

Características principais:

- Busca híbrida (keyword + BM25 + RRF)
- Claims com ciclo de vida (confiança, supersessão, decaimento)
- Health gate com thresholds configuráveis
- Catálogo de jobs canônicos agendáveis (`jobs cron`)
- Guardrails de conteúdo sensível com opt-in explícito (`--allow-sensitive`)
- Git auto-commit com opt-out (`--no-commit`)
- Frontend recomendado: Obsidian via `obsidian-terminal`

## Comandos

| Comando          | Descrição                                         | Exemplo                                                 |
| ---------------- | ------------------------------------------------- | ------------------------------------------------------- |
| `ingest`         | Adicionar documentos/URLs a `raw/`                | `kb ingest doc.md https://example.com`                  |
| `import-book`    | Importar EPUB/PDF em capítulos markdown           | `kb import-book livro.epub --compile`                   |
| `compile`        | Compilar `raw/` → wiki via LLM (paralelo)         | `kb compile --workers 4`                                |
| `qa`             | Perguntar com routing por fonte                   | `kb qa "pergunta" -f --no-commit`                       |
| `search`         | Busca híbrida (keyword + BM25 + RRF)              | `kb search "termo"`                                     |
| `heal`           | Correção estocástica de N arquivos                | `kb heal --n 10`                                        |
| `lint`           | Auditoria da wiki via LLM                         | `kb lint`                                               |
| `jobs list`      | Listar jobs canônicos                             | `kb jobs list`                                          |
| `jobs run`       | Executar job (`compile`, `review`, `decay`, etc.) | `kb jobs run compile`                                   |
| `jobs gate`      | Health gate com thresholds                        | `kb jobs gate --stale-max-pct 15`                       |
| `jobs cron`      | Encadeamento operacional completo                 | `kb jobs cron`                                          |
| `jobs doc-gate`  | Conformidade documental para mudanças de código   | `kb jobs doc-gate --base-ref main`                      |
| `handoff create` | Handoff estruturado de sessão                     | `kb handoff create --scope "modulo" --summary "resumo"` |

## Instalação

```bash
git clone https://github.com/wendeus0/LLM-knowledge-base
cd kb

# Base (ingest, search, jobs, handoff)
pip install -e .

# Com suporte a LLM (compile, qa, heal, lint)
pip install -e ".[llm]"

# Suporte a PDFs textuais
pip install -e ".[pdf]"

# OCR para PDFs escaneados
pip install -e ".[ocr]"

# Ingestão de URLs (web scraping)
pip install -e ".[web]"

# Desenvolvimento (pytest, ruff)
pip install -e ".[dev]"

# Tudo junto
pip install -e ".[llm,pdf,ocr,web,dev]"
```

## Configuração

Crie `.env` na raiz do projeto (veja `.env.example`):

```bash
KB_API_KEY=sua_api_key_aqui
KB_BASE_URL=https://opencode.ai/zen/go/v1  # opcional
KB_MODEL=kimi-k2.5                          # opcional
KB_DATA_DIR=/caminho/para/seu/llm-wiki      # recomendado: fora deste repositório
KB_TOPICS=cybersecurity,ai,python,typescript # opcional; `general` é fallback implícito
```

Estrutura esperada em `KB_DATA_DIR`:

```
<KB_DATA_DIR>/
  raw/          ← documentos fonte + books/
  wiki/         ← markdown compilado
  outputs/      ← file-backs de QA
  kb_state/     ← manifesto + knowledge + learnings + claims + tracking
```

## Uso Rápido

```bash
export KB_DATA_DIR=/caminho/para/seu/llm-wiki

# Ingerir documento de exemplo
kb ingest examples/raw/getting-started.md

# Compilar para wiki
kb compile

# Compilar livro específico
kb compile "Mathematics for Machine Learning"

# Perguntar
kb qa "O que este corpus descreve?"

# Arquivar resposta (fluxo recomendado com Obsidian)
kb qa "Resuma este corpus" -f --no-commit

# Conteúdo sensível (opt-in explícito)
kb compile --allow-sensitive

# Health check
kb heal --n 5 --no-commit
kb lint

# Importar livros
kb import-book ~/Downloads/book.epub ~/Downloads/book.pdf --compile

# OCR para PDFs escaneados
kb import-book ~/Downloads/scan.pdf --ocr --chunk-pages 10
```

## Obsidian

Frontend recomendado: Obsidian sobre o vault do usuário, com o plugin [`obsidian-terminal`](https://github.com/polyipseity/obsidian-terminal).

### Setup

1. Configurar `KB_DATA_DIR` para o diretório do vault
2. Abrir `<KB_DATA_DIR>/wiki` como vault no Obsidian
3. Instalar o plugin `obsidian-terminal`
4. Criar profile integrado com executable `/bin/zsh` (ou `/bin/bash`), arguments `--login`
5. Adicionar alias: `alias kb='<repo>/.venv/bin/kb'`
6. Usar no terminal integrado: `kb qa "pergunta" --allow-sensitive`

Guia completo: [docs/OBSIDIAN.md](docs/OBSIDIAN.md)

## Arquitetura

```
# Repositório da engine
kb/
├── kb/                  ← pacote Python / engine
│   ├── cli.py           ← CLI Typer (680 linhas)
│   ├── client.py         ← wrapper OpenAI SDK + validação de modelo
│   ├── compile.py        ← raw → wiki via LLM (paralelo)
│   ├── qa.py             ← Q&A com routing e wikilink traversal
│   ├── search.py         ← busca híbrida (keyword + BM25 + RRF)
│   ├── heal.py           ← healing estocástico
│   ├── lint.py           ← auditoria via LLM
│   ├── jobs.py           ← jobs canônicos + health gate
│   ├── claims.py         ← ciclo de vida de claims
│   ├── book_import.py    ← facade EPUB/PDF
│   ├── book_import_core.py ← parsing core (1100+ linhas)
│   ├── router.py         ← routing por fonte
│   ├── graph.py          ← wikilink traversal
│   ├── guardrails.py     ← detecção de conteúdo sensível
│   ├── state.py          ← persistência JSON
│   ├── outputs.py        ← file-back store
│   ├── web_ingest.py     ← URL → Markdown
│   ├── git.py            ← auto-commit helper
│   ├── handoff.py        ← handoff de sessão
│   ├── doc_gate.py       ← conformidade documental
│   ├── config.py         ← variáveis de ambiente e constantes
│   ├── cmds/             ← camada de execução (RTK-style)
│   ├── core/             ← runner + tracking SQLite
│   ├── discover/         ← classificação de comandos
│   └── analytics/        ← métricas e histórico de comandos
├── tests/               ← 223 testes (96% cobertura)
├── docs/                ← documentação do produto
├── features/            ← SPECs por feature
└── examples/            ← exemplos neutros

# Corpus do usuário (fora do repositório)
<KB_DATA_DIR>/
├── raw/                 ← documentos fonte + books/
├── wiki/                ← markdown compilado e versionado
├── outputs/             ← file-backs de QA
└── kb_state/            ← manifesto + knowledge + learnings + claims
```

Diagramas completos: [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)

## Convenções

- **Corpus separado:** `raw/`, `wiki/`, `outputs/`, `kb_state/` vivem em `KB_DATA_DIR`, fora do repositório
- **Frontmatter YAML:** cada artigo compilado inclui `title`, `topic`, `tags`, `source`, `translated_by`, `reviewed_at`
- **Tradução:** artigos compilados são gerados em português
- **Git:** writes no corpus podem gerar commit automático; `--no-commit` suprime
- **LLM:** o LLM nunca escreve a wiki manualmente — tudo via CLI
- **Sensibilidade:** `--allow-sensitive` é opt-in explícito para bypass de guardrails
- **Spec Driven Development:** nenhuma mudança não trivial sem SPEC
- **Test Driven Development:** comportamento novo nasce RED antes de GREEN

## Testes

Baseline validada em 2026-04-08: 223 testes passando, 96% de cobertura total.

```bash
pytest                                    # todos os testes
pytest --cov=kb --cov-report=html         # com cobertura
pytest tests/unit/                        # apenas unitários
pytest tests/integration/                 # apenas integração
ruff check kb tests                       # lint
```

Cobertura por módulo: `git.py` 100%, `cli.py` 98%, `client.py` 97%, `book_import_core.py` 97%, `compile.py` 91%.

## Documentação

| Documento                                                              | Descrição                                  |
| ---------------------------------------------------------------------- | ------------------------------------------ |
| [CONTEXT.md](CONTEXT.md)                                               | Contexto macro, princípios e fluxo SDD+TDD |
| [AGENTS.md](AGENTS.md)                                                 | Convenções e contexto operacional          |
| [CONTRIBUTING.md](CONTRIBUTING.md)                                     | Regras de contribuição e gates             |
| [docs/architecture/SDD.md](docs/architecture/SDD.md)                   | Spec Driven Development                    |
| [docs/architecture/TDD.md](docs/architecture/TDD.md)                   | Convenções de teste                        |
| [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) | Arquitetura C4 completa                    |
| [docs/architecture/SPEC_FORMAT.md](docs/architecture/SPEC_FORMAT.md)   | Formato de SPEC                            |
| [docs/API.md](docs/API.md)                                             | Referência CLI + Python API (813 linhas)   |
| [docs/OBSIDIAN.md](docs/OBSIDIAN.md)                                   | Integração com Obsidian                    |
| [docs/adr/](docs/adr/)                                                 | 13 ADRs (0001-0013)                        |
| [SECURITY.md](SECURITY.md)                                             | Política de segurança                      |

## Stack

| Camada        | Tecnologia                                                |
| ------------- | --------------------------------------------------------- |
| Linguagem     | Python 3.11+                                              |
| CLI           | Typer + Rich                                              |
| LLM           | OpenAI SDK (OpenCode Go, OpenAI, local)                   |
| Armazenamento | JSON (`kb_state/`), Markdown (`wiki/`), SQLite (tracking) |
| Busca         | Keyword + BM25 + RRF (sem dependência externa)            |
| Versionamento | Git                                                       |
| Testes        | pytest + pytest-cov                                       |
| Lint          | ruff                                                      |

## Roadmap

- [x] Sistema base de ingestão e compilação
- [x] Importação de livros (EPUB/PDF)
- [x] Q&A com file-back e routing por fonte
- [x] Busca híbrida (keyword + BM25 + RRF)
- [x] Stochastic healing e lint
- [x] Claims com ciclo de vida
- [x] Jobs canônicos e health gate
- [x] Suite de testes completa (223 testes, 96% cobertura)
- [x] Integração com Obsidian
- [x] Modo no-commit e allow-sensitive
- [x] Handoff de sessão
- [x] Tracking SQLite de comandos
- [x] Conformidade documental (doc-gate)
- [ ] Embeddings + RAG híbrido
- [ ] Multi-agent specialization

## Licença

MIT
