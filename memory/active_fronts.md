---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frente ABERTA em 2026-08-06 — compile multi-fonte (ADR-0018, decisão 2)

**Status:** `WAYFINDER_CHARTED` — map traçado, 8 tickets criados, nenhum resolvido.
**Artefatos:** `docs/research/2026-08-06-compile-multi-fonte/{MAP.md, 001..008-*.md}`
**Destination:** o map fecha em **artigo**, não em SPEC nem ADR — um primeiro artigo de tema real no vault, costurado de várias fontes, conferido em tela renderizada.
**Regra de casa:** o compile de tema entra como feature com pipeline completo desde o início (SPEC → PLAN → CONTRACT → RED → GREEN). Protótipo throwaway não é o caminho oficial. Toda afirmação estrutural carrega evidência `caminho:linha`.

**Resolvido em 2026-08-06:** [qualidade-da-proveniencia](../docs/research/2026-08-06-compile-multi-fonte/008-qualidade-da-proveniencia.md) — a proveniência por basename **sustenta** o agrupamento por tema (0 falso positivo em 40 pares, teto de 7,5%; 94,8% dos basenames únicos; a cadeia omite em vez de errar). Destravou `medir-sobreposicao-tematica`. O gargalo real é cobertura: 120 de 345 vivos ficam fora, e o viés é concentrado em `learning` e num livro de `ai`.

**Frontier (abertos, desbloqueados):** [medir-sobreposicao-tematica](../docs/research/2026-08-06-compile-multi-fonte/001-medir-sobreposicao-tematica.md), [o-que-e-um-tema](../docs/research/2026-08-06-compile-multi-fonte/002-o-que-e-um-tema.md), [de-onde-a-sintese-le](../docs/research/2026-08-06-compile-multi-fonte/003-de-onde-a-sintese-le.md).

**Evidência medida no charting que muda o desenho:**
- O manifest tem **zero** artigos com mais de uma fonte — 856 entradas, 856 artigos distintos. O 1:1 está escrito nas primitivas (`kb/state.py:88-108`, `kb/state.py:232-258`).
- **824 de 856 (96%)** da proveniência veio de `backfill-basename` — match de nome de arquivo. É o critério que o ADR elegeu como *o* agrupador.
- `wiki/_chapters/` é **inalcançável** por todo retrieval (`kb/fsutil.py:21-22`, `kb/search.py:25-26`, `kb/embeddings.py:62-63`, `kb/lexical_index.py:44`, `kb/graph.py:28`). Única exceção: `kb/api/articles.py:39-49`.
- `library/` tem **23 fontes ainda em PDF/EPUB não extraídos**; a categoria `llm/` tem 10 binários e zero markdown; só 34 dos 43 livros de `software-engineering/` têm `metadata.json`.
- Dos 345 vivos, **120 sem proveniência** (os `unresolved`; o REPORT da 029 dizia 124). Sete deles estão soltos na raiz da wiki e são capítulos de livro que escaparam do reagrupamento.
- Wiki viva concentrada: 214 `algorithms` + 89 `learning` = 303 de 345. Arquitetura, Python e testes foram todos para `_chapters/`.

## Frente fechada em 2026-08-06 — higiene do corpus / ADR-0018 etapas 1–3 (027/028/029)

**Status:** COMPLETO. PRs #69, #70 e #71 mergeados; `main` @ `52d1006`. O gate final (mover 851 → decisão do dono: 630 em 37 livros; transcripts e harness ficam) executado com 37 commits e zero erros.

O que destrava: **compile multi-fonte** — proveniência materializada, `library/` íntegra, `_chapters/` populado, `_*` blindado. Abrir com wayfinder próprio.

## Frente fechada em 2026-08-05 — plataforma de estudos (026)

**Status:** entregue e mergeada. PR #66 (F1–F5) e PR #67 (correção do review + Direção B), `main` @ `858c888`.

O que a rodada de correção mudou de substantivo, além de fechar os apontamentos: dois bugs de concorrência com teste que os reproduz (revisão simultânea perdia o `fsrs_state`; migração simultânea estourava `duplicate column name`), a âncora de destaque passou a casar contra o texto renderizado em vez do Markdown cru, o índice de wikilinks ganhou invalidação por assinatura do corpus, e as transições de cartão viraram condicionais no `WHERE`.

**Aberto na frente:** a subtração visual na trilha depende de marcação de "li este artigo", que não existe — é o próximo passo 1 do `REPORT.md`. O resto está em `PENDING_LOG.md` (sessão 2026-08-05).

## Frente ativa

### Política de corpus — map FECHADO (2026-07-30 → 2026-07-31)

