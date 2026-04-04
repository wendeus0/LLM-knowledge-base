# kb — LLM-powered Personal Knowledge Base

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-41%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

Sistema de knowledge base pessoal mantido por LLM. Coleta documentos brutos, compila para wiki em markdown, responde perguntas contra a wiki, faz health checks e healing automático.

Inspirado na [proposta de Andrej Karpathy](https://karpathy.ai/) sobre sistemas de conhecimento assistidos por IA.

## Features

| Feature         | Descrição                                              | Comando                    |
| --------------- | ------------------------------------------------------ | -------------------------- |
| **Ingest**      | Adicionar documentos brutos à fila de processamento    | `kb ingest <arquivo>`      |
| **Book Import** | Importar EPUB/PDF textual em capítulos markdown        | `kb import-book <arquivo>` |
| **Compile**     | Transformar documentos raw em wiki estruturada via LLM | `kb compile`               |
| **Q&A**         | Perguntar contra a wiki com contexto inteligente       | `kb qa "pergunta"`         |
| **Search**      | Busca simples por palavras-chave na wiki               | `kb search "termo"`        |
| **Heal**        | Correção estocástica: links, stubs, timestamps         | `kb heal --n 10`           |
| **Lint**        | Health checks e auditoria da wiki                      | `kb lint`                  |

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd kb

# Instalar dependências base
pip install -e .

# Instalar com suporte a LLM (compile, qa, heal, lint)
pip install -e ".[llm]"

# Instalar dependências de desenvolvimento
pip install -e ".[dev]"
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```bash
KB_API_KEY=sua_api_key_aqui
KB_BASE_URL=https://opencode.ai/zen/go/v1  # opcional
KB_MODEL=opencode-go/kimi-k2.5              # opcional
```

## Uso Rápido

```bash
# 1. Ingerir um documento
kb ingest docs/artigo-sobre-xss.md

# 2. Compilar para wiki (usa LLM para estruturar)
kb compile

# 3. Fazer perguntas
kb qa "O que é XSS e como prevenir?"

# 4. Arquivar resposta na wiki
kb qa "Explique CSRF" -f

# 5. Health check
kb heal --n 5
kb lint
```

## Arquitetura

```
kb/
├── raw/              ← documentos fonte (não processados)
│   └── books/        ← livros importados (EPUB/PDF)
├── wiki/             ← markdown compilado, versionado
│   ├── _index.md     ← índice automático
│   ├── cybersecurity/
│   ├── ai/
│   ├── python/
│   └── typescript/
├── kb/               ← pacote Python
│   ├── cli.py        ← interface Typer
│   ├── client.py     ← wrapper OpenAI SDK
│   ├── compile.py    ← raw → wiki (LLM)
│   ├── qa.py         ← Q&A + file-back
│   ├── search.py     ← busca por keywords
│   ├── heal.py       ← stochastic healing
│   ├── lint.py       ← health checks
│   ├── book_import_core.py  # núcleo de importação
│   ├── config.py     ← constantes e env
│   └── git.py        ← commits automáticos
└── tests/            ← testes unitários e integração
```

## Convenções

- **Topics:** `cybersecurity`, `ai`, `python`, `typescript`
- **Frontmatter YAML:** Cada artigo da wiki inclui `title`, `topic`, `tags`, `source`, `reviewed_at`
- **Git:** Todo write na wiki gera commit automático
- **LLM:** O LLM nunca escreve a wiki manualmente — tudo é via CLI

## Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=kb --cov-report=html

# Apenas unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/

# Lint
ruff check kb
```

## Documentação

| Documento                                                            | Descrição                            |
| -------------------------------------------------------------------- | ------------------------------------ |
| [AGENTS.md](AGENTS.md)                                               | Convenções e contexto do projeto     |
| [docs/architecture/TDD.md](docs/architecture/TDD.md)                 | Convenções de teste                  |
| [docs/architecture/SPEC_FORMAT.md](docs/architecture/SPEC_FORMAT.md) | Formato de especificação de features |
| [docs/adr/](docs/adr/)                                               | Architectural Decision Records       |

## Roadmap

- [x] Sistema base de ingestão e compilação
- [x] Importação de livros (EPUB/PDF)
- [x] Q&A com file-back
- [x] Stochastic healing
- [x] Suite de testes completa
- [ ] Integração com Obsidian como frontend
- [ ] Expansão de cobertura de testes
- [ ] Suporte a mais formatos de entrada

## License

MIT
