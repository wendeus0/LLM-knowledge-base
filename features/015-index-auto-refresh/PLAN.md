# PLAN — 015-index-auto-refresh

## Arquitetura

Uma função em `kb/embeddings.py`, chamada pelos três comandos que escrevem na wiki:

```
refresh_embeddings_index(enabled: bool) -> dict | None
    ├─ enabled falso ou KB_INDEX_AUTO_REFRESH=0  → None (não toca em nada)
    ├─ probe do servidor indisponível            → None + aviso em stderr
    └─ build_index(WIKI_DIR, STATE_DIR)          → relatório (incremental por hash)
        └─ qualquer exceção                       → None + aviso; nunca propaga
```

Chamada em três lugares, sempre **ao fim** do trabalho:

| Comando | Ponto | Observação |
|---|---|---|
| `kb compile` | fim de `compile_many`, junto de `update_index` (`kb/compile.py:53-54`) | uma vez por lote, não por artigo |
| `kb heal` | fim de `heal()`, após o laço | cobre reescrita e remoção |
| `kb qa --to-wiki` | após `out.write_text` (`kb/qa.py:167`) | só no caminho `--to-wiki` |

**Por que ao fim do lote:** `build_index` varre o corpus e compara hashes. Chamá-lo por artigo transformaria um compile de 100 capítulos em 100 varreduras de 1.037 arquivos. Ao fim, é uma varredura e N embeds — o mesmo custo de rede, uma fração do I/O.

**Por que em `embeddings.py` e não num módulo novo:** a função é uma composição fina de `build_index` (mesmo módulo) com `probe` (014). Módulo novo para cinco linhas seria cerimônia.

## Decisões

1. **Default ligado.** Índice defasado tem valor negativo — responde com confiança sobre um corpus que não existe mais. O custo é proporcional ao que mudou, e quem escreveu o artigo é justamente quem quer encontrá-lo.
2. **Nunca propaga falha.** O comando principal (compilar, curar, arquivar) já terminou seu trabalho; falhar por causa do índice seria trocar um efeito colateral por um erro.
3. **Probe antes de tentar.** Sem servidor, `build_index` levantaria RuntimeError no meio do lote. Probe é mais barato que a falha.
4. **Aviso em stderr**, como a 014 estabeleceu — stdout dos comandos continua parseável.

## Condições binárias de risco

- Endpoint HTTP público: não
- I/O em DB real / migration: não
- UI com estado interativo: não
- Output estrutural estável: **sim** — saída de `compile`/`heal` ganha linha nova
- Contrato HTTP entre serviços: não
- Fluxo E2E multi-página: não

## Arquivos

| Arquivo | Mudança |
|---|---|
| `kb/embeddings.py` | `refresh_embeddings_index()` |
| `kb/compile.py` | chamada ao fim de `compile_many`; parâmetro de controle |
| `kb/heal.py` | chamada ao fim de `heal()`; parâmetro de controle |
| `kb/qa.py` | chamada no caminho `--to-wiki` |
| `kb/cli.py` | flag `--no-index-refresh` nos três comandos |
| `tests/unit/test_index_refresh.py` | novo |
| `tests/integration/test_index_refresh_cli.py` | novo |

## Riscos

- **Latência percebida:** compile de 1 artigo passa a fazer varredura de 1.037 hashes (~0,7s medido no rebuild anterior). Aceitável; mensurar no REPORT.
- **Compile em lote grande:** 100 capítulos → 100 embeds extras. É o custo correto, mas é custo. `--no-index-refresh` é a válvula para importações grandes.
- **`heal` que apaga artigo:** `build_index` já remove do índice o que sumiu do corpus — comportamento herdado, não novo.
