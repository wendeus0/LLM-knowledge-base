# Notes — sensitive-execution-controls

## Decisões provisórias

1. `--allow-sensitive` é uma autorização explícita por execução, não persistente.
2. `--no-commit` vale apenas para o fluxo acionado; não altera a política global do projeto.
3. O write local continua acontecendo com `--no-commit`; apenas o commit git é suprimido.

## Ambiguidades futuras

- Precisamos de diretórios com política fixa (`raw/private/`, `wiki/private/`)?
- Vale adicionar `KB_DEFAULT_NO_COMMIT` ou `KB_SENSITIVE_MODE` no futuro?
- Devemos registrar em log local que uma execução ocorreu com `--allow-sensitive`?

## Features futuras relacionadas

- políticas por diretório
- níveis de sensibilidade
- auditoria/telemetria local de execuções sensíveis
- aprovação em lote para jobs agendados
