# DEBT_REPORT.md

## Sprint fechado em 2026-04-03

## P0

- Nenhum débito P0 aberto.

## P1

1. **Validar fluxo real com OpenCode Go**
   - a baseline está verde, mas ainda depende de mocks para o subsistema LLM

2. **Fechar política operacional para conteúdo sensível**
   - falta regra clara de classificação do que pode ir ao provider

3. **Definir convenção de uso para `--no-commit` e `--allow-sensitive`**
   - flags já existem, mas ainda precisam de política de uso e revisão operacional

## P2

1. **Adicionar tooling formal de cobertura**
   - hoje existe evidência funcional forte, mas não métrica percentual reproduzível

2. **Formalizar integração `book2md` → `kb`**
   - ainda há acoplamento operacional aceitável, porém provisório

3. **Integração Obsidian**
   - desejável, mas não bloqueia a baseline atual

4. **Embeddings + RAG híbrido**
   - futuro, condicionado à escala da wiki

## Veredito

- sprint fecha com baseline estável
- débito atual é majoritariamente operacional/documental, não de quebra técnica imediata
