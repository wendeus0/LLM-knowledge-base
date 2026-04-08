# PENDING_LOG.md

Pendências e decisões abertas.

| Prioridade | Item                                                                                                       | Status                                                                                                            | Data       |
| ---------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ---------- |
| P1         | Validar fluxo end-to-end com OpenCode Go real (`import-book --compile`, `qa`, `heal`, `lint`)              | ✅ Concluído — todos os comandos validados; 12 caps compilados de EPUB real                                       | 2026-04-07 |
| P1         | Fechar política operacional para conteúdo sensível enviado ao provider externo                             | ✅ Concluído — `docs/SENSITIVE_CONTENT_POLICY.md` criado                                                          | 2026-04-07 |
| P1         | Definir convenção operacional de uso de `--no-commit` e `--allow-sensitive`                                | ✅ Concluído — documentado em `docs/SENSITIVE_CONTENT_POLICY.md`                                                  | 2026-04-07 |
| P1         | Corrigir root cause de code fence wrapping em outputs do LLM                                               | ✅ Concluído — SYSTEM prompt + `_strip_outer_fence()` em `compile.py`                                             | 2026-04-07 |
| P1         | Merge PR#14 (wikilink-traversal) — aguardando aprovação                                                    | ✅ Concluído — mergeado conforme confirmação do usuário                                                           | 2026-04-07 |
| P1         | Merge PR#15 (rich-book-import-metadata) — aguardando aprovação                                             | ✅ Concluído — mergeado conforme confirmação do usuário                                                           | 2026-04-07 |
| P1         | Abrir PR com entregas do sprint (feat/wikilink-traversal branch)                                           | ✅ Concluído — PR#19 aberto                                                                                       | 2026-04-07 |
| P2         | Adicionar toolchain formal de cobertura (`pytest-cov`/`coverage.py`)                                       | ✅ Concluído — `pytest-cov` em `[dev]`; 80% cobertura; HTML em `htmlcov/`                                         | 2026-04-07 |
| P2         | Formalizar dependência/distribuição entre `book2md` e `kb` (pacote compartilhado vs dependência explícita) | ✅ Concluído — A3 rejeitada formalmente em ADR-0001; núcleo permanece em `kb/book_import_core.py`                 | 2026-04-07 |
| P2         | Integração Obsidian                                                                                        | ✅ Concluído — `<KB_DATA_DIR>/wiki` validado com plugin `obsidian-terminal`; `kb qa` executado dentro do Obsidian | 2026-04-07 |
| P2         | Higienização do repositório open source                                                                    | ✅ Concluído — corpus pessoal movido para `<KB_DATA_DIR>`; engine separada do conteúdo                            | 2026-04-07 |
| P1         | Hardenizar `compile` paralelo seguro com persistência serial determinística                                | ✅ Concluído — `compile_to_artifact`, `persist_artifact`, `compile_many` e `--workers/--commit` entregues         | 2026-04-08 |
| P1         | Alinhar `import-book --compile` ao mesmo contrato de batch seguro                                          | ✅ Concluído — `import-book --compile` usa `compile_many()` quando `workers > 1` e agrega falhas por capítulo     | 2026-04-08 |
| P1         | Rerodar suíte completa com cobertura real e incluir `kb/cli.py` no relatório                               | ✅ Concluído — `139` testes passando; cobertura total `78%`; `kb/cli.py` em `60%`                                 | 2026-04-08 |
| P2         | Embeddings + RAG híbrido                                                                                   | Pendente (futuro)                                                                                                 | 2026-04-03 |

## P0 (Bloqueadores)

- Nenhum bloqueador aberto no fechamento desta sessão.

## P1 (Importante)

**Cobertura de testes após hardening de compile**

- baseline atual: `139` testes passando, cobertura total real `78%`
- aumento material de visibilidade: `kb/cli.py` voltou para o relatório real (`60%`) após remoção do `omit`
- foco sugerido para próxima sessão: subir cobertura dos módulos mais fracos sem abrir nova feature

## P2 (Nice-to-have)

**Falso positivo no guardrail de credenciais**

- `OPENAI_API_KEY` como nome de variável em exemplos de código (não credencial real) dispara `SensitiveContentError`
- Mitigação atual: `--allow-sensitive` para livros técnicos com exemplos de código
- Refinamento desejável: guardrail mais contextual (ex: ignorar padrões em blocos de código markdown)

**Gaps de cobertura prioritários para a próxima sessão**

- `kb/cli.py`: `60%` — faltam paths de erro e comandos menos exercitados
- `kb/book_import_core.py`: `68%` — faltam fallbacks e paths menos comuns de PDF/TOC/assets
- `kb/git.py`: `31%` — faltam testes de integração dos commits automáticos/opt-in
- `kb/client.py`: `68%` — faltam paths de erro e validações do provider

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
