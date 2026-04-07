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

**Problema:** Tudo é commitado em `main` sem branches.

**Solução:** Para kb em solo mode, tudo em main é OK. Se colab, criar branches de feature.

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

**Problema:** LLM retorna conteúdo de `compile` envolvido em `` ```markdown `` ou `` ``` ``, corrompendo o frontmatter YAML dos artigos da wiki.

**Causa raiz:** Exemplos de formato no SYSTEM prompt que usam `` ``` `` ensinam o modelo a envolver a resposta em fences.

**Solução (dupla):** (1) SYSTEM prompt explicitamente instrui "SEM code fences"; (2) `_strip_outer_fence()` em `compile.py` remove fences defensivamente após cada chamada.

**Sinal de alerta:** Artigos que começam com `` ```markdown `` em vez de `---` no frontmatter.

---

### P9: Falso positivo de guardrail em código técnico

**Problema:** Nome de variável `OPENAI_API_KEY` em exemplos de código de livros técnicos dispara `SensitiveContentError`.

**Mitigação atual:** `--allow-sensitive` para livros técnicos com exemplos de código.

**Solução futura:** guardrail contextual que ignora padrões em blocos de código markdown.

---

## Padrões que funcionam

✓ Ingest → compile 1:N (um documento pode gerar vários artigos)
✓ File-back → novo artigo, não overwrite existente
✓ Heal aleatório mantém wiki fresca sem custo de full scan
✓ TF-IDF + relevância semântica coexistem bem (sem embeddings)
✓ Git automático = zero conflitos se LLM segue estratégia (append/update)
