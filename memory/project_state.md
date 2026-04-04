---
name: Project State
description: Estado atual, sprint, branch ativo, marcos
type: project
---

## Estrutura

Criada: 2026-04-03

```
kb/
├── raw/              ← documentos fonte
├── wiki/             ← markdown compilado
│   ├── _index.md
│   ├── cybersecurity/, ai/, python/, typescript/
├── kb/               ← pacote Python
│   ├── client.py, compile.py, qa.py, search.py, heal.py, lint.py, git.py, cli.py, config.py
├── pyproject.toml
├── .env.example
├── CLAUDE.md, AGENTS.md, ERROR_LOG.md, PENDING_LOG.md
├── memory/           ← memória distribuída
└── .git/             ← versionado
```

## Status

**Iniciativa:** Fase 1 — estrutura base
- ✓ Arquivos Python criados (client, compile, qa, search, heal, lint, git, cli)
- ✓ Comandos CLI funcionando (kb ingest, compile, qa, search, heal, lint)
- ✓ Git automático em todo write
- ✓ Stochastic heal implementado
- ✓ File-back (qa --file-back) implementado
- ⚠ Pendente: .env configurado com chave de API
- ⚠ Pendente: Testes (tests/)

## Branch ativo

`main` — projeto solo, sem branches de feature

## Sprint

N/A — projeto novo

## Marcos (Milestones)

1. **Setup completo** (em progresso)
   - [ ] Instalar `pip install -e .`
   - [ ] Configurar .env
   - [ ] Teste end-to-end: ingest → compile → qa → heal

2. **Testes** (futuro)
   - [ ] Unit tests (compile, qa, search)
   - [ ] Integration tests (raw → wiki → qa)
   - [ ] 70%+ coverage

3. **Obsidian** (futuro)
   - [ ] Integração nativa (plugin ou CLI hook)
   - [ ] Visualização de wiki/ em tempo real

## Tópicos de pesquisa (wiki/)

Inicialmente vazios. Planejados:
- cybersecurity
- ai
- python
- typescript

## Tecnologias

- **Language:** Python 3.11+
- **CLI:** Typer
- **UI:** Rich
- **LLM:** OpenAI SDK (OpenCode Go)
- **Search:** TF-IDF (scikit-learn)
- **Storage:** JSON (config), Markdown (wiki), Git
