# kb — Plano de Robustez do Core + Template de Artigo + Backlog

> **Para workers agênticos:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar task a task. Passos usam checkboxes (`- [ ]`).
> Este arquivo é a cópia de trabalho canônica do plano — mantenha-o atualizado conforme as tasks avançam.

**Goal:** Blindar o caminho crítico ingest→compile→qa→heal, introduzir o template de artigo como artefato core que guia a estrutura do output do LLM, cortar código morto, fechar gaps de CI/teste e entregar o backlog (stats, diff, SPEC multi-vault).

**Architecture:** A engine (`kb/`) permanece com a mesma topologia; as mudanças são: (1) um módulo único de frontmatter substituindo 4 parsers ad-hoc; (2) validação estruturada do output do LLM antes de persistir (compile e heal); (3) templates de artigo versionados na engine com override por vault; (4) compile passa a consumir `metadata.json` dos livros para dar contexto ao prompt.

**Tech Stack:** Python 3.11+, Typer, Rich, pytest, ruff, GitHub Actions. LLM via OpenAI SDK (opcional, sempre mockado em teste).

---

## Open questions (responder antes ou durante execução — não bloqueiam as Fases 0–2)

1. **Versão/release:** há ~3 features mergeadas desde 0.4.0 e o CHANGELOG está estagnado. Subimos para **0.5.0** ao final da Fase 3 (template é feature de usuário) ou o dono prefere decidir o momento? *Default do plano: preencher `[Não publicado]` no CHANGELOG e NÃO subir versão — bump é decisão do dono.*
2. **`--cov-fail-under`:** o plano fixa **85** (cobertura real ~90%+, margem para flutuação). Confirmar ou ajustar.
3. **Heal com output inválido do LLM:** o plano adota **skip + log** (artigo intocado, ação `skipped_invalid_output`). Alternativa seria quarentena em diretório separado. Confirmar se skip+log basta.
4. **Conteúdo fino do template de artigo:** a Task 8 entrega um template inicial de estrutura (seções, referências, fidelidade à fonte). O refinamento pedagógico (o que um "paper perfeito" tem para o SEU estudo) é do dono — revisar `kb/templates/*.md` após a task e iterar por PR.
5. **SPECs 008/009 são drafts:** se ao ler `features/008-kb-stats/SPEC.md` ou `features/009-kb-diff/SPEC.md` algum critério de aceite for ambíguo, **parar e perguntar** — não inventar comportamento (regra ❌1 hidden assumptions).

---

## Resultado do review (quatro lentes) — contexto para o executor

### Lente 1 — Overbuilt/redundante (cortar)
- `kb/core/runner.py` (78 linhas): **zero callers** em produção e testes; `jobs.py` chama `track_command` direto. Ghost code da arquitetura RTK.
- Métrica `savings_pct` (tracking/analytics): mede `raw_output vs filtered_output`, mas como nada usa o runner com filtro, `raw == filtered` sempre → savings 0 para sempre. Métrica morta.
- `kb/cmds/lint/run.py` (9 linhas) e `kb/cmds/search/run.py` (26): wrappers de indireção pura com um call-site.
- `tomli; python_version < '3.11'` em `pyproject.toml:12`: dead dep (floor é 3.11).
- 4 implementações divergentes de parsing de frontmatter (`compile.py:191`, `qa.py:137-145`, `graph.py:26-48`, `outputs.py:10-29`) e 4 variantes de slugify.

### Lente 2 — Frágil (blindar)
- **Parsing do output do LLM sem validação**: `_strip_outer_fence` (compile.py:59) e `_extract_topic_and_title` (compile.py:191) quebram com YAML indentado/ausente; nenhum teste cobre output malformado.
- **`heal` sobrescreve artigos com output cru do LLM** (heal.py:87-89) sem validação nem backup; deleta stubs com `unlink()` direto.
- **`client.chat` pode retornar `None`** (client.py:97) → `AttributeError` em todos os callers.
- **`git.commit` engole toda exceção** (git.py:32) — usuário acha que versionou e não versionou.
- **Escritas não-atômicas** (`write_text` direto) em compile/heal/outputs.
- **CI não roda pytest nem ruff** — 327 testes sem gate; ruff sem configuração.
- Config global resolvida no import (`config.py`) — mitigada pelos monkeypatches do conftest; não mexer agora (registrado como débito, ver fim do plano).

