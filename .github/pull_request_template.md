## Resumo

Descreva objetivamente o problema e a solução.

## Tipo de mudança

- [ ] Feature
- [ ] Bugfix
- [ ] Documentação
- [ ] Refatoração
- [ ] Segurança

## Governança documental (obrigatório)

- [ ] Li e segui a ordem: `CONTEXT.md` -> `docs/architecture/SDD.md` -> `docs/architecture/TDD.md` -> `docs/architecture/SPEC_FORMAT.md` -> `features/<feature>/SPEC.md` (quando houver feature em foco)
- [ ] Esta mudança possui SPEC em `features/<feature>/SPEC.md` quando aplicável (mudança não trivial/contratual)
- [ ] Quando houver SPEC aplicável, ela foi atualizada para refletir o escopo real desta PR
- [ ] Se houve decisão arquitetural durável, registrei ADR em `docs/adr/`
- [ ] Se não houve ADR, explicitei o motivo abaixo

### Referências obrigatórias

- SPEC: <!-- ex.: features/minha-feature/SPEC.md -->
- ADR(s): <!-- ex.: docs/adr/0012-meu-tema.md ou "não aplicável" -->

## TDD e validação

- [ ] TEST_RED escrito/atualizado antes do CODE_GREEN
- [ ] Testes relevantes passando
- [ ] Lint limpo
- [ ] Documentação atualizada (README/CONTRIBUTING/arquitetura, quando aplicável)

### Evidências

```bash
# cole aqui os comandos e saídas resumidas
python -m pytest ...
ruff check ...
```

## Como testar

Liste passos objetivos para reproduzir e validar localmente.

## Riscos e mitigação

- Risco 1:
- Mitigação 1:

## Checklist final

- [ ] Não introduz quebra não documentada
- [ ] Escopo está alinhado com a SPEC
- [ ] Alterações são rastreáveis por documentos técnicos
