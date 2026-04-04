---
name: Handoff
description: Última sessão (atualizado ao encerrar)
type: project
---

## Sprint close — 2026-04-03

**O que foi feito neste ciclo:**
- `kb` foi consolidado como implementação principal para importação de livros
- `book2md` passou a operar como compat layer/laboratório sobre o núcleo compartilhado
- `kb import-book` ganhou integração operacional com `kb compile`
- `compile` passou a descobrir arquivos de `raw/` recursivamente, incluindo `raw/books/`
- suporte inicial a PDF textual foi ampliado com segmentação heurística básica
- OpenAI SDK virou extra opcional `.[llm]`
- validação explícita de modelos compatíveis com OpenCode Go foi adicionada
- suíte `kb` validada com 53 testes passing e `book2md` com 17 testes passing
- lint limpo nas duas bases
- auditoria de segurança do sprint registrada em `SECURITY_AUDIT_REPORT.md`
- ADR criado para registrar a consolidação arquitetural do fluxo de livros e do subsistema LLM opcional

**O que falta:**
- smoke test real com a chave/endpoint OpenCode Go
- política explícita para conteúdo sensível e commits automáticos
- decisão sobre distribuição formal entre `book2md` e `kb`

**Próximo passo recomendado:**
1. instalar extra `.[llm]` se necessário
2. rodar `kb import-book <arquivo.epub> --compile`
3. validar `qa`, `heal` e `lint` contra o provider real
4. revisar recomendações do `SECURITY_AUDIT_REPORT.md`

**Prompt de retomada:**
> Retome do sprint fechado em 2026-04-03 no projeto `kb`. Primeiro valide o fluxo real com OpenCode Go (`pip install -e .[llm]`, `kb import-book <arquivo> --compile`, `kb qa`, `kb heal`, `kb lint`), depois transforme as recomendações de segurança operacional em decisões/documentação acionáveis.
