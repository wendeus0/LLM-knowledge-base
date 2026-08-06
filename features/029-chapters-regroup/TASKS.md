# TASKS — 029-chapters-regroup

**Spec:** `features/029-chapters-regroup/SPEC.md`
**Plan:** `features/029-chapters-regroup/PLAN.md`

```yaml
- id: C1
  priority: P1
  parallel: false
  depends_on: []
  ac_ref: RF-01
  tag: AFK
  vertical_slice: yes
  behavior: "iter_articles único honra _*/.*/symlink e é adotado por lint, heal, archive, update_index e stats; heal deixa de poder tocar _summaries hoje."
  verify: "python -m pytest tests/unit/test_fsutil_articles.py tests/unit/test_lint.py tests/unit/test_heal.py tests/unit/test_archive.py tests/unit/test_stats.py -q"
  state: passing
```

```yaml
- id: C2
  priority: P1
  parallel: false
  depends_on: [C1]
  ac_ref: RF-02
  tag: AFK
  vertical_slice: yes
  behavior: "Stub removido pelo heal vai para archive/ com backup versionado e manifest marcado archived — nunca unlink (V7 mínimo)."
  verify: "python -m pytest tests/unit/test_heal.py -q"
  state: passing
```

```yaml
- id: C3
  priority: P1
  parallel: false
  depends_on: [C1]
  ac_ref: RF-03, RF-04, RF-06
  tag: AFK
  vertical_slice: yes
  behavior: "kb regroup scan agrupa por manifest.book com unresolved como braço humano; apply --book move artigo+summary para _chapters/, atualiza manifest e índices, commita por livro."
  verify: "python -m pytest tests/unit/test_regroup.py tests/integration/test_regroup_cli.py -q"
  state: passing
```

```yaml
- id: C4
  priority: P1
  parallel: false
  depends_on: [C2, C3]
  ac_ref: RF-05
  tag: HITL
  vertical_slice: yes
  behavior: "Gate final do dono: relatório de grupos → aprovação explícita (a wiki esvazia) → apply livro a livro com tag prévia → index build + smoke + tela."
  verify: "relatório aprovado + contagens + tela"
  state: passing
```

## Definition of Done

`state: passing` = verify verde + (HITL) evidência de aprovação e tela. Feature fecha com C1–C4 passing e `quality-gate` PASS.
