---
title: Infra alignment phase 1
epic: infra
status: approved
pr:
---

# Infra alignment phase 1

## Objetivo

Hoje o repositório tem drift entre versão empacotada e releases documentados, mantém a taxonomia de tópicos fixa no código e concentra OCR/PDF dentro de `kb/book_import_core.py`; esta fase alinha o contrato de release, externaliza a taxonomia para configuração runtime e reduz o acoplamento do importador sem quebrar o contrato público.

## Requisitos funcionais

- [ ] RF-01: a versão empacotada deve ter uma única fonte de verdade no pacote Python e o release mais recente em `CHANGELOG.md` deve permanecer alinhado com ela
- [ ] RF-02: os tópicos suportados devem poder ser configurados por `KB_TOPICS`, preservando a lista atual como default e `general` como fallback implícito
- [ ] RF-03: `compile` e `qa --file-back` devem usar a taxonomia configurada tanto para prompts quanto para resolução do diretório de saída
- [ ] RF-04: o pipeline de PDF/OCR deve sair de `kb/book_import_core.py` para módulo dedicado, mantendo mensagens de erro estáveis e imports públicos existentes

## Requisitos técnicos

- RT-01: usar versionamento dinâmico do Hatch apontando para `kb/__init__.py`
- RT-02: manter compatibilidade de imports existentes em `kb.book_import_core`
- RT-03: evitar breaking change em CLI ou formato de artefatos
- RT-04: manter testes offline com mocks para LLM, PyMuPDF e OCR

## Mudanças de API/CLI

- Configuração pública nova: `KB_TOPICS=topic-a,topic-b,topic-c`
- `general` permanece implícito e não deve ser listado em `KB_TOPICS`
- Sem novos comandos CLI

## Testes

- Unit:
  - contrato de versão entre `pyproject.toml`, `kb.__version__` e `CHANGELOG.md`
  - parsing de `KB_TOPICS` com normalização, deduplicação e fallback
  - regressão do pipeline de `book_import`/PDF mantendo mensagens estáveis
- Manual:
  1. `KB_TOPICS=ml,security kb compile --no-commit`
  2. `KB_TOPICS=ml,security kb qa "..." -f --no-commit`

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 1 dia |
| Bloqueador | não   |
| Risco      | médio |

## Dependências

- `README.md` e `README.en.md` atualizados na sessão anterior

## ADR

- Necessária? sim
- Referências: `docs/adr/0014-release-version-source-of-truth.md`, `docs/adr/0015-runtime-topic-taxonomy.md`

## Critérios de aceite

- [ ] contrato de versão deixa de depender de sincronização manual entre pacote e changelog sem teste
- [ ] taxonomia deixa de estar fixa em `kb/config.py` sem ponto de configuração operacional
- [ ] `kb/book_import_core.py` perde a responsabilidade direta pelo pipeline PDF/OCR

## Evidências esperadas

- `python -m pytest tests/unit/test_config.py tests/unit/test_version_contract.py tests/unit/test_book_import.py tests/unit/test_book_import_core.py tests/unit/test_compile.py tests/unit/test_qa.py -q`
- `ruff check kb tests`

## Notas

Não inclui hook `pre-commit`, templates de issue nem refactor amplo do pipeline EPUB; isso fica para fases seguintes.
