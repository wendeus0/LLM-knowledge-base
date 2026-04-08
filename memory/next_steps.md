---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

1. **[P1] Formalizar os gates finais da branch `feat/test-coverage-90`**
   - `branch-sync` já está limpo (`origin/main...HEAD = 0/0`)
   - ainda faltam `feature-scope-guard` e `enforce-workflow`

2. **[P1] Commitar e abrir PR da frente `test-coverage-90`**
   - quality gate e security review já passaram localmente
   - `features/test-coverage-90/REPORT.md` deve ser a base do resumo técnico

3. **[P1] Validar `compile_many()` contra provider real**
   - usar pequeno lote com `--workers 4`
   - confirmar ausência de corrupção em `kb_state/` e `_index.md`

4. **[P2] Harmonizar semântica de commit explícito**
   - avaliar se comandos ainda baseados em `--no-commit` devem migrar para `--commit` explícito

## Médio prazo

5. **[P2] Consolidar ergonomia do Obsidian**
   - opcional: configurar hotkeys/profile defaults no `obsidian-terminal`
   - opcional: documentar atalhos de uso diário no vault em `<KB_DATA_DIR>/wiki`
   - base já está operacional; sem bloqueador técnico

6. **[P2] Completar a separação engine vs. corpus**
   - Neutralizar referências históricas restantes a temas pessoais em docs de arquitetura/ADR
   - Avaliar tornar `TOPICS` configurável em vez de fixo no código
   - Decidir se `examples/` permanece mínimo ou ganha seeds neutros adicionais

7. **[P2] Refinar guardrail de credenciais**
   - Falso positivo: `OPENAI_API_KEY` como nome de variável em código dispara `SensitiveContentError`
   - Solução: ignorar padrões em blocos de código markdown (fenced code blocks)

8. **[P2] Embeddings + RAG híbrido**
   - Reavaliar quando wiki ultrapassar ~200 artigos

## Bloqueadores atuais

- Nenhum bloqueador técnico de código
- Bloqueio operacional de entrega: gates finais de escopo/workflow ainda não emitidos formalmente
- Baseline: `223` testes passando, cobertura total real `96%`
