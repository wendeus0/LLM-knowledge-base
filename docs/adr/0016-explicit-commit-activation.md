# ADR 0016 — Ativação explícita de commit por comando

- **Status:** Aceito
- **Data:** 2026-04-12

## Contexto

O projeto já havia adotado Git como fonte de verdade para o corpus do usuário, mas a política histórica de commit automático por default passou a conflitar com o uso real do produto.

Problemas observados:

- `kb compile` já havia migrado para `--commit` explícito, enquanto `ingest`, `import-book`, `qa --file-back` e `heal` ainda seguiam auto-commit por padrão
- a superfície pública da CLI ficou inconsistente, exigindo que o usuário memorize contratos diferentes para operações semelhantes
- workflows exploratórios e via Obsidian querem write local frequente sem poluir o histórico Git a cada execução
- a futura adoção de `pre-commit` no repositório não deve ser confundida com a política de versionamento do corpus do produto

## Decisão

1. Todo comando público que escreve no corpus do usuário deve operar em modo local por padrão.
2. O versionamento Git do corpus passa a ser ativado explicitamente por comando via `--commit`.
3. `--no-commit` permanece aceito por compatibilidade e clareza, mas deixa de ser o caminho principal documentado.
4. Fluxos encadeados devem propagar a decisão explícita do caller, incluindo `ingest --compile`, `import-book --compile`, `qa --file-back` e writes internos em `outputs/` e `raw/`.
5. O helper `kb.git.commit()` continua existindo como mecanismo opcional e silencioso, fora do caminho crítico quando Git não está disponível.

## Consequências

### Positivas

- superfície CLI unificada para todos os comandos que escrevem no corpus
- menor ruído de histórico em workflows exploratórios e locais
- semântica mais clara: write local primeiro, versionamento quando explicitamente desejado
- separação conceitual melhor entre política do produto e hooks locais de desenvolvimento

### Negativas

- audit trail não nasce mais automaticamente para todo write
- usuários precisam lembrar de adicionar `--commit` quando quiserem persistir histórico Git naquela execução
- documentação e testes antigos precisaram ser atualizados para o novo contrato

## Alternativas consideradas

### A1. Manter auto-commit por padrão

- **Rejeitada.** Mantém a inconsistência já existente e continua gerando histórico excessivo em fluxos locais.

### A2. Configuração global persistente para política de commit

- **Rejeitada.** Esconderia uma decisão operacional importante fora do comando executado e aumentaria risco de surpresa.

### A3. Commit manual totalmente externo ao produto

- **Rejeitada.** O produto ainda precisa oferecer um caminho integrado para versionamento do corpus quando o usuário quiser esse comportamento no próprio comando.

## Supersede

- substitui a política de commit automático default descrita em `docs/adr/0003-git-versioning-strategy.md`
- substitui a parte de commit de `docs/adr/0007-explicit-sensitive-and-no-commit-controls.md`

## Referências

- `features/explicit-commit-contract/SPEC.md`
- `docs/adr/0003-git-versioning-strategy.md`
- `docs/adr/0007-explicit-sensitive-and-no-commit-controls.md`
