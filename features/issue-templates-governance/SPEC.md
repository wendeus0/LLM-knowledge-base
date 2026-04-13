---
title: Issue templates governance
epic: infra
status: approved
pr:
---

# Issue templates governance

## Objetivo

Hoje o repositório exige governança forte em PR e contribuição, mas ainda recebe issues sem estrutura; esta frente adiciona intake padronizado para bugs, features e tarefas operacionais, alinhado a SDD/TDD e à política de segurança.

## Requisitos funcionais

- [ ] RF-01: a abertura de bug deve coletar comportamento atual, comportamento esperado, passos de reprodução e evidências mínimas
- [ ] RF-02: a abertura de feature deve coletar problema, resultado desejado, critérios iniciais de aceitação e impacto previsto em CLI/API/docs
- [ ] RF-03: a abertura de tarefa operacional deve separar manutenção/governança de feature de produto
- [ ] RF-04: a página de abertura de issue deve desabilitar issues em branco e direcionar vulnerabilidades para o fluxo privado de `SECURITY.md`

## Requisitos técnicos

- RT-01: usar GitHub Issue Forms em `.github/ISSUE_TEMPLATE/*.yml`
- RT-02: alinhar a linguagem e os campos com `CONTRIBUTING.md`, `SECURITY.md` e `.github/pull_request_template.md`
- RT-03: evitar mudanças em workflow de CI ou superfície CLI

## Mudanças de API/CLI

Nenhuma. A mudança afeta apenas a interface de criação de issues no GitHub.

## Testes

- Manual:
  1. revisar os formulários YAML criados em `.github/ISSUE_TEMPLATE/`
  2. validar sintaxe local dos YAMLs
  3. conferir que `CONTRIBUTING.md` referencia os templates corretos e o fluxo de segurança

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 2h    |
| Bloqueador | não   |
| Risco      | baixo |

## Dependências

- `.github/pull_request_template.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

## ADR

- Necessária? não
- Se sim, referência: não aplicável

## Critérios de aceite

- [ ] abertura de bug deixa de ser texto livre sem dados mínimos de reprodução
- [ ] abertura de feature passa a capturar insumos suficientes para iniciar SPEC
- [ ] manutenção operacional deixa de competir com feature request no mesmo template
- [ ] vulnerabilidades deixam de disputar o fluxo de issues públicas

## Evidências esperadas

- Comandos executados:
  - `python -c "import yaml, pathlib; [yaml.safe_load(path.read_text(encoding='utf-8')) for path in pathlib.Path('.github/ISSUE_TEMPLATE').glob('*.yml')]"`
- Arquivos alterados:
  - `.github/ISSUE_TEMPLATE/config.yml`
  - `.github/ISSUE_TEMPLATE/bug_report.yml`
  - `.github/ISSUE_TEMPLATE/feature_request.yml`
  - `.github/ISSUE_TEMPLATE/operational_task.yml`
  - `CONTRIBUTING.md`

## Notas

Não inclui Discussions, automação de labels nem integração com Projects.
