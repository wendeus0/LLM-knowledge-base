# Dossiê — rowboat

## Identificação

- **Snapshot lido:** commit `e1f2656b343d8a294ddc60d8c8b1533a5ee3261c`; a data e assunto do commit são os reportados por `git log -1` no clone. O tamanho observado do diretório é `182M`.
- **Licença:** Apache License 2.0 (`LICENSE:1-4`).
- **Layout:** monorepo sem um manifesto raiz único: `apps/rowboat` e `apps/rowboatx` são aplicações web Next; `apps/x` é um workspace desktop Electron com renderer Vite/React e `packages/core`; `apps/cli` é o pacote Node `@rowboatlabs/rowboatx`; `apps/python-sdk` é o pacote Python `rowboat` (`apps/rowboat/package.json:1-16`, `apps/rowboatx/package.json:1-10`, `apps/x/package.json:1-23`, `apps/cli/package.json:1-21`, `apps/python-sdk/pyproject.toml:1-22`).
- **Stack predominante:** TypeScript/Node em todas as aplicações principais; Next + React nos dois frontends web (`apps/rowboat/package.json:54-64`, `apps/rowboatx/package.json:31-51`); Electron no desktop (`apps/x/apps/main/package.json:1-13`); Vite + React no renderer desktop (`apps/x/apps/renderer/package.json:5-12`, `apps/x/apps/renderer/package.json:71-85`); Python/Pydantic/Requests no SDK (`apps/python-sdk/pyproject.toml:5-22`).

## Mapa de aplicações

| App | Responsabilidade observada | Evidência |
| --- | --- | --- |
| `apps/x` | Produto desktop: orquestra build do core, preload, renderer Vite e processo Electron. | `apps/x/package.json:6-23`, `apps/x/apps/main/package.json:1-13` |
| `apps/x/packages/core` | Runtime e serviços da aplicação desktop: agente, knowledge graph, memória e integrações. | `apps/x/packages/core/package.json:5-15`, `apps/x/packages/core/src/runtime/tools/domains/memory.ts:12-34` |
| `apps/rowboat` | Console web Next para configurar projetos/workflows, fontes, tools, triggers, chats e jobs; inclui APIs e workers RAG. | `apps/rowboat/package.json:6-16`, `apps/rowboat/app/projects/[projectId]/workflow/page.tsx:1`, `apps/rowboat/app/scripts/rag-worker.ts:1-21` |
| `apps/rowboatx` | Interface web alternativa para executar chats, observar streams e abrir/editar recursos de agente/configuração. | `apps/rowboatx/app/page.tsx:110-142`, `apps/rowboatx/app/page.tsx:492-545`, `apps/rowboatx/app/page.tsx:547-812` |
| `apps/cli` | Binário Node `rowboatx`, servidor Hono/SSE e TUI Ink para runs, modelos e MCP. | `apps/cli/package.json:6-18`, `apps/cli/src/server.ts:1-18`, `apps/cli/src/tui/index.tsx:1-8` |
| `apps/python-sdk` | Cliente Python síncrono para a API de chat por projeto. | `apps/python-sdk/src/rowboat/client.py:10-50`, `apps/python-sdk/src/rowboat/schema.py:39-58` |
| `apps/docs` | Site de documentação, construído como serviço opcional no Compose. | `docker-compose.yml:232-238` |
| `apps/experimental` | Espaço de integrações experimentais; o Compose referencia, mas deixa comentados, widget de chat, webhook tools, runner de simulação e handler Twilio. | `docker-compose.yml:103-121`, `docker-compose.yml:204-215`, `docker-compose.yml:240-250` |

## 1. Memória

### O que o código chama de memória

No produto mais recente, `apps/x`, a memória pessoal explícita é o diretório local `WorkDir/knowledge/Agent Notes/`, não uma coleção vetorial. O tool `save-to-memory` registra observações concisas no arquivo `inbox.md`; a descrição do próprio tool delimita o conteúdo a preferências, padrões de comunicação, contexto de relacionamentos, hábitos de agenda e instruções explícitas (`apps/x/packages/core/src/runtime/tools/domains/memory.ts:13-27`).

