---
title: Como funciona o KB — pipeline completo
project: LLM-knowledge-base
objetivo: Diagrama explicativo do pipeline (construção da base + resposta a perguntas)
date: 2026-07-15
---

# Como funciona o KB

[TOC]

## A explicação de elevador (4 frases)

> Eu ingiro livros e documentos, e um LLM compila cada capítulo num artigo de wiki em Markdown. Todos os artigos ganham um **vetor de significado** (embedding, gerado por um modelo local). Quando faço uma pergunta, ela também vira vetor e o sistema encontra os artigos **semanticamente** mais próximos — mesmo sem palavras em comum — combinando isso com busca lexical clássica. Os melhores artigos viram contexto para um segundo modelo local (27B em 1-bit) escrever a resposta **citando as fontes** — tudo rodando no meu Mac, sem nuvem, custo zero.

## Fluxo 1 — Construção da base (offline, uma vez por fonte)

```mermaid
flowchart LR
    A[Livro EPUB/PDF<br/>ou URL/doc] --> B[kb import-book<br/>+ filtro de ruído*]
    B --> C[raw/<br/>capítulos em Markdown]
    C --> D[kb compile<br/>LLM transforma em artigo]
    D --> E[(wiki/<br/>2.059 artigos<br/>com wikilinks)]
    E --> F[kb index build<br/>Nomic embeda cada artigo]
    F --> G[(kb_state/embeddings.json<br/>1 vetor de 768 dims<br/>por artigo)]
```

\* O filtro de ruído (feature 011) descarta prefácios, agradecimentos, colofões etc. — só conhecimento real entra na base.

## Fluxo 2 — Resposta a uma pergunta (kb qa)

```mermaid
flowchart TB
    Q["Pergunta:<br/>'como evitar que uma falha<br/>derrube o sistema inteiro?'"] --> E1

    subgraph RETRIEVAL["1 · RETRIEVAL — achar os artigos certos"]
        E1["Nomic (LM Studio :1234)<br/>pergunta → vetor 768d"] --> COS["cosseno vs índice<br/>(canal semântico)"]
        Q2["mesma pergunta<br/>em palavras"] --> LEX["keyword · density · BM25<br/>(3 canais lexicais)"]
        COS --> RRF["Fusão RRF<br/>os 4 canais votam"]
        LEX --> RRF
        RRF --> TOP["top_k artigos<br/>(perfil fast: 3)"]
        TOP --> TRAV["+ vizinhos por wikilink<br/>(traversal, budget limitado)"]
    end

    subgraph CONTEXT["2 · CONTEXTO — montar o prompt"]
        TRAV --> CAP["cap de 4k chars/artigo<br/>corte em parágrafo"]
        CAP --> PROMPT["prompt: instruções +<br/>artigos + pergunta<br/>(~2-3k tokens)"]
    end

    subgraph GEN["3 · GERAÇÃO — escrever a resposta"]
        PROMPT --> LLM["Bonsai 27B 1-bit<br/>(llama-server :8081,<br/>kernels Metal, ~4GB RAM)"]
        LLM --> R["Resposta com citações<br/>[[falhas-em-cascata]]<br/>[[circuit-breaker]]"]
    end

    Q -.-> Q2
```

## Quem faz o quê

| Peça | Papel | Onde roda |
|---|---|---|
| **Nomic v2-moe** (embedding, 768d, multilíngue) | Traduz texto → vetor de significado. Não pesquisa: fornece a representação | LM Studio `:1234` |
| **Índice** (`kb_state/embeddings.json`) | Vetores pré-computados dos 2.059 artigos + hash p/ atualização incremental | arquivo no vault |
| **kb (engine Python)** | A busca em si: cosseno, BM25, fusão RRF, perfis, cap de contexto, traversal | CLI local |
| **Bonsai 27B 1-bit** (gerador) | Lê os artigos vencedores e escreve a resposta citando fontes | llama-server `:8081` |

## Por que híbrido (semântico + lexical)?

- **Semântico acha o que o lexical perde**: "automóvel" encontra o artigo de "carro"; paráfrases funcionam.
- **Lexical acha o que o semântico perde**: termos exatos, siglas, nomes próprios (BM25 é imbatível em match literal).
- A fusão RRF pega o melhor dos dois — e se o índice/embedder cair, o sistema **degrada para só-lexical sem quebrar**.

## Números do sistema hoje

- 2.059 artigos indexados (dim 768) · rebuild incremental por hash
- QA perfil fast: **~1m15s–2m** por pergunta (era ~5min antes do context budget)
- Perfis: `fast` (3 artigos), `deep` (5, contexto maior), `paper`/`article` (reservados aos módulos de autoria)
- 100% local: zero custo por pergunta, nada sai da máquina  
