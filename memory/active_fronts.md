---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F1: Book Import (feat/book-import)

**Status:** Código existe, sem SPEC formal

**O que tem:**
- `kb/book_import.py` — facade
- `kb/book_import_core.py` — parser EPUB/PDF, HTML→Markdown, extração de capítulos
- `kb/cli.py` — comando `kb import-book`
- Testes unitários e de integração

**O que falta:**
- SPEC formal (regra: sem código de feature nova sem SPEC)
- Code review
- Decisão D7 (dependências): book_import_core usa apenas stdlib (OK)

**Next action:** Criar SPEC retroativa ou aceitar como feature informal

---

## Decisões abertas

### Q1: Obsidian — quando?

Wiki já é Obsidian-compatible. Plugin é futuro (P2).
Usuário pode abrir `wiki/` como vault agora.

### Q2: Escalabilidade — quando migrar para embeddings?

Limiar: >500 artigos. Atual: ~5 artigos. Sem urgência.

---

## Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| LLM gera conflitos git | Baixa | Médio | Estratégia append/update |
| API key exposta | Média | Alto | .env (gitignored) |
| Wiki grande demais | Baixa | Médio | Planejar embeddings |
| Wikilinks quebrados | Média | Baixo | Lint + heal |