O store durável é uma árvore de arquivos Markdown. O prompt do agente de manutenção define quatro classes: `user.md` para identidade e contexto; `preferences.md` para regras/preferências gerais; `style/email.md` para padrões de escrita; e arquivos temáticos apenas para preferências recorrentes (`apps/x/packages/core/src/knowledge/agent_notes_agent.ts:24-31`). Há também o estado operacional em `WorkDir/agent_notes_state.json`, com mapas de emails e conversas processadas e `lastRunTime` (`apps/x/packages/core/src/knowledge/agent_notes_state.ts:5-11`).

Portanto, “memória” tem dois níveis que o código mantém separados: (1) memória pessoal global do agente em `Agent Notes`; (2) a knowledge base de entidades e fontes em outros Markdown sob `knowledge/`. O segundo nível é usado para extrair e curar pessoas, organizações, projetos, tópicos e reuniões; o próprio curador enumera esses tipos de nota (`apps/x/packages/core/src/knowledge/note_curation.ts:41-47`). Não há evidência, nesta leitura, de que `Agent Notes` seja indexado em Qdrant.

### Escrita e admissão

Uma conversa pode gerar uma candidata a memória quando o agente escolhe chamar `save-to-memory`: a execução cria o diretório se necessário e faz `appendFile` de uma linha `- [ISO timestamp] nota` em `inbox.md` (`apps/x/packages/core/src/runtime/tools/domains/memory.ts:19-27`). Esse é um mecanismo de captura explícito, decidido pelo agente; a instrução do tool diz quando ele deve considerar a observação “worth remembering” (`apps/x/packages/core/src/runtime/tools/domains/memory.ts:13-18`).

Um serviço assíncrono amplia as fontes: lê (a) emails enviados pelo usuário, (b) entradas de inbox e (c) mensagens de conversas Copilot ainda não processadas (`apps/x/packages/core/src/knowledge/agent_notes.ts:230-267`). Quando há material, envia tudo ao agente `agent_notes_agent` com timestamp corrente via `runWhenPossible` (`apps/x/packages/core/src/knowledge/agent_notes.ts:269-289`). Só após sucesso ele marca os emails/runs como processados, limpa a inbox e persiste o estado (`apps/x/packages/core/src/knowledge/agent_notes.ts:291-303`). O loop começa imediatamente e então consulta a cada 10 segundos (`apps/x/packages/core/src/knowledge/agent_notes.ts:19`, `apps/x/packages/core/src/knowledge/agent_notes.ts:343-358`).

A decisão semântica de reter não é uma regra determinística de schema: é delegada ao LLM que recebe a instrução `Agent Notes`. Ela ordena encaminhar inbox para `preferences.md` ou arquivo temático, extrair fatos duráveis de chats para `user.md`, e tratar emails enviados como evidência de estilo (`apps/x/packages/core/src/knowledge/agent_notes_agent.ts:33-38`). A mesma instrução manda descartar tarefas pontuais/efêmeras e não criar arquivos vazios (`apps/x/packages/core/src/knowledge/agent_notes_agent.ts:78-98`).

### Schema e manutenção

O schema da memória pessoal é deliberadamente leve: Markdown, com bullets timestampados obrigatórios para `user.md` no formato `- [ISO_TIMESTAMP] fato` (`apps/x/packages/core/src/knowledge/agent_notes_agent.ts:85-90`). `preferences.md` e arquivos temáticos não têm schema rígido além de serem concisos; `style/email.md` é uma taxonomia cumulativa organizada por contexto de destinatário, com no máximo 2–3 exemplos por bucket (`apps/x/packages/core/src/knowledge/agent_notes_agent.ts:57-70`).

Há deduplicação e atualização por instrução do agente: antes de incluir um fato, ele deve procurar equivalentes inclusive com outra redação; fatos já presentes recebem timestamp novo; preferências podem ser reorganizadas/deduplicadas preservando as ainda relevantes (`apps/x/packages/core/src/knowledge/agent_notes_agent.ts:85-93`). A expiração é semântica, não TTL: fatos transitórios antigos podem ser removidos, enquanto fatos estáveis devem persistir (`apps/x/packages/core/src/knowledge/agent_notes_agent.ts:87-91`). O JSON de controle evita reprocessar a mesma fonte, mas não é o conteúdo da memória (`apps/x/packages/core/src/knowledge/agent_notes_state.ts:7-11`, `apps/x/packages/core/src/knowledge/agent_notes_state.ts:43-52`).

