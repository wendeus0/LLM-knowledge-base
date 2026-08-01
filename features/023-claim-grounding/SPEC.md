---
title: QA — verificação de ancoragem por afirmação
epic: qa
status: draft
pr:
---

# QA — Verificação de Ancoragem por Afirmação

## Objetivo

Hoje `kb qa` apresenta uma resposta sem indicar quais afirmações decorrem do contexto recuperado. Depois de gerar a resposta, o comando deve verificar cada afirmação elegível contra esse contexto e informar se está **ancorada**, **contradita** ou **sem apoio**, sem impedir a entrega da resposta.

## Contexto

Este é o estágio de *faithfulness/groundedness*, não de cobertura do corpus ou detecção de lacuna. A medição do protótipo confirmou a composição: o cosseno seleciona as três premissas candidatas e o NLI julga cada par premissa/hipótese. Trocar esses papéis é erro de arquitetura: NLI precisa do par e o retrieval produz a premissa.

O modelo é `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`, escolhido para o corpus técnico em português traduzido. Com janelas deslizantes de 12 sentenças e sobreposição, a preservação de afirmações legítimas foi 72% (mediana de entailment 0,755); com uma sentença, foi 18% (mediana 0,067). Fabricações foram detectadas em 100% das faixas medidas. Em deriva sutil — negação, número trocado ou comparação invertida — o método acertou 5/6; em 12 fabricações injetadas, 12/12. O contra-exemplo decisivo é “o circuit breaker NÃO abre após falhas”: cosseno 0,786, mas contradição NLI 0,998.

## Requisitos funcionais

- [ ] RF-01 [P1]: Dada uma resposta de `kb qa` e o contexto efetivamente enviado ao gerador, quando o verificador estiver disponível, então cada afirmação elegível recebe exatamente um veredito: `ancorada`, `contradita` ou `sem apoio`, acompanhado da melhor evidência curta e das pontuações do julgamento.
- [ ] RF-02 [P1]: Dada uma afirmação elegível, quando ela for verificada, então o sistema compara a hipótese com as três janelas de contexto mais similares; cada janela contém 12 sentenças em janela deslizante com sobreposição.
- [ ] RF-03 [P1]: Dada uma resposta com mais afirmações do que o orçamento permite, quando o limite padrão de 24 julgamentos de pares for atingido, então apenas as primeiras oito afirmações elegíveis são verificadas e o resultado informa quantas ficaram sem verificação por limite, sem atribuir-lhes um dos três vereditos.
- [ ] RF-04 [P1]: Dado que o serviço NLI está indisponível, responde com erro ou retorna payload inválido, quando `kb qa` for executado, então a resposta normal continua disponível e o terminal recebe um único aviso em stderr de que a verificação foi degradada.
- [ ] RF-05 [P1]: Dado um resultado de verificação disponível, quando a saída humana do CLI for usada, então ela mostra após a resposta um bloco por afirmação; quando `--json` for usado, então stdout contém somente um documento JSON estável com `answer`, `grounding` e, quando aplicável, `saved_path`; quando `--file-back` for usado, então o arquivo em `outputs/` inclui a seção `## Verificação de ancoragem da resposta` com os mesmos vereditos.
- [ ] RF-06 [P2]: Dado que a verificação encontra `contradita` ou `sem apoio`, quando a resposta é exibida ou arquivada, então o resultado é apresentado como aviso/anotação e nunca bloqueia, remove nem reescreve a resposta.
- [ ] RF-07 [P2]: Dado que o usuário não deseja pagar o custo da verificação, quando usar `--no-grounding`, então `kb qa` preserva o comportamento anterior e não tenta contatar o serviço NLI.

## Requisitos técnicos

- RT-01: O cliente principal do `kb` não adiciona `torch`, `transformers`, `sentencepiece` ou pesos NLI ao `pyproject.toml`. O NLI roda em serviço HTTP local separado, configurável por `KB_GROUNDING_BASE_URL` e `KB_GROUNDING_MODEL`, com padrão em loopback; a engine usa somente o cliente HTTP leve já compatível com o padrão de embeddings.
- RT-02: O contrato local expõe descoberta em `GET /v1/models` e classificação em `POST /v1/nli`, recebendo o modelo e pares `premise`/`hypothesis` e devolvendo, na mesma ordem, probabilidades para `entailment`, `contradiction` e `neutral`. O serviço deve estar limitado a loopback; não é endpoint público.
- RT-03: O orçamento padrão é 24 julgamentos NLI por resposta (três candidatas por no máximo oito afirmações). Agrupar pares em uma requisição HTTP é permitido, mas não altera a contagem de julgamentos do orçamento. `KB_GROUNDING_MAX_PAIRS` pode reduzi-lo ou ampliá-lo; valor não múltiplo de três é arredondado para baixo.
- RT-04: O veredito de uma afirmação é `ancorada` quando o maior entailment domina os outros rótulos nas três candidatas, `contradita` quando alguma candidata tem contradição acima de 0,5 e não houve entailment dominante, e `sem apoio` nos demais casos.
- RT-05: Falha do serviço, timeout, modelo ausente, resposta malformada, contexto vazio e resposta sem afirmações elegíveis são caminhos degradáveis; nenhuma dessas condições altera o texto da resposta de QA nem produz erro de comando.
- RT-06: O resultado é uma anotação efêmera da execução e do file-back; não cria claim, audit event, índice nem escrita adicional em `kb_state/`.

## Mudanças de API/CLI

