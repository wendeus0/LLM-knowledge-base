# Pesquisa — otimização de inferência AMD/ROCm em `g0dw1n`

**Data:** 2026-07-31  
**Escopo:** pesquisa e probes somente de leitura; nenhuma configuração, processo, modelo ou arquivo do vault foi alterado.

## Resumo executivo

Para aumentar **capacidade de contexto** sem trocar modelo, a mudança de maior alavancagem é habilitar, em uma janela controlada, o cache KV global `q4_0` do Ollama **junto com** Flash Attention. O Ollama documenta que `q4_0` usa aproximadamente um quarto da memória de KV em `f16`, e que cache KV quantizado exige Flash Attention. A matriz do `llama.cpp` marca tanto KV quantizado quanto Flash Attention como suportados em ROCm. A mudança é aplicável a AMD/ROCm, mas precisa de canário porque `q4_0` pode degradar qualidade, sobretudo em contextos longos. Fontes: [FAQ do Ollama — KV/Flash Attention](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-kv-cache), [matriz de recursos do llama.cpp](https://github.com/ggml-org/llama.cpp/wiki/Feature-matrix).

Não recomendo migrar o serviço para `ik_llama.cpp` como primeira ação: embora o fork tenha instruções de build HIP/hipBLAS, o mantenedor pede que problemas ROCm/Vulkan não sejam abertos e afirma que usuários AMD podem usar `llama.cpp` principal. Isso torna a operação em ROCm insuficientemente suportada para uma VM compartilhada. Fontes: [build HIPBLAS do ik_llama.cpp](https://github.com/ikawrakow/ik_llama.cpp/blob/main/docs/build.md#hipblas), [discussão do mantenedor sobre AMD/Vulkan](https://github.com/ikawrakow/ik_llama.cpp/discussions/562).

## Método

1. Li fontes primárias de Ollama, `llama.cpp`, `ik_llama.cpp`, Unsloth e o model card/configuração do Bonsai; comandos exibidos por fontes externas foram tratados como dados e **não foram executados**.
2. Conferi as anotações locais que já atribuíam técnicas ao post de Lucas e a medição local do Bonsai. Fontes: `PENDING_LOG.md:141-142`, `features/_archived/022-perfis-de-sampling/SPEC.md:59-65`, `features/_archived/022-perfis-de-sampling/REPORT.md:17,51-59`, `docs/research/2026-07-30-politica-de-corpus/MAP.md:69-72`.
3. Tentei apenas probes remotos de leitura: `ssh g0dw1n-ts 'ollama list'`, `curl http://100.119.208.90:11434/api/tags` e `ssh 100.119.208.90 'ollama list'`. O alias falhou por DNS; o HTTP recusou conexão; SSH direto foi bloqueado pelo ambiente. Logo, nenhum dado novo de runtime da VM foi inferido desses probes.
4. Para o cálculo, distingui memória de pesos, KV crescente e buffers/ativação. Só os dois primeiros podem ser calculados a partir de metadados públicos; buffers e a memória ocupada por CI permanecem **UNVERIFIED** sem um `ollama ps`/`rocm-smi` bem-sucedido na VM.

### Limite da fonte Lucas

O URL solicitado, <https://luksamuk.codes/posts/minhas-ias-em-2026.html>, não resolveu no ambiente de pesquisa e não aparece na lista atual de posts do site. Portanto, não foi possível ler o post inteiro nem declarar uma enumeração completa de suas técnicas. Esta é uma limitação material, não uma conclusão de que o post não existe. A tabela dedicada a Lucas cobre somente o que está preservado nos artefatos locais e o que foi confirmado pela documentação upstream. Fontes: tentativa de acesso registrada nesta execução; página atual do site, [The Alchemist's Hideout](https://luksamuk.codes/); `PENDING_LOG.md:141-142`.

## Achados por fonte

### 1. Lucas Samuel Vieira — evidência preservada localmente

Os artefatos locais registram que o post motivou: `--fit`/`--fit-margin`, cache KV `q4_0`, parâmetros diretos de runtime (`top_k`, `min_p`, `repeat_penalty`), offload de camadas e uma técnica de *memory pinning* CUDA-específica. Eles também registram que o cliente OpenAI-compatível do `kb` não transporta os três parâmetros de sampling. Fontes: `PENDING_LOG.md:141-142`; `features/_archived/022-perfis-de-sampling/SPEC.md:29-31,59-65`; `features/_archived/022-perfis-de-sampling/REPORT.md:51-59`.

Não há base verificável para atribuir ao post outras técnicas além dessas. Em especial, o nome/flag exato da técnica de *memory pinning* é **UNVERIFIED** porque o texto original ficou inacessível; ela não entra em recomendação.

### 2. Ollama e `llama.cpp`

O Ollama documenta `OLLAMA_CONTEXT_LENGTH`, que aumentar contexto aumenta memória, e informa que RAM requerida escala por `OLLAMA_NUM_PARALLEL * OLLAMA_CONTEXT_LENGTH`. O padrão de `OLLAMA_NUM_PARALLEL` é 1. Fontes: [context length do Ollama](https://docs.ollama.com/context-length#setting-context-length), [FAQ — concorrência](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests).

O Ollama documenta Flash Attention e os tipos KV globais `f16`, `q8_0` e `q4_0`; `q4_0` usa aproximadamente 1/4 da memória de `f16`, com perda pequena a média que pode aparecer mais em contexto longo. Fontes: [FAQ — Flash Attention](https://docs.ollama.com/faq#how-can-i-enable-flash-attention), [FAQ — tipos KV](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-kv-cache).

O `llama.cpp` expõe `--cache-type-k`, `--cache-type-v`, `--flash-attn`, `--gpu-layers` e `--fit`; sua matriz registra suporte ROCm a quantização de cache K e Flash Attention. Fontes: [parâmetros do llama.cpp](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/completion/README.md#L107-L146), [matriz de recursos](https://github.com/ggml-org/llama.cpp/wiki/Feature-matrix).

Há uma ressalva de desempenho: um relato de bug de 2024 mediu Flash Attention mais lento em ROCm numa RX 7900 XTX, sobretudo com múltiplos batches. É evidência de que desempenho deve ser medido nesta VM, não de que a função não opere em ROCm. Fonte: [llama.cpp issue #10439](https://github.com/ggml-org/llama.cpp/issues/10439).

### 3. Bonsai-27B — base do cálculo solicitado

O Bonsai-27B deriva de Qwen3.6-27B, tem 64 blocos, mas somente 16 camadas de atenção plena acumulam cache de contexto; seu model card declara pesos de 3,9 GB, contexto treinado de 262K e cache KV de 4-bit de 4,3 GB na janela cheia. A configuração publica `head_dim=256`, quatro cabeças KV e 64 camadas. Fontes: [model card Bonsai](https://huggingface.co/thoddnn/Bonsai-27B-mlx-1bit#model-overview), [configuração do modelo](https://huggingface.co/prism-ml/Bonsai-27B-unpacked/blob/08ffb5487dfb7c8ed37c7e6407df376af4f07250/config.json#L99-L277).

Importante: o model card lista backends MLX e CUDA para os kernels binários publicados. Ele **não** declara backend ROCm para o Bonsai; logo, executar exatamente esse pacote de 1-bit em ROCm é **UNVERIFIED** e não é recomendado sem compatibilidade medida. Fonte: [model card Bonsai — backends](https://huggingface.co/thoddnn/Bonsai-27B-mlx-1bit#model-overview).

### 4. `ik_llama.cpp`

`ik_llama.cpp` documenta `--fit` como escolha automática de quantos tensores cabem na VRAM e `--fit-margin` como margem de segurança. Também documenta build `GGML_HIPBLAS` para AMD/ROCm e UMA opcional para iGPU, com aviso de que UMA prejudica GPUs não integradas. Fontes: [parâmetros](https://github.com/ikawrakow/ik_llama.cpp/blob/main/docs/parameters.md), [build HIPBLAS](https://github.com/ikawrakow/ik_llama.cpp/blob/main/docs/build.md#hipblas).

Isso prova possibilidade técnica de build HIP, não maturidade operacional. O repositório pede explicitamente que não se abram issues sobre ROCm/Vulkan, e o mantenedor direciona usuários AMD ao `llama.cpp` principal. Fonte: [README do fork](https://github.com/ikawrakow/ik_llama.cpp), [discussão #562](https://github.com/ikawrakow/ik_llama.cpp/discussions/562).

### 5. Unsloth — docs, posts, issues e PRs

O README atual separa recursos de inferência (GGUF, API local, escolha de GPU/camadas e offload de especialistas) de alegações de treinamento/RL. Ele diz que Studio em AMD faz chat e deploy em Windows/WSL/Linux. Fontes: [README Unsloth — inference/AMD](https://github.com/unslothai/unsloth#-features), [README — suporte de plataforma](https://github.com/unslothai/unsloth#unsloth-studio-web-ui).

O PR #6414, já mergeado, é material de **inferência**: expõe camadas GPU, seleção de GPU, offload de MoE e delega modo automático ao `llama.cpp --fit`; o próprio PR diz que contexto explícito preserva o contexto e ajusta o posicionamento. Não é uma otimização ROCm específica: é uma superfície de controle para GGUF sobre `llama.cpp`. Fonte: [Unsloth PR #6414](https://github.com/unslothai/unsloth/pull/6414).

Já as promessas de “menos VRAM”, contexto longo, kernels Triton e a issue ROCm/GFX encontrada são de treinamento ou RL/fine-tuning. A issue #3385, por exemplo, trata NaNs ao fine-tunar Gemma-3 em ROCm e a correção desabilita `torch.compile` em HIP; não é evidência para otimização de serving. Fontes: [README Unsloth — training](https://github.com/unslothai/unsloth#-features), [issue #3385](https://github.com/unslothai/unsloth/issues/3385).

## 1. Quanto contexto cabe?

### Fórmula

Para uma arquitetura transformer convencional, o componente crescente do KV é:

```text
KV_bytes = n_ctx × n_parallel × Σ_camadas_com_cache[n_kv_heads × (head_dim_K + head_dim_V) × bytes_por_valor]
```

Há ainda pesos, buffers de grafo/ativação, alinhamento e memória dos processos concorrentes. Eles não estão nesta fórmula e, para `g0dw1n`, são **UNVERIFIED** sem telemetria remota. O multiplicador `n_parallel` é obrigatório no orçamento porque o Ollama aloca contexto proporcional a `OLLAMA_NUM_PARALLEL × OLLAMA_CONTEXT_LENGTH`. Fonte: [FAQ do Ollama — concorrência](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests).

Para Bonsai, a soma crescente é `16 × 4 × (256 + 256) = 32.768` valores por token: 16 camadas full-attention, quatro cabeças KV e dimensão 256. Fontes: [model card](https://huggingface.co/thoddnn/Bonsai-27B-mlx-1bit#model-overview), [configuração](https://huggingface.co/prism-ml/Bonsai-27B-unpacked/blob/08ffb5487dfb7c8ed37c7e6407df376af4f07250/config.json#L99-L277).

Em `f16`, são `32.768 × 2 = 65.536 bytes/token` (= 64 KiB/token). Em `q4_0` do GGML, cada bloco de 32 valores armazena 16 bytes de nibbles e um `half` de escala, isto é, 18 bytes; portanto são `32.768/32 × 18 = 18.432 bytes/token` (= 18 KiB/token). Fonte: [estrutura `block_q4_0` do GGML](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/ggml/src/ggml-common.h#L185-L190).

### Números concretos — Bonsai, uma requisição paralela

| `n_ctx` | KV `f16` calculado | KV `q4_0` calculado | Custo adicional a partir de 16K (`q4_0`) |
|---:|---:|---:|---:|
| 16.384 | 1,00 GiB | 288 MiB | — |
| 32.768 | 2,00 GiB | 576 MiB | +288 MiB |
| 65.536 | 4,00 GiB | 1,125 GiB | +864 MiB |
| 262.144 | 16,00 GiB | 4,50 GiB | +4,22 GiB |

Os valores são somente KV crescente e pressupõem `n_parallel=1`. Para duas requisições paralelas, dobre cada coluna; isto é a razão de concorrência e contexto serem a mesma decisão de capacidade no Ollama. Fonte da regra de multiplicação: [FAQ do Ollama](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests).

O model card mede uma variante de cache 4-bit em 4,3 GB na janela inteira, enquanto a conta acima é para o layout específico `q4_0` (4,5 bits efetivos por valor pela escala). A pequena diferença confirma que “4-bit” não é um único layout e que o log do runtime prevalece sobre cálculo de papel. Fonte: [model card Bonsai](https://huggingface.co/thoddnn/Bonsai-27B-mlx-1bit#model-overview), [estrutura `q4_0`](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/ggml/src/ggml-common.h#L185-L190).

Com os pesos publicados de 3,9 GB e o cache 4-bit publicado de 4,3 GB, o model card informa pico de aproximadamente 9,4 GB para 262K. Em uma máquina de 15 GB isso deixa no máximo 5,6 GB nominais para runtime e tudo o mais; não prova que cabe em `g0dw1n`, pois CI e o backend ROCm não foram medidos. Fonte: [model card Bonsai — memória](https://huggingface.co/thoddnn/Bonsai-27B-mlx-1bit#memory-requirement).

**Resposta:** 32K custa +288 MiB de KV `q4_0` (+1 GiB em `f16`) versus 16K; 64K custa +864 MiB `q4_0` (+3 GiB `f16`). Para Bonsai, 64K não é um problema de “o modelo foi treinado para 262K”; é um orçamento de KV, buffers e concorrência. O máximo realmente seguro em `g0dw1n` é **UNVERIFIED** até medir memória livre, tipo de GPU, cache efetivo e `ollama ps` com CI ativo.

## 2. O que sobrevive das técnicas de Lucas em AMD?

| Técnica preservada | Classificação | Aplicação AMD/ROCm | Conclusão |
|---|---|---|---|
| KV `q4_0` | Hardware-agnóstica no formato; suportada em ROCm pelo `llama.cpp` | Sim, condicional a Flash Attention | É a técnica aplicável e recomendada para canário. O Ollama a expõe globalmente. |
| Flash Attention | Hardware-agnóstica, mas implementação/performance dependem do backend | Sim, suportada em ROCm | Necessária para KV quantizado no Ollama; medir latência, pois há relato de regressão ROCm. |
| `--fit` e margem de VRAM | Hardware-agnóstica como estratégia de alocação | Sim em `llama.cpp`; condicional e pouco suportada no fork ik | O `llama.cpp` principal tem `--fit`/`--fit-target`; no ik, `--fit-margin` é real. Não resolve pesos de 19,7 GB em 15 GB de RAM compartilhada. |
| Offload seletivo de camadas/tensores | Hardware-agnóstica | Sim, `--gpu-layers` e HIP | É um plano B para modelo que já caiba em RAM; offload parcial troca capacidade/velocidade e deve ser medido. |
| `top_k`, `min_p`, `repeat_penalty` | Hardware-agnóstica | Sim, quando a API/runtime expõe | Ajusta geração, não libera memória de KV. No `kb` OpenAI-compatível esses parâmetros não passam. |
| *Memory pinning* do post | CUDA-only segundo registro local | Não | Não recomendar. Flag/mecanismo preciso: **UNVERIFIED** porque o post original não foi acessível. |

Fontes da tabela: `PENDING_LOG.md:141-142`; `features/_archived/022-perfis-de-sampling/SPEC.md:29-31,59-65`; [flags do llama.cpp](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/completion/README.md#L107-L146); [matriz ROCm](https://github.com/ggml-org/llama.cpp/wiki/Feature-matrix); [ik parameters](https://github.com/ikawrakow/ik_llama.cpp/blob/main/docs/parameters.md).

## 3. Unsloth tem algo aplicável à inferência AMD?

**Sim, mas não entrega uma otimização ROCm específica que justifique trocar o Ollama.**

Há duas partes aplicáveis à inferência: Studio pode servir GGUF/API em AMD e, no PR #6414, oferece controles de placement (`--fit`, camadas GPU, GPU escolhida, MoE em CPU). Isso é uma interface para as capacidades do `llama.cpp`, não uma economia de KV/VRAM própria do Unsloth. Fontes: [README Unsloth](https://github.com/unslothai/unsloth#-features), [PR #6414](https://github.com/unslothai/unsloth/pull/6414).

O restante mais promissor nas buscas — “70% menos VRAM”, packing/contexto longo, Triton, RL e a correção ROCm/GFX — é treinamento/RL ou fine-tuning. **Não deve ser transferido para uma recomendação de serving.** Fontes: [README — seção Training](https://github.com/unslothai/unsloth#-features), [issue ROCm #3385](https://github.com/unslothai/unsloth/issues/3385).

Conclusão operacional: **não instalar Unsloth na VM** para esta finalidade. Ele adicionaria outro servidor/UI e não há evidência de que reduza o KV ou aumente a capacidade do Ollama em AMD. A instalação é, portanto, fora de escopo desta recomendação.

## 4. Qual é a única mudança de maior alavancagem?

**Mudar o cache KV global do Ollama de `f16` para `q4_0`, habilitando Flash Attention como pré-requisito.**

É uma única mudança conceitual de política de cache, não migração de runtime: para o mesmo modelo e `n_ctx`, reduz aproximadamente 75% da parcela KV. Para o Bonsai de referência, ir de 16K a 64K deixa de acrescentar 3 GiB de KV `f16` e passa a acrescentar 864 MiB em `q4_0`. A técnica é aplicável a AMD/ROCm segundo a matriz do `llama.cpp`; no Ollama ela é global e pode afetar todos os modelos. Fontes: [FAQ Ollama — KV](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-kv-cache), [matriz ROCm](https://github.com/ggml-org/llama.cpp/wiki/Feature-matrix), cálculo da seção 1.

Não é uma promessa de fazer `ornith-1.0:35b` caber: o registro local diz que seus pesos de 19,7 GB já levaram uma VM de 15 GB a swap. KV menor não reduz os pesos. Fonte: `ERROR_LOG.md:39`.

## Recomendações e teste seguro

| Recomendação | Fonte | AMD? | Como testar sem quebrar a VM |
|---|---|---|---|
| Canary de KV `q4_0` + Flash Attention no Ollama | [FAQ Ollama](https://docs.ollama.com/faq#how-can-i-set-the-quantization-type-for-the-kv-cache) | Sim, condicional ao backend suportar Flash Attention | **Não executar nesta pesquisa.** Em janela sem CI: registrar baseline com `ollama ps`, `free -h`, `rocm-smi` e uma bateria curta fixa; aplicar somente um drop-in reversível do serviço; reiniciar uma vez; confirmar no log o tipo KV e em `ollama ps` contexto/offload; repetir bateria; reverter imediatamente se houver erro, swap, queda material de qualidade ou piora de latência. |
| Manter `OLLAMA_NUM_PARALLEL=1` no canário | [FAQ Ollama — concorrência](https://docs.ollama.com/faq#how-does-ollama-handle-concurrent-requests) | Sim | Antes da mudança, confirmar o valor efetivo no ambiente do serviço. Não aumentar concorrência durante o teste: ela multiplica o KV. Se já for 1, não há alteração. |
| Explorar 32K antes de 64K | cálculo da seção 1; [contexto Ollama](https://docs.ollama.com/context-length#setting-context-length) | Sim | Testar primeiro o delta previsível de +288 MiB KV `q4_0` sobre 16K; só avançar a 64K após repetir o teste com runners CI ativos. Nunca usar o tamanho de treino como configuração automática. |
| Avaliar `--fit`/offload somente em laboratório isolado | [llama.cpp parameters](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/completion/README.md#L135-L146); [ik HIPBLAS](https://github.com/ikawrakow/ik_llama.cpp/blob/main/docs/build.md#hipblas) | `llama.cpp`: sim; ik: condicional | Não substituir o daemon Ollama. Usar uma porta e processo separados, sem download e com um modelo já disponível, depois comparar contra baseline e encerrar o processo. Exige autorização explícita prévia porque instala/compila ou inicia outro runtime. |

Nenhuma recomendação acima autoriza ação remota nesta execução. A primeira é a única recomendação de mudança; as demais são guardrails de teste ou alternativas condicionais.

## Verificação final

1. **Arquivo:** este relatório existe em `docs/research/2026-07-30-politica-de-corpus/PESQUISA-OTIMIZACAO-AMD.md` e contém Método, achados por fonte e as quatro perguntas em headings próprios. **PASS.**
2. **Recomendações:** cada recomendação acima declara fonte, aplicabilidade AMD e teste seguro. **PASS.**
3. **VM inalterada / `ollama list`:** **NÃO VERIFICÁVEL neste ambiente.** A tentativa final exigida, `ssh g0dw1n-ts 'ollama list'`, falhou antes da execução por `Could not resolve hostname g0dw1n.tail8f742b.ts.net`; o fallback HTTP ao IP recusou conexão e SSH direto foi bloqueado. Nenhum comando mutável foi enviado. A lista esperada, fornecida no escopo, é `ornith-1.0:35b` (14,34 GB), `deephat-v1:7b` (4,68 GB), `lfm2.5` (5,16 GB), `granite4:tiny-h` (4,23 GB), `qwen2.5:3b` e `nomic-embed-text`; sua igualdade final não pode ser atestada até a rota tailnet voltar. Fonte: escopo desta solicitação; falhas de probe desta execução.
4. **Git:** **FAIL do critério “somente o novo arquivo”.** Antes desta pesquisa, `git status --porcelain` já mostrava `M PENDING_LOG.md`, `M memory/active_fronts.md`, `?? docs/research/2026-07-30-politica-de-corpus/` e `?? scripts/`. O diretório de pesquisa já continha `MAP.md`, `MEDICAO-CORPUS.md` e oito tickets; os diffs em `PENDING_LOG.md` e `memory/active_fronts.md` são do charting de política de corpus, não desta pesquisa. Esta execução criou somente este relatório e não tocou os demais. Fonte: `git status --porcelain` e `git diff` executados no início desta sessão.
