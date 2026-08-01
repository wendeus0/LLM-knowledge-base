# Handoff — 2026-08-01 (fim de sessão)

## O que fechou

**Feature 023 — verificação de ancoragem: `DELIVERED`.** 8/8 tasks `passing`. Da SPEC ao serviço rodando: `kb qa` agora classifica cada afirmação em `ancorada`/`contradita`/`sem apoio`, sem nunca bloquear a resposta. PRs #61 e #62 mergeados.

**Serviço NLI em `:1235`** — `local-ai-lab/nli-server.py`, LaunchAgent `com.wendeus.kb-nli` com KeepAlive. Ressurreição provada com `kill -9`. Contrato validado: negação → contradição 0,998.

**Holdout congelado** — 12 pares artigo→fonte em 6 domínios, cada trecho validado byte a byte. Manifest privado em `.holdout/` (gitignored); `HOLDOUT.md` com hashes no repo. Saiu de zero, que era a limitação mais registrada da feature.

**Skill `test-appeasement-audit`** no harness — detector AST + julgamento por evidência + gate de CI com ratchet. Reusável em qualquer repo Python: 1 arquivo + 1 linha de CI.

**F-03 fechado (PR #63)** — o último P1 do backlog de segurança. Os quatro caminhos de egresso do kb agora ou não podem ser desviados por proxy, ou passam pelo gate de conteúdo sensível.

## O que aprendi e vale carregar

**O guard valida a URL, não o caminho.** Duas vezes, em dois transportes: `urllib` segue redirect carregando o `Authorization`; `httpx` proxia `localhost` se `HTTP_PROXY` estiver setado (medido). Nos dois casos o achado veio de review externo, não meu.

**Código feito para passar em teste é padrão, não acidente.** Quatro ocorrências documentadas no kb. O gate mecânico agora quebra o CI quando reaparece — e o `getattr` que passou por mim, pelo Codex e por 4 revisores automáticos ontem seria exit 1 hoje.

## Estado

- `main` em **869 passed**, zero PRs abertos
- Backlog de segurança: nenhum P1 aberto (F-06, F-08 seguem P2)
- Serviços locais: `:1234` embeddings, `:8081` rerank, `:1235` NLI — os três no launchd

## Próximo passo natural

**Ticket 006 — reagrupamento por tema.** É a maior decisão de produto pendente do map e destrava o estágio 1 da pilha (cobertura por centroide, medido e aprovado, sem SPEC porque depende dessa decisão). Exige grilling interativo — não delegável.

Alternativa se quiser algo mecânico: espalhar o gate de appeasement para outros repos, ou os F-06/F-08 (P2, pisos de dependência com CVE e symlink na wiki).

## Prompt de retomada

```
Retomar o kb. Feature 023 entregue, F-03 fechado, main em 869 passed sem PRs
abertos. Próximo: grilling do ticket 006 (reagrupamento por tema) — é decisão
de produto e destrava o estágio 1 da pilha de verificação.
```
