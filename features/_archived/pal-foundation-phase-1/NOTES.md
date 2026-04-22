# Notes — pal-foundation-phase-1

## Ambiguidades / decisões para próximos ciclos

1. `knowledge` e `learnings` devem ser versionados em git automaticamente ou apenas persistidos localmente?
   - decisão provisória da fase 1: versionar como artefato auditável e simples

2. O guardrail deve apenas pedir confirmação ou também oferecer `--allow-sensitive` e `--no-commit`?
   - fase 1: confirmação interativa/bloqueio em funções programáticas
   - futuro: flags explícitas

3. Jobs agendados devem executar diretamente a lógica Python ou reentrar via subprocess/CLI?
   - fase 1: executar lógica Python diretamente para manter testes simples

## Features futuras registradas

- multi-agent specialization
- rankings híbridos lexical + embeddings
- learnings explícitos por correção do usuário
- lint específico de `knowledge`/`learnings`
- geração de crontab/systemd snippets
- modo `no-commit` para fluxos sensíveis
