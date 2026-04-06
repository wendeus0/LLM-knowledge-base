# PENDING_LOG.md

Pendências e decisões abertas.

| Prioridade | Item | Status | Data |
|------------|------|--------|------|
| P1 | Validar fluxo end-to-end com OpenCode Go real (`import-book --compile`, `qa`, `heal`, `lint`) | Pendente | 2026-04-03 |
| P1 | Fechar política operacional para conteúdo sensível enviado ao provider externo | Pendente | 2026-04-03 |
| P1 | Definir convenção operacional de uso de `--no-commit` e `--allow-sensitive` | Pendente | 2026-04-03 |
| P2 | Adicionar toolchain formal de cobertura (`pytest-cov`/`coverage.py`) | Pendente | 2026-04-03 |
| P2 | Formalizar dependência/distribuição entre `book2md` e `kb` (pacote compartilhado vs dependência explícita) | Pendente | 2026-04-03 |
| P2 | Integração Obsidian | ✅ Concluído | 2026-04-04 |
| P2 | Embeddings + RAG híbrido | Pendente (futuro) | 2026-04-03 |

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
- Especificar quando `--allow-sensitive` é aceitável e quando deve ser proibido
- Definir quando `--no-commit` pode ser usado sem violar rastreabilidade desejada
- Considerar políticas por diretório (`raw/private/`) em ciclo futuro

## P2 (Nice-to-have)

**Cobertura e qualidade**
- Instalar `pytest-cov` ou `coverage.py`
- Passar a produzir relatório percentual de cobertura por sprint

**Integração estrutural com book2md**
- Hoje `book2md` funciona como compat layer/lab
- Próximo passo opcional: empacotar dependência de forma explícita e remover fallback por path

**Obsidian integration** ✅ Concluído em 2026-04-04
- `wiki/.obsidian/` criado com config de vault + Shell Commands plugin pré-configurado
- 5 hotkeys mapeados: Ctrl+Shift+C/Q/H/L/S → compile/qa/heal/lint/search
- Passo manual restante: instalar plugin Shell Commands via Obsidian UI

**Embeddings + RAG**
- Atual: busca lexical simples funciona para a escala atual
- Quando escalar: adicionar embeddings + índice vetorial
- Não bloqueia a baseline atual
