---
title: Explicit commit activation contract
epic: infra
status: done
pr:
---

# Explicit commit activation contract

## Objetivo

Hoje `kb compile` já exige `--commit` explícito, mas `ingest`, `import-book`, `qa --file-back` e `heal` ainda fazem commit por padrão; esta frente unifica o contrato para que todo write local aconteça sem commit automático e o versionamento só ocorra quando o comando for acionado explicitamente.

## Requisitos funcionais

- [ ] RF-01: `ingest`, `import-book`, `compile`, `qa` com file-back e `heal` devem escrever localmente por padrão sem criar commit git.
- [ ] RF-02: todo comando público que pode gerar commit no corpus deve expor ativação explícita de commit no CLI, usando um contrato consistente com `compile`.
- [ ] RF-03: fluxos encadeados devem preservar a escolha explícita de commit, incluindo `ingest --compile`, `import-book --compile`, `qa --file-back --to-wiki` e writes internos de URL ingest/output store.
- [ ] RF-04: help do CLI e documentação pública não devem mais descrever commit automático como comportamento padrão do produto.

## Requisitos técnicos

- RT-01: APIs internas que escrevem no corpus e podem commitar devem operar com `no_commit=True` por padrão, mantendo o commit helper como mecanismo opcional acionado pelo caller.
- RT-02: a mudança deve preservar compatibilidade operacional mínima para usuários já acostumados com `--no-commit`, preferindo convergir os comandos para `--no-commit/--commit` com default local-only.
- RT-03: a mudança deve permanecer offline-testable, cobrindo CLI e helpers sem exigir Git real configurado nem provider externo.
- RT-04: `pre-commit` do repositório fica explicitamente fora do escopo desta frente e só deve ser atacado depois de o contrato do produto estar unificado.

## Mudanças de API/CLI

- CLI:
  - `kb compile` permanece com `--no-commit/--commit`, default sem commit.
  - `kb ingest`, `kb import-book`, `kb qa` e `kb heal` devem migrar para um contrato equivalente, em vez de opt-out implícito.
- API interna:
  - funções como `ingest_url(...)`, `answer_and_file(...)`, `heal(...)`, `compile_file(...)`, `compile_many(...)`, `persist_artifact(...)` e helpers relacionados devem propagar a decisão explícita do caller sem inverter o default para commit.
- Compatibilidade:
  - `--no-commit` continua aceito onde já existe; `--commit` passa a ser o gatilho explícito e documentado.

## Testes

- Unit:
  - atualizar/expandir `tests/unit/test_cli.py` para refletir default sem commit em `ingest`, `qa` e `heal`.
  - atualizar/expandir testes de compile/import/output/web ingest para garantir propagação correta de `no_commit` nos fluxos encadeados.
  - validar helpers de Git/outputs/web ingest sem side effects quando commit não for explicitamente pedido.
- Integration:
  - cobrir `import-book --compile` e `ingest --compile` sem commit explícito.
  - cobrir ao menos um fluxo com `--commit` explícito para provar que o versionamento continua funcional.
- Manual:
  1. `kb ingest arquivo.md`
  2. `kb ingest arquivo.md --commit`
  3. `kb qa "pergunta" -f`
  4. `kb qa "pergunta" -f --commit`

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 3h    |
| Bloqueador | não   |
| Risco      | médio |

## Dependências

- `features/jobs-and-git-operational-contract/SPEC.md`
- `docs/adr/0003-git-versioning-strategy.md`

## ADR

- Necessária? sim
- Se sim, referência: atualizar `docs/adr/0003-git-versioning-strategy.md` ou criar ADR sucessora que formalize commit explícito por comando

## Critérios de aceite

- [ ] Todos os comandos públicos que escrevem no corpus deixam de commitar por padrão.
- [ ] A superfície CLI fica consistente e documentada com `--commit` explícito.
- [ ] Testes relevantes cobrem default local-only e o caminho explícito de commit.

## Evidências esperadas

- Comandos executados:
  - `ruff check kb tests`
  - `python -m pytest tests/unit/test_cli.py tests/unit/test_web_ingest.py tests/unit/test_outputs.py tests/unit/test_book_import.py tests/unit/test_compile.py -q`
  - `python -m pytest tests/integration/test_book_import_cli.py tests/integration/test_outputs_store.py tests/integration/test_sensitive_execution_cli.py -q`
- Arquivos alterados:
  - `kb/cli.py`
  - `kb/web_ingest.py`
  - `kb/outputs.py`
  - `kb/heal.py`
  - `README.md`
  - `CONTRIBUTING.md`

## Notas

Esta frente existe para destravar a adoção de `pre-commit` sem acoplar hooks locais ao runtime do produto. O comportamento de commit automático hoje descrito em `README.md` e no ADR 0003 entra em conflito com a direção desejada do sistema e deve ser tratado como dívida arquitetural explícita.
