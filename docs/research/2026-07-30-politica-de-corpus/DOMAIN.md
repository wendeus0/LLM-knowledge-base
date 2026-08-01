# DOMAIN — Política de corpus do kb

> Produzido pelo `grill-with-docs` sobre o ticket 004 (2026-07-31). Glossário e invariantes do esforço; não é SPEC. Decisões de cada ticket ficam no `## Answer` do ticket.

## Glossário

| Termo | Definição |
|-------|-----------|
| **Artigo de tema** | O entregável do kb. Documento sobre um assunto, costurado a partir de **várias fontes** de `library/` e dos artigos-de-capítulo relevantes. Gerado **sob demanda**, quando o usuário pede o tema. É isto que vive em `wiki/` e é lido no Obsidian |
| **Artigo-de-capítulo** | O que os 1.037 artigos atuais são: recorte de um capítulo de um livro, 1 documento fonte → 1 artigo. Deixa de ser entregável e passa a ser **camada de insumo** |
| `_chapters/` | Destino dos artigos-de-capítulo depois de absorvidos por um artigo de tema. A convenção `_*` do vault já os exclui do índice e da busca (mesmo mecanismo de `_summaries/` e `_sources/`). Não é descarte: continuam em disco, como insumo e para auditoria |
| **Compile multi-fonte** | O compile que a política exige: muitos documentos → um artigo. Diferente do compile atual (1:1). Pressupõe retrieval sobre `library/`, não sobre `wiki/` |
| **Aprofundar** | Operação nova (`kb deepen` ou equivalente): relê a fonte original e reescreve um artigo com mais profundidade. Distinta de `heal`, que é proibido de tocar conteúdo substantivo (`kb/heal.py:17-25`) |
| **Referência bibliográfica real** | Herdado de [`011/DOMAIN.md`](../../../features/_archived/011-corpus-noise-filter/DOMAIN.md): citação da fonte original com autor, título e capítulo — não wikilink interno. Exige rastreabilidade de origem por trecho, que **não existe em `kb/`** |
| **Wiki como produto** | O artigo compilado é o entregável, lido diretamente. Oposto de "wiki como insumo", onde o artigo só existiria para o `qa` recuperar. **Decidido: produto** (ticket 004) |

## Decisões fechadas (grilling do 004, 2026-07-31)

1. **A wiki é produto.** O usuário abre o Obsidian e lê o artigo. Artigo raso é **bug**, não design.
2. **A superfície de leitura é o Obsidian hoje, e o app próprio é o destino.** Reafirma a decisão 1 da 011 e resolve a contradição com o `CLAUDE.md`, que declarava o Obsidian como frontend oficial sem ressalva: ele é o atual, não o final.
3. **O min-refs vale e o corpus atual é dívida** — os 1.035 artigos sem referência estão abaixo do padrão, não isentos dele.
4. **O artigo passa a costurar várias fontes.** Resolve a impossibilidade estrutural do min-refs 5 sob o compile 1:1 (um capítulo tem uma fonte bibliográfica; exigir cinco dele é impossível por construção, não por esforço do modelo).
5. **Nasce uma operação de aprofundar.** `heal` continua proibido de alterar conteúdo substantivo; melhorar artigo passa a ser comando próprio.
6. **O artigo de tema é gerado sob demanda**, quando o usuário pede o tema — não automaticamente no import.
7. **Artigo-de-capítulo absorvido vai para `_chapters/`**, saindo da vista e da busca sem sair do disco.
8. **O retrieval é fundação do app próprio** (ticket 007), não só do `qa`. O investimento do ADR-0017 e dos PRs de 2026-07-31 permanece justificado sob a decisão "wiki é produto".

## Decisões fechadas (grilling do 006, 2026-07-31)

9. **O reagrupamento é lote único**, não convergência sob demanda; os originais em `_chapters/` tornam a operação reversível.
10. **Todos os 1.037 vão para `_chapters/`**, absorvidos ou não.
11. **Perder retrievability do detalhe absorvido é aceito** — e em troca o gate de qualidade passa a ser **"não perdeu informação"**, não só "tem referências".
12. **O critério de agrupamento é a proveniência** (`raw/books/*/metadata.json`), não cosseno nem LLM. Os dois são aproximação de um dado que o sistema já tem e não usa porque o `manifest.json` nunca ligou artigo à fonte.
13. **O cosseno tem outro papel:** detectar tema que **atravessa** livros (DDD = dois livros, um tema).

## Decisões fechadas (grilling do 005, 2026-07-31)

14. **Fonte admitida: livros e papers, curados pelo usuário.** Web aberta fica fora da rotina; `discovery` mantém só arXiv, `kb ingest <url>` fica para uso deliberado, auto-commit segue desligado.
15. **Livro novo sobre tema existente marca o tema como stale** — não reescreve o que já foi lido sem ordem.
16. **Não há detecção automática de lacuna.** Derrubada por medição (abaixo). O usuário diz quando falta; o kb não sugere leitura e portanto não alucina bibliografia.
17. **A propriedade offline do ADR-0017 fica preservada** — consequência de 16, não decisão separada.

## Decisões fechadas (grilling do 007, 2026-07-31)

