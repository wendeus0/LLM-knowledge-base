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

3. **[P2] Instalar Shell Commands plugin no Obsidian (passo manual — usuário)**
   - Abrir `wiki/` como vault
   - Settings → Community plugins → Shell Commands → Install → Enable
   - Verificar hotkeys Ctrl+Shift+C/Q/H/L/S

## Médio prazo

4. **[P2] Refinar guardrail de credenciais**
   - Falso positivo: `OPENAI_API_KEY` como nome de variável em código dispara `SensitiveContentError`
   - Solução: ignorar padrões em blocos de código markdown (fenced code blocks)

5. **[P2] Aumentar cobertura em `kb/git.py` (31%) e `kb/client.py` (63%)**

6. **[P2] Embeddings + RAG híbrido**
   - Reavaliar quando wiki ultrapassar ~200 artigos

## Bloqueadores atuais

- Nenhum bloqueador técnico
- Baseline: 113 testes passando, 8 falhando pré-existentes (web_ingest mock)
