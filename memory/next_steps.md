---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

0. **[P1] Resolver trabalho não commitado em branch errado**
   - `git checkout -b feat/pal-foundation-phase-1` a partir do estado atual
   - Passar pelo workflow: quality-gate → report-writer → branch-sync-guard → git-flow-manager
   - Separar commits por feature (pal-foundation e sensitive-execution-controls são escopos distintos)

1. **[P1] Rodar smoke test real com OpenCode Go**
   - `pip install -e .[llm]`
   - `kb import-book <arquivo.epub> --compile`
   - `kb qa "pergunta de verificação"`
   - `kb heal --n 3`
   - `kb lint`

2. **[P1] Fechar política operacional de sensibilidade**
   - consolidar regra explícita para conteúdo sensível
   - definir quando usar `--allow-sensitive`
   - definir quando usar `--no-commit`
   - alinhar docs com `SECURITY_AUDIT_REPORT.md`

## Curto prazo (próximas 2 sessões)

3. **[P2] Finalizar Obsidian: instalar Shell Commands plugin manualmente**
   - Abrir `wiki/` como vault
   - Settings → Community plugins → Shell Commands → Install → Enable
   - Verificar hotkeys Ctrl+Shift+C/Q/H/L/S

4. **[P2] Adicionar tooling formal de cobertura**
   - instalar `pytest-cov` ou `coverage.py`
   - passar a gerar relatório percentual por sprint

5. **[P2] Formalizar distribuição entre `book2md` e `kb`**
   - escolher entre dependência explícita ou pacote compartilhado
   - remover fallback por path se a distribuição formal for adotada

## Médio prazo

6. **[P2] Embeddings + RAG híbrido**
   - reavaliar quando a wiki ultrapassar a escala confortável da busca lexical

## Bloqueadores atuais

- Nenhum bloqueador técnico
- Trabalho não commitado em branch errado é risco de perda, mas não bloqueia leitura/uso
