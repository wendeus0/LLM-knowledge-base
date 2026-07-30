# REPORT — 015-index-auto-refresh

**Data:** 2026-07-29
**Status:** `DONE` (código local; commit pendente de push)
**Ciclo:** SPEC → PLAN/TASKS → RED (8 testes) → GREEN → suíte → validação E2E em vault isolado

## O que mudou

- **`kb/embeddings.py`:** `refresh_embeddings_index(enabled)` — decide por flag e por `KB_INDEX_AUTO_REFRESH`, faz probe do servidor antes de tentar, delega a `build_index` (incremental por hash, da 012) e **captura qualquer falha**. Devolve o relatório ou `None`, sempre com aviso em stderr quando pula.
- **`kb/compile.py`:** refresh ao fim de `compile_many`, uma vez por lote — não por artigo.
- **`kb/heal.py`:** refresh ao fim de `heal()`, cobrindo reescrita e remoção.
- **`kb/qa.py`:** refresh no caminho `--to-wiki`.
- **`kb/cli.py`, `kb/cmds/{compile,qa}/run.py`:** flag `--no-index-refresh` em `compile` e `heal`, propagada pelas camadas intermediárias.

**Fora do escopo declarado, corrigido no mesmo ciclo** (débito descoberto pela validação E2E):

- `_iter_articles` e `_iter_docs` ignoravam `_*` mas **não** diretórios ocultos. `.heal_backup/` — criado pelo próprio `heal` — entrava no índice semântico e na busca lexical, assim como qualquer `.md` sob `wiki/.obsidian/`. `kb/stats.py` já excluía `.heal_backup` explicitamente; os dois coletores não. Agora ambos ignoram `_*` e `.*`.

## Validação

- 8 testes novos (5 unit em `test_index_refresh.py`, 3 integration em `test_index_refresh_cli.py`), mais 1 unit para os diretórios ocultos. Todos nascidos RED por `AssertionError`.
- Suíte completa: **486 passed**, cobertura **93%**, ruff limpo. Quatro testes existentes atualizados para o novo contrato de kwargs (mudança intencional).
- **E2E em vault isolado** (`scratchpad/vault-e2e-01`, servidor de embeddings real, zero chamadas ao LLM de chat — usei um stub, que o `heal` remove sem consultar o modelo):

| Passo | Resultado |
|---|---|
| `kb index build` inicial | 2 artigos indexados |
| `kb heal -n 10` | stub removido do disco |
| Índice **sem** rodar `index build` | stub **fora do índice** — refresh automático funcionou |

- **Incrementalidade medida no vault real (1.037 artigos):** build consecutivo faz `0 indexados, 1037 inalterados` em **0,65s**, sem nenhuma chamada de embedding. O refresh automático custa uma varredura de hashes, não um re-embed.

## Riscos / dívida

- O refresh varre o corpus inteiro para comparar hashes (~0,65s em 1.037 artigos). Cresce linearmente; num corpus 10× maior seria perceptível ao fim de cada compile.
- `--no-index-refresh` foi entregue em `compile` e `heal`. Em `qa --to-wiki` o controle é só por `KB_INDEX_AUTO_REFRESH` — a flag exigiria propagar por mais uma camada e o caso de uso (arquivar uma resposta) não justifica.
- **Observação não explicada:** o índice do vault continha uma entrada `.heal_backup/ai.ml.20260729-000926` de um `heal` executado fora desta sessão. Não há crontab nem launchd configurado para o `kb`. Provavelmente outra sessão ou execução manual — registrado porque implicou um re-embed completo dos 1.037 artigos durante a validação.
- Edição direta no Obsidian continua invisível até `kb index build` — watcher ficou fora de escopo por decisão da SPEC.

## Próximos passos

1. Feature 016 — `kb bench` + golden set. Sem ele, comparar `v1.5` × `v2-moe` ou avaliar chunking é opinião.
2. Feature 017 — chunking por seção: **388 dos 1.037 artigos (37%) são truncados a 8k chars** no embedding. A medição de hoje confirmou o número que o REPORT de 012 estimou.
3. Considerar um job `index-refresh` em `kb/jobs.py` para cobrir edições feitas fora da CLI.
