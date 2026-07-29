---
name: Handoff
description: Última sessão (atualizado ao encerrar)
type: project
---

## Sessão — 2026-07-15/16 (stack 100% local + features 011-013)

**Read before acting:**

- `PENDING_LOG.md` (seção 2026-07-15/16) e `ERROR_LOG.md` (entradas 2026-07-15)
- Plano aprovado: `~/.claude/plans/vamos-tentar-ajustar-primeiro-cheeky-fern.md`
- Roadmap grillado: `features/011-corpus-noise-filter/DOMAIN.md` (12 decisões)

**Current state:**

- Stack local fim-a-fim: **Bonsai 27B 1-bit** GGUF no fork llama.cpp PrismML (pin `62061f91`) via `~/dev/personal/local-ai-lab/start-bonsai-server.sh` em `:8081` (ctx 16384, ubatch 1024, thinking off) + **Nomic v2-moe** no LM Studio `:1234`; Ollama removido; `.env` → `KB_DATA_DIR=~/vault`
- ⚠️ Servidores NÃO sobem no boot: `lms server start` + `start-bonsai-server.sh` após reinício
- Suíte: **452 passed**, 93% cobertura; features **011/012/013 DONE locais, SEM commit** (REPORTs em `features/*/REPORT.md`)
- QA fast: ~1m15s–2m/pergunta (era ~5min); vault com 2.059 artigos indexados, 74 ruídos arquivados
- MLX 1-bit (4.8G) guardado aguardando upstream (issue mlx#3161; watch cloud semanal `trig_01FcZK3rUtxfdUsYvCvZ4HiK`)

**Anotação do dono no encerramento:**

> Seguiremos os testes do KB; **eventualmente testar o Bonsai 8B 1-bit** para execução dessas tarefas — gate: golden set (feature 014).

**Open points:**

- P1: commits das 011-013 (aguardam pedido do dono)
- Tensor API Metal desabilitado no ambiente (pp sem aceleração) — frente de investigação → PR ao fork
- `summaries/` duplica artigos no índice; VM G0dwin offline

**Recommended next session:**

> Subir os dois servidores locais, depois iniciar a **feature 014 — `kb bench` + golden set** (~12-15 perguntas do vault, grader de fidelidade): é o gate da decisão do Bonsai 8B e do bench da VM. Alternativa se o dono pedir: commits das 011-013 primeiro.
