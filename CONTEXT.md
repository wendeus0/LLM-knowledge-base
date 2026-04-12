# CONTEXT.md

Contexto operacional e de produto do LLM-knowledge-base.

## Identidade do projeto

O repositório `LLM-knowledge-base` entrega a engine `kb`, responsável por manter uma base de conhecimento viva a partir de documentos brutos.

Ciclo central:

1. Ingestão de fontes em `raw/`
2. Compilação assistida por LLM para `wiki/`
3. Consulta (`qa`) e busca (`search`) sobre a wiki
4. Healing (`heal`) e auditoria (`lint`) para manter qualidade

## Princípios norteadores

- Spec Driven Development (SDD): nenhuma mudança não trivial entra sem SPEC.
- Test Driven Development (TDD): comportamento novo/alterado nasce com testes RED antes do código GREEN.
- Rastreabilidade documental: decisões e mudanças precisam de trilha verificável.
- Separação engine × corpus: código no repositório; dados do usuário em `KB_DATA_DIR`.
- Segurança e controle: guardrails para conteúdo sensível e controle explícito de commit (`--no-commit`).

## Fonte de verdade para execução

Antes de alterações não triviais, ler nesta ordem:

1. `CONTEXT.md`
2. `docs/architecture/SDD.md`
3. `docs/architecture/TDD.md`
4. `docs/architecture/SPEC_FORMAT.md`
5. `features/<feature>/SPEC.md` (quando houver feature em foco)

Regra de precedência em caso de conflito:

- `features/<feature>/SPEC.md` governa comportamento da feature
- `docs/architecture/SDD.md` governa arquitetura e desenho de evolução
- `docs/architecture/TDD.md` governa estratégia de testes
- `docs/architecture/SPEC_FORMAT.md` governa formato e completude das SPECs
- `CONTEXT.md` governa contexto macro do produto e limites de escopo

## Fluxo padrão de trabalho

SPEC -> TEST_RED -> CODE_GREEN -> REFACTOR -> VALIDATE -> REPORT

Definições:

- SPEC: definir escopo, critérios e evidências esperadas.
- TEST_RED: escrever/ajustar testes que falham para representar o requisito.
- CODE_GREEN: implementar mínimo para passar os testes.
- REFACTOR: melhorar design sem alterar comportamento.
- VALIDATE: rodar suíte adequada (unit/integration/lint).
- REPORT: registrar o que mudou, evidências e riscos residuais.

## Artefatos de rastreabilidade

- `features/<feature>/SPEC.md`: contrato da feature.
- `features/<feature>/NOTES.md` (opcional): lacunas e decisões locais.
- `docs/adr/*.md`: decisões arquiteturais relevantes e duráveis.
- `REPORT.md` / relatórios específicos: evidências de execução.

## Critérios mínimos para aceitar mudança

- SPEC existente e atualizada para o escopo.
- Testes cobrindo requisitos funcionais e cenários críticos.
- Evidências de validação anexáveis (comandos/saídas/arquivos alterados).
- Sem quebra da separação engine/corpus.

## Fora de escopo por padrão

- Alterações manuais em `wiki/` fora do fluxo da engine.
- Mudanças arquiteturais sem ADR quando houver impacto de longo prazo.
- Implementação de requisitos não documentados em SPEC.
