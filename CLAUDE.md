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
cd /home/g0dsssp33d/work/kb
pip install -e .

# 2. Configurar API
cp .env.example .env
# Editar .env com KB_API_KEY

# 3. Adicionar um documento
kb ingest ~/Downloads/artigo.md

# 4. Compilar para wiki
kb compile

# 5. Fazer uma pergunta
kb qa "O que é XSS?"

# 6. Arquivar a resposta de volta
kb qa "O que é SQL injection?" -f

# 7. Auditoria (health checks)
kb lint

# 8. Healing estocástico (10 arquivos aleatórios)
kb heal --n 10
```

## Tópicos de pesquisa (wiki/)

- **cybersecurity** — vulnerabilidades, técnicas, defesas
- **ai** — machine learning, LLMs, agentes
- **python** — padrões, libs, performance
- **typescript** — type system, frameworks, patterns

## Stack técnico

- Python 3.11+, Typer, Rich, OpenAI SDK
- OpenCode Go API (OpenAI-compatible)
- Git automático em todo write
- Busca lexical simples em Markdown
- Markdown + YAML frontmatter

## Configuração de ambiente

```
KB_API_KEY=<sua-api-key>
KB_BASE_URL=https://opencode.ai/zen/go/v1
KB_MODEL=opencode-go/kimi-k2.5
```

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
2. **Stochastic heal** — `kb heal` processa N arquivos aleatórios, corrige links, deleta stubs
3. **Git automático** — todo write é commit (estratégia Pawel Huryn: append/update, nunca rewrite)
4. **Sem RAG sofisticado** — TF-IDF simples + busca de palavra-chave funciona bem até ~100 artigos/400K palavras
5. **Obsidian-ready** — wiki/ é um vault pronto para Obsidian (wikilinks, markdown)

## Próximos passos

- Instalar dependências (`pip install -e .[dev]` para ambiente de desenvolvimento)
- Configurar API
- Testar fluxo básico (ingest → compile → qa → file-back)
- (Futuro) Integração Obsidian native
- (Futuro) Embeddings + RAG if wiki > 500 artigos
- (Futuro) Finetuning no corpus da wiki
