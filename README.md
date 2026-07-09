# kb — Engine de Knowledge Base mantida por LLM

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/wendeus0/LLM-knowledge-base/actions/workflows/tests.yml/badge.svg)](https://github.com/wendeus0/LLM-knowledge-base/actions/workflows/tests.yml)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)

Transforme leitura bruta em conhecimento vivo: você ingere documentos, URLs e livros inteiros; um LLM compila tudo em uma wiki markdown estruturada e navegável no Obsidian, responde perguntas com base nela e a mantém saudável de forma autônoma. Baseado na [proposta de Andrej Karpathy](https://karpathy.ai/) de knowledge bases mantidas por LLM.

> [English version](README.en.md)

> Este repositório contém a **engine** (`kb`), testes e documentação. O **corpus/vault do usuário** vive fora daqui, em um diretório apontado por `KB_DATA_DIR`.

## Visão Geral

O `kb` implementa um ciclo central de 4 etapas:

```
Ingest → Compile → Q&A / Search → Heal / Lint
```

- **Ingest** — coleta documentos, URLs e livros (EPUB/PDF) para `raw/`
- **Compile** — transforma `raw/` em wiki estruturada via LLM, com validação do output
- **Q&A / Search** — consulta a wiki com routing por fonte, traversal de wikilinks e busca híbrida
- **Heal / Lint** — manutenção estocástica com backup e auditoria automática

### Pipeline LLM com validação real

- Output do LLM **validado antes de persistir**: frontmatter obrigatório, strip de code fences, erro limpo por arquivo — lixo não vira artigo
- **Templates de artigo versionados** na engine (`kb/templates/`), com override por vault em `<KB_DATA_DIR>/templates/` — a estrutura da wiki é sua, sem tocar código
- **Compile ciente de livro**: capítulos importados carregam título, autor e posição no livro (via `metadata.json`) para o prompt
- **Healing com rede de segurança**: backup versionado + validação anti-perda antes de qualquer sobrescrita; escrita atômica em todos os artefatos

### Conhecimento estruturado

- Busca híbrida (keyword + BM25 + RRF) sem dependência externa
- Claims com ciclo de vida (confiança, supersessão, decaimento) e trilha de auditoria append-only
- Q&A com file-back: cada resposta pode virar artigo ou output versionável

### Operação

- Jobs canônicos agendáveis (`jobs cron`) + health gate com thresholds
- Dashboard de métricas (`kb stats`) e diff visual da wiki (`kb diff`)
- Guardrails de conteúdo sensível com opt-in explícito; proteção SSRF na ingestão de URLs
- Git com commit explícito por comando (`--commit`)
- CI com matriz Python 3.11–3.13 e gate de cobertura (85%)

## Comandos

| Comando          | Descrição                                         | Exemplo                                                 |
| ---------------- | ------------------------------------------------- | ------------------------------------------------------- |
| `ingest`         | Adicionar documentos/URLs a `raw/`                | `kb ingest doc.md https://example.com`                  |
| `import-book`    | Importar EPUB/PDF em capítulos markdown           | `kb import-book livro.epub --compile`                   |
| `compile`        | Compilar `raw/` → wiki via LLM (paralelo)         | `kb compile --workers 4`                                |
| `qa`             | Perguntar com routing por fonte                   | `kb qa "pergunta" -f --commit`                          |
| `search`         | Busca híbrida (keyword + BM25 + RRF)              | `kb search "termo"`                                     |
| `stats`          | Dashboard de métricas da wiki                     | `kb stats --json`                                       |
| `diff`           | Diff visual da wiki via git                       | `kb diff --stat --since HEAD~3`                         |
| `heal`           | Correção estocástica de N arquivos                | `kb heal --n 10`                                        |
| `lint`           | Auditoria da wiki via LLM                         | `kb lint`                                               |
| `archive`        | Mover artigos stale/órfãos de wiki/ → archive/    | `kb archive --stale --dry-run`                          |
| `discovery run`  | Descobrir e ingerir fontes novas (arXiv, news)    | `kb discovery run --query "llm agents"`                 |
| `jobs list`      | Listar jobs canônicos                             | `kb jobs list`                                          |
| `jobs run`       | Executar job (`compile`, `review`, `decay`, etc.) | `kb jobs run compile`                                   |
| `jobs gate`      | Health gate com thresholds                        | `kb jobs gate --stale-max-pct 15`                       |
| `jobs cron`      | Imprime bloco de cron sugerido                    | `kb jobs cron`                                          |
| `jobs doc-gate`  | Conformidade documental para mudanças de código   | `kb jobs doc-gate --base-ref main`                      |
| `handoff create` | Handoff estruturado de sessão                     | `kb handoff create --scope "modulo" --summary "resumo"` |

## Instalação

```bash
git clone https://github.com/wendeus0/LLM-knowledge-base
cd LLM-knowledge-base

# Base (ingest, search, stats, diff, jobs, handoff)
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

Se preferir atalhos locais para setup e validação recorrente:

```bash
make help
make install-dev
make lint
make test-unit
make check
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
  templates/    ← (opcional) override dos templates de artigo
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

# Arquivar resposta localmente (fluxo recomendado com Obsidian)
kb qa "Resuma este corpus" -f

# Arquivar e versionar explicitamente
kb qa "Resuma este corpus" -f --commit

# Ver a saúde da wiki
kb stats

# Ver o que mudou desde o último commit
kb diff --stat

# Conteúdo sensível (opt-in explícito)
kb compile --allow-sensitive

# Health check local
kb heal --n 5
kb lint

# Importar livros
kb import-book ~/Downloads/book.epub ~/Downloads/book.pdf --compile

# OCR para PDFs escaneados
kb import-book ~/Downloads/scan.pdf --ocr --chunk-pages 10
```

## Templates de artigo

A estrutura dos artigos compilados vive em templates versionados — `kb/templates/article.md` (documentos avulsos) e `kb/templates/chapter.md` (capítulos de livro, com contexto do livro no frontmatter). Para customizar sem tocar na engine, coloque sua versão em `<KB_DATA_DIR>/templates/` e ela passa a valer para o seu vault.

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
├── kb/                     ← pacote Python / engine
│   ├── cli.py              ← CLI Typer (10 comandos + grupos jobs/discovery/handoff)
│   ├── client.py           ← wrapper OpenAI SDK + validação provider/modelo
│   ├── compile.py          ← raw → wiki via LLM (paralelo, validação de output, contexto de livro)
│   ├── templates/          ← templates de artigo/capítulo (override por vault)
│   ├── templates_loader.py ← resolução engine ↔ vault
│   ├── frontmatter.py      ← parser único de frontmatter YAML plano
│   ├── qa.py               ← Q&A com routing e wikilink traversal
│   ├── search.py           ← busca híbrida (keyword + BM25 + RRF)
│   ├── stats.py            ← agregação de métricas (dashboard)
│   ├── diff.py             ← git diff da wiki formatado
│   ├── heal.py             ← healing estocástico (validação + backup versionado)
│   ├── lint.py             ← auditoria via LLM
│   ├── archive.py          ← arquivamento de artigos stale/órfãos
│   ├── jobs.py             ← jobs canônicos + health gate
│   ├── claims.py           ← ciclo de vida de claims
│   ├── audit.py            ← trilha append-only de eventos de claims
│   ├── discovery.py        ← descoberta arXiv/news + ingestão agendável
│   ├── book_import.py      ← facade EPUB/PDF
│   ├── book_import_core.py ← parser EPUB (TOC, HTML→MD, metadata)
│   ├── book_import_pdf.py  ← extração PDF (PyMuPDF; OCR opcional)
│   ├── router.py           ← routing por fonte
│   ├── graph.py            ← wikilink traversal
│   ├── guardrails.py       ← detecção de conteúdo sensível
│   ├── web_ingest.py       ← URL → Markdown (proteção SSRF)
│   ├── state.py            ← persistência JSON
│   ├── outputs.py          ← file-back store
│   ├── fsutil.py           ← escrita atômica
│   ├── git.py              ← commit explícito
│   ├── handoff.py          ← handoff de sessão
│   ├── doc_gate.py         ← conformidade documental
│   ├── config.py           ← variáveis de ambiente e constantes
│   ├── cmds/               ← camada de execução (compile, qa)
│   ├── core/               ← tracking SQLite de execuções
│   ├── discover/           ← classificação declarativa de comandos
│   └── analytics/          ← saúde de claims + histórico de comandos
├── tests/                  ← 405 testes (92% de cobertura; gate de 85% no CI)
├── docs/                   ← documentação do produto
├── features/               ← SPECs por feature
└── examples/               ← exemplos neutros

# Corpus do usuário (fora do repositório)
<KB_DATA_DIR>/
├── raw/                    ← documentos fonte + books/
├── wiki/                   ← markdown compilado e versionado
├── outputs/                ← file-backs de QA
├── kb_state/               ← manifesto + knowledge + learnings + claims
└── templates/              ← (opcional) override dos templates
```

Design e evolução da arquitetura: [docs/architecture/SDD.md](docs/architecture/SDD.md)

## Convenções

- **Corpus separado:** `raw/`, `wiki/`, `outputs/`, `kb_state/` vivem em `KB_DATA_DIR`, fora do repositório
- **Frontmatter YAML:** cada artigo compilado inclui `title`, `topic`, `tags`, `source`, `translated_by`; `reviewed_at` é carimbado pelo heal
- **Templates:** estrutura do artigo definida em `kb/templates/`, customizável por vault
- **Tradução:** artigos compilados são gerados em português
- **Git:** writes no corpus ficam locais por padrão; use `--commit` para versionar na execução atual
- **LLM:** o LLM nunca escreve a wiki manualmente — tudo via CLI, com validação de output antes de persistir
- **Sensibilidade:** `--allow-sensitive` é opt-in explícito para bypass de guardrails
- **Spec Driven Development:** nenhuma mudança não trivial sem SPEC
- **Test Driven Development:** comportamento novo nasce RED antes de GREEN

## Testes e CI

405 testes (unit + integração), 92% de cobertura total. O CI roda pytest e ruff em Python 3.11, 3.12 e 3.13 a cada PR, com gate de cobertura em 85%.

```bash
pytest                                    # todos os testes
pytest --cov=kb --cov-report=html         # com cobertura HTML
pytest tests/unit/                        # apenas unitários
pytest tests/integration/                 # apenas integração
ruff check kb tests                       # lint

# Atalhos equivalentes
make lint
make test
make test-unit
make test-integration
make check
```

## Documentação

| Documento                                                            | Descrição                                  |
| -------------------------------------------------------------------- | ------------------------------------------ |
| [CONTEXT.md](CONTEXT.md)                                             | Contexto macro, princípios e fluxo SDD+TDD |
| [AGENTS.md](AGENTS.md)                                               | Convenções e contexto operacional          |
| [CONTRIBUTING.md](CONTRIBUTING.md)                                   | Regras de contribuição e gates             |
| [docs/architecture/SDD.md](docs/architecture/SDD.md)                 | Software Design Document                   |
| [docs/architecture/TDD.md](docs/architecture/TDD.md)                 | Convenções de teste                        |
| [docs/architecture/SPEC_FORMAT.md](docs/architecture/SPEC_FORMAT.md) | Formato de SPEC                            |
| [docs/API.md](docs/API.md)                                           | Referência CLI + Python API                |
| [docs/OBSIDIAN.md](docs/OBSIDIAN.md)                                 | Integração com Obsidian                    |
| [docs/adr/](docs/adr/)                                               | ADRs (0001–0016)                           |
| [SECURITY.md](SECURITY.md)                                           | Política de segurança                      |

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
| Lint / CI     | ruff + GitHub Actions (matriz 3.11–3.13)                  |

## Roadmap

- [x] Sistema base de ingestão e compilação
- [x] Importação de livros (EPUB/PDF) com metadata rica
- [x] Q&A com file-back e routing por fonte
- [x] Busca híbrida (keyword + BM25 + RRF)
- [x] Stochastic healing com backup e validação
- [x] Claims com ciclo de vida + trilha de auditoria
- [x] Jobs canônicos, health gate e discovery (arXiv/news)
- [x] Integração com Obsidian
- [x] Validação estruturada do output do LLM no compile
- [x] Templates de artigo com override por vault + compile ciente de livro
- [x] Dashboard de métricas (`kb stats`) e diff da wiki (`kb diff`)
- [x] CI com matriz 3.11–3.13 e gate de cobertura
- [ ] Multi-vault (SPEC pronta em `features/010-multi-vault-foundation/`)
- [ ] Embeddings + RAG híbrido

## Licença

GNU Affero General Public License v3.0 — veja [LICENSE](LICENSE).

O AGPL-3.0 garante que modificações e usos em rede (SaaS, APIs) permaneçam abertos: qualquer fork ou serviço exposto a usuários deve disponibilizar o código-fonte correspondente sob a mesma licença.
