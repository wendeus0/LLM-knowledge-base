# PENDING_LOG.md

Pendências e decisões abertas.

| Prioridade | Item                                                                                                                   | Status                                                                                                                                                       | Data       |
| ---------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| P1         | Validar fluxo end-to-end com OpenCode Go real (`import-book --compile`, `qa`, `heal`, `lint`)                          | ✅ Concluído — todos os comandos validados; 12 caps compilados de EPUB real                                                                                  | 2026-04-07 |
| P1         | Fechar política operacional para conteúdo sensível enviado ao provider externo                                         | ✅ Concluído — `docs/SENSITIVE_CONTENT_POLICY.md` criado                                                                                                     | 2026-04-07 |
| P1         | Definir convenção operacional de uso de `--no-commit` e `--allow-sensitive`                                            | ✅ Concluído — documentado em `docs/SENSITIVE_CONTENT_POLICY.md`                                                                                             | 2026-04-07 |
| P1         | Corrigir root cause de code fence wrapping em outputs do LLM                                                           | ✅ Concluído — SYSTEM prompt + `_strip_outer_fence()` em `compile.py`                                                                                        | 2026-04-07 |
| P1         | Merge PR#14 (wikilink-traversal) — aguardando aprovação                                                                | ✅ Concluído — mergeado conforme confirmação do usuário                                                                                                      | 2026-04-07 |
| P1         | Merge PR#15 (rich-book-import-metadata) — aguardando aprovação                                                         | ✅ Concluído — mergeado conforme confirmação do usuário                                                                                                      | 2026-04-07 |
| P1         | Abrir PR com entregas do sprint (feat/wikilink-traversal branch)                                                       | ✅ Concluído — PR#19 aberto                                                                                                                                  | 2026-04-07 |
| P2         | Adicionar toolchain formal de cobertura (`pytest-cov`/`coverage.py`)                                                   | ✅ Concluído — `pytest-cov` em `[dev]`; 80% cobertura; HTML em `htmlcov/`                                                                                    | 2026-04-07 |
| P2         | Formalizar dependência/distribuição entre `book2md` e `kb` (pacote compartilhado vs dependência explícita)             | ✅ Concluído — A3 rejeitada formalmente em ADR-0001; núcleo permanece em `kb/book_import_core.py`                                                            | 2026-04-07 |
| P2         | Integração Obsidian                                                                                                    | ✅ Concluído — `<KB_DATA_DIR>/wiki` validado com plugin `obsidian-terminal`; `kb qa` executado dentro do Obsidian                                            | 2026-04-07 |
| P2         | Higienização do repositório open source                                                                                | ✅ Concluído — corpus pessoal movido para `<KB_DATA_DIR>`; engine separada do conteúdo                                                                       | 2026-04-07 |
| P1         | Hardenizar `compile` paralelo seguro com persistência serial determinística                                            | ✅ Concluído — `compile_to_artifact`, `persist_artifact`, `compile_many` e `--workers/--commit` entregues                                                    | 2026-04-08 |
| P1         | Alinhar `import-book --compile` ao mesmo contrato de batch seguro                                                      | ✅ Concluído — `import-book --compile` usa `compile_many()` quando `workers > 1` e agrega falhas por capítulo                                                | 2026-04-08 |
| P1         | Rerodar suíte completa com cobertura real e incluir `kb/cli.py` no relatório                                           | ✅ Concluído — `139` testes passando; cobertura total `78%`; `kb/cli.py` em `60%`                                                                            | 2026-04-08 |
| P1         | Elevar cobertura total para >=90% e fechar gaps em `kb/cli.py`, `kb/client.py`, `kb/git.py` e `kb/book_import_core.py` | ✅ Concluído — `223` testes passando; cobertura total `96%`; `kb/cli.py` `98%`, `kb/client.py` `97%`, `kb/git.py` `100%`, `kb/book_import_core.py` `97%`     | 2026-04-08 |
| P1         | Tirar a frente atual de `main` e finalizar o fluxo Git em branch dedicada                                              | ✅ Concluído parcialmente — branch `feat/test-coverage-90` criada; ainda faltam `feature-scope-guard`, `enforce-workflow` e ação explícita de commit/push/PR | 2026-04-08 |
| P2         | Embeddings + RAG híbrido                                                                                               | Pendente (futuro) — escopo coberto por RF-05 de `llm-wiki-v2-foundation`                                                                                     | 2026-04-03 |
| P1         | Fechar `ingest-url` via PR                                                                                             | ✅ Concluído — PR #32 mergeado (commit `6072c1d`) + artefatos docs                                                                                            | 2026-04-22 |
| P1         | Fechar `006-kb-archive` via PR                                                                                         | ✅ Concluído — PR #31 mergeado (`5f56418`) + PR #33 arquivamento (`6150b4a`)                                                                                  | 2026-04-22 |
| P2         | Triar backlog de 10 propostas de feature do usuário                                                                    | ✅ Concluído — 3 ondas priorizadas em `memory/next_steps.md`; item BM25 descartado (já entregue)                                                              | 2026-04-22 |
| P2         | Decidir destino de `kb/audit.py`                                                                                       | ✅ Resolvido — integrar em `llm-wiki-v2-foundation` como parte de RF-07 (commit na branch da feature)                                                         | 2026-04-22 |
| P2         | Corrigir referências fantasmas a `kb diff`/`kb stats` em `CLAUDE.md`                                                   | ✅ Concluído — refs marcadas como (backlog) 008/009; SPECs draft criadas                                                                                     | 2026-04-22 |

