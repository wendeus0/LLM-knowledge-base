---
name: Handoff
description: Estado para a próxima sessão
type: project
---

## Handoff — 2026-07-30

### Onde paramos

Branch `feat/semantic-retrieval-foundation`, **10 commits, nenhum push**, working tree limpo, `586 passed` / 92% / ruff limpo.

Sequência entregue nesta sessão: engenharia reversa de três repos externos → roadmap medido → features **014 a 022** (as 011/012/013 estavam prontas e sem commit desde 15/jul e foram resgatadas).

### O resultado que importa

Retrieval saiu de `recall@5 = 0,230` (lexical) para **0,467**, e MRR de `0,127` para **0,343**. Cada ganho foi medido contra um golden de 152 casos, não estimado.

O que funcionou: **canal semântico** (+18pp, o maior salto) e **rerank do top-20 com temperatura 0** (+5,3pp de recall, +42% de MRR sobre não reordenar).

O que **não** funcionou, e está registrado como negativo: chunking por seção (+1 caso em 50, MRR pior), expansão por termos (zero), troca de modelo de rerank para `granite4` (**pior que não reordenar**).

### Próximo passo recomendado

**Restringir a saída do rerank** — pedir os N mais relevantes em vez de ordenar 20. A 022 provou que sampling corrige omissão mas **não** corrige alucinação de índice: o granite4 produziu 32 posições fora de faixa mesmo com decodificação gulosa. Encolher o espaço de saída é o que resta.

Antes disso, dois itens P1 baratos: documentar a config vencedora no `.env.example` e resolver onde o golden set mora (hoje num vault não versionado, e ele **não é reconstruível**).

### Ambiente

- **Rerank:** `bonsai-27b-1bit` em `localhost:8081` (via `start-bonsai-server.sh`). ~20s/query, mas é o único que melhora o resultado.
- **Embeddings:** LM Studio em `localhost:1234`, `nomic-embed-text-v2-moe`. Servidor não sobe no boot; `KB_EMBED_AUTOSTART=1` resolve.
- **VM `g0dw1n`:** acessível pela tailnet sem túnel (firewall corrigido na origem, `100.119.208.90:11434`, 0,3s). Ollama com `granite4:tiny-h`, `deephat-v1:7b`, `lfm2.5`, `nomic-embed-text`. **Não é dedicada** (CI runners) e modelos >8 GB não cabem.

### Prompt de retomada

> Retomando o kb na branch `feat/semantic-retrieval-foundation` (10 commits sem push). Leia `memory/project_state.md` para os números de retrieval medidos e `PENDING_LOG.md` para as pendências. O próximo passo planejado é restringir a saída do rerank (pedir top-5 em vez de ordenar 20), com gate no `kb bench --rerank 20` contra a baseline `recall@5 = 0,467 / MRR = 0,343`. Antes disso há dois P1 rápidos: documentar `bonsai@temp 0` no `.env.example` e decidir onde versionar o golden set de 152 casos.
