# SDD.md

Guia de Spec Driven Development (SDD) para o LLM-knowledge-base.

## Objetivo

Garantir que toda evolução relevante do projeto seja guiada por especificação explícita, validável e rastreável.

A SPEC é o contrato de comportamento. Código e testes implementam esse contrato.

## Quando SPEC é obrigatória

Criar/atualizar `features/<feature>/SPEC.md` sempre que houver:

- nova feature
- mudança de comportamento observável
- alteração de contrato CLI/API
- mudança de política de dados, segurança ou persistência
- refactor com impacto funcional

Mudanças triviais (typos, comentários, ajustes cosméticos sem efeito funcional) podem ser exceção.

## Ciclo SDD oficial

1. Descoberta do problema
2. Escrita/atualização da SPEC
3. Validação da SPEC contra `SPEC_FORMAT.md`
4. Planejamento de testes (entrada do TDD)
5. Implementação incremental
6. Evidência e relatório

Sem SPEC estável, não avançar para implementação não trivial.

## Estrutura mínima da SPEC

A SPEC deve seguir `docs/architecture/SPEC_FORMAT.md` e conter no mínimo:

- objetivo claro
- requisitos funcionais verificáveis
- requisitos técnicos
- plano de testes (unit + integration + manual quando fizer sentido)
- dependências e riscos

Requisitos devem ser testáveis e sem ambiguidade.

## Princípios de qualidade da SPEC

- Atomicidade: uma SPEC por feature/coorte de mudança.
- Testabilidade: cada requisito mapeia para ao menos um teste.
- Rastreabilidade: decisões relevantes apontam para ADR quando necessário.
- Evolução controlada: alterações de escopo devem ser refletidas na SPEC antes do código.

## Relação entre SDD e TDD

- SDD define o que e por que.
- TDD define como validar via ciclo RED -> GREEN -> REFACTOR.

Sem SPEC, TDD vira adivinhação.
Sem TDD, SPEC vira documento sem garantia executável.

## Regra de precedência documental

Em caso de conflito:

1. `features/<feature>/SPEC.md` governa o comportamento da feature.
2. `docs/architecture/SDD.md` governa arquitetura e desenho de evolução.
3. `docs/architecture/TDD.md` governa estratégia de testes.
4. `docs/architecture/SPEC_FORMAT.md` governa formato da SPEC.
5. `CONTEXT.md` governa contexto macro e limites do produto.

## Quando abrir ADR

Criar/atualizar ADR em `docs/adr/` quando houver decisão arquitetural durável, por exemplo:

- mudança de estratégia de roteamento/recuperação
- mudança de política de persistência e versionamento
- alteração estrutural de guardrails e segurança
- alteração estrutural na separação engine × corpus

SPEC descreve a feature; ADR registra a decisão arquitetural.

## Checklist de entrada para implementação

- SPEC criada/atualizada e consistente com `SPEC_FORMAT.md`
- critérios de aceitação explícitos
- impactos em CLI/API documentados
- riscos e dependências descritos
- necessidade (ou não) de ADR declarada

## Checklist de saída

- requisitos da SPEC cobertos por testes
- validações executadas e registradas
- docs impactadas atualizadas
- rastreabilidade preservada (SPEC, ADR quando aplicável, relatório)
