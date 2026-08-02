---
feature: 026-plataforma-de-estudos
title: Plataforma de estudos web
epic: infra
status: ready
created: 2026-08-02
pr:
---

# Plataforma de estudos web

## Objetivo

Hoje o `kb` é consumido principalmente pela CLI e por um leitor externo. A plataforma deve permitir estudar a wiki local no navegador: navegar pelos artigos, perguntar à engine, registrar anotações separadas, criar e revisar flashcards com agenda derivada do SRS.

## Context

O `kb` permanece a engine headless e continua sendo o único responsável pelo corpus compilado em `wiki/`. A plataforma é um segundo produto local, destinado a substituir o Obsidian como leitor privado em localhost; ela não é um editor da wiki.

O ciclo esperado alterna navegação e pergunta. A busca da tela deve preservar a recuperação híbrida do `kb` — RRF de keyword, densidade, BM25 e canal semântico, com rerank quando configurado — pois uma busca própria do front seria regressão funcional.

O identificador público e persistente de um artigo é `rel_slug`, por exemplo `ai/transformers`. A pré-condição F0 é que a resolução de wikilinks também use essa identidade, inclusive onde há stems duplicados no vault.

## Goal

Disponibilizar um ciclo local e verificável de ler um artigo, registrar estudo separado, aceitar somente flashcards ancorados no artigo e revisá-los na data calculada pelo SRS.

## Requisitos funcionais

### F1 — API HTTP da engine

- [ ] RF-01 [P1]: Dado o servidor local em execução, quando o cliente solicitar `GET /health`, então recebe uma resposta HTTP de sucesso que informa a disponibilidade da aplicação sem expor paths locais do corpus.
- [ ] RF-02 [P1]: Dada uma consulta válida, quando o cliente solicitar `GET /search`, então recebe resultados na mesma ordem produzida pela busca híbrida do `kb`, inclusive o rerank quando ele estiver habilitado, e cada resultado identifica o artigo por `rel_slug`.
- [ ] RF-03 [P1]: Dada uma pergunta válida, quando o cliente solicitar `POST /qa`, então recebe exatamente os campos JSON de `kb qa --json`: `answer`, `grounding.status`, `grounding.checked_claims`, `grounding.unverified_due_to_limit`, `grounding.claims` e `saved_path`.
- [ ] RF-04 [P1]: Dado um `rel_slug` válido, quando o cliente solicitar `GET /article/{slug:path}`, então recebe o artigo correspondente e metadados suficientes para apresentá-lo sem revelar o path absoluto ou o objeto `Path` interno.
- [ ] RF-05 [P1]: Dado o corpus configurado, quando o cliente solicitar `GET /stats`, então recebe as métricas agregadas que a engine já expõe para a wiki, sem alterar o corpus ou seu estado.

### F2 — Leitor

- [ ] RF-06 [P1]: Dado um artigo retornado pela plataforma, quando o estudante o abre, então seu Markdown é apresentado como superfície de leitura e cada wikilink resolvido navega para o `rel_slug` correto, inclusive quando existem artigos com mesmo stem em tópicos distintos.
- [ ] RF-07 [P1]: Dado um artigo aberto, quando houver outros artigos que apontam para ele, então o leitor exibe backlinks navegáveis identificados por `rel_slug`.
- [ ] RF-08 [P1]: Dado o leitor, quando o estudante pesquisar ou enviar uma pergunta pela respectiva caixa, então a página apresenta os resultados ou a resposta da API da engine, preservando os avisos de grounding da resposta.
- [ ] RF-09 [P1]: Dado o leitor em qualquer artigo, quando o estudante alternar entre os temas disponíveis, então há tema claro com fundo bege, não branco puro, e tema escuro com acento laranja, ambos com contraste suficiente para leitura longa.
- [ ] RF-10 [P1]: Dado o leitor em tela larga, quando o estudante navega pela trilha, então a sidebar esquerda permanece como navegação primária, mostra progresso e artigos do contexto atual, enquanto o artigo ocupa a superfície de leitura à direita.

### F3 — Notas e destaques

