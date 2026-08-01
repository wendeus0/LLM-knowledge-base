# ADR 0018 — Política de corpus: artigo de tema no lugar de artigo de capítulo

- **Status:** Aceito
- **Data:** 2026-07-31
- **Origem:** map [política de corpus](../research/2026-07-30-politica-de-corpus/MAP.md), tickets 001–007
- **Supera parcialmente:** [ADR 0013](0013-claim-centric-lifecycle-and-hybrid-retrieval-foundation.md) (Fase 3 ganha conteúdo concreto)
- **Reativa:** decisões 1, 3 e 10 de [`011/DOMAIN.md`](../../features/_archived/011-corpus-noise-filter/DOMAIN.md)

## Contexto

A pergunta que abriu o esforço foi prática: *"posso usar o kb para estudar Google Dorking agora, ou preciso refazer o vault?"* A resposta medida foi **nenhum dos dois**.

O retrieval já tinha sido consertado ([ADR-0017](0017-hybrid-retrieval-with-measured-llm-rerank.md)) e melhorou de novo durante este esforço: `recall@5` foi de 0,467 para **0,526** e MRR de 0,343 para **0,352**, ao corrigir a colisão de slug e o snippet vazio do candidato exclusivamente semântico.

O corpus também não era o problema que se supunha. A medição do ticket 003 derrubou a hipótese de rasura: mediana de **10 headings por artigo**, 93% com cinco ou mais, nenhum sem heading. O que a medição encontrou foi outra coisa — **1.035 de 1.037 artigos sem nenhuma referência**, **59 pares** com cosseno ≥ 0,95, e proveniência perdida.

O gargalo é a **camada de compilação**, e o diagnóstico final é mais específico do que "os artigos são rasos":

> **O corpus não é 1.037 artigos sobre temas. São ~40 livros fatiados em 1.037 capítulos.**

O clustering por cosseno a 0,88 agrupa 45% do corpus, e os grupos **reconstroem os livros**: 31 capítulos de *Learning DDD* + *Implementing DDD*, 16 de *Property-Based Testing with PropEr*, 15 de *Automate the Boring Stuff*, 11 de *Observability Engineering*. Os 568 artigos sem cluster são o mesmo fenômeno pelo avesso — `circuit-breaker.md`, `fail-fast.md`, `dogpile.md` e `criar-back-pressure.md` são todos do *Release It!*, e o cosseno não os junta porque cada capítulo fala de coisa diferente dentro do mesmo livro.

## Decisão

### 1. A wiki é produto

O artigo compilado é o entregável, lido diretamente. **Artigo raso é bug, não design.** Isso reativa a decisão 10 de `011/DOMAIN.md` (mínimo de referências bibliográficas reais) e torna dívida — não isenção — os 1.035 artigos sem referência.

### 2. O artigo é de tema e multi-fonte

O compile deixa de ser 1 documento → 1 artigo e passa a costurar **várias fontes** sobre um tema.

Isto não é preferência estética: é a única saída de uma **impossibilidade estrutural**. Sob o compile 1:1, um artigo vindo de um capítulo tem exatamente uma fonte bibliográfica; exigir cinco dele é impossível por construção, não por esforço do modelo. Ou o min-refs caía, ou o artigo passava a costurar — e costurar foi a escolha.

O artigo de tema é **gerado sob demanda**, quando o usuário pede o tema. Nunca por job automático.

### 3. Os 1.037 artigos são reagrupados em lote, pela proveniência

Recorte de capítulo vira recorte de tema. Os originais vão **todos** para `_chapters/` — fora do índice e da busca pela convenção `_*`, sem sair do disco, o que torna a operação reversível.

**O critério de agrupamento é a proveniência** (`raw/books/*/metadata.json`), não cosseno nem LLM. Os dois são aproximação de um dado que o sistema já tem e não usa porque o `manifest.json` nunca ligou artigo à fonte. O cosseno tem outro papel: detectar tema que **atravessa** livros (DDD é o caso claro — dois livros, um tema).