No nível separado da knowledge base, há consolidação explícita das notas de entidades: o curador compacta atividade com mais de 60 dias por mês, elimina duplicatas/near-duplicates, promove padrões recorrentes para fatos/observações e marca relações sem interação por 90+ dias como `status: stale` (`apps/x/packages/core/src/knowledge/note_curation.ts:63-89`). Isso é manutenção da base de conhecimento, não o mecanismo de injeção da memória pessoal descrito abaixo.

### Recuperação na resposta

A recuperação da memória pessoal é por carregamento de arquivo no assembly do agente. `loadAgentNotesContext()` injeta integralmente `user.md` como “About the User” e `preferences.md` como “User Preferences”; os outros `.md` são apenas listados para leitura sob demanda via `file-readText` quando diretamente relevantes (`apps/x/packages/core/src/runtime/assembly/workspace-context.ts:34-84`). `inbox.md` fica explicitamente excluído desse carregamento (`apps/x/packages/core/src/runtime/assembly/workspace-context.ts:58-61`).

O carregamento é condicionado ao trait `workspaceContext`: agentes sem ele recebem `{ agentNotesContext: null, userWorkDir: null }` (`apps/x/packages/core/src/runtime/assembly/workspace-context.ts:98-114`). Na resolução de uma turn, esse contexto é carregado e passado a `composeSystemInstructions`, antes da seleção de tools (`apps/x/packages/core/src/runtime/turns/bridges/real-agent-resolver.ts:129-153`). Logo, a memória pessoal relevante já entra no system prompt de cada resposta elegível; a memória temática adicional é recuperada por arquivo somente quando o agente julga necessário.

## 2. Frontend

### Duas superfícies, dois estágios

`apps/rowboat` é o console web completo: `package.json` o declara Next 15.3.8 com React 19.1, TypeScript, Tailwind, HeroUI, Mermaid, `react-resizable-panels`, Quill e clientes MongoDB/Redis/Qdrant (`apps/rowboat/package.json:5-16`, `apps/rowboat/package.json:30-64`). A árvore de rotas do App Router cobre projetos, editor de workflow, fontes, jobs, conversas, gatilhos e configurações; as ferramentas aparecem como parte do editor de workflow (`apps/rowboat/app/projects/[projectId]/workflow/page.tsx:1`, `apps/rowboat/app/projects/[projectId]/sources/page.tsx:1`, `apps/rowboat/app/projects/[projectId]/jobs/page.tsx:1`, `apps/rowboat/app/projects/[projectId]/conversations/page.tsx:1`, `apps/rowboat/app/projects/[projectId]/manage-triggers/page.tsx:1`, `apps/rowboat/app/projects/[projectId]/config/page.tsx:1`, `apps/rowboat/app/projects/[projectId]/workflow/workflow_editor.tsx:9-43`). A rota-base de um projeto redireciona para `/workflow`, tornando o editor o ponto de entrada do projeto (`apps/rowboat/app/projects/[projectId]/page.tsx:4-12`).

`apps/rowboatx` é uma segunda interface Next 15.5/React 19, com Radix UI, Tiptap, `@xyflow/react` e AI SDK (`apps/rowboatx/package.json:5-52`). Nesta cópia, ela tem uma única rota `app/page.tsx` e `next.config.ts` usa `output: "export"` (`apps/rowboatx/app/page.tsx:1-61`, `apps/rowboatx/next.config.ts:4-10`). O código referencia uma API em `window.config.apiBase` e endpoints `/runs`, `/agents`, `/config`, `/models` e `/mcp`; a implementação desses endpoints não está sob `apps/rowboatx/app/api/` neste clone (`apps/rowboatx/app/page.tsx:111-194`, `apps/rowboatx/app/page.tsx:515-537`, `apps/rowboatx/app/page.tsx:561-655`).

### Estado, navegação e telas

No console `rowboat`, o `WorkflowEditor` mantém em React o projeto, fontes e gatilhos (`apps/rowboat/app/projects/[projectId]/workflow/app.tsx:42-55`), persiste no `localStorage` a escolha draft/live e auto-publicação por projeto (`apps/rowboat/app/projects/[projectId]/workflow/app.tsx:42-74`), e atualiza fontes pendentes por polling de sete segundos (`apps/rowboat/app/projects/[projectId]/workflow/app.tsx:131-150`). A navegação é por projeto e tem sidebar recolhível, cujo estado é local (`apps/rowboat/app/projects/layout/nav.tsx:10-58`).