- [ ] RF-11 [P1]: Dado um artigo identificado por `rel_slug`, quando o estudante cria, edita ou remove uma nota, então a alteração é persistida no estado de estudo da plataforma e não modifica o arquivo Markdown do artigo.
- [ ] RF-12 [P1]: Dado um trecho selecionado em um artigo, quando o estudante o destaca, então o destaque é associado ao `rel_slug`, permanece separado do arquivo compilado e é reapresentado na leitura do artigo enquanto sua âncora puder ser localizada.

### F4 — Flashcards

- [ ] RF-13 [P1]: Dado um artigo aberto, quando o estudante pedir geração de flashcards, então a plataforma produz cartões em estado de curadoria, vinculados ao `rel_slug`, sem aceitá-los automaticamente para revisão.
- [ ] RF-14 [P1]: Dado um cartão candidato e o conteúdo do artigo de origem, quando a verificação de grounding concluir `ancorada`, então o estudante pode aceitá-lo para revisão; quando concluir `contradita`, `sem apoio`, `degraded` ou `skipped`, então o cartão não pode ser aceito.
- [ ] RF-15 [P1]: Dado um cartão em curadoria, quando o estudante o aceitar, editar ou descartar, então a decisão fica registrada no estado de estudo e não altera o artigo compilado.

### F5 — Revisão e calendário

- [ ] RF-16 [P1]: Dado um flashcard aceito, quando o estudante registrar uma revisão, então sua próxima data devida é calculada pelo SRS e armazenada no estado de estudo.
- [ ] RF-17 [P1]: Dado o calendário de estudos, quando o estudante o abre, então ele mostra a fila de cartões devidos e suas datas calculadas; o estudante não informa manualmente a data de agendamento.

## Requisitos técnicos

- RT-01: A aplicação HTTP usa FastAPI; as páginas usam Jinja2, htmx e Alpine. JavaScript isolado fica restrito a interações para as quais htmx não seja adequado, como atalhos da revisão.
- RT-02: O servidor aceita conexões apenas em loopback. Não há autenticação, HTTPS nem exposição de rede nesta feature.
- RT-03: Todo identificador de artigo que cruza a fronteira HTTP, de template ou de persistência é `rel_slug`. `Path`, absoluto ou relativo, nunca é serializado nem exposto ao cliente.
- RT-04: `POST /qa` preserva literalmente o formato de saída JSON de `kb/cli.py:492-528`:

  ```json
  {
    "answer": "...",
    "grounding": {
      "status": "verified",
      "checked_claims": 0,
      "unverified_due_to_limit": 0,
      "claims": [
        {"claim": "...", "verdict": "ancorada", "evidence": "...", "scores": {}}
      ]
    },
    "saved_path": null
  }
  ```

  A rota não faz file-back; portanto `saved_path` é `null`. Caso uma extensão futura exponha uma identidade de artigo em vez desse campo, ela usa `rel_slug`, nunca `Path`.
- RT-05: `SensitiveContentError` em qualquer rota que possa alcançar provider externo resulta em HTTP 409 com informação segura para o cliente. O servidor nunca solicita confirmação interativa nem envia conteúdo sensível após esse erro.
- RT-06: Um `slug` contendo tentativa de traversal, path absoluto, normalização que escape da wiki ou formato inválido resulta em HTTP 400; a solicitação não lê arquivos fora de `wiki/`.
- RT-07: A resolução de wikilinks e o cálculo de backlinks constroem um índice por varredura do corpus uma vez por carga ou atualização controlada do corpus. Resolver cada link fazendo nova busca no vault é proibido, pois bloqueia a leitura no vault de 1.040 artigos.
- RT-08: O estado de notas, destaques, flashcards e revisões fica em SQLite próprio da plataforma. Ele não escreve em `wiki/` nem reutiliza os arquivos JSON de `kb_state/` para esses dados.
- RT-09: A geração e a verificação de cartões reutilizam as capacidades de LLM e grounding já existentes na engine; uma indisponibilidade da verificação mantém o cartão em curadoria e impede sua aceitação.
- RT-10: A renderização de Markdown suporta a regra de wikilink do corpus e converte seus destinos para URLs por `rel_slug`; a plataforma não introduz uma segunda busca, índice de relevância ou identidade por stem.

## Mudanças de API/CLI

