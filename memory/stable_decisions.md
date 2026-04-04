---
name: Stable Decisions
description: Decisões arquiteturais fixas (append-only)
type: project
---

## Decisões fixas (não reconsiderar)

### D1: LLM responsável por TUDO que vai na wiki

**Why:** O principal insight de Karpathy — você nunca escreve a wiki manualmente. O LLM escreve tudo, você apenas fornece raw data e perguntas.

**How to apply:** Toda feature que toque em wiki/ deve ser feita via LLM (compile, heal, qa --file-back, lint).

---

### D2: Git automático em todo write

**Why:** Conflitos resolvem naturalmente se o LLM só append/atualiza seções (Pawel Huryn). Cada escrita é um commit — não há staging manual.

**How to apply:** `compile`, `heal`, `qa --file-back` chamam `git.commit()`. Se falhar, continua silenciosamente (sem git = sem commit).

---

### D3: Stochastic heal (não determinístico)

**Why:** Scale para vaults grandes (1000+ artigos) sem processar tudo. Cada sessão cura N arquivos aleatórios.

**How to apply:** `kb heal --n 10` (ou cron à noite). O LLM encontra connections, remove stubs, stampa `reviewed_at`.

---

### D4: TF-IDF simples, não embeddings

**Why:** Funciona bem até ~100 artigos/~400K palavras. Embeddings adiciona complexidade e latência sem benefício nessa escala.

**How to apply:** Se wiki cresce muito (>500 artigos), considerar migração para FAISS + embeddings.

---

### D5: Obsidian-first markdown

**Why:** Wikilinks `[[conceito]]`, frontmatter YAML, estrutura de pastas — tudo compatível com Obsidian. Wiki é um vault.

**How to apply:** Toda compilação garante wikilinks. Tema de pesquisa = pasta. `_index.md` mantém lista master.

---

### D6: Tópicos fixos iniciais

**Why:** Organizar wiki por domínio. Fácil de expandir depois.

**Topics:** cybersecurity, ai, python, typescript, general (fallback)

**How to apply:** LLM classifica em compile. Helm pode reclassificar.

---

### D7: Sem dependências externas pesadas

**Why:** Manter o projeto lean e portável. Sem FAISS, redis, elasticsearch — só o que é necessário.

**Allowed:** openai, typer, rich, pytest, ruff (dev only)

**How to apply:** Qualquer sugestão de dependência nova precisa de aprovação.

