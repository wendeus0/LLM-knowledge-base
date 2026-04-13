# ADR 0015 — Taxonomia de tópicos configurável em runtime

- Status: Aceito
- Data: 2026-04-12

## Contexto

`kb` usava uma lista fixa de tópicos em `kb/config.py` (`cybersecurity`, `ai`, `python`, `typescript`). Isso acopla a engine a um corpus específico e exige edição de código para adaptar a taxonomia de um vault diferente.

## Decisão

1. Os tópicos suportados passam a ser configurados por `KB_TOPICS`.
2. Quando `KB_TOPICS` não estiver definido ou produzir lista vazia, a engine usa a lista histórica como default.
3. `general` continua sendo fallback implícito e não entra na lista configurável.
4. `compile` e `qa` devem consumir helpers de configuração para prompts e resolução do diretório wiki.

## Consequências

### Positivas

- desacopla a engine de um domínio fixo
- reduz necessidade de forks locais para adaptar taxonomia
- mantém compatibilidade retroativa quando a variável não é usada

### Negativas

- a taxonomia passa a depender da configuração do ambiente
- tópicos mal configurados podem fragmentar a organização da wiki

## Alternativas consideradas

### A1. Manter lista fixa no código

- Rejeitada por exigir mudança de código para uma decisão operacional do corpus.

### A2. Persistir tópicos em `kb_state/manifest.json`

- Adiada. Seria mais flexível, mas introduz governança e migração de estado desnecessárias para a primeira fase.

## Referências

- `kb/config.py`
- `kb/compile.py`
- `kb/qa.py`
- `docs/architecture/ARCHITECTURE.md`
