# Handoff — 2026-08-05

Sessão fechou a feature 026 em `main`. Nada pendente de commit.

## O que foi entregue

PR #67 mergeado (`858c888`), em cima do PR #66 que outra sessão mergeou às 10:51 do mesmo dia. Seis commits: correção dos ~85 apontamentos dos bots de review do PR #66, reconciliação dos documentos da feature, auditoria da ementa bibliográfica, a Direção de design B, e duas rodadas de resposta ao review do próprio PR #67 (CodeAnt, CodeRabbit e cubic).

**Gate:** `968 passed`, cobertura 93%, `ruff check kb study tests` limpo, gate de test-appeasement exit 0 — verificado com `KB_DATA_DIR` apontando para o vault real e para um caminho inexistente. CI verde nos três Pythons e na `main` depois do merge.

## Decisões desta rodada que não estão óbvias no código

- **Dois tokens de acento.** `#b4551f` (a cor que o usuário escolheu por imagem) é preenchimento; texto usa `--accent-ink`. Como texto, `#b4551f` dá 4,02:1 sobre o bege e 3,63:1 sobre o escuro — abaixo do AA, e a tela vai para escola. Registrado em `docs/research/2026-08-01-kb-para-estudo/DESIGN.md`.
- **`study.db` fica em `DATA_DIR`, não em `kb_state/`.** Há teste explícito fixando isso (`test_study_annotations.py`); o `.gitignore` ganhou `/study.db*`.
- **Guard de rating removido de `study/web.py`** — sobreviveu à mutação porque `study/review.py:14` já validava.
- **Fase 4 (lote mecânico) foi delegada ao Codex** via MCP com `model: gpt-5.6-luna`; `gpt-5.6-sol` e `gpt-5.2-codex` são recusados pelo conector com conta ChatGPT. Revisei e ajustei dois pontos do que ele entregou.

## Duas coisas para decidir na próxima sessão

1. **Branches remotas mergeadas** — `feat/026-plataforma-estudos` e `fix/pr-66-review-followup`. Não apagadas por exigirem confirmação.
2. **Marcar leitura de artigo** é o próximo passo com maior efeito na tela: destrava o progresso real e a subtração na trilha. Ver `memory/next_steps.md`.

## Prompt de retomada

```
Leia memory/project_state.md e memory/next_steps.md. A feature 026 está em main
(858c888). Quero atacar a marcação de leitura de artigo — ela destrava o
progresso real e a subtração na trilha, pendências P2 do PENDING_LOG.
```
