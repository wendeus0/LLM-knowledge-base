# ADR 0006 — Fundação com routing nativo, memória separada e guardrails inspirada em Pal

- **Status:** Aceito
- **Data:** 2026-04-03

## Contexto

O `kb` já possui um pipeline funcional de `raw/ -> wiki/`, busca lexical, Q&A e manutenção da wiki no corpus do usuário. Entretanto, a consulta ainda depende quase inteiramente de `wiki/`, não há separação clara entre conhecimento compilado e aprendizados operacionais do sistema, e os guardrails de conteúdo sensível estão majoritariamente documentados, mas pouco impostos em runtime.

A análise do repositório `agno-agi/pal` mostrou quatro padrões com alto valor para o `kb`:

1. roteamento por fonte nativa em vez de uma única estratégia de busca
2. separação entre `knowledge` e `learnings`
3. pipeline de ingestão com artefatos compilados reutilizáveis
4. governança operacional aplicada com confirmações e evals

Ao mesmo tempo, o `kb` continua sendo um produto local, orientado a CLI, markdown e git. Portanto, a adaptação precisa preservar simplicidade e auditabilidade.

## Decisão

1. Adotar uma **fase inicial de fundação** em vez de replicar a arquitetura de `Pal` integralmente.
2. Introduzir **routing por fonte nativa** no `qa`, começando com quatro fontes locais: `wiki`, `raw`, `knowledge` e `learnings`.
3. Criar stores separados e simples em disco para **`knowledge`** e **`learnings`**, sem banco externo nesta fase.
4. Estender o pipeline de compilação para gerar **summary compilado** e atualizar o store de knowledge.
5. Aplicar **guardrails com confirmação** antes de enviar conteúdo potencialmente sensível ao provider externo ou persistir file-back sensível.
6. Adicionar **jobs canônicos agendáveis** como catálogo declarativo de manutenção, sem daemon residente nesta fase.
7. Tratar **multi-agent specialization** como evolução futura, explicitamente fora do escopo inicial.

## Consequências

### Positivas

- melhora a precisão do `qa` ao escolher a fonte mais adequada
- cria uma base clara para memória funcional do produto
- aumenta auditabilidade do pipeline com summaries e manifestos
- reduz risco operacional ao mover parte da política de segurança para runtime
- prepara o projeto para evoluções futuras sem exigir infraestrutura adicional agora

### Negativas

- adiciona novos artefatos persistidos e mais caminhos de leitura
- introduz mais complexidade na superfície do `qa`
- exige atualização de testes e documentação para evitar drift
- o scheduler continua dependente de execução externa (cron/systemd/CI) até fase futura

## Alternativas consideradas

### A1. Manter a arquitetura atual e apenas documentar o roadmap
- **Rejeitada.** O projeto já possui lacunas operacionais conhecidas em guardrails e em separação de memória; documentar sem implementar manteria os riscos atuais.

### A2. Reproduzir `Pal` quase integralmente com múltiplos agentes e integrações externas
- **Rejeitada.** Seria overengineering para a baseline atual do `kb` e exigiria infraestrutura incompatível com a proposta leve do projeto.

### A3. Introduzir banco SQL e scheduler residente já na primeira fase
- **Rejeitada.** O valor imediato pode ser capturado com artefatos locais em disco e jobs declarativos, com custo muito menor.
