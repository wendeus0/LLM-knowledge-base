---
title: Knowledge and Memory in AI Agents
topic: ai
tags: [ai-agents, memory, rag, vector-stores, knowledge-graphs, llm, context-window, embeddings, semantic-search]
source: 10-chapter-6-knowledge-and-memory.md
---

# Knowledge and Memory in AI Agents

Memory in [[AI Agents]] refers to information dynamically injected into prompts to complement the [[LLM]]'s parametric memory (weights), distinct from computer system memory like RAM. It maintains interaction state, previous tasks, results, and enables learning across sessions. Effective memory systems allow agents to incorporate external knowledge, maintain state across sessions, and perform complex tasks more effectively.

## Foundational Memory Approaches

### Context Window Management

The simplest approach relies on the [[Context Window]]—all information provided to the foundation model during invocation. A **rolling context window** maintains conversation history in a first-in, first-out (FIFO) fashion: as new interactions occur, oldest content is ejected when the token limit is reached.

**Limitations:**
- Information loss occurs regardless of relevance when the window fills
- Large prompts may cause the model to miss important information
- Relevant context should be placed near the end of the prompt for better utilization

### Keyword-Based Memory

This approach extracts keywords from each interaction using the foundation model's [[Named Entity Recognition]] capabilities. The system maintains:
- Storage for each response
- A mapping from keywords to original documents

When new prompts arrive, keywords are extracted and the lookup is consulted to include previous occurrences. This preserves broader context for specific topics over time.

**Hybrid Approach:** Split the context window between keyword retrieval (j most recent matches) and rolling context (k most recent interactions).

## Semantic Memory and Vector Stores

[[Semantic Memory]] enables long-term storage and retrieval of general knowledge, concepts, and past experiences using [[Embeddings]]—vector representations capturing semantic meaning in high-dimensional space.

### Semantic Search vs. Keyword Search

Unlike keyword matching, [[Semantic Search]] understands context and intent, retrieving results based on meaning rather than exact lexical matches. Models like Word2Vec, GloVe, and [[BERT]] place semantically similar words closer together in vector space.

### Vector Store Implementation

1. **Embedding Generation**: Text is converted to dense vectors using [[LLM]] embedding models
2. **Storage**: Vectors are stored in specialized databases ([[Vector Store]]) like FAISS, Annoy, or vectordb, optimized for high-dimensional similarity search
3. **Retrieval**: Query embeddings enable rapid similarity search to find semantically relevant information, even without shared keywords

## Retrieval Augmented Generation (RAG)

[[RAG]] combines retrieval mechanisms with generative models to enhance response accuracy and contextual relevance:

- **Retrieval Phase**: Searches corpus or vector store for relevant information
- **Generation Phase**: Retrieved context is fed into the generative model to synthesize informed responses

RAG is especially valuable for incorporating domain-specific or organization-specific policies and information beyond the model's training data.

### Semantic Experience Memory

Extends RAG by storing embeddings of all previous interactions, not just external documents. Each user input is vectorized and searched against the memory store of past interactions. This allows agents to:
- Maintain context across sessions (avoiding "blank slate" starts)
- Retrieve relevant past interactions even without keyword matches
- Personalize responses based on accumulated experience

## Graph RAG and Knowledge Graphs

[[Graph RAG]] extends traditional RAG by integrating [[Knowledge Graph]] structures to manage complex interrelationships between information elements.

### Architecture Components

1. **Knowledge Graph**: Stores entities (nodes) and relationships (edges) explicitly
2. **Retrieval System**: Queries graphs to extract subgraphs or clusters relevant to the query
3. **Generative Model**: Synthesizes graph-structured data into coherent responses

**Advantages:**
- Handles multi-hop relationships (entities connected through intermediate nodes)
- Captures rich contextual dependencies lost in flat vector retrieval
- Enables reasoning over structured relationships

### Building Knowledge Graphs

The construction process involves:
- **Data Collection**: Gathering from databases, documents, and user-generated content
- **Data Preprocessing**: Cleaning, deduplication, and standardization
- **Entity Recognition**: Identifying nodes (people, places, concepts) using [[Named Entity Recognition]]
- **Relationship Extraction**: Determining edges between entities
- **Ontology Design**: Defining schema for entity types and possible relationships
- **Graph Population**: Creating nodes and edges in graph databases (Neo4j, Amazon Neptune)
- **Integration and Validation**: Linking external data, resolving entity duplication
- **Maintenance**: Continuous updates as new knowledge emerges

### Dynamic Knowledge Graphs

**Promise:**
- Real-time information integration (news, social media, monitoring systems)
- Adaptive learning without periodic retraining
- Structured reasoning over evolving data

**Perils:**
- **Maintenance Complexity**: Continuous updates risk propagating errors
- **Resource Intensity**: Computational demands grow with graph complexity
- **Security Concerns**: Real-time integration of sensitive data requires strict controls
- **Overreliance Risk**: Automated decisions may miss external factors not captured in the graph

## Working Memory

[[Working Memory]] serves as temporary storage for immediate data manipulation, analogous to human short-term memory. It's crucial for tasks requiring step-by-step reasoning and dynamic decision-making.

### Whiteboards and Scratchpads

Digital **whiteboards** (or scratchpads) provide flexible canvases for intermediate computation:
- Store temporary data during multi-step problem solving
- Allow agents to manipulate information dynamically
- Enable "thinking step-by-step" across modalities
- Essential for complex computations and program prediction

### Note Taking

The **self-note** approach prompts the model to annotate input context with explanatory notes before answering:
1. Model generates notes on context sections
2. Model generates notes on the question itself
3. Model produces final answer using annotated context

This mimics human margin notes and summarization, improving performance on reasoning and evaluation tasks compared to direct question-answering or simple [[Chain of Thought]] approaches.

## Conceitos Relacionados
- [[AI Agents]]
- [[Context Window]]
- [[Embeddings]]
- [[Vector Store]]
- [[RAG]]
- [[Knowledge Graph]]
- [[Graph RAG]]
- [[Working Memory]]
- [[LLM]]
- [[Semantic Search]]
- [[Named Entity Recognition]]
- [[Chain of Thought]]
- [[LangGraph]]