18. **A tela é superfície de autoria e leitura.** Primeiro trabalho: pedir o tema e ver o artigo nascer.
19. **A tela absorve a leitura; o Obsidian sai.** A decisão 1 da `011/DOMAIN.md` (app próprio como superfície única) volta a valer integralmente.
20. **v1 já lê** — o ciclo fecha no primeiro dia, sem fase dependente de outra ferramenta.

Argumento que apareceu na verificação: **o Obsidian não honra a convenção `_*`** (ela exclui do índice do `kb`, não do Obsidian). Depois da migração do 006 ele mostraria ~30 temas misturados com 1.037 capítulos, a menos que se configure exclusão manual. A política do 006 degrada o Obsidian como leitor.

Custo declarado: é o item mais caro de todo o map. O que o reduz é o corpus visível encolher de 1.037 para ~30.

## O que o score do retrieval não mede

**O score não separa acerto de erro.** Golden de 152 casos, híbrido sem rerank, score do primeiro resultado: acertos ficam entre 0,0367 e 0,0641; erros, entre 0,0361 e 0,0636. Sobreposição quase total. Um limiar que pegue dois terços das lacunas diz "não sei" em 27 perguntas que o sistema sabia responder.

A causa é estrutural: RRF é soma de inversos de posição e mede **concordância entre canais**, não confiança. Um artigo errado que os quatro canais concordam em rankear alto tira score alto.

**Consequência:** detectar lacuna exige uma métrica que o retrieval atual não produz. Vira pré-requisito, não parte da política. Detalhe e tabelas em [`tickets/005`](tickets/005-origem-do-conhecimento.md).

## O que o corpus é, medido

**Não são 1.037 artigos sobre temas. São ~40 livros fatiados em 1.037 capítulos.** O clustering a 0,88 agrupa 45% do corpus e os grupos reconstroem os livros; os 568 restantes são capítulos do mesmo livro falando de coisas diferentes. Detalhe e mapa proposto em [`MAPA-DE-TEMAS.md`](MAPA-DE-TEMAS.md).

## Entidades (deltas)

- **Artigo de tema** — entidade nova. Atributos que a política exige: tema, fontes (N), referências bibliográficas reais, artigos-de-capítulo absorvidos.
- **Artigo-de-capítulo** — entidade existente que **muda de papel**: de entregável para insumo.
- **Fonte** (`library/`) — deixa de ser só origem de import e passa a ser **corpus de retrieval** do compile multi-fonte.

## Relações (deltas)

- `Artigo de tema` **1:N** `Fonte` — a relação que o min-refs exige e que o compile 1:1 não permite.
- `Artigo de tema` **N:N?** `Artigo-de-capítulo` — **em aberto**. Um capítulo sobre autenticação serve a "segurança de APIs" e a "criptografia aplicada". Se a relação for N:N, capítulo nunca é "consumido" e o critério de arquivamento por absorção cai. **Decisão adiada: medir a sobreposição temática no corpus atual antes de fechar** (ticket 006).

## Invariantes (deltas)

- Artigo de tema sem referências bibliográficas reais não passa na validação — herdado da decisão 10 da 011, agora exequível porque o artigo tem várias fontes.
- `heal` nunca altera conteúdo substantivo; aprofundar é operação distinta e explícita.
- Artigo-de-capítulo absorvido sai do índice e da busca (`_chapters/`), nunca do disco.
- A geração de artigo de tema é disparada pelo usuário, nunca por job automático.

## Pré-requisitos técnicos que a política expõe

Nenhum destes existe hoje; todos bloqueiam a execução da política e nenhum é decisão nova — são consequências das decisões acima.

| Pré-requisito | Estado | Bloqueia |
|---|---|---|
| Rastreabilidade de origem por trecho | inexistente (grep em `kb/` não acha nada) | referência bibliográfica **real** — sem ela o gate só conta linhas, e conta linha inventada igual |
| `manifest.json` materializado | nunca criado neste vault | ligar artigo à fonte; sem ele `kb deepen` não sabe o que reler, e recompile duplica |
| Retrieval sobre `library/` | inexistente (retrieval é sobre `wiki/`) | compile multi-fonte — achar as passagens de várias fontes sobre um tema |
| Medição de sobreposição temática | não feita | fechar a cardinalidade `Artigo de tema` × `Artigo-de-capítulo` |

## Refs cruzadas

- [`011/DOMAIN.md`](../../../features/_archived/011-corpus-noise-filter/DOMAIN.md) — decisões 1 (app próprio), 3 (rastreabilidade por trecho), 10 (min-refs 5). As três voltam a valer sob "wiki é produto"; a 3 é pré-requisito da 10.
- [ADR-0013](../../adr/0013-claim-centric-lifecycle-and-hybrid-retrieval-foundation.md) — Fase 3 ("automação operacional e quality gates") é onde o gate de profundidade mora. Aceito, não executado.
- [ADR-0017](../../adr/0017-hybrid-retrieval-with-measured-llm-rerank.md) — retrieval híbrido medido; permanece válido, agora como fundação do app (decisão 8).
- [ADR-0011](../../adr/0011-externalize-user-corpus-from-engine-repo.md) — separação engine × corpus; `_chapters/` e o compile multi-fonte vivem do lado do corpus.
- `CLAUDE.md` § "Pontos-chave" item 6 — declara o Obsidian como frontend oficial sem ressalva. **Precisa de ajuste** conforme a decisão 2.
