# Arquitetura do kb

> Engine de knowledge base mantida por LLM

> **Nota de escopo:** este documento descreve a engine e pode usar `raw/`, `wiki/` e `outputs/` como nomes lógicos de diretórios. No modelo recomendado atual, esses diretórios vivem no `KB_DATA_DIR` do usuário, fora do repositório principal.

## 1. Visão Geral (C4 Model)

### Contexto (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Contexto Externo                                │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │  Usuário    │     │ Documentos  │     │   Livros    │                  │
│   │  (Dev)      │     │   (.md)     │     │(.epub/.pdf) │                  │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                  │
│          │                   │                   │                          │
│          │  kb <comando>     │   ingest          │   import-book            │
│          │                   │                   │                          │
│          └───────────────────┴───────────────────┘                          │
│                              │                                               │
│                              ▼                                               │
│   ┌─────────────────────────────────────────────────────────────┐          │
│   │                    Sistema kb (LLM-KB)                       │          │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │          │
│   │  │ Ingest  │  │ Compile │  │   QA    │  │  Heal   │        │          │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │          │
│   └─────────────────────────────────────────────────────────────┘          │
│                              │                                               │
│                              ▼                                               │
│   ┌─────────────────────────────────────────────────────────────┐          │
│   │                    OpenAI-Compatible API                     │          │
│   │              (OpenCode Go / OpenAI / Local)                  │          │
│   └─────────────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Containers (C4 Level 2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Sistema kb — Containers                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        CLI Typer (kb/cli.py)                         │   │
│  │   ingest │ import-book │ compile │ qa │ search │ heal │ lint         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐ │
│  │                                 ▼                                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│ │
│  │  │   Compile    │  │     QA       │  │    Heal      │  │   Lint     ││ │
│  │  │   Engine     │  │   Engine     │  │   Engine     │  │  Engine    ││ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘│ │
│  │           │               │               │               │          │ │
│  │           └───────────────┴───────────────┴───────────────┘          │ │
│  │                           │                                          │ │
│  │                    ┌────────────┐                                    │ │
│  │                    │   Client   │                                    │ │
│  │                    │   LLM      │                                    │ │
│  │                    └────────────┘                                    │ │
│  │                           │                                          │ │
│  └───────────────────────────┼──────────────────────────────────────────┘ │
│                              ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Armazenamento                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   raw/       │  │   wiki/      │  │    Git       │              │   │
│  │  │  (fonte)     │  │ (compilado)  │  │(versionado)  │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagrama de Fluxo de Dados

### Fluxo Principal: Ingest → Compile → Wiki

```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────┐
│ Usuário │────▶│  CLI    │────▶│   ingest    │────▶│    raw/     │────▶│         │
│         │     │  Typer  │     │  (copy)     │     │ (documento) │     │         │
└─────────┘     └─────────┘     └─────────────┘     └─────────────┘     │         │
                                                                        │         │
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────────┐     │  LLM    │
│   Git   │◀────│  commit │◀────│   compile   │◀────│   LLM API   │◀────│ Engine  │
│  Repo   │     │  auto   │     │  (markdown) │     │  (process)  │     │         │
└─────────┘     └─────────┘     └─────────────┘     └─────────────┘     │         │
                                              │                         │         │
                                              ▼                         └─────────┘
                                        ┌─────────────┐
                                        │    wiki/    │
                                        │ (markdown   │
                                        │  + frontmatter
                                        │  + wikilinks│
                                        └─────────────┘
```

### Fluxo de Importação de Livros

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Livro      │────▶│ book_import │────▶│ book_import │────▶│   Capítulos │
│ (.epub/.pdf)│     │  (CLI)      │     │  _core.py   │     │   Markdown  │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  metadata   │◀────│  metadata   │◀────│   raw/      │◀────│   Escrita   │
│   .json     │     │  (dict)     │     │  books/     │     │   em Disco  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Fluxo de Q&A

```
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌─────────────┐
│ Pergunta│────▶│   QA    │────▶│   search    │────▶│  wiki/      │
│ Usuário │     │  CLI    │     │ (relevância)│     │ (artigos)   │
└─────────┘     └─────────┘     └─────────────┘     └──────┬──────┘
                                                           │
┌─────────┐     ┌─────────┐     ┌─────────────┐     ┌──────┴──────┐
│ Usuário │◀────│  Rich   │◀────│    LLM      │◀────│   Contexto  │
│ (ver)   │     │ Markdown│     │  (resposta) │     │  (top_k)    │
└─────────┘     └─────────┘     └─────────────┘     └─────────────┘

[Opção --file-back]
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  file-back  │────▶│  LLM gera   │────▶│ outputs/    │
│   (rascunho)│     │   artigo    │     │ (padrão)    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    Git      │
                                        │   commit    │
                                        └─────────────┘
```

### Fluxo de Heal (Estocástico)

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  kb     │────▶│   Seleção   │────▶│   Amostra   │────▶│   wiki/     │
│ heal -n │     │  Aleatória  │     │   N files   │     │ (arquivos)  │
└─────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                               │
                        ┌──────────────────────────────────────┼──────┐
                        │                                      │      │
                        ▼                                      ▼      ▼
                ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                │   stub?     │────▶│   delete    │     │  healthy?   │
                │  (vazio)    │yes  │   arquivo   │no   │  (process)  │
                └─────────────┘     └─────────────┘     └──────┬──────┘
                                                               │
                                                               ▼
                        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                        │  git commit │◀────│  stamp      │◀────│    LLM      │
                        │  (batch)    │     │ reviewed_at │     │ (correções) │
                        └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 3. Descrição dos Fluxos

### 3.1 Ingest → Compile → Wiki

**Propósito:** Transformar documentos brutos em artigos wiki estruturados.

**Etapas:**

1. **Ingest** (`kb ingest <arquivo>`)
   - Copia arquivo para `raw/` (preserva original)
   - Suporta: `.md`, `.markdown`, `.txt`, `.rst`

2. **Compile** (`kb compile`)
   - Descobre arquivos em `raw/` (recursivo, incluindo `raw/books/`)
   - Envia conteúdo + metadados para LLM com prompt de sistema específico
   - LLM retorna markdown com frontmatter YAML
   - Salva em `wiki/<topic>/<slug>.md`
   - Commit automático: `feat(wiki): compile <arquivo> → <artigo>`

3. **Update Index** (automático)
   - Regenera `wiki/_index.md` listando todos os artigos
   - Commit automático: `chore(wiki): update _index.md`

**Frontmatter gerado:**

```yaml
---
title: <título>
topic: <topic-derivado-do-corpus|general>
tags: [tag1, tag2]
source: <nome do arquivo original>
---
```

### 3.2 Importação de Livros

**Propósito:** Converter livros EPUB/PDF em capítulos markdown individuais.

**Etapas:**

1. **Parse EPUB** (`book_import_core.py`)
   - Extrai `container.xml` → `content.opf` → manifest + spine
   - Parse NCX (toc) ou nav.xhtml para títulos de capítulos
   - Extrai HTML de cada capítulo

2. **Parse PDF** (`book_import_core.py`)
   - Extrai texto de operadores PDF (`Tj`, `TJ`)
   - Detecta capítulos por padrões de heading
   - Fallback: documento único se não segmentável

3. **Conversão HTML→Markdown**
   - `_MarkdownHTMLParser`: parser HTML customizado
   - Preserva: headings, listas, bold, italic
   - Remove: script, style tags

4. **Escrita**
   - Capítulos: `raw/books/<livro>/<NN>-<slug>.md`
   - Metadados: `raw/books/<livro>/metadata.json`

5. **Compile opcional** (`--compile`)
   - Compila cada capítulo para wiki/
   - Atualiza índice

### 3.3 Q&A Workflow

**Propósito:** Responder perguntas consultando a wiki.

**Etapas:**

1. **Busca** (`search.find_relevant`)
   - Tokeniza query em termos
   - Conta ocorrências em cada artigo da wiki
   - Retorna top_k mais relevantes

2. **Contexto**
   - Concatena conteúdo dos artigos relevantes
   - Formata para prompt do LLM

3. **Resposta** (`qa.answer`)
   - LLM gera resposta baseada no contexto
   - Cita fontes usando `[[wikilink]]`
   - Renderizado com Rich Markdown no CLI

4. **File-back opcional** (`qa.answer_and_file`)
   - LLM converte resposta em artigo wiki
   - Extrai topic/title do frontmatter gerado
   - Salva em `outputs/` por padrão; com `to_wiki=True`, salva em wiki/; commit só ocorre com ativação explícita

### 3.4 Heal Workflow

**Propósito:** Manutenção estocástica da wiki (escala para vaults grandes).

**Etapas:**

1. **Seleção aleatória**
   - Coleta todos os arquivos `.md` em wiki/
   - Amostra N arquivos aleatoriamente (`random.sample`)

2. **Por arquivo:**
   - **Stub detection:** Se conteúdo significativo < threshold → deleta
   - **LLM heal:** Envia artigo para correção
     - Adiciona wikilinks faltantes
     - Remove placeholders vazios
     - Sugere novos artigos (como comentário)
   - **Stamp:** Adiciona/atualiza `reviewed_at: YYYY-MM-DD`

3. **Batch commit opcional**
   - Se `--commit` estiver ativo, gera commit único para todos os arquivos modificados
   - Mensagem: `chore(heal): stochastic heal (N files)`

**Ações possíveis:**

- `healed`: correções aplicadas
- `deleted_stub`: artigo vazio removido
- `reviewed_no_changes`: apenas stamp atualizado

---

## 4. Componentes

### 4.1 Core Components

| Componente | Arquivo     | Responsabilidade                                         |
| ---------- | ----------- | -------------------------------------------------------- |
| **CLI**    | `cli.py`    | Interface Typer, orquestração de comandos, Rich UI       |
| **Config** | `config.py` | Constantes, paths, env vars, topics                      |
| **Client** | `client.py` | Wrapper OpenAI SDK, validação provider/model             |
| **Git**    | `git.py`    | Commit helper explícito, staging, mensagens padronizadas |

### 4.2 Feature Components

| Componente  | Arquivo      | Responsabilidade                                      |
| ----------- | ------------ | ----------------------------------------------------- |
| **Compile** | `compile.py` | Transforma raw/ → wiki/, gera frontmatter, wikilinks  |
| **QA**      | `qa.py`      | Busca + LLM para respostas, file-back opcional        |
| **Search**  | `search.py`  | TF-IDF simples (contagem), retorna artigos relevantes |
| **Heal**    | `heal.py`    | Manutenção estocástica, correções, stubs, stamps      |
| **Lint**    | `lint.py`    | Health checks LLM, wikilinks quebrados (local)        |

### 4.3 Book Import Components

| Componente      | Arquivo               | Responsabilidade                           |
| --------------- | --------------------- | ------------------------------------------ |
| **Book Import** | `book_import.py`      | Interface pública, defaults, erro handling |
| **Book Core**   | `book_import_core.py` | Parse EPUB/PDF, HTML→Markdown, escrita     |

### 4.4 Responsabilidades Detalhadas

#### `kb/cli.py`

- Define todos os comandos Typer
- Importa módulos sob demanda (lazy imports)
- Formata saída com Rich (Markdown, cores, ícones)

#### `kb/config.py`

- Paths base: `ROOT`, `RAW_DIR`, `WIKI_DIR`
- Config LLM: `API_KEY`, `BASE_URL`, `MODEL`
- Taxonomia runtime: `TOPICS`, `is_supported_topic()`, `wiki_topic_dir()`

#### `kb/client.py`

- `get_client()`: factory OpenAI com validação
- `chat()`: wrapper para completions com retry
- Validação OpenCode Go: modelos permitidos

#### `kb/compile.py`

- `discover_compile_targets()`: encontra arquivos compiláveis
- `compile_file()`: processa um arquivo via LLM
- `update_index()`: regenera `_index.md`
- Extensões suportadas: `.md`, `.markdown`, `.txt`, `.rst`

#### `kb/qa.py`

- `answer()`: consulta wiki, retorna resposta markdown
- `answer_and_file()`: responde + arquiva como artigo
- Sistema de prompts separados para cada modo

#### `kb/search.py`

- `find_relevant()`: retorna `list[Path]` para QA
- `search()`: retorna `list[dict]` com score + snippet
- Algoritmo: soma de contagens de termos (case-insensitive)

#### `kb/heal.py`

- `heal(n)`: processa N arquivos aleatórios
- `_is_stub()`: detecta artigos vazios
- `_stamp_reviewed()`: adiciona `reviewed_at` ao frontmatter
- Batch commit opcional ao final

#### `kb/lint.py`

- `lint_wiki()`: auditoria LLM da wiki
- Detecção local de wikilinks quebrados (regex)
- Relatório markdown com seções

#### `kb/git.py`

- `commit()`: stage + commit silencioso
- Ignora se não há mudanças
- Paths relativos ao ROOT

#### `kb/book_import.py`

- Interface pública: `import_epub()`, `extract_book_metadata()`
- Exports para reuso: `_write_chapters`, `_write_metadata`

#### `kb/book_import_core.py`

- Parse EPUB: XML seguro (defusedxml), ZIP handling
- Conversão HTML→Markdown: `_MarkdownHTMLParser`
- Detecção de capítulos: padrões de heading

#### `kb/book_import_pdf.py`

- Parse PDF: extração textual, OCR opcional e chunking
- Heurísticas de TOC para capítulos

---

## 5. Interfaces

### 5.1 CLI Typer

```bash
# Instalação
pip install -e .          # base
pip install -e .[llm]     # + OpenAI SDK

# Comandos
kb ingest <arquivo>                       # Copia para raw/
kb import-book <livro...> [--compile]     # EPUB/PDF → raw/books/
kb compile [alvo]                         # raw/ → wiki/ (arquivo, diretório ou nome de livro)
kb qa "pergunta" [-f]                     # Pergunta + file-back opcional
kb search "termo"                         # Busca keyword
kb heal -n 10                             # Heal estocástico
kb lint                                   # Health check
```

### 5.2 API Python

```python
# Config
from kb.config import RAW_DIR, WIKI_DIR, TOPICS, topic_prompt_options

# Client LLM
from kb.client import chat
response = chat(messages=[{"role": "user", "content": "..."}])

# Compile
from kb.compile import compile_file, discover_compile_targets
for target in discover_compile_targets():
    compile_file(target)

# QA
from kb.qa import answer, answer_and_file
response = answer("o que é X?")
response, path = answer_and_file("o que é X?")

# Search
from kb.search import find_relevant, search
paths = find_relevant("query", top_k=5)
results = search("query", top_k=10)

# Heal
from kb.heal import heal
log = heal(n=10)  # list[{"file": "...", "action": "..."}]

# Lint
from kb.lint import lint_wiki
report = lint_wiki()  # markdown string

# Git
from kb.git import commit
commit("msg", [path1, path2])

# Book Import
from kb.book_import import import_epub, extract_book_metadata
files, metadata = import_epub(Path("livro.epub"), output_dir)
```

### 5.3 Estrutura de Diretórios

```
kb/
├── raw/                    # Documentos fonte (não processados)
│   ├── doc1.md
│   └── books/              # Livros importados
│       └── livro/
│           ├── 01-intro.md
│           ├── 02-capitulo-2.md
│           └── metadata.json
│
├── wiki/                   # Markdown compilado, versionado
│   ├── _index.md           # Índice automático
│   ├── cybersecurity/
│   │   └── artigo.md
│   ├── ai/
│   ├── python/
│   └── typescript/
│
├── kb/                     # Pacote Python
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── client.py
│   ├── compile.py
│   ├── qa.py
│   ├── search.py
│   ├── heal.py
│   ├── lint.py
│   ├── git.py
│   ├── book_import.py
│   └── book_import_core.py
│
├── tests/                  # Testes pytest
│   ├── unit/
│   └── integration/
│
├── pyproject.toml
└── .env                    # KB_API_KEY, KB_BASE_URL, KB_MODEL
```

---

## 6. Decisões Arquiteturais

### 6.1 LLM como Compilador

**Decisão:** Usar LLM para transformar documentos brutos em markdown estruturado.

**Rationale:**

- Extrai tópicos, tags, conceitos automaticamente
- Gera wikilinks para conectar conhecimento
- Elimina necessidade de templates rígidos

**Trade-offs:**

- Latência proporcional à API
- Custo de tokens (mas wiki pessoal = volume baixo)
- Qualidade depende do modelo

### 6.2 Git como Sistema de Versionamento

**Decisão:** writes no corpus ficam locais por padrão; commit ocorre apenas quando o comando é executado com `--commit`.

**Rationale:**

- Histórico completo quando o usuário decide versionar a execução
- Rollback simples de alterações problemáticas
- Controle explícito sobre quando materializar audit trail em Git

**Trade-offs:**

- Menos rastreabilidade automática se o usuário não usar `--commit`
- Possíveis conflitos continuam mitigados por estratégia de append

### 6.3 Stochastic Heal

**Decisão:** Processar N arquivos aleatórios por execução.

**Rationale:**

- Escalabilidade: vaults grandes não travam
- Distribuição uniforme de manutenção
- Não requer track de estado

**Trade-offs:**

- Não garante que todos os arquivos sejam processados
- Múltiplas execuções necessárias para cobertura total

### 6.4 Busca Simples (TF Count)

**Decisão:** Algoritmo de busca = soma de contagens de termos.

**Rationale:**

- Sem dependências externas (embeddings, vector DB)
- Suficiente para wiki pessoal (< 1000 artigos)
- Latência instantânea

**Trade-offs:**

- Não captura semântica (sinônimos, contexto)
- Ranking simples (não BM25)
- Escalabilidade limitada

### 6.5 Estratégia de Conflito: Append/Update

**Decisão:** LLM apenas adiciona ou atualiza seções, nunca reescreve completamente.

**Rationale:**

- Reduz conflitos git
- Preserva edições manuais (embora não recomendado)
- Segue estratégia Pawel Huryn

**Trade-offs:**

- Lógica mais complexa em prompts
- Possível acúmulo de conteúdo obsoleto

### 6.6 Separação Book Import Core

**Decisão:** `book_import_core.py` separado de `book_import.py`.

**Rationale:**

- Reuso entre CLI e futuras interfaces
- Testabilidade isolada
- Possível extração para pacote separado

**Trade-offs:**

- Mais arquivos para manter
- API pública vs interna (convenção `_` prefix)

### 6.7 Lazy Imports

**Decisão:** Imports dentro de funções em CLI.

**Rationale:**

- CLI inicia rápido mesmo sem dependências LLM
- Permite uso de comandos básicos (ingest, search) sem OpenAI

**Trade-offs:**

- Código menos limpo
- Potencial overhead em chamadas repetidas

### 6.8 Type Hints Mínimos

**Decisão:** Type hints apenas onde crítico (config, cliente).

**Rationale:**

- Código mais legível
- Menos cerimônia
- Python 3.11+ moderno

**Trade-offs:**

- Menor suporte de IDE
- Não verificável com mypy

---

## 7. Diagrama de Dependências

```
                            ┌─────────────┐
                            │   Typer     │
                            │   (CLI)     │
                            └──────┬──────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  book_import  │◀──────▶│  book_import  │        │    search     │
│  (interface)  │        │    _core      │        │   (keyword)   │
└───────────────┘        │  (parsing)    │        └───────────────┘
                         └───────────────┘                │
                                │                         │
                                ▼                         ▼
                         ┌───────────────┐        ┌───────────────┐
                         │  defusedxml   │        │    path       │
                         │   zipfile     │        │   (stdlib)    │
                         └───────────────┘        └───────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Core Pipeline                                   │
│                                                                             │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌──────┐ │
│   │   CLI   │────▶│ compile │     │   qa    │     │  heal   │     │ lint │ │
│   │commands │     │         │     │         │     │         │     │      │ │
│   └─────────┘     └────┬────┘     └────┬────┘     └────┬────┘     └───┬──┘ │
│                        │               │               │              │    │
│                        └───────────────┼───────────────┘              │    │
│                                        │                              │    │
│                                        ▼                              │    │
│                              ┌─────────────────┐                      │    │
│                              │     client      │                      │    │
│                              │  (OpenAI SDK)   │                      │    │
│                              └────────┬────────┘                      │    │
│                                       │                               │    │
│                              ┌────────┴────────┐                      │    │
│                              │     config      │                      │    │
│                              │  (API_KEY, etc) │                      │    │
│                              └────────┬────────┘                      │    │
│                                       │                               │    │
│                        ┌──────────────┼──────────────┐                │    │
│                        │              │              │                │    │
│                        ▼              ▼              ▼                ▼    │
│                   ┌─────────┐   ┌─────────┐   ┌─────────┐        ┌──────┐  │
│                   │  raw/   │   │  wiki/  │   │   git   │        │search│  │
│                   │ (fonte) │   │(output) │   │(commit) │        │(local│  │
│                   └─────────┘   └─────────┘   └─────────┘        └──────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   config    │
                              │  (consts)   │
                              └──────┬──────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│     git       │          │    client     │          │     qa        │
│  (autocommit) │          │   (LLM API)   │          │  (respostas)  │
└───────────────┘          └───────────────┘          └───────┬───────┘
                                                              │
                                                              ▼
                                                    ┌─────────────────┐
                                                    │     search      │
                                                    │  (relevância)   │
                                                    └─────────────────┘

Legenda:
──────▶  Import/dependência direta
◀──────▶ Dependência bidirecional (compartilhamento)
```

### Matriz de Dependências

| Módulo             | Importa                             | É importado por                 |
| ------------------ | ----------------------------------- | ------------------------------- |
| `config`           | `os`, `pathlib`, `dotenv`           | Todos os outros módulos         |
| `git`              | `config`, `subprocess`              | `compile`, `qa`, `heal`         |
| `client`           | `config`, `openai`                  | `compile`, `qa`, `heal`, `lint` |
| `search`           | `config`                            | `qa`                            |
| `compile`          | `client`, `config`, `git`           | `cli`                           |
| `qa`               | `client`, `config`, `search`, `git` | `cli`                           |
| `heal`             | `client`, `config`, `git`           | `cli`                           |
| `lint`             | `client`, `config`                  | `cli`                           |
| `book_import`      | `book_import_core`, `config`        | `cli`                           |
| `book_import_core` | `defusedxml`, `zipfile`             | `book_import`                   |
| `cli`              | Todos acima (lazy)                  | — (entry point)                 |

---

## 8. Fluxos de Dados Resumidos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Fluxos de Dados                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. INGEST
   Arquivo ──▶ raw/ ──▶ (aguarda compile)

2. COMPILE
   raw/*.md ──▶ LLM ──▶ wiki/<topic>/*.md ──▶ git commit

3. IMPORT-BOOK
   .epub/.pdf ──▶ parse ──▶ raw/books/<livro>/*.md + metadata.json
                          └──▶ --compile ──▶ wiki/ ──▶ git commit

4. QA
   Pergunta ──▶ search ──▶ wiki/*.md ──▶ LLM ──▶ Resposta
                                         └──▶ --file-back ──▶ outputs/ ──▶ git commit

5. HEAL
   wiki/*.md ──▶ random.sample(N) ──▶ LLM/heurísticas ──▶ wiki/ ──▶ git commit

6. LINT
   wiki/*.md ──▶ heurísticas locais + LLM ──▶ Relatório markdown

7. SEARCH
   Query ──▶ keyword matching ──▶ Resultados ordenados
```

---

## 9. Convenções e Contratos

### Nomenclatura

- **Funções/variáveis:** `snake_case`
- **Classes:** `PascalCase`
- **Constantes:** `UPPER_CASE`
- **Privados:** `_prefix`

### Git Commits

- Format: `<tipo>(<escopo>): <descrição>`
- Tipos: `feat`, `chore`
- Mensagens padrão para operações automáticas

### Frontmatter YAML

```yaml
---
title: string
topic: topic-derivado-do-corpus|general
tags: [string]
source: string
reviewed_at: YYYY-MM-DD # adicionado por heal
---
```

### Wikilinks

- Formato: `[[conceito]]`
- Resolução: case-insensitive, slug matching
- Geração automática em compile/qa

---

## 10. Extensibilidade

### Novos Comandos CLI

Adicionar em `cli.py`:

```python
@app.command()
def novo_comando(arg: str):
    """Descrição."""
    from kb.novo_modulo import funcao
    funcao(arg)
```

### Novos Topics

`TOPICS` agora pode ser configurado por `KB_TOPICS`, preservando a lista histórica como default. `general` segue como fallback implícito fora da taxonomia configurável.

### Novos Formatos de Importação

Extender `book_import_core.py`:

```python
def _extract_chapters_from_format(source: Path, ...) -> tuple[list[dict], dict]:
    # Implementar parser
    pass
```

### Integração Obsidian

- `<KB_DATA_DIR>/wiki` é compatível com vault Obsidian
- Wikilinks nativos (`[[...]]`)
- Frontmatter YAML padrão
- `_index.md` como MOC (Map of Content)
