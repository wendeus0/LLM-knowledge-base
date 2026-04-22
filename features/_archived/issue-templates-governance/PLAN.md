# PLAN — Issue templates governance

## Objetivo técnico

Criar intake estruturado no GitHub sem expandir escopo para automações, labels dinâmicas ou novos workflows.

## Estratégia

1. Criar `config.yml` para desabilitar blank issues e expor contact links relevantes.
2. Criar três formulários distintos:

- bug report
- feature request
- operational task

3. Atualizar `CONTRIBUTING.md` para refletir o fluxo real de abertura de issues.
4. Validar sintaxe local dos YAMLs.

## Riscos

- drift com `SECURITY.md` se o link privado de vulnerabilidades divergir
- formulário genérico demais e sem campos suficientes para intake SDD

## Fora de escopo

- GitHub Discussions
- automação de labels/projetos
- templates adicionais para docs-only ou security advisory
