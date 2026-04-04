---
name: Stable Decisions
description: Decisões arquiteturais fixas (append-only)
type: project
---

## Decisões fixas (não reconsiderar sem motivo forte)

### D1: LLM responsável por tudo que vai para `wiki/`

**Why:** O principal insight do projeto continua sendo usar o LLM para compilar, enriquecer e manter a wiki.

**How to apply:** Toda escrita em `wiki/` permanece concentrada em `compile`, `heal` e `qa --file-back`.

---

### D2: Git automático em todo write da wiki

**Why:** Mantém rastreabilidade e recuperação simples quando a wiki é mutada por automação.

**How to apply:** `compile`, `heal` e `qa --file-back` continuam chamando `git.commit()`. Falha de git não deve derrubar o fluxo principal.

---

### D3: Stochastic heal (não determinístico)

**Why:** Escala melhor do que reprocessar toda a wiki a cada execução.

**How to apply:** `kb heal --n 10` permanece o padrão operacional para manutenção incremental.

---

### D4: Busca lexical simples antes de embeddings

**Why:** A escala atual não justifica complexidade extra.

**How to apply:** Embeddings só entram quando o tamanho/qualidade da busca lexical deixarem de ser suficientes.

---

### D5: Obsidian-first markdown

**Why:** Wikilinks, frontmatter YAML e estrutura de pastas continuam sendo uma interface humana e portátil excelente.

**How to apply:** Saída compilada deve continuar compatível com Obsidian por padrão.

---

### D6: `kb` é a source of truth para importação de livros

**Why:** Evita divergência entre laboratório e produto.

**How to apply:** O núcleo canônico mora em `kb/book_import_core.py`; `book2md` atua como compat layer/laboratório.

---

### D7: `raw/books/` é o destino estrutural de importação de livros

**Why:** Separa ingestão estrutural da publicação final na wiki.

**How to apply:** `kb import-book` escreve capítulos e `metadata.json` em `raw/books/<livro>/`; `kb compile` pode promover esses capítulos para `wiki/`.

---

### D8: Recursos LLM são opcionais no ambiente, não no desenho do produto

**Why:** A importação de livros deve funcionar sem dependências extras, enquanto `compile/qa/heal/lint` continuam sendo capacidades assistidas por LLM.

**How to apply:** `openai` fica em `.[llm]`; o import em `kb.client` é lazy e os comandos LLM falham com mensagem explícita se o extra não estiver instalado.

---

### D9: OpenCode Go usa nome simples de modelo, sem prefixo

**Why:** O provider rejeita formatos como `opencode-go/kimi-k2.5`.

**How to apply:** Para `KB_BASE_URL=https://opencode.ai/zen/go/v1`, aceitar `kimi-k2.5`, `minimax-2.7` e `glm-5`; validar antes da chamada ao provider.
