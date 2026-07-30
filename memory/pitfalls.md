---
name: Pitfalls
description: Armadilhas técnicas recorrentes (append-only)
type: project
---

## Armadilhas a evitar

### P1: Editar wiki manualmente

**Problema:** Se você editar markdown direto, LLM não sabe e pode sobrescrever.

**Solução:** Use CLI (`kb compile`, `kb qa -f`, `kb heal`) — sempre via LLM.

---

### P2: Esquecer .env

**Problema:** Sem KB_API_KEY, todos os comandos falham silenciosamente.

**Solução:** Sempre `cp .env.example .env` e preencher antes de usar.

---

### P3: Esperar TF-IDF escalar infinito

**Problema:** Com >1000 artigos, TF-IDF fica lento e impreciso.

**Solução:** Monitorar tamanho de wiki/. Ao passar 500 artigos, planejar migração para embeddings.

---

### P4: Wikilinks com espaços/caracteres especiais

**Problema:** `[[SQL Injection]]` vs `[[SQL injection]]` — slug diferente.

**Solução:** LLM gera slugs consistentes em compile. Heal detecta quebrados.

---

### P5: Git push sem branch

**Problema:** trabalho local feito em `main` vira tentação de commitar/pushar direto e dificulta revisão.

**Solução:** crie branch de feature antes de commitar qualquer frente relevante. Mesmo em fluxo solo, use branch + PR quando houver diff não trivial.

---

### P6: Heal deletar artigos importantes

**Problema:** Heal autodetecta stubs vazios e deleta. Se foi acidental, perdeu.

**Solução:** Git preserva histórico. Antes de usar heal, fazer commit ou backup.

---

### P7: LLM alucinando referências

**Problema:** LLM adiciona `[[ConceituoQueNaoExiste]]` em wikilinks.

**Solução:** Lint detecta wikilinks quebrados. Heal remove refs inválidas.

---

### P8: LLM envolvendo output em code fences

**Problema:** LLM retorna conteúdo de `compile` envolvido em ` ```markdown ` ou ` ``` `, corrompendo o frontmatter YAML dos artigos da wiki.

**Causa raiz:** Exemplos de formato no SYSTEM prompt que usam ` ``` ` ensinam o modelo a envolver a resposta em fences.

**Solução (dupla):** (1) SYSTEM prompt explicitamente instrui "SEM code fences"; (2) `_strip_outer_fence()` em `compile.py` remove fences defensivamente após cada chamada.

**Sinal de alerta:** Artigos que começam com ` ```markdown ` em vez de `---` no frontmatter.

---

### P9: Falso positivo de guardrail em código técnico

**Problema:** Nome de variável `OPENAI_API_KEY` em exemplos de código de livros técnicos dispara `SensitiveContentError`.

**Mitigação atual:** `--allow-sensitive` para livros técnicos com exemplos de código.

**Solução futura:** guardrail contextual que ignora padrões em blocos de código markdown.

---

### P10: Overfitting de testes em parser/helper interno

**Problema:** testes de `book_import_core` ficam frágeis quando fixam whitespace exato, ordem incidental ou estruturas intermediárias do parser.

**Solução:** para EPUB/PDF, teste contrato observável: `toc_source`, `chapter_source`, categorias de erro estáveis, precedência entre fontes e presença de fragmentos relevantes de conteúdo.

---

## Padrões que funcionam

✓ Ingest → compile 1:N (um documento pode gerar vários artigos)
✓ File-back → novo artigo, não overwrite existente
✓ Heal aleatório mantém wiki fresca sem custo de full scan
✓ TF-IDF + relevância semântica coexistem bem (sem embeddings)
✓ Git automático = zero conflitos se LLM segue estratégia (append/update)

## Sessão 2026-07-15/16 (stack local)

