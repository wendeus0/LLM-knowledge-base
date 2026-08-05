# PLAN — Plataforma de estudos web

**Branch:** `feat/026-plataforma-estudos` (existente; não criar outra)
**Data:** 2026-08-02
**Spec:** `features/026-plataforma-de-estudos/SPEC.md`
**Escopo entregue nesta branch:** F0 de identidade como gate, F1 (API HTTP), F2 (leitor) e também F3–F5, que o corte original previa para depois e entraram na mesma branch assim que o leitor foi validado (ver `REPORT.md`). O que este PLAN chama de "posterior" abaixo descreve a intenção no momento do planejamento, não o que ficou de fora.

## Contexto técnico

| Campo | Valor |
|---|---|
| Linguagem/versão | Python 3.11+ |
| Dependências principais | `fastapi`, `uvicorn`, `jinja2`, `markdown-it-py`, `mdit-py-plugins` e `fsrs`; os extras `api` e `study` já estão declarados em `pyproject.toml`. |
| Storage | Corpus permanece em `KB_DATA_DIR/wiki/`; estado da plataforma usa `KB_DATA_DIR/study/study.db`, separado de `kb_state/` e da wiki. |
| Estratégia de testes | `test-design`, com `test-red` como base, fixtures de wiki/estado integralmente isoladas, HTTP via `TestClient` e prova renderizada no browser para a UI. |
| Plataforma alvo | Dois serviços locais em loopback: API FastAPI e leitor Jinja2/htmx/Alpine. |
| Tipo de projeto | Monorepo: `kb/` continua engine headless; `study/` é o segundo produto local. |
| Constraints | Sem ORM, sem migrations versionadas, sem escrita em `wiki/`, sem `Path` no contrato, sem busca própria no leitor, sem autenticação/exposição de rede nesta fase. |

## Arquitetura escolhida

A fronteira entre os produtos é HTTP local. `kb/api/` adapta capacidades já existentes da engine, sem duplicar recuperação, Q&A, guardrails ou métricas. `study/` fala apenas com essa API por HTTP e renderiza as páginas; o navegador fala apenas com o leitor. Assim, o mesmo-origin do leitor não exige expor a API ao browser nem introduzir CORS nesta entrega.

```text
browser
  │ HTTP loopback
  ▼
study/ (Jinja2 + htmx + Alpine + Markdown renderer)
  │ HTTP loopback; rel_slug e JSON serializável
  ▼
kb/api/ (FastAPI, schemas e adaptadores)
  ├─► kb/search.py       busca híbrida + rerank configurado
  ├─► kb/qa.py           QA estruturado + guardrails/grounding
  ├─► kb/graph.py        índice único de wikilinks + backlinks
  ├─► kb/stats.py        métricas agregadas
  └─► KB_DATA_DIR/wiki/  somente leitura

F3–F5 (posterior): study/state.py ─► KB_DATA_DIR/study/study.db
```

F0 é um gate, não uma segunda identidade: `rel_slug` é o caminho relativo a `wiki/`, sem extensão, em URLs, JSON, templates e SQLite. O índice de `kb.graph.build_link_index()` é construído uma vez por carga/atualização controlada. Um wikilink qualificado resolve diretamente; um link com stem ambíguo não é convertido para um destino arbitrário e o leitor mostra falha de navegação.

As rotas de F1 ficam em loopback e retornam modelos Pydantic que excluem `Path`: `GET /health`, `GET /search`, `POST /qa`, `GET /article/{slug:path}`, `GET /stats` e `GET /articles` — a listagem entrou durante a F2, quando ficou claro que a home e a sidebar não tinham como montar "últimos artigos" nem "artigos deste topic" sem furar a fronteira HTTP do ADR-0019. São seis. `POST /qa` não faz file-back e fixa `saved_path: null`; seu corpo é equivalente campo a campo ao JSON de `kb qa --json`. `SensitiveContentError` torna-se HTTP 409 seguro, sem confirmação interativa.

## Decisões técnicas