O editor compõe configuração de agente, pipeline, tools, prompt, fontes de dados, Copilot, playground e grafo de agentes (`apps/rowboat/app/projects/[projectId]/workflow/workflow_editor.tsx:9-43`). Ele suporta modos draft/live e reversão ao workflow ao vivo (`apps/rowboat/app/projects/[projectId]/workflow/app.tsx:66-74`, `apps/rowboat/app/projects/[projectId]/workflow/app.tsx:152-170`). Fora do editor, fontes são listadas com nome, tipo (URLs, texto, arquivos locais ou S3), status atualizável e flag `active` (`apps/rowboat/app/projects/[projectId]/sources/components/sources-list.tsx:120-175`); jobs são agrupados por período e exibem status, motivo e data de criação (`apps/rowboat/app/projects/[projectId]/jobs/components/jobs-list.tsx:65-94`, `apps/rowboat/app/projects/[projectId]/jobs/components/jobs-list.tsx:161-235`).

`rowboatx` concentra a navegação lateral em recursos retornados pela API: agentes, configuração e runs (`apps/rowboatx/components/app-sidebar.tsx:89-139`). O estado local da página inclui seleção de agente, `runId`, conversa, texto/resposta/raciocínio correntes, status do stream e artefato selecionado (`apps/rowboatx/app/page.tsx:110-142`). Trocar o agente zera a conversa e o `runId` (`apps/rowboatx/app/page.tsx:699-706`). Um recurso selecionado abre como artefato: agente/configuração pode ser JSON ou Markdown editável; run é somente leitura (`apps/rowboatx/app/page.tsx:547-655`, `apps/rowboatx/app/page.tsx:708-812`).

### O que a UI torna observável além de Markdown num editor

Pela leitura estática, a diferença não é “editar Markdown”: é apresentar e manipular o estado operacional de agentes.

- O console constrói uma representação Mermaid do workflow: nó de entrada, agentes, tools, delegações entre agentes e relações “uses” extraídas das instruções (`apps/rowboat/app/projects/[projectId]/entities/AgentGraphVisualizer.tsx:36-118`). Isso expõe topologia de execução, algo que o conteúdo isolado de um `.md` não contém como estado calculado.

- O Playground oferece chat para testar um workflow, criar novo chat, ligar/desligar mensagens de debug e copiar o transcript como JSON (`apps/rowboat/app/projects/[projectId]/playground/app.tsx:35-57`, `apps/rowboat/app/projects/[projectId]/playground/app.tsx:61-132`). As mensagens do assistente passam por renderização Markdown e podem incluir previews de imagens e latência (`apps/rowboat/app/projects/[projectId]/playground/components/messages.tsx:145-225`).

- A lista de fontes mostra o tipo, estado de processamento e ativação, e a lista de jobs relaciona cada execução a um gatilho/agenda e estado `pending`/`running`/`completed`/`failed` (`apps/rowboat/app/projects/[projectId]/sources/components/sources-list.tsx:131-175`, `apps/rowboat/app/projects/[projectId]/jobs/components/jobs-list.tsx:82-124`, `apps/rowboat/app/projects/[projectId]/jobs/components/jobs-list.tsx:161-235`). São metadados e ciclo de vida de execução, não apenas corpus.

- `rowboatx` representa uma conversa como uma sequência tipada de mensagem, chamada de tool e bloco de reasoning (`apps/rowboatx/app/page.tsx:63-105`). O render inclui input/resultado/status da tool e blocos expansíveis de reasoning, além do texto parcial do assistente durante streaming (`apps/rowboatx/app/page.tsx:847-953`). Isto faz o percurso do agente observável no mesmo histórico em que a resposta aparece.

- A mesma página também abre e salva agentes/configurações como artefatos Markdown/JSON, mas deixa runs somente leitura (`apps/rowboatx/app/page.tsx:547-655`, `apps/rowboatx/app/page.tsx:708-812`). Assim, ela separa artefato configurável de evidência de execução, distinção que não é inerente a um editor de arquivos.