- **Modelos reasoning (qwen3.5/Bonsai) devolvem `content` vazio** se o thinking não for desligado — sinal: `usage` conta tokens mas resposta vazia; mitigação: `--chat-template-kwargs '{"enable_thinking":false}'` no llama-server (o `--reasoning-budget 0` sozinho NÃO basta).
- **`kb` sem `KB_DATA_DIR` cai no repo silenciosamente** ("Nenhum contexto relevante" em vault cheio) — resolvido com `.env`, mas o sinal engana: parece corpus vazio, é path errado.
- **MLX 1-bit não roda em runtime nenhum de fábrica** (LM Studio, mlx-lm oficial) — só nos forks PrismML; compilar o fork MLX exige Xcode completo (compilador `metal` não vem no CLT, mesmo em modo JIT).
- **Trocar modelo de embedding exige rebuild do índice** — o gate de integridade (012) detecta e degrada p/ lexical, mas a busca fica pior em silêncio; conferir `kb index status` após mexer em modelos.
- **ubatch maior nem sempre ajuda**: 1024 deu +29% de pp; 2048 PIOROU (pressão de memória em 16GB) — sempre medir, nunca extrapolar.

## Sessão 2026-07-29/30 — armadilhas de medição e isolamento

### Fixture que isola metade do estado é pior que não isolar

`tmp_wiki` isolava `WIKI_DIR` mas não `STATE_DIR`. Enquanto nada escrevia em `kb_state/` durante testes, ninguém notou. Quando a feature 015 pendurou refresh de índice no `heal`, um teste passou a **reconstruir o índice do vault real a partir de uma wiki temporária de 1 artigo** — 1.037 vetores viraram 1, e a suíte continuou verde.

**Detecção:** grave um sentinela no artefato real, rode a suíte, confira se sobreviveu. `tests/unit/test_conftest_isolation.py` é a guarda permanente.

### Default silencioso em parâmetro de modo

`search(mode=...)` só tratava `"keyword"`; qualquer outro valor caía no híbrido. `--mode lexical` mediu híbrido, e a "comparação" produziu dois números idênticos que eu quase reportei como resultado. **Valor desconhecido deve levantar, não escolher por você.**

### Medição contra provider morto devolve a baseline, não erro

Rerank degrada para a ordem original quando o LLM falha — correto por design. Consequência: com o provider fora, 152 chamadas falharam e o bench reportou exatamente o número da baseline. **Parecia válido.** Só o contador `failed` da instrumentação revelou. Preflight antes do lote é o mínimo; ele não cobre "morreu no meio".

### Cache tem de incluir tudo que muda a resposta

A chave do cache de rerank incluía modelo e candidatos, mas não os parâmetros de sampling. Medir o efeito de temperatura 0 teria reusado respostas geradas a 0,8 — conclusão sobre o cache, disfarçada de conclusão sobre sampling.

### Omissão e alucinação são modos de falha distintos, e só um é configurável

O rerank descartava índice inválido, duplicado e omitido **em silêncio**. Instrumentar mostrou que:

- **omissão** (modelo devolve menos posições) é largamente artefato de temperatura — no bonsai, cobertura foi de 75% para 93% com temp 0;
- **alucinação de índice** (citar o candidato 23 numa lista de 20) é determinística — o granite4 manteve 32 inválidos sob decodificação gulosa.

Cobertura alta com índices inventados é **pior que triagem parcial confiável**, e pior que não reordenar. O modo de falha domina a taxa de falha.

### Golden set por título superestima em ~2×

Semear casos de avaliação usando o título do artigo como pergunta mede casamento de string. Deu `recall@5 = 0,860`; com 50 perguntas conceituais escritas à mão, a realidade era `0,420`. Qualquer decisão tomada sobre o primeiro número partiria de premissa errada.

### Amostra pequena esconde ruído como resultado

Três experimentos seguidos deram deltas de 1 a 2 casos em 50 — dentro do erro padrão de ~7pp. Ampliar para 152 casos (erro ~4pp) foi o que permitiu distinguir o ganho do rerank. **Instrumento antes de experimento.**

### Substituição em lote sem dry-run corrompe import

Script automatizado trocou `from kb.client import ... is_provider_resource_limit_error` por `from kb.sampling import ...` e inseriu import com indentação inválida. `core/rules/workflow-feature.md` § "mudança ampla e mecânica" exige dry-run e conferência de diffstat justamente para isso.
