# ADR 0007 — Controles explícitos `--allow-sensitive` e `--no-commit`

- **Status:** Parcialmente supercedido por ADR 0016 (parte de commit)
- **Data:** 2026-04-03

## Contexto

Após a introdução dos guardrails iniciais inspirados em `Pal`, o projeto `kb` passou a bloquear ou confirmar interativamente operações que enviam conteúdo potencialmente sensível ao provider externo. Ao mesmo tempo, a política histórica do produto continuava sendo commitar automaticamente todo write relevante no corpus do usuário, especialmente na wiki.

Essa combinação era boa para uso manual simples, mas insuficiente para dois cenários reais:

1. automação/execução não interativa, em que prompts de confirmação atrapalham
2. experimentos ou material sensível, em que o usuário quer escrever localmente sem registrar commit automático imediato

## Decisão

1. Adotar `--allow-sensitive` como **opt-in explícito por execução** para `compile`, `qa`, `qa --file-back`, `heal`, `lint` e `import-book --compile`.
2. A decisão original foi adotar `--no-commit` como **opt-out explícito do commit automático** para fluxos que escrevem no corpus do usuário (`wiki/` ou `outputs/`).
3. Manter o comportamento seguro por padrão:
   - sem `--allow-sensitive`, o sistema continua bloqueando programaticamente ou pedindo confirmação
   - sem `--no-commit`, o sistema continuava fazendo commit automático onde já fazia antes
4. Limitar o efeito das flags à execução corrente; não criar estado global persistente nesta fase.

## Consequências

### Positivas

- melhora previsibilidade operacional para automação e experimentação
- reduz risco de persistir conteúdo sensível em histórico git por acidente
- preserva a segurança por padrão para usuários normais do CLI
- mantém a interface pública simples, com flags locais e explícitas

### Negativas

- adiciona mais combinações possíveis de execução no CLI
- usuários podem usar `--allow-sensitive` sem política operacional madura se a documentação não for seguida
- `--no-commit` reduz rastreabilidade quando usado sem disciplina

## Alternativas consideradas

### A1. Manter apenas confirmação interativa

- **Rejeitada.** Não atende automação nem casos em que a confirmação precisa ser declarativa e repetível.

### A2. Criar configuração global persistente para sensibilidade/commit

- **Rejeitada.** Aumentaria risco operacional e esconderia decisões perigosas fora do comando invocado.

### A3. Remover completamente o commit automático

- **Rejeitada na época.** Esta alternativa foi posteriormente revisitada e substituída por commit explícito por comando no ADR 0016.

## Atualização

O controle de sensibilidade via `--allow-sensitive` continua válido. A parte desta ADR referente ao modelo de commit foi substituída por `docs/adr/0016-explicit-commit-activation.md`.
