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

2. **[P1] Consolidar política de segurança operacional**
   - Ler `SECURITY_AUDIT_REPORT.md`
   - Definir regra explícita para conteúdo sensível
   - Decidir se algum fluxo deve ganhar modo sem commit automático

3. **[P1] Limpeza de artefatos do workspace antes de commit/release**
   - Revisar `raw/` e `wiki/` gerados durante experimentos
   - Garantir que apenas artefatos intencionais sejam versionados

## Curto prazo (próximas 2 sessões)

4. **[P2] Formalizar distribuição entre `book2md` e `kb`**
   - Escolher entre dependência explícita ou pacote compartilhado
   - Remover fallback por path se a distribuição formal for adotada

5. **[P2] Melhorar heurísticas de PDF textual**
   - Detectar prefácio/introdução/apêndice
   - Refinar separação de capítulos em layouts menos limpos

6. **[P2] Documentação operacional de uso**
   - Explicar claramente quando usar `ingest`
   - Explicar quando usar `import-book`
   - Explicar quando usar `--compile`

## Médio prazo

7. **[P2] Obsidian integration**
   - Abrir wiki como vault
   - Avaliar plugin/automação leve se o uso crescer

8. **[P2] Embeddings + RAG**
   - Reavaliar quando a wiki ultrapassar a escala confortável da busca lexical

## Bloqueadores atuais

- Nenhum bloqueador técnico aberto
- Dependências LLM são opcionais, mas o smoke test real ainda está pendente