**Status:** `WAYFINDER_CLEAR` — 8 de 8 tickets resolvidos. Destination entregue: [ADR-0018](../docs/adr/0018-corpus-policy-theme-articles-over-chapter-articles.md).
**Artefatos:** `docs/research/2026-07-30-politica-de-corpus/{MAP.md, DOMAIN.md, MAPA-DE-TEMAS.md, MEDICAO-CORPUS.md, tickets/}`
**Regra de casa do diretório:** toda afirmação estrutural carrega evidência `caminho:linha`; afirmação sem evidência é marcada `UNVERIFIED` e não entra no ADR.

**O que a política travou:** a wiki é produto; o artigo passa a ser de tema e multi-fonte, gerado sob demanda; os 1.037 artigos de capítulo são reagrupados em lote **pela proveniência** e vão para `_chapters/`; a fonte é livro e paper curados pelo usuário, sem web aberta na rotina; **não há detecção automática de lacuna**; a tela própria absorve autoria e leitura, e o Obsidian sai.

**Três decisões foram derrubadas ou reformuladas por medição, não por argumento:**
- "o corpus é raso" — falso: mediana de 10 headings, 93% com ≥5. O detector original media aderência ao template.
- "limiar de score detecta lacuna" — falso: acertos (0,0367–0,0641) e erros (0,0361–0,0636) se sobrepõem quase por inteiro. RRF mede concordância entre canais, não confiança.
- "agrupar por cosseno" — substituído por proveniência: o clustering revelou que o corpus são ~40 livros fatiados, e `raw/books/*/metadata.json` já sabe qual capítulo veio de qual livro.

**Cinco pré-requisitos técnicos bloqueiam a execução** (nenhum existe): rastreabilidade de origem por trecho, `manifest.json` materializado, retrieval sobre `library/`, medição de sobreposição temática, e medida de confiança da resposta. Execução sai pelo `spec-pipeline`.

**Achados do charting que reorientam o projeto:**
- `raw/` está vazia (dois `.DS_Store`); `kb compile` tem zero alvos. As 869 fontes só existem em `library/`, 185 MB **fora do git**.
- `manifest.json` nunca foi materializado — um recompile **duplicaria** a wiki em vez de atualizá-la (`kb/state.py:87` × `kb/compile.py:223-231`).
- O compile produz artigo raso por design e ninguém mediu: prompt sem instrução de profundidade, `_validate_output` aceita três frases, `max_tokens` nunca enviado.
- Qualidade de resposta do `qa` tem zero medição — o `bench` mede ordenação. O grader de fidelidade segue pendente desde `PENDING_LOG.md:119`.
- O perfil `article` (`top_k=5`, 8k, traverse — `kb/config.py:88`) existe **sem consumidor**; o `qa` roda `fast` com cap de 4k que corta a cauda de 40% dos artigos.
- Zero material de recon/OSINT no vault — a pergunta que abriu o esforço não tinha fonte para responder.

**Decisões travadas no grilling:** o produto é o output do `kb qa`, não a densidade do arquivo na wiki; em lacuna de corpus, o kb deve buscar fonte em vez de se abster ou completar com conhecimento paramétrico; a interface própria entra no escopo (era out of scope no map anterior).

### Retrieval medido — features 014 a 022 (2026-07-30)

**Status:** mergeado em `main` (`f694190`), 16 commits. Servidores locais sobem por LaunchAgent.
**Resumo:** `recall@5` de 0,230 (lexical) para **0,467**; MRR de 0,127 para **0,343**. Cada ganho medido contra golden de 152 casos.

| Feature | Resultado |
|---|---|
| 014 embed-server-autostart | servidor sobe sozinho; degradação deixa de ser silenciosa |
| 015 index-auto-refresh | índice acompanha compile/heal/qa; incremental (0,65s sem re-embed) |
| 016 bench-golden-set | `kb bench` com recall@k e MRR — o instrumento que viabilizou o resto |
| 017 chunking-por-secao | **negativo:** +1 caso em 50, MRR pior. Mantida por eliminar truncamento de 35% do corpus |
| 018 expansao-de-query | HyDE +4pp; `terms` zero. Opt-in (~10s/query) |
| 019 golden-expandido | 50 → 152 casos; erro padrão de ~7pp para ~4pp |
| 020 rerank-llm | **+5,3pp recall, +24% MRR** — maior ganho da sequência |
| 021 rerank-provider-dedicado | **negativo:** `granite4` pior que não reordenar (0,388 < 0,414) |
| 022 perfis-de-sampling | temp 0 no rerank: **MRR +42%** sobre não reordenar |

**Decisão fechada:** rerank com `bonsai-27b-1bit` local e perfil `deterministic`. O modelo da VM é 13× mais rápido e pior.

