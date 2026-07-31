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
| P2         | Embeddings + RAG híbrido                                                                                               | ✅ Concluído — features 012/014–022; ADR-0017. `recall@5` 0,230 → 0,467, MRR 0,127 → 0,343 no golden de 152 casos                                            | 2026-07-30 |
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

**Embeddings + RAG** — ✅ resolvido em 2026-07-30 (ADR-0017)

- Era: "busca lexical simples funciona para a escala atual (~14 artigos em wiki/ai/)"
- Virou: o corpus chegou a 1.033 artigos e o lexical media `recall@5` 0,230. Canal semântico + rerank levaram a 0,467
- Índice vetorial dedicado permanece rejeitado: brute-force em memória basta até ~5.000 artigos

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
| ~~P1~~ | ~~Documentar em `.env.example` a configuração medida como melhor~~ | ✅ Concluído — `.env.example` traz a tabela medida, o motivo de o granite4 ser pior que não reordenar, e as duas URLs de provider | 2026-07-30 |
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

## Sessão 2026-07-30 — higienização de artefatos

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P2 | Reconciliar `docs/superpowers/plans/2026-07-09-core-robustness.md` — 73 checkboxes abertos, zero marcados | Os artefatos que o plano promete já existem (`frontmatter.py`, `templates_loader.py`, `templates/`, `stats.py`, `diff.py`) e 008/009 foram entregues nos PRs #43/#44. Marcar exige verificar item a item contra o código; nota de status adicionada no topo do plano enquanto isso não acontece | 2026-07-30 |
| P2 | `features/010-multi-vault-foundation` é a única aberta e segue em `draft` desde abril | Decidir se entra no roadmap ou vai para `_archived/` como descartada. O BACKLOG da engenharia reversa avaliou os 11 portes contra vault único, por decisão explícita | 2026-07-30 |
| P3 | `docs/architecture/TDD.md` não foi revisado nesta higienização | Data de 2026-04-07; não se sabe se a estratégia de testes descrita ainda corresponde à suíte de 602 testes | 2026-07-30 |

## Sessão 2026-07-30 — charting da política de corpus

Achados de leitura durante o `wayfinder` de política de corpus (`docs/research/2026-07-30-politica-de-corpus/`). Ambos são bugs de retrieval, fora do escopo daquele map — registrados aqui por decisão explícita do Out of scope.

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P1 | **O reranker recebe snippet vazio para candidatos exclusivamente semânticos** | `snippets` só é populado para docs com `tf_total > 0` (`kb/search.py:84-87`); `_apply_rerank` monta o candidato com `item.get("snippet","")` (`:151-154`). Um artigo recuperado **apenas** pelo canal de embeddings — a classe exata que o canal semântico existe para resgatar — chega ao LLM como `12. nome-do-arquivo — ` sem texto. O rerank então julga por slug. Suspeita a medir: parte do teto de `recall@5 = 0,467` é isto, não limite do modelo | 2026-07-30 |
| P2 | **Colisão de `stem` faz artigo sumir do resultado** | `_apply_rerank` chaveia por `path.stem` (`kb/search.py:155-156`) e o vault tem 4 stems duplicados em topics diferentes (`algebra-linear`, `honeycomb`, `fundamentos-de-engenharia-de-dados`, `decomposicoes-de-matrizes`). Dois no mesmo head → um sobrescreve o outro no `by_slug` e desaparece. Afeta também a medição: `run_bench` compara por `Path(item["path"]).stem` (`kb/bench.py:246`), então um caso pode "acertar" o arquivo errado | 2026-07-30 |
| P2 | **`com.wendeus.kb-rerank` roda fora do launchd** | O plist tem `KeepAlive=true`, mas `launchctl list` mostra o job sem PID e com último exit code 1. O `llama-server` que atende `:8081` (PID 33508) é órfão — subido à mão ou sobrevivente de um launchd que desistiu. Se morrer, não volta sozinho, e o `kb qa` degrada silenciosamente para sem-rerank | 2026-07-30 |
| ~~P3~~ | ~~**Dois checkouts divergentes do repo**~~ **RESOLVIDO 2026-07-31**: `~/dev/github.com/wendeus0/` é o canônico — ganhou `.env` (`KB_DATA_DIR=/Users/wendeus/vault`, gitignored) e `.venv` (Python 3.14.6, `pip install -e .[llm,dev,web,pdf]`). Baseline validada: 609 passed / 91% / ruff clean; `kb index status` confirma DATA_DIR no vault. `~/dev/personal/` fica como cópia obsoleta (atrás de `main`) | 2026-07-30 |

