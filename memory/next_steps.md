---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

1. **[P1] Merge PR#14 e PR#15** (F4)
   - Revisar e mergear `feat/wikilink-traversal` e `feat/rich-book-import-metadata`
   - Verificar se há conflitos após merge sequencial

2. **[P1] Rodar smoke test real com OpenCode Go** (F1)
   - `pip install -e .[llm]`
   - `kb import-book <arquivo.epub> --compile`
   - `kb qa "pergunta de verificação"`
   - `kb heal --n 3`
   - `kb lint`

3. **[P1] Fechar política operacional de sensibilidade** (F2)
   - consolidar regra explícita para conteúdo sensível
   - definir quando usar `--allow-sensitive`
   - definir quando usar `--no-commit`
   - alinhar docs com `SECURITY_AUDIT_REPORT.md`

## Curto prazo (próximas 2 sessões)

4. **[P2] Finalizar Obsidian: instalar Shell Commands plugin manualmente**
   - Abrir `wiki/` como vault
   - Settings → Community plugins → Shell Commands → Install → Enable
   - Verificar hotkeys Ctrl+Shift+C/Q/H/L/S

5. **[P2] Adicionar tooling formal de cobertura**
   - instalar `pytest-cov` ou `coverage.py`
   - passar a gerar relatório percentual por sprint

6. **[P2] Formalizar distribuição entre `book2md` e `kb`** (F3)
   - escolher entre dependência explícita ou pacote compartilhado
   - remover fallback por path se a distribuição formal for adotada

## Médio prazo

7. **[P2] Embeddings + RAG híbrido**
   - reavaliar quando a wiki ultrapassar a escala confortável da busca lexical

## Bloqueadores atuais

- Nenhum bloqueador técnico
- Baseline estável: 85 testes passando, main limpa
