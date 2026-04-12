# API do kb

Documentação completa da API pública da engine de knowledge base.

> **Nota de escopo:** `raw/`, `wiki/`, `outputs/` e `kb_state/` são diretórios lógicos do corpus do usuário. No modelo recomendado atual, eles vivem em `KB_DATA_DIR`, fora do repositório principal.

---

## Índice

1. [CLI](#cli)
2. [API Python](#api-python)
3. [Integração Programática](#integração-programática)
4. [Códigos de Retorno](#códigos-de-retorno)
5. [Variáveis de Ambiente](#variáveis-de-ambiente)

---

## CLI

### Uso Geral

```bash
kb [COMANDO] [OPÇÕES]
```

### Comandos

#### `kb ingest`

Copia um arquivo para o diretório `raw/`.

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição                                  |
| --------- | ---- | ----------- | ------------------------------------------ |
| `path`    | Path | Sim         | Caminho do arquivo para adicionar a `raw/` |

**Exemplo:**

```bash
kb ingest documentos/notas.md
kb ingest /home/user/docs/artigo.txt
```

**Retorno:**

- Sucesso: mensagem `Adicionado: raw/<nome_do_arquivo>`
- Código: `0`

---

#### `kb import-book`

Importa um ou mais livros EPUB ou PDF textual para `raw/books/` em arquivos Markdown por capítulo.

**Parâmetros:**

| Parâmetro         | Tipo         | Obrigatório | Padrão             | Descrição                                           |
| ----------------- | ------------ | ----------- | ------------------ | --------------------------------------------------- |
| `paths`           | `List[Path]` | Sim         | -                  | Um ou mais arquivos EPUB/PDF textual                |
| `--output`        | Path         | Não         | `raw/books/<slug>` | Diretório de saída; ignorado com múltiplos arquivos |
| `--compile`       | Flag         | Não         | `False`            | Compilar os capítulos importados após a importação  |
| `--ocr`           | Flag         | Não         | `False`            | Ativa OCR para PDFs de scan ou com texto corrompido |
| `--force`         | Flag         | Não         | `False`            | Reimporta livros já existentes em `raw/books/`      |
| `--workers`, `-j` | int          | Não         | `4`                | Número de livros processados em paralelo            |
| `--chunk-pages`   | int          | Não         | `15`               | Páginas por chunk no fallback de PDFs sem TOC       |

**Exemplo:**

```bash
# Importar EPUB
kb import-book livros/python.epub

# Importar com diretório específico
kb import-book livros/ia.pdf --output raw/books/inteligencia-artificial

# Importar múltiplos livros em paralelo
kb import-book livros/python.epub livros/ia.pdf -j 2

# Importar PDF escaneado com OCR
kb import-book livros/scan.pdf --ocr --chunk-pages 10

# Importar e compilar automaticamente
kb import-book livros/clean-code.epub --compile
```

**Retorno:**

- Sucesso: `<N> capítulos importados em <caminho> (metadata: metadata.json)`
- Erro: código `1` com mensagem descritiva

---

#### `kb compile`

Compila documentos de `raw/` para a wiki em Markdown usando LLM.

**Parâmetros:**

| Parâmetro           | Tipo | Obrigatório | Padrão         | Descrição                                                |
| ------------------- | ---- | ----------- | -------------- | -------------------------------------------------------- |
| `target`            | str  | Não         | `None` (todos) | Arquivo, diretório ou nome de livro já importado         |
| `--update-index`    | Flag | Não         | `True`         | Atualizar `_index.md` após compilar                      |
| `--allow-sensitive` | Flag | Não         | `False`        | Permite envio explícito de conteúdo sensível ao provider |
| `--no-commit`       | Flag | Não         | `False`        | Escreve localmente sem criar commit git                  |

**Exemplo:**

```bash
# Compilar todos os arquivos em raw/
kb compile

# Compilar arquivo específico
kb compile raw/notas-reuniao.md

# Compilar um diretório importado em raw/books/
kb compile raw/books/mathematics-for-machine-learning

# Compilar por nome parcial do livro
kb compile "Mathematics for Machine Learning"

# Compilar sem atualizar índice
kb compile --no-update-index
```

**Retorno:**

- Sucesso: lista de arquivos compilados com caminhos
- Aviso: `[yellow]Nenhum arquivo em raw/` (código `0`)

---

#### `kb qa`

Responde uma pergunta consultando a wiki.

**Parâmetros:**

| Parâmetro           | Tipo | Obrigatório | Padrão  | Descrição                                  |
| ------------------- | ---- | ----------- | ------- | ------------------------------------------ |
| `question`          | str  | Sim         | -       | Pergunta para a knowledge base             |
| `--file-back`, `-f` | Flag | Não         | `False` | Arquivar resposta em `outputs/` por padrão |

**Exemplo:**

```bash
# Pergunta simples
kb qa "Quais são as principais vulnerabilidades OWASP?"

# Pergunta e arquivo a resposta
kb qa "Como funciona o pattern Singleton?" --file-back
```

**Retorno:**

- Sucesso: resposta em Markdown
- Com `--file-back`: exibe caminho do arquivo salvo

---

#### `kb search`

Busca artigos na wiki por palavra-chave.

**Parâmetros:**

| Parâmetro | Tipo | Obrigatório | Descrição       |
| --------- | ---- | ----------- | --------------- |
| `query`   | str  | Sim         | Termos de busca |

**Exemplo:**

```bash
kb search "async"
kb search docker
```

**Retorno:**

- Sucesso: lista de resultados com score e snippet
- Sem resultados: `[yellow]Nenhum resultado encontrado.` (código `0`)

**Formato do resultado:**

```
<nome_do_arquivo> (<caminho_relativo>) score=<número>
  <trecho encontrado>
```

---

#### `kb lint`

Executa health checks LLM sobre a wiki (relatório apenas).

**Parâmetros:**

Nenhum.

**Exemplo:**

```bash
kb lint
```

**Retorno:**

- Sucesso: relatório Markdown com:
  - Inconsistências entre artigos
  - Dados ausentes
  - Wikilinks quebrados
  - Oportunidades de novos artigos
  - Sugestões de perguntas

---

#### `kb heal`

Heal estocástico: processa N artigos aleatórios, corrige links, remove stubs, atualiza `reviewed_at`.

**Parâmetros:**

| Parâmetro   | Tipo | Obrigatório | Padrão | Descrição                                 |
| ----------- | ---- | ----------- | ------ | ----------------------------------------- |
| `--n`, `-n` | int  | Não         | `10`   | Número de arquivos aleatórios a processar |

**Exemplo:**

```bash
# Heal padrão (10 arquivos)
kb heal

# Heal com 20 arquivos
kb heal --n 20
```

**Retorno:**

- Sucesso: lista de ações realizadas com ícones:
  - `✓` (green): arquivo curado (`healed`)
  - `✗` (red): stub deletado (`deleted_stub`)
  - `·` (dim): revisado sem mudanças (`reviewed_no_changes`)

---

## API Python

### Configuração (`kb.config`)

```python
from kb.config import RAW_DIR, WIKI_DIR, API_KEY, BASE_URL, MODEL, TOPICS
```

**Constantes:**

| Nome          | Tipo      | Descrição                                      |
| ------------- | --------- | ---------------------------------------------- |
| `ROOT`        | Path      | Raiz do projeto                                |
| `DATA_DIR`    | Path      | Diretório do corpus do usuário (`KB_DATA_DIR`) |
| `RAW_DIR`     | Path      | `raw/` - documentos fonte                      |
| `WIKI_DIR`    | Path      | `wiki/` - markdown compilado                   |
| `OUTPUTS_DIR` | Path      | `outputs/` - file-backs de QA                  |
| `STATE_DIR`   | Path      | `kb_state/` - manifesto/knowledge/learnings    |
| `API_KEY`     | str       | KB_API_KEY do .env                             |
| `BASE_URL`    | str       | Endpoint LLM (padrão: opencode.ai)             |
| `MODEL`       | str       | Modelo LLM (padrão: kimi-k2.5)                 |
| `TOPICS`      | list[str] | Tópicos suportados atualmente                  |

---

### Cliente LLM (`kb.client`)

```python
from kb.client import get_client, chat, validate_provider_model_compatibility
```

#### `get_client()`

Retorna uma instância do cliente OpenAI configurada.

**Retorno:** `OpenAI`

**Exceções:**

- `RuntimeError`: KB_API_KEY não definida
- `RuntimeError`: Dependência `openai` não instalada

---

#### `chat(messages, model=None, **kwargs)`

Envia mensagens para o LLM e retorna a resposta.

**Parâmetros:**

| Parâmetro  | Tipo       | Padrão           | Descrição                            |
| ---------- | ---------- | ---------------- | ------------------------------------ |
| `messages` | list[dict] | -                | Lista de mensagens no formato OpenAI |
| `model`    | str        | `MODEL` (config) | Modelo a usar                        |
| `**kwargs` | -          | -                | Argumentos adicionais para a API     |

**Retorno:** `str` - conteúdo da resposta

**Exceções:**

- `ValueError`: Modelo incompatível com OpenCode Go

---

#### `validate_provider_model_compatibility(base_url, model)`

Valida compatibilidade de modelo com o provedor.

**Modelos suportados para OpenCode Go:**

- `kimi-k2.5`
- `minimax-2.7`
- `glm-5`

---

### Compilação (`kb.compile`)

```python
from kb.compile import compile_file, discover_compile_targets, update_index
```

#### `compile_file(raw_path)`

Compila um documento bruto para a wiki.

**Parâmetros:**

| Parâmetro  | Tipo | Descrição                    |
| ---------- | ---- | ---------------------------- |
| `raw_path` | Path | Caminho do arquivo em `raw/` |

**Retorno:** `Path` - caminho do arquivo compilado

**Efeitos colaterais:**

- Escreve arquivo em `wiki/` do corpus do usuário
- Faz commit git automático

---

#### `discover_compile_targets(base=None)`

Descobre arquivos elegíveis para compilação.

**Parâmetros:**

| Parâmetro | Tipo | Padrão    | Descrição                 |
| --------- | ---- | --------- | ------------------------- |
| `base`    | Path | `RAW_DIR` | Diretório ou arquivo base |

**Retorno:** `list[Path]` - arquivos encontrados

**Extensões suportadas:** `.md`, `.markdown`, `.txt`, `.rst`

---

#### `update_index()`

Regenera `wiki/_index.md` listando todos os artigos.

**Retorno:** `None`

**Efeitos colaterais:**

- Escreve `wiki/_index.md`
- Faz commit git automático

---

### Q&A (`kb.qa`)

```python
from kb.qa import answer, answer_and_file
```

#### `answer(question, top_k=5)`

Responde uma pergunta consultando a wiki.

**Parâmetros:**

| Parâmetro  | Tipo | Padrão | Descrição                                 |
| ---------- | ---- | ------ | ----------------------------------------- |
| `question` | str  | -      | Pergunta a responder                      |
| `top_k`    | int  | `5`    | Número de artigos relevantes a considerar |

**Retorno:** `str` - resposta em Markdown

---

#### `answer_and_file(question, top_k=5)`

Responde e arquiva a resposta na wiki.

**Parâmetros:**

| Parâmetro  | Tipo | Padrão | Descrição                    |
| ---------- | ---- | ------ | ---------------------------- |
| `question` | str  | -      | Pergunta a responder         |
| `top_k`    | int  | `5`    | Número de artigos relevantes |

**Retorno:** `tuple[str, Path | None]` - (resposta, caminho do arquivo salvo)

**Efeitos colaterais:**

- Escreve arquivo em `outputs/` por padrão, ou em `wiki/` com `to_wiki=True`
- Faz commit git automático, salvo com `no_commit=True`

---

### Busca (`kb.search`)

```python
from kb.search import search, find_relevant
```

#### `search(query, top_k=10)`

Busca artigos na wiki por palavra-chave.

**Parâmetros:**

| Parâmetro | Tipo | Padrão | Descrição            |
| --------- | ---- | ------ | -------------------- |
| `query`   | str  | -      | Termos de busca      |
| `top_k`   | int  | `10`   | Máximo de resultados |

**Retorno:** `list[dict]` com chaves:

- `path`: Path - caminho do arquivo
- `score`: int - pontuação de relevância
- `snippet`: str - trecho contendo os termos

---

#### `find_relevant(query, top_k=5)`

Retorna artigos mais relevantes (para uso interno do Q&A).

**Retorno:** `list[Path]` - caminhos dos artigos

---

### Git helper (`kb.git`)

```python
from kb.git import commit
```

#### `commit(message, paths, enabled=True)`

Stageia paths relativos e cria commit quando houver mudanças staged.

**Parâmetros:**

| Parâmetro | Tipo | Padrão | Descrição |
| --------- | ---- | ------ | --------- |
| `message` | str | - | Mensagem de commit |
| `paths` | list[Path] | - | Arquivos a serem adicionados via `git add` |
| `enabled` | bool | `True` | Quando `False`, não executa side effects |

**Comportamento operacional:**

- Idempotente quando não há mudanças staged (`git diff --cached --quiet`)
- Suprime falhas de git indisponível sem quebrar o fluxo principal

---

### Heal (`kb.heal`)

```python
from kb.heal import heal
```

#### `heal(n=10)`

Processa N arquivos aleatórios da wiki.

**Parâmetros:**

| Parâmetro | Tipo | Padrão | Descrição                      |
| --------- | ---- | ------ | ------------------------------ |
| `n`       | int  | `10`   | Número de arquivos a processar |

**Retorno:** `list[dict]` - log de ações com chaves:

- `file`: str - nome do arquivo
- `action`: str - `healed`, `deleted_stub`, `reviewed_no_changes`

**Efeitos colaterais:**

- Modifica/deleta arquivos em `wiki/`
- Faz commit git automático

---

### Lint (`kb.lint`)

```python
from kb.lint import lint_wiki
```

#### `lint_wiki()`

Executa health checks sobre a wiki.

**Retorno:** `str` - relatório em Markdown

---

### Importação de Livros (`kb.book_import`)

```python
from kb.book_import import (
    import_epub,
    default_output_dir,
    extract_book_metadata,
    BookImportError,
)
```

#### `import_epub(source, output_dir=None)`

Importa EPUB/PDF para capítulos Markdown.

**Parâmetros:**

| Parâmetro    | Tipo | Padrão             | Descrição           |
| ------------ | ---- | ------------------ | ------------------- |
| `source`     | Path | -                  | Arquivo EPUB ou PDF |
| `output_dir` | Path | `raw/books/<slug>` | Diretório de saída  |

**Retorno:** `tuple[list[Path], Path]` - (arquivos de capítulo, metadata.json)

**Exceções:**

- `BookImportError`: Erro na importação

---

#### `default_output_dir(source)`

Retorna diretório padrão para importação.

**Retorno:** `Path` - `raw/books/<slug_do_nome>`

---

#### `extract_book_metadata(source)`

Extrai metadados de um livro.

**Retorno:** `dict` com `title`, `author`, `language`

---

### Núcleo de Importação (`kb.book_import_core`)

Funções de baixo nível para importação:

```python
from kb.book_import_core import (
    convert_book,
    write_chapters,
    write_metadata,
    html_to_markdown,
    slugify,
    build_chapter_filename,
    BookConversionError,
)
```

---

### Git (`kb.git`)

```python
from kb.git import commit
```

#### `commit(message, paths)`

Stage paths e commita silenciosamente.

**Parâmetros:**

| Parâmetro | Tipo       | Descrição           |
| --------- | ---------- | ------------------- |
| `message` | str        | Mensagem do commit  |
| `paths`   | list[Path] | Arquivos a commitar |

---

## Integração Programática

### Exemplo 1: Pipeline de Ingestão

```python
from pathlib import Path
from kb.config import RAW_DIR
from kb.compile import compile_file, discover_compile_targets, update_index

# Adicionar documento
source = Path("documentos/meu-artigo.md")
dest = RAW_DIR / source.name
dest.write_bytes(source.read_bytes())

# Compilar
for target in discover_compile_targets():
    compiled = compile_file(target)
    print(f"Compilado: {compiled}")

update_index()
```

### Exemplo 2: Sistema de Q&A Customizado

```python
from kb.qa import answer
from kb.search import search

# Buscar primeiro
results = search("async runtime", top_k=3)
for r in results:
    print(f"{r['path'].name}: score={r['score']}")

# Responder pergunta
resposta = answer("Como funciona este corpus?", top_k=5)
print(resposta)
```

### Exemplo 3: Manutenção Programática

```python
from kb.heal import heal
from kb.lint import lint_wiki

# Ver saúde da wiki
relatorio = lint_wiki()
print(relatorio)

# Curar 5 arquivos
log = heal(n=5)
for entry in log:
    print(f"{entry['file']}: {entry['action']}")
```

### Exemplo 4: Importação em Lote

```python
from pathlib import Path
from kb.book_import import import_epub

livros_dir = Path("livros")
for livro in livros_dir.glob("*.epub"):
    try:
        capitulos, metadata = import_epub(livro)
        print(f"{livro.name}: {len(capitulos)} capítulos importados")
    except Exception as e:
        print(f"Erro em {livro.name}: {e}")
```

### Exemplo 5: Uso Direto do Cliente LLM

```python
from kb.client import chat

resposta = chat(
    messages=[
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Explique o que é uma knowledge base."},
    ],
    model="kimi-k2.5",
    temperature=0.7,
)
print(resposta)
```

---

## Códigos de Retorno

### CLI

| Código | Significado      | Comandos      |
| ------ | ---------------- | ------------- |
| `0`    | Sucesso          | Todos         |
| `1`    | Erro de execução | `import-book` |

### Comportamento por Comando

| Comando       | Sucesso          | Aviso                | Erro           |
| ------------- | ---------------- | -------------------- | -------------- |
| `ingest`      | `0` + mensagem   | -                    | Exceção Python |
| `import-book` | `0` + contagem   | -                    | `1` + mensagem |
| `compile`     | `0` + lista      | `0` + aviso          | Exceção Python |
| `qa`          | `0` + resposta   | -                    | Exceção Python |
| `search`      | `0` + resultados | `0` + sem resultados | -              |
| `lint`        | `0` + relatório  | -                    | Exceção Python |
| `heal`        | `0` + log        | `0` + wiki vazia     | -              |

### Exceções Python

| Exceção               | Módulo             | Causa                                     |
| --------------------- | ------------------ | ----------------------------------------- |
| `RuntimeError`        | `client`           | API key não definida, dependência ausente |
| `ValueError`          | `client`           | Modelo incompatível com provedor          |
| `BookImportError`     | `book_import`      | Erro na importação de livro               |
| `BookConversionError` | `book_import_core` | Erro de conversão de formato              |

---

## Variáveis de Ambiente

### Obrigatórias

| Variável     | Descrição                  | Exemplo  |
| ------------ | -------------------------- | -------- |
| `KB_API_KEY` | API key para acesso ao LLM | `sk-...` |

### Opcionais

| Variável         | Padrão                          | Descrição                               |
| ---------------- | ------------------------------- | --------------------------------------- |
| `KB_BASE_URL`    | `https://opencode.ai/zen/go/v1` | Endpoint da API LLM                     |
| `KB_MODEL`       | `kimi-k2.5`                     | Modelo padrão a usar                    |
| `KB_DATA_DIR`    | `ROOT`                          | Diretório base do corpus do usuário     |
| `KB_RAW_DIR`     | `KB_DATA_DIR/raw`               | Override opcional para documentos fonte |
| `KB_WIKI_DIR`    | `KB_DATA_DIR/wiki`              | Override opcional para wiki compilada   |
| `KB_OUTPUTS_DIR` | `KB_DATA_DIR/outputs`           | Override opcional para file-backs de QA |
| `KB_STATE_DIR`   | `KB_DATA_DIR/kb_state`          | Override opcional para manifesto/estado |

### Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto:

```bash
KB_API_KEY=sua-chave-aqui
KB_BASE_URL=https://opencode.ai/zen/go/v1
KB_MODEL=kimi-k2.5
KB_DATA_DIR=/caminho/para/seu/llm-wiki
```

### Detecção

As variáveis são carregadas automaticamente via `python-dotenv` no módulo `kb.config`.

---

## Estrutura de Diretórios

```
<KB_DATA_DIR>/
├── raw/              # Documentos fonte (não processados)
│   └── books/        # Livros importados
├── wiki/             # Markdown compilado, versionado
│   ├── _index.md     # Índice automático
│   ├── topic-a/
│   ├── topic-b/
│   └── summaries/
├── outputs/          # File-backs de QA
├── kb_state/         # Manifesto, knowledge, learnings
└── (repo kb)         # Engine e pacote Python
```

---

## Frontmatter YAML

Todo arquivo wiki gerado inclui frontmatter:

```yaml
---
title: Título do Artigo
topic: general
tags: [tag1, tag2]
source: nome-do-arquivo-original.md
reviewed_at: 2024-01-15
---
```

**Campos:**

- `title`: Título do artigo
- `topic`: Tópico principal derivado do corpus (ou `general`)
- `tags`: Lista de tags
- `source`: Arquivo fonte original
- `reviewed_at`: Data da última revisão (adicionado pelo heal)

---

## Wikilinks

Use wikilinks para referenciar outros artigos:

```markdown
Veja também [[Runtime Assíncrono]] para mais detalhes.

Conceitos relacionados:

- [[Threading]]
- [[Concurrency]]
```

Links quebrados são detectados por `kb lint`.
