---
title: Safe parallel compile
epic: compile
status: approved
pr:
---

# Safe parallel compile

## Objetivo

Hoje `kb compile` processa múltiplos arquivos em paralelo com persistência serial determinística e sem commit automático por padrão. Esta continuação endurece a feature para validar concorrência com mais confiança, alinhar `import-book --compile` ao mesmo contrato de lote seguro e remover a necessidade de overrides manuais para rodar a suíte local de testes.

## Requisitos funcionais

- [ ] `kb compile` deve aceitar `--workers` e produzir o mesmo resultado funcional do fluxo atual quando `--workers=1`
- [ ] quando `--workers>1`, a geração dos artigos deve poder ocorrer em paralelo sem corromper `kb_state/manifest.json`, `kb_state/knowledge.json` ou `wiki/_index.md`
- [ ] a persistência dos artefatos gerados deve ocorrer em ordem estável e determinística
- [ ] falhas de um arquivo não devem abortar imediatamente o lote inteiro; o comando deve processar os demais alvos e reportar quais falharam ao final
- [ ] `_index.md` deve ser atualizado no máximo uma vez por execução do lote, ao final da persistência
- [ ] o comportamento padrão de `kb compile` deve ser sem commit automático; commit só pode ocorrer quando explicitamente pedido pelo usuário
- [ ] `kb import-book --compile` deve reutilizar o mesmo modelo de geração paralela + persistência serial para os capítulos importados
- [ ] falhas ao compilar capítulos importados não devem impedir a persistência dos capítulos bem-sucedidos; o comando deve reportar as falhas ao final

## Requisitos técnicos

- separar a geração LLM de um artefato puro da fase de escrita em disco e atualização de estado
- impedir escrita concorrente em wiki, manifest, knowledge e índice
- manter compatibilidade de `compile_file()` como wrapper interno para chamadas existentes
- preservar fallback para erro de resource limit e guardrails de conteúdo sensível
- manter os testes offline com LLM mockado
- permitir executar `python -m pytest` sem precisar sobrescrever `addopts` manualmente em ambientes sem `pytest-cov`

## Mudanças de API

### CLI

- `kb compile [target] [--workers N] [--allow-sensitive] [--commit]`
- `kb import-book <arquivo>... [--compile] [--workers N] [--allow-sensitive] [--commit]`

### Comportamento

- `--workers` controla o paralelismo da fase de geração; `1` preserva o fluxo serial
- `--commit` habilita commit explícito; a ausência da flag mantém escrita local sem commit
- `compile_file()` permanece disponível como wrapper compatível sobre geração + persistência
- `import-book --compile` aplica o mesmo contrato de lote seguro usado por `kb compile`

## Testes

- Unit: `compile_to_artifact`, `persist_artifact`, `compile_many`, fallback de resource limit, ausência de commit por default
- Integration: lote com múltiplos arquivos, persistência determinística, atualização única do índice, falha parcial sem abortar o lote inteiro, `import-book --compile` com capítulos compilados em batch
- Manual:
  1. `kb compile --workers 1`
  2. `kb compile --workers 4`
  3. `kb compile --workers 4 --commit`
  4. `kb import-book livro.epub --compile --workers 4`

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 1 dia |
| Bloqueador | não   |
| Risk       | médio |

## Dependências

- `sensitive-execution-controls` já concluída como base de flags operacionais

## Notas

### Casos de erro

- erro de provider/resource limit em um arquivo → retry pré-processado apenas para aquele arquivo
- erro definitivo em um arquivo do lote → arquivo entra no relatório de falhas e os demais seguem
- erro definitivo em um capítulo importado → capítulo entra no relatório de falhas e os demais seguem
- alvo inexistente ou sem arquivos válidos → CLI mantém comportamento atual de saída sem processamento

### Fora de escopo

- paralelizar writes em disco ou updates de estado
- alterar `qa`, `heal` ou outros comandos além de `import-book --compile` para o mesmo modelo paralelo
- introduzir commits automáticos por configuração global
