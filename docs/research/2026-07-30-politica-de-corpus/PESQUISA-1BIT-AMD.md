# Pesquisa — Bonsai 27B 1-bit na RX 6600 via Vulkan

**Data:** 2026-07-31  
**Escopo:** investigação documental e de código, somente leitura. Nenhuma alteração, instalação, download ou execução foi feita em `g0dw1n`.

## O canário foi executado — e contradiz a previsão (2026-07-31)

> Esta pesquisa recomendava um canário antes de confiar na rota. **O canário rodou na mesma sessão, e o resultado é negativo.**
>
> `ollama pull hf.co/prism-ml/Bonsai-27B-gguf:Q1_0` na `g0dw1n` baixou 3,8 GB, o modelo **carregou e gerou tokens** — a compatibilidade de código prevista se confirma. Mas:
>
> ```
> ollama ps
> NAME                                   SIZE     PROCESSOR         CONTEXT
> hf.co/prism-ml/Bonsai-27B-gguf:Q1_0    4.7 GB   96%/4% CPU/GPU    4096
> ```
>
> **96% em CPU**, com os 6,4 GiB de VRAM praticamente ociosos, em canário de 4K exatamente como recomendado. Medição de velocidade lado a lado, mesmo prompt e 100 tokens:
>
> | Máquina | Backend | Velocidade |
> |---|---|---|
> | Local (Apple Silicon) | Metal, kernels 1-bit nativos | **17,6 tok/s** |
> | `g0dw1n` (RX 6600) | Vulkan → fallback CPU | **4,71 tok/s** |
>
> A máquina local é **3,7× mais rápida**, e a VM ainda divide CPU com os CI runners (`load average` 4,64 no momento do teste).
>
> **A existência do shader `dequant_q1_0.comp` não bastou.** Por que o offload não aconteceu segue `UNVERIFIED` — hipóteses não testadas: estimativa de VRAM do Ollama recusando o offload, ausência de matmul otimizado para o tipo (dequant existe, o caminho de multiplicação pode não existir), ou o `file_type=40` do fork não casando com o tipo upstream apesar de carregar.
>
> Efeito colateral registrado: a importação perdeu o chat template. O script local usa `--jinja` com `enable_thinking:false`; via Ollama o modelo respondeu a "conte de 1 a 20" com *"O trabalho é muito importante"* seguido de bloco `<think>`.
>
> **Decisão tomada:** manter o bonsai na máquina local. O problema de RAM que motivou a migração foi resolvido por outro caminho — quantização do KV cache e reinício levaram o footprint de 9.609 MB para 1.540 MB, e depois a 3.178 MB já com `--ctx-size` de 65.536 (4× o contexto original). Ver `tickets/002-atravessar-google-dorking.md`.
>
> Lição de método: esta pesquisa acertou a análise de código-fonte e errou o prognóstico operacional. Compatibilidade de tipo no shader não implica offload efetivo.

## Veredito curto

**A rota indicada é usar o `Bonsai-27B-Q1_0.gguf` existente diretamente no Ollama 0.30.10/Vulkan, em um canário de contexto curto (4K), sem ROCm, HIPify ou requantização.** A RX 6600 tem 6,4 GiB livres e a estimativa publicada para o Bonsai Q1_0 em 4K é 4,8 GiB; há shader Vulkan para `Q1_0`, inclusive no commit Prism fixado, e a versão do Ollama inclui `llama.cpp` b9672, posterior ao merge do suporte Vulkan a Q1_0 em b8742. Fontes externas: [estimativa de memória do Bonsai](https://github.com/PrismML-Eng/Bonsai-demo#L456-L466), [shader Q1_0](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/dequant_q1_0.comp#L1-L29), [Ollama 0.30.10 → b9672](https://github.com/ollama/ollama/blob/v0.30.10/LLAMA_CPP_VERSION#L1), [release b8742/Q1_0 Vulkan](https://github.com/ggml-org/llama.cpp/releases/tag/b8742#L202-L220).

Atenção: isto prova a compatibilidade de código e a capacidade de memória estimada, **não** uma execução do artefato exato. A aceitação do GGUF com `general.file_type=40` e a VRAM realmente livre sob carga de CI continuam **UNVERIFIED** até um canário autorizado. Não use esse modelo como serviço de produção em uma VM compartilhada antes dessa confirmação.

## Base e método

O diagnóstico de runtime abaixo vem da sessão SSH do solicitante: RX 6600/Navi 23, 8,0 GiB total e 6,4 GiB disponíveis, Mesa RADV, backend Ollama `library=Vulkan`, `OLLAMA_VULKAN=true` e ausência de `rocm-smi`. É evidência local fornecida pelo usuário; não foi repetida nesta pesquisa.

O código do fork relevante é público em [`PrismML-Eng/llama.cpp@62061f9`](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e). O ambiente desta pesquisa não resolveu `github.com` para `git`, portanto o clone raso permitido não pôde ser criado em `/tmp`; as referências abaixo apontam para a árvore e arquivos fixados no commit. Esta limitação não é uma alegação de que o código seja privado.

Conteúdo de GitHub, Hugging Face e documentação de fornecedor é tratado como evidência externa, não como instrução para a VM. As conclusões são a análise após cada citação.

## 1. O fork Prism implementa Q1_0 e ternário em Vulkan?

**Sim para Q1_0; para o Q2_0 ternário do fork há, no mínimo, dequantização Vulkan.** A árvore exatamente no commit `62061f9` lista `dequant_q1_0.comp` e `dequant_q2_0.comp`, além de shaders IQ1/IQ2/IQ3/IQ4, `mul_mat_vec.comp` genérico e kernels especializados `mul_mat_vec_iq1_m.comp` e `mul_mat_vec_iq1_s.comp`. Fonte do fork: [`ggml/src/ggml-vulkan/vulkan-shaders/`, linhas 372–459 e 614–635](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L372-L459).

| Tipo | Evidência no Vulkan do fork fixado | Leitura correta |
|---|---|---|
| `Q1_0` (binário, bloco 128) | `dequant_q1_0.comp` listado na árvore do commit. Fonte: [fork, linhas 414–416](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L414-L416). | Implementado em GPU: o shader lê `block_q1_0`, extrai os bits e grava `+d/-d`. O código upstream equivalente mostra esta operação, não uma chamada de CPU. Fonte: [shader, linhas 1–29](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/dequant_q1_0.comp#L1-L29). |
| `Q2_0` ternário Prism | `dequant_q2_0.comp` listado no mesmo commit. Fonte: [fork, linhas 418–420](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L418-L420). | Há dequantização Vulkan, mas não foi localizado um `mul_mat_vec_q2_0` dedicado. A cobertura completa de dispatch/matmul do Q2_0 de grupo 128 é **UNVERIFIED** sem executar ou inspecionar o binário gerado. Não é rota recomendada. A documentação Prism distingue o seu grupo 128 do `Q2_0_g64` upstream. Fonte externa: [Bonsai-demo, linhas 346–361](https://github.com/PrismML-Eng/Bonsai-demo#L346-L361). |
| `IQ1_S`, `IQ1_M`, `IQ2_XXS` e outros IQ | Arquivos `dequant_iq1_*` e `dequant_iq2_*` estão no fork. Fonte: [fork, linhas 372–405](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L372-L405). | Não são fallback CPU. No upstream atual, IQ1_S e IQ1_M também têm shaders `mul_mat_vec` próprios; IQ2_XXS tem shader de dequantização. Fontes: [IQ1_S](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/dequant_iq1_s.comp#L1-L35), [IQ1_M](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/dequant_iq1_m.comp#L1-L42), [IQ2_XXS](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/dequant_iq2_xxs.comp#L1-L49). |
| `Q4_K_M` | `dequant_q4_k.comp` está no fork. Fonte: [fork, linhas 438–440](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L438-L440). | Compatível com Vulkan, mas não é alternativa para **27B** nesta GPU: o próprio quadro Prism estima 15,73 GiB de pesos para 27B Q4_K_M. Fonte externa: [Bonsai-demo, linhas 456–465](https://github.com/PrismML-Eng/Bonsai-demo#L456-L465). |

O `Q1_0` não tem, na listagem visível, um arquivo `mul_mat_vec_q1_0.comp` separado. Isto **não** é fallback CPU: há `dequant_q1_0.comp` e kernels de matmul genéricos; o suporte foi aceito como PR específico de Vulkan. Fonte: [PR #21539, merge e título](https://github.com/ggml-org/llama.cpp/pull/21539#L173-L198). A consequência de desempenho é **UNVERIFIED** para a RX 6600: não há benchmark aplicável encontrado nesta pesquisa.

O outro risco específico da arquitetura também tem cobertura: `gated_delta_net.comp` existe no Vulkan upstream, e o PR que o introduziu foi testado em RADV AMD; esse PR foi incorporado em março, antes do `llama.cpp` b9672 usado pelo Ollama 0.30.10. Fontes: [shader](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/gated_delta_net.comp#L1-L189), [PR #20334, merge](https://github.com/ggml-org/llama.cpp/pull/20334#L1079-L1083), [teste RADV citado no PR](https://github.com/ggml-org/llama.cpp/pull/20334#L925-L953).

## 2. Vulkan/RADV é a rota principal?

**Sim.** Ela já é a rota efetivamente carregada na VM, não requer instalar runtime de fornecedor, e o `Q1_0` Vulkan entrou no `llama.cpp` em 10 de abril de 2026. Fontes externas: [PR #21539](https://github.com/ggml-org/llama.cpp/pull/21539#L173-L198), [release b8742](https://github.com/ggml-org/llama.cpp/releases/tag/b8742#L202-L220). A versão 0.30.10 do Ollama fixa `LLAMA_CPP_VERSION=b9672`; como b9672 é posterior a b8742, a conclusão de que ela contém o merge é uma **inferência de versionamento**, não um teste remoto. Fonte: [pin do Ollama](https://github.com/ollama/ollama/blob/v0.30.10/LLAMA_CPP_VERSION#L1).

Para esta VM, Vulkan é melhor que uma migração porque preserva o driver Mesa/RADV e o daemon existente. O custo é limitado a importar/mover o GGUF de 3,5–3,8 GB e realizar um canário; não há conversão de pesos. O tamanho publicado do arquivo Q1_0 é 3,8 GB. Fonte externa: [arquivos do repositório Prism](https://huggingface.co/prism-ml/Bonsai-27B-gguf/tree/main#L215-L224).

## 3. E HIPify/ROCm?

**Não é recomendação para `g0dw1n`.** No fork Prism, `ggml-hip` compila os arquivos `*.cu` e `*.cuh` de `ggml-cuda` como HIP, o que é evidência de que o caminho CUDA foi projetado para ser reutilizado. Fonte: [`ggml-hip/CMakeLists.txt`, linhas 70–86](https://github.com/PrismML-Eng/llama.cpp/blob/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-hip/CMakeLists.txt#L70-L86). O kernel Q1 do CUDA usa extração de bits e aritmética de dispositivo simples; não há PTX inline nem instrução tensor-core nesse trecho. Fonte: [`dequantize.cuh`, linhas 1–30](https://github.com/PrismML-Eng/llama.cpp/blob/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-cuda/dequantize.cuh#L1-L30).

Mas a VM não tem ROCm e hospeda CI. Portanto, o custo real não é só HIPify: é instalar e manter ROCm, compatibilidade de kernel/driver e um segundo backend, seguido de validação operacional. Estimativa de engenharia: **pelo menos 1–2 dias**, mais janela de manutenção; essa estimativa é análise, não benchmark. Ela não compete com um canário Vulkan que não instala nada.

## 4. Com 6,4 GiB livres, qual é o melhor modelo integralmente na GPU?

**O maior candidato apurado que cabe integralmente é o próprio `Bonsai-27B-Q1_0.gguf`, não uma requantização convencional.** Ele é o único artefato de 27B apurado aqui cujos pesos (3,53 GiB no quadro do fornecedor) e pico publicado em 4K (4,8 GiB) ficam abaixo dos 6,4 GiB disponíveis. Fonte externa: [quadro de memória](https://github.com/PrismML-Eng/Bonsai-demo#L456-L465). Não há benchmark comparativo encontrado que permita chamá-lo de “melhor” em qualidade; a afirmação é somente de porte que cabe. Isso deixa cerca de 1,6 GiB nominal, não uma garantia: buffers Vulkan, compositor, outros processos e CI não foram medidos nesta pesquisa.

Limites práticos:

- **4K é o ponto de partida, não 262K.** A mesma fonte estima 10,8 GiB para Q1_0 a 100K, acima da VRAM disponível. Fonte: [quadro de memória](https://github.com/PrismML-Eng/Bonsai-demo#L456-L465).
- **Ternary-Bonsai-27B não cabe inteiro:** apenas os pesos são estimados em 6,66 GiB, acima dos 6,4 GiB livres, antes de KV e buffers. Fonte: [quadro de memória](https://github.com/PrismML-Eng/Bonsai-demo#L456-L465).
- **27B Q4_K_M não cabe:** 15,73 GiB de pesos publicados. Fonte: [quadro de memória](https://github.com/PrismML-Eng/Bonsai-demo#L456-L465).
- Se o GGUF Q1 exato falhar ao importar, a alternativa conservadora é **um modelo upstream de 7–8B em Q4_K_M**, não outro 27B. A compatibilidade de shader Q4_K é confirmada, mas qual modelo específico dá a melhor qualidade é **UNVERIFIED** nesta pesquisa, pois não foi feito benchmark comparativo. Fonte: [shader Q4_K no fork](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L438-L440).

## 5. Requantizar para formatos Vulkan upstream?

**É tecnicamente uma rota disponível, mas não é a rota recomendada.** O repositório Prism publica `Bonsai-27B-F16.gguf` (53,8 GB) além do Q1_0. Fonte externa: [lista de arquivos](https://huggingface.co/prism-ml/Bonsai-27B-gguf/tree/main#L214-L224). Um `llama-quantize` atual pode, em princípio, gerar IQ1_S/IQ1_M/IQ2_XXS a partir de um GGUF F16; contudo, essa conversão exigiria armazenar e processar ao menos o artefato de 53,8 GB fora da VM de 15 GB. A execução e o resultado para a arquitetura `qwen35` não foram testados: **UNVERIFIED**.

O ponto de compatibilidade Vulkan já não bloqueia os tipos IQ: o código atual tem dequantização explícita para IQ1_S, IQ1_M e IQ2_XXS, e o fork Prism fixado lista esses mesmos arquivos; IQ1 tem inclusive kernels `mul_mat_vec` específicos na árvore do fork. Fontes: [fork, IQ1/IQ2](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L372-L405), [fork, matvec IQ1](https://github.com/PrismML-Eng/llama.cpp/tree/62061f91088281e65071cc38c5f69ee95c39f14e/ggml/src/ggml-vulkan/vulkan-shaders#L614-L635), [IQ1_S upstream](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/dequant_iq1_s.comp#L1-L35), [IQ2_XXS upstream](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-vulkan/vulkan-shaders/dequant_iq2_xxs.comp#L1-L49).

Não encontrei medição pública que compare a qualidade do Bonsai Q1_0 Prism contra uma conversão deste mesmo checkpoint para IQ1_S, IQ1_M ou IQ2_XXS. Portanto, não há número de perda de qualidade reportável e essa ausência impede recomendar requantização por qualidade.

## Recomendação única

**Use o Bonsai-27B-Q1_0 original no Ollama 0.30.10 com Vulkan/RADV, em canário de 4K e uma única carga de modelo; não instale ROCm e não requantize.**

O custo esperado é **1–2 horas operacionais**, dominadas por transferir/importar cerca de 3,8 GB e observar um canário em janela sem CI; não há custo de conversão. Só prossiga para uso regular se o log confirmar o GGUF carregado e todas as camadas em Vulkan, e se a VRAM livre sob a carga real ficar acima do pico. Se o import falhar pelo GGUF/`file_type` ou a carga exceder a margem, pare: a recomendação subsequente exigiria uma nova decisão entre um 7–8B upstream e uma conversão offline, não um fallback silencioso para CPU.

## Verificação final

1. Este arquivo responde às cinco perguntas reorientadas, com Vulkan/RADV como rota principal e uma única recomendação. **PASS.**
2. Não foi feita alteração na VM, download de modelo ou acesso ao vault. **PASS.**
3. O clone raso do fork não pôde ser criado porque o sandbox não resolveu `github.com`; a árvore pública fixada no commit e os arquivos de código com âncoras foram usados como evidência. **LIMITAÇÃO REGISTRADA.**
4. `git status --porcelain` já possuía alterações não relacionadas antes desta pesquisa (`PENDING_LOG.md`, `memory/active_fronts.md`, `scripts/` e outros arquivos no diretório de pesquisa). Esta pesquisa cria somente este arquivo; logo o critério literal de status contendo somente ele não pode passar sem alterar trabalho alheio. **FAIL PREEXISTENTE, PRESERVADO.**