### Lente 3 — Faltando para o objetivo
- **Nenhum template de artigo/paper**: a estrutura do output vive inline em `compile._system_prompt()` (compile.py:28-56), genérica.
- **Compile ignora `metadata.json`** dos livros (título, autor, TOC, posição do capítulo — gerado rico em `book_import_core.write_metadata`) → capítulos compilados sem contexto do livro.
- CI de teste/lint inexistente; testes zero para `book_import_pdf.py` (216 linhas), `core/tracking.py`, `discover/*`.
- Comandos `kb stats` e `kb diff` especificados mas não implementados.
- SPEC de multi-vault inexistente apesar de citada como "feature ativa".

### Lente 4 — Estrutura vs objetivo
- `cli.py` (827 linhas) concentra lógica de negócio de `ingest`/`import-book`/`archive` + 5 cópias do loop de confirmação sensível.
- `book_import_core.py` (931 linhas) é monólito EPUB (container+OPF+TOC+HTML→MD+writers). **Não** será dividido neste plano (risco > ganho para modelo barato); registrado como débito.
- Drift de verdade-fonte: CLAUDE.md cita feature inexistente; memória de abril contradiz o disco; `features/006-kb-archive/` não arquivada; `.pi/tasks/*.json` versionado contra o `.gitignore`; badges e README defasados.

---

## Global Constraints

- Python ≥ 3.11. Testes: `python -m pytest`. Lint: `ruff check kb tests`.
- **Nunca commitar em `main`.** Uma branch por fase (nomes indicados em cada fase), Conventional Commits `<tipo>(<escopo>): <desc>` ≤72 chars, imperativo.
- **Nunca chamar o LLM real em teste** — sempre `patch("kb.<módulo>.chat")`.
- Docstrings em português para funções públicas; **sem type hints novos** exceto onde crítico; **sem comentários não pedidos**; matchear o estilo do arquivo alvo (aspas, formatação).
- Corpus do usuário vive fora do repo (`KB_DATA_DIR`); paths de teste sempre via fixture `tmp_raw_wiki` (`tests/conftest.py:13`).
- Testes nomeados `test_should_<behavior>_when_<condition>`, estilo Dado/Quando/Então como os existentes.
- Cada task termina com `python -m pytest -q` verde e `ruff check kb tests` limpo antes do commit.
- Push/PR somente ao final de cada fase, e **somente com confirmação do dono**.

---

# FASE 0 — Verdade-fonte (branch `chore/truth-sync`)

### Task 1: Sincronizar docs, memória e estado com a realidade

**O quê/por quê:** três audiências (dono, colaboradores OSS, recrutadores) leem docs que hoje mentem. Um modelo barato executando as fases seguintes precisa de ground truth correto. Custo baixíssimo, alavancagem alta.

**Files:**
- Modify: `CLAUDE.md` (linhas ~125 e ~131)
- Modify: `memory/active_fronts.md`, `memory/project_state.md`, `memory/next_steps.md`, `memory/handoff.md`
- Move: `features/006-kb-archive/` → `features/_archived/006-kb-archive/`
- Modify: `README.md` e `README.en.md` (tabela de comandos + badges)
- Modify: `CHANGELOG.md` (seção `[Não publicado]`)
- Delete do índice: `.pi/tasks/tasks-*.json`

**Steps:**

