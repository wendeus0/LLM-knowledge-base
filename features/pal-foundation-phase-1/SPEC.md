---
title: Pal foundations phase 1
epic: infra
status: draft
pr:
---

# Pal foundations phase 1

## Objetivo

Hoje o `kb` possui ingestão, compilação e Q&A centrados quase exclusivamente na `wiki/`. Esta feature introduz uma fundação inicial inspirada em `agno-agi/pal`: roteamento por fonte nativa, memória separada (`knowledge` vs `learnings`), summary compilado, guardrails operacionais, jobs agendáveis e cobertura automatizada desses fluxos.

## Requisitos funcionais

- [ ] `kb qa` deve decidir uma rota principal de leitura entre `wiki`, `raw`, `knowledge` e `learnings` usando heurísticas determinísticas e produzir resposta usando a fonte escolhida
- [ ] operações que enviam conteúdo ao provider externo (`compile`, `qa`, `qa --file-back`, `heal`, `lint`) devem interromper ou pedir confirmação quando detectarem conteúdo potencialmente sensível
- [ ] toda compilação bem-sucedida deve registrar artefato em `knowledge`, produzir um summary compilado e manter manifesto mínimo reutilizável pelo roteamento
- [ ] o produto deve manter stores separados para `knowledge` e `learnings`, sem misturar os dois tipos de memória no mesmo arquivo
- [ ] o CLI deve expor jobs canônicos ao menos para listar e executar tarefas agendáveis de manutenção
- [ ] a suíte automatizada deve cobrir routing, guardrails, knowledge/learnings stores, geração de summaries e execução de jobs

## Requisitos técnicos

- manter compatibilidade com a baseline atual de CLI local, markdown e git
- evitar dependência obrigatória nova além da stack atual
- implementar a memória funcional em formato simples e auditável em disco
- preservar o comportamento existente de `search`, `compile`, `heal` e `lint` quando os novos caminhos não forem acionados
- permitir evolução futura para ranking híbrido e especialização multi-agent sem reescrever a interface pública

## Mudanças de API

### CLI

- novo grupo `kb jobs`
  - `kb jobs list`
  - `kb jobs run <job>`

### Comportamento

- `kb qa` passa a usar roteamento por fonte
- fluxos com provider externo podem pedir confirmação quando houver sensibilidade detectada
- `kb compile` passa a gerar summary compilado e registrar knowledge

## Testes

- Unit: roteamento de perguntas para cada fonte, detecção de sensibilidade, stores de knowledge/learnings, geração de summary
- Integration: ingest -> compile -> summary -> knowledge; jobs canônicos; guardrail bloqueando conteúdo sensível
- Manual:
  1. `kb ingest <arquivo>`
  2. `kb compile`
  3. `kb qa "resuma a fonte original"`
  4. `kb jobs list`
  5. `kb jobs run compile`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 1-3 dias |
| Bloqueador | não |
| Risk | médio |

## Dependências

- baseline atual de `kb` íntegra
- política operacional derivada de `SECURITY_AUDIT_REPORT.md`

## Notas

### Fora de escopo

- especialização multi-agent
- embeddings/RAG vetorial
- scheduler daemon residente
- integração com Gmail/Calendar/Slack
- sincronização remota de contexto
