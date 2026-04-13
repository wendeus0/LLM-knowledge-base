# ADR 0014 — Fonte única de verdade para versão de release

- Status: Aceito
- Data: 2026-04-12

## Contexto

O repositório documenta releases em `CHANGELOG.md`, mas `pyproject.toml` permaneceu em `0.1.0` mesmo após entradas até `0.4.0`. Isso cria ambiguidade operacional: pacote instalado, metadata de build e documentação pública podem apontar para versões diferentes.

## Decisão

1. `kb.__version__` passa a ser a fonte canônica da versão do pacote.
2. O Hatch deve ler a versão dinamicamente a partir de `kb/__init__.py`.
3. `CHANGELOG.md` deve manter a entrada mais recente alinhada com `kb.__version__`.
4. Um teste automatizado deve falhar se o contrato entre pacote, build metadata e changelog divergir.

## Consequências

### Positivas

- reduz drift entre build e documentação
- torna explícito o ponto único de manutenção da versão
- transforma o contrato de release em gate executável

### Negativas

- ainda existe sincronização humana do conteúdo do changelog
- mudar a versão exige atualização deliberada antes de publicar

## Alternativas consideradas

### A1. Manter versão fixa apenas em `pyproject.toml`

- Rejeitada por já ter falhado operacionalmente sem um gate forte.

### A2. Usar apenas tags Git como fonte de verdade

- Rejeitada porque o pacote continua precisando de metadata local para build e instalação antes do fluxo de release completo.

## Referências

- `pyproject.toml`
- `kb/__init__.py`
- `CHANGELOG.md`
