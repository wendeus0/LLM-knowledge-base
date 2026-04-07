---
title: Learning in Agentic Systems
topic: ai
tags: [agentic-systems, machine-learning, fine-tuning, non-parametric-learning, reflexion, experiential-learning, llm]
source: 11-chapter-7-learning-in-agentic-systems.md
---

# Learning in Agentic Systems

Learning in [[agentic systems]] refers to the capability of agents to improve their performance through interaction with the environment, adapting to changing conditions and refining strategies over time. This process enables agents to move beyond static behavior and develop dynamic responses to complex tasks.

There are two fundamental approaches to implementing learning in agents: [[non-parametric learning]], which improves performance without altering model parameters, and [[parametric learning]], which involves training or fine-tuning the foundation model's parameters.

## Non-Parametric Learning

[[Non-parametric learning]] encompasses techniques that enhance agent performance automatically without modifying the underlying model weights. These methods are typically simpler to implement and require less computational resources than parametric approaches.

### Exemplar Learning

[[Exemplar learning]] is the simplest form of non-parametric learning, where agents store successful interactions as [[few-shot examples]] for [[in-context learning]]. As the agent performs tasks, high-quality examples are collected in a [[memory bank]] containing context, actions, outcomes, and feedback.

Rather than using fixed few-shot examples hard-coded into prompts, advanced implementations dynamically retrieve the most relevant examples using text or semantic retrieval methods. This approach significantly improves performance across various tasks while remaining lightweight and transparent.

### Reflexion

[[Reflexion]] extends exemplar learning by incorporating [[linguistic feedback]]. Agents maintain a memory buffer of reflective text analyzing their performance on previous trials. This technique accommodates both numerical and free-form feedback, allowing agents to:

- Analyze unsuccessful attempts
- Devise new plans of action accounting for past mistakes
- Inject these reflections into subsequent prompts to improve performance

Reflexion operates by prompting the agent to reflect on strategy and path taken, then generating concise plans for future attempts when encountering similar tasks.

### Experiential Learning (ExpeL)

[[Experiential learning]] represents an advanced evolution of non-parametric approaches, specifically the [[ExpeL]] methodology. Unlike simple exemplar storage, this technique aggregates insights across multiple experiences to improve future policy through [[cross-task learning]].

The system maintains a dynamic list of insights extracted from experiences, implementing a governance mechanism with four operations:

- **AGREE**: Retain existing rules strongly relevant to the task
- **REMOVE**: Eliminate contradictory or duplicate rules
- **EDIT**: Modify existing rules to be more general or enhanced
- **ADD**: Introduce new rules distinct from existing ones

Insights are continuously reevaluated and adjusted in importance relative to other learned rules. This enables agents to [[distill]] general, high-level critiques from specific failures, facilitating adaptation to [[non-stationary environments]] where conditions change over time.

## Parametric Learning: Fine Tuning

[[Parametric learning]] involves adjusting the parameters of predefined models to improve task-specific performance. When sufficient evaluation data exists and non-parametric approaches become computationally expensive due to large context windows, fine-tuning becomes advantageous.

### Fine-Tuning Large Foundation Models

[[Large foundation models]] (such as [[GPT-4o]], [[Claude]], or [[Gemini]]) offer exceptional performance across diverse tasks due to their extensive pre-training on general-purpose datasets. [[Fine-tuning]] these models involves targeted adjustments to adapt their vast knowledge to specific domains.

Advantages include:
- Deep contextual understanding and nuanced language handling
- [[Multi-tasking]] and [[transfer learning]] capabilities
- Enhanced autonomous decision-making and reasoning

However, fine-tuning large models requires significant computational resources (high-end GPUs), substantial financial investment, and large volumes of high-quality, domain-specific data to avoid [[bias]] or [[overfitting]].

### The Promise of Small Models

[[Small models]] (such as [[LLaMA]] or [[Phi]]) offer resource-efficient alternatives to large foundation models. Their advantages include:

- **Interpretability**: Fewer parameters enable easier analysis of decision-making processes
- **Agility**: Faster iteration cycles and rapid experimentation
- **Accessibility**: Open-source availability and lower infrastructure costs
- **Sustainability**: Reduced energy consumption for training and inference
- **Edge deployment**: Feasibility for [[embedded devices]], mobile applications, and [[IoT]] networks

When fine-tuned for specific, narrowly defined tasks, small models can achieve comparable or superior performance to large models while enabling frequent updates and [[federated learning]] scenarios.

### Function Calling Fine-Tuning

[[Function calling fine-tuning]] is a specialized technique enhancing an agent's ability to interact with external [[APIs]], tools, or functions. This approach trains models to:

- Understand [[API schemas]], including function names, argument types, and return formats
- Make contextual decisions about when to invoke functions versus providing direct responses
- Parse and validate arguments accurately from user inputs
- Handle errors and exceptions gracefully, either prompting for clarification or offering alternatives

Implementation requires careful dataset preparation covering diverse invocation scenarios and robust security measures including [[input validation]] and function whitelisting to prevent unintended execution.

## Considerations for Implementation

When designing learning capabilities for agentic systems, consider that implementing learning requires additional design, evaluation, and [[monitoring]]. While powerful, these capabilities may not be necessary for all applications. Generally, practitioners should begin with [[non-parametric learning]] approaches due to their simplicity and lower resource requirements, transitioning to [[parametric learning]] only when the volume of examples justifies the computational investment.

## Conceitos Relacionados
- [[agentic systems]]
- [[non-parametric learning]]
- [[parametric learning]]
- [[in-context learning]]
- [[few-shot learning]]
- [[Reflexion]]
- [[experiential learning]]
- [[fine-tuning]]
- [[foundation models]]
- [[function calling]]
- [[memory bank]]
- [[cross-task learning]]
- [[transfer learning]]
- [[non-stationary environments]]
- [[federated learning]]
- [[overfitting]]
