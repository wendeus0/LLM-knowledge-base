# Mapa de temas proposto — insumo do ticket 006

> Gerado em 2026-07-31 para a decisão do ticket 006. **Proposta, não decisão.** O agrupamento por cosseno é medido; a atribuição dos artigos sem cluster é inferida por título e precisa de verificação antes de virar migração.

## Como foi feito

Híbrido, como o grilling do 006 pediu:

1. **Esqueleto medido** — clustering single-linkage por cosseno sobre a média L2-normalizada dos chunks de cada artigo, no índice de embeddings que já existe. Limiar 0,88: **116 grupos cobrindo 469 artigos (45%)**.
2. **Nomeação e cauda** — os 568 artigos sem cluster foram atribuídos por leitura de título. É a parte frágil desta proposta.

Limiares testados e por que 0,88:

| Limiar | Grupos | Agrupados | Maior grupo |
|---:|---:|---:|---:|
| 0,95 | 980 | 110 (11%) | 3 |
| 0,90 | 817 | 331 (32%) | 17 |
| **0,88** | **684** | **469 (45%)** | **31** |
| 0,85 | 455 | 679 (65%) | 148 |
| 0,82 | 222 | 862 (83%) | 637 |

A janela é estreita: de 0,88 para 0,85 o maior grupo salta de 31 para 148, e em 0,82 vira um caroço de 637 artigos — 61% do corpus num grupo só. A qualidade desmorona antes de a cobertura chegar a dois terços.

## O achado que muda a decisão

**O corpus não é 1.037 artigos sobre temas. É ~40 livros fatiados em 1.037 capítulos.**

Os clusters estão reconstruindo os livros, não descobrindo temas: C1 são 31 capítulos de *Learning DDD* + *Implementing DDD*; C3 são 16 de *Property-Based Testing with PropEr*; C4 são 15 de *Automate the Boring Stuff*; C7 são 11 de *Observability Engineering*; C11 são 9 de *Mind in Society* (Vygotsky); C17 são 8 de *Make It Stick*.

Os 568 sem cluster são o mesmo fenômeno pelo avesso: o cosseno não os juntou porque cada capítulo fala de uma coisa **diferente dentro do mesmo livro**. `circuit-breaker.md`, `fail-fast.md`, `dogpile.md`, `falhas-em-cascata.md`, `criar-back-pressure.md` são todos *Release It!*, e nenhum se parece com o outro o suficiente para agrupar.

**Consequência para o 006:** o critério de agrupamento mais forte não é cosseno nem LLM — é a **proveniência**, que já existe em `raw/books/*/metadata.json` e que o `manifest.json` inexistente deveria ligar ao artigo. O ticket 001 protegeu essas fontes; elas sabem qual capítulo veio de qual livro.

## Temas propostos

Contagem exata só para os clusters medidos. Para os demais, a atribuição é proposta.

### Arquitetura e design de software

| Tema | Origem | Clusters | Ordem de grandeza |
|---|---|---|---|
| Domain-Driven Design | *Learning DDD*, *Implementing DDD*, *Domain-Driven Refactoring* | C1 (31), C23 (5), C60 (2) | ~60 com a cauda (entities, factories, domain services, eventstorming, bounded contexts) |
| Estabilidade e falhas em produção | *Release It!* | C24 (5), C53 (3) | ~50 (circuit breaker, fail fast, dogpile, back pressure, governor, casos de estudo) |
| Arquitetura de software (fundamentos e trade-offs) | *Fundamentals of Software Architecture*, *The Hard Parts* | C33 (4) | ~40 (acoplamento, decomposição, granularidade, ADRs, estilos) |
| Arquitetura hexagonal e limpa | *Get Your Hands Dirty on Clean Architecture* | — | ~12 (web adapter, adaptador de persistência, casos de uso, fronteiras) |
| Arquitetura orientada a eventos | *Event-Driven Architecture*, livro de Go | C22 (5), C35 (3) | ~20 (event sourcing, NATS, workflows distribuídos) |
| Padrões de integração empresarial | *Enterprise Integration Patterns* | C52 (3), C55 (3) | ~20 (canais, endpoints, loan broker, estilos) |
| Design de APIs | *API Design Patterns* | C8 (10) | ~30 (soft deletion, field masks, filtragem, copy/move) |

### Dados e sistemas distribuídos

| Tema | Origem | Clusters | Ordem de grandeza |
|---|---|---|---|
| Sistemas de dados intensivos | *DDIA* | C34 (4), C54 (3) | ~30 (consistência, consenso, codificação e evolução, dados derivados) |
| Motores de banco de dados | *Database Internals* | C51 (3) | ~15 (B-Trees, LSM, recuperação) |
| Performance de SQL e índices | *SQL Performance Explained* | — | ~15 (cláusula WHERE, clusterização, joins, índices lentos) |
| Observabilidade | *Observability Engineering* | C7 (11) | ~35 (OpenTelemetry, eventos estruturados, SLO, amostragem, telemetria) |
| Engenharia de dados | *Fundamentals of Data Engineering* | C38 (3) | ~10 |

### Algoritmos e matemática