- `kb qa` verifica ancoragem por padrão quando o serviço local está disponível e imprime o bloco de verificação depois da resposta.
- `kb qa --no-grounding` desliga essa etapa explicitamente.
- `kb qa --json` introduz saída estruturada exclusiva em stdout: `answer` (string), `grounding` (objeto com estado, contagens, afirmações verificadas e afirmações omitidas por limite) e `saved_path` (string ou `null`). Progresso e avisos permanecem em stderr.
- `kb qa --file-back` mantém o local padrão em `outputs/`; acrescenta a seção de verificação ao artefato. `--to-wiki` continua compatível e recebe a mesma anotação no artigo gerado.
- Novas variáveis: `KB_GROUNDING_BASE_URL`, `KB_GROUNDING_MODEL`, `KB_GROUNDING_API_KEY`, `KB_GROUNDING_TIMEOUT` e `KB_GROUNDING_MAX_PAIRS`.

## Testes

- Unit: extração de afirmações, janelas de 12 sentenças sobrepostas, seleção das três candidatas, mapeamento dos três vereditos, teto de 24 pares, arredondamento do limite, payload HTTP e falhas/malformações degradáveis.
- Integration: `kb qa` com clientes de geração, embedding e NLI simulados; verifica bloco humano, JSON sem texto extra em stdout, `--no-grounding`, file-back anotado e resposta preservada quando o NLI falha.
- Manual: com o servidor local e o modelo medido, repetir os seis pares de deriva sutil e as 12 fabricações do protótipo; registrar a taxa observada e a latência, sem promover os números atuais a garantia de produção.

## Dados de contexto

| Chave | Valor |
|---|---|
| Estimativa | 1–2 dias |
| Bloqueador | não; sem o servidor a feature degrada |
| Risco | alto — há 28% de falso alarme medido e novo contrato HTTP local |
| MVP | RF-01 a RF-05 |

## Dependências

- Feature 014 (`embed_server`) como padrão de probe HTTP local e aviso em stderr.
- Servidor NLI local provisionado fora das dependências do pacote `kb`.
- O reagrupamento por tema do ticket 006 não é dependência: detecção de lacuna permanece explicitamente fora desta feature.

## ADR

- Necessária? não nesta etapa; a decisão segue o gatilho de revisão do ADR-0018 e reutiliza o padrão local já adotado para embeddings. Criar ADR apenas se o contrato do serviço passar a ser remoto/público ou se introduzir nova persistência.

## Critérios de aceite

- [ ] AC-01: RF-01 e RF-02 demonstrados por teste com uma afirmação ancorada, uma contradita e uma sem apoio; o caso de negação não pode passar apenas pelo cosseno.
- [ ] AC-02: RF-03 demonstrado com nove afirmações elegíveis: no máximo oito são julgadas, no máximo 24 pares são enviados e uma fica declarada como não verificada por limite.
- [ ] AC-03: RF-04 demonstrado com timeout e payload NLI inválido: a mesma resposta de geração é retornada e há somente um aviso em stderr.
- [ ] AC-04: RF-05 demonstrado pela CLI: modo humano mostra o resultado por afirmação, `--json` é parseável e o file-back contém a anotação.
- [ ] AC-05: RF-06 e RF-07 demonstrados: um veredito negativo não impede resposta/arquivo e `--no-grounding` não faz chamada NLI.

## Métricas de sucesso

- Não bloquear nenhuma resposta por veredito de grounding durante o MVP.
- No conjunto manual atual, manter pelo menos a evidência de viabilidade medida: 5/6 derivas sutis sinalizadas e 12/12 fabricações sinalizadas; reportar também a preservação observada, sabendo que a linha de base é 72% e não é meta de aceite.
- Nunca exceder 24 julgamentos NLI por resposta com a configuração padrão.

## Casos de erro

- Serviço NLI inacessível, timeout ou modelo não anunciado → resposta normal; um aviso em stderr e `grounding.status: "degraded"` no modo JSON.
- Resposta NLI incompleta, fora de ordem ou sem as três probabilidades → descartar a verificação daquela execução, preservar a resposta e avisar em stderr.
- Contexto vazio, ou nenhuma afirmação com tamanho mínimo → resposta normal com `grounding.status: "skipped"`, sem inventar vereditos.
- Mais afirmações que o orçamento → verificar somente o prefixo que cabe, declarar a contagem omitida e não tratar omissão como `sem apoio`.

## Fora de escopo

- Detectar se o corpus cobre a pergunta, abster-se de responder ou sugerir novas fontes (estágio de lacuna, dependente do ticket 006).
- Consistência entre múltiplas gerações, verbalização de confiança, rerank ou alteração do retrieval.
- Treinar/calibrar um NLI de domínio, converter o modelo para ONNX ou corrigir os limiares com conjunto de validação separado.
- Bloquear, editar ou regenerar respostas com base em um veredito negativo.

## Questões abertas

Nenhuma pendente.

**Resolvida (2026-08-01):** o `ADR-0018` e o `ESTADO-DA-ARTE-GROUNDING.md` não estavam visíveis no checkout porque vivem na branch do PR #59, ainda não mergeado — esta feature saiu de `main`. Não há trabalho de restauração: os arquivos chegam com aquele merge. O conteúdo usado na redação, recuperado de `b67977a` e `4cba94d`, é o mesmo.

## Notas

Limitações declaradas da medição: limiares ajustados nos mesmos dados de avaliação, sem conjunto de validação separado; apenas oito pares artigo↔fonte, quase todos de IA/LLM; e conjuntos negativos pequenos. A taxa de preservação de 72% implica 28% de falso alarme, suficiente para avisar e investigar, não para bloquear a resposta.
