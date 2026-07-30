---
title: Autostart e diagnóstico do servidor de embeddings local
epic: search
status: done
pr:
---

# Autostart e diagnóstico do servidor de embeddings local

## Objetivo

Hoje, com o servidor de embeddings parado, `kb search`/`kb qa` degradam para o retrieval lexical **em silêncio** — o comportamento é correto como fallback (RF-05 da 012) e ruim como padrão: o usuário perde o canal semântico sem nenhum sinal, e uma sessão inteira pode transcorrer com recuperação pior sem que ninguém perceba.

O sistema deve (a) detectar o estado do servidor, (b) opcionalmente subi-lo por conta própria quando o runtime local estiver disponível, e (c) **tornar visível** toda degradação. O fallback continua existindo; o que deixa de existir é o silêncio.

Fatia 1 da Fase 1 do roadmap revisado (2026-07-28). Complementa a 012, que entregou o canal semântico com degradação progressiva.

Verificação viva (2026-07-28): LM Studio instalado com CLI em `~/.lmstudio/bin/lms`; servidor desligado por padrão (`autoStartOnLaunch: false`); modelos `text-embedding-nomic-embed-text-v2-moe` e `-v1.5` presentes; endpoint OpenAI-compat em `http://localhost:1234/v1`.

## Requisitos funcionais

- [x] RF-01: `kb index status` reporta o estado do servidor de embeddings (acessível / inacessível) além do estado do índice, incluindo o endpoint consultado
- [x] RF-02: `kb index status` reporta se o modelo configurado está entre os modelos servidos pelo endpoint; modelo ausente é sinalizado distintamente de servidor inacessível
- [x] RF-03: com `KB_EMBED_AUTOSTART` ativo e servidor inacessível, o kb tenta subir o runtime local uma vez antes de desistir, aguardando o endpoint responder até um teto de tempo
- [x] RF-04: com `KB_EMBED_AUTOSTART` inativo (padrão), nenhum processo é iniciado — o comportamento é apenas detectar e reportar
- [x] RF-05: degradação para lexical em `kb search`/`kb qa` emite aviso visível uma vez por execução, indicando a causa (servidor inacessível, modelo divergente, índice ausente) e a ação corretiva
- [x] RF-06: `kb index build` com servidor inacessível falha com mensagem que nomeia o runtime real, o endpoint e o comando para subi-lo — hoje a mensagem cita Ollama e `ollama serve`, que não é o runtime em uso
- [x] RF-07: comando de autostart configurável por env, com default para o runtime detectado; ausência do binário é reportada sem quebrar a execução

## Requisitos técnicos

- Probe de disponibilidade contra `/v1/models` do endpoint configurado (`KB_EMBED_BASE_URL`), com timeout curto — nunca bloqueia a busca por mais que esse teto
- O probe é a **única** fronteira de rede nova; reusa o cliente já disponível, sem dependência adicional
- Autostart executa comando externo (`lms server start` por default), com timeout próprio e no máximo uma tentativa por execução do processo
- Nenhuma chamada de rede em teste: probe e autostart são injetáveis/monkeypatcháveis, como `embed_texts` já é hoje
- O aviso de degradação sai por `stderr`, para não contaminar saídas parseáveis
- Estado do servidor não é cacheado em disco — é informação de momento

## Mudanças de API/CLI

- `kb index status`: passa a exibir bloco de servidor (endpoint, alcançável, modelo presente)
- Novas env vars: `KB_EMBED_AUTOSTART` (default desligado), `KB_EMBED_AUTOSTART_CMD` (default `lms server start`), `KB_EMBED_PROBE_TIMEOUT` (default curto), `KB_EMBED_AUTOSTART_TIMEOUT`
- `kb search`/`kb qa`: sem mudança de interface; ganham o aviso em stderr quando degradam

## Testes

- Unit: probe com endpoint respondendo, recusando conexão e estourando timeout; detecção de modelo presente/ausente na lista retornada; autostart respeitando o flag (não invoca comando quando desligado); autostart com binário ausente; teto de uma tentativa
- Integration (sem rede, probe e runner monkeypatchados): `index status` com servidor acessível e inacessível; `search` degradando com aviso em stderr e resultado lexical idêntico ao atual; `index build` com servidor fora reportando runtime/endpoint/comando corretos
- Manual: com servidor parado e autostart ligado, `kb search` sobe o LM Studio e usa o canal semântico; com autostart desligado, degrada e avisa

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 4–6h |
| Bloqueador | não |
| Risk | baixa (aditivo; caminho padrão não inicia processo algum) |

## Dependências

- Feature 012 entregue (canal semântico e `kb index`)
- Runtime local com endpoint OpenAI-compat; ausência degrada, não bloqueia

## Notas

**Fora de escopo:**
- Escolher ou trocar modelo automaticamente (o usuário configura por env)
- Gerenciar ciclo de vida do servidor além do start (não derruba, não reinicia)
- Suporte a múltiplos runtimes simultâneos ou descoberta automática de porta
- Reindexação automática após o servidor subir (é a 015)

**Casos de erro:**
- Binário de autostart ausente → reporta e segue degradado, sem exceção
- Autostart executa mas endpoint não responde dentro do teto → reporta e segue degradado
- Endpoint responde mas não lista o modelo configurado → sinaliza distintamente; `index build` falha cedo com a lista de modelos disponíveis, em vez de falhar no meio do lote

**Débito adjacente a corrigir no mesmo ciclo** (repo_mode solo, débito visível dentro do escopo):
- `kb/embeddings.py:3,28,99` citam Ollama e `ollama serve`; o runtime real é o endpoint configurado, hoje LM Studio. A SPEC e o REPORT de 012 têm a mesma divergência.

**Open questions:**
- (nenhuma)
