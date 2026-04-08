---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

1. **[P1] Revisar e mergear o PR de `feat/compile-parallel-hardening`**
   - confirmar diff final, checks e cobertura antes do merge

2. **[P1] Subir cobertura de `kb/cli.py` (`60%`)**
   - priorizar paths de erro, `jobs`, `heal`, `lint` e branches pouco exercitadas do `compile`

3. **[P1] Subir cobertura de `kb/book_import_core.py` (`68%`) e `kb/git.py` (`31%`)**
   - focar em fallbacks de TOC/assets/PDF e integração de commit

4. **[P2] Validar `compile_many()` contra provider real**
   - usar pequeno lote com `--workers 4`
   - confirmar ausência de corrupção em `kb_state/` e `_index.md`

5. **[P2] Consolidar ergonomia do Obsidian**
   - opcional: configurar hotkeys/profile defaults no `obsidian-terminal`
   - opcional: documentar atalhos de uso diário no vault em `<KB_DATA_DIR>/wiki`
   - base já está operacional; sem bloqueador técnico

## Médio prazo

6. **[P2] Completar a separação engine vs. corpus**
   - Neutralizar referências históricas restantes a temas pessoais em docs de arquitetura/ADR
   - Avaliar tornar `TOPICS` configurável em vez de fixo no código
   - Decidir se `examples/` permanece mínimo ou ganha seeds neutros adicionais

7. **[P2] Refinar guardrail de credenciais**
   - Falso positivo: `OPENAI_API_KEY` como nome de variável em código dispara `SensitiveContentError`
   - Solução: ignorar padrões em blocos de código markdown (fenced code blocks)

8. **[P2] Aumentar cobertura em `kb/client.py` (68%)**

9. **[P2] Embeddings + RAG híbrido**
   - Reavaliar quando wiki ultrapassar ~200 artigos

## Bloqueadores atuais

- Nenhum bloqueador técnico
- Baseline: `139` testes passando, cobertura total real `78%`
