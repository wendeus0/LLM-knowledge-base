---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (próxima sessão)

1. **[P2] Finalizar Obsidian: instalar Shell Commands plugin manualmente** (passo manual — usuário)
   - Abrir `wiki/` como vault
   - Settings → Community plugins → Shell Commands → Install → Enable
   - Verificar hotkeys Ctrl+Shift+C/Q/H/L/S

## Concluído nesta sessão (2026-04-07)

- [x] PR#14 + PR#15 mergeados (F4)
- [x] Smoke test completo: `search`, `lint`, `qa`, `heal`, `import-book --compile` OK (F1)
- [x] Política operacional de sensibilidade — `docs/SENSITIVE_CONTENT_POLICY.md` (F2)
- [x] pytest-cov instalado; 80% cobertura; HTML em `htmlcov/` (F5)
- [x] Relação `book2md` ↔ `kb` formalizada — A3 rejeitada em ADR-0001 (F3/F6)
- [x] EPUB "Building Applications with AI Agents" importado e compilado — 12 artigos em wiki/ai/

## Médio prazo

7. **[P2] Embeddings + RAG híbrido**
   - reavaliar quando a wiki ultrapassar a escala confortável da busca lexical

## Bloqueadores atuais

- Nenhum bloqueador técnico
- Baseline estável: 85 testes passando, main limpa
