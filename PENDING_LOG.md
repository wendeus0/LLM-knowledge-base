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

**[deferido] docs/API.md sem o grupo `jobs` e `handoff create`**

- Origem: sanitização do README 2026-07-09 — `stats`/`diff`/`archive` documentados; `jobs list|run|gate|cron|doc-gate` e `handoff create` seguem fora da referência CLI
- Fechar num ciclo próprio de docs (5+ subcomandos, seção nova)

**[deferido] Coluna `savings_pct` órfã no schema de tracking.db**

- Origem: refactor/dead-code-cut 2026-07-09 (plano de robustez, Task 9)
- Métrica removida de render/consultas (`analytics/gain.py`, `analytics/history.py`); coluna permanece no schema SQLite e nos INSERTs de `core/tracking.py` para evitar migração
- Fechar quando houver migração de schema por outro motivo

**[deferido] Débitos estruturais do plano de robustez 2026-07-09**

- Split de `book_import_core.py` (931 linhas: epub/toc/markdownize/writers)
- Extração da lógica de `ingest`/`import-book`/`archive` do `cli.py` + helper único de confirmação sensível (5 cópias)
- Unificar 4 variantes de slugify
- `kb/config.py` resolve paths no import (pré-requisito da SPEC 010-multi-vault)

**[deferido] fsync do diretório pós-os.replace em fsutil**

- Origem: triagem de reviews de bot 2026-07-09 (finding 39.12, cubic)
- Crash imediatamente após `atomic_write_text` pode perder o rename; fsync do dir pai fecharia a janela
- Deferido: durabilidade extrema para dados regeneráveis (raw/ persiste como fonte)

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

## Sessão 2026-07-15/16 — stack local + features 011-013

**Anotação do dono no encerramento:** seguiremos os testes do KB; eventualmente testar o **Bonsai 8B 1-bit** para execução dessas tarefas (gate: golden set da feature 014).

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P1 | Commit das features 011 (noise filter), 012 (semantic retrieval), 013 (context budget) + defaults locais | Tudo DONE local com REPORTs; working tree sem commit por decisão de fluxo | 2026-07-16 |
| P2 | Feature 014 — `kb bench` + golden set (~12-15 perguntas do vault, grader de fidelidade) | Gate da decisão Bonsai 8B p/ QA cotidiano e do bench dos modelos da VM G0dwin | 2026-07-16 |
| P2 | Servidores locais não sobem no boot (`lms server start` + `start-bonsai-server.sh` manuais) | Candidato a launchd; sem eles o kb degrada p/ lexical e o chat falha | 2026-07-16 |
| P2 | Chunking + re-rank + sumários-como-sinal-de-retrieval | SPEC própria (evolução da 012); ganho estrutural de latência+precisão | 2026-07-16 |
| P2 | Investigação tensor API Metal → PR ao fork PrismML-Eng/llama.cpp | Time-box 1 sessão de diagnóstico; ganho potencial 3-10x no prompt processing | 2026-07-16 |
| P3 | Decisão sobre `summaries/` duplicando artigos no índice de embeddings | Resultados podem vir em dobro (ex.: circuit-breaker.md 2x) | 2026-07-16 |
| P3 | MLX 1-bit (4.8G) guardado aguardando suporte upstream | Watch cloud semanal ativo (segundas ~9h07 BRT) | 2026-07-16 |
| P3 | [deferido] Bench de modelos da VM G0dwin | VM offline (connection refused); usar golden set da 014 quando ligar | 2026-07-16 |

## Sessão 2026-07-29/30 — retrieval medido (features 014–022)

**Resolvidos desta lista:** commit das 011/012/013 (P1, feito); `kb bench` + golden set (P2, feito na 016 com 152 casos); chunking + rerank (P2, feito nas 017/020); `summaries/` duplicando o índice (P3, feito — renomeado para `_summaries/`); bench dos modelos da VM (P3 deferido — VM online, granite4 medido).

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P1 | **10 commits sem push** na branch `feat/semantic-retrieval-foundation` | Features 011–022. Push e PR só com pedido explícito do dono | 2026-07-30 |
| P1 | **Golden set (152 casos) vive em `~/vault/kb_state/bench/golden.json`, não versionado** | Diferente do índice, **não é reconstruível**: os 50 casos curados são trabalho manual. Cópia volátil em scratchpad da sessão | 2026-07-30 |
| P1 | Documentar em `.env.example` a configuração medida como melhor: rerank com `bonsai-27b-1bit` e temperatura 0 | MRR 0,343 contra 0,242 sem rerank (+42%); sem doc, a config se perde | 2026-07-30 |
| P2 | Restringir a saída do rerank: pedir top-5 em vez de ordenar 20 | Ataca alucinação de índice, que sampling **não** corrige (granite4: 32 inválidos mesmo a temp 0) | 2026-07-30 |
| P2 | Índice de embeddings em 148 MB (chunking por seção, 8.685 chunks) sem ganho de recall comprovado | 017 mediu +1 caso em 50 (ruído) e MRR pior; mantida por eliminar truncamento de 35% do corpus. Quantizar ou reverter se o tamanho incomodar | 2026-07-30 |
| P2 | `preflight()` cobre "provider morto no início", não "morreu no meio" | Duas medições foram perdidas por isso; só o contador `failed` revelou. Verificação contínua durante o lote ficou fora de escopo | 2026-07-30 |
| P2 | Perfis `analytical`, `generative` e `diverse` escolhidos por julgamento, **não medidos** | Só `deterministic` tem evidência. Medir os outros exige instrumento para qualidade de prosa, que não existe | 2026-07-30 |
| P2 | Busca lexical é o gargalo do bench: `_iter_docs` relê os 1.033 arquivos por query (~3s) | Com cache de rerank quente, 152 casos ainda levam 9 min. Índice lexical persistente resolveria | 2026-07-30 |
| P3 | `ik_llama.cpp` com `--fit --fit-margin` e KV cache q4_0 para viabilizar um 35B na VM | Reabriria o teste de compressão declarado inviável (ornith-35b: 19,7 GB em 15 GB de RAM). Referência: post de Lucas Samuel Vieira (2026). Ressalva: memory pinning dele é CUDA, a VM é AMD/ROCm | 2026-07-30 |
| P3 | `top_k`, `min_p`, `repeat_penalty` inacessíveis via cliente OpenAI-compat | Só trafegam pela API nativa do runtime. Limita o que a feature 022 pode controlar | 2026-07-30 |
| P3 | Revisar `expected` do golden onde há artigos irmãos igualmente válidos | Parte das falhas restantes é erro de medida, não de busca (verificado em amostra) | 2026-07-30 |
| P3 | Expandir golden além de 152 casos | Erro padrão em ~4pp; experimentos com delta menor que isso continuam inconclusivos | 2026-07-30 |
| P3 | VM `g0dw1n` não é dedicada: hospeda CI runners de `visep` e `infinityfit`, 15 GB de RAM | Rerank em lote compete com os containers | 2026-07-30 |
