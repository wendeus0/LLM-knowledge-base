---
title: outputs/ — Store separado para respostas de QA
epic: qa
status: draft
pr:
---

# outputs/ — Store Separado para Respostas de QA

## Objetivo

Hoje `kb qa -f` arquiva respostas geradas de volta em `wiki/`, misturando conhecimento compilado com derivados de sessão. O sistema deve separar os dois: `wiki/` contém apenas conhecimento curado pelo LLM a partir de fontes; `outputs/` acumula respostas, relatórios e análises geradas por QA.

## Requisitos funcionais

- [ ] `outputs/` é criado automaticamente na raiz do projeto se não existir
- [ ] `kb qa -f` (file-back) grava a resposta em `outputs/` por padrão, não em `wiki/`
- [ ] `kb qa -f --to-wiki` mantém o comportamento anterior: arquiva diretamente em `wiki/`
- [ ] Arquivo gerado em `outputs/` segue naming: `outputs/<topic>/<YYYY-MM-DD>-<slug>.md`
- [ ] Arquivo gerado tem frontmatter mínimo: `title`, `source_question`, `date`, `topic`
- [ ] Git commit automático após write em `outputs/` (mesmo comportamento de `wiki/`)
- [ ] `kb qa -f --no-commit` suprime o commit (consistente com demais comandos)
- [ ] `outputs/` é incluído em `.gitignore` por padrão? **Não** — outputs são artefatos valiosos e versionados, assim como a wiki.

## Requisitos técnicos

- Criar `kb/outputs.py` com função `write_output(question, answer, topic)` responsável por naming, frontmatter e write
- `qa.py`: alterar fluxo de `file_back=True` para chamar `outputs.write_output()` por padrão; `to_wiki=True` mantém caminho atual
- `config.py`: adicionar `OUTPUTS_DIR = ROOT / "outputs"` (análogo a `WIKI_DIR`)
- `git.py`: nenhuma mudança necessária — `commit_file()` já aceita qualquer path
- Naming do arquivo: `slugify(question[:60])` + data ISO

## Mudanças de API

```bash
# Comportamento atual (deprecado como padrão):
kb qa "O que é XSS?" -f           # → wiki/cybersecurity/xss.md

# Novo padrão:
kb qa "O que é XSS?" -f           # → outputs/cybersecurity/2026-04-06-o-que-e-xss.md

# Para forçar na wiki (casos explícitos):
kb qa "O que é XSS?" -f --to-wiki # → wiki/cybersecurity/xss.md (comportamento anterior)
```

## Testes

- **Unit:** `test_outputs.py` — `write_output()` gera path correto, frontmatter válido, slug sanitizado
- **Integration:** `kb qa "pergunta" -f` cria arquivo em `outputs/`, não em `wiki/`; `--to-wiki` cria em `wiki/`
- **Manual:** confirmar que `outputs/` aparece no `git log` após file-back

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 2h |
| Bloqueador | não |
| Risk | baixa |

## Dependências

- Nenhuma — feature autossuficiente

## Notas

- A separação `wiki/` vs `outputs/` reflete o princípio de Karpathy: wiki é o cérebro, outputs são os pensamentos gerados numa sessão
- `--to-wiki` existe para casos onde o usuário quer deliberadamente enriquecer a wiki com uma resposta sintetizada
- Outputs antigos em `wiki/` (gerados pelo comportamento atual) não precisam ser migrados — são válidos como conteúdo de wiki
