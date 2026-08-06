# REPORT — 028-provenance-dedup-topics

**Estado:** `DONE_WITH_CONCERNS`
**Tela:** trilha `operations` com 123 artigos e "Artigo 1 de 123 na trilha" conferida no leitor (screenshot em `.playwright-mcp/trilha-operations.png`, não versionado)
**Branch:** `feat/028-provenance-dedup-topics`

## Contexto

Segunda feature do esforço de higiene (etapas 1–2 do ADR-0018, plano de 2026-08-05). Antes dela: manifest com 5 entradas em 1.042 artigos, duplicatas de ingestão visíveis na home da plataforma, 429 artigos `general` na raiz e uma cauda de topics-variante que `canonical_topic` colapsaria.

## Mudanças (engine)

- **`kb/state.py`** — manifest v2 aditivo: `source` relativo a `DATA_DIR`, `article` relativo a `WIKI_DIR`, `book`, `provenance`, `status: archived`; compat legada (`provenance` ausente ⇒ `compile`); helpers `mark_archived`/`update_article_path` — o guard de recompile nunca mais fica apontando para path inexistente em silêncio.
- **`kb/backfill.py` + `kb manifest backfill`** — cadeia basename único → conteúdo idêntico → cosseno (piso 0,75, embed on-demand com degrade) → `unresolved` explícito. Sem braço LLM: proveniência nunca é inventada.
- **`kb/dedup.py` + `kb dedup scan|apply`** — dupla-chave (mesma fonte ∪ cosseno ≥0,95 ∧ ratio ≥0,85), sobrevivente por regra (topic > raiz; empate → mais palavras), summary acompanha, manifest atualizado. **Achado que mudou o desenho:** o caso emblemático (mesmo documento OWASP em duas URLs) tem cosseno 0,976 e ratio 0,248 — nenhuma chave automática o pega, e afrouxar o ratio engoliria pares temáticos. Solução: `review_candidates` — a máquina lista os gêmeos semânticos de prosa distinta e o humano decide.
- **`kb/topics.py` + `kb topics normalize|assign`** — normalize determinístico pelo mapa aprovado; assign via LLM **restrito** à taxonomia (resposta fora da lista é rejeitada no parse, nunca gravada); escrita por regex in-place atômica (o serializer de frontmatter não faz round-trip fiel). `KB_TOPICS` no `.env` do engine com os 10 canônicos, validado contra `canonical_topic` no ambiente real.

## Lotes no vault (todos com relatório → aprovação do dono → apply → commit)

| Lote | Resultado | Commit |
|---|---|---|
| B3 backfill | 859 entradas materializadas (824 basename, 23 conteúdo, 12 cosseno com score); 121 `unresolved` explícitos | `e253c6d` |
| B5 dedup | 4 pares mesma-fonte + par OWASP (aprovado da lista de revisão); manifest repontado pós-move; 55 gêmeos temáticos preservados para o reagrupamento | `baddaf4`, `486a4be` |
| B6 normalize | 15 variantes → canônicos | `fcd45ff` |
| B8 assign | 429 aplicados, zero rejeições; distribuição final do vault: algorithms 254, software-architecture 229, operations 123, learning 96, ai 80, python 79, testing 43, data 33, harness 23, cybersecurity 15 — zero `general` | `942f7e5` |

Vault: 1.042 → **975 artigos vivos** (somando os lotes da 027); manifest com **854 entradas** de proveniência auditável; tags de rollback por lote (`pre-backfill`, `pre-dedup`, `pre-topics`). Tela conferida: home sem a duplicata OWASP; trilhas por topic real.

## Validação

**1.016 passed**, ruff limpo, appeasement exit 0, cobertura 93%. Suíte isolada do `.env` do desenvolvedor (o reload de `kb.config` re-executava `load_dotenv` e o novo `KB_TOPICS` vazou para um teste — corrigido com no-op de dotenv no fixture).

## Riscos e dívida

| Item | Estado |
|---|---|
| **`topics assign --apply` reclassifica em vez de consumir o relatório aprovado** | Temperatura 0 e modelo local minimizam divergência, e frontmatter é reversível por linha — mas o desenho certo é o scan persistir propostas e o apply consumi-las. Registrado como melhoria |
| 121 artigos `unresolved` sem proveniência | Explícitos no manifest? Não — ficam FORA do manifest por decisão (nunca inventar). Braço humano do agrupamento (029) |
| 55 gêmeos temáticos | Insumo do reagrupamento; lista reproduzível via `kb dedup scan` |
| Upsert do backfill esconde colisão de fonte durante o apply | Mitigado: o dedup por fonte roda sobre os links recomputados, não sobre o manifest; o reponte pós-dedup corrige as entradas |

## Próximos passos

Feature 029 (`chapters-regroup`): C1 helper `_*` (corrige bug latente do heal em `_summaries` hoje), C2 heal sem unlink, C3 agrupamento por `manifest.book`, C4 move final com gate explícito do dono.