Ordem de execução, da mais barata à mais cara, com verificação em cada etapa:

1. `kb noise scan` retroativo
2. reconstruir a ligação artigo → fonte
3. agrupar por livro, com o cosseno achando os temas transversais
4. LLM nomeia e resolve o resto, com aprovação humana

**Perder retrievability do detalhe absorvido é aceito** — e em troca o gate de qualidade passa a ser **"não perdeu informação"**, não só "tem referências".

### 4. A fonte é livro e paper, curados pelo usuário

Web aberta fica **fora da rotina**. O que atravessa a fronteira é escolhido por você, e a curadoria fica no humano, no ponto em que é barata.

- `discovery` fica, **só com arXiv**; Google News sai.
- `kb ingest <url>` continua para uso deliberado, sem job automático.
- **Auto-commit permanece desligado** (`KB_DISCOVERY_AUTOCOMMIT`), confirmando o default defensivo adotado em resposta ao achado F-02 da auditoria de segurança.
- Livro novo sobre tema existente **marca o tema como stale**; não reescreve o que já foi lido.

### 5. Não há detecção automática de lacuna

**Derrubada por medição.** A decisão do grilling era limiar de score no retrieval; medi antes de fixar, e o score não separa acerto de erro.

Golden de 152 casos, híbrido sem rerank, score do primeiro resultado:

| | n | mín | mediana | máx |
|---|---:|---:|---:|---:|
| acertou | 63 | 0,0367 | 0,0532 | 0,0641 |
| errou | 89 | 0,0361 | 0,0502 | 0,0636 |

As faixas se sobrepõem quase por inteiro. Um limiar que pegue dois terços das lacunas faz o sistema dizer "não sei" em **27 das 63 perguntas que sabia responder**.

A causa é estrutural: RRF é soma de inversos de posição e mede **concordância entre canais**, não confiança na resposta. Não vira medida de confiança com calibração — vira com outra métrica.

**Consequência em cascata:** sem detecção de lacuna, não há consulta a LLM grande externa, e a **propriedade offline do ADR-0017 fica preservada** — resultado, não decisão separada. E o kb não sugere leitura, então o modo de falha de alucinar bibliografia some junto.

### 6. A superfície é a tela própria, que absorve a leitura

A tela é superfície de **autoria e leitura**: pedir o tema, acompanhar a geração, ler o resultado. **v1 já fecha o ciclo.** O Obsidian sai da divisão de trabalho, reativando integralmente a decisão 1 de `011/DOMAIN.md`.

Argumento que apareceu na verificação: **o Obsidian não honra a convenção `_*`** — ela exclui do índice do `kb`, não dele. Depois do reagrupamento, ele mostraria ~30 temas misturados com 1.037 capítulos, salvo exclusão configurada à mão. A política do item 3 degrada o Obsidian como leitor, o que remove o argumento "ele já faz bem".

É o item mais caro desta política, por larga margem. O que o reduz é o corpus visível encolher de 1.037 para ~30.

## Pré-requisitos técnicos

Nenhum existe hoje. Todos bloqueiam a execução e nenhum é decisão nova — são consequências das decisões acima.

| Pré-requisito | Bloqueia |
|---|---|
| Rastreabilidade de origem por trecho | referência bibliográfica **real**; sem ela o gate conta linhas numa seção e conta linha inventada igual |
| `manifest.json` materializado | ligar artigo à fonte — reagrupamento (3), `kb deepen`, recompile e marca de stale (4) |
| Retrieval sobre `library/` | compile multi-fonte (2) |
| Medição de sobreposição temática | cardinalidade artigo de tema × capítulo |
| Medida de confiança da resposta | detecção de lacuna (5), se algum dia voltar |

## Efeito no BACKLOG da engenharia reversa

