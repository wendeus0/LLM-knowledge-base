---
feature: 028-provenance-dedup-topics
status: validated
validated_at: 2026-08-05
validated_by: orquestrador (Fable 5), premissas verificadas por exploração + medição no vault real
---

# CONTRACT — 028-provenance-dedup-topics

## Premissas técnicas verificadas

| # | Premissa | Verificação | Estado |
|---|---|---|---|
| 1 | O pareamento por basename cobre a maioria | medição de 2026-07-31: 834 basename único + 23 conteúdo idêntico = 857/1.037; 63 ambíguos; 117 sem candidato (`MEDICAO-CORPUS.md:111-120`) | **confirmado** (recontar pós-027: 62 artigos a menos) |
| 2 | Fontes existem em três raízes | `source_candidates=library:804, raw:0, wiki/_sources:712` | **confirmado** |
| 3 | Índice de embeddings dá o vetor do artigo sem re-embedar | `kb_state/embeddings.json` formato 2, vetores por chunk com média L2 já usada pelo script de medição | **confirmado** |
| 4 | Embedar capítulo ambíguo on-demand é viável | servidor `:1234` (LaunchAgent) ativo; `embed_texts` disponível | **confirmado** — degrade para `unresolved` se fora |
| 5 | Manifest atual não conflita | 5 entradas, todas de `kb ingest` cybersecurity, fora dos alvos do backfill (que as preserva) | **confirmado** |
| 6 | `canonical_topic` colapsa topic fora de `KB_TOPICS` para `general` | `kb/config.py:58-62`; `KB_TOPICS` ausente no `.env` do engine (o do vault não existe) | **confirmado** — B6 seta no engine |
| 7 | Frontmatter não faz round-trip fiel pelo serializer | `parse`/`serialize` reordenam e reescrevem aspas | **confirmado** — edição regex in-place |
| 8 | O guard de recompile é `find_compiled_entry` | `kb/state.py:92-97` ← `_resolve_output_path` | **confirmado** — teste de não-regressão obrigatório |

## Premissas de produto (do DOMAIN)

- Dedup só de duplicata de ingestão; par temático intocável (veto do ADR-0018 a V5 isolado).
- Sobrevivente: path com topic vence a raiz; empate → mais palavras.
- Topic é só frontmatter; nenhum arquivo muda de path nesta feature.
- Taxonomia de topics é fechada pelo dono no relatório B6, antes de qualquer assign.
- Todo lote: relatório (dry-run default) → aprovação → apply → commit no vault.

## Riscos aceitos

| Risco | Mitigação |
|---|---|
| Limiar de dedup (0,95 / 0,85) engolir par temático | Dupla-chave é candidatura; diff por par no relatório; gate humano |
| Backfill por cosseno atribuir livro errado a ambíguo | `provenance: backfill-cosine` com score gravado — auditável e revisável no agrupamento (029) |
| LLM propor topic fora da taxonomia | Rejeição dura no parse; proposta rejeitada aparece no relatório como pendência |
| 117 `unresolved` | Aceito — braço humano do agrupamento (029); nunca inventar proveniência |

## Gate de TDD

3 condições binárias de risco (output estrutural, store real, não-determinístico) → `test-design` com `test-red` base; `topics assign` ganha testes de restrição com LLM mockado (eval real fica para o lote HITL, que é gate humano por construção).
