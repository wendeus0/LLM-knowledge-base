---
name: Handoff
description: Estado para a próxima sessão
type: project
---

## Handoff — 2026-07-30 (encerramento)

### Onde paramos

`main` @ `94459e3`, tudo pushado, working tree limpo, `602 passed` / 92% / ruff limpo. CI verde.

A branch `feat/semantic-retrieval-foundation` (16 commits) foi mergeada em `f694190` com `--no-ff`. Nada pendente de publicação.

### O resultado que importa

Retrieval saiu de `recall@5 = 0,230` (lexical) para **0,467**, e MRR de `0,127` para **0,343**. Cada ganho medido contra um golden de 152 casos, não estimado.

O que funcionou: **canal semântico** (+18pp) e **rerank do top-20 a temperatura 0** (+42% de MRR). O que **não** funcionou, registrado como negativo no ADR-0017 para não ser retentado: chunking por seção, expansão por termos, e trocar o modelo de rerank por um 13× mais rápido (pior que não reordenar).

### O que esta sessão mudou além dos números

1. **O ganho medido não chegava a ninguém.** `rerank_depth` só era passado pelo `bench`; nem `kb search` nem `kb qa` o expunham. Agora `--rerank N` no search (opt-in, 2,7s → 36,7s) e ligado por padrão no `qa` (2m15 → 2m26, `--no-rerank` para sair).
2. **`--commit` nunca versionou nada.** `kb/git.py` resolvia contra o repo do código; com `KB_DATA_DIR` fora dele, o path era descartado e a função retornava `True`. Corrigido, e `~/vault` virou repo git.
3. **Os servidores locais sobem no login.** LaunchAgents `com.wendeus.kb-embed` (:1234, `StartInterval` 60s com watchdog idempotente) e `com.wendeus.kb-rerank` (:8081, `KeepAlive`). Mecanismos diferentes porque `lms server start` retorna e `llama-server` fica em foreground.
4. **ADR-0017** registra a decisão de retrieval e supera o ADR-0004, cujos próprios gatilhos de revisão haviam disparado.
5. **Artefatos sincronizados.** `features/` mostra uma frente aberta em vez de quinze; `SDD.md`, `CONTEXT.md` e `.pi/manifest.yaml` deixaram de descrever um produto que não existe mais.

### Próximo passo recomendado

**Restringir a saída do rerank** — pedir os N mais relevantes em vez de ordenar 20. A 022 provou que sampling corrige omissão mas **não** alucinação de índice (o granite4 produziu 32 posições fora de faixa mesmo greedy). Encolher o espaço de saída é o que resta. Gate: `kb bench --rerank 20` contra `recall@5 = 0,467 / MRR = 0,343`.

Antes disso, um P1 que continua aberto: **onde o golden set mora**. Hoje em `~/vault/kb_state/bench/golden.json`, num vault que agora é git mas onde `kb_state/` está parcialmente gitignored. Diferente do índice, ele **não é reconstruível** — os 50 casos curados são trabalho manual.

### Ambiente

- **Embeddings:** LM Studio :1234, `nomic-embed-text-v2-moe`. Sobe por LaunchAgent.
- **Rerank:** `bonsai-27b-1bit` :8081 via `start-bonsai-server.sh`. Sobe por LaunchAgent. Logs em `~/Library/Logs/kb-*.log`.
- **VM `g0dw1n`:** acessível pela tailnet sem túnel (`100.119.208.90:11434`). Não é dedicada (hospeda CI runners) e modelos >8 GB não cabem em 15 GB.
- **Vault:** `~/vault` é repo git desde hoje (`0160552`, 4.281 arquivos, 50 MB). `.gitignore` exclui `library/` (185 MB), `embeddings.json` (148 MB) e `tracking.db`.

### Prompt de retomada

> Retomando o kb. `main` @ `94459e3`, tudo pushado, 602 testes verdes. Leia `memory/project_state.md` para os números de retrieval, `docs/adr/0017-hybrid-retrieval-with-measured-llm-rerank.md` para a decisão e seus gatilhos de revisão, e `PENDING_LOG.md` para o que ficou aberto. O próximo passo planejado é restringir a saída do rerank (pedir top-5 em vez de ordenar 20), com gate no `kb bench --rerank 20` contra `recall@5 = 0,467 / MRR = 0,343`. O P1 que continua aberto é decidir onde versionar o golden set de 152 casos — ele não é reconstruível. Regra que esta sessão custou caro para aprender: ganho medido pelo instrumento pode não existir no produto; verifique pelo comando que o usuário digita.
