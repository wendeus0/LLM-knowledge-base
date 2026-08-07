---
name: Next Steps
description: Próximos passos priorizados
type: project
---

## Atualizado: 2026-08-06

### O próximo esforço: compile multi-fonte (ADR-0018, decisão 2)

1. **Abrir wayfinder/spec do compile multi-fonte.** O artigo de tema costura várias fontes sob demanda; pré-requisitos prontos (proveniência, library, _chapters). Insumos: `MAPA-DE-TEMAS.md`, os 55 gêmeos temáticos (`kb dedup scan`), os 124 unresolved.
2. **Marcar leitura de artigo na plataforma** (pendência da 026) — progresso real e subtração na trilha; agora com 345 artigos visíveis, a trilha é navegável de ponta a ponta.

### Anterior (2026-08-05)

### Da plataforma de estudos (026), agora que ela está em `main`

1. **Marcar leitura de artigo.** Destrava as duas coisas que ficaram pela metade: o progresso deixa de ser posição e vira leitura, e a trilha ganha a subtração da direção B (concluído sai de cena, o próximo passo fica em destaque). É o menor pedaço com maior efeito na tela.
2. **Dedup dos 59 pares com cosseno ≥ 0,95.** O usuário viu os duplicados em segundos ao abrir o leitor. A causa raiz é o `manifest.json` nunca materializado — o compile não sabe que já viu a fonte. Sobe de prioridade porque agora a duplicata é visível, não medida.
3. **Compilar direto pelo gancho de fontes.** Hoje ele lista o que existe em `raw/`, `library/` e `wiki/_sources`; falta o botão que dispara `compile_file`.

### Anterior (2026-07-31)

### P0 — a mais urgente do sprint

0. **Proteger o que não é reconstruível** (ticket 001 do map, frontier). O golden de 152 casos (`~/vault/kb_state/bench/golden.json`) e as **869 fontes de `library/` (185 MB, fora do git)** sustentam toda decisão sobre o corpus. O ticket 006 discute recompilar; sem o material bruto, essa opção deixa de existir. Barato e destrava o resto do map.

### P1 — decisão central do map, agora destravada

1. **Ticket 004 — a wiki é produto ou insumo?** Destravou com 002 e 003 entregues. Decide se o compile precisa de gate de profundidade, se a definição de artigo robusto de `011/DOMAIN.md` volta, e se a interface do 007 é leitor ou front do `qa`. As outras decisões derivam desta.

### P1 — baratos e destravam o resto

1. ~~Decidir onde o golden set mora~~ — absorvido pelo item 0 acima, que amplia o escopo para `library/`.

~~2. Documentar a config vencedora no `.env.example`~~ — feito em 2026-07-30.
~~3. Push da branch~~ — mergeada em `main` (`f694190`) e publicada.

### P2 — próximo ganho de retrieval

4. ~~**Restringir a saída do rerank:** pedir os N mais relevantes em vez de ordenar 20~~ — **NEGATIVO MEDIDO (2026-07-31)**. Implementado e medido em `feat/rerank-top-n` (não mergeado). Zerou os índices fora da faixa, que era o alvo, mas **recall@5 caiu de 0,526 para 0,493** (−5 acertos em 152) porque o modelo devolve menos do que se pede: cobertura 0,91, seis omissões severas. MRR subiu (0,352 → 0,364) — acerta em posição melhor, erra mais vezes. Medição limpa (`failed: 0`, `degraded: false`). Reabrir só se o critério do projeto virar MRR, ou com reranker que não omita.
5. **Índice lexical persistente.** `_iter_docs` relê os 1.033 arquivos por query (~3s); é o gargalo de qualquer medição agora que o rerank tem cache.
6. **Verificação contínua do provider durante o lote.** O `preflight` cobre só o início; duas medições foram perdidas por falha no meio.

### P3 — condicionados

7. **Expandir o golden além de 152 casos** se algum experimento futuro tiver delta esperado abaixo de ~4pp.
8. **`ik_llama.cpp` com `--fit` e KV cache q4_0** para viabilizar um 35B na VM — reabriria o teste de compressão. Ressalva: memory pinning da referência é CUDA, a VM é AMD/ROCm.
9. **Revisar `expected` do golden** onde há artigos irmãos igualmente válidos; parte das falhas restantes é erro de medida.
10. **Quantizar ou reverter o chunking** se os 148 MB de índice incomodarem — a 017 não comprovou ganho de recall.

## 2026-08-01

### P1 — decisão do usuário antes de tudo

0. **Mergear ou revisar #59 e #60.** O #59 trava as decisões da política de corpus (o ADR-0018 não existe em `main`, e a SPEC da 023 precisou recuperá-lo do histórico git). O #60 carrega protótipo + especificação da 023.

### P1 — se a 023 seguir

1. **`test-design`** — não `test-red`. Duas condições binárias de risco no PLAN. Testes de contrato HTTP (`GET /v1/models`, `POST /v1/nli`) e de estabilidade do JSON são obrigatórios antes do GREEN.
2. **Provisionar o serviço NLI local em `:1235`.** Porta verificada livre. `torch`/`transformers` ficam fora do `pyproject` por decisão de arquitetura — o serviço é separado, como já é o de embeddings.
3. **Coletar os 12 pares mínimos do holdout** e congelá-los antes de qualquer recalibração. Sem isso não há aceite de desempenho, só testes de contrato.

### P2 — herdado

4. Estágio 1 (cobertura) espera o reagrupamento por tema do ticket 006.
5. Achados F-03/F-06/F-08 da auditoria de segurança seguem abertos no `PENDING_LOG.md`.

## 2026-08-02 em diante

1. **Ticket 006 — reagrupamento por tema** (interativo). Maior decisão de produto pendente; destrava o estágio 1 da pilha de verificação.
2. **Rodada do holdout** — configuração congelada, uma execução, publicar taxas e hashes. Reportar a taxa cross-língue à parte (artigos PT, fontes EN).
3. **F-06 e F-08** (P2) — pisos de dependência com CVE e symlink na wiki lido para o provider.
4. **Espalhar o gate de appeasement** para outros repos Python (1 arquivo + 1 linha de CI).
5. **Threading de `--allow-sensitive`** até embeddings/rerank (hoje opt-in por `KB_EGRESS_ALLOW_SENSITIVE`).

## 2026-08-03 em diante

1. **Escolher a direção visual** — bloqueia qualquer trabalho de aparência.
2. **Decidir o PR #66.**
3. **Ingestão da ementa** — separar o `aberto` e baixável, rodar `import-book`.
4. **Dedup dos 59 pares** — a plataforma tornou visível o que exigia medição por cosseno.
5. **Rerank** — é o único gargalo que sobrou; todo comando ainda pede `--no-rerank`.
6. **Progresso de leitura** — a barra da sidebar mostra 0% porque nada a alimenta.