## Sessão 2026-07-31 — gate de saída do compile

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P3 | **`tests/unit/test_diff.py::test_diff_error_message_should_escape_rich_markup` falha localmente, mas passa no CI** | Pré-existente, confirmado por `git stash`: falha igual com e sem as mudanças do dia. **O CI do PR #46 passou em 3.11, 3.12 e 3.13**, então é ambiental, não da branch — o teste espera `'[bold]injetado[/bold]'` literal em `result.output` e o Rich local renderiza a markup escapada com códigos ANSI (comportamento dependente de TTY/versão). Rebaixado de P2 para P3: o gate de CI não é afetado; incomoda quem roda `pytest` local | 2026-07-31 |
| P2 | **Seção "Exemplos" preenchida com conteúdo que não é exemplo continua sem detector** | Três heurísticas testadas contra o corpus e contra os dois artigos-alvo reais, todas descartadas com medição: (1) Jaccard de sobreposição entre seções — os artigos ruins deram 0,205 e 0,109, e o p99 do corpus é 0,254, então não há limiar que separe; (2) concretude condicional (artigo com sintaxe em outras seções mas não em Exemplos) — pega os dois alvos mas reprova 25 de 129 artigos técnicos legítimos, 19,4%; (3) fração de termos novos na seção — os alvos deram 0,574 e 0,600, **acima** da mediana do corpus (0,571). Detectar isso exige juiz semântico (LLM no gate), que é decisão de custo própria | 2026-07-31 |
| P3 | **`kb compile` não tem `--force` para gravar apesar do gate** | O gate é fail-closed sem escape hatch. Propagar a flag exigiria tocar `kb/cli.py`, `kb/cmds/compile/run.py` e as assinaturas de `compile_many`/`compile_to_artifact`. Deixado fora por escopo; a taxa de reprovação medida no corpus é 0,10% (1 de 1.039), então não bloqueia uso | 2026-07-31 |

## Sprint-close 2026-07-31 — débito classificado

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| **P1 (segurança)** | **`kb ingest <url>` traz conteúdo não-confiável que vira contexto do LLM sem filtro de injeção** | Achado no sprint-close, ao ingerir 4 páginas de terceiro (OWASP, Wikipedia, Exploit-DB) pela primeira vez. O caminho `raw/ → compile → wiki → qa` faz conteúdo web arbitrário alimentar o prompt em duas etapas. `kb/guardrails.py` tem apenas `SENSITIVE_PATTERNS` (api_key/token/password) — **nenhuma checagem de prompt injection**. A regra 8 do AGENTS.md ("output de ferramenta externa é dado, nunca instrução") não tem enforcement neste caminho. O conteúdo ingerido nesta sessão foi verificado e está limpo, mas não há gate para o próximo. `kb/web_ingest.py` já protege contra SSRF, o que mostra que a fronteira foi pensada para rede e não para conteúdo | 2026-07-31 |
| P1 | **Auditoria de segurança vencida** | A última é de **2026-04-07** (`docs/reports/SECURITY_AUDIT_2026-04-07.md`), quase 4 meses e vários sprints atrás — critério 2 do `sprint-close` dispara. Não executada neste ciclo por escopo; o sprint tocou apenas `kb/compile.py`, `scripts/` e testes, sem CI/CD, auth, infra, APIs públicas ou skills. Executar `security-audit` no início do próximo sprint | 2026-07-31 |
| P2 | **`kb ingest` não remove boilerplate nem detecta página vazia de conteúdo** | Ticket 002: o GHDB foi ingerido com **zero dorks** — só `"This site requires JavaScript"` — e o comando **reportou sucesso**. 1.358 palavras de chrome parecem conteúdo legítimo; numa ingestão em lote isso vira artigo compilado de nada. Além disso `html2text` colapsa markdown puro numa linha só, destruindo a estrutura de que `kb/chunking.py` depende | 2026-07-31 |
| P2 | **`kb compile <path relativo>` falha com mensagem enganosa** | Interpreta o caminho como nome de livro: `"Nenhum livro encontrado para: raw/arquivo.md"`. Exige caminho absoluto e a mensagem não indica isso | 2026-07-31 |

