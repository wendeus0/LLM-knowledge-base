# ADR 0009 — Store de outputs de QA separado da wiki

> **Nota histórica:** este ADR foi escrito quando `raw/`, `wiki/` e `outputs/` ainda viviam dentro do repositório principal. No modelo recomendado atual, esses diretórios vivem no `KB_DATA_DIR` do usuário.

- **Status:** Aceito
- **Data:** 2026-04-06

## Contexto

O comando `kb qa --file-back` arquivava respostas diretamente em `wiki/`, misturando conteúdo compilado pelo pipeline canônico (`compile`) com conteúdo gerado ad-hoc por perguntas livres. Isso gerava dois problemas:

1. `wiki/` ficava poluída com artigos sem frontmatter canônico, não rastreados pelo manifesto.
2. Não havia como distinguir entre "conhecimento compilado e revisado" e "resposta de QA arquivada".

## Decisão

Respostas de `kb qa --file-back` vão para **`outputs/`** por padrão, não para `wiki/`. A wiki continua recebendo apenas conteúdo gerado por `compile`, `heal` e `lint`.

- `--to-wiki` mantém o comportamento antigo como opt-in explícito.
- `outputs/` é um store de rascunhos e capturas de QA; não passa por healing automático.
- O store é implementado em `kb/outputs.py`.

## Consequências

### Positivas
- `wiki/` mantém integridade semântica: só contém artigos compilados pelo pipeline canônico
- separação clara entre conhecimento revisado e capturas brutas de QA
- outputs de QA ficam acessíveis sem contaminar o vault Obsidian

### Negativas
- usuário que espera file-back na wiki precisa usar `--to-wiki` explicitamente
- `outputs/` não participa do grafo de wikilinks por padrão

## Alternativas consideradas

### A1. Subdiretório `wiki/qa/` para file-back
- **Rejeitada:** segrega visualmente mas não resolve a contaminação semântica do vault.

### A2. Manter file-back na wiki sem separação
- **Rejeitada:** causa os problemas descritos no contexto.