| Item | Efeito |
|---|---|
| **V1** — `kb lint` audita 20 de 1.037 | **Validado e mais urgente.** Com a wiki como produto, auditar 2% do corpus sem avisar é falha de gate. |
| **V2** — índice persistente | **Entregue** em 2026-07-31 (PR #58): 8,7× mais rápido, paridade de resultado provada. |
| **V5** — dedup e merge-before-create no compile | **Absorvido e ampliado.** O V5 pedia medição antes de implementar; a medição foi feita (59 pares ≥ 0,95, 296 ≥ 0,90, 1.432 ≥ 0,85) e mostrou que dedup é caso particular do reagrupamento por tema. Não implementar V5 isolado. |
| **V7** — tombstone em vez de apagar | **Validado.** `_chapters/` é a materialização disso, e as duas políticas de remoção que convivem (`heal.py` faz `unlink`, `archive.py` move com backup) precisam ser reconciliadas antes do lote. |
| **V10** — taxonomia editorial de confiança | **Reordenado para depois.** Faz sentido sobre artigo de tema, não sobre capítulo. |
| **V11** — índice autoritativo | **Invalidado, com reforço.** O V2 entregue confirma: índice derivado e descartável dá o ganho sem a segunda fonte de verdade. |
| Compatibilidade multi-vault | Segue fora de escopo; a feature 010 foi arquivada em 2026-07-31. |

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Manter os artigos como estão | Manter por inércia não é decidir. A medição mostrou granularidade errada, não só profundidade insuficiente |
| Recompilar 1:1 com prompt melhor | Não resolve o min-refs (uma fonte por artigo) nem a fragmentação temática; e reproduziria em escala o defeito que 002 achou e que nenhum gate pega |
| Convergência sob demanda, sem lote | Deixaria a wiki misturada por tempo indeterminado, com capítulo e tema lado a lado |
| Agrupar por cosseno | O limiar é frágil: de 0,88 para 0,85 o maior grupo salta de 31 para 148; em 0,82 vira um caroço de 637 artigos. E aproxima um dado que a proveniência já tem |
| Admitir web aberta na rotina | O gate de injeção (PR #54) torna possível, não desejável: curadoria humana no ponto barato vale mais que volume |
| Limiar de score para lacuna | Medido e derrubado: as distribuições se sobrepõem |
| Obsidian como leitor permanente | A convenção `_*` não vale nele; depois do reagrupamento a experiência piora sem configuração manual |

## Gatilhos de revisão

- **A medição de sobreposição temática mostrar que capítulo alimenta vários temas com frequência** — cai o critério de arquivamento por absorção, e `_chapters/` passa a ser camada permanente em vez de transitória.
- **O custo da tela própria se mostrar proibitivo na fase de `prototype`** — reabre a divisão de trabalho com o Obsidian (item 6).
- **Surgir medida de confiança da resposta** (grader de fidelidade) — reabre a detecção automática de lacuna (item 5), junto com os dois sinais que esta rodada não testou: cosseno do canal semântico puro e margem entre 1º e 2º colocado.
- **O reagrupamento produzir artigos de tema que perdem informação** — o gate de "não perdeu informação" falha, e a decisão de mandar `_chapters/` para fora da busca (item 3) volta à mesa.

## Consequências

**Positivas.** A política é executável sem depender de infraestrutura nova de terceiros, preserva a propriedade offline, e cada decisão cara passou por medição — três delas foram derrubadas ou reformuladas pelo número (rasura do corpus, limiar de lacuna, agrupamento por cosseno).

**Negativas, declaradas.** O item 6 é caro. O reagrupamento em lote reescreve o corpus inteiro de uma vez, e a reversibilidade depende de `_chapters/` ter sido preservado corretamente. Os cinco pré-requisitos técnicos precisam existir antes de qualquer execução, e o primeiro deles — proveniência por trecho — foi definido na feature 011 em julho e nunca implementado.

**O que fica pendente e por quê.** A cardinalidade artigo de tema × capítulo foi adiada de propósito: decidir sem medir a sobreposição seria escolher no escuro, e a medição é barata. Vai para `PENDING_LOG.md`, não para dentro deste ADR.
