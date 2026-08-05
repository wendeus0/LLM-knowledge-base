# TASKS — 028-provenance-dedup-topics

**Spec:** `features/028-provenance-dedup-topics/SPEC.md`
**Plan:** `features/028-provenance-dedup-topics/PLAN.md`

```yaml
- id: B1
  priority: P1
  parallel: false
  depends_on: []
  ac_ref: RF-01
  tag: AFK
  vertical_slice: yes
  behavior: "Manifest v2 aditivo (source rel DATA_DIR, article rel WIKI_DIR, provenance, book, status archived) com compat legada e helpers mark_archived/update_article_path; find_compiled_entry não regride."
  verify: "python -m pytest tests/unit/test_state.py -q"
  state: passing
```

```yaml
- id: B2
  priority: P1
  parallel: false
  depends_on: [B1]
  ac_ref: RF-02, RF-08
  tag: AFK
  vertical_slice: yes
  behavior: "kb manifest backfill pareia artigo→fonte (basename único → conteúdo → cosseno com piso 0,75 → unresolved), relatório sem --apply, escrita com --apply."
  verify: "python -m pytest tests/unit/test_backfill.py tests/integration/test_manifest_cli.py -q"
  state: passing
```

```yaml
- id: B3
  priority: P1
  parallel: false
  depends_on: [B2]
  ac_ref: RF-02
  tag: HITL
  vertical_slice: yes
  behavior: "Lote real: backfill report no vault → aprovação do dono → --apply --commit; cobertura ≥82% com provenance auditável."
  verify: "kb manifest backfill (report) + aprovação registrada + contagens"
  state: passing
```

```yaml
- id: B4
  priority: P1
  parallel: false
  depends_on: [B1]
  ac_ref: RF-03, RF-04
  tag: AFK
  vertical_slice: yes
  behavior: "Manutenção do manifest em archive/move + kb dedup scan com critério dupla-chave (mesma fonte ∪ cosseno≥0,95 ∧ ratio≥0,85), diff por par e sobrevivente proposto."
  verify: "python -m pytest tests/unit/test_dedup.py tests/unit/test_state.py -q"
  state: passing
```

```yaml
- id: B5
  priority: P1
  parallel: false
  depends_on: [B3, B4]
  ac_ref: RF-05
  tag: HITL
  vertical_slice: yes
  behavior: "Lote real: dedup report com diff → aprovação → apply --commit; par OWASP some da home (tela)."
  verify: "kb dedup scan + aprovação + tela da home"
  state: passing
```

```yaml
- id: B6
  priority: P1
  parallel: true
  depends_on: []
  ac_ref: RF-06
  tag: AFK
  vertical_slice: yes
  behavior: "KB_TOPICS no .env do engine (taxonomia proposta em relatório) + kb topics normalize com mapa fechado de variantes e edição in-place que preserva o resto do arquivo."
  verify: "python -m pytest tests/unit/test_topics.py -q"
  state: not_started
```

```yaml
- id: B7
  priority: P1
  parallel: false
  depends_on: [B6]
  ac_ref: RF-07, RF-08
  tag: AFK
  vertical_slice: yes
  behavior: "kb topics assign propõe topic via LLM restrito à taxonomia (fora da lista → rejeitado no parse), relatório sem --apply."
  verify: "python -m pytest tests/unit/test_topics.py tests/integration/test_topics_cli.py -q"
  state: not_started
```

```yaml
- id: B8
  priority: P1
  parallel: false
  depends_on: [B5, B7]
  ac_ref: RF-06, RF-07
  tag: HITL
  vertical_slice: yes
  behavior: "Lotes reais: taxonomia fechada pelo dono → normalize → assign → apply --commit; trilhas da plataforma povoadas, conferidas em tela."
  verify: "relatórios aprovados + tela das trilhas"
  state: not_started
```

## Definition of Done

`state: passing` = verify verde + (HITL) evidência de aprovação e tela. Feature fecha com B1–B8 passing e `quality-gate` PASS.
