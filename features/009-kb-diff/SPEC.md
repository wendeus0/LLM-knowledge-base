---
title: kb diff — Diff visual da wiki via git
epic: infra
status: draft
pr:
---

# kb diff — Diff visual da wiki via git

## Objetivo

Permitir comparar o estado da wiki antes/depois de operações como `compile` ou `heal`, usando `git diff` internamente com formatação Rich para highlight de mudanças.

## Requisitos funcionais

- [ ] RF-01: `kb diff` deve mostrar diff da wiki em relação ao último commit
- [ ] RF-02: `kb diff --stat` deve mostrar resumo estatístico (arquivos alterados, inserções, remoções)
- [ ] RF-03: `kb diff --since <ref>` deve comparar contra ref arbitrária (commit, tag, branch)
- [ ] RF-04: saída formatada com Rich (syntax highlighting para diff de markdown)
- [ ] RF-05: deve funcionar apenas quando `KB_DATA_DIR` é um repositório git

## Requisitos técnicos

- RT-01: usar `subprocess.run(["git", "diff", ...])` dentro de `KB_DATA_DIR`
- RT-02: reutilizar `kb/git.py` para verificação de estado git
- RT-03: zero dependências novas

## Mudanças de API/CLI

Novo comando `kb diff [--stat] [--since <ref>]`. Sem breaking changes.

## Testes

- Unit: parsing de saída git diff, formatação Rich, fallback sem git
- Integration: diff com repo git de teste e commits reais

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | ~2h |
| Bloqueador | não |
| Risco | baixo |

## Dependências

- `kb/git.py` (já existe)
- `KB_DATA_DIR` com git inicializado

## ADR

- Necessária? não

## Critérios de aceite

- [ ] `kb diff` mostra diff do último commit em wiki/
- [ ] `kb diff --stat` mostra resumo de alterações
- [ ] `kb diff --since HEAD~3` compara contra ref arbitrária
- [ ] Mensagem clara quando `KB_DATA_DIR` não é repo git

## Evidências esperadas

- Comandos executados:
  - `python -m pytest tests/unit/test_diff.py`
  - `ruff check kb`
- Arquivos alterados:
  - `kb/cli.py` (novo comando)
  - `kb/diff.py` (novo módulo)
  - `tests/unit/test_diff.py` (novos testes)

## Notas

Funcionalidade simples — wrap de `git diff` com formatação. Requer que o usuário tenha `--commit` habilitado no fluxo (sem commits, sem diff).
