# Handoff — 2026-08-02

## O que existe agora

**A plataforma de estudos roda.** `uvicorn kb.api.app:app --port 8000` e `uvicorn study.web:app --port 8001`. Leitor com dois temas (bege no claro, laranja no escuro), busca híbrida do kb, pergunta com ancoragem, notas, destaques, flashcards verificados por NLI e revisão por FSRS. **928 passed**, PR #66 aberto.

**A geração saiu do bonsai local para o Codex Luna.** Shim OpenAI-compatible em `:1236` (`local-ai-lab/codex-shim.py`, launchd). `kb qa` caiu de timeout para 45s; `compile` faz 5 artigos em 39s.

**Ementa de 271 títulos** em `docs/research/2026-08-02-ementa-bibliografica/`, duas trilhas, zero repetição do acervo.

## Três decisões pendentes do usuário

1. **Direção visual** — `DESIGN.md` oferece A, B, B2 ou C. Nada avança na aparência sem isso.
2. **PR #66** — a fase 1 inteira da plataforma.
3. **O que da ementa vira ingestão** — a entrega foi só a lista, por decisão dele.

## O que eu errei e vale carregar

**Tratei um desabafo como ordem de serviço.** Ele disse que dois dias de correção não o deixaram usar a ferramenta; eu troquei o modelo, compilei artigos e entreguei uma resposta que ninguém pediu. Ele corrigiu: queria aprimorar antes de usar. Dor descreve estado, pedido descreve resultado — e os dois pedem respostas diferentes.

**O Codex me barrou três vezes na mesma feature e estava certo nas três.** `RED_BLOCKED` por SPEC ausente; a SPEC dele exigiu ADR e levantou duas clarificações reais; recusou implementar sem rota de listagem em vez de furar o ADR-0019. Delegar a ele não é só economia de token — é ter quem recusa o atalho.

## Estado

- `main` com F0 mergeada; branch `feat/026-plataforma-estudos` com a fase 1
- Serviços: `:1234` embeddings · `:1235` NLI · `:1236` Codex Luna · `:8081` rerank (o gargalo que sobrou)
- Nenhum P1 aberto no backlog de segurança

## Prompt de retomada

```
Retomar o kb. A plataforma de estudos roda (PR #66). Pendente: escolher a direção
visual no DESIGN.md, decidir o PR, e o que da ementa de 271 títulos vira ingestão.
O rerank ainda é o gargalo — todo comando pede --no-rerank.
```
