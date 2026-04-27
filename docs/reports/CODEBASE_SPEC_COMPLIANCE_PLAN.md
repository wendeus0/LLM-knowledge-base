# CODEBASE_SPEC_COMPLIANCE_PLAN.md

Plano inicial para analisar toda a base de código sob a política obrigatória de lastro em SPEC/ADR.

## Objetivo

Garantir que toda implementação existente no repositório esteja mapeada para:

- uma SPEC em `features/<feature>/SPEC.md`
- testes correspondentes ao comportamento especificado
- ADR quando houver decisão arquitetural durável

Implementação sem lastro será classificada como não conforme.

## Princípios de execução

- Evidência acima de opinião.
- Traçabilidade arquivo a arquivo.
- Priorização por risco (segurança, persistência, comportamento público CLI/API).
- Correções pequenas, incrementalmente auditáveis.

## Fase 1 — Inventário e mapeamento

1. Inventariar módulos em `kb/` por domínio funcional.
2. Mapear cada domínio para uma feature existente (`features/*`).
3. Classificar itens sem mapeamento como `GAP_SPEC`.

Entregável: matriz `módulo -> feature/SPEC -> status`.

## Fase 2 — Cobertura de especificação

Para cada feature/módulo:

1. Verificar se a SPEC cobre o comportamento real observado no código.
2. Identificar lacunas de requisito (código sem requisito explícito).
3. Identificar requisito sem implementação (SPEC desatualizada).

Entregável: lista `DRIFT_SPEC_CODE` com severidade (alta/média/baixa).

## Fase 3 — Cobertura de testes por requisito

1. Para cada requisito funcional da SPEC, localizar testes correspondentes.
2. Classificar cobertura por requisito:
   - `OK` (há teste e valida comportamento)
   - `PARCIAL`
   - `AUSENTE`
3. Levantar risco por ausência em caminhos críticos.

Entregável: matriz `requisito -> testes -> status`.

## Fase 4 — ADR e decisões arquiteturais

1. Revisar módulos com decisões estruturais (routing, state, guardrails, git integration, outputs, etc.).
2. Confirmar se há ADR existente para cada decisão durável.
3. Abrir pendências `GAP_ADR` quando necessário.

Entregável: backlog de ADRs faltantes.

## Fase 5 — Plano de correção (enforcement)

1. Criar ondas de correção por prioridade:
   - Onda 1: segurança + comportamento público
   - Onda 2: persistência + integrações
   - Onda 3: ergonomia e dívida técnica
2. Cada correção deve nascer com:
   - SPEC atualizada
   - TEST_RED
   - implementação GREEN
   - evidência no PR

Entregável: roadmap operacional por sprint/bloco.

## Critérios de aceite da conformidade global

- 100% dos módulos mapeados a SPEC ou explicitamente fora de escopo documentado.
- 100% das mudanças arquiteturais duráveis cobertas por ADR.
- 100% dos requisitos críticos com testes correspondentes.
- 0 PR aceita sem referência explícita de SPEC (e ADR quando aplicável).

## Modo de execução recomendado

- Executar auditoria em lotes pequenos por domínio (`compile`, `qa`, `heal`, `lint`, `search`, `infra`).
- Publicar relatório incremental por lote.
- Rejeitar alterações novas fora da política durante a migração.

## Primeira iteração sugerida (imediata)

1. Lote `compile + qa` (maior impacto funcional). ✅
2. Lote `heal + lint + search + infra` com classificação `GAP_SPEC/GAP_TEST/GAP_ADR`. ✅
3. Consolidar backlog priorizado por severidade e tipo de gap.
4. Iniciar correções pela severidade alta.
