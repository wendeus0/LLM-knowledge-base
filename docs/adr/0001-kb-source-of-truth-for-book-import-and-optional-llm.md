# ADR 0001 — kb como source of truth para importação de livros e subsistema LLM opcional

- **Status:** Aceito
- **Data:** 2026-04-03

## Contexto

O fluxo de importação de livros começou em `book2md` como protótipo separado, mas evoluiu até se tornar funcionalmente relevante para o produto `kb`. Ao mesmo tempo, o projeto precisava permitir uso parcial sem dependência obrigatória do SDK `openai`, já que a importação de livros é local, enquanto `compile/qa/heal/lint` continuam dependendo de provider LLM.

Sem uma decisão formal, havia risco de:

- divergência de implementação entre laboratório e produto
- acoplamento implícito e frágil entre os repositórios
- confusão entre capacidades locais e capacidades assistidas por LLM

## Decisão

1. `kb` passa a ser a implementação principal (source of truth) para importação/exportação de livros.
2. O núcleo canônico do fluxo fica em `kb/book_import_core.py`.
3. `book2md` permanece como compat layer/laboratório, reutilizando o núcleo de `kb`.
4. O destino estrutural da importação continua sendo `raw/books/<livro>/`.
5. `kb compile` passa a tratar `raw/` de forma recursiva, permitindo promover capítulos importados para a wiki.
6. O subsistema LLM permanece parte do produto, mas o SDK `openai` vira dependência opcional (`.[llm]`).
7. Para OpenCode Go, o projeto valida explicitamente nomes de modelo compatíveis e sem prefixo.
8. A extração de PDF passa a usar PyMuPDF como caminho principal, com OCR opcional apenas para PDFs escaneados ou com texto corrompido.
9. A identidade de recompilação de artigos passa a ser ancorada no `source` normalizado em `raw/`, não no slug derivado do título traduzido.

## Consequências

### Positivas

- reduz duplicação e divergência entre laboratório e produto
- deixa claro que a importação de livros é parte nativa do `kb`
- melhora a experiência para ambientes sem dependências LLM
- preserva o valor central do projeto nas features assistidas por LLM
- reduz ruído de nomes de livros importados e estabiliza recompilações da wiki mesmo quando a tradução do título muda

### Negativas

- `book2md` passa a depender operacionalmente do núcleo de `kb`
- a distribuição externa de `book2md` ainda exige decisão futura mais formal
- cresce a necessidade de política operacional clara para uso de provider externo com conteúdo sensível
- suporte a OCR adiciona dependências opcionais de sistema e biblioteca para casos de PDF escaneado

## Alternativas consideradas

### A1. Manter `book2md` e `kb` com implementações separadas

- **Rejeitada** por aumentar custo de manutenção e risco de divergência.

### A2. Tornar o SDK `openai` obrigatório para todo o projeto

- **Rejeitada** porque a importação de livros funciona sem LLM e não deve exigir dependência desnecessária.

### A3. Extrair imediatamente um terceiro pacote compartilhado

- **Rejeitada**. Fluxo de livro estabilizado (PR#14 + PR#15 mergeados). Distribuição externa de `book2md` não tem demanda concreta. O núcleo em `kb/book_import_core.py` cobre todos os casos de uso; `book2md` pode continuar consumindo esse núcleo diretamente sem empacotamento formal.

**Critério de reabertura:** necessidade real de instalar `book2md` fora do workspace atual como pacote independente.