**Próximo:** restringir a saída do rerank (top-5 em vez de ordenar 20) — sampling corrige omissão, não alucinação de índice.

**Alcance corrigido em 2026-07-30:** o rerank existia só para o `bench`. Agora `kb search --rerank N` (opt-in) e `kb qa` (ligado por padrão em todos os perfis, `--no-rerank` / `KB_RERANK_DEPTH` para sair). Sete features registraram ganho num caminho que nenhum comando expunha.

### Engenharia reversa + roadmap revisado (2026-07-28)

**Status:** map `WAYFINDER_CLEAR` — 5/5 tickets resolvidos, sem névoa restante. Plano em `~/.claude/plans/apenas-isso-pode-ser-frolicking-falcon.md`
**Artefatos:** `docs/research/2026-07-28-engenharia-reversa/{MAP.md, SINTESE.md, BACKLOG.md, DOSSIE-*.md, tickets/}` — 11 itens de backlog ordenados por valor
**Resumo:** wayfinder para levantar dossiê de engenharia reversa + portes candidatos. Executado via `fable-gpt` (GPT 5.6 Terra) com review zero-trust. Sem compromisso de implementar.

**O que cada repo resolveu:**
- **Hikari-knowledge** — markdown autoritativo + grafo derivado + vetor opcional por RRF (`300/(10+rank)`, calibrado para nunca deslocar hit lexical exato) + curadoria por gates.
- **graphify** — retrieval léxico-IDF + travessia de grafo, **sem vetor em ponto algum**; sem match, responde `No matching nodes found.` e para. Prosa é cidadã de segunda classe.
- **rowboat** — memória pessoal em Markdown carregado no prompt; Qdrant só para RAG de documentos, filtrado por projeto. A UI expõe estado operacional, não conteúdo.

**Convergência:** arquivo é a verdade nos três; vetor só em papel auxiliar e delimitado. Valida a aposta do kb — e expõe que os três mantêm uma camada derivada (grafo, grafo, curadoria) que o kb não tem.

**Out of scope registrado:** decidir se o kb terá UI própria — vira esforço separado.

**Descoberta que redefiniu o roadmap:** as features **011, 012 e 013 já estão implementadas** em `~/dev/personal/LLM-knowledge-base`, sem commit desde 2026-07-15. `kb/embeddings.py` com canal semântico no RRF, `kb index build|status`, perfis de contexto. Servidor: LM Studio em `localhost:1234` com `nomic-embed-text-v2-moe` (não Ollama, apesar do que SPEC e REPORT dizem).

**Corpus medido (2026-07-28):** 2.781 `.md` em `~/vault/wiki` (1.759 fora de `summaries/`, 1.022 em `summaries/`), 4.26M palavras; `~/vault/library` com 869 fontes / 4.79M palavras. `kb index status` reporta `2059/2059` — denominador é o próprio índice, não o corpus.

**Achados sobre o kb — ainda abertos:**
- `kb/lint.py:37` — `articles[:20]`: auditoria semântica vê 20 de 2.781 sem avisar.
- `kb/compile.py:204-210` — `discover_compile_targets` não consulta o manifesto; `kb/jobs.py:35` chama sem argumento, então o job agendado reprocessaria o corpus inteiro.
- `kb/search.py:_iter_docs` — relê e tokeniza a wiki a cada busca (3 varreduras/query); `kb/graph.py:17-23` faz `rglob` completo por wikilink dentro do BFS.
- Slug `[:60]` sem colisão em `compile.py:216`, `outputs.py:40`, `qa.py:150`.
- `kb/heal.py:98` faz `unlink` enquanto `archive.py` move com backup.

**Corrigidos em 2026-07-30:**
- `kb/git.py` — resolvia tudo contra `ROOT`; com `KB_DATA_DIR` fora do repo, `--commit` era descartado em silêncio. Agora resolve o repo que contém cada arquivo e avisa quando não há nenhum. `~/vault` virou repo git (`0160552`).
- `tests/conftest.py` — isola todo o estado, não só `WIKI_DIR`, e desliga refresh de índice e rerank na suíte.

### Plano de robustez do core (2026-07-09)

**Status:** em execução — plano em `docs/superpowers/plans/2026-07-09-core-robustness.md`
**Branches:** uma por fase (chore/truth-sync → ci/test-gate → fix/pipeline-hardening → feat/article-template → refactor/dead-code-cut → test/uncovered-modules → feat/008 → feat/009 → feat/010-spec), empilhadas até merge
**Resumo:** review completo (4 lentes) → hardening do pipeline ingest→compile→qa→heal, template de artigo como artefato core (engine + override por vault), cortes de código morto, CI com pytest+ruff, cobertura de módulos nus, backlog 008/009 e SPEC de 010.