1. **Decisão:** separar `kb/api/` de `study/` e comunicar somente por HTTP loopback. **Motivo:** concretiza a fronteira do ADR-0019, mantém a engine reusável e impede imports de domínio do `kb` em templates.
2. **Decisão:** adaptar `search`, `answer_with_grounding`, `collect_stats` e o índice de grafo; não reimplementar suas regras na API ou no leitor. **Motivo:** preserva a ordenação híbrida/rerank, o JSON de QA e a política de guardrails já contratados pela SPEC.
3. **Decisão:** usar `rel_slug` como único identificador externo e validar o slug antes de qualquer acesso. **Motivo:** stems colidem no vault; `Path` viola RT-03 e um slug não validado abre risco de traversal.
4. **Decisão:** manter o leitor como segundo serviço que consulta a API por HTTP, com adaptador HTTP stdlib testável. **Motivo:** preserva a fronteira real entre serviços e evita CORS ao deixar o browser no mesmo origin de `study/`.
5. **Decisão:** renderizar Markdown com `markdown-it-py` e um renderer de wikilink que consulta o índice já carregado. **Motivo:** links e backlinks preservam a identidade por `rel_slug` sem varrer o vault por link ou criar índice de relevância próprio.
6. **Decisão:** fechar tokens concretos de UI antes do GREEN visual e validar a tela renderizada. **Motivo:** `DIRECAO-VISUAL.md` fixa layout e direção, mas exige `visual-direction` para cores, escala e espaçamento; ler template não prova aparência.
7. **Decisão:** para F3–F5, usar `sqlite3` da stdlib em `study/state.py`, com `_ensure_schema(conn)` idempotente e alterações aditivas locais. **Motivo:** segue `kb/core/tracking.py`, evita ORM e migrations versionadas, e mantém o estado de estudo fora da wiki e de `kb_state/`.
8. **Decisão:** destacar por texto citado e deslocamento aproximado; quando o texto não é reencontrado, marcar `orphaned`, ocultar da leitura e listar para ação humana. **Motivo:** a SPEC proíbe apagar o estudo ou reposicioná-lo por adivinhação após `compile`/`heal`.
9. **Decisão:** aceitar flashcard somente se o grounding for literalmente `ancorada`; `contradita`, `sem apoio`, `degraded` e `skipped` ficam em curadoria. **Motivo:** indisponibilidade de verificação não pode virar aprovação implícita.
10. **Decisão:** registrar ratings FSRS 1:1 (`Again`, `Hard`, `Good`, `Easy`) como 1–4 e calcular `due_at` pela biblioteca. **Motivo:** elimina uma escala intermediária que distorceria o agendamento e impede edição manual da data devida.

## Módulos e pontos de integração

| Arquivo | Mudança planejada |
|---|---|
| `kb/api/app.py` | Novo: aplicação FastAPI, bind configurável porém restrito a loopback no comando de execução, registro das seis rotas e mapeamento seguro de erros. |
| `kb/api/schemas.py` | Novo: modelos de request/response serializáveis; proíbe `Path` e fixa o schema público de QA. |
| `kb/api/articles.py` | Novo: valida `rel_slug`, lê artigo permitido, deriva metadados e backlinks do índice carregado e devolve 400/404 sem vazar paths. |
| `kb/search.py`, `kb/qa.py`, `kb/stats.py`, `kb/graph.py` | Integração somente por adaptadores: preservar busca ordenada, QA/grounding, agregados e índice; F0 é confirmado antes de alterar qualquer camada. |
| `kb/config.py` | Novo diretório de estado `study/` sob `KB_DATA_DIR` para F3–F5, sem reutilizar `STATE_DIR`. |
| `study/app.py` | Novo: aplicação do leitor, rotas de páginas e cliente HTTP para `kb/api/`, sem importar módulos de domínio do `kb`. |
| `study/render.py` | Novo: Markdown, transformação de wikilinks para URLs por `rel_slug`, backlinks e tratamento visível de link ambíguo/inconsistente. |
| `study/templates/` | Novo: layout, artigo, fragmentos htmx de busca/QA e sidebar de trilha. |
| `study/static/` | Novo: tokens claro/escuro, layout de leitura e JavaScript mínimo para alternância/atalhos que htmx não cobre. |
| `study/state.py` | Novo, posterior: SQLite de notas, destaques, cartões, revisões e operações transacionais de curadoria/agendamento. |
| `study/cards.py` e `study/review.py` | Novos, posteriores: geração/grounding de cartões e ponte 1:1 entre rating da UI e FSRS. |
| `tests/unit/test_api_*.py`, `tests/integration/test_api_*.py` | Novos: contratos HTTP, serialização, traversal, equivalência ordenada e isolamento de estado. |
| `tests/unit/test_study_*.py`, `tests/integration/test_study_*.py` | Novos: renderer, banco, transições, integração HTTP e fluxos do leitor; testes de browser para afirmações de aparência. |

