# SDD.md — Software Design Document

## LLM-knowledge-base (kb)

Documento de referência arquitetural. Skills leem este arquivo para entender a estrutura do sistema antes de tomar decisões de design.

---

## Visão Geral

Engine CLI que mantém uma knowledge base viva a partir de documentos brutos: ingestão em `raw/`, compilação assistida por LLM para `wiki/` (markdown com frontmatter YAML e wikilinks), Q&A roteado por fonte, healing estocástico e auditoria. Engine e corpus são separados — código no repositório, dados do usuário em `KB_DATA_DIR`.

**Stack:** Python 3.11+ · Typer (CLI) · Rich (terminal UI) · OpenAI SDK (compatível OpenCode Go) · JSON/JSONL para estado · Markdown + YAML frontmatter para conteúdo · Git como histórico opt-in.

---

## Arquitetura em Camadas

```
┌──────────────────────────────────────────────────────┐
│                  CLI (Typer + Rich)                  │  kb/cli.py
│  ingest · import-book · compile · qa · search       │
│  lint · heal · archive · jobs · discovery · handoff │
├──────────────────────────────────────────────────────┤
│              Orquestração de comandos                │  kb/cmds/ · kb/core/
│  cmds: compile · qa · search · lint · watch         │
│  core: runner · tracking                            │
├──────────────────────────────────────────────────────┤
│                      Domínio                         │  kb/*.py
│  compile · qa · router · search · heal · lint       │
│  claims · audit · guardrails · graph                │
│  book_import · web_ingest · discovery · doc_gate    │
│  handoff · jobs · outputs · archive · analytics     │
├──────────────────────────────────────────────────────┤
│              Estado / Persistência                   │  kb/state.py · kb/git.py
│  manifest.json · knowledge.json · learnings.json    │
│  claims.jsonl · audit.jsonl   (+ commit opt-in)     │
├──────────────────────────────────────────────────────┤
│                    LLM Client                        │  kb/client.py
│  OpenAI SDK · validação provider/model              │
│  fallback de resource limit                         │
└──────────────────────────────────────────────────────┘
            ↕ (KB_BASE_URL / KB_MODEL)
┌──────────────────────────────────────────────────────┐
│         LLM Provider (OpenCode Go default)           │
│  https://opencode.ai/zen/go/v1                       │
│  Modelos validados: kimi-k2.5 · minimax-2.7 · glm-5 │
└──────────────────────────────────────────────────────┘
            ↕ (KB_DATA_DIR — fora do repositório)
┌──────────────────────────────────────────────────────┐
│                Corpus do usuário                     │
│  raw/ · wiki/ · outputs/ · archive/                  │
│  kb_state/ (manifest · knowledge · learnings ·       │
│             claims · audit)                          │
└──────────────────────────────────────────────────────┘
```

---

## Módulos Principais

### `kb/` — domínio

| Arquivo | Responsabilidade |
|---------|------------------|
| `cli.py` | Entry point Typer; declara comandos e sub-apps (`jobs`, `discovery`, `handoff`) |
| `client.py` | Cliente LLM; valida par provider/model; classifica erros de resource limit |
| `config.py` | Resolve `KB_DATA_DIR`, paths e taxonomia de tópicos a partir do ambiente |
| `compile.py` | Pipeline raw → wiki: prompt, escrita com frontmatter, claims compilados |
| `qa.py` | Q&A com routing por fonte; opcional file-back em `outputs/` ou wiki |
| `router.py` | Decide rota (`wiki`/`learnings`/`raw`/`knowledge`) e monta contexto |
| `search.py` | Busca lexical (keyword/TF-IDF simples) sobre `wiki/` |
| `heal.py` | Stochastic heal de N arquivos: links, stubs, reviewed_at |
| `lint.py` | Health checks da wiki (wikilinks quebrados + auditoria LLM) |
| `claims.py` | Lifecycle de claims: confiança, supersession, decaimento |
| `audit.py` | Trilha append-only de eventos sobre claims |
| `guardrails.py` | Detecção de conteúdo sensível antes de chamadas ao provider |
| `state.py` | Manifest, knowledge, learnings; descoberta de fontes raw |
| `git.py` | `commit()` opt-in invocado pelos comandos com `--commit` |
| `book_import*.py` / `web_ingest.py` | Ingestão EPUB/PDF (textual e OCR) e scraping HTML para `raw/` |
| `discovery.py` / `doc_gate.py` / `jobs.py` | Descoberta periódica, gate de docs, catálogo de jobs canônicos |
| `handoff.py` / `graph.py` | Handoff de sessão; travessia de wikilinks para Q&A |
| `outputs.py` / `archive.py` | Escrita em `outputs/` e movimentação para `archive/` |

### `kb/cmds/` — orquestração por comando

`compile`, `qa`, `search`, `lint`. Encapsulam a lógica chamada pelo `cli.py`, mantendo o entry point fino.

### `kb/core/` — execução

| Arquivo | Responsabilidade |
|---------|------------------|
| `runner.py` | Execução padronizada de comandos (timing, exit codes) |
| `tracking.py` | Telemetria local de uso (`track_command`) |

### `kb/analytics/` e `kb/discover/`

Analytics: `gain`, `health`, `history` (métricas sobre o corpus). Discover: `registry`, `rules` (classificação de jobs/sources para descoberta).

---

## Fluxo de Dados

