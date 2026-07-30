# REPORT — 022-perfis-de-sampling

**Data:** 2026-07-30
**Status:** `DONE` — ganho medido e melhor configuração encontrada.
**Ciclo:** SPEC → RED (9 + 1 testes) → GREEN → medição das quatro combinações modelo × temperatura

## O que mudou

- **`kb/sampling.py` (novo):** quatro perfis com `temperature` e `top_p` explícitos — `deterministic` (0,0), `analytical` (0,2), `generative` (0,6), `diverse` (0,9). Override por `KB_SAMPLING_<PERFIL>_TEMP`, perfil desconhecido levanta erro.
- **As nove chamadas ao LLM passam a declarar perfil:** `rerank` determinístico; `heal`, `lint` e `qa` analíticos; `compile`, file-back e expansão de query generativos; geração de casos do golden diversa.
- **Chave de cache do rerank inclui o sampling** — mudar temperatura invalida, senão a medição reusaria respostas de outra configuração.

## Motivação

Nenhuma das nove chamadas especificava amostragem: todas herdavam o default do provider, **0,8 no Ollama**. `rerank` (ordenar 20 índices, nenhuma variação admissível) e `generate_cases` (inventar perguntas, variedade é o objetivo) compartilhavam o mesmo número, que ninguém escolheu.

Origem: post técnico de Lucas Samuel Vieira sobre seu setup de inferência local, que registra os parâmetros de amostragem explicitamente. A leitura evidenciou o que o `kb` nunca declarou.

## Validação

- 10 testes novos, nascidos RED. Suíte: **586 passed**, ruff limpo.

### Medição — quatro combinações, golden de 152 casos

| Configuração | recall@5 | MRR | cobertura | omissão severa | índices inválidos |
|---|---|---|---|---|---|
| sem rerank | 0,414 | 0,242 | — | — | — |
| `granite4` @ 0,8 | 0,342 | 0,215 | 90% | 6 | 36 |
| `granite4` @ 0,0 | 0,388 | 0,247 | 96% | 3 | 32 |
| `bonsai` @ 0,8 | 0,467 | 0,299 | 75% | 40 | 0 |
| **`bonsai` @ 0,0** | **0,467** | **0,343** | **93%** | **3** | **0** |

**Melhor configuração: `bonsai-27b-1bit` com temperatura 0** — MRR de 0,242 (sem rerank) para 0,343, **+42% relativo**.

## Dois achados que corrigem diagnósticos anteriores

**1. A omissão do bonsai era artefato de temperatura.** A 020 mediu cobertura de 75% e omissão severa em 26% das chamadas, e eu interpretei como degradação por quantização a 1 bit. Com temperatura 0, a cobertura sobe para 93% e a omissão severa cai para 2%. Era configuração, não compressão.

**2. A hipótese sobre os índices inválidos estava errada.** Eu afirmei que as 36 posições fora de faixa do `granite4` vinham de amostragem estocástica. Sob decodificação gulosa caíram apenas para 32 — o modelo viola o intervalo **deterministicamente**. Isso é capacidade, não configuração, e nenhum ajuste de sampling conserta.

Os dois defeitos que eu havia fundido são distintos: **omissão é corrigível por configuração; alucinação de índice não é.** A instrumentação da 020 media o primeiro, e o segundo é o que decide o resultado.

**Consequência para a 021:** o veredito "trocar o modelo piorou" **sobrevive** à correção. O `granite4` a 0,388 continua abaixo de não reordenar (0,414). Não foi má configuração da minha parte — foi o modelo.

## Efeito colateral notável

O recall@5 do bonsai não mudou (0,467 nas duas temperaturas), mas o **MRR subiu 15%**. Os mesmos artigos são encontrados, em posições melhores — que é exatamente o que se espera de um rerank mais estável, e o que o recall@5 sozinho não captura.

## Riscos / dívida

- **`top_k`, `min_p` e `repeat_penalty` ficam fora:** não trafegam pelo cliente OpenAI-compat, só pela API nativa do runtime. O post do Lucas os usa; o `kb` não pode.
- Os perfis `analytical`, `generative` e `diverse` foram **escolhidos por julgamento, não medidos.** Só o `deterministic` tem evidência. Medir os outros exigiria instrumento para qualidade de prosa, que não existe.
- A medição do bonsai levou 91 min e foi morta pelo runner na primeira tentativa; concluiu desacoplada via `nohup`. O cache por chamada é o que tornou a retomada barata.

## Próximos passos

1. Fixar `bonsai` @ temperatura 0 como configuração de rerank recomendada e documentar no `.env.example`.
2. Restringir a saída do rerank (pedir top-5 em vez de ordenar 20) — reduz o espaço de alucinação de índice, que é o defeito que sampling não resolve.
3. Se o teste de compressão importar, o caminho é `ik_llama.cpp` com `--fit` e KV cache q4_0 (do post do Lucas) para viabilizar um 35B na VM — hoje o `ornith-35b` não cabe.
