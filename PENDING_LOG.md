# PENDING_LOG.md

Pendências e decisões abertas.

| Prioridade | Item | Status | Data |
|------------|------|--------|------|
| P1 | Validar fluxo end-to-end com OpenCode Go real (`import-book --compile`, `qa`, `heal`, `lint`) | Pendente | 2026-04-03 |
| P1 | Decidir política final para conteúdo sensível enviado ao provider externo e para commits automáticos de conteúdo compilado | Pendente | 2026-04-03 |
| P2 | Formalizar dependência/distribuição entre `book2md` e `kb` (pacote compartilhado vs dependência explícita) | Pendente | 2026-04-03 |
| P2 | Integração Obsidian | Pendente | 2026-04-03 |
| P2 | Embeddings + RAG | Pendente (futuro) | 2026-04-03 |

## P0 (Bloqueadores)

- Nenhum bloqueador aberto no fechamento deste sprint.

## P1 (Importante)

**Validação real com provider**
- Rodar smoke test com a configuração atual do `.env`
- Exercitar `kb import-book arquivo.epub --compile`
- Exercitar `kb qa`, `kb heal` e `kb lint` contra o endpoint OpenCode Go
- Confirmar mensagens de erro e ergonomia para ambientes sem extra `.[llm]`

**Política de segurança operacional**
- Definir regra explícita sobre documentos que podem ser enviados ao provider externo
- Avaliar se `compile`/`qa --file-back`/`heal` devem oferecer modo sem commit automático em cenários sensíveis
- Registrar orientação operacional derivada do `SECURITY_AUDIT_REPORT.md`

## P2 (Nice-to-have)

**Integração estrutural com book2md**
- Hoje `book2md` funciona como compat layer/lab
- Próximo passo opcional: empacotar dependência de forma explícita e remover fallback por path

**Obsidian integration**
- Wiki já é Obsidian-compatible (markdown + wikilinks)
- Futuro: plugin Obsidian que chama `kb` via CLI

**Embeddings + RAG**
- Atual: busca lexical simples funciona para a escala atual
- Quando escalar: adicionar embeddings + índice vetorial
- Não bloqueia a baseline atual
