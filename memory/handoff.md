---
name: Handoff
description: Última sessão (atualizado ao encerrar)
type: project
---

## Sessão — 2026-04-07 (Repo hygiene / corpus extraction)

**O que foi feito:**
- Corpus pessoal extraído do repositório principal para `/home/g0dsssp33d/work/llm-wiki`
- Diretórios `raw/`, `wiki/`, `outputs/` e `kb_state/` removidos do repo principal e realocados para o diretório externo
- `kb/config.py` atualizado para suportar `KB_DATA_DIR` e overrides específicos (`KB_RAW_DIR`, `KB_WIKI_DIR`, `KB_OUTPUTS_DIR`, `KB_STATE_DIR`)
- `.env.example`, README, `docs/OBSIDIAN.md`, `.pi/manifest.yaml`, `AGENTS.md` e `CLAUDE.md` atualizados para separar engine vs. corpus
- `examples/` criado com seed neutro mínimo para onboarding
- `.gitignore` ajustado para não versionar corpus local nem `.obsidian/`
- Fluxo validado após migração: `kb search` passou a ler o corpus em `/home/g0dsssp33d/work/llm-wiki`

**O que falta:**
- Mergear PR#19 (feat/wikilink-traversal → main)
- Corrigir 8 testes falhando em `test_web_ingest.py` (mock setup pré-existente)
- Neutralizar referências históricas restantes a corpus temático pessoal em docs de arquitetura/ADR
- Avaliar tornar `TOPICS` configurável em vez de fixo no código

**Métricas da sessão:**
- Engine e corpus: desacoplados
- Diretório de dados ativo: `/home/g0dsssp33d/work/llm-wiki`
- Seed neutro criado: `examples/raw/getting-started.md`
- Configuração suportada: `KB_DATA_DIR`, `KB_RAW_DIR`, `KB_WIKI_DIR`, `KB_OUTPUTS_DIR`, `KB_STATE_DIR`

**Prompt de retomada:**
> Retome o projeto `kb` após a higienização do repositório. A engine está separada do corpus pessoal, que agora vive em `/home/g0dsssp33d/work/llm-wiki`, e o projeto suporta `KB_DATA_DIR`. Próximas ações: (1) revisar/neutralizar docs históricos ainda acoplados ao corpus antigo; (2) corrigir 8 testes de `test_web_ingest.py`; (3) avaliar tornar `TOPICS` configurável.

---

## Sessão — 2026-04-07 (Obsidian integration close)

**O que foi feito:**
- Integração operacional com Obsidian consolidada usando o plugin `obsidian-terminal`
- A estratégia com `Shell Commands` foi descartada por fragilidade de PATH/working directory e falta de input dinâmico para `qa`
- Profile integrado do plugin configurado com shell login (`/bin/zsh --login` no Linux)
- Fluxo validado no terminal integrado do Obsidian com `kb qa "Como implementar um orquestrador em meu workflow?" --allow-sensitive`
- README atualizado com menção explícita ao plugin adotado e tutorial de uso
- `docs/OBSIDIAN.md` criado com passo a passo operacional completo

**O que falta:**
- Mergear PR#19 (feat/wikilink-traversal → main)
- Corrigir 8 testes falhando em `test_web_ingest.py` (mock setup pré-existente)
- Refinar guardrail para falso positivo de nomes de variável em código técnico
- Opcional: configurar hotkeys/profile defaults no `obsidian-terminal`

**Métricas da sessão:**
- Vault Obsidian: operacional
- Plugin adotado: `obsidian-terminal`
- Comando validado no Obsidian: `kb qa`
- Documentação atualizada: `README.md`, `docs/OBSIDIAN.md`, logs de sessão

**Prompt de retomada:**
> Retome o projeto `kb` após a consolidação da integração com Obsidian. O vault `wiki/` está operacional com `obsidian-terminal`, `kb qa` já rodou com sucesso dentro do Obsidian e o README/tutorial foram atualizados. Próximas ações: (1) mergear PR#19; (2) corrigir 8 testes de `test_web_ingest.py`; (3) refinar o guardrail de sensibilidade para exemplos de código.

---

## Sessão — 2026-04-07 (Sprint close)

**O que foi feito:**
- Smoke test completo com OpenCode Go real: `search`, `lint`, `qa`, `heal`, `import-book --compile` OK
- EPUB "Building Applications with AI Agents" importado → 12 artigos em `wiki/ai/`
- `docs/SENSITIVE_CONTENT_POLICY.md` criado — critérios para `--allow-sensitive` e `--no-commit`
- pytest-cov instalado; 80% cobertura baseline; HTML em `htmlcov/`
- ADR-0001 atualizado — A3 (extração de pacote) rejeitada formalmente
- ADR-0010 criado — defesa dupla para output do LLM (prompt + `_strip_outer_fence()`)
- Root cause de code fence wrapping identificado e corrigido:
  - SYSTEM prompt em `compile.py` atualizado com instrução "SEM code fences"
  - `_strip_outer_fence()` adicionado como defesa defensiva em `compile_file()`
  - 25 artigos em `wiki/ai/` e `wiki/summaries/ai/` corrigidos manualmente
- PR#19 aberto (branch `feat/wikilink-traversal`) com todas as entregas do sprint

**O que falta:**
- Merge PR#19 (feat/wikilink-traversal → main)
- Corrigir 8 testes falhando em `test_web_ingest.py` (mock setup pré-existente)
- Instalar Shell Commands plugin no Obsidian (passo manual do usuário)
- Refinar guardrail para falso positivo de nomes de variável em código técnico

**Métricas do sprint:**
- Testes: 113 passando, 8 falhando (pré-existentes, test_web_ingest.py)
- Cobertura: 80% total
- Wiki: 14 artigos em wiki/ai/, 11 summaries
- ADRs: 0001–0007, 0010

**Prompt de retomada:**
> Retome o projeto `kb` após o sprint de 2026-04-07. As entregas deste sprint: smoke test real OK, EPUB importado (12 artigos wiki/ai/), política de sensibilidade criada, pytest-cov 80%, fix de code fence em compile.py, PR#19 aberto. Próximas ações: (1) mergear PR#19; (2) corrigir 8 testes falhando em test_web_ingest.py (mock AttributeError); (3) instalar Shell Commands no Obsidian (passo manual).

---

## Sessão — 2026-04-06

**O que foi feito:**
- revisão da violation P2 do PR#15 (`feat/rich-book-import-metadata`)
- fix aplicado em `kb/book_import_core.py:173`: `_resolve_href` agora recebe `unquote(src)` para alinhar paths resolvidos com keys do `image_map` (built from decoded manifest hrefs)
- PR#15 description atualizada via `gh pr edit 15`
- sprint-close executado: logs, memória e handoff atualizados

---

## Sprint close — 2026-04-03

**O que foi feito neste ciclo:**
- fundação inspirada em Pal: routing por fonte, stores, manifesto, summaries, jobs, guardrails, flags `--allow-sensitive`/`--no-commit`
- ADRs `0006` e `0007` criados
- baseline validada com **85 testes passando**
