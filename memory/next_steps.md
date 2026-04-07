---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

1. **[P1] Mergear PR#19** (feat/wikilink-traversal → main)
   - `gh pr merge 19 --squash` ou via UI do GitHub

2. **[P1] Corrigir 8 testes falhando em `test_web_ingest.py`**
   - Mock setup: `patch.object` retorna `None` quando atributo não existe no target
   - Arquivo: `tests/unit/test_web_ingest.py`
   - Cobertura atual: 27% → esperada >70% após fix

3. **[P2] Consolidar ergonomia do Obsidian**
   - Opcional: configurar hotkeys/profile defaults no `obsidian-terminal`
   - Opcional: documentar atalhos de uso diário no vault em `<KB_DATA_DIR>/wiki`
   - Base já está operacional; sem bloqueador técnico

## Médio prazo

4. **[P2] Completar a separação engine vs. corpus**
   - Neutralizar referências históricas restantes a temas pessoais em docs de arquitetura/ADR
   - Avaliar tornar `TOPICS` configurável em vez de fixo no código
   - Decidir se `examples/` permanece mínimo ou ganha seeds neutros adicionais

5. **[P2] Refinar guardrail de credenciais**
   - Falso positivo: `OPENAI_API_KEY` como nome de variável em código dispara `SensitiveContentError`
   - Solução: ignorar padrões em blocos de código markdown (fenced code blocks)

6. **[P2] Aumentar cobertura em `kb/git.py` (31%) e `kb/client.py` (63%)**

7. **[P2] Embeddings + RAG híbrido**
   - Reavaliar quando wiki ultrapassar ~200 artigos

## Bloqueadores atuais

- Nenhum bloqueador técnico
- Baseline: 113 testes passando, 8 falhando pré-existentes (web_ingest mock)
