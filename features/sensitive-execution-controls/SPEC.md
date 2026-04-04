---
title: Sensitive execution controls
epic: infra
status: draft
pr:
---

# Sensitive execution controls

## Objetivo

Hoje o `kb` já detecta conteúdo potencialmente sensível e pede confirmação em alguns fluxos LLM, mas ainda não oferece controles explícitos de execução para automação e para cenários em que o usuário quer evitar commits automáticos. Esta feature adiciona flags operacionais previsíveis para permitir uso consciente do provider externo e da persistência em git.

## Requisitos funcionais

- [ ] `kb compile`, `kb qa`, `kb qa --file-back`, `kb heal` e `kb lint` devem aceitar uma flag explícita para permitir processamento de conteúdo sensível sem prompt interativo
- [ ] fluxos que escrevem na wiki (`compile`, `qa --file-back`, `heal`, atualização de índice ligada ao compile) devem aceitar uma flag explícita para executar sem commit automático em git
- [ ] quando `--no-commit` estiver ativo, os arquivos devem ser escritos normalmente em disco, mas nenhum commit git deve ser disparado por aquele fluxo
- [ ] quando `--allow-sensitive` não estiver ativo, o comportamento seguro atual deve ser preservado: bloqueio programático e confirmação no CLI antes de enviar conteúdo ao provider externo
- [ ] a documentação operacional do projeto deve explicar quando usar `--allow-sensitive` e `--no-commit`, incluindo riscos e limitações

## Requisitos técnicos

- preservar compatibilidade da CLI atual, adicionando apenas flags opcionais
- concentrar a decisão de commit em um ponto simples e testável
- evitar duplicação de lógica entre CLI e módulos internos
- manter a suíte offline, sem chamadas reais a provider externo

## Mudanças de API

### CLI

- `kb compile [--allow-sensitive] [--no-commit]`
- `kb qa [--allow-sensitive]`
- `kb qa --file-back [--allow-sensitive] [--no-commit]`
- `kb heal [--allow-sensitive] [--no-commit]`
- `kb lint [--allow-sensitive]`
- `kb import-book --compile [--allow-sensitive] [--no-commit]`

### Comportamento

- `--allow-sensitive` pula a confirmação interativa e autoriza o envio do conteúdo detectado ao provider externo
- `--no-commit` mantém write local sem criar commit git naquele fluxo

## Testes

- Unit: flags propagadas corretamente para compile/qa/heal/lint; commit helper respeita `enabled=False`
- Integration: `compile --no-commit` escreve artigo e summary sem chamar commit; `qa --file-back --no-commit` salva artigo sem commit; `--allow-sensitive` permite seguir sem erro
- Manual:
  1. `kb compile --allow-sensitive --no-commit`
  2. `kb qa "..." --allow-sensitive`
  3. `kb qa "..." --file-back --no-commit`
  4. `kb heal --allow-sensitive --no-commit`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 0.5-1 dia |
| Bloqueador | não |
| Risk | médio |

## Dependências

- `pal-foundation-phase-1` concluída
- guardrails e jobs já disponíveis na baseline atual

## Notas

### Fora de escopo

- políticas por diretório (`raw/private/`)
- classificação multinível de sensibilidade
- scheduler persistente
- UI/TUI para aprovação interativa rica
