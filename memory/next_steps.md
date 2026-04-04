---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

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

3. **[P1] Preparar commit/push/PR da branch atual**
   - revisar `git status`
   - garantir que artefatos intencionais apenas estejam no diff
   - usar o fluxo `/git-flow-manager` ao final

## Curto prazo (próximas 2 sessões)

4. **[P2] Adicionar tooling formal de cobertura**
   - instalar `pytest-cov` ou `coverage.py`
   - passar a gerar relatório percentual por sprint

5. **[P2] Formalizar distribuição entre `book2md` e `kb`**
   - escolher entre dependência explícita ou pacote compartilhado
   - remover fallback por path se a distribuição formal for adotada

6. **[P2] Melhorar documentação operacional de uso**
   - explicar claramente quando usar `ingest`
   - explicar quando usar `import-book`
   - explicar quando usar `--compile`, `--allow-sensitive` e `--no-commit`

## Médio prazo

7. **[P2] Obsidian integration**
   - abrir wiki como vault
   - avaliar plugin/automação leve se o uso crescer

8. **[P2] Embeddings + RAG híbrido**
   - reavaliar quando a wiki ultrapassar a escala confortável da busca lexical

## Bloqueadores atuais

- Nenhum bloqueador técnico aberto
- Dependências LLM são opcionais, mas o smoke test real ainda está pendente
