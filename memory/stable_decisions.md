---
name: Stable Decisions
description: Decisões arquiteturais fixas (append-only)
type: project
---

## Decisões fixas (não reconsiderar sem motivo forte)

### D1: LLM responsável por tudo que vai para `wiki/`

**Why:** O principal insight do projeto é usar o LLM para compilar, enriquecer e manter a wiki.

**How to apply:** Toda escrita em `wiki/` permanece concentrada em `compile`, `heal` e `qa --file-back`.

---

### D2: Commits de mutação são controlados por comando, padrão local sem commit

**Why:** Rastreabilidade é importante, mas workflows exploratórios e via Obsidian precisam de write local frequente sem poluir histórico Git. ADR-0016 formalizou modo local por padrão.

**How to apply:** novos fluxos operam em modo local por padrão. `--commit` ativa versionamento explícito por execução; `--no-commit` permanece aceito por compatibilidade.

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

**Why:** Wikilinks, frontmatter YAML e estrutura de pastas são uma interface humana e portátil excelente.

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

---

### D10: `qa` deve rotear por fonte nativa antes de responder

**Why:** Nem toda pergunta deve depender só da wiki; o produto distingue `wiki`, `raw`, `knowledge` e `learnings`.

**How to apply:** Evoluções do `qa` devem preservar roteamento explícito e auditável antes de considerar soluções mais complexas.

---

### D11: controles sensíveis e de commit são explícitos por comando

**Why:** Segurança e rastreabilidade seguras por padrão, com escape hatch apenas consciente e local à execução. Consolidado em ADR-0016.

**How to apply:** `--allow-sensitive` e `--commit` são flags por comando; não introduzir configuração global persistente sem nova decisão arquitetural.

---

### D12: defesa dupla para qualidade de output do LLM em `compile`

**Why:** O LLM pode envolver output em code fences mesmo com instrução explícita.

**How to apply:** Toda geração de conteúdo via `compile` aplica `_strip_outer_fence()` após a resposta do LLM, além de instruções explícitas no SYSTEM prompt.

---

### D13: Paralelismo seguro em `compile` usa geração paralela e persistência serial

**Why:** estado global não é seguro para escrita concorrente, mas a geração LLM é paralelizável.

**How to apply:** `compile_many()` paraleliza apenas a fase de geração. Toda persistência e atualização de estado permanece serial e determinística.

---

### D14: Contratos de `book_import_core` favorecem precedência explícita e erro estável

**Why:** importação de EPUB/PDF ficou mais confiável quando as heurísticas ambíguas foram reduzidas.

**How to apply:** em EPUB, `nav` é a fonte canônica de TOC antes de `ncx`; resolução de imagem deve preferir caminho completo/normalizado e devolver `None` em basename ambíguo; em PDF com OCR, sucesso sem texto deve manter o erro estável.

---

### D15: Runtime topic taxonomy (ADR-0015)

**Why:** TOPICS hardcoded não escala com o corpus do usuário. Taxonomia derivável em runtime é mais flexível.

**How to apply:** `KB_TOPICS` env var configura a taxonomia em runtime; quando vazia, a engine usa defaults históricos. compile/qa consomem helpers de config para prompts e resolução de diretório wiki.
