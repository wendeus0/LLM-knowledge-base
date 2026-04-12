# SPEC_FORMAT.md

Formato obrigatório de SPEC para features do kb.

## Estrutura

```yaml
---
title: <Título da feature>
epic: <compile|qa|heal|lint|search|infra>
status: <draft|approved|in_progress|done>
pr: <link PR quando mergear>
---

# <Título>

## Objetivo

<Uma frase: o que o sistema faz agora vs. o que deveria fazer>

## Requisitos funcionais

- [ ] <critério 1>
- [ ] <critério 2>
- [ ] <critério 3>

## Requisitos técnicos

- <decisão arquitetural 1>
- <decisão arquitetural 2>

## Mudanças de API/CLI

Se público: descrever novo CLI, novo módulo público, contratos de flags, compatibilidade e possíveis breaking changes.

## Testes

- Unit: <o que testar>
- Integration: <fluxo end-to-end>
- Manual: <steps para reproduzir>

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | <horas> |
| Bloqueador | <sim/não> |
| Risk | <baixa/média/alta> |

## Dependências

- <feature A que deve estar pronta primeiro>

## Notas

<qualquer coisa else relevant>
```

## Epics do kb

- **compile:** raw/ → wiki/ no corpus do usuário
- **qa:** perguntas contra wiki
- **heal:** stochastic healing
- **lint:** health checks
- **search:** busca na wiki
- **infra:** client, config, git, CLI

## Exemplo

```markdown
---
title: Heal — detectar artigos órfãos
epic: heal
status: draft
---

# Heal — Detectar Artigos Órfãos

## Objetivo

Quando heal roda, detectar artigos que não são referenciados por nenhum outro artigo. Opcionalmente deletar ou marcar como "candidato a delete".

## Requisitos funcionais

- [ ] Heal detecta wikilinks faltando em artigos que citam conceitos
- [ ] Heal sugere artigos órfãos (não citados por ninguém)
- [ ] Flag `--delete-orphans` deleta artigos sem referências

## Requisitos técnicos

- Usar grafo de wikilinks existentes
- Não delete stubs valiosos (sem conteúdo mas muita demanda)

## Testes

- Unit: detectar órfãos em wiki small (5 artigos)
- Integration: heal numa wiki real

## Dados

| Chave | Valor |
|-------|-------|
| Estimativa | 2h |
| Bloqueador | não |
| Risk | médio |

## Dependências

- heal base funcional

```
