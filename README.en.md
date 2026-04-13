# kb — LLM-powered Knowledge Base Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-223%20passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

An LLM-maintained knowledge base engine that ingests raw documents, compiles them into a structured markdown wiki, answers questions against the wiki, and performs automated health checks and healing. Inspired by [Andrej Karpathy](https://karpathy.ai/)'s vision for AI-assisted knowledge systems.

> [Versão em português](README.md)

> This repository contains the **engine** (`kb`), tests, and documentation. The **user corpus/vault** should live outside this repository, in a directory pointed to by `KB_DATA_DIR`.

## Overview

`kb` implements a 4-step central cycle:

```
Ingest → Compile → Q&A / Search → Heal / Lint
```

- **Ingest** — collect documents and URLs into `raw/`
- **Compile** — transform `raw/` into a structured wiki via LLM
- **Q&A** — query the wiki with source routing and wikilink traversal
- **Heal / Lint** — stochastic maintenance and automated auditing

Key features:

- Hybrid search (keyword + BM25 + RRF)
- Claim lifecycle (confidence, supersession, decay)
- Health gate with configurable thresholds
- Catalog of schedulable canonical jobs (`jobs cron`)
- Sensitive content guardrails with explicit opt-in (`--allow-sensitive`)
- Git auto-commit with opt-out (`--no-commit`)
- Recommended frontend: Obsidian via `obsidian-terminal`

## Commands

| Command          | Description                                    | Example                                                  |
| ---------------- | ---------------------------------------------- | -------------------------------------------------------- |
| `ingest`         | Add documents/URLs to `raw/`                   | `kb ingest doc.md https://example.com`                   |
| `import-book`    | Import EPUB/PDF as markdown chapters           | `kb import-book book.epub --compile`                     |
| `compile`        | Compile `raw/` → wiki via LLM (parallel)       | `kb compile --workers 4`                                 |
| `qa`             | Ask questions with source routing              | `kb qa "question" -f --no-commit`                        |
| `search`         | Hybrid search (keyword + BM25 + RRF)           | `kb search "term"`                                       |
| `heal`           | Stochastic healing of N files                  | `kb heal --n 10`                                         |
| `lint`           | Wiki audit via LLM                             | `kb lint`                                                |
| `jobs list`      | List canonical jobs                            | `kb jobs list`                                           |
| `jobs run`       | Run a job (`compile`, `review`, `decay`, etc.) | `kb jobs run compile`                                    |
| `jobs gate`      | Health gate with thresholds                    | `kb jobs gate --stale-max-pct 15`                        |
| `jobs cron`      | Full operational chain                         | `kb jobs cron`                                           |
| `jobs doc-gate`  | Document conformity for code changes           | `kb jobs doc-gate --base-ref main`                       |
| `handoff create` | Structured session handoff                     | `kb handoff create --scope "module" --summary "summary"` |

## Installation

```bash
git clone https://github.com/wendeus0/LLM-knowledge-base
cd kb

# Base (ingest, search, jobs, handoff)
pip install -e .

# With LLM support (compile, qa, heal, lint)
pip install -e ".[llm]"

# Textual PDF support with PyMuPDF
pip install -e ".[pdf]"

# OCR for scanned PDFs
pip install -e ".[ocr]"

# URL ingestion (web scraping)
pip install -e ".[web]"

# Development (pytest, ruff)
pip install -e ".[dev]"

# Everything
pip install -e ".[llm,pdf,ocr,web,dev]"
```

## Configuration

Create a `.env` file in the project root (see `.env.example`):

```bash
KB_API_KEY=your_api_key_here
KB_BASE_URL=https://opencode.ai/zen/go/v1  # optional
KB_MODEL=kimi-k2.5                          # optional
KB_DATA_DIR=/path/to/your/llm-wiki          # recommended: outside this repository
KB_TOPICS=cybersecurity,ai,python,typescript # optional; `general` remains the fallback
```

Expected structure inside `KB_DATA_DIR`:

```
<KB_DATA_DIR>/
  raw/          ← source documents + books/
  wiki/         ← compiled markdown
  outputs/      ← QA file-backs
  kb_state/     ← manifest + knowledge + learnings + claims + tracking
```

## Quick Start

```bash
export KB_DATA_DIR=/path/to/your/llm-wiki

# Ingest sample document
kb ingest examples/raw/getting-started.md

# Compile to wiki
kb compile

# Compile a specific book
kb compile "Mathematics for Machine Learning"

# Ask questions
kb qa "What does this corpus describe?"

# Archive response (recommended Obsidian workflow)
kb qa "Summarize this corpus" -f --no-commit

# Sensitive content (explicit opt-in)
kb compile --allow-sensitive

# Health check
kb heal --n 5 --no-commit
kb lint

# Import books
kb import-book ~/Downloads/book.epub ~/Downloads/book.pdf --compile

# OCR for scanned PDFs
kb import-book ~/Downloads/scan.pdf --ocr --chunk-pages 10
```

## Obsidian Integration

Recommended frontend: Obsidian over the user's vault, with the [`obsidian-terminal`](https://github.com/polyipseity/obsidian-terminal) community plugin.

### Setup

1. Set `KB_DATA_DIR` to your vault directory
2. Open `<KB_DATA_DIR>/wiki` as a vault in Obsidian
3. Install the `obsidian-terminal` plugin
4. Create an integrated profile with executable `/bin/zsh` (or `/bin/bash`), arguments `--login`
5. Add an alias: `alias kb='<repo>/.venv/bin/kb'`
6. Use the integrated terminal: `kb qa "question" --allow-sensitive`

Full guide: [docs/OBSIDIAN.md](docs/OBSIDIAN.md) (Portuguese)

## Architecture

```
# Engine repository
kb/
├── kb/                  ← Python package / engine
│   ├── cli.py           ← Typer CLI (680 lines)
│   ├── client.py        ← OpenAI SDK wrapper + model validation
│   ├── compile.py       ← raw → wiki via LLM (parallel)
│   ├── qa.py            ← Q&A with routing and wikilink traversal
│   ├── search.py        ← hybrid search (keyword + BM25 + RRF)
│   ├── heal.py          ← stochastic healing
│   ├── lint.py          ← LLM-based audit
│   ├── jobs.py          ← canonical jobs + health gate
│   ├── claims.py        ← claim lifecycle
│   ├── book_import.py   ← EPUB/PDF facade
│   ├── book_import_core.py ← core parsing (1100+ lines)
│   ├── router.py        ← source routing
│   ├── graph.py         ← wikilink traversal
│   ├── guardrails.py    ← sensitive content detection
│   ├── state.py         ← JSON persistence
│   ├── outputs.py       ← file-back store
│   ├── web_ingest.py    ← URL → Markdown
│   ├── git.py           ← auto-commit helper
│   ├── handoff.py       ← session handoff
│   ├── doc_gate.py      ← document conformity gate
│   ├── config.py        ← env vars and constants
│   ├── cmds/            ← execution layer (RTK-style)
│   ├── core/            ← runner + SQLite tracking
│   ├── discover/        ← command classification
│   └── analytics/       ← metrics and command history
├── tests/               ← 223 tests (96% coverage)
├── docs/                ← product documentation
├── features/            ← per-feature SPECs
└── examples/            ← neutral examples

# User corpus (outside repository)
<KB_DATA_DIR>/
├── raw/                 ← source documents + books/
├── wiki/                ← compiled, versioned markdown
├── outputs/             ← QA file-backs
└── kb_state/            ← manifest + knowledge + learnings + claims
```

Full C4 diagrams: [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) (Portuguese)

## Conventions

- **Separated corpus:** `raw/`, `wiki/`, `outputs/`, `kb_state/` live in `KB_DATA_DIR`, outside the repository
- **YAML frontmatter:** each compiled article includes `title`, `topic`, `tags`, `source`, `translated_by`, `reviewed_at`
- **Translation:** compiled articles are generated in Portuguese
- **Git:** corpus writes may trigger auto-commit; `--no-commit` suppresses
- **LLM:** the LLM never manually writes the wiki — everything goes through the CLI
- **Sensitivity:** `--allow-sensitive` is an explicit opt-in to bypass guardrails
- **Spec Driven Development:** no non-trivial change without a SPEC
- **Test Driven Development:** new behavior starts RED before GREEN

## Testing

Validated baseline as of 2026-04-08: 223 tests passing, 96% total coverage.

```bash
pytest                                    # all tests
pytest --cov=kb --cov-report=html         # with coverage
pytest tests/unit/                        # unit only
pytest tests/integration/                 # integration only
ruff check kb tests                       # lint
```

Per-module coverage: `git.py` 100%, `cli.py` 98%, `client.py` 97%, `book_import_core.py` 97%, `compile.py` 91%.

## Documentation

| Document                                                               | Description                                          |
| ---------------------------------------------------------------------- | ---------------------------------------------------- |
| [CONTEXT.md](CONTEXT.md)                                               | Macro context, principles, SDD+TDD flow (Portuguese) |
| [AGENTS.md](AGENTS.md)                                                 | Operational conventions (Portuguese)                 |
| [CONTRIBUTING.md](CONTRIBUTING.md)                                     | Contribution rules and gates (Portuguese)            |
| [docs/architecture/SDD.md](docs/architecture/SDD.md)                   | Spec Driven Development (Portuguese)                 |
| [docs/architecture/TDD.md](docs/architecture/TDD.md)                   | Test conventions (Portuguese)                        |
| [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) | Full C4 architecture (Portuguese)                    |
| [docs/architecture/SPEC_FORMAT.md](docs/architecture/SPEC_FORMAT.md)   | SPEC format (Portuguese)                             |
| [docs/API.md](docs/API.md)                                             | CLI + Python API reference (Portuguese)              |
| [docs/OBSIDIAN.md](docs/OBSIDIAN.md)                                   | Obsidian integration guide (Portuguese)              |
| [docs/adr/](docs/adr/)                                                 | 13 ADRs (0001-0013)                                  |
| [SECURITY.md](SECURITY.md)                                             | Security policy                                      |

## Tech Stack

| Layer      | Technology                                                |
| ---------- | --------------------------------------------------------- |
| Language   | Python 3.11+                                              |
| CLI        | Typer + Rich                                              |
| LLM        | OpenAI SDK (OpenCode Go, OpenAI, local)                   |
| Storage    | JSON (`kb_state/`), Markdown (`wiki/`), SQLite (tracking) |
| Search     | Keyword + BM25 + RRF (no external dependency)             |
| Versioning | Git                                                       |
| Testing    | pytest + pytest-cov                                       |
| Linting    | ruff                                                      |

## Roadmap

- [x] Base ingestion and compilation system
- [x] Book import (EPUB/PDF)
- [x] Q&A with file-back and source routing
- [x] Hybrid search (keyword + BM25 + RRF)
- [x] Stochastic healing and lint
- [x] Claim lifecycle
- [x] Canonical jobs and health gate
- [x] Full test suite (223 tests, 96% coverage)
- [x] Obsidian integration
- [x] No-commit mode and allow-sensitive
- [x] Session handoff
- [x] SQLite command tracking
- [x] Document conformity gate (doc-gate)
- [ ] Embeddings + hybrid RAG
- [ ] Multi-agent specialization

## License

MIT