```
kb ingest doc.md|URL
  → copia/scrape → raw/ → state.record_ingest() → [--commit] git.commit()

kb compile
  → discover_compile_targets() em raw/
  → guardrails.assert_safe_for_provider() (opt-in: --allow-sensitive)
  → client.chat(system_prompt + raw)
  → wiki/<topic>/<slug>.md (frontmatter YAML)
  → state.mark_compiled() + upsert_knowledge() + claims.record_compiled_claims()
  → [--commit] git.commit()

kb qa "pergunta"
  → router.decide_route() → wiki | learnings | raw | knowledge
  → router.build_context() (search lexical + graph.traverse de wikilinks)
  → claims.find_relevant_claims() → client.chat(SYSTEM + contexto)
  → terminal (Rich Markdown)
  → [-f] outputs.write_output()  [--to-wiki] arquiva como artigo  [--commit] git.commit()

kb heal --n N
  → amostra N arquivos de wiki/ → corrige wikilinks, remove stubs, atualiza reviewed_at
  → audit.record_event() para mutações relevantes
```

---

## Modelo de Dados Central

```yaml
# Frontmatter YAML do artigo wiki
title: <título em português>
topic: <tópico canônico ou "general">
tags: [tag1, tag2]
source: <nome do arquivo origem em raw/>   # ou "qa" para file-back de Q&A
reviewed_at: <ISO-8601>
```

```jsonc
// kb_state/manifest.json — registro de ingestão e compilação
// status="ingested" após record_ingest; vira "compiled" após mark_compiled
{ "source": "raw/<path>", "kind": "raw|book|web", "status": "ingested" }
{ "source": "raw/<path>", "kind": "raw", "status": "compiled",
  "article": "<path para wiki/<topic>/<slug>.md>",
  "summary": "<path para summary>", "topic": "<topic>", "title": "<título>" }

// kb_state/knowledge.json — sumários estruturados por artigo
{ "source": "wiki/<topic>/<slug>.md", "title": "...", "topic": "...",
  "tags": [...], "summary": "..." }

// kb_state/learnings.json — padrões e correções aprendidas
{ "kind": "...", "content": "...", "source": "system|user", "ts": "..." }

// kb_state/claims.jsonl — afirmações com lifecycle
{ "claim_id": "clm_<uuid>", "statement": "...", "confidence": 0..1,
  "supersedes": ["clm_..."], "source": "wiki/...", "created_at": "...",
  "decayed_at": "..." }

// kb_state/audit.jsonl — trilha append-only de eventos
{ "schema_version": "1.0", "event_id": "evt_<uuid>", "event_type": "...",
  "claim_id": "clm_...", "payload": {...}, "source": "...", "timestamp": "..." }
```

---

## Decisões Arquiteturais Estáveis

| Decisão | Escolha | Motivo | ADR |
|---------|---------|--------|-----|
| Source of truth do código | Engine no repo, corpus em `KB_DATA_DIR` | Separar evolução da engine de dados pessoais | 0001, 0011 |
| Framework CLI | Typer + Rich | Sub-apps tipados, UX rica em terminal | 0002 |
| Versionamento | Git opt-in via `--commit` | Writes locais por padrão; histórico explícito | 0003, 0016 |
| Recuperação | Busca lexical (keyword/TF-IDF) | Suficiente até ~100 artigos / 400K palavras | 0004 |
| Manutenção da wiki | Stochastic heal de N arquivos | Escala para vaults grandes sem custo total | 0005 |
| Routing de Q&A | Heurística por fonte (PAL-inspired) | Selecionar contexto certo por intenção da pergunta | 0006 |
| Conteúdo sensível | Guardrails + `--allow-sensitive` explícito | Falha fechada para chamadas a provider externo | 0007 |
| Contexto de Q&A | Travessia de wikilinks | Enriquece sem custo de embeddings | 0008 |
| File-back de QA | `outputs/` separado de `wiki/` | Não polui a wiki compilada com respostas ad hoc | 0009 |
| Formato LLM | Belt-and-suspenders no parsing | Defesa contra fences e ruído na saída | 0010 |
| Provider/model | Validação par base_url ↔ modelo + fallback | Erros claros e degradação previsível | 0012 |
| Lifecycle de claims | Confiança, supersession, decaimento | Conhecimento envelhece e precisa ser superado | 0013 |
| Versão do release | Fonte única em `kb/__init__.py` | Sem drift entre pacote e tag | 0014 |
| Taxonomia de tópicos | Configurável via `KB_TOPICS` | Adaptável sem alterar código | 0015 |

---

## Restrições

- Nunca editar `wiki/` manualmente — apenas via CLI/LLM (estratégia append/update, jamais rewrite)
- Corpus do usuário e `.obsidian/` ficam fora do repositório principal
- Chamadas ao provider passam por guardrails; conteúdo sensível só prossegue com `--allow-sensitive`
- `--commit` é explícito por comando; `--no-commit` permanece aceito por compatibilidade
- API key apenas em `.env` (`KB_API_KEY`); nunca em código ou em commits
- LLM não escreve a wiki manualmente — toda escrita passa pelo pipeline
- Sem RAG/embeddings até o corpus exigir (>500 artigos)
- OpenCode Go aceita apenas modelos sem prefixo (`kimi-k2.5`, `minimax-2.7`, `glm-5`)
- `repo_mode: solo` — fix proativo de issues encontrados no caminho permitido
