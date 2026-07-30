# DOMAIN — 011 KB app visual + módulos de autoria + higiene de corpus + RAG local

> Grilling em andamento (grill-with-docs, 2026-07-15). Roadmap multi-frente; pode ser fatiado em features separadas na fase de SPEC.

## Glossário

| Termo | Definição |
|-------|-----------|
| KB (app) | Interface gráfica própria, independente do Obsidian, para navegar os MDs da wiki, fazer perguntas (QA) e disparar geração de papers/artigos. Possível rename do repo `LLM-knowledge-base` → `KB` |
| Paper | Documento simples e objetivo sobre um tema, gerado a partir da wiki + fontes originais (`raw/`) |
| Artigo robusto | Documento mais profundo com número mínimo X de referências **bibliográficas reais** (autor, título, capítulo — formato acadêmico) |
| Referência bibliográfica real | Citação da fonte original ingerida (livro/paper), não wikilink interno — exige metadados de origem por trecho |
| Ruído de corpus | Capítulos sem conteúdo de conhecimento: agradecimentos, dedicatórias, **prefácios**, **capítulos de encerramento**, **elogios/endorsements** (praise), colofão e correlatos (delta 2026-07-15: prefácios já aparecem com frequência no vault atual) |
| Retrieval híbrido | BM25 + embeddings + grafo com fallback progressivo — já decidido no ADR-0013 (Fase 2 do rollout) |
| Modelo de embedding local | Família Nomic (ex.: nomic-embed-text) via Ollama, disponível no Mac e na VM Godwin |

## Decisões fechadas (onda A, 2026-07-15)

1. **Visual = app próprio, não Obsidian.** Web UI local é o mecanismo aceito como ponto de partida (`kb serve`), mas a visão do dono é um aplicativo com interface própria — possivelmente nativo em Swift (dono migrou para iOS). Funções do app: abrir/renderizar os MDs, processar perguntas, criar papers/artigos, e retornar artigo existente quando a pergunta já foi respondida. Referências de inspiração (externas, não-verificadas): `github.com/nashsu/llm_wiki` e gist do Karpathy (`442a6bf555914893e9891c11519de94f`).
2. **Fonte dos módulos de autoria:** wiki + fontes originais (`raw/`) — sem pesquisa externa na v1.
3. **Referências do artigo robusto:** bibliográficas reais (formato acadêmico), o que exige rastreabilidade de origem por trecho.
4. **Corte de ruído:** na importação (`import-book` classifica e exclui capítulos-ruído, com override) **+ comando retroativo** para varrer/arquivar o ruído já ingerido no corpus existente. Taxonomia de ruído confirmada pelo dono: agradecimentos, dedicatórias, prefácios, capítulos de encerramento, elogios/endorsements, colofão e correlatos.
5. **Possível rename do repo** `LLM-knowledge-base` → `KB` (a confirmar formalização).

## Decisões fechadas (onda B, 2026-07-15)

6. **Arquitetura app↔engine:** a engine ganha API HTTP; o app (Swift ou web) é cliente. A API será servida num **terceiro servidor** — nem o Mac, nem a VM Godwin (detalhes do servidor em aberto).
7. **Citação bibliográfica:** granularidade livro + capítulo (autor, título, capítulo) — compatível com os metadados que o `import-book` já carrega, consistente entre EPUB e PDF.
8. **Índice de embeddings:** por vault, local à máquina que hospeda o vault (a reconciliar com a decisão 6 — se a engine vive no terceiro servidor, o vault principal e seu índice vivem lá).

## Decisões fechadas (onda C, 2026-07-15)

9. **Vault principal vive junto da engine no terceiro servidor** (engine + API + vault + índice de embeddings); Mac e iPhone são clientes. Ingestão de livros passa a ser via API/upload.
10. **X de referências:** configurável (`--min-refs`), default 5, como gate de validação (artigo falha se não atingir).
11. **IAs locais:** ambos os mundos — engine kb (heal/lint/classificação de capítulos/embeddings com modelo local pequeno) e harness AI-dotfiles (roteamento via `local-llm-router`), sobre a mesma infra Ollama (Mac + VM Godwin + servidor novo).
12. **Prioridade #1 do roadmap:** corte de ruído + RAG/embeddings (higiene do corpus e retrieval semântico antes do app e dos módulos de autoria).

## Invariantes (deltas)

- Nenhum capítulo classificado como ruído (agradecimentos, dedicatória, colofão etc.) entra em `raw/` sem override explícito.
- Artigo robusto sem ≥ X referências bibliográficas reais não passa validação (mesmo padrão fail-closed da validação de compile).
- Separação engine × corpus preservada (CONTEXT.md): o app/API não grava na wiki fora do fluxo da engine.
- Retrieval híbrido degrada progressivamente (ADR-0013): sem índice de embeddings disponível, search/qa continuam via BM25.

## Inspirações externas (não-confiáveis até verificação de adoção)

- `github.com/nashsu/llm_wiki` + gist Karpathy `442a6bf5...` — referências da visão de wiki mantida por LLM com interface própria.
- `github.com/Graphify-Labs/graphify` (MIT, Python + tree-sitter) — knowledge graph **sem embeddings** (traversal real, comunidades Leiden, edges EXTRACTED/INFERRED, visualização HTML interativa força-direcionada). Dono ouviu boas referências; candidato a absorção de ferramenta/know-how no app. Encaixe natural: eixo relacional (grafo) do retrieval híbrido do ADR-0013 + visualização do app. Adoção formal deve passar por `capability-adoption-loop` (pin de commit, varredura).

## Refs cruzadas

- ADR-0013 (claim-centric + retrieval híbrido) — o pedido de RAG/embeddings é a execução da Fase 2, não decisão nova
- ADR-0004 (keyword search) — superado em parte pelo 0013; sem conflito novo
- ADR-0009 (outputs store) — candidato a lar dos papers/artigos gerados
- ADR-0012 (compatibilidade provider/modelo) — base para modelos locais via endpoint OpenAI-compat (Ollama)
- Feature 010 (multi-vault, draft) — interage com onde vive o índice vetorial e qual vault o app serve
- `kb/templates/` + override por vault — infra reutilizável para templates de paper/artigo
- PENDING_LOG P2 "Embeddings + RAG híbrido" (2026-04-03) — este roadmap o executa

## Aberto (fica para spec-clarify / design da fase respectiva)

- Detalhes do terceiro servidor (provedor, specs, GPU para Ollama, exposição de rede/auth da API)
- App cliente: Swift nativo (iOS/macOS) vs web — o dono tende a Swift ("talvez"), decisão da fase do app
- Formalização do rename `LLM-knowledge-base` → `KB` (dono sinalizou intenção)
- Formato de citação acadêmica (ABNT/APA/livre) — detalhe da SPEC dos módulos de autoria
- Adoção do graphify (absorver ferramenta vs know-how) — passa por capability-adoption-loop na fase do app/grafo
