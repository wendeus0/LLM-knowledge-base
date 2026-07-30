---
title: Provider dedicado para o rerank e preflight de lote
epic: search
status: done
pr:
---

# Provider dedicado para o rerank e preflight de lote

## Objetivo

O rerank é a única etapa do pipeline que exige **saída estruturada longa** do LLM ("ordene estes 20 índices"), e é exatamente onde a quantização pesa: medido na 020, o `bonsai-27b-1bit` local devolveu os 20 índices pedidos em apenas 20% das chamadas, com cobertura média de 75% e omissão severa em 26%.

`compile`, `qa` e `heal` funcionam bem com esse modelo — a tarefa deles é prosa curta. Trocar o modelo global para consertar o rerank penalizaria três etapas que não têm o problema.

O sistema deve permitir configurar um provider **só para o rerank**, e deve abortar um lote de medição quando esse provider não responde — em vez de degradar silenciosamente e produzir um número que parece válido.

## Requisitos funcionais

- [x] RF-01: `KB_RERANK_MODEL` e `KB_RERANK_BASE_URL` configuram o provider do rerank; ausentes, cai para o modelo e endpoint gerais
- [x] RF-02: trocar o modelo de rerank invalida o cache — respostas de modelos diferentes não se misturam
- [x] RF-03: `kb bench --rerank N` faz preflight do provider antes do lote e aborta com mensagem explícita se ele não responder
- [x] RF-04: preflight não roda quando o rerank está desligado — sem `--rerank`, nenhuma chamada é feita
- [x] RF-05: `KB_RERANK_API_KEY` para providers que exigem chave distinta

## Requisitos técnicos

- `_call_llm` é a fronteira única de rede do rerank; com endpoint dedicado, instancia cliente próprio, senão delega a `kb.client.chat`
- Chave de cache inclui o modelo de rerank resolvido, não o `KB_MODEL`
- Preflight é uma chamada mínima ("responda apenas: 1"), barata o bastante para não pesar
- Nenhuma chamada de rede em teste

## Mudanças de API/CLI

- Novas env vars: `KB_RERANK_MODEL`, `KB_RERANK_BASE_URL`, `KB_RERANK_API_KEY`
- `kb bench --rerank N` passa a falhar cedo quando o provider está fora

## Testes

- Unit: resolução do modelo e endpoint (com e sem dedicado); invalidação de cache ao trocar modelo; preflight abortando com provider morto, prosseguindo com provider vivo, e não sendo chamado sem `--rerank`
- Manual: rerank apontado para o Ollama da VM via tailnet, medido no golden de 152 casos

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 2–3h |
| Bloqueador | não |
| Risk | baixa (aditivo; sem as env vars o comportamento é o anterior) |

## Dependências

- 020 (rerank), 016/019 (bench e golden para medir)

## Notas

**Motivação do preflight — incidente registrado:** uma queda de energia derrubou o túnel SSH para a VM no meio de uma medição. As 152 chamadas falharam, cada uma degradou corretamente para a ordem original, e o bench reportou `recall@5 = 0,414` — idêntico à baseline sem rerank. Dezoito minutos para produzir um número que parecia válido e não media nada. O preflight cobre "provider morto desde o início"; **não cobre "morreu no meio"**, que aconteceu numa segunda medição (65 de 152 falharam) e só foi detectado pelo contador `failed` da instrumentação.

**Fora de escopo:**
- Provider dedicado para expansão de query (a tarefa é curta e o modelo atual dá conta)
- Retry ou failover entre providers
- Verificação contínua durante o lote — hoje só há preflight e o contador de falhas no fim

**Open questions:**
- (nenhuma)
