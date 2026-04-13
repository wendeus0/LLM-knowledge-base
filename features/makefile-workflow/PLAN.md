# PLAN — Makefile workflow

## Objetivo técnico

Adicionar um `Makefile` pequeno que elimine repetição de comandos comuns sem criar uma camada paralela de automação.

## Estratégia

1. Criar alvo `help` autodocumentado.
2. Adicionar alvos de instalação mais usados: base, llm, dev e all.
3. Adicionar alvos de qualidade: `lint`, `test`, `test-unit`, `test-integration`, `check`.
4. Adicionar poucos atalhos operacionais para `kb jobs list`, `kb jobs cron` e `kb handoff create` apenas se o comando ficar claro e parametrizável.
5. Atualizar `README.md` e `CONTRIBUTING.md` para citar o `Makefile` como atalho recomendado, sem remover os comandos brutos.

## Riscos

- excesso de targets e crescimento do `Makefile` além do necessário
- targets que escondem argumentos importantes do CLI e criam falsa abstração

## Fora de escopo

- `scripts/` shell/python
- geração de ambiente virtual
- automação de push/PR/release
