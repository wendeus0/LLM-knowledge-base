# ANALYSIS_REPORT.md

Gerado em: 2026-04-04 | Branch: main | Commit: f66c3df

---

## 1. Visão Geral da Codebase

**Produto:** Knowledge base pessoal mantida por LLM. O usuário injeta documentos brutos (`raw/`) e o sistema produz uma wiki em markdown versionada com git.

**Padrão arquitetural:** CLI com módulos por função, sem camadas intermediárias (sem services/repositories). Tudo passa pelo `chat()` de `client.py`.

**Módulos principais:**

| Módulo | Responsabilidade |
|--------|-----------------|
| `config.py` | Env vars, paths raiz (`RAW_DIR`, `WIKI_DIR`) |
| `client.py` | Wrapper OpenAI SDK, validação de modelos OpenCode Go |
| `compile.py` | `raw/ → wiki/` via LLM, discovery recursiva |
| `qa.py` | Responde perguntas contra wiki; `--file-back` arquiva resposta |
| `search.py` | TF-IDF lexical simples em markdown |
| `heal.py` | Stochastic heal: corrige N artigos aleatórios |
| `lint.py` | Auditoria da wiki via LLM |
| `git.py` | Commit automático em todo write |
| `book_import_core.py` | Parser EPUB/PDF → capítulos Markdown (stdlib + defusedxml) |
| `book_import.py` | Facade sobre o core com `BookImportError` |
| `cli.py` | Typer CLI com 8 comandos |

**Fluxo central:**
```
raw/ → compile → wiki/ → qa → (resposta)
                wiki/ → qa --file-back → novo artigo em wiki/
EPUB/PDF → import-book → raw/books/ → [--compile] → wiki/
```

---

## 2. Fluxos Críticos

### Compile
1. `cli.compile` chama `discover_compile_targets(file)` — varredura recursiva em `raw/`
2. Para cada arquivo: `compile_file(path)` → `chat()` → extrai frontmatter → `_wiki_path(topic, title)` → grava MD → `commit()`
3. Finaliza com `update_index()` → regrava `_index.md` → `commit()`

### Import Book
1. `import_epub(source, target_dir)` → identifica `.epub` ou `.pdf`
2. EPUB: lê OPF via `defusedxml`, extrai spine + TOC, converte capítulos HTML → Markdown
3. PDF: regex sobre texto bruto, segmenta por padrão `Capítulo N`
4. Grava `.md` por capítulo + `metadata.json`
5. Com `--compile`: chama `compile_file()` para cada capítulo → wiki/

### QA
1. `search.find_relevant(question)` → TF-IDF simples em `wiki/**/*.md`
2. Constrói contexto com até 5 artigos mais relevantes
3. `chat()` responde com system prompt de Q&A
4. Se `--file-back`: segundo `chat()` gera artigo wiki → grava → `commit()`

---

## 3. Débitos Técnicos

### P0 — Bloqueia

| ID | Descrição | Localização |
|----|-----------|-------------|
| D1 | **Baseline quebrada sem .venv** — `python -m pytest` falha com `ModuleNotFoundError: No module named 'defusedxml'` porque usa `/usr/bin/python` sem as deps instaladas. AGENTS.md documenta o comando errado. | `AGENTS.md`, `.venv/` |

### P1 — Urgente

| ID | Descrição | Localização |
|----|-----------|-------------|
| D2 | **`config.py` explode no import** — `API_KEY = os.environ["KB_API_KEY"]` levanta `KeyError` sem mensagem útil quando `.env` não está configurado. Todo import de `kb.config` falha silenciosamente em ambientes sem `.env`. | `config.py:11` |
| D3 | **Teste anti-pattern** — `test_should_raise_clear_error_when_epub_is_invalid` usa `try/except/else` com `raise AssertionError` em vez de `pytest.raises`. Se a exceção for do tipo errado, o teste passa silenciosamente. | `tests/unit/test_book_import.py:79-90` |
| D4 | **`lint.py` importa `re` dentro de função** — `import re` na linha 29 de `lint_wiki()` em vez de no topo do módulo. Funciona, mas viola convenção e impacta legibilidade. | `lint.py:29` |

### P2 — Importante

| ID | Descrição | Localização |
|----|-----------|-------------|
| D5 | **Slug duplicado em `compile.py` e `qa.py`** — ambos fazem slug manual (`.lower().replace(" ", "-")` ou `re.sub`) sem normalizar acentos. `book_import_core.slugify()` já resolve isso mas não é reutilizado. | `compile.py:57`, `qa.py:75` |
| D6 | **`wiki/q.md` e arquivos de wiki não commitados** — `wiki/o-que---machine-learning.md`, `wiki/q.md`, `wiki/qual-diferen-a-xss.md` estão em `raw/` ou `wiki/` untracked. O projeto define que writes na wiki são auto-commitados, mas esses arquivos existem sem commit. | `git status` |
| D7 | **`raw/` não está em `.gitignore`** — documentos brutos (possivelmente sensíveis) ficam versionados junto com o código. Contradiz o achado M1 do SECURITY_AUDIT_REPORT. | `.gitignore` |
| D8 | **Sem `[tool.pytest.ini_options]`** — não há configuração de testpaths ou addopts no `pyproject.toml`. `pytest` descobre testes mas sem controle explícito de escopo. | `pyproject.toml` |

