# PLAN — Explicit commit activation contract

## Objetivo técnico

Alinhar toda a superfície de escrita do produto ao mesmo modelo já adotado por `compile`: escrever localmente por padrão e só versionar quando `--commit` for fornecido pelo caller.

## Estratégia

1. Identificar todos os comandos públicos e helpers internos que hoje assumem commit por padrão.
2. Ajustar a CLI para um contrato uniforme `--no-commit/--commit`, com default local-only.
3. Propagar o default sem commit pelos helpers internos de ingest, outputs, heal e fluxos encadeados de compile/import.
4. Atualizar documentação e ADR para remover a narrativa de auto-commit por padrão.
5. Validar com testes unitários/integration focados e lint.

## Superfície principal

- `kb/cli.py`
- `kb/web_ingest.py`
- `kb/outputs.py`
- `kb/heal.py`
- `kb/book_import.py` e fluxos de compile-after
- `README.md`, `README.en.md`, `CONTRIBUTING.md`, `docs/API.md`
- `docs/adr/0003-git-versioning-strategy.md` ou ADR sucessora

## Decisões de implementação

- Preferir compatibilidade explícita a breaking change abrupta: manter `--no-commit` aceito e introduzir `--commit` como caminho documentado.
- Não adicionar configuração global/env para política de commit nesta fase.
- Não introduzir `pre-commit` ainda; essa frente é pré-requisito conceitual para ela.

## Riscos

- Regressão em testes existentes que assumem auto-commit como default.
- Divergência entre fluxo serial e paralelo de `compile`/`import-book` na propagação do flag.
- Documentação espalhada ainda afirmar auto-commit como regra.

## Saída esperada

- SPEC aprovada para implementação.
- Lista objetiva de arquivos/testes a alterar.
- Decisão registrada sobre ADR necessária para substituir o contrato anterior.
