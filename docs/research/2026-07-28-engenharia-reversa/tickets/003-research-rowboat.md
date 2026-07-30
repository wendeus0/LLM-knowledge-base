# Engenharia reversa — rowboat

Type: research
Status: resolved
Blocked by: —

## Question

Como o `rowboatlabs/rowboat` estrutura um "AI coworker with memory" — e o que a camada de memória e a UI dele sugerem para o kb?

Alvo do dossiê:

1. **Memória** — o que persiste entre sessões, em que store, como é escrito e recuperado, como decide o que lembrar. É o eixo mais próximo do kb (o kb é memória durável em markdown).
2. **Frontend** — `apps/rowboat` e `apps/rowboatx`: stack, layout, o que a UI mostra que um editor de markdown não mostraria. Evidência para a pergunta em aberto "o kb deveria ter UI própria" — descrever o que a UI resolve, sem recomendar.
3. **Contrato front↔agente** — streaming, estado de sessão, exibição de passos do agente.
4. **CLI e SDK** — `apps/cli`, `apps/python-sdk`: qual a superfície não-visual e como convive com a UI.
5. **Armazenamento** — Qdrant aparece no `docker-compose.yml`: onde vetores entram e para quê.

Repo grande (182 MB, TypeScript). Priorize memória e frontend; o resto é nota curta.

## Answer

Dossiê: [DOSSIE-rowboat.md](../DOSSIE-rowboat.md). Commit lido `e1f2656`. Executado por GPT 5.6 Terra (effort high) via `fable-gpt`, no segundo despacho — o primeiro run morreu deixando arquivo de 0 byte, e foi reexecutado em modo síncrono com escrita incremental. Review zero-trust aprovado; o executor rodou o próprio verify (55 caminhos citados, 0 faltando).

Gist — o achado principal contraria a expectativa de que "app com memória" significa banco vetorial:

- **A memória pessoal é Markdown em disco, não Qdrant.** `WorkDir/knowledge/Agent Notes/` com `user.md` (identidade), `preferences.md` (regras), `style/email.md` e temáticos. Qdrant existe, mas serve RAG de documentos do console web, filtrado por `projectId`/`sourceId`. São dois sistemas separados que o código não cruza.
- **Captura e consolidação são desacopladas.** O tool `save-to-memory` só faz append de `- [timestamp] nota` em `inbox.md`; um serviço periódico (10s neste snapshot, comentado como valor de teste) manda o acumulado a um agente curador, e só limpa a inbox após sucesso.
- **Recuperação é carregamento de arquivo, não busca.** `user.md` e `preferences.md` entram integralmente no system prompt; os demais `.md` são apenas *listados* para leitura sob demanda via tool. `inbox.md` é explicitamente excluído do carregamento.
- **Expiração é semântica, não TTL.** A instrução do curador manda refrescar timestamp de fato reconfirmado, remover fato transitório envelhecido e preservar fato estável — com a regra explícita de que perder observação já registrada é a pior falha possível.
- **A UI expõe estado operacional, não conteúdo.** É a resposta à pergunta que motivou o ticket: grafo Mermaid da topologia de agentes, ciclo de vida de fontes e jobs (`pending`/`running`/`completed`/`failed`), distinção draft/live com reversão, e — em `rowboatx` — reasoning, tool call, input/resultado e artefato como itens tipados distintos no mesmo histórico. Nada disso é conteúdo de arquivo; é estado calculado que um editor de markdown não tem como mostrar.
- **Streaming por SSE em duas etapas** nas duas superfícies: ação cria turn em cache e devolve `streamId`; cliente abre `EventSource` e recebe `message`/`tool-call`/`tool-result`/`done`. Continuidade de sessão é `conversationId` reenviado pelo cliente.
- **Ressalva de estado do repo:** o entrypoint de chat da CLI (`apps/cli/src/app.ts:44`) é `throw new Error("Not implemented")` com a implementação comentada. O caminho vivo é servidor Hono + TUI.