---

## 4. Saúde de Dependências

**Status geral:** DEP_OK em ambiente `.venv`, BROKEN em sistema global.

| Dep | Versão requerida | Instalada (.venv) | Instalada (sistema) | Risco |
|-----|-----------------|-------------------|---------------------|-------|
| `defusedxml` | `>=0.7` | ✓ | ✗ | **ALTO** — sem .venv, 9 testes falham |
| `typer` | `>=0.12` | ✓ (0.24.1) | ✓ | OK |
| `rich` | `>=13.0` | ✓ (14.3.3) | ✓ | OK |
| `python-dotenv` | `>=1.0` | ✓ (1.2.2) | ✓ | OK |
| `openai` | `>=1.0` (opcional `.[llm]`) | ✓ | ✗ | MÉDIO — compile/qa/heal/lint falham sem |
| `pytest` | `>=8.0` (dev) | ✓ | desconhecido | OK |
| `ruff` | `>=0.6` (dev) | ✓ | desconhecido | OK |

**Auditoria de CVEs:** não executada (sem ferramenta; ver recomendação L1 do SECURITY_AUDIT_REPORT).

**Env vars obrigatórias:**

| Var | Obrigatória | Default | Status |
|-----|------------|---------|--------|
| `KB_API_KEY` | Sim | — | Configurada em `.env` (não versionado) |
| `KB_BASE_URL` | Não | `https://opencode.ai/zen/go/v1` | Default OK |
| `KB_MODEL` | Não | `kimi-k2.5` | Default OK |

---

## 5. Cobertura de Testes

**Resultado com `.venv` ativo:** 59/59 passing (0.22s)  
**Resultado sem `.venv`:** 46/59 passing — 13 falhas por `ModuleNotFoundError: defusedxml`

| Módulo | Testes | Obs |
|--------|--------|-----|
| `book_import_core` + `book_import` | 9 unit + 5 integration | Cobertura rica: EPUB, PDF, TOC, XXE, dirty XHTML |
| `compile` | 7 unit | Mocks de LLM + git |
| `qa` | 5 unit | Mock de chat e search |
| `search` | 6 unit | |
| `heal` | 2 unit | |
| `lint` | 5 unit | |
| `client` | 4 unit | Validação OpenCode Go |
| Integration (heal, ingest/compile/qa) | 3 | |

**Gaps identificados:**
- `git.py` — zero testes diretos
- `config.py` — zero testes (falha em import sem `.env` não testada)
- `cli.py` (comandos `qa`, `heal`, `lint`, `ingest`) — sem testes de integração CLI
- PDF com segmentação por capítulo: coberto apenas no caso feliz simples

---

## 6. Oportunidades de Aprimoramento

| Prioridade | Oportunidade | Impacto |
|-----------|-------------|---------|
| P1 | Corrigir documentação de `python -m pytest` para exigir `.venv` | Evita falsos negativos na CI e onboarding |
| P1 | Tornar `KB_API_KEY` opcional com fallback gracioso | UX melhor — mensagem clara ao invés de traceback |
| P1 | Adicionar `pytest.ini_options` com `testpaths = ["tests"]` | Explícito e evita descoberta acidental |
| P2 | Extrair `slugify` como utilitário compartilhado | Remove duplicação em `compile.py` e `qa.py` |
| P2 | Adicionar `raw/` ao `.gitignore` (ou documentar policy explícita) | Alinhamento com SECURITY_AUDIT M1 |
| P2 | Adicionar testes CLI para `qa`, `heal`, `lint`, `ingest` | Cobertura de superfície pública |
| P2 | `git.py` mínimo de testes com subprocess mock | Garante que auto-commit não silencia erros inesperados |
| P3 | Mover `import re` de `lint.py:29` para topo do módulo | Convenção e clareza |

---

## 7. Próximos Passos Recomendados

1. **[IMEDIATO]** Corrigir D1: atualizar `AGENTS.md` para documentar `source .venv/bin/activate && python -m pytest` como comando canônico de testes.
2. **[IMEDIATO]** Adicionar `[tool.pytest.ini_options]` ao `pyproject.toml` para evitar execução acidental fora do venv.
3. **[P1]** Corrigir D2 em `config.py`: substituir `os.environ["KB_API_KEY"]` por `os.getenv(...)` com raise explicativo e lazy para operações LLM.
4. **[P1]** Corrigir D3 em `test_book_import.py:79-90`: usar `pytest.raises`.
5. **[P1]** Corrigir D4 em `lint.py:29`: mover `import re` para topo.
6. **[P2]** Decidir policy de `raw/` no git (versionado vs `.gitignore`) e documentar.
7. **[P2]** Commitar ou remover wiki files untracked (`wiki/q.md`, etc.).
8. **[P2]** Smoke test real com OpenCode Go (pendência do sprint anterior).
