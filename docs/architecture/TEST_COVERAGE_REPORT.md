# TEST_COVERAGE_REPORT.md

## Sprint fechado em 2026-04-03

## Evidência disponível

- suíte executada com sucesso: **85 testes passando**
- coleta atual: **85 testes collected**
- baseline validada com `pytest -q`
- **não há artefato numérico de cobertura atualizado** neste ambiente porque `pytest-cov` / `coverage.py` não estão instalados

## Cobertura funcional observada

### Áreas bem cobertas neste sprint

- `kb.compile`
  - compilação de raw para wiki
  - geração de summary compilado
  - update de índice
  - controle `--no-commit`
- `kb.qa`
  - roteamento por fonte nativa
  - file-back
  - `--allow-sensitive`
  - `--no-commit`
- `kb.heal`
  - fluxo de healing
  - guardrails
  - supressão de commit
- `kb.guardrails`
  - detecção de padrões sensíveis
  - bloqueio programático
  - bypass explícito
- `kb.state`
  - manifesto
  - knowledge
  - learnings
- `kb.jobs`
  - jobs canônicos `list/run`
- CLI
  - flags `--allow-sensitive`
  - flags `--no-commit`
  - propagação correta para módulos internos
- `kb.book_import_core`
  - fallback para parsing XML em ambiente mínimo
  - rejeição de XML inseguro

## Gaps prioritários

### P1

1. **Cobertura numérica formal ausente**
   - falta instalar e rodar ferramenta de cobertura (`pytest-cov` ou `coverage.py`)
   - impede medir regressão percentual por módulo

2. **Smoke test real com provider ainda pendente**
   - suíte atual é offline/mocked
   - ainda falta validar `import-book --compile`, `qa`, `heal` e `lint` contra OpenCode Go real

### P2

3. **Fluxos manuais/documentais ainda sem golden tests**
   - README / help do CLI / mensagens operacionais podem ganhar asserts mais específicos

4. **Jobs ainda sem persistência de execução**
   - há cobertura de invocação, mas não de histórico/telemetria porque a feature ainda não existe

## Veredito

- **Status:** cobertura funcional suficiente para fechar o sprint
- **Limitação:** cobertura percentual não auditável neste ambiente atual
- **Próximo passo recomendado:** adicionar tooling de cobertura e rodar smoke real com provider
