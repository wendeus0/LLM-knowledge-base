# AGENTS.md — kb

@~/.claude/AGENTS.md

## Domínio do projeto

> Manifesto estruturado do Pi: `.pi/manifest.yaml`


**Produto:** Sistema de knowledge base pessoal mantido por LLM. Coleta documentos brutos, compila para wiki em markdown, responde perguntas contra a wiki, faz health checks e healing automático. Baseado na proposta de Andrej Karpathy.

**Stack:**
- Linguagem: Python 3.11+
- Framework: Typer (CLI), Rich (terminal UI)
- Cliente LLM: OpenAI SDK (compatível com OpenCode Go)
- Armazenamento: JSON (strategies.json), Markdown (wiki/)
- Busca: contagem simples de palavras-chave em Markdown
- Versionamento: Git (todo write é commit automático)

## Comandos do projeto

```bash
# Instalar dependências base
pip install -e .

# Instalar features LLM (compile/qa/heal/lint)
pip install -e .[llm]

# Rodar testes
python -m pytest

# Lint
ruff check kb

# Build
pip install -e .

# Dev/CLI
kb ingest <arquivo>      # Adicionar documento a raw/
kb import-book <arquivo> # Importar EPUB/PDF textual para raw/books/
kb compile               # Compilar raw/ (recursivo, incluindo raw/books/) → wiki/ + summaries + knowledge
kb compile --no-commit   # Compilar sem commit git automático
kb compile --allow-sensitive # Autorizar processamento sensível explicitamente
kb qa "pergunta"         # Perguntar com routing por fonte nativa
kb qa "pergunta" -f      # Perguntar e arquivar resposta (file-back)
kb qa "pergunta" -f --no-commit # File-back sem commit automático
kb search "termo"        # Buscar na wiki
kb heal --n 10          # Stochastic heal: N arquivos aleatórios
kb heal --allow-sensitive --no-commit # Healing sensível/experimental
kb lint                 # Health checks (audit)
kb jobs list            # Listar jobs agendáveis
kb jobs run <job>       # Executar job canônico
```

## Convenções de código

- Módulos em `kb/` por função: `client.py` (LLM), `compile.py` (raw→wiki), `router.py` (routing por fonte), `state.py` (knowledge/learnings/manifest), `guardrails.py` (conteúdo sensível), `jobs.py` (jobs canônicos), `book_import.py`/`book_import_core.py` (importação de livros), `qa.py` (Q&A), `search.py`, `heal.py`, `lint.py`, `config.py`, `git.py`
- Nomes: snake_case para funções/variáveis, PascalCase para classes
- Sem type hints explícitos a menos que seja crítico (config, cliente)
- Docstrings em português para funções públicas

## Convenções de teste

- Framework: pytest
- Localização: `tests/`
- Teste de integração > teste unitário (sistema integrado)
- Fixtures: raw/ e wiki/ de teste

## Regras específicas do domínio

- Todo write na wiki (compile, heal, qa --file-back) faz commit git automático
- Chamadas ao provider externo passam por guardrails de conteúdo sensível e podem exigir confirmação
- `--allow-sensitive` faz opt-in explícito para processar conteúdo sinalizado
- `--no-commit` preserva writes locais, mas suprime o commit automático do fluxo atual
- Conflitos git são raros porque o LLM apenas append/atualiza seções, nunca reescreve (estratégia Pawel Huryn)
- Stochastic heal processa N arquivos aleatórios por execução (scale para vaults grandes)
- O LLM nunca escreve a wiki manualmente — tudo é automatizado
- Compilação adiciona frontmatter YAML: title, topic, tags, source, reviewed_at

## Arquitetura

```
kb/
├── raw/              ← documentos fonte (não processados)
│   └── books/        ← livros importados em capítulos markdown + metadata.json
├── wiki/             ← markdown compilado, versionado
│   ├── _index.md     ← índice atualizado automaticamente
│   ├── cybersecurity/
│   ├── ai/
│   ├── python/
│   └── typescript/
├── kb/               ← pacote Python
│   ├── client.py     ← wrapper OpenAI SDK
│   ├── compile.py    ← raw/ → wiki/ (LLM + summary compilado)
│   ├── qa.py         ← Q&A + file-back
│   ├── router.py     ← roteamento entre wiki/raw/knowledge/learnings
│   ├── state.py      ← manifesto + stores knowledge/learnings
│   ├── guardrails.py ← política de sensibilidade em runtime
│   ├── jobs.py       ← catálogo de jobs canônicos
│   ├── search.py     ← contagem simples de palavras-chave
│   ├── heal.py       ← stochastic heal
│   ├── lint.py       ← health checks (LLM)
│   ├── git.py        ← commit automático
│   ├── config.py     ← constantes, paths, env
│   └── cli.py        ← Typer CLI
└── pyproject.toml
```

## Palavras-chave do domínio

| Termo | Significado |
|-------|-------------|
| raw/ | Documentos fonte antes de compilação |
| wiki | Coleção de .md compilados e versionados |
| compile | LLM processa raw/ e escreve wiki/ |
| Q&A | Query contra a wiki com contexto |
| file-back | Arquivar resposta de volta na wiki |
| heal | Correção estocástica: links, stubs, reviewed_at |
| topic | Classificação (cybersecurity, ai, python, typescript) |
| frontmatter | YAML no início de cada .md (title, topic, tags) |

## Restrições específicas

- Nunca editar wiki manualmente — apenas via CLI/LLM
- API key só em .env (nunca em código)
- Git commits automáticos → sem staging manual de wiki/
- Compile, heal, qa sempre comitam se houver mudanças

## Fluxo de sessão

Para visão rápida e estruturada de comandos, paths e convenções estáveis, consulte também `.pi/manifest.yaml`.


1. `session-open` (context-health, triage)
2. Trabalho (ingest, compile, qa, heal, lint)
3. `session-close` (logs, memoria)

## Próximos passos

- [ ] Instalar base: `pip install -e .`
- [ ] Instalar LLM opcional: `pip install -e .[llm]`
- [ ] Configurar `.env` com KB_API_KEY
- [ ] Testar: `kb ingest docs/test.md && kb compile`
- [ ] Testar: `kb import-book livro.epub --compile`
- [ ] Integrar Obsidian como frontend
- [ ] Expandir cobertura de testes em `tests/`