| Rota | Comportamento público |
| --- | --- |
| `GET /health` | Estado de disponibilidade da aplicação local. |
| `GET /search` | Busca da engine; resultados ordenados pela recuperação do `kb`, identificados por `rel_slug`. |
| `POST /qa` | Pergunta à engine; resposta com o JSON literal de `kb qa --json` descrito em RT-04. |
| `GET /article/{slug:path}` | Artigo identificado por `rel_slug`, seu conteúdo e metadados serializáveis. |
| `GET /stats` | Agregado de métricas já fornecido pela engine. |

Não há mudança de contrato da CLI nesta feature. A API HTTP não oferece rota de escrita de artigo compilado.

## Testes

- Unit: conversão de artigo para `rel_slug`; rejeição de traversal; serialização sem `Path`; montagem do índice único de wikilinks; resolução de duplicate stems; estado e transições de nota, destaque, cartão e revisão; bloqueio de aceitação de grounding não `ancorada`; cálculo de próxima revisão.
- Integration: servidor em loopback com corpus e estado isolados; todas as cinco rotas; equivalência ordenada entre `/search` e a busca da engine; equivalência campo a campo de `/qa` e `kb qa --json`; HTTP 409 para conteúdo sensível; fluxo artigo → nota/destaque → cartão ancorado aceito → revisão → fila devida.
- Manual: abrir artigos reais em ambos os temas, alternar tema, confirmar layout sidebar/artigo, navegar wikilinks e backlinks, pesquisar, perguntar, revisar um cartão e verificar que nenhum arquivo de `wiki/` mudou.

## Dados de contexto

| Chave | Valor |
| --- | --- |
| Estimativa | Não estimada nesta SPEC; F1–F5 excedem uma entrega pequena e devem ser planejadas em fatias. |
| Bloqueador | F0 — resolução de identidade por `rel_slug` para stems duplicados. |
| Risco | Alto — novo contrato HTTP, persistência independente, UI com estado e agendamento. |
| MVP | Todos os requisitos e critérios de aceite P1. |

## Dependências

- F0 de identidade única por `rel_slug`, incluindo a resolução em grafo, lint e archive.
- Busca híbrida e rerank já disponíveis na engine.
- `kb/grounding.py` disponível para verificar cartões.
- Serviço de grounding local, quando disponível; sem ele a criação de cartões continua possível, mas a aceitação permanece bloqueada.
- Biblioteca `fsrs` para o agendamento de revisões.

## ADR

**Escrita:** [ADR-0019](../../docs/adr/0019-study-platform-as-second-product-over-headless-engine.md) — a plataforma é segundo produto sobre a engine headless; corpus é território da engine e estado de estudo é território da plataforma; `rel_slug` é a identidade pública.

## Acceptance criteria

- [ ] AC-01 [P1] Dado o servidor em loopback, quando `health`, `search`, `qa`, `article` e `stats` forem chamados com entradas válidas, então cada rota retorna resposta HTTP de sucesso e nenhum payload contém objeto `Path`, path absoluto ou identificador por stem.
- [ ] AC-02 [P1] Dada a mesma consulta e a mesma configuração de rerank, quando ela for executada pela API e pela busca da engine, então os resultados devolvidos têm a mesma ordenação por `rel_slug`.
- [ ] AC-03 [P1] Dada uma resposta de QA, quando ela for solicitada pela API e pela CLI em JSON, então os campos e a estrutura de `answer`, `grounding` e `saved_path` são equivalentes; na API, `saved_path` é `null`.
- [ ] AC-04 [P1] Dado conteúdo classificado como sensível, quando uma rota que usa provider for chamada sem autorização explícita, então a resposta é HTTP 409 e não há prompt interativo; dado um slug malicioso, quando `/article/{slug}` for chamado, então a resposta é HTTP 400 sem leitura fora da wiki.
- [ ] AC-05 [P1] Dado um vault com stems duplicados e wikilinks, quando os artigos forem renderizados, então cada link e backlink leva ao `rel_slug` correto e o índice é construído sem uma varredura por link.
- [ ] AC-06 [P1] Dado um artigo, quando o estudante criar nota ou destaque, então ambos reaparecem no artigo e uma comparação do arquivo compilado antes e depois não mostra modificação.
- [ ] AC-07 [P1] Dado um cartão gerado, quando o grounding for `sem apoio`, `contradita`, `degraded` ou `skipped`, então a interface não oferece aceitação; quando for `ancorada`, então o estudante pode aceitar, editar ou descartar o cartão.
- [ ] AC-08 [P1] Dado um cartão aceito, quando o estudante registrar uma revisão e abrir o calendário, então a data calculada pelo SRS aparece na fila devida sem campo para definir manualmente seu agendamento.
- [ ] AC-09 [P1] Dado o leitor em tema claro ou escuro, quando o estudante abre um artigo em tela larga, então vê respectivamente fundo bege ou acento laranja e a sidebar de trilha com progresso à esquerda do conteúdo.

