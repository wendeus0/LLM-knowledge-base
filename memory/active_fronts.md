---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frente ativa

### Política de corpus — map aberto (2026-07-30)

**Status:** `WAYFINDER_CHARTED` — 8 tickets, 0 resolvidos. Frontier: 001, 002, 003.
**Artefatos:** `docs/research/2026-07-30-politica-de-corpus/{MAP.md, tickets/}`
**Destination:** ADR que trava o fundamento do corpus — origem do conhecimento novo, destino dos 1.037 artigos atuais, wiki como produto ou insumo, e superfície de leitura. Gradua o que o map de engenharia reversa deixou em Out of scope.

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