Estas afirmações descrevem componentes, dados e controles presentes no código; não inferem cores, dimensões, responsividade efetiva ou aparência final renderizada.

## 3. Contrato front↔agente

### Console `apps/rowboat`

O contrato principal é SSE em duas etapas: a ação de servidor cria uma turn em cache e devolve `streamId` (`apps/rowboat/app/actions/copilot.actions.ts:25-58`); o browser abre `EventSource` para `/api/copilot-stream-response/:streamId` (`apps/rowboat/app/projects/[projectId]/copilot/use-copilot.tsx:82-137`). A rota consome o gerador do controller e emite eventos SSE `message`, `tool-call`, `tool-result` e, ao fim, `done` (`apps/rowboat/app/api/copilot-stream-response/[streamId]/route.ts:17-54`). O hook concatena os fragmentos de texto, mantém `loading`, e expõe que uma tool está ativa com a query associada (`apps/rowboat/app/projects/[projectId]/copilot/use-copilot.tsx:35-40`, `apps/rowboat/app/projects/[projectId]/copilot/use-copilot.tsx:98-127`).

O Playground aplica o mesmo padrão para a execução do workflow: cria uma `Conversation` uma vez, cria uma cached turn contendo apenas a última mensagem e assina `/api/stream-response/:key` (`apps/rowboat/app/projects/[projectId]/playground/components/chat.tsx:37-50`, `apps/rowboat/app/projects/[projectId]/playground/components/chat.tsx:214-249`; `apps/rowboat/app/actions/playground-chat.actions.ts:11-53`). Durante o stream, atualiza `optimisticMessages`; no evento `done`, grava atomically o output completo como fonte de verdade; em erro, restaura o último estado confirmado (`apps/rowboat/app/projects/[projectId]/playground/components/chat.tsx:263-315`). A rota SSE correspondente encaminha cada `TurnEvent` do controller (`apps/rowboat/app/api/stream-response/[streamId]/route.ts:19-52`).

A API pública `POST /api/v1/:projectId/chat` também aceita `conversationId`, `messages`, `mockTools` e `stream`; com `stream: true`, entrega o mesmo formato SSE, e sem ele devolve JSON com `conversationId` e `turn` (`apps/rowboat/app/api/v1/[projectId]/chat/route.ts:18-82`). A continuidade de sessão é, portanto, a `conversationId` persistida/reenviada pelo cliente, não um histórico mantido apenas na página.

### `apps/rowboatx`

O cliente alternativo estabelece uma única assinatura `EventSource('/api/stream')` e trata eventos de execução publicados pelo backend (`apps/rowboatx/app/page.tsx:252-296`). Para uma conversa nova, cria `POST /runs/new` com `agentId`; para cada mensagem, faz `POST /runs/:runId/messages/new` (`apps/rowboatx/app/page.tsx:492-545`). No servidor `apps/cli`, o endpoint de stream assina o bus e retransmite todos os eventos como SSE, enquanto há endpoints para mensagem, autorização de tool, resposta a pedido humano e parada do run (`apps/cli/src/server.ts:21-129`, `apps/cli/src/server.ts:131-169`).

Os passos intermediários são deliberadamente expostos: o reducer local interpreta `reasoning-delta`, `text-delta`, `tool-call`, `tool-invocation` e `tool-result`, mantendo estado e resultado por chamada (`apps/rowboatx/app/page.tsx:298-489`). A renderização ordenada mostra mensagens, entrada/saída/status de tools e blocos de reasoning, inclusive os que ainda estão em streaming (`apps/rowboatx/app/page.tsx:847-953`). Esse comportamento é verificável no cliente; não foi executado neste levantamento.

## 4. CLI e SDK

O pacote Node instala o executável `rowboatx` (`apps/cli/package.json:6-18`). A superfície implementada e verificável inclui um servidor Hono com OpenAPI e SSE, endpoints de mensagem/run, autorizações de tool e respostas humanas (`apps/cli/src/server.ts:21-186`), além de uma TUI Ink que aponta por padrão para `http://127.0.0.1:3000` ou `ROWBOATX_SERVER_URL` (`apps/cli/src/tui/index.tsx:1-8`). Há rotinas de configuração interativa de provider/modelo, com opções OpenAI, Anthropic, Google, Ollama, OpenRouter e compatível com OpenAI (`apps/cli/src/app.ts:197-232`).

