# ADR 0011 — Externalizar corpus do usuário para fora do repositório da engine

- **Status:** Aceito
- **Data:** 2026-04-07

## Contexto

O repositório principal do `kb` passou a misturar duas responsabilidades distintas:

1. a **engine** do produto (`kb/`, testes, documentação, CLI)
2. o **corpus pessoal do usuário** (`raw/`, `wiki/`, `outputs/`, `kb_state/`, `.obsidian/`)

Essa mistura gerava problemas para distribuição open source:

- confundia produto com uso pessoal
- fazia parecer que domínios temáticos específicos do corpus eram parte oficial do projeto
- introduzia ruído de editor/Obsidian no diff do produto
- dificultava onboarding de terceiros, que deveriam usar seu próprio vault

## Decisão

1. O repositório principal passa a distribuir apenas a **engine** do `kb`, testes, documentação e exemplos neutros.
2. O corpus do usuário deve viver fora do repositório principal, apontado por `KB_DATA_DIR`.
3. Os diretórios lógicos `raw/`, `wiki/`, `outputs/` e `kb_state/` passam a ser tratados como dados do usuário, não como artefatos canônicos do repo da engine.
4. O Obsidian torna-se o frontend oficial recomendado, mas sobre `<KB_DATA_DIR>/wiki`.
5. Arquivos locais de editor, incluindo `.obsidian/`, não devem ser versionados no repositório principal.
6. O repositório principal pode conter apenas exemplos neutros mínimos em `examples/` para onboarding.

## Consequências

### Positivas

- separação clara entre produto e conteúdo do usuário
- onboarding open source mais limpo
- menos ruído de arquivos locais e configurações de editor
- menor risco de comunicar corpus temático pessoal como parte oficial do projeto
- base mais adequada para múltiplos usuários e múltiplos vaults

### Negativas

- setup inicial exige configurar `KB_DATA_DIR`
- parte da documentação histórica precisa ser neutralizada gradualmente
- exemplos de uso precisam ser mais cuidadosos para não depender do corpus do autor

## Alternativas consideradas

### A1. Manter corpus no repositório principal
- **Rejeitada.** Mantém a confusão entre engine e conteúdo e prejudica o posicionamento open source.

### A2. Manter corpus no repo principal mas como exemplo completo
- **Rejeitada.** Mesmo com documentação explicando, a tendência é o exemplo ser interpretado como distribuição oficial do produto.

### A3. Remover corpus sem oferecer seed neutro
- **Parcialmente rejeitada.** A engine deve ficar separada, mas exemplos mínimos em `examples/` ajudam onboarding e smoke tests.

## Implementação inicial

- `kb/config.py` passou a suportar `KB_DATA_DIR` e overrides por diretório
- `.gitignore` passou a ignorar `raw/`, `wiki/`, `outputs/`, `kb_state/` e `.obsidian/`
- corpus pessoal atual foi movido para diretório externo
- README e docs principais foram reposicionados para engine vs. corpus
- `examples/` foi criado com seed neutro mínimo

## Próximos passos

1. Neutralizar documentação histórica restante ainda acoplada ao corpus antigo
2. Avaliar tornar `TOPICS` configurável por corpus
3. Definir se o corpus do usuário terá repositório próprio versionado