- [ ] **1.** Em `CLAUDE.md`, seção "Contexto técnico atual": trocar `**Feature ativa:** 010-multi-vault-foundation` por `**Feature ativa:** nenhuma — backlog: 008-kb-stats, 009-kb-diff, 010-multi-vault (SPEC pendente, ver features/)`. Remover/ajustar a linha de "Alterações recentes" que descreve 010 como entregue.
- [ ] **2.** Reescrever `memory/active_fronts.md`: mover `llm-wiki-v2-foundation` (mergeada, PR #35) e `006-kb-archive` para "Frentes concluídas"; frentes em backlog = 008, 009, 010-multi-vault (meta real, SPEC pendente — decisão do dono em 2026-07-09). Corrigir `memory/project_state.md` (remover "004-kb-diff/005-kb-stats concluídas" — nunca existiram com esses números) e atualizar `memory/handoff.md` com data atual.
- [ ] **3.** `git mv features/006-kb-archive features/_archived/006-kb-archive` (memória confirma merge via PR #31 + arquivamento via PR #33).
- [ ] **4.** `git rm --cached .pi/tasks/tasks-*.json` (o `.gitignore` já tem a regra; o arquivo entrou antes dela).
- [ ] **5.** README.md e README.en.md: adicionar `archive` e `discovery run` à tabela de comandos (assinaturas em `kb/cli.py:517` e `kb/cli.py:581`); trocar badges hardcoded `tests-311`/`coverage-90%+` por badge do workflow de CI que a Task 2 cria (`https://github.com/<owner>/<repo>/actions/workflows/tests.yml/badge.svg`) — se a Task 2 ainda não rodou, deixar o badge apontando para o workflow que ela criará (`tests.yml`).
- [ ] **6.** `CHANGELOG.md`: preencher `[Não publicado]` com: ingest-url (PR #32), llm-wiki-v2-foundation (PR #35), kb archive (PR #31/#33), kimi-k2.7-code + topic routing (`a12ef49`). **Não** subir versão (open question 1).
- [ ] **7. Verify:** `git status` mostra só os arquivos esperados; `grep -rn "010-multi-vault" CLAUDE.md memory/` reflete o novo texto; `grep -n "archive" README.md` encontra a linha nova; `python -m pytest -q` verde (nada de código tocado).
- [ ] **8. Commit:** `chore(docs): sincronizar CLAUDE.md, memória, features e README com o estado real`

---

# FASE 1 — Gate de CI (branch `ci/test-gate`)

### Task 2: Workflow de testes + lint com gate de cobertura

**O quê/por quê:** 327 testes e ruff não rodam em PR — a maior fragilidade única do repo. Tudo que vem depois ganha rede de proteção. Fazer ANTES dos refactors.

**Files:**
- Create: `.github/workflows/tests.yml`
- Modify: `pyproject.toml` (seção `[tool.ruff]` nova; `addopts`; remover dep `tomli`)

**Steps:**

- [ ] **1.** Criar `.github/workflows/tests.yml`:

```yaml
name: tests
on:
  pull_request:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e .[llm,web,pdf,dev]
      - run: ruff check kb tests
      - run: python -m pytest -q --cov=kb --cov-report=term-missing --cov-fail-under=85
```

- [ ] **2.** Em `pyproject.toml`: adicionar

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP"]
```

  Remover a linha `"tomli; python_version < '3.11'"` das dependências (dead dep — floor é 3.11). **Não** adicionar `--cov-fail-under` ao `addopts` local (deixa o dev rodar subsets sem falhar por cobertura; o gate vive no CI).
- [ ] **3.** Rodar `ruff check kb tests` localmente. Se as regras novas (`I`, `B`, `UP`) apontarem violações, corrigir **apenas** as mecânicas (ordenação de import, sintaxe antiga); se alguma exigir mudança de comportamento, adicionar `# noqa` com justificativa e registrar em `PENDING_LOG.md`.
- [ ] **4. Verify:** `ruff check kb tests` → exit 0. `python -m pytest -q --cov=kb --cov-fail-under=85` → verde com cobertura ≥85%.
- [ ] **5. Commit:** `ci: rodar pytest+ruff em PR com matriz 3.11-3.13 e gate de cobertura`

---

# FASE 2 — Robustez do caminho crítico (branch `fix/pipeline-hardening`)

### Task 3: Módulo único de frontmatter

**O quê/por quê:** 4 parsers ad-hoc divergentes é o berço dos bugs de compile/heal/qa. Um módulo testado vira a fundação das Tasks 4 e 5.

**Files:**
- Create: `kb/frontmatter.py`
- Test: `tests/unit/test_frontmatter.py`
- Modify (adoção): `kb/compile.py:191-202`, `kb/qa.py:137-145`, `kb/graph.py:26-48`, `kb/outputs.py:10-29`

**Interfaces (produz):**
```python
parse(text: str) -> tuple[dict, str]   # (frontmatter_dict, body) — dict vazio se não há frontmatter
serialize(meta: dict, body: str) -> str
has_frontmatter(text: str) -> bool
```
Parsing manual linha-a-linha (chave: valor; listas `[a, b]` viram list de strings) — **sem dependência de PyYAML** (mantém a base de deps enxuta; os frontmatters do kb são planos).

- [ ] **1.** Escrever `tests/unit/test_frontmatter.py` com casos: frontmatter válido; sem frontmatter; valor com `:` no meio (`title: Attention: is all you need`); chave com espaços antes (`  topic: ai` — deve aceitar); lista `tags: [a, b]`; frontmatter não fechado (retorna dict vazio + texto original); roundtrip `serialize(parse(x)) == x` normalizado.
- [ ] **2.** Rodar: `python -m pytest tests/unit/test_frontmatter.py -q` → FAIL (módulo não existe).
- [ ] **3.** Implementar `kb/frontmatter.py` mínimo que passa.
- [ ] **4.** Adotar nos 4 call-sites, mantendo o comportamento externo idêntico (os testes existentes desses módulos são o contrato — não alterá-los, exceto se espelharem detalhe interno do parser antigo).
- [ ] **5. Verify:** `python -m pytest -q` verde completo.
- [ ] **6. Commit:** `refactor(frontmatter): unificar 4 parsers ad-hoc em kb/frontmatter.py`

### Task 4: Validação do output do LLM no compile

**O quê/por quê:** hoje qualquer lixo que o LLM devolver vira artigo. Validar antes de persistir é o coração da "robustez qualitativa" pedida pelo dono e pré-requisito para o template ter força de contrato (Fase 3).

**Files:**
- Modify: `kb/compile.py` (`_strip_outer_fence`, novo `_validate_output`, `compile_to_artifact`)
- Modify: `kb/client.py:97` (chat retornando None)
- Test: `tests/unit/test_compile_output_validation.py`

**Comportamento a implementar:**
1. `client.chat` → se `response.choices[0].message.content` é `None` ou vazio, levantar `RuntimeError("Provider retornou resposta vazia")` (em vez de retornar None).
2. `_strip_outer_fence` robusto: remover fence externa mesmo com language tag (` ```markdown `), preservar fences internas de código.
3. Novo `_validate_output(compiled_markdown, source_name)` chamado em `compile_to_artifact` após o strip: exige frontmatter presente (via `frontmatter.has_frontmatter`), `title` e `topic` não vazios, corpo não vazio após o frontmatter. Falha → levantar `CompileOutputError` (nova exceção em `compile.py`) com mensagem citando o arquivo fonte. `compile_many` já converte exceções em `CompileFailure` — nada a mudar lá; conferir que a mensagem aparece no relatório de falhas do CLI.

- [ ] **1.** Testes primeiro (`test_compile_output_validation.py`, mock de `kb.compile.chat`): output sem frontmatter → `CompileOutputError`; title vazio → erro; fence com language tag → strippada; fence interna de código preservada; `chat` devolvendo None → `RuntimeError` de `client` (testar em `tests/unit/test_client.py`); output válido → artifact criado.
- [ ] **2.** FAIL → implementar mínimo → PASS.
- [ ] **3. Verify:** suíte completa verde; `grep -n "CompileOutputError" kb/compile.py` existe.
- [ ] **4. Commit:** `fix(compile): validar output do LLM antes de persistir e endurecer strip de fences`

### Task 5: Heal seguro (backup + validação antes de sobrescrever)

**O quê/por quê:** heal é o único fluxo que REESCREVE artigos existentes e hoje confia cegamente no LLM. Um output ruim destrói conteúdo bom — inaceitável para wiki de estudo.

**Files:**
- Modify: `kb/heal.py`
- Test: `tests/unit/test_heal.py` (ampliar)

**Comportamento a implementar:**
1. Antes de `path.write_text(...)` com output do LLM: validar com `kb.frontmatter` que o output preserva frontmatter (mesmo `title`), e que `len(output) >= 0.5 * len(original)` (heal só adiciona links/limpa — colapso de tamanho = LLM destruiu conteúdo). Inválido → não escrever, logar `{"file": ..., "action": "skipped_invalid_output"}` (open question 3: skip+log).
2. Backup antes de qualquer escrita/deleção: copiar o arquivo original para `WIKI_DIR / ".heal_backup" / <nome>.<YYYYMMDD-HHMMSS>.md` (mesmo padrão de versionamento do `archive._versioned_backup` — ler `kb/archive.py` e reusar/extrair se aplicável). Vale também para `deleted_stub`.

- [ ] **1.** Testes primeiro: LLM devolve output sem frontmatter → artigo intocado + ação `skipped_invalid_output`; LLM devolve 10% do tamanho → intocado; output válido → escrito + backup existe em `.heal_backup/`; stub deletado → backup existe.
- [ ] **2.** FAIL → implementar → PASS.
- [ ] **3. Verify:** suíte completa verde.
- [ ] **4. Commit:** `fix(heal): backup versionado e validação de output antes de sobrescrever artigos`

### Task 6: `git.commit` deixa de engolir erros + escrita atômica

**O quê/por quê:** commit silenciosamente perdido = usuário acha que versionou. Escrita não-atômica pode deixar artigo truncado se o processo morre no meio.

**Files:**
- Modify: `kb/git.py` (except silencioso na linha ~32)
- Create: função `atomic_write_text(path, text)` em `kb/config.py` ou novo `kb/fsutil.py` (decidir pelo menor acoplamento — `fsutil.py` novo é mais limpo)
- Modify: `kb/compile.py` (`persist_artifact`, `_write_summary`), `kb/heal.py`, `kb/outputs.py` — trocar `write_text` de artefatos por `atomic_write_text`
- Test: `tests/unit/test_git.py` (ampliar), `tests/unit/test_fsutil.py`

**Comportamento:** `git.commit` captura a exceção, imprime warning via Rich/stderr (`[kb] aviso: commit falhou: <stderr do git>`) e retorna `False` (hoje retorna None); callers não mudam. `atomic_write_text` = escrever em `path.with_suffix(path.suffix + ".tmp")` + `os.replace` (mesmo padrão de `discovery._merge_and_save_seen_urls`).

- [ ] **1.** Testes primeiro: commit com repo git inexistente → retorna False e não levanta; warning emitido (capsys). `atomic_write_text` grava conteúdo e não deixa `.tmp` para trás.
- [ ] **2.** FAIL → implementar → PASS.
- [ ] **3. Verify:** suíte completa verde.
- [ ] **4. Commit:** `fix(git,fs): sinalizar commit falho e escrita atômica de artefatos`

---

# FASE 3 — Template de artigo como artefato core (branch `feat/article-template`)

### Task 7: Templates versionados + resolução com override por vault

**O quê/por quê:** decisão do dono (2026-07-09): a estrutura do artigo deixa de viver hardcoded no prompt e vira artefato versionado na engine (`kb/templates/`), com override opcional em `<KB_DATA_DIR>/templates/`. É o que permite iterar a qualidade do output sem tocar código.

**Files:**
- Create: `kb/templates/article.md`, `kb/templates/chapter.md`
- Create: `kb/templates_loader.py` (resolução engine-default vs vault-override)
- Modify: `kb/compile.py` (`_system_prompt` passa a injetar o template)
- Modify: `pyproject.toml` (garantir que `kb/templates/*.md` entra no wheel — hatchling inclui o pacote, conferir `force-include`/packages)
- Test: `tests/unit/test_templates_loader.py`, ajuste em testes de compile

**Interfaces (produz):**
```python
# kb/templates_loader.py
resolve_template(name: str) -> str   # lê <KB_DATA_DIR>/templates/<name>.md se existir, senão kb/templates/<name>.md (via importlib.resources)
```

- [ ] **1.** Criar `kb/templates/article.md` (conteúdo inicial — dono refina depois, open question 4):

```markdown
---
title: <título em português>
topic: <topic>
tags: [<tag1>, <tag2>]
source: <arquivo original>
translated_by: ai
---

# <título>

> **Resumo:** 2-4 frases com a tese central do material, fiel à fonte.

## Contexto e motivação
<por que este conceito existe; problema que resolve>

## Conceitos centrais
<definições precisas; termos técnicos consolidados podem ficar em inglês; use [[wikilinks]] para conceitos que merecem artigo próprio>

## Como funciona
<mecanismo, passos ou formulação — fiel à fonte, sem inventar>

## Exemplos
<exemplos concretos DA FONTE; se a fonte não tem, omitir a seção>

## Limitações e trade-offs
<o que a fonte aponta; se não aponta, omitir>

## Conceitos Relacionados
- [[conceito1]]
- [[conceito2]]

## Referências
- <fonte original e obras citadas no material>

---
> **Nota:** Artigo gerado e traduzido automaticamente por IA a partir de material em inglês. Pode conter imprecisões. Consulte a fonte original.
```

- [ ] **2.** Criar `kb/templates/chapter.md`: mesmo esqueleto + frontmatter com `book: <título do livro>`, `book_author: <autor>`, `chapter: <N> — <título do capítulo>` e instrução `<Este artigo compila UM capítulo; mantenha fidelidade à posição dele no livro e referencie capítulos vizinhos com [[wikilinks]] quando citados>`.
- [ ] **3.** Testes primeiro (`test_templates_loader.py`): sem override → devolve conteúdo do template da engine; com `<KB_DATA_DIR>/templates/article.md` presente (fixture `tmp_raw_wiki` + criar dir) → devolve o override; nome inexistente → `FileNotFoundError` com mensagem clara.
- [ ] **4.** Implementar `resolve_template` (engine via `importlib.resources.files("kb") / "templates"`; override via path derivado de `kb.config` — atenção: resolver o dir do vault em runtime, não no import, para respeitar os monkeypatches do conftest).
- [ ] **5.** Integrar em `compile._system_prompt()`: as regras de comportamento (idioma, wikilinks, sem code fences, fidelidade à fonte) permanecem no prompt; o bloco "Formato de saída" passa a ser o conteúdo de `resolve_template("article")`. A instrução de fidelidade nova: substituir "Extrai e organiza os conceitos-chave" por "Extrai e organiza os conceitos-chave COM FIDELIDADE à fonte — não invente conteúdo que não está no material; omita seções do template sem material correspondente".
- [ ] **6.** A validação da Task 4 (`_validate_output`) continua exigindo frontmatter+title+topic — agora o template garante que o LLM sabe o formato; nenhum acoplamento rígido seção-a-seção (LLM pode omitir seções vazias).
- [ ] **7. Verify:** suíte verde; `python -c "from kb.templates_loader import resolve_template; print(resolve_template('article')[:80])"` imprime o início do template; build do pacote inclui os .md: `pip install -e . && python -c "import importlib.resources as r; print((r.files('kb')/'templates'/'article.md').is_file())"` → True.
- [ ] **8. Commit:** `feat(templates): template de artigo versionado com override por vault injetado no compile`

### Task 8: Compile ciente de livro (consumir metadata.json)

**O quê/por quê:** o import de livros gera `metadata.json` rico (título, autor, TOC, posição do capítulo — `book_import_core.write_metadata`) que o compile ignora. Injetar esse contexto + usar `chapter.md` é a alavanca direta de acurácia livro→MD que o dono pediu.

**Files:**
- Modify: `kb/compile.py` (`_build_prompt`, `compile_to_artifact`, seleção de template)
- Test: `tests/unit/test_compile_book_context.py`

**Comportamento:**
1. Em `compile_to_artifact`, se `raw_path.parent / "metadata.json"` existe e `raw_path.name` consta em `metadata["chapters"][*]["file"]`: carregar título/autor do livro, índice e título do capítulo, `chapter_count`.
2. Prompt de sistema usa `resolve_template("chapter")`; o user prompt ganha preâmbulo: `Contexto: capítulo {index}/{chapter_count} ("{chapter_title}") do livro "{book_title}" de {book_author}.`
3. Frontmatter validado continua igual (title/topic obrigatórios); campos `book`/`chapter` são responsabilidade do template — se o LLM os omitir, não falha a validação (só title/topic são contrato).
4. `metadata.json` ilegível/corrompido → fallback silencioso para o fluxo sem contexto + warning no console (não pode quebrar compile de livro antigo).

- [ ] **1.** Testes primeiro: capítulo com metadata.json ao lado → mock de chat recebe system prompt contendo o template chapter e user prompt contendo `capítulo 2/12` e o título do livro; arquivo sem metadata → fluxo atual intocado; metadata corrompido (JSON inválido) → compila com template article + warning.
- [ ] **2.** FAIL → implementar → PASS.
- [ ] **3. Verify:** suíte completa verde; teste de integração `tests/integration/test_book_import_cli.py` continua verde.
- [ ] **4. Commit:** `feat(compile): injetar contexto do livro (metadata.json) e template de capítulo`

---

# FASE 4 — Cortes (branch `refactor/dead-code-cut`)

### Task 9: Remover código morto e indireções

**O quê/por quê:** decisão do dono: cortar tudo que é morto. Menos superfície = menos manutenção paga em tokens.

**Files:**
- Delete: `kb/core/runner.py`
- Modify: `kb/core/__init__.py` (remover re-exports `run_command`/`CommandResult`)
- Delete: `kb/cmds/lint/run.py`, `kb/cmds/search/run.py` (e seus `__init__.py` se ficarem vazios) — mover as ~10 linhas úteis de formatação para os comandos em `kb/cli.py:445` e `kb/cli.py:433`
- Modify: `kb/analytics/gain.py` + `kb/analytics/history.py` — remover apenas o cálculo/render de `savings_pct` (sempre 0); **manter** a coluna no schema SQLite de `core/tracking.py` (migração de schema é risco desnecessário; registrar em PENDING_LOG)
- Modify: testes que referenciam o que foi removido (`tests/unit/test_rtk_front.py` — conferir mocks)

**Steps:**

- [ ] **1.** Confirmar zero callers antes de cada deleção: `grep -rn "run_command\|CommandResult" kb tests` → só definições/re-export; `grep -rn "cmds.lint\|cmds.search" kb tests` → listar e migrar cada um.
- [ ] **2.** Aplicar deleções e migrações. `jobs run metrics` continua funcionando sem a linha de savings (rodar `python -m pytest tests/unit/test_rtk_front.py -q`).
- [ ] **3. Verify:** `python -m pytest -q` verde; `ruff check kb tests` limpo; `kb --help` lista os mesmos comandos de antes (`python -m kb.cli --help` ou `kb --help`).
- [ ] **4.** Registrar em `PENDING_LOG.md`: `| P2 | [deferido] coluna savings_pct órfã no schema tracking.db | origem: refactor/dead-code-cut 2026-07-09 |`
- [ ] **5. Commit:** `refactor: remover runner morto, métrica savings e wrappers de indireção`

---

# FASE 5 — Cobertura dos módulos nus (branch `test/uncovered-modules`)

### Task 10: Testes para book_import_pdf, core/tracking e discover/*

**O quê/por quê:** módulos com zero teste dedicado no caminho de import de livros (PDF!) e na infraestrutura de jobs. PDF é entrada primária do fluxo de estudo do dono.

**Files:**
- Create: `tests/unit/test_book_import_pdf.py`, `tests/unit/test_tracking.py`, `tests/unit/test_discover_registry.py`
- (leitura prévia obrigatória: `kb/book_import_pdf.py`, `kb/core/tracking.py`, `kb/discover/registry.py`, `kb/discover/rules.py`)

**Steps:**

- [ ] **1.** `test_book_import_pdf.py`: mockar `fitz` (PyMuPDF) — testar a lógica pura: chunking por TOC quando outline existe; fallback de chunk por páginas (15) sem outline; título de capítulo derivado. NÃO testar OCR (depende de binário tesseract — fora de escopo, anotar no teste).
- [ ] **2.** `test_tracking.py`: em `tmp_path`, criar DB, `track_command`, ler de volta; migração de schema (chamar duas vezes o init não quebra).
- [ ] **3.** `test_discover_registry.py`: classificação declarativa comando→categoria conforme `rules.py`; comando desconhecido → categoria default.
- [ ] **4. Verify:** `python -m pytest -q --cov=kb --cov-report=term-missing` — cobertura de `book_import_pdf.py` sai de ~0 para ≥70%; total ≥85% mantido.
- [ ] **5. Commit:** `test: cobrir book_import_pdf, core/tracking e discover`

---

# FASE 6 — Backlog de features (uma branch por feature)

### Task 11: `kb stats` (branch `feat/008-kb-stats`)

- [ ] **1.** Ler `features/008-kb-stats/SPEC.md` inteira. Se qualquer critério de aceite for ambíguo → **parar e perguntar ao dono** (open question 5).
- [ ] **2.** Seguir o pipeline do repo: os artefatos da feature (SPEC validada, PLAN/TASKS se exigidos) vivem no base branch antes da branch da feature — conferir `features/008-kb-stats/.state` e criar se ausente.
- [ ] **3.** TDD: testes de CLI primeiro (padrão de `tests/integration/test_archive_cli.py` — `CliRunner` do Typer), depois implementação usando as primitivas existentes de `kb/analytics/health.py`, `kb/analytics/history.py` e `kb/claims.py` (a SPEC nota que as primitivas já existem — NÃO reimplementar métricas).
- [ ] **4. Verify:** critérios de aceite da SPEC, um a um, com comando/teste que prova cada um; suíte completa verde.
- [ ] **5. Commit(s):** `feat(stats): ...` conforme escopo da SPEC.

### Task 12: `kb diff` (branch `feat/009-kb-diff`)

- [ ] **1.** Ler `features/009-kb-diff/SPEC.md` inteira; mesma regra de ambiguidade.
- [ ] **2.** É wrap de `git diff` sobre `wiki/` com formatação Rich — zero dependências novas (contrato da SPEC). Reusar `kb/git.py` para localizar o repo do vault.
- [ ] **3.** TDD: testes de CLI primeiro (repo git fixture em `tmp_path` com 2 commits na wiki), depois implementação.
- [ ] **4. Verify:** critérios da SPEC + suíte verde.
- [ ] **5. Commit(s):** `feat(diff): ...`

### Task 13: SPEC de 010-multi-vault (branch `feat/010-multi-vault-spec`) — SÓ ESPECIFICAÇÃO

**O quê/por quê:** decisão do dono: multi-vault é meta real sem SPEC. Este plano NÃO implementa — apenas produz a SPEC para revisão humana.

- [ ] **1.** Ler `docs/architecture/SPEC_FORMAT.md`, `docs/architecture/SDD.md` e `features/_template/SPEC.md`.
- [ ] **2.** Redigir `features/010-multi-vault-foundation/SPEC.md` (status: draft) cobrindo: múltiplos vaults sob um `KB_DATA_DIR` raiz OU múltiplos `KB_DATA_DIR`s nomeados; seleção por flag `--vault`/env; impacto em config.py (hoje resolve paths no import — a SPEC deve citar esse débito como pré-requisito); migração de vault único.
- [ ] **3.** Marcar todas as decisões em aberto com `NEEDS CLARIFICATION` — o dono resolve via `spec-clarify`. **Gate HITL: a SPEC não avança sem aprovação do dono.**
- [ ] **4. Verify:** SPEC segue SPEC_FORMAT.md (frontmatter, critérios de aceite verificáveis onde já decidido).
- [ ] **5. Commit:** `spec(010): draft de multi-vault-foundation para revisão`

---

## Débitos registrados, NÃO incluídos neste plano (não esquecer — PENDING_LOG)

| Item | Por que ficou de fora |
|---|---|
| `kb/config.py` resolve tudo no import (impede multi-vault limpo) | Refactor invasivo; vira pré-requisito DENTRO da SPEC 010 |
| `book_import_core.py` (931 linhas) dividir em epub/toc/markdownize/writers | Risco alto para modelo barato; sem bug ativo conhecido |
| `cli.py` (827): extrair lógica de `ingest`/`import-book`/`archive` + helper único de confirmação sensível (5 cópias) | Vale um `refactor-plan` próprio com o dono presente |
| 4 variantes de slugify | Baixo impacto; unificar oportunisticamente quando tocar os arquivos |
| Falso positivo do guardrail em nomes de variável (`OPENAI_API_KEY` em código de livro) | Débito P2 antigo; exige decisão de heurística |
| Coluna `savings_pct` órfã no schema tracking.db | Migração de schema desnecessária agora |

## Ordem de execução e por quê

`Fase 0 → 1 → 2 (3→4→5→6) → 3 (7→8) → 4 → 5 → 6 (11→12→13)`

Verdade-fonte primeiro (barato, corrige o chão), CI antes de qualquer refactor (rede de proteção), frontmatter antes de compile/heal (fundação), validação de compile antes do template (o template só tem força se o output é validado), cortes depois da robustez (suíte já endurecida detecta regressão), cobertura antes das features novas, features por último (dependem de tudo estar estável).

## Verificação global de fim de plano

- [ ] `python -m pytest -q --cov=kb --cov-fail-under=85` → verde nas 3 versões (via CI)
- [ ] `ruff check kb tests` → exit 0
- [ ] `kb --help` lista: ingest, import-book, compile, qa, search, lint, heal, archive, stats, diff, discovery, jobs, handoff
- [ ] Smoke manual do dono: `kb import-book <epub real> --compile` num vault de teste → artigos seguem o template de capítulo com contexto do livro no frontmatter
- [ ] `grep -rn "010-multi-vault" CLAUDE.md` → coerente com features/ no disco
