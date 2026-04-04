# CLAUDE.md — kb

@AGENTS.md

## Sobre o projeto

> Manifesto estruturado do Pi: `.pi/manifest.yaml`


**kb** é um sistema de knowledge base pessoal mantido por LLM. A ideia é automática:
- Jogue documentos em `raw/`
- LLM compila para wiki em markdown estruturado
- Faça perguntas contra a wiki
- Cada resposta enriquece a wiki (file-back)
- Healing automático (stochastic heal) mantém a wiki fresca mesmo em escala

Baseado em proposta de Andrej Karpathy: "LLMs Turn Raw Research Into a Living Knowledge Base"

## Como começar

Para contexto rápido e estruturado do projeto, paths e comandos principais, consulte também `.pi/manifest.yaml`.


```bash
# 1. Instalar
cd . # na raiz do projeto
pip install -e .
pip install -e .[llm]   # necessário para compile/qa/heal/lint

# 2. Configurar API
cp .env.example .env
# Editar .env com KB_API_KEY

# 3. Adicionar um documento
kb ingest ~/Downloads/artigo.md

# 4. Importar um livro em capítulos (opcional)
kb import-book ~/Downloads/livro.epub --compile

# 5. Compilar para wiki
kb compile

# 6. Fazer uma pergunta
kb qa "O que é XSS?"

# 7. Arquivar a resposta de volta
kb qa "O que é SQL injection?" -f

# 8. Auditoria (health checks)
kb lint

# 9. Healing estocástico (10 arquivos aleatórios)
kb heal --n 10
```

## Tópicos de pesquisa (wiki/)

- **cybersecurity** — vulnerabilidades, técnicas, defesas
- **ai** — machine learning, LLMs, agentes
- **python** — padrões, libs, performance
- **typescript** — type system, frameworks, patterns

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

1. **Loop de composição** — cada `qa` com `--file-back` adiciona à wiki
2. **Importação de livros integrada** — `kb import-book` quebra EPUB/PDF textual em capítulos markdown dentro de `raw/books/` e pode compilar tudo com `--compile`
3. **Stochastic heal** — `kb heal` processa N arquivos aleatórios, corrige links, deleta stubs
4. **Git automático** — todo write é commit (estratégia Pawel Huryn: append/update, nunca rewrite)
5. **Sem RAG sofisticado** — TF-IDF simples + busca de palavra-chave funciona bem até ~100 artigos/400K palavras
6. **Obsidian-ready** — wiki/ é um vault pronto para Obsidian (wikilinks, markdown)

## Próximos passos

- Instalar dependências (`pip install -e .[dev]` para ambiente de desenvolvimento)
- Configurar API
- Testar fluxo básico (ingest → compile → qa → file-back)
- (Futuro) Integração Obsidian native
- (Futuro) Embeddings + RAG if wiki > 500 artigos
- (Futuro) Finetuning no corpus da wiki