---

## Frentes em backlog (SPEC draft)

### 008-kb-stats — comando `kb stats` (dashboard Rich). Primitivas em `kb/analytics/` e `kb/claims.py`. ~3h.
### 009-kb-diff — comando `kb diff` (git diff da wiki com Rich). Wrap de git, zero deps novas. ~2h.
### 010-multi-vault-foundation — **meta real, SPEC pendente** (decisão do dono 2026-07-09). Task 13 do plano produz o draft; HITL do dono antes de avançar. Pré-requisito citado: `kb/config.py` resolve paths no import.

---

## Frentes concluídas

- **llm-wiki-v2-foundation** — mergeada via PR #35 (`4835419`); artefatos em `features/_archived/`.
- **ingest-url** — mergeada via PR #32 (`6072c1d`).
- **006-kb-archive** — mergeada via PR #31 + arquivamento via PR #33; diretório movido para `features/_archived/` em 2026-07-09.

---

## Decisões abertas

Ver "Open questions" no plano (`docs/superpowers/plans/2026-07-09-core-robustness.md`): bump de versão 0.5.0, conteúdo fino do template de artigo, quarentena vs skip no heal.

## Decisões resolvidas nesta rodada (2026-07-09)

- Multi-vault é meta real sem SPEC (não drift de doc) → Task 13 do plano.
- Cortar todo código morto (runner.py, savings, wrappers cmds/lint|search).
- Backlog 008/009 entra como fase final do plano.
- Template de artigo: default versionado na engine (`kb/templates/`) com override em `<KB_DATA_DIR>/templates/`.

## 2026-07-16

1. **014 — kb bench + golden set** (próxima; gate do Bonsai 8B — anotação do dono)
2. Chunking + re-rank (SPEC própria) · 3. Tensor API → PR fork · 4. Módulos paper/artigo → API/app (roadmap DOMAIN 011)

## 2026-08-01 — verificação de resposta

**023-claim-grounding** — `CONTRACT_VALID` + `EVAL_DESIGN_PARTIAL`. Especificação fechada (SPEC/PLAN/TASKS/CONTRACT/EVALS), nenhum código de feature escrito. Próximo passo é `test-design`, não `test-red`: o PLAN marca duas condições binárias de risco (output estrutural estável pelo `--json`, contrato HTTP entre serviços). SPEC, PLAN, TASKS e EVALS redigidos pelo GPT 5.6 Terra; gates e review zero-trust do orquestrador.

**PRs abertos aguardando decisão do usuário:**
- **#59** — tickets 004/005/006/007 do map da política de corpus + ADR-0018. Trava decisões; a 023 saiu de `main` e não enxerga o ADR.
- **#60** — protótipo medido da pilha de verificação + toda a especificação da 023.

**Política de corpus** — `WAYFINDER_CLEAR`. Os oito tickets foram fechados; o ADR-0018 consolidou.

### O que a pilha de verificação mede, e o que não mede

| Estágio | Pergunta | Veredito |
|---|---|---|
| 1 — cobertura por centroide de tema | o acervo tem material? | **confirmado**, sem SPEC (depende do ticket 006) |
| 2 — ancoragem (cosseno seleciona, NLI julga) | a afirmação decorre do contexto? | **confirmado** → feature 023 |
| 3 — consistência entre gerações | as gerações concordam? | **não confirmado**, sem sinal em amostra de 4 |

Juiz LLM verbalizando confiança foi medido e reprovado (83% de falso alarme) — é o pior método da literatura de incerteza, não um problema do modelo escolhido.

## 2026-08-01 (fim) — frentes fechadas

- **023-claim-grounding** — `DELIVERED`, PRs #61/#62.
- **024-f03-guardrail-egress** — `DONE`, PR #63. Último P1 de segurança.
- **Política de corpus** — `WAYFINDER_CLEAR` desde a manhã; ADR-0018 em `main`.

Nenhuma feature ativa. Próxima frente natural: ticket 006 (decisão de produto, exige grilling).

## 2026-08-02

**026-plataforma-de-estudos** — fase 1 entregue (F1 a F5), PR #66 aberto. O ciclo ler→buscar→perguntar→gerar card→verificar→revisar fecha.

**Pendente de decisão do usuário:** direção visual (A/B/B2/C no `DESIGN.md`), o merge do #66, e o que da ementa vira ingestão.

**Fase 2 declarada:** roadmap/trilha, progresso de leitura (a barra existe sem dado que a alimente), e o botão que dispara `compile` a partir do gancho de fontes.
