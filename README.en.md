# kb — LLM-powered Knowledge Base Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/wendeus0/LLM-knowledge-base/actions/workflows/tests.yml/badge.svg)](https://github.com/wendeus0/LLM-knowledge-base/actions/workflows/tests.yml)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)

Turn raw reading into living knowledge: you ingest documents, URLs, and entire books; an LLM compiles everything into a structured markdown wiki browsable in Obsidian, answers questions against it, and keeps it healthy on its own. Based on [Andrej Karpathy](https://karpathy.ai/)'s vision of LLM-maintained knowledge bases.

> [Versão em português](README.md)

> This repository contains the **engine** (`kb`), tests, and documentation. The **user corpus/vault** lives outside it, in a directory pointed to by `KB_DATA_DIR`.

## Overview

`kb` implements a 4-step central cycle:

```
Ingest → Compile → Q&A / Search → Heal / Lint
```

- **Ingest** — collect documents, URLs, and books (EPUB/PDF) into `raw/`
- **Compile** — transform `raw/` into a structured wiki via LLM, with output validation
- **Q&A / Search** — query the wiki with source routing, wikilink traversal, and hybrid search
- **Heal / Lint** — stochastic maintenance with backups and automated auditing

### LLM pipeline with real validation

- LLM output is **validated before persisting**: mandatory frontmatter, code-fence stripping, clean per-file errors — garbage never becomes an article
- **Versioned article templates** in the engine (`kb/templates/`), with per-vault override in `<KB_DATA_DIR>/templates/` — the wiki structure is yours, no code changes needed
- **Book-aware compile**: imported chapters carry book title, author, and position (via `metadata.json`) into the prompt
- **Healing with a safety net**: versioned backups + anti-loss validation before any overwrite; atomic writes for all artifacts

### Structured knowledge

- Hybrid search (keyword + BM25 + RRF) with zero external dependencies
- Claim lifecycle (confidence, supersession, decay) with an append-only audit trail
- Q&A with file-back: every answer can become an article or a versionable output

### Operations

- Schedulable canonical jobs (`jobs cron`) + health gate with thresholds
- Metrics dashboard (`kb stats`) and visual wiki diff (`kb diff`)
- Sensitive-content guardrails with explicit opt-in; SSRF protection on URL ingestion
- Git with explicit per-command commit (`--commit`)
- CI with a Python 3.11–3.13 matrix and coverage gate (85%)

## Commands

| Command          | Description                                    | Example                                                  |
| ---------------- | ---------------------------------------------- | -------------------------------------------------------- |
| `ingest`         | Add documents/URLs to `raw/`                   | `kb ingest doc.md https://example.com`                   |
| `import-book`    | Import EPUB/PDF as markdown chapters           | `kb import-book book.epub --compile`                     |
| `compile`        | Compile `raw/` → wiki via LLM (parallel)       | `kb compile --workers 4`                                 |
| `qa`             | Ask questions with source routing              | `kb qa "question" -f --commit`                           |
| `search`         | Hybrid search (keyword + BM25 + RRF)           | `kb search "term"`                                       |
| `stats`          | Wiki metrics dashboard                         | `kb stats --json`                                        |
| `diff`           | Visual wiki diff via git                       | `kb diff --stat --since HEAD~3`                          |
| `heal`           | Stochastic healing of N files                  | `kb heal --n 10`                                         |
| `lint`           | Wiki audit via LLM                             | `kb lint`                                                |
| `archive`        | Move stale/orphan articles from wiki/ → archive/ | `kb archive --stale --dry-run`                         |
| `discovery run`  | Discover and ingest new sources (arXiv, news)  | `kb discovery run --query "llm agents"`                  |
| `jobs list`      | List canonical jobs                            | `kb jobs list`                                           |
| `jobs run`       | Run a job (`compile`, `review`, `decay`, etc.) | `kb jobs run compile`                                    |
| `jobs gate`      | Health gate with thresholds                    | `kb jobs gate --stale-max-pct 15`                        |
| `jobs cron`      | Print suggested cron block                     | `kb jobs cron`                                           |
| `jobs doc-gate`  | Document conformity for code changes           | `kb jobs doc-gate --base-ref main`                       |
| `handoff create` | Structured session handoff                     | `kb handoff create --scope "module" --summary "summary"` |

## Installation

```bash
git clone https://github.com/wendeus0/LLM-knowledge-base
cd LLM-knowledge-base

# Base (ingest, search, stats, diff, jobs, handoff)
pip install -e .

# With LLM support (compile, qa, heal, lint)
pip install -e ".[llm]"

# Textual PDF support
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

Local shortcuts for setup and recurring validation:

```bash
make help
make install-dev
make lint
make test-unit
make check
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
  templates/    ← (optional) article template overrides
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

# Archive response locally (recommended Obsidian workflow)
kb qa "Summarize this corpus" -f

# Archive and version explicitly
kb qa "Summarize this corpus" -f --commit

# Check wiki health
kb stats

# See what changed since the last commit
kb diff --stat

# Sensitive content (explicit opt-in)
kb compile --allow-sensitive

# Local health check
kb heal --n 5
kb lint

# Import books
kb import-book ~/Downloads/book.epub ~/Downloads/book.pdf --compile

# OCR for scanned PDFs
kb import-book ~/Downloads/scan.pdf --ocr --chunk-pages 10
```

## Article templates

The structure of compiled articles lives in versioned templates — `kb/templates/article.md` (standalone documents) and `kb/templates/chapter.md` (book chapters, with book context in the frontmatter). To customize without touching the engine, place your version in `<KB_DATA_DIR>/templates/` and it takes effect for your vault.

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
├── kb/                     ← Python package / engine
│   ├── cli.py              ← Typer CLI (10 commands + jobs/discovery/handoff groups)
│   ├── client.py           ← OpenAI SDK wrapper + provider/model validation
│   ├── compile.py          ← raw → wiki via LLM (parallel, output validation, book context)
│   ├── templates/          ← article/chapter templates (per-vault override)
│   ├── templates_loader.py ← engine ↔ vault resolution
│   ├── frontmatter.py      ← single flat-YAML frontmatter parser
│   ├── qa.py               ← Q&A with routing and wikilink traversal
│   ├── search.py           ← hybrid search (keyword + BM25 + RRF)
│   ├── stats.py            ← metrics aggregation (dashboard)
│   ├── diff.py             ← formatted wiki git diff
│   ├── heal.py             ← stochastic healing (validation + versioned backups)
│   ├── lint.py             ← LLM-based audit
│   ├── archive.py          ← stale/orphan article archiving
│   ├── jobs.py             ← canonical jobs + health gate
│   ├── claims.py           ← claim lifecycle
│   ├── audit.py            ← append-only claim event trail
│   ├── discovery.py        ← arXiv/news discovery + schedulable ingestion
│   ├── book_import.py      ← EPUB/PDF facade
│   ├── book_import_core.py ← EPUB parser (TOC, HTML→MD, metadata)
│   ├── book_import_pdf.py  ← PDF extraction (PyMuPDF; optional OCR)
│   ├── router.py           ← source routing
│   ├── graph.py            ← wikilink traversal
│   ├── guardrails.py       ← sensitive content detection
│   ├── web_ingest.py       ← URL → Markdown (SSRF protection)
│   ├── state.py            ← JSON persistence
│   ├── outputs.py          ← file-back store
│   ├── fsutil.py           ← atomic writes
│   ├── git.py              ← explicit commit helper
│   ├── handoff.py          ← session handoff
│   ├── doc_gate.py         ← document conformity gate
│   ├── config.py           ← env vars and constants
│   ├── cmds/               ← execution layer (compile, qa)
│   ├── core/               ← SQLite execution tracking
│   ├── discover/           ← declarative command classification
│   └── analytics/          ← claim health + command history
├── tests/                  ← 405 tests (92% coverage; 85% CI gate)
├── docs/                   ← product documentation
├── features/               ← per-feature SPECs
└── examples/               ← neutral examples

# User corpus (outside the repository)
<KB_DATA_DIR>/
├── raw/                    ← source documents + books/
├── wiki/                   ← compiled, versioned markdown
├── outputs/                ← QA file-backs
├── kb_state/               ← manifest + knowledge + learnings + claims
└── templates/              ← (optional) template overrides
```

Architecture design and evolution: [docs/architecture/SDD.md](docs/architecture/SDD.md)

## Conventions

- **Separate corpus:** `raw/`, `wiki/`, `outputs/`, `kb_state/` live in `KB_DATA_DIR`, outside the repository
- **YAML frontmatter:** every compiled article includes `title`, `topic`, `tags`, `source`, `translated_by`; `reviewed_at` is stamped by heal
- **Templates:** article structure defined in `kb/templates/`, customizable per vault
- **Translation:** compiled articles are generated in Portuguese
- **Git:** corpus writes stay local by default; use `--commit` to version the current run
- **LLM:** the LLM never writes the wiki manually — everything goes through the CLI, with output validation before persisting
- **Sensitivity:** `--allow-sensitive` is the explicit opt-in to bypass guardrails
- **Spec Driven Development:** no non-trivial change without a SPEC
- **Test Driven Development:** new behavior is born RED before GREEN

## Tests and CI

405 tests (unit + integration), 92% total coverage. CI runs pytest and ruff on Python 3.11, 3.12, and 3.13 for every PR, with an 85% coverage gate.

```bash
pytest                                    # all tests
pytest --cov=kb --cov-report=html         # with HTML coverage
pytest tests/unit/                        # unit only
pytest tests/integration/                 # integration only
ruff check kb tests                       # lint

# Equivalent shortcuts
make lint
make test
make test-unit
make test-integration
make check
```

## Documentation

| Document                                                             | Description                                 |
| -------------------------------------------------------------------- | ------------------------------------------- |
| [CONTEXT.md](CONTEXT.md)                                             | Macro context, principles, and SDD+TDD flow |
| [AGENTS.md](AGENTS.md)                                               | Conventions and operational context         |
| [CONTRIBUTING.md](CONTRIBUTING.md)                                   | Contribution rules and gates                |
| [docs/architecture/SDD.md](docs/architecture/SDD.md)                 | Software Design Document                    |
| [docs/architecture/TDD.md](docs/architecture/TDD.md)                 | Testing conventions                         |
| [docs/architecture/SPEC_FORMAT.md](docs/architecture/SPEC_FORMAT.md) | SPEC format                                 |
| [docs/API.md](docs/API.md)                                           | CLI + Python API reference                  |
| [docs/OBSIDIAN.md](docs/OBSIDIAN.md)                                 | Obsidian integration                        |
| [docs/adr/](docs/adr/)                                               | ADRs (0001–0016)                            |
| [SECURITY.md](SECURITY.md)                                           | Security policy                             |

## Stack

| Layer         | Technology                                                |
| ------------- | --------------------------------------------------------- |
| Language      | Python 3.11+                                              |
| CLI           | Typer + Rich                                              |
| LLM           | OpenAI SDK (OpenCode Go, OpenAI, local)                   |
| Storage       | JSON (`kb_state/`), Markdown (`wiki/`), SQLite (tracking) |
| Search        | Keyword + BM25 + RRF (no external dependency)             |
| Versioning    | Git                                                       |
| Tests         | pytest + pytest-cov                                       |
| Lint / CI     | ruff + GitHub Actions (3.11–3.13 matrix)                  |

## Roadmap

- [x] Core ingestion and compilation system
- [x] Book import (EPUB/PDF) with rich metadata
- [x] Q&A with file-back and source routing
- [x] Hybrid search (keyword + BM25 + RRF)
- [x] Stochastic healing with backups and validation
- [x] Claim lifecycle + audit trail
- [x] Canonical jobs, health gate, and discovery (arXiv/news)
- [x] Obsidian integration
- [x] Structured LLM output validation in compile
- [x] Article templates with per-vault override + book-aware compile
- [x] Metrics dashboard (`kb stats`) and wiki diff (`kb diff`)
- [x] CI with 3.11–3.13 matrix and coverage gate
- [ ] Multi-vault (SPEC ready in `features/010-multi-vault-foundation/`)
- [ ] Embeddings + hybrid RAG

## License

GNU Affero General Public License v3.0 — see [LICENSE](LICENSE).

AGPL-3.0 ensures modifications and network uses (SaaS, APIs) remain open: any fork or user-facing service must make the corresponding source code available under the same license.
