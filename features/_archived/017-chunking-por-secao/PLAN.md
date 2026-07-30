# PLAN — 017-chunking-por-secao

## Arquitetura

A divisão é pura e testável isoladamente; o resto é adaptação do que já existe.

| Função | Responsabilidade | Pureza |
|---|---|---|
| `split_sections(text)` | corpo → lista de `(heading, conteúdo)`, incluindo preâmbulo | pura |
| `build_chunks(title, text, max_chars, min_chars)` | seções → chunks com contexto, agrupando curtas e dividindo longas | pura |
| `build_index` | passa a iterar chunks por artigo | I/O |
| `semantic_ranking` | cosseno por chunk, agregação por máximo | I/O leve |

## Formato do índice

```json
{
  "format": 2,
  "model": "...",
  "dim": 768,
  "articles": {
    "ai/artigo.md": {
      "hash": "sha256 do arquivo inteiro",
      "chunks": [
        {"heading": "O que é", "vector": [...]},
        {"heading": "Gotchas", "vector": [...]}
      ]
    }
  }
}
```

Manter `articles` como chave de topo preserva a incrementalidade por artigo (RF-06) e a remoção de artigo apagado, que já funcionam. `format: 2` é o discriminador do RF-07 — ausente significa formato 1 (um vetor por artigo).

## Decisões

1. **Agregação por máximo, não soma.** Soma premiaria artigo longo por ter mais chunks — exatamente o viés que o chunking existe para corrigir. Máximo responde "este artigo tem uma seção que casa muito bem", que é o que interessa.
2. **Hash por artigo, não por chunk.** Editar um artigo refaz todos os seus chunks. Hash por chunk economizaria embeds em edição pontual, mas exigiria rastrear identidade de chunk através de reordenações de seção — complexidade desproporcional ao ganho.
3. **Contexto no texto embedado.** `<título> — <heading>` antes do conteúdo. Uma seção "Gotchas" isolada não diz de que assunto ela trata; com o título, diz.
4. **Agrupar seções curtas.** Uma seção de 80 caracteres vira vetor de ruído que pode casar com qualquer coisa. Mínimo de ~200 chars, agrupando com a seguinte.
5. **Sem overlap.** Seções são unidades semânticas naturais e a mediana é 647 chars — o risco de cortar uma ideia ao meio é baixo. Medir antes de adicionar complexidade.

## Custo estimado

7.743 seções → após agrupamento de curtas, algo entre 5k e 7k chunks. Build inicial ~5–9 min (contra 70s hoje). Índice cresce de 17,8 MB para algo entre 90 e 120 MB. Busca: cosseno sobre ~7k vetores em vez de 1k — de ~30ms para ~200ms por query, estimado; **medir**, e se doer, `numpy` entra (wheel já em cache).

## Condições binárias de risco

- Output estrutural estável: **sim** — formato do índice muda
- Demais: não

## Arquivos

| Arquivo | Mudança |
|---|---|
| `kb/chunking.py` | novo — `split_sections`, `build_chunks` |
| `kb/embeddings.py` | `build_index`, `load_index`, `semantic_ranking`, `index_status` |
| `kb/cli.py` | contagem de chunks no `index status`/`build` |
| `tests/unit/test_chunking.py` | novo |
| `tests/unit/test_embeddings_chunks.py` | novo |

## Riscos

- **Latência de busca** cresce ~7×. Mensurável no bench; `numpy` é o plano B.
- **Ganho pode não vir.** Se o recall não melhorar, a feature é revertida e o aprendizado registrado — é para isso que a baseline existe. Critério: `recall@5 > 0,420` no golden curado.
- **Índice 6× maior** em disco. 120 MB num vault de 36 MB de texto é desproporcional mas aceitável localmente; se incomodar, quantização é fatia futura.
