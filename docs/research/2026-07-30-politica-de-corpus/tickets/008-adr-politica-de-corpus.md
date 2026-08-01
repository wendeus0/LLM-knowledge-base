# O ADR da política de corpus

Type: task
Status: resolved (2026-07-31)
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

## Answer

**Entregue: [ADR-0018](../../../adr/0018-corpus-policy-theme-articles-over-chapter-articles.md)** — política de corpus, artigo de tema no lugar de artigo de capítulo.

O ADR responde as quatro perguntas do ticket (wiki produto ou insumo, origem do conhecimento novo, destino do corpus atual, superfície de leitura), declara o efeito sobre os itens V1/V2/V5/V7/V10/V11 do BACKLOG anterior, lista os cinco pré-requisitos técnicos que bloqueiam execução, e registra quatro gatilhos de revisão no formato do ADR-0017.

**Superação verificada, como o ticket exigia:**
- **ADR-0013** — a Fase 3 ("automação operacional e quality gates") ganha conteúdo concreto: o gate de qualidade passa a ser "não perdeu informação". Não é superado por omissão.
- **ADR-0011** (externalizar corpus) — intocado. A decisão do ticket 001 manteve o golden no vault, agora com remote privado; a separação engine × corpus segue valendo.
- **ADR-0017** — reforçado, não superado: a propriedade offline fica preservada como consequência de não haver detecção automática de lacuna.

**O que ficou pendente e por quê** (vai para `PENDING_LOG.md`, não para dentro do ADR): a cardinalidade artigo de tema × artigo-de-capítulo. Decidir sem medir a sobreposição temática seria escolher no escuro, e a medição é barata.

**Fechamento do map:** `WAYFINDER_CLEAR` registrado em `memory/active_fronts.md`.
