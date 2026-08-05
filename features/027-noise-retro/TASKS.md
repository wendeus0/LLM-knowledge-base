# TASKS — 027-noise-retro

**Spec:** `features/027-noise-retro/SPEC.md`
**Plan:** `features/027-noise-retro/PLAN.md`

```yaml
- id: T-001
  priority: P1
  parallel: false
  depends_on: []
  ac_ref: RF-01, RF-02
  tag: AFK
  vertical_slice: yes
  behavior: "kb noise scan varre raw/books/ e library/*/*/ e devolve candidatos estruturados (livro, título do capítulo, categoria, artigo, summary), com contenção de path preservada nas duas raízes."
  verify: "python -m pytest tests/unit/test_noise.py -q"
  state: passing
```

```yaml
- id: T-002
  priority: P1
  parallel: false
  depends_on: [T-001]
  ac_ref: RF-03, RF-04, RF-05, RF-06
  tag: AFK
  vertical_slice: yes
  behavior: "kb noise apply move artigos (e summaries) via semântica move_to_archive preservando hierarquia com backup versionado, commita origem+destino, regenera _index.md e atualiza embeddings; capítulos-fonte intocados."
  verify: "python -m pytest tests/unit/test_noise.py tests/integration/test_noise_cli.py -q"
  state: passing
```

```yaml
- id: T-003
  priority: P1
  parallel: false
  depends_on: [T-002]
  ac_ref: RF-01..RF-06
  tag: HITL
  vertical_slice: yes
  behavior: "Lote real no vault: preflight (working tree limpa, crontab sem kb, tag git), scan, relatório book-qualified, aprovação do dono, apply --commit, contagens conferidas e home da plataforma verificada em tela."
  verify: "kb noise scan && kb stats (antes/depois) + aprovação registrada"
  state: passing
```

## Definition of Done

`state: passing` = verify verde + (HITL) evidência de aprovação e tela. Feature fecha com T-001..T-003 passing e `quality-gate` PASS.
