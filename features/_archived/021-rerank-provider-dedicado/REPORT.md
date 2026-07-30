# REPORT — 021-rerank-provider-dedicado

**Data:** 2026-07-29
**Status:** `DONE_WITH_CONCERNS` — infra entregue; o experimento de modelo produziu resultado **negativo** e um achado inesperado.
**Ciclo:** RED (4 testes de provider + 3 de preflight) → GREEN → firewall da VM → medição em 152 casos

## O que mudou

- **`kb/rerank.py`:** `rerank_model()` / `rerank_base_url()` resolvem provider dedicado por `KB_RERANK_MODEL` / `KB_RERANK_BASE_URL` / `KB_RERANK_API_KEY`, caindo para o geral quando ausentes. `_call_llm` passa a ser a fronteira única de rede. Chave de cache usa o modelo de rerank resolvido — trocar de modelo invalida naturalmente.
- **`preflight()`:** chamada mínima ao provider, executada por `run_bench` antes do lote quando `--rerank` está ativo.
- **VM `g0dw1n`:** `hermes-host-firewall.sh` fazia `iptables -F INPUT` e recriava as regras sem a tailnet, descartando o que o `/etc/iptables/iptables.rules` já declarava. Duas linhas acrescentadas (escopo mínimo: `tailscale0`, TCP, portas 22 e 11434), backup em `.bak-20260729`, inserção idempotente.

## Validação

- 7 testes novos, nascidos RED. Suíte: **576 passed**, ruff limpo.
- Acesso direto Mac → VM: **0,3s** de latência, sem túnel.

### Experimento: trocar o modelo de rerank

| Configuração | recall@5 | MRR | cobertura | omissão severa | índices inválidos |
|---|---|---|---|---|---|
| sem rerank | 0,414 | 0,242 | — | — | — |
| **`bonsai-27b-1bit` (local)** | **0,467** | **0,299** | 75% | 26% | **0** |
| `granite4:tiny-h` (VM) | 0,342 | 0,215 | 90% | 4% | **36** |

**O `granite4` ficou abaixo de não fazer rerank nenhum.** Melhorou tudo que eu media como problema — cobertura de 75% para 90%, omissão severa de 26% para 4% — e piorou o resultado.

A variável que explica é a última coluna. O bonsai **triava**: devolvia poucos índices, todos válidos. O granite4 **preenche**: devolve quase todos, 36 deles inventados (posições fora da faixa de 20). Cada índice alucinado ocupa a vaga de um candidato real.

**Achado:** o modo de falha domina a taxa de falha. Cobertura alta com índices errados é pior que triagem parcial confiável — e pior que não reordenar.

## Limitação metodológica declarada

**O experimento não isolou a variável pretendida.** A intenção era testar "compressão a 1 bit degrada saída estruturada"; na prática trocaram-se três coisas ao mesmo tempo: quantização, tamanho do modelo (27B → 4,2 GB) e provider. O resultado mede "modelo pequeno bem quantizado perde de modelo grande muito quantizado nesta tarefa", que é diferente da pergunta original.

Isolar compressão exigiria um modelo de 27–35B menos comprimido. O `ornith-1.0:35b` seria o candidato, mas ocupa 19,7 GB numa VM de 15 GB — carregá-lo joga a máquina em swap e trava até chamadas triviais (medido: `qwen2.5:3b` estourou 2 min). **A infra disponível não permite o teste limpo.**

## Riscos / dívida

- **A VM não é dedicada:** hospeda os CI runners de `visep` e `infinityfit` e tem 15 GB de RAM. Rerank em lote compete com esses containers.
- **Preflight cobre "morto no início", não "morreu no meio".** Uma medição perdeu 65 de 152 chamadas quando o túnel caiu no meio do lote; só o contador `failed` da instrumentação revelou. Verificação contínua ficou fora de escopo.
- O modelo de rerank permanece o `bonsai-27b-1bit` local, por ser o melhor medido — apesar de ser o mais lento (20s/query contra 1,4s).

## Próximos passos

1. **Restringir a saída em vez de trocar o modelo:** pedir os N mais relevantes (não ordenar 20) reduz o espaço de alucinação de índice, que é o defeito dominante. Ataca a causa medida.
2. Testar `deephat-v1:7b` e `lfm2.5` só se houver hipótese nova — trocar modelo às cegas já produziu um resultado negativo.
3. Se o teste de compressão importar, precisa de máquina com RAM para um 35B.