Importante para delimitar a superfície: a função de chat `app()` em `apps/cli/src/app.ts` inicia com `throw new Error("Not implemented")`; a implementação interativa abaixo está comentada (`apps/cli/src/app.ts:38-152`). Assim, não é correto afirmar que esse caminho de CLI executa conversas neste snapshot sem rodá-lo; o servidor/TUI e os módulos de runs existem no código, mas o entrypoint de chat mostrado não está ativo.

O SDK Python é independente da CLI e fala com a API web legada. `Client(host, projectId, apiKey)` constrói `host/api/v1/{projectId}/chat`, envia `Authorization: Bearer`, e expõe `run_turn()` síncrono via `requests.post` (`apps/python-sdk/src/rowboat/client.py:10-50`). O contrato Python modela mensagens de sistema/usuário/assistente/tool, tool calls, `conversationId`, `mockTools` e o `turn.output` retornado (`apps/python-sdk/src/rowboat/schema.py:4-58`). Para continuar uma conversa sem UI, o chamador reenvia o `conversationId` recebido na turn anterior (`apps/python-sdk/src/rowboat/client.py:59-73`).

Logo, convivem dois planos não-visuais no snapshot: a família `apps/cli`/`rowboatx` para runs locais e streaming via Hono, e o SDK Python para a API HTTP por projeto do console `apps/rowboat`; os caminhos/base URLs e schemas citados não são os mesmos (`apps/cli/src/server.ts:21-186`, `apps/python-sdk/src/rowboat/client.py:10-35`).

## 5. Armazenamento

O Compose da aplicação web provisiona MongoDB, Redis, Qdrant e um volume de uploads local (`docker-compose.yml:3-10`, `docker-compose.yml:217-230`, `docker-compose.yml:252-268`). Mongo é persistido em `./data/mongo`; Qdrant em `./data/qdrant`; uploads são um bind mount de `./data/uploads` para `/app/uploads` (`docker-compose.yml:3-10`, `docker-compose.yml:65-66`, `docker-compose.yml:223-224`, `docker-compose.yml:262-263`). O Dockerfile de Qdrant apenas parte de `qdrant/qdrant:latest` e acrescenta `curl` para o healthcheck (`Dockerfile.qdrant:1-3`).

No `apps/rowboat`, Mongo contém ao menos `chats`, `chat_messages`, configurações Twilio e chamadas inbound (`apps/rowboat/app/lib/mongodb.ts:6-12`); Redis é instanciado a partir de `REDIS_URL` (`apps/rowboat/app/lib/redis.ts:1-3`); e Qdrant é um cliente HTTP configurado por `QDRANT_URL`/`QDRANT_API_KEY` (`apps/rowboat/app/lib/qdrant.ts:1-7`).

**Vetores: RAG de documentos, não a memória pessoal de `Agent Notes`.** O setup cria a coleção Qdrant `embeddings` com dimensão configurável (default 1536) e distância `Dot` (`apps/rowboat/app/scripts/setup_qdrant.ts:4-17`). O worker RAG divide documentos em chunks de 1024 com sobreposição 20, gera embeddings e persiste pontos com `projectId`, `sourceId`, `docId`, `content`, `title` e `name`; depois grava o conteúdo Markdown e status `ready` no documento de fonte (`apps/rowboat/app/scripts/rag-worker.ts:41-45`, `apps/rowboat/app/scripts/rag-worker.ts:136-176`). Ele repete a mesma operação para URLs raspadas e texto, e remove os vetores filtrando pelos três IDs quando a fonte/documento é apagada (`apps/rowboat/app/scripts/rag-worker.ts:179-245`, `apps/rowboat/app/scripts/rag-worker.ts:248-335`).

Na resposta, a tool RAG calcula embedding da pergunta, consulta `embeddings` filtrando `projectId` e fontes ativas solicitadas, e opcionalmente busca o conteúdo integral do documento no repositório Mongo (`apps/rowboat/src/application/lib/agents-runtime/agent-tools.ts:159-267`). O schema `DataSourceDoc` confirma que os documentos têm fonte, projeto, versão, status, conteúdo, tentativas/erro e origem URL/arquivo/texto (`apps/rowboat/src/entities/models/data-source-doc.ts:3-43`).