| Tema | Clusters | Ordem de grandeza |
|---|---|---|
| Análise de complexidade e notação assintótica | C14 (8), C21 (6), C32 (4), C69 (2), C70 (2) | ~30 |
| Recorrências e teorema mestre | C9 (9), C50 (3) | ~15 |
| Ordenação | C19 (6), C20 (6) | ~15 |
| Grafos e caminhos mínimos | C12 (8), C13 (8), C41 (3), C68 (2) | ~25 |
| Árvores de busca e balanceamento | C15 (8), C28 (4), C71 (2) | ~20 |
| Tabelas hash | C16 (8) | ~10 |
| Heaps e filas de prioridade | C43 (3), C45 (3) | ~10 |
| Programação dinâmica | C31 (4), C47 (3), C48 (3), C49 (3) | ~20 |
| Strings e suffix arrays | C30 (4) | ~8 |
| Union-Find | C46 (3) | ~5 |
| Fenwick tree e consultas de intervalo | C42 (3) | ~5 |
| Álgebra linear | C26 (4), C44 (3) | ~15 |
| Geometria analítica e cálculo vetorial | C56 (3), C72 (2) | ~8 |
| Probabilidade e distribuições | C66 (2) | ~5 |
| Panorama de algoritmos (índices e sumários de livro) | C2 (16), C27 (4), C29 (4) | ~25 |

### IA e machine learning

| Tema | Origem | Clusters | Ordem de grandeza |
|---|---|---|---|
| Design de sistemas de ML | *Designing ML Systems* | C6 (12), C61 (2) | ~25 |
| LLMs e engenharia de prompt | *Hands-On LLMs* | C18 (7), C64 (2) | ~20 |
| Agentes de IA | *Building Applications with AI Agents* | C62 (2), C63 (2), C67 (2) | ~15 |
| Deep learning e redes neurais | *Deep Learning with Python* | C37 (3), C39 (3) | ~15 |
| Engenharia de IA | *AI Engineering* | C36 (3) | ~10 |

### Python

| Tema | Origem | Clusters | Ordem de grandeza |
|---|---|---|---|
| Python fundamentos e automação | *Automate the Boring Stuff* | C4 (15) | ~25 |
| Python avançado e modelo de dados | *Effective Python*, *Fluent Python* | C5 (13), C25 (5) | ~30 |

### Testes e código legado

| Tema | Origem | Clusters | Ordem de grandeza |
|---|---|---|---|
| Property-based testing | *PBT with PropEr* | C3 (16) | ~25 |
| Código legado e refatoração | *Working Effectively with Legacy Code* | C57 (3) | ~25 |

### Aprendizagem

| Tema | Origem | Clusters | Ordem de grandeza |
|---|---|---|---|
| Ciência da aprendizagem | *Make It Stick* | C17 (8), C58 (3), C59 (3) | ~40 |
| Vygotsky e desenvolvimento | *Mind in Society* | C11 (9) | ~15 |

### Harness e IA aplicada ao desenvolvimento

| Tema | Clusters | Ordem de grandeza |
|---|---|---|
| Agentes de código e harness | C10 (9) | ~20 |

## Ruído que o filtro da 011 não pegou

Artigos compilados de capítulos que a taxonomia de ruído da feature 011 (agradecimentos, dedicatórias, prefácios, colofão, endorsements) deveria ter barrado — mas que já estavam no corpus quando o filtro nasceu:

- `dedicatorias.md`
- `bolakale-aremu-perfil-do-autor.md`
- `beneficios-da-assinatura-packt-e-recursos-complementares-do-.md`
- `documento-indeterminado-aviso-de-versao-eletronica.md`
- `download-de-recursos-de-treinamento-e-obtencao-de-ajuda-adic.md`
- `guia-para-este-livro.md`
- `coruja-de-oma-strix-butleri.md` — exemplo de taxonomia biológica dentro de um livro técnico

O `kb noise scan` existe e é retroativo. Rodá-lo antes de qualquer reagrupamento é barato e reduz o corpus a reagrupar.

## Onde esta proposta é frágil

1. **A atribuição dos 568 sem cluster é inferência por título**, não medição. Um artigo chamado `fluxo-de-controle.md` pode ser de qualquer um dos livros.
2. **A ordem de grandeza por tema é estimativa.** Só os números de cluster são exatos.
3. **Um capítulo pode pertencer a dois temas** — a cardinalidade que o grilling do 004 deixou explicitamente em aberto. Esta proposta assume um destino por capítulo, o que a medição pode invalidar.
4. **Livros que aparecem em dois temas** existem: *DDIA* alimenta "sistemas de dados intensivos" e "motores de banco de dados"; o livro de Go alimenta "arquitetura orientada a eventos" e "padrões de integração".

## Recomendação

O critério de agrupamento mais defensável **não é cosseno nem LLM: é a proveniência**, que existe em `raw/books/*/metadata.json` e está protegida desde o ticket 001. Cosseno e LLM são aproximações do que o metadado já sabe — e a razão de precisarmos aproximar é que o `manifest.json` nunca foi materializado.

Ordem sugerida, da mais barata à mais cara:

1. `kb noise scan` retroativo — tira o ruído antes de reagrupar
2. Reconstruir a ligação artigo → fonte a partir de `raw/books/*/metadata.json` (é a mesma dívida que bloqueia o recompile e o `kb deepen`)
3. Agrupar por livro, usando os clusters de cosseno para detectar temas que **atravessam** livros (DDD é o caso mais claro: dois livros, um tema)
4. LLM nomeia e resolve os casos que não se encaixam

Isso torna o "lote único" executável com verificação em cada etapa, em vez de uma rodada de 1.037 chamadas apostando num limiar.
