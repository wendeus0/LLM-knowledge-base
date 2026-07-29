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

Tempo: ~13s para 50 casos em qualquer modo (dominado pelas 50 varreduras completas do corpus na busca lexical).

### Curadoria do golden set — e o quanto o seed enganava

Os 50 casos foram reescritos à mão: perguntas como um humano escreveria, com vocabulário **deliberadamente diferente** do artigo, e `expected` listando todos os artigos que responderiam legitimamente (há quatro grupos de irmãos no corpus, ex.: três artigos sobre *Building Applications with AI Agents*).

| Golden set | lexical | hybrid | ganho do semântico |
|---|---|---|---|
| Semeado por título | 0,680 | 0,860 | +26% relativo |
| **Curado com perguntas reais** | **0,240** | **0,420** | **+75% relativo** |

Duas conclusões que só a curadoria revelou:

1. **O seed por título superestimava a qualidade em ~2×.** Buscar um artigo pelo próprio título é tarefa fácil e não representa uso real. Qualquer decisão tomada sobre `0,860` teria partido de premissa errada.
2. **O canal semântico é bem mais valioso do que o seed sugeria** — quase dobra o recall quando a pergunta não repete o vocabulário do artigo, que é exatamente o caso de uso que motivou a 012.

### Onde o sistema falha (diagnóstico)

| corte | recall (hybrid) |
|---|---|
| @5 | 0,420 |
| @10 | 0,520 |
| @20 | **0,720** |

**O gargalo é ordenação, não recuperação:** 30 pontos de recall vivem entre a 6ª e a 20ª posição. Das 29 falhas em @5, 24 são artigos que sequer entram no top-10.

Dos 10 casos falhos investigados, 7 são artigos acima de 8k chars — truncados no embedding. Mas `a-janela-de-mudanca` (3,4k) e `a-condicao-responde-ao-tratamento` (4,5k) falham sem truncamento, o que aponta para um segundo fator: um artigo longo inteiro reduzido a um único vetor perde especificidade.

### Comparação de modelos de embedding

Mesmo golden curado, mesmo corpus, reindexação completa para cada um:

| modelo | recall@5 | recall@10 | recall@20 | MRR@5 | build |
|---|---|---|---|---|---|
| **nomic-embed-text-v2-moe** | **0,420** | **0,520** | **0,720** | **0,272** | ~70s |
| nomic-embed-text-v1.5 | 0,280 | 0,440 | 0,560 | 0,156 | ~4m30 |

**v2-moe vence em toda a curva** (+50% relativo em recall@5). Consistente com o corpus ser majoritariamente em português — o v1.5 é treinado predominantemente em inglês. Decisão: manter o v2-moe, que já era o default. O índice foi restaurado do backup após o experimento.

## Riscos / dívida

- **50 casos são poucos para decisões finas.** Uma diferença de 1 acerto move o recall em 2 pontos; comparações apertadas entre configurações vão precisar de mais casos para não confundir ruído com sinal. A comparação v2-moe × v1.5 foi larga o bastante (14pp) para não sofrer disso.
- **O golden curado tem viés do curador.** Eu escrevi as 50 perguntas a partir dos artigos, então elas herdam minha leitura do que cada um responde. Perguntas escritas por quem consulta o vault no dia a dia seriam material melhor — e provavelmente mais difíceis.
- **O golden vive no vault, que não é versionado.** Diferente do índice, ele não é reconstruível: é trabalho manual. Cópia de segurança em `scratchpad/golden-curado.json`, mas o lugar certo seria um repositório.
- Os capítulos de livro do CLRS concentram as falhas: nove artigos irmãos, títulos genéricos, conteúdo longo e sobreposto. São o pior caso do corpus para retrieval e valem análise própria.
- O relatório agora registra se o canal semântico respondeu (`canal semântico ativo/INATIVO`), fechando o requisito técnico que faltava — um `hybrid` medido com servidor fora é um `lexical` disfarçado, e foi um dos modos de falha desta sessão.
- Bench com 1.037 casos custaria ~4,5 min por modo. `--limit` no seed é a válvula.

## Próximos passos

1. Feature 017 — chunking por seção: ataca as duas causas identificadas (37% truncados + diluição do artigo longo num vetor). Baseline a bater: hybrid 0,420 / MRR 0,272 com golden curado.
2. Considerar rerank do top-20 — o recall@20 de 0,720 indica que há 30 pontos esperando reordenação.
3. Expandir o golden set além de 50 casos, cobrindo os tópicos que hoje não têm representação.
