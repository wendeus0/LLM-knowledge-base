# AGENTS.md — kb

@~/.claude/AGENTS.md

## Read first

Antes de alterações não triviais, leia estes documentos nesta ordem:

1. `CONTEXT.md`
2. `docs/architecture/SDD.md`
3. `docs/architecture/TDD.md`
4. `docs/architecture/SPEC_FORMAT.md`
5. `features/<feature>/SPEC.md` (quando a tarefa for de feature)

Se houver conflito:

- `features/<feature>/SPEC.md` governa o comportamento da feature
- `docs/architecture/SDD.md` governa arquitetura e evolução
- `docs/architecture/TDD.md` governa estratégia de testes
- `docs/architecture/SPEC_FORMAT.md` governa formato da SPEC
- `CONTEXT.md` governa contexto macro e limites do produto

## Domínio do projeto

> Manifesto estruturado do Pi: `.pi/manifest.yaml`


**Produto:** Engine de knowledge base mantida por LLM. Coleta documentos brutos, compila para wiki em markdown, responde perguntas contra a wiki, faz health checks e healing automático. Baseado na proposta de Andrej Karpathy.

**Stack:**
- Linguagem: Python 3.11+
- Framework: Typer (CLI), Rich (terminal UI)
- Cliente LLM: OpenAI SDK (compatível com OpenCode Go)
- Armazenamento: JSON (`kb_state/`), Markdown (`wiki/`) dentro do `KB_DATA_DIR` do usuário
- Busca: contagem simples de palavras-chave em Markdown
- Versionamento: Git (writes podem gerar commit automático, com opt-out via `--no-commit`)

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
kb ingest <arquivo>      # Adicionar documento a raw/ do vault do usuário
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

- O corpus do usuário deve viver fora do repositório principal, preferencialmente via `KB_DATA_DIR`
- Writes em wiki/outputs/ podem fazer commit automático dependendo do comando e de `--no-commit`
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
├── kb/               ← pacote Python / engine
├── docs/             ← documentação
├── tests/            ← testes
├── examples/         ← exemplos neutros
└── <KB_DATA_DIR>/    ← corpus/vault do usuário (fora do repositório principal)
   ├── raw/           ← documentos fonte + books/
   ├── wiki/          ← markdown compilado
   ├── outputs/       ← file-backs de QA
   └── kb_state/      ← manifesto + stores knowledge/learnings
```

## Palavras-chave do domínio

| Termo | Significado |
|-------|-------------|
| raw/ | Documentos fonte antes de compilação |
| wiki | Coleção de .md compilados e versionados |
| compile | LLM processa raw/ e escreve wiki/ |
| Q&A | Query contra a wiki com contexto |
| file-back | Arquivar resposta em `outputs/` por padrão |
| heal | Correção estocástica: links, stubs, reviewed_at |
| topic | Classificação gerada/derivada do corpus |
| frontmatter | YAML no início de cada .md (title, topic, tags) |

## Restrições específicas

- Nunca editar wiki manualmente — apenas via CLI/LLM
- API key só em .env (nunca em código)
- Não versionar `.obsidian/` e corpus pessoal no repositório principal
- Preferir `qa -f --no-commit` no fluxo via Obsidian

## Fluxo de sessão

Para visão rápida e estruturada de comandos, paths e convenções estáveis, consulte também `.pi/manifest.yaml`.


1. `session-open` (context-health, triage)
2. Trabalho (ingest, compile, qa, heal, lint)
3. `session-close` (logs, memoria)

## Próximos passos

- [ ] Instalar base: `pip install -e .`
- [ ] Instalar LLM opcional: `pip install -e .[llm]`
- [ ] Configurar `.env` com `KB_API_KEY` e `KB_DATA_DIR`
- [ ] Testar: `kb ingest examples/raw/getting-started.md && kb compile`
- [ ] Testar: `kb import-book livro.epub --compile`
- [ ] Validar Obsidian em `<KB_DATA_DIR>/wiki`
- [ ] Expandir cobertura de testes em `tests/`
