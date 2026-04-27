# CLAUDE.md — kb

@AGENTS.md

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

## Sobre o projeto

> Manifesto estruturado do Pi: `.pi/manifest.yaml`

**kb** é uma engine de knowledge base mantida por LLM. A ideia é automática:

- Jogue documentos em `raw/` do seu vault/corpus local
- LLM compila para `wiki/` em markdown estruturado
- Faça perguntas contra a wiki
- Cada resposta pode ser arquivada em `outputs/` (file-back)
- Healing automático (stochastic heal) mantém a wiki fresca mesmo em escala

Baseado em proposta de Andrej Karpathy: "LLMs Turn Raw Research Into a Living Knowledge Base"

## Como começar

Para contexto rápido e estruturado do projeto, paths e comandos principais, consulte também `.pi/manifest.yaml`.

```bash
# 1. Instalar
cd . # na raiz do projeto
pip install -e .
pip install -e .[llm]   # necessário para compile/qa/heal/lint

# 2. Configurar API e diretório de dados
cp .env.example .env
# Editar .env com KB_API_KEY e KB_DATA_DIR

# 3. Adicionar um documento
kb ingest examples/raw/getting-started.md

# 4. Importar um livro em capítulos (opcional)
kb import-book ~/Downloads/livro.epub --compile

# 5. Compilar para wiki
kb compile

# 6. Fazer uma pergunta
kb qa "O que é XSS?"

# 7. Arquivar a resposta em outputs/
kb qa "O que é SQL injection?" -f --no-commit

# 8. Auditoria (health checks)
kb lint

# 9. Healing estocástico (10 arquivos aleatórios)
kb heal --n 10
```

## Modelo de dados

O repositório principal entrega a engine. O conteúdo do usuário deve viver fora daqui, em um diretório apontado por `KB_DATA_DIR`, com a estrutura:

- `raw/` — documentos fonte
- `wiki/` — markdown compilado
- `outputs/` — file-backs de QA
- `kb_state/` — manifesto, knowledge, learnings

## Stack técnico

- Python 3.11+, Typer, Rich
- OpenAI SDK opcional para recursos LLM
- OpenCode Go API (OpenAI-compatible)
- Git automático em todo write
- Busca lexical simples em Markdown
- Markdown + YAML frontmatter

## Configuração de ambiente

```
KB_API_KEY=<sua-api-key>
KB_BASE_URL=https://opencode.ai/zen/go/v1
KB_MODEL=kimi-k2.5
KB_DATA_DIR=<caminho-para-seu-llm-wiki>
```

Validação explícita: quando `KB_BASE_URL` aponta para OpenCode Go, o projeto aceita apenas nomes de modelo compatíveis e sem prefixo (ex.: `kimi-k2.5`, `minimax-2.7`, `glm-5`). Exemplo inválido: `opencode-go/kimi-k2.5`.

Para modelos locais (Ollama):

```
KB_BASE_URL=http://localhost:11434/v1
KB_API_KEY=ollama
KB_MODEL=qwen2.5-coder:7b
```

## Modo colaborativo vs. solo

`repo_mode: solo` — um contribuidor, fix proativo de issues encontrados.

## Pontos-chave

1. **Separação engine vs. corpus** — código no repositório principal; dados do usuário em `KB_DATA_DIR`
2. **Importação de livros integrada** — `kb import-book` quebra EPUB/PDF textual em capítulos markdown dentro de `raw/books/` e pode compilar tudo com `--compile`
3. **Stochastic heal** — `kb heal` processa N arquivos aleatórios, corrige links, deleta stubs
4. **Git automático** — writes no corpus local podem gerar commit (estratégia Pawel Huryn: append/update, nunca rewrite)
5. **Sem RAG sofisticado** — TF-IDF simples + busca de palavra-chave funciona bem até ~100 artigos/400K palavras
6. **Obsidian oficial** — o frontend recomendado é o Obsidian apontando para `<KB_DATA_DIR>/wiki`

## Contexto técnico atual

**Feature ativa:** 010-multi-vault-foundation
**Stack:** Python 3.11+, Typer, Rich
**Build:** `pip install -e .`
**Testes:** `python -m pytest`
**Alterações recentes:**

- 010-multi-vault-foundation: fundação para múltiplos vaults sob `KB_DATA_DIR`
- (mergeado) llm-wiki-v2-foundation: fundação da wiki v2 (PR #35)
- (mergeado) ingest-url: ingestão a partir de URL (PR #32)
- 006-kb-archive: comando `kb archive` para mover artigos stale/órfãos de wiki/ → archive/
- (backlog) 008-kb-stats, 009-kb-diff

## Layout de docs

- `docs/architecture/` — apenas SDD.md, TDD.md, SPEC_FORMAT.md (artefatos arquiteturais vivos); `_archived/` guarda predecessores
- `docs/adr/` — ADRs duráveis
- `docs/reports/` — relatórios datados (cobertura, débito, auditoria, conformidade)
- `docs/research/` — blueprints, sínteses e pesquisa exploratória
- `docs/policies/` — DATA_POLICY, ARTIFACT_POLICY, SENSITIVE_CONTENT_POLICY
- `docs/council/` — debates multi-agente sobre decisões abertas
- `docs/handoffs/` — handoffs operacionais gerados por `kb handoff create`
- `docs/templates/`, `docs/facts/`, `docs/API.md`, `docs/OBSIDIAN.md`, `docs/DEPLOYMENT.md` — referência operacional

## Próximos passos

- Instalar dependências (`pip install -e .[dev]` para ambiente de desenvolvimento)
- Configurar API
- Testar fluxo básico (ingest → compile → qa → file-back)
- Validar Obsidian sobre `<KB_DATA_DIR>/wiki`
- (Futuro) Integração Obsidian native
- (Futuro) Embeddings + RAG if wiki > 500 artigos
- (Futuro) Finetuning no corpus da wiki
