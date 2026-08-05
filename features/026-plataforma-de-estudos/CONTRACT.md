---
feature: 026-plataforma-de-estudos
status: validated
validated_at: 2026-08-02
validated_by: orquestrador (Opus 5) — SPEC, PLAN e TASKS redigidos por GPT 5.6 Terra, revisados zero-trust
---

# CONTRACT — 026-plataforma-de-estudos

Premissas verificadas no ambiente ou no repositório, não assumidas.

## Premissas técnicas verificadas

| # | Premissa | Verificação | Estado |
|---|---|---|---|
| 1 | Dependências disponíveis | `import fastapi, uvicorn, jinja2, markdown_it, mdit_py_plugins, fsrs` passa no venv | **confirmado** — extras `api` e `study` declarados no `pyproject.toml` |
| 2 | Porta livre para a plataforma | `:8000` livre; `:8080` e `:5000` ocupadas | **confirmado** — `:8000` é o alvo. Os quatro serviços do kb (`:1234` embeddings, `:1235` NLI, `:1236` Codex, `:8081` rerank) não conflitam |
| 3 | O contrato JSON do `/qa` existe para copiar | `kb/cli.py:492` inicia o `json.dumps` com `answer` e `grounding` | **confirmado** — RT-04 copia literal, não reinventa |
| 4 | `build_link_index` e `resolve_wikilink_all` disponíveis | import direto passa | **confirmado** — F0 mergeada no PR #65 |
| 5 | `rel_slug` aceita `wiki_dir` explícito | assinatura `(path, wiki_dir=None)` | **confirmado** — a API precisa disso para não depender da global |
| 6 | Padrão de SQLite do projeto existe | `kb/core/tracking.py`: sqlite3 stdlib, `_ensure_schema` com `CREATE TABLE IF NOT EXISTS`, migração leve por `PRAGMA table_info` | **confirmado** — o banco da plataforma segue o mesmo, sem ORM |
| 7 | `B008` isento para os módulos novos | `per-file-ignores` cobre `kb/api/*.py` e `study/*.py` | **confirmado** — FastAPI usa `Depends()`/`Query()` em default, mesmo caso do typer |
| 8 | O grounding roda e serve para verificar card | serviço NLI em `:1235` sob launchd, 6 casos executados com mediana de 281ms | **confirmado** — RF-14 é executável, não aspiracional |

## Premissas de produto

| # | Premissa | Estado |
|---|---|---|
| 9 | A plataforma **não escreve** em `wiki/` | **acordado** — ADR-0019. Elimina o conflito com `compile`/`heal` por construção |
| 10 | A plataforma **não escreve** em `kb_state/` | **acordado** — só lê. `kb_state/*.json` não tem locking (exceto discovery); escrita concorrente com a CLI seria corrida real |
| 11 | Localhost, sem auth, bind em loopback | **acordado** — expor à rede exige ADR próprio (gatilho registrado no 0019) |
| 12 | Roadmap fora desta feature | **acordado** — fase 2; a sidebar da F2 já nasce no formato que ele vai preencher |
| 13 | Card não-ancorado não pode ser aceito | **acordado** — RF-14. `contradita`, `sem apoio`, `degraded` e `skipped` bloqueiam a aceitação |

## Riscos aceitos

| Risco | Mitigação acordada |
|---|---|
| **Seis condições binárias de risco** — a maior contagem de qualquer feature deste repo | Fluxo é `test-design`, não `test-red` puro. Contrato JSON, HTTP, SQLite isolado e fluxo de browser recebem teste de desenho próprio |
| **Aparência renderizada não é verificável por teste unitário** | Tasks de layout e tema são `HITL`. O `AGENTS.md` exige tela renderizada — screenshot ou URL rodando, não leitura de componente |
| **Escopo grande para uma entrega** | Corte aceito, recomendado pelo próprio redator da SPEC: F1 (API) + F2 (leitor) primeiro; F3–F5 declaradas com `depends_on` e entregues depois do leitor validado |
| **Destaque ancora em texto que a engine reescreve** | Política, não trava: âncora perdida vira `órfão` listado à parte. Nunca apagado, nunca reposicionado por aproximação |
| **A API vira contrato a manter** | Enquanto localhost sem auth, o custo é baixo. Terceiro consumidor é gatilho de revisão do ADR-0019 |
| **Duas persistências convivem** | `kb_state/` (corpus) e o banco da plataforma (estudo). Backup passa a ter dois alvos — declarado no ADR |

## Gate de TDD

Seis condições marcadas no PLAN — endpoint público é a única não marcada. Portanto **`test-design`**, com `test-red` como camada base (`RED_OK` segue sendo o gate canônico). Obrigatórios antes do GREEN: teste de contrato HTTP das cinco rotas, teste de estabilidade do JSON, teste de isolamento do SQLite, e teste de traversal em `/article/{slug}`.

## Fora deste contrato

- Roadmap, trilha importada e cobertura curricular (fase 2).
- Autenticação, HTTPS, deploy em VM, acesso remoto.
- Aplicativo nativo.
- Edição, criação ou remoção de artigo compilado.
- Busca própria do front — a do `kb` é requisito, não opção.

## Referências

- `features/026-plataforma-de-estudos/SPEC.md` — `SPEC_VALID` em 2026-08-02
- `features/026-plataforma-de-estudos/PLAN.md` — arquitetura e condições de risco
- `docs/adr/0019-study-platform-as-second-product-over-headless-engine.md`
- `docs/research/2026-08-01-kb-para-estudo/` — map, direção visual e varredura de frontends
