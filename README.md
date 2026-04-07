# kb — LLM-powered Knowledge Base Engine

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-41%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

Engine de knowledge base mantida por LLM. Coleta documentos brutos, compila para wiki em markdown, responde perguntas contra a wiki, faz health checks e healing automático.

Inspirado na [proposta de Andrej Karpathy](https://karpathy.ai/) sobre sistemas de conhecimento assistidos por IA.

> Este repositório contém a **engine** (`kb`), testes e documentação. O **corpus/vault do usuário** deve ficar fora daqui, em um diretório próprio apontado por `KB_DATA_DIR`.

## Features

| Feature         | Descrição                                              | Comando                    |
| --------------- | ------------------------------------------------------ | -------------------------- |
| **Ingest**      | Adicionar documentos brutos à fila de processamento    | `kb ingest <arquivo>`      |
| **Book Import** | Importar EPUB/PDF textual em capítulos markdown        | `kb import-book <arquivo>` |
| **Compile**     | Transformar documentos raw em wiki estruturada via LLM + summary compilado | `kb compile`               |
| **Q&A**         | Perguntar com routing por fonte nativa (`wiki`, `raw`, `knowledge`, `learnings`) | `kb qa "pergunta"`         |
| **Search**      | Busca simples por palavras-chave na wiki               | `kb search "termo"`        |
| **Heal**        | Correção estocástica: links, stubs, timestamps         | `kb heal --n 10`           |
| **Lint**        | Health checks e auditoria da wiki                      | `kb lint`                  |
| **Jobs**        | Catálogo de rotinas agendáveis de manutenção           | `kb jobs list` / `kb jobs run compile` |

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
KB_MODEL=kimi-k2.5                          # opcional
KB_DATA_DIR=/caminho/para/seu/llm-wiki      # recomendado: fora deste repositório
```

`KB_DATA_DIR` aponta para o vault/corpus do usuário. Dentro dele, o `kb` espera encontrar ou criar:

```text
<KB_DATA_DIR>/
  raw/
  wiki/
  outputs/
  kb_state/
```

Veja também `.env.example`.

## Uso Rápido

```bash
# 1. Aponte para seu vault/corpus local
export KB_DATA_DIR=/caminho/para/seu/llm-wiki

# 2. Ingerir um documento neutro de exemplo
kb ingest examples/raw/getting-started.md

# 3. Compilar para wiki (usa LLM para estruturar)
kb compile

# 4. Fazer perguntas
kb qa "O que este corpus descreve?"

# 5. Arquivar resposta fora da wiki (recomendado no fluxo Obsidian)
kb qa "Resuma este corpus" -f --no-commit

# 6. Permitir explicitamente conteúdo sensível quando necessário
kb compile --allow-sensitive

# 7. Health check
kb heal --n 5 --no-commit
kb lint
```

## Obsidian

O frontend oficial recomendado é o Obsidian sobre o vault do usuário, e a integração operacional recomendada usa o plugin community [`obsidian-terminal`](https://github.com/polyipseity/obsidian-terminal).

### Setup recomendado

1. Configurar `KB_DATA_DIR` para o diretório do seu vault/corpus local
2. Abrir `<KB_DATA_DIR>/wiki` como vault no Obsidian
3. Instalar o plugin `obsidian-terminal`
4. Criar um profile integrado com:
   - Executable: `/bin/zsh` (ou `/bin/bash`)
   - Arguments: `--login`
5. Adicionar no shell um alias apontando para o binário do projeto:

```bash
alias kb='<raiz-do-repositorio>/.venv/bin/kb'
```

> Substitua `<raiz-do-repositorio>` pelo caminho absoluto do seu clone local.

6. No terminal integrado do Obsidian, entrar na raiz do projeto e rodar:

```bash
cd <raiz-do-repositorio>
kb --help
kb qa "Como implementar um orquestrador em meu workflow?" --allow-sensitive
```

Tutorial completo:

- [docs/OBSIDIAN.md](docs/OBSIDIAN.md)
- Plugin upstream: <https://github.com/polyipseity/obsidian-terminal>

## Arquitetura

```text
# Repositório da engine
kb/
├── kb/               ← engine/CLI principal
├── docs/             ← documentação do produto
├── tests/            ← testes unitários e integração
└── examples/         ← exemplos neutros de corpus/seed

# Corpus/vault do usuário (fora deste repositório)
<KB_DATA_DIR>/
├── raw/              ← documentos fonte
├── wiki/             ← markdown compilado
├── outputs/          ← file-backs de QA
└── kb_state/         ← manifesto/knowledge/learnings
```

## Convenções

- **Corpus do usuário:** `raw/`, `wiki/`, `outputs/` e `kb_state/` devem ficar preferencialmente fora do repositório principal via `KB_DATA_DIR`
- **Frontmatter YAML:** Cada artigo compilado inclui `title`, `topic`, `tags`, `source`, `reviewed_at`
- **Git:** writes no corpus local podem gerar commit automático, exceto quando `--no-commit` é usado explicitamente
- **LLM:** O LLM nunca escreve a wiki manualmente — tudo é via CLI
- **Sensibilidade:** operações com provider externo aceitam `--allow-sensitive` para bypass explícito da confirmação interativa

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
| [docs/OBSIDIAN.md](docs/OBSIDIAN.md)                                 | Guia oficial de uso com Obsidian     |
| [docs/adr/](docs/adr/)                                               | Architectural Decision Records       |

## Roadmap

- [x] Sistema base de ingestão e compilação
- [x] Importação de livros (EPUB/PDF)
- [x] Q&A com file-back
- [x] Stochastic healing
- [x] Suite de testes completa
- [ ] Multi-agent specialization (futuro)
- [x] Integração com Obsidian como frontend oficial recomendado (`obsidian-terminal`)
- [ ] Embeddings + RAG híbrido (futuro)
- [x] Modo no-commit para cenários sensíveis

## License

MIT
