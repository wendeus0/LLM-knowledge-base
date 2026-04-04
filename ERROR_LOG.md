# ERROR_LOG.md

Erros e bloqueadores encontrados durante sessões de IA.

| Data | Erro | Status | Nota |
|------|------|--------|------|
| 2026-04-03 | Import de `openai` no topo de `kb.client` quebrava a coleta dos testes quando o extra LLM não estava instalado | ✓ RESOLVIDO | Refatorado para import lazy; recursos LLM agora falham apenas no uso real |
| 2026-04-03 | Configurações antigas aceitavam nome de modelo incompatível com OpenCode Go (`opencode-go/kimi-k2.5`) | ✓ RESOLVIDO | Default/documentação migrados para `kimi-k2.5` e validação explícita adicionada |
| 2026-04-03 | Estrutura de `compile` não alcançava capítulos importados em `raw/books/` | ✓ RESOLVIDO | `compile` passou a descobrir arquivos recursivamente e ignorar `metadata.json` |
| 2026-04-03 | Sem erros bloqueantes remanescentes no fechamento do sprint | — | Base validada com testes e lint limpos |
