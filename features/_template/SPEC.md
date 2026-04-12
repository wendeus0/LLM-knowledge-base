---
title: <Título da feature>
epic: <compile|qa|heal|lint|search|infra>
status: draft
pr: <link PR quando mergear>
---

# <Título da feature>

## Objetivo

Descreva em uma frase o comportamento atual e o comportamento desejado.

## Requisitos funcionais

- [ ] RF-01: <requisito verificável>
- [ ] RF-02: <requisito verificável>
- [ ] RF-03: <requisito verificável>

## Requisitos técnicos

- RT-01: <decisão técnica obrigatória>
- RT-02: <restrição técnica relevante>

## Mudanças de API/CLI

Descreva comandos, parâmetros, contratos públicos, compatibilidade e possíveis quebras.

## Testes

- Unit: <o que precisa cobrir>
- Integration: <fluxo end-to-end esperado>
- Manual: <passos de validação manual, se aplicável>

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | <horas> |
| Bloqueador | <sim/não> |
| Risco | <baixo/médio/alto> |

## Dependências

- <feature/doc/infra que precisa existir antes>

## ADR

- Necessária? <sim/não>
- Se sim, referência: `docs/adr/00xx-<titulo>.md`

## Critérios de aceite

- [ ] Critério 1 validado por teste
- [ ] Critério 2 validado por teste
- [ ] Critério 3 validado por evidência operacional

## Evidências esperadas

- Comandos executados:
  - `python -m pytest ...`
  - `ruff check ...`
- Arquivos alterados:
  - `<arquivo A>`
  - `<arquivo B>`

## Notas

Registre lacunas, decisões locais e limitações conhecidas.