Em contraste, a memória pessoal da seção 1 é gravada sob `WorkDir/knowledge/Agent Notes` e carregada com leitura de arquivos no prompt (`apps/x/packages/core/src/runtime/tools/domains/memory.ts:19-27`, `apps/x/packages/core/src/runtime/assembly/workspace-context.ts:34-84`). O código analisado não cruza esse diretório com `qdrantClient`; portanto o papel demonstrado de Qdrant é RAG de data sources do console web, não a recuperação de `Agent Notes`.

## Decisões de design identificadas

| Decisão | Evidência | Trade-off aparente |
| --- | --- | --- |
| Memória pessoal em Markdown local, distinta do índice vetorial | `save-to-memory` faz append em `knowledge/Agent Notes/inbox.md`; o contexto é carregado de `user.md`/`preferences.md`. `apps/x/packages/core/src/runtime/tools/domains/memory.ts:13-33`; `apps/x/packages/core/src/runtime/assembly/workspace-context.ts:34-84` | Inspeção e edição humana simples, com custo de seleção/curadoria por LLM e sem busca semântica demonstrada para essa memória. |
| Curadoria assíncrona separa captura de consolidação | Inbox é processada por serviço periódico e só limpa após `runWhenPossible` bem-sucedido. `apps/x/packages/core/src/knowledge/agent_notes.ts:244-303`, `apps/x/packages/core/src/knowledge/agent_notes.ts:343-358` | A resposta pode usar memória já consolidada com menos trabalho síncrono, mas uma nova observação não entra imediatamente no prompt. |
| Carregamento total somente do contexto global; detalhes sob demanda | `user.md` e `preferences.md` entram no prompt; outros arquivos são listados para `file-readText`. `apps/x/packages/core/src/runtime/assembly/workspace-context.ts:34-84` | Mantém o prompt menor e preserva granularidade, mas a recuperação dos detalhes depende de julgamento/tool call do agente. |
| Interfaces de streaming mostram execução, não só resposta final | SSE expõe `tool-call`/`tool-result`; `rowboatx` materializa reasoning/tool/message em itens distintos. `apps/rowboat/app/api/copilot-stream-response/[streamId]/route.ts:17-54`; `apps/rowboatx/app/page.tsx:298-489` | Maior observabilidade para o usuário; acopla UI e protocolo a eventos internos de execução. |
| RAG isolado por projeto e fonte | Pontos Qdrant carregam `projectId`/`sourceId`/`docId`; a consulta filtra projeto e fontes selecionadas. `apps/rowboat/app/scripts/rag-worker.ts:153-169`; `apps/rowboat/src/application/lib/agents-runtime/agent-tools.ts:223-247` | Reduz mistura entre projetos/fontes; exige pipeline de ingestão, chunking e worker separado. |
| Workflow editável/testável com distinção draft/live | A UI seleciona `draftWorkflow` ou `liveWorkflow`, persiste a escolha e permite reverter. `apps/rowboat/app/projects/[projectId]/workflow/app.tsx:42-74`, `apps/rowboat/app/projects/[projectId]/workflow/app.tsx:152-203` | Permite experimentar antes de publicar; aumenta os estados que a interface e o backend precisam reconciliar. |

## UNVERIFIED

- A aparência efetiva (cores, tamanhos, disposição final e responsividade) de qualquer tela não foi verificada: não houve build nem execução, conforme o escopo.
- Não foi executado o desktop `apps/x`; por isso não se confirma quais serviços são inicializados numa instalação normal nem se a memória está habilitada para todos os agentes configuráveis.
- Não foi encontrado, nesta leitura, backend para os endpoints locais consumidos por `apps/rowboatx` (`/api/rowboat/*`) dentro de `apps/rowboatx`; a origem/deploy desses endpoints permanece não verificada.
- Não se afirma que o console `apps/rowboat` e o desktop `apps/x` compartilhem dados, autenticação ou um ciclo de release: ambos coexistem no clone, mas o acoplamento operacional não foi executado nem demonstrado por um arquivo único de composição.
- A afirmação negativa sobre não haver indexação Qdrant de `Agent Notes` é limitada ao código pesquisado neste snapshot; não é uma prova sobre componentes externos, versões posteriores ou configuração de runtime.