## Schema SQLite da plataforma

O banco posterior é `KB_DATA_DIR/study/study.db`. O módulo abre conexões com `sqlite3`, habilita chaves estrangeiras por conexão, chama `_ensure_schema(conn)` antes de operar e faz `commit()` explícito, no padrão de `kb/core/tracking.py`. Não há ORM, tabela de versão de migration ou escrita nos JSONs de `kb_state/`.

| Tabela | Colunas e invariantes |
|---|---|
| `notes` | `id INTEGER PRIMARY KEY`, `rel_slug TEXT NOT NULL`, `body TEXT NOT NULL`, `created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`. Cada nota pertence ao artigo por `rel_slug`, nunca por path. |
| `highlights` | `id INTEGER PRIMARY KEY`, `rel_slug TEXT NOT NULL`, `quoted_text TEXT NOT NULL`, `approximate_offset INTEGER NOT NULL`, `status TEXT NOT NULL CHECK (status IN ('active','orphaned'))`, `created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`. A reabertura busca `quoted_text`; ausência vira `orphaned`. |
| `flashcards` | `id INTEGER PRIMARY KEY`, `rel_slug TEXT NOT NULL`, `front TEXT NOT NULL`, `back TEXT NOT NULL`, `status TEXT NOT NULL CHECK (status IN ('curated','accepted','discarded'))`, `grounding_status TEXT NOT NULL`, `grounding_evidence TEXT`, `fsrs_state TEXT`, `due_at TEXT`, `created_at TEXT NOT NULL`, `updated_at TEXT NOT NULL`, `accepted_at TEXT`. Aceitação é guardada pela aplicação para `grounding_status = 'ancorada'`; agenda é estado FSRS serializado, não data manual. |
| `reviews` | `id INTEGER PRIMARY KEY`, `flashcard_id INTEGER NOT NULL REFERENCES flashcards(id)`, `rel_slug TEXT NOT NULL`, `rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 4)`, `reviewed_at TEXT NOT NULL`, `due_at TEXT NOT NULL`, `fsrs_state TEXT NOT NULL`. O `rel_slug` repetido dá rastreabilidade por artigo sem derivar path; `due_at` é resultado do FSRS. |

Índices posteriores: `notes(rel_slug)`, `highlights(rel_slug, status)`, `flashcards(rel_slug, status, due_at)` e `reviews(flashcard_id, reviewed_at)`. Todas as datas usam ISO-8601 UTC. A regra de aceitação e o cálculo de agenda são transacionais: uma revisão inválida não altera `flashcards.due_at` nem cria `reviews`.

## Condições binárias de risco

| Condição | Marca | Por quê |
|---|---|---|
| Endpoint HTTP público | não | API e leitor aceitam somente loopback; não há exposição de rede nesta feature. |
| I/O em DB real / migration / query não-trivial | **sim** | F3–F5 adicionam SQLite persistente, foreign keys, estados de curadoria e agenda calculada. |
| UI com estado interativo | **sim** | Tema, busca/QA, notas, curadoria e revisão mudam estado e fluxo de teste. |
| Output estrutural estável | **sim** | O JSON das seis rotas, sobretudo `/qa`, é contrato público parseável e não pode vazar `Path`. |
| Contrato HTTP entre serviços | **sim** | `study/` depende do comportamento e dos erros de `kb/api/` por HTTP. |
| Contrato frontend↔backend | **sim** | Templates/htmx consomem respostas serializadas da API por meio do cliente do leitor. |
| Fluxo E2E multi-página/browser real | **sim** | Leitura, links/backlinks, sidebar, tema, busca/QA e revisão atravessam páginas e interação real. |

