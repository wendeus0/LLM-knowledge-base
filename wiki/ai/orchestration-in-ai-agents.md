```
---
title: Orchestration in AI Agents
topic: ai
tags: [ai-agents, orchestration, skill-selection, planning, llm, langchain]
source: 09-chapter-5-orchestration.md
---

# Orchestration in AI Agents

**Orchestration** é o processo de coordenar como [[AI Agents|agentes de IA]] utilizam suas [[Skills|habilidades]] (skills) para resolver tarefas complexas. Enquanto tarefas simples podem ser resolvidas com informações intrínsecas aos [[Foundation Models|modelos de fundação]], tarefas complexas exigem múltiplas habilidades com dependências entre si, exigindo seleção, execução e planejamento adequados.

## Skill Selection (Seleção de Habilidades)

A seleção de habilidades é a base para o planejamento avançado. Diferentes abordagens oferecem trade-offs entre latência, acurácia e complexidade:

### Generative Skill Selection

A abordagem mais simples, onde o modelo de linguagem recebe as descrições das habilidades e seleciona a mais apropriada para o contexto. 

**Vantagens:** Fácil implementação, não requer treinamento adicional ou [[Embeddings|embeddings]].
**Desvantagens:** Alta latência devido à chamada adicional ao LLM.

### Semantic Skill Selection

Padrão mais comum e recomendado para a maioria dos casos. As descrições das habilidades são convertidas em embeddings usando modelos como ADA, Titan, Cohere ou [[BERT]], indexadas em um [[Vector Database|banco de dados vetorial]] (ex: [[FAISS]]). Em runtime, a query do usuário é embedada e a habilidade mais semanticamente similar é recuperada.

**Vantagens:** Mais rápida que a seleção generativa, performática e escalável.

### Hierarchical Skill Selection

Para cenários com grande número de habilidades semanticamente similares. As skills são organizadas em grupos hierárquicos. Primeiro seleciona-se o grupo, depois a skill específica dentro dele.

**Trade-off:** Aumenta a acurácia mas adiciona latência e complexidade. Requer manutenção dos grupos.

### Machine Learned Skill Selection

Utiliza técnicas de [[Machine Learning]] treinadas em pares tarefa-habilidade históricos. Permite usar modelos menores e mais rápidos que LLMs genéricos, reduzindo custo e latência.

**Desvantagens:** Introduz custo de manutenção de modelo, requer dados de treinamento extensivos.

## Skill Execution (Execução de Habilidades)

### Parametrização

Processo de definir os parâmetros da função baseado na definição da skill e no contexto atual do agente. O estado atual, incluindo progresso e contexto adicional (hora, localização), é injetado no prompt para que o modelo preencha os argumentos corretamente. Recomenda-se validação básica dos tipos de dados.

### Execução

Fase onde a skill é efetivamente executada, localmente ou via APIs remotas. Requer implementação de lógica de timeout e retry ajustada às necessidades de latência do caso de uso.

## Skill Topologies (Topologias de Habilidades)

Estruturas que definem como múltiplas skills se relacionam e são executadas:

### Single Skill Execution

Execução de única habilidade por tarefa. Fundamento mínimo sobre o qual padrões mais complexos são construídos.

### Parallel Skill Execution

Execução simultânea de múltiplas skills independentes. Útil quando é necessário consultar diversas fontes de dados simultaneamente. Tipicamente envolve uma chamada ao LLM para filtrar quais skills são necessárias antes da execução paralela.

### Chains (Cadeias)

Sequências de ações executadas linearmente, onde cada ação depende da conclusão da anterior. Comuns em workflows passo a passo. Recomenda-se definir comprimento máximo para evitar acúmulo de erros.

### Trees (Árvores)

Estruturas ramificadas onde o agente escolhe entre múltiplos caminhos em pontos de decisão. Permitem que o agente determine se a tarefa está completa, se é impossível de completar, ou navegar para outros nós folha. Reduz a probabilidade de subtarefas serem esquecidas.

**Parâmetros-chave:** Número máximo de skills por execução e profundidade máxima da árvore.

### Graphs (Grafos)

Redes interconectadas com dependências não-lineares. Extensão das árvores que permite consolidar resultados de múltiplos nós previamente executados (ação de *consolidate*). Ideal para raciocínio complexo que exige unir descobertas de múltiplas skills anteriores.

**Trade-off:** Maior flexibilidade e expressividade, mas maior complexidade de gerenciamento e novas classes de erros possíveis.

### Escolhendo uma Topologia

- **Linear (Chains):** Tarefas sequenciais simples
- **Hierárquica (Trees):** Tarefas com múltiplas camadas de abstração ou decomposição em subtarefas
- **Grafos:** Componentes interconectados com dependências dinâmicas e imprevisíveis

**Princípio:** Comece simples e adicione complexidade apenas quando necessário.

## Planning (Planejamento)

### Iterative Planning (Planejamento Iterativo)

Abordagem "gananciosa" (greedy) onde o agente escolhe e executa uma ação por vez. Vantagens: simplicidade, baixa latência, fácil manutenção. Recomendado como ponto de partida e suficiente para tarefas com poucas skills.

### Zero-Shot Planning

Geração de planos para tarefas nunca vistas antes, baseada apenas no entendimento do agente sobre o espaço de ações e seus efeitos. Útil em ambientes dinâmicos onde tarefas variam constantemente.

### In-Context Learning with Hand-Crafted Examples

Uso de exemplos manuais (few-shot) criados por desenvolvedores com expertise de domínio. Os exemplos são embedados e indexados para recuperação semântica, guiando o planejamento futuro. Oferece precisão mas pode carecer de flexibilidade para cenários novos.

### Plan Adaptation (Adaptação de Planos)

Capacidade de modificar planos baseado em resultados de ações anteriores. A técnica [[ReAct]] (Reason-Act) alterna entre passos de raciocínio e ação, permitindo ao agente decidir se deve continuar buscando dados ou completar a tarefa.

**PlanReAct:** Extensão que adiciona fluxo de auto-reflexão com [[Chain of Thought|Chain of Thought (CoT)]], combinando planejamento, raciocínio e ação.

## Melhores Práticas

1. **Trade-off Latência vs Acurácia:** Considere os requisitos do sistema—há trade-off claro entre esses fatores
2. **Número de Ações:** Quanto maior o número típico de ações, mais complexa a abordagem de planejamento necessária
3. **Adaptabilidade:** Se o plano precisa mudar significativamente baseado em resultados anteriores, use técnicas de adaptação incremental (ReAct)
4. **Testes:** Desenvolva casos de teste representativos para avaliar diferentes abordagens
5. **Simplicidade:** Escolha a abordagem mais simples que atenda aos requisitos do caso de uso

Comece com cenários bem definidos e abordagens simples de orquestração, escalando gradualmente a complexidade conforme necessário.

## Conceitos Relacionados
- [[AI Agents]]
- [[Foundation Models]]
- [[LLM]]
- [[Skill Selection]]
- [[Semantic Skill Selection]]
- [[Generative Skill Selection]]
- [[Hierarchical Skill Selection]]
- [[Embeddings]]
- [[Vector Database]]
- [[FAISS]]
- [[Skill Execution]]
- [[Skill Topologies]]
- [[Chains]]
- [[Trees]]
- [[Graphs]]
- [[Planning]]
- [[Iterative Planning]]
- [[Zero-Shot Planning]]
- [[In-Context Learning]]
- [[Few-Shot Learning]]
- [[ReAct]]
- [[PlanReAct]]
- [[Chain of Thought]]
- [[LangChain]]
- [[Machine Learning]]
```