# PLAN — 016-bench-golden-set

## Arquitetura

Módulo novo `kb/bench.py`, com o cálculo separado da execução — a parte que precisa de teste rigoroso é a métrica, e ela não deve depender de I/O:

| Função | Responsabilidade | Pureza |
|---|---|---|
| `evaluate_case(ranked_slugs, expected, k)` | recall e posição do primeiro acerto de **um** caso | pura |
| `aggregate(results, k)` | recall@k e MRR do conjunto | pura |
| `load_golden(path)` | lê e valida o arquivo | I/O |
| `seed_golden(wiki_dir, limit)` | gera casos título→artigo | I/O |
| `run_bench(mode, k)` | orquestra: golden → `search()` → métricas | I/O |

**Formato do golden set:**

```json
{
  "cases": [
    {"question": "o que é circuit breaker", "expected": ["circuit-breaker"]},
    {"question": "como evitar falha em cascata", "expected": ["falhas-em-cascata", "bulkheads"]}
  ]
}
```

`expected` são slugs (stem do arquivo), não caminhos — sobrevivem a mudança de pasta por topic.

## Decisões

1. **Métrica por slug, não por path.** O topic de um artigo pode mudar; a identidade não.
2. **`--seed` sem LLM.** Título como pergunta é fraco como avaliação, mas é honesto, gratuito e determinístico — e um sistema que não acha o artigo pelo próprio título tem bug, não tem nuance. Serve de piso, e o usuário cura por cima.
3. **Caso inválido é categoria própria.** Se o artigo esperado sumiu do corpus, isso não é falha de recuperação — misturar as duas coisas produziria um número que piora sozinho conforme a wiki evolui.
4. **Uma configuração por execução.** Comparar é rodar duas vezes e olhar os dois números; embutir a comparação no comando esconderia qual configuração estava ativa.
5. **Cabeçalho registra o estado do servidor.** Um `hybrid` medido com o servidor fora é um `lexical` disfarçado — o pior tipo de número.

## Condições binárias de risco

- Output estrutural estável: **sim** — `--json` é contrato parseável
- Demais condições: não

## Arquivos

| Arquivo | Mudança |
|---|---|
| `kb/bench.py` | novo |
| `kb/cli.py` | comando `bench` |
| `tests/unit/test_bench.py` | novo — foco nas métricas puras |
| `tests/integration/test_bench_cli.py` | novo |

## Riscos

- **Golden set semeado por título mede pouco.** Mitigado por ser explicitamente um piso, e por o relatório distinguir casos semeados de casos curados seria complexidade extra — deixo o registro no REPORT.
- **`hybrid` não é determinístico entre execuções** se o índice mudar no meio. Aceito: o cabeçalho traz a contagem de artigos indexados.