Como há condições marcadas, o fluxo é **`test-design`**, que orquestra **`test-red`** como camada base antes do GREEN. Contratos JSON/HTTP, SQLite isolado e fluxo de browser recebem testes de desenho específicos; aparência renderizada tem checkpoint HITL.

## Success metric

```yaml
success_metric:
  name: "ciclo local de estudo sem alterar a wiki"
  target: "Sem meta numérica medida nesta etapa; demonstrar os AC-01 a AC-09 no MVP F1+F2 e manter F3–F5 como entrega posterior."
  observable_at: "testes de contrato/integracao e evidência HITL da tela renderizada"
  measure_window: "validação da feature antes de aprovar a entrega"
  baseline: "não medido"
```

## Constitution check

O plano mantém o corpus fora do repositório e a wiki sob domínio exclusivo da engine: F1/F2 somente leem `wiki/`, e F3–F5 escrevem apenas no banco da plataforma. Chamadas de QA e geração continuam sujeitas aos guardrails; a API converte conteúdo sensível em 409, sem confirmação interativa. O uso de `rel_slug` evita serializar paths. Nenhuma tarefa cria branch, commit ou push.

## Dependências entre componentes

1. F0 prova a identidade e a resolução determinística antes de qualquer URL ou payload de artigo.
2. A fundação da API e seus schemas habilitam health, artigo, busca, QA e stats sem acoplamento do leitor ao domínio.
3. As seis rotas contratuais habilitam o cliente HTTP de `study/` e seus fragmentos de leitura, busca e pergunta.
4. O renderer e o índice habilitam wikilinks/backlinks corretos; os tokens visuais e a prova em browser habilitam a validação de F2.
5. Depois de F2 validado, SQLite habilita notas/destaques; curadoria ancorada habilita flashcards aceitos; somente então FSRS habilita revisão e calendário.

## Limitações e riscos residuais

- O primeiro corte não entrega persistência de estudo, flashcards, revisão ou calendário; F3–F5 não devem ser apresentados como concluídos pelo MVP F1+F2.
- A API local sem autenticação é apropriada apenas para loopback. Qualquer acesso remoto exige novo ADR para threat model, auth e HTTPS.
- O reader precisa informar links ambíguos em vez de inventar um destino; qualificar os wikilinks do corpus continua sendo responsabilidade do fluxo da engine.
- Destaques podem se tornar órfãos após `compile` ou `heal`; a política preserva o dado, mas requer uma superfície posterior de manutenção.
- FSRS e grounding introduzem dependências operacionais; falha de grounding mantém cartões em curadoria e falha de agendamento conserva a última agenda válida.
- Não há linha de base numérica de uso, latência ou adesão do leitor; o plano não inventa metas para essas medições.

## Divergências entre o planejado e o entregue

Registradas aqui em vez de reescritas acima: o texto do plano vale como intenção da época, e o `REPORT.md` vale como estado real.

| Planejado | Entregue | Por quê |
|---|---|---|
| Cinco rotas em F1 | Seis — `GET /articles` entrou junto | Home e sidebar precisavam de listagem; sem ela, o leitor importaria `kb` direto e furaria o ADR-0019 |
| `study/app.py` | `study/web.py` | Nome do módulo; nenhuma mudança de arquitetura |
| `study/state.py` como SQLite único | `study/db.py` (esquema e conexão) + `notes.py`, `highlights.py`, `cards.py`, `review.py` | Um módulo por assunto ficou mais legível que um `state.py` com quatro domínios |
| Banco em `KB_DATA_DIR/study/study.db` | `KB_DATA_DIR/study.db` | Diretório extra sem conteúdo próprio; o teste `test_study_annotations.py` fixa que o banco fica ao lado do vault e fora de `wiki/` e `kb_state/` |
| F3–F5 depois do MVP | Na mesma branch | O leitor foi validado e o ciclo de estudo só fecha com nota, cartão e revisão |
