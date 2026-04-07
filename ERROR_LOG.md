# ERROR_LOG.md

Erros e bloqueadores encontrados durante sessões de IA.

| Data | Erro | Status | Nota |
|------|------|--------|------|
| 2026-04-03 | Import de `openai` no topo de `kb.client` quebrava a coleta dos testes quando o extra LLM não estava instalado | ✓ RESOLVIDO | Refatorado para import lazy; recursos LLM agora falham apenas no uso real |
| 2026-04-03 | Configurações antigas aceitavam nome de modelo incompatível com OpenCode Go (`opencode-go/kimi-k2.5`) | ✓ RESOLVIDO | Default/documentação migrados para `kimi-k2.5` e validação explícita adicionada |
| 2026-04-03 | Estrutura de `compile` não alcançava capítulos importados em `raw/books/` | ✓ RESOLVIDO | `compile` passou a descobrir arquivos recursivamente e ignorar `metadata.json` |
| 2026-04-03 | Ambientes mínimos sem `defusedxml` quebravam a importação/testes de EPUB | ✓ RESOLVIDO | `book_import_core` ganhou fallback seguro e bloqueio explícito para XML inseguro |
| 2026-04-03 | Sem erros bloqueantes remanescentes no fechamento deste sprint | — | Baseline validada com 85 testes passando |
| 2026-04-04 | Sem erros nesta sessão | — | Sessão focada em triage e configuração Obsidian; baseline mantida |
| 2026-04-06 | Sem erros bloqueantes | — | Sessão focada em review de PR#15; fix de URL-encoding aplicado |
| 2026-04-07 | LLM retornava output de `compile` envolto em code fences (`` ```markdown `` / `` ``` ``), corrompendo frontmatter YAML de 25 artigos em `wiki/ai/` e `wiki/summaries/ai/` | ✓ RESOLVIDO | Causa raiz: SYSTEM prompt usava `` ``` `` para delimitar exemplo de formato. Fix duplo: (1) prompt atualizado com instrução explícita "SEM code fences"; (2) `_strip_outer_fence()` adicionado em `compile.py` como defesa defensiva |
| 2026-04-07 | `kb compile` interrompeu no capítulo 9 com `SensitiveContentError` — falso positivo: nome de variável `OPENAI_API_KEY` em exemplos de código do livro disparou o guardrail de credenciais | ✓ RESOLVIDO (mitigado) | Reexecutado com `--allow-sensitive`; documentado em `docs/SENSITIVE_CONTENT_POLICY.md`. Causa raiz (falso positivo em nomes de variável) permanece como débito P2 |
| 2026-04-07 | `kb heal` pareceu travar (>60s sem output) | ✓ RESOLVIDO | Latência do provider OpenCode Go, não erro. Comando completou com sucesso em background |
| 2026-04-07 | 8 testes falham em `tests/unit/test_web_ingest.py` — `AttributeError: None does not have the attribute 'get'` | ABERTO | Falha pré-existente no setup de mock; não introduzida nesta sessão. Escopo fora deste sprint |
