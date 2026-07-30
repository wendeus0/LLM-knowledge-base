---
title: Retrieval semântico — embeddings locais Nomic no search/qa híbrido
epic: search
status: done
pr:
---

# Retrieval semântico — embeddings locais Nomic no search/qa híbrido

## Objetivo

Hoje `kb search`/`kb qa` recuperam artigos só por sinal lexical (keyword + density + BM25 fundidos por RRF) — "carro" não encontra "automóvel", e perguntas parafraseadas perdem artigos relevantes. O sistema deve ganhar um canal semântico (embeddings gerados por modelo local Nomic via Ollama) fundido aos canais lexicais, com **degradação progressiva**: sem índice ou sem Ollama, tudo funciona como hoje.

Fatia 2 do roadmap grillado (`features/011-corpus-noise-filter/DOMAIN.md`, decisões 8 e 12) — executa a Fase 2 do ADR-0013 e fecha o item P2 "Embeddings + RAG híbrido" do PENDING_LOG (2026-04-03).

Verificação viva (2026-07-15): Ollama ativo no Mac com `nomic-embed-text-v2-moe:latest` disponível.

## Requisitos funcionais

- [x] RF-01: `kb index build` gera o índice de embeddings do vault (um vetor por artigo da wiki) em `kb_state/`, reportando quantos artigos foram indexados
- [x] RF-02: reexecução de `kb index build` é incremental — só artigos novos ou alterados são re-embedados; artigos removidos saem do índice; corpus inalterado → "0 a indexar"
- [x] RF-03: `kb index status` mostra cobertura (indexados/total), modelo usado e artigos pendentes (stale)
- [x] RF-04: com índice presente, `kb search` retorna artigos semanticamente relacionados mesmo sem overlap lexical com a query (canal semântico entra na fusão RRF junto aos canais existentes)
- [x] RF-05: sem índice (ou índice vazio), `kb search`/`kb qa` retornam exatamente o resultado lexical atual, sem erro — degradação silenciosa no search, com nota informativa no `index status`
- [x] RF-06: `kb qa` usa o mesmo retrieval híbrido (via `find_relevant`), herdando o canal semântico automaticamente
- [x] RF-07: modelo e endpoint de embedding configuráveis por env (`KB_EMBED_MODEL`, `KB_EMBED_BASE_URL`), com defaults para Ollama local + Nomic
- [x] RF-08: índice gravado com metadados de integridade (modelo, dimensão); consulta com índice de modelo/dimensão divergente do configurado ignora o índice (fallback lexical) e `index status` orienta rebuild

## Requisitos técnicos

- Embeddings via endpoint OpenAI-compat (`/v1/embeddings`) do Ollama — separado do `KB_API_KEY`/`BASE_URL` do chat; sem dependência nova (SDK `openai` já é dependência opcional)
- Índice em arquivo único versionável por vault em `kb_state/` (JSON/JSONL com hash do conteúdo por artigo p/ incrementalidade) — brute-force cosine em memória; sem FAISS/sqlite-vec nesta fatia (corpus ~centenas de artigos)
- Granularidade v1: **um embedding por artigo** (título + corpo truncado ao limite do modelo); chunking por seção fica fora desta fatia
- Canal semântico entra como 4º ranking na fusão `_rrf_fuse` existente — não substitui os lexicais
- Arquivos/pastas de infra (`_*`) são ignorados na indexação (mesma convenção do `noise scan` e do `_iter_docs`)
- Separação engine × corpus preservada: índice vive no vault (`kb_state/`), nunca no repo da engine

## Mudanças de API/CLI

- Novo sub-app: `kb index build [--force]` (força re-embed total) e `kb index status`
- `kb search`/`kb qa`: sem mudança de interface — canal semântico é transparente
- Novas env vars: `KB_EMBED_MODEL` (default `nomic-embed-text-v2-moe:latest`), `KB_EMBED_BASE_URL` (default `http://localhost:11434/v1`)

## Testes

- Unit: hash/incrementalidade do índice (novo, alterado, removido, inalterado); cosine similarity com vetores trabalhados à mão; integridade modelo/dimensão; truncamento de corpo
- Integration (embedder fake/monkeypatch — sem rede): `index build` cria índice e reporta contagem; rebuild incremental; `index status`; `search` retorna artigo semanticamente próximo sem overlap lexical (vetores controlados); sem índice → resultado idêntico ao lexical; índice de modelo divergente → ignorado com fallback
- Manual: `kb index build` no vault real (~475 artigos pós-limpeza) + query semântica de controle (ex.: "como evitar que uma falha derrube todo o sistema" deve trazer circuit-breaker/bulkheads) comparando com o resultado lexical

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 8–12h |
| Bloqueador | não |
| Risk | baixa-média (canal aditivo com fallback; risco maior é qualidade do embedding por artigo inteiro, mitigado pelo bench manual) |

## Dependências

- Feature 011 entregue (corpus limpo antes de indexar — evita embedar ruído)
- Ollama com modelo Nomic no host (verificado vivo; ausência degrada para lexical, não bloqueia)

## Notas

**Fora de escopo (fatias futuras do roadmap, ver DOMAIN.md):**
- Chunking por seção/heading (avaliar após bench do embedding por artigo)
- Canal relacional/grafo (3º eixo do ADR-0013; candidato a absorver know-how do graphify)
- Reranker e avaliação automatizada com golden set (`kb index bench`) — medir antes de otimizar
- Índice remoto/servidor (terceiro servidor do roadmap) e integração VM Godwin
- Embeddings nos módulos paper/artigo (features seguintes consomem este canal)

**Casos de erro:**
- Ollama fora do ar durante `index build` → erro claro indicando endpoint/modelo e como subir o serviço; índice pré-existente permanece intacto
- Índice corrompido (JSON inválido) → search/qa degradam para lexical sem crash; `index status` reporta corrupção e orienta rebuild
- Artigo maior que o limite do modelo → truncado com registro no relatório do build (contagem de truncados)

**Open questions:**
- (nenhuma)