## Success criteria

- Todos os critérios P1 estão entregues e testados; este é o limiar de MVP.
- Um fluxo integral demonstrável fecha sem editar a wiki: abrir artigo, pesquisar ou perguntar, gravar nota ou destaque, gerar e aceitar cartão ancorado, revisar e encontrá-lo na fila calculada.
- Os testes de contrato registram zero serializações de `Path` e zero acessos de `/article/{slug}` fora da wiki para os cenários maliciosos cobertos.
- A equivalência de busca e de JSON de QA é demonstrada contra a engine, sem substituição da recuperação por busca do front.

## Casos de erro

- Conteúdo sensível em busca, pergunta ou geração de cartões → HTTP 409, sem confirmação interativa e sem envio posterior ao provider.
- `slug` com traversal, path absoluto ou formato inválido → HTTP 400, sem expor se existe arquivo fora da wiki.
- Artigo inexistente com slug válido → HTTP 404, sem revelar paths internos.
- Índice de wikilinks indisponível ou inconsistente → o leitor informa falha de navegação e não direciona o usuário para artigo de mesmo stem incorreto.
- Serviço de grounding inacessível, timeout ou payload inválido → cartão permanece em curadoria, não pode ser aceito e o usuário recebe estado de verificação indisponível.
- Serviço de agendamento indisponível ou dado de revisão inválido → a revisão não é confirmada nem recebe data inventada; o cartão conserva a última agenda válida.
- Banco de estudo indisponível → notas, destaques, decisões de curadoria e revisões não são confirmados como salvos; o artigo continua legível e intacto.

## Non-goals

- Roadmap e cobertura curricular por trilha; pertencem à fase 2.
- Autenticação, contas, HTTPS, deploy em VM, acesso remoto ou sincronização multiusuário.
- Aplicativo nativo, Electron ou substituição da plataforma por frontend OSS/SSG.
- Edição, criação ou remoção do artigo Markdown compilado, inclusive por notas, destaques, cartões ou revisão.
- Busca client-side, índice de relevância próprio do front ou alteração dos algoritmos de retrieval e rerank do `kb`.
- Grafo de wikilinks como navegação primária.

## Open questions

Nenhuma pendente. As duas levantadas na redação foram resolvidas em 2026-08-02:

**Destaque cuja âncora sumiu após `compile`/`heal`.** O destaque guarda o texto citado e um deslocamento aproximado, não uma posição fixa. Ao reabrir o artigo, a localização é por busca do texto citado; se ele não existe mais, o destaque **não é apagado nem reposicionado por adivinhação** — passa a `órfão`, some da superfície de leitura e aparece numa lista própria com o trecho original e o artigo de origem. Apagar silenciosamente perderia trabalho do estudante; reposicionar por aproximação inventaria uma âncora que ninguém escolheu. A mesma regra vale para o destaque cujo artigo inteiro deixou de existir.

**Escala de revisão.** Os quatro ratings que a `fsrs` oferece — `Again`, `Hard`, `Good`, `Easy` — mapeados 1:1, sem escala intermediária própria. Rótulos em português na interface (`De novo`, `Difícil`, `Bom`, `Fácil`) e atalhos `1`–`4`. Inventar escala própria exigiria remapear para a da biblioteca de qualquer forma, e o remapeamento é onde o agendamento se distorce sem que ninguém perceba.

## Notas

Esta SPEC documenta F1–F5 porque elas formam o ciclo de estudo solicitado, mas não recomenda implementá-las como uma única entrega. O corte recomendado para o primeiro plano executável é F1 + F2, precedido por F0; F3–F5 seguem em SPECs filhas ou em etapas explícitas após o leitor estar validado. A dependência de referência visual pendente no plano foi superada por `DIRECAO-VISUAL.md`, que fixa a direção necessária para F2.
