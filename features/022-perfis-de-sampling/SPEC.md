---
title: Perfis de sampling por tarefa
epic: infra
status: done
pr:
---

# Perfis de sampling por tarefa

## Objetivo

Nenhuma das nove chamadas ao LLM no `kb` especifica parâmetros de amostragem. Todas rodam no default do provider — **temperatura 0,8 no Ollama** — desde `rerank` (que pede uma lista de índices e não admite invenção) até a geração de perguntas do golden (que quer justamente variedade).

O custo disso foi medido: na 021, o `granite4` produziu **36 índices fora da faixa de 20 candidatos**, e esse foi o fator que fez o rerank ficar **abaixo de não reordenar** (0,342 contra 0,414). Amostragem estocástica num espaço onde só 20 valores são válidos gera exatamente esse defeito. O diagnóstico da 021 atribuiu a piora a capacidade e quantização do modelo; a configuração nunca foi considerada.

O sistema deve declarar o perfil de amostragem de cada tarefa, em vez de herdar um default que serve mal a quase todas.

## Requisitos funcionais

- [x] RF-01: perfis nomeados de sampling, com `temperature` e `top_p` explícitos por perfil
- [x] RF-02: cada uma das nove chamadas ao LLM declara seu perfil
- [x] RF-03: `rerank` e classificação de ruído usam perfil determinístico (temperatura 0)
- [x] RF-04: geração de perguntas do golden usa perfil diverso — variedade é o objetivo ali
- [x] RF-05: override por variável de ambiente, para experimentar sem editar código
- [x] RF-06: perfil desconhecido levanta erro, em vez de cair num default silencioso

## Requisitos técnicos

- Módulo `kb/sampling.py` com a tabela de perfis; `chat` já aceita `**kwargs` e repassa ao provider — nenhuma mudança no cliente
- Apenas `temperature` e `top_p`: são os parâmetros que o protocolo OpenAI-compat aceita. `top_k`, `min_p` e `repeat_penalty` (usados em setups llama.cpp diretos) **não** trafegam pelo cliente OpenAI e ficam fora
- Sem dependência nova

## Mudanças de API/CLI

- Novo módulo `kb/sampling.py`
- Novas env vars `KB_SAMPLING_<PERFIL>_TEMP` para override
- Nenhuma mudança de interface de comando

## Testes

- Unit: resolução de cada perfil; override por env; perfil desconhecido levantando erro; determinístico com temperatura exatamente 0
- Integration: `rerank` chamando o provider com `temperature=0`; geração de perguntas com perfil diverso
- Manual: remedir rerank com `bonsai` e `granite4` sob temperatura 0, comparando com 0,467 e 0,342

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 2–3h |
| Bloqueador | **sim** — invalida parcialmente a conclusão da 021 |
| Risk | média (toca todas as chamadas ao LLM; mitigado por perfis conservadores e medição) |

## Dependências

- 016/019 (bench e golden) para medir o efeito no rerank

## Notas

**Origem:** post técnico de Lucas Samuel Vieira sobre seu setup de inferência local (2026), que registra explicitamente os parâmetros de amostragem do seu runtime. A leitura evidenciou que o `kb` nunca declarou os seus.

**Consequência para a 021:** o veredito "trocar o modelo de rerank piorou o resultado" foi medido com temperatura 0,8 nos dois modelos. Se a temperatura explicar os índices inválidos, aquela comparação precisa ser refeita antes de servir como base de decisão.

**Fora de escopo:**
- `top_k`, `min_p`, `repeat_penalty` — inacessíveis via cliente OpenAI-compat
- Ajuste de offload de camadas, KV cache quantizado e flags de runtime (`--fit`, `--cache-type-k`) — são configuração do servidor de inferência, não do `kb`
- Escolha de modelo por tarefa

**Open questions:**
- (nenhuma)