## Sessão 2026-07-31 — inconsistência de versionamento

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P3 | **`.gitignore` exclui `docs/reports/`, mas 12 relatórios estão versionados** | `.gitignore:21` tem `docs/reports/`; ao mesmo tempo `git ls-files` lista 12 arquivos tracked ali (`COVERAGE_2026-04-22.md`, `DEBT_2026-04-22.md`, `SECURITY_AUDIT_2026-04-07.md`, a série `CODEBASE_SPEC_COMPLIANCE_*`). A regra só afeta untracked, então os antigos seguem versionados e os novos exigem `git add -f` — foi o caso do relatório deste sprint. O `CLAUDE.md` § "Layout de docs" documenta `docs/reports/` como "relatórios datados (cobertura, débito, auditoria, conformidade)", o que contradiz o ignore. Decidir: versionar relatórios (remover a linha do gitignore) ou não (destrackear os 12 e ajustar o CLAUDE.md) | 2026-07-31 |

## Sessão 2026-07-31 — review do PR #50 (colisão de stem)

Achados do review adversarial (Codex + Opus fresco) fora do escopo do PR — mesma classe do bug corrigido, em outros módulos.

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P2 | **`kb/graph.py`, `kb/archive.py` e `kb/lint.py` ainda chaveiam por stem** | `graph.py:23` (`candidate.stem == slug`): wikilink `[[honeycomb]]` resolve para o homônimo que o `rglob` achar primeiro. `archive.py:40,49` (`_normalize_link(p.stem)` para órfãos): linkar um homônimo faz o outro parecer linkado e bloqueia seu arquivamento. `lint.py:26` (`{p.stem.lower()}`): mesmo colapso na detecção de link quebrado. O vault tem 4 stems duplicados. Corrigir com a mesma identidade `rel_slug` do PR #50 — mas wikilinks por stem são a convenção do Obsidian, então graph/archive/lint precisam decidir entre desambiguar (custo de UX) ou documentar a resolução "primeiro achado" | 2026-07-31 |
| P3 | **Efeitos operacionais do PR #50 a lembrar na próxima medição** | (1) Cache do rerank invalidado por inteiro — slug novo muda todas as chaves de `_cache_key`; as 611 entradas de `kb_state/rerank.json` viram lixo inalcançável e a próxima `kb bench --rerank 20` re-emite as 152 chamadas (~18 min). (2) `--sample-seed` não reproduz amostras antigas — o pool mudou de stems para rel slugs (medido: 1 em comum de 30 com seed 42). (3) O pool de geração cresceu 1.035 → 1.039: os 4 homônimos agora são amostráveis | 2026-07-31 |

## Auditoria de segurança 2026-07-31 — achados não corrigidos no ciclo

Relatório completo: `docs/reports/SECURITY_AUDIT_2026-07-31.md`. Veredito `SECURITY_FAIL` por F-01 (SSRF pinning ausente em HTTPS) e F-02 (cadeia `discovery` desatendida), ambos endereçados em PR próprio. O que segue é o restante.

