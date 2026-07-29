# REPORT — 016-bench-golden-set

**Data:** 2026-07-29
**Status:** `DONE_WITH_CONCERNS` (código local; commit pendente de push; concerns abaixo)
**Ciclo:** SPEC → PLAN/TASKS → RED (16 testes) → GREEN → suíte → medição no vault real → dois bugs encontrados e corrigidos

## O que mudou

- **`kb/bench.py` (novo):** métricas puras (`evaluate_case`, `aggregate`) separadas do I/O (`load_golden`, `seed_golden`, `write_golden`, `run_bench`). recall@k e MRR calculados sobre casos válidos; caso cujo artigo esperado sumiu do corpus é categoria própria, não falha de recuperação.
- **`kb/cli.py`:** comando `kb bench [--mode] [--k] [--seed [--limit]] [--json]`.
- **Golden set** em `kb_state/bench/golden.json`, com `expected` por slug (sobrevive a mudança de topic).

**Dois defeitos encontrados durante a medição e corrigidos no mesmo ciclo:**

1. **`search()` aceitava modo desconhecido em silêncio.** Só `"keyword"` era tratado; qualquer outro valor caía no caminho híbrido. Meu primeiro `--mode lexical` mediu híbrido e produziu números idênticos aos do `--mode hybrid` — dois experimentos iguais apresentados como comparação. Agora existe `SEARCH_MODES` explícito, `lexical` é um modo real (RRF dos três canais lexicais, sem consultar o semântico) e modo desconhecido levanta `ValueError`.

2. **A suíte de testes destruía o índice do vault real.** Regressão introduzida pela feature 015: ao acrescentar refresh de índice ao fim do `heal()`, o teste pré-existente `test_heal_workflow.py::test_should_update_reviewed_at_timestamp` — que usa a fixture `tmp_wiki` — passou a disparar `build_index`. A fixture isolava `WIKI_DIR` mas **não** `STATE_DIR`: o build lia um wiki temporário de 1 artigo e escrevia no `kb_state` do usuário. Resultado: 1.037 vetores (17,8 MB) viraram 1 (17 KB), e o canal semântico ficou morto sem nenhum sinal. `tmp_wiki` agora isola todo o estado (`STATE_DIR`, manifesto, knowledge, learnings, claims, audit, `tracking.DB_PATH`) e `tmp_raw_wiki` ganhou `router.WIKI_DIR` e `tracking.DB_PATH`.

## Validação

- 16 testes novos (12 unit em `test_bench.py`, 4 integration em `test_bench_cli.py`), mais 3 unit para modos de busca e 6 de guarda de isolamento de fixture. Todos nascidos RED por `AssertionError`.
- Suíte: **511 passed**, cobertura 92%, ruff limpo.
- **Isolamento verificado pelo método que detectou o bug:** sentinela gravado no índice do vault → suíte completa → sentinela **intacto**.

### Primeira medição de retrieval do projeto

Golden set semeado com 50 casos (título → artigo), corpus de 1.033 artigos:

| Modo | recall@5 | MRR | acertos |
|---|---|---|---|
| lexical (keyword + densidade + BM25) | 0,680 | 0,449 | 34/50 |
| **hybrid (lexical + semântico)** | **0,860** | **0,594** | **43/50** |

**O canal semântico vale +18 pontos de recall (+26% relativo) e +14,5 de MRR.** É a primeira evidência medida de que a feature 012 entregou valor — até aqui era argumento.

Tempo: ~13s para 50 casos em qualquer modo (dominado pelas 50 varreduras completas do corpus na busca lexical).

## Riscos / dívida

- **O golden set semeado por título é um piso, não uma avaliação.** Ele mede "o sistema acha o artigo pelo próprio título" — útil como sanity check e para comparar configurações entre si, fraco como proxy de perguntas reais. Os 50 casos precisam de curadoria humana para virar avaliação de verdade.
- Os casos que mais falham são capítulos de livro com títulos genéricos (`Ordenação e Estatísticas de Ordem`, `Algoritmos de Grafos`) — provavelmente concorrem com dezenas de artigos do mesmo livro. Vale investigar antes de concluir qualquer coisa sobre o ranking.
- O relatório agora registra se o canal semântico respondeu (`canal semântico ativo/INATIVO`), fechando o requisito técnico que faltava — um `hybrid` medido com servidor fora é um `lexical` disfarçado, e foi um dos modos de falha desta sessão.
- Bench com 1.037 casos custaria ~4,5 min por modo. `--limit` no seed é a válvula.

## Próximos passos

1. Curar o golden set com perguntas reais, substituindo os títulos semeados.
2. Feature 017 — chunking por seção: **388 dos 1.037 artigos (37%) truncados a 8k**. Agora existe baseline (`hybrid 0,860 / 0,594`) contra o qual medir.
3. Comparar `v1.5` × `v2-moe` com o mesmo golden set — os dois estão em disco e agora há instrumento.
