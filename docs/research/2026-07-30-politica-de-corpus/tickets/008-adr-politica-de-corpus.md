# O ADR da política de corpus

Type: task
Status: open
Blocked by: 004-wiki-produto-ou-insumo, 005-origem-do-conhecimento, 006-destino-dos-artigos-atuais, 007-o-que-a-tela-faz

## Question

Consolidar as decisões travadas em um ADR — o destination deste map.

O ADR precisa responder, com a evidência de cada ticket linkada:

1. **A wiki é produto ou insumo** (004), e a consequência disso para o gate de profundidade do compile.
2. **De onde vem conhecimento novo** (005): fonte admitida, quem dispara a aquisição, como se detecta lacuna, e o que fazer com a dependência de LLM externa.
3. **O destino do corpus atual** (006): manter, arquivar ou recompilar, com o pré-requisito técnico nomeado.
4. **A superfície de leitura** (007): Obsidian, tela própria, ou ambos com divisão de trabalho declarada.

Além disso, o ADR deve declarar explicitamente:

- **Quais itens do [BACKLOG anterior](../../2026-07-28-engenharia-reversa/BACKLOG.md) a política valida, invalida ou reordena.** V2 (índice persistente) e V5 (dedup no compile) são os mais sensíveis — V5 depende diretamente do que 003 medir, e V2 muda de prioridade conforme a wiki seja produto ou insumo.
- **O que fica pendente e por quê** — a névoa que sobreviver ao map vai para `PENDING_LOG.md`, não para dentro do ADR.
- **Gatilhos de revisão**, no formato que o ADR-0017 usa (`:67-71`): sob quais condições medidas esta política deve ser reaberta.

Superação a verificar: o ADR-0013 (fundação claim-centric, retrieval híbrido em 3 fases) tem eixos não executados, e o ADR-0011 (externalizar corpus para fora do repo) pode ser tocado pela decisão de 001 sobre onde o golden mora. Nenhum dos dois deve ser superado por omissão.

**Fechamento do map** (`WAYFINDER_CLEAR`, obrigatório e completo):

- destination + `DOMAIN.md` deste diretório entregues como insumo do `spec-pipeline`;
- linha de fechamento em `memory/active_fronts.md`;
- regra de casa do diretório registrada nas Notes do `MAP.md`.

Emitido via `adr-manager`, com espelho em `memory/stable_decisions.md`.

## Answer

<!-- preencher na resolução -->