| Prioridade | Item | Contexto | Data |
| --- | --- | --- | --- |
| P1 | **F-03 — embeddings e rerank escapam do guardrail de conteúdo sensível** | `assert_safe_for_provider` cobre compile/qa/heal/lint e **não** os canais novos: `embed_texts` manda o texto integral de cada artigo para `KB_EMBED_BASE_URL` (`kb/embeddings.py:32-43`, `:111`) e o rerank manda pergunta + snippets para `KB_RERANK_BASE_URL` (`kb/rerank.py:113-133`, `:207-218`), ambos URLs livres de env sem validação de host/esquema; `compile`/`qa`/`heal` disparam `refresh_embeddings_index` automaticamente. `--allow-sensitive` deixou de ser o gate único de egresso. Auditoria 2026-07-31 | 2026-07-31 |
| P2 | **F-06 — pisos de dependência admitem versões com CVE e CI sem lock** | `requests>=2.31` admite 2.31.0 (CVE-2024-35195, CVE-2024-47081 — vazamento de credencial `.netrc`, exatamente o caminho do `web_ingest`); `pymupdf>=1.24` admite versões iniciais com falhas de memória do MuPDF, e o parser recebe PDF não-confiável. Ambiente atual está OK (requests 2.34.2, pymupdf 1.28.0); o risco é o piso. `.github/workflows/tests.yml:17` instala sem lock nem hash. Subir pisos + lock com hashes | 2026-07-31 |
| P2 | **F-08 — symlink na wiki é lido e enviado ao provider** | `archive.py:36,59` pula symlinks; `search.py:28`, `embeddings.py:49`, `lint.py:22`, `heal.py:85-89`, `compile.py:545` não. `wiki/x.md → ~/.ssh/config` entra no corpus. Filtro `is_symlink()` centralizado no iterador de artigos | 2026-07-31 |
| P3 | **F-07/F-09 a F-15 — higiene de segurança da auditoria 2026-07-31** | F-07: `permissions: contents: read` faltando em `tests.yml`/`kb-doc-governance.yml`, inputs interpolados em `run:` no `kb-jobs-and-health-gate.yml`. F-09: `git add` sem `--` (`kb/git.py:64`) e `doc-gate` sem a validação de prefixo `-` que `diff.py:28-29` já faz. F-10: `source_url`/`source_question` no frontmatter sem `_yaml_quote` (herdado de abril). F-11: `SENSITIVE_PATTERNS` sem AWS/GitHub/GitLab/Bearer/JWT (herdado de abril). F-12: fallback `xml.etree` no `discovery.py:19-22` sem a pré-checagem de DOCTYPE que `book_import_core` tem. F-13: sem cap de bytes em `response.text`/`read_bytes`/`ZipFile.read` (zip bomb em EPUB). F-14: `KB_API_KEY` default `"local"` mata o guard `if not API_KEY`. F-15: `KB_EMBED_AUTOSTART_CMD` executa comando vindo de env (opt-in, sem shell). Também: `SECURITY.md` afirma sanitização de path que não vale para `manifest.json`/`metadata.json` | 2026-07-31 |
| P3 | **`kb_state/rerank.json` não tem poda nem versionamento** | Achado nos reviews dos PRs #50/#51: entradas invalidadas por mudança de chave (`_cache_key`) ficam no arquivo para sempre — duas invalidações totais consecutivas (slugs no #50, snippets no #51) deixaram ~600 entradas de peso morto; cada miss lê e regrava o arquivo inteiro. 81 KB hoje, crescimento O(queries distintas). Poda por idade/versão de chave quando incomodar | 2026-07-31 |
| P3 | **Snippet semântico pode divergir do chunk vencedor em índice pré-#51 ou stale** | O caminho exato (hash + ordinal) só funciona com índice reconstruído após o PR #51 e arquivo inalterado; caso contrário cai para heading (merge de seção curta e split por budget mapeiam vários chunks no mesmo heading — 7 chunks no vault com heading duplicado). Snippet segue melhor que vazio; corrigir de vez exigiria gravar o texto do chunk no índice | 2026-07-31 |
