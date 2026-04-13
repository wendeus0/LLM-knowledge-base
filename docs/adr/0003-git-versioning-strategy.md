# ADR 0003 — Git como sistema de versionamento do corpus

- **Status:** Supercedido por ADR 0016
- **Data:** 2026-04-04

## Contexto

O projeto `kb` mantém uma wiki em markdown gerada a partir de documentos brutos no corpus do usuário. Cada operação que modifica a wiki (compile, heal, ou `qa --file-back` com `--to-wiki`) resulta em mudanças no filesystem que precisam ser persistidas e rastreáveis.

Sem uma estratégia de versionamento formal, havia risco de:

- perda de histórico de mudanças na wiki
- dificuldade de reversão em caso de erro na geração
- crescimento descontrolado do diretório wiki/ sem mecanismo de compactação
- necessidade de infraestrutura adicional (banco de dados, serviço externo)

## Decisão

1. Git será a fonte de verdade única para o estado versionado da wiki no corpus do usuário.
2. A política inicial adotada foi executar commits automáticos sempre que a wiki fosse modificada por operações do CLI.
3. Não haverá staging manual — o processo é totalmente automatizado.
4. Adotamos a estratégia de Pawel Huryn: operações são append-only ou atualizam seções específicas, nunca reescrevem arquivos completos arbitrariamente.
5. Mensagens de commit seguem padrão descritivo: `kb: <operação> - <contexto>`.
6. Conflitos são tratados como eventos raros — a estratégia append-only minimiza ocorrências.

## Consequências

### Positivas

- audit trail completo e imutável de todas as mudanças na wiki
- capacidade de reversão para qualquer ponto no tempo via `git checkout` ou `git revert`
- eliminação da necessidade de backend de banco de dados
- replicação e backup simplificados via push/pull para remotes
- compressão automática de histórico via packfiles do Git

### Negativas

- repositório cresce em tamanho conforme a wiki se expande
- possibilidade de conflitos em cenários de uso colaborativo (não previsto no uso solo)
- histórico de commits pode ficar denso com operações frequentes
- requer Git instalado e configurado no ambiente de execução

## Alternativas consideradas

### A1. SQLite como backend de versionamento

- **Rejeitada** por adicionar dependência e complexidade sem ganho proporcional. O Git já é necessário para o código do projeto.

### A2. S3 com versioning habilitado

- **Rejeitada** por introduzir dependência de infraestrutura cloud, custos operacionais e latência de rede. Elimina a possibilidade de uso totalmente offline.

### A3. Sem versionamento (filesystem apenas)

- **Rejeitada** por não atender ao requisito de audit trail e reversibilidade. Mudanças acidentais ou erros na geração seriam irreversíveis.

### A4. Git com staging manual obrigatório

- **Rejeitada** por adicionar fricção ao fluxo de trabalho. O objetivo do projeto é automação total do ciclo de vida da documentação.

## Referências

- Estratégia de Pawel Huryn: [pawelhuryn.com](https://pawelhuryn.com) — abordagem de notas incrementais e não-destrutivas
- Git como source of truth para knowledge bases: modelo similar ao Obsidian Git / Foam
- `docs/adr/0016-explicit-commit-activation.md`