## P0 (Bloqueadores)

- Nenhum bloqueador. Baseline verde: 311/311 passed (branch `fix/baseline-green-2026-04-22`).

## P1 (Importante)

**Frente ativa: `llm-wiki-v2-foundation`**

- Status: PLAN_READY → próximo: `test-red` em branch dedicada
- `kb/audit.py` + `tests/unit/test_audit.py` já commitados em `fix/baseline-green-2026-04-22` (também pertencem a RF-07)
- SPEC, PLAN, TASKS em `features/llm-wiki-v2-foundation/`

**Cobertura de `kb/discovery.py`**

- 25% — módulo novo (PR #34) sem testes dedicados
- Criar `tests/unit/test_discovery.py` cobrindo run loop, lock, seen-tracking

**Fechamento da frente `test-coverage-90`**

- baseline atual: `223` testes passando, cobertura total real `96%`
- módulos-alvo concluídos acima do limiar: `kb/cli.py` `98%`, `kb/client.py` `97%`, `kb/git.py` `100%`, `kb/book_import_core.py` `97%`
- branch dedicada criada: `feat/test-coverage-90`
- pendente: `git-flow-manager` + push/PR quando solicitado

## P2 (Nice-to-have)

**Falso positivo no guardrail de credenciais**

- `OPENAI_API_KEY` como nome de variável em exemplos de código (não credencial real) dispara `SensitiveContentError`
- Mitigação atual: `--allow-sensitive` para livros técnicos com exemplos de código
- Refinamento desejável: guardrail mais contextual (ex: ignorar padrões em blocos de código markdown)

**Próximas frentes técnicas**

- validar `compile_many()` com provider real e múltiplos workers
- avaliar harmonizar semântica de commit explícito nos comandos que ainda usam `--no-commit`
- manter novos testes de `book_import_core` orientados a contrato, não a detalhes de parser

**Obsidian operacional via `obsidian-terminal`**

- `<KB_DATA_DIR>/wiki` aberto como vault no Obsidian
- Plugin `obsidian-terminal` adotado no lugar de `Shell Commands`
- Profile integrado validado com shell login (`/bin/zsh --login` ou `/bin/bash --login`)
- `kb qa` executado com sucesso dentro do terminal integrado
- Próximo refinamento opcional: documentar/profile defaults e hotkeys do plugin

**Próxima etapa estrutural do open source**

- Remover/neutralizar referências históricas restantes a corpus temático pessoal em docs de arquitetura/ADR
- Avaliar tornar `TOPICS` configurável em vez de fixo no código
- Definir se `examples/` deve crescer com seeds neutros adicionais ou permanecer mínimo

**Embeddings + RAG**

- Atual: busca lexical simples funciona para a escala atual (~14 artigos em wiki/ai/)
- Quando escalar: adicionar embeddings + índice vetorial
- Não bloqueia a baseline atual
