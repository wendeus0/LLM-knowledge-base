# O destino dos 1.037 artigos atuais

Type: grilling
Status: open
Blocked by: 003-medir-qualidade-corpus, 004-wiki-produto-ou-insumo

## Question

Manter, arquivar ou recompilar?

A intenção declarada na abertura do esforço foi "refazer todo o vault". O charting mostrou que essa opção **não está disponível hoje** — não por custo, por pré-requisito ausente. Cada caminho tem um bloqueio próprio:

**Recompilar** exige duas coisas que não existem:

- `manifest.json` nunca foi materializado neste vault (declarado em `kb/config.py:18-21`, ausente em `~/vault/kb_state/`). Sem ele, `find_compiled_entry()` (`kb/state.py:87`) devolve `None` para tudo e `_resolve_output_path` (`kb/compile.py:223-231`) escreve em caminho novo derivado de `slugify(title)`. O recompile **duplica** a wiki em vez de atualizá-la: 1.037 artigos viram 2.074, e a proveniência raw→artigo continua perdida.
- `raw/` está vazia. O insumo teria que ser re-derivado das 869 fontes de `library/` via `import-book`, que é um passo com perdas próprias e não determinístico.

Custo, para dimensionar: 1.037 a 2.074 chamadas generativas com documento inteiro no prompt (`kb/compile.py:307,324`), sem chunking e sem cache, mais 4m32 de reindexação. Zero em dinheiro se rodar local; sem token accounting no repo para converter em valor se rodar remoto.

**Arquivar** exige política de tombstone que o produto não tem: `heal.py:64-67` faz `unlink` e `archive.py:119` move com backup — duas políticas de remoção convivendo no mesmo código. É o V7 do backlog anterior, classificado custo baixo porque as peças já existem.

**Manter** é a opção default e a única sem pré-requisito — mas só é defensável se o ticket 003 mostrar que os artigos prestam para o uso que o 004 decidir. Manter por inércia não é decidir.

**Quarta opção que a medição pode abrir:** recompilar seletivamente. Se 003 mostrar que a rasura se concentra em topics ou em faixas de compressão específicas, recompilar 15% do corpus com pré-requisito menor é diferente de recompilar tudo.

### Pontos a fechar

- Qual caminho, e o que ele exige que exista antes (o pré-requisito vira ticket ou SPEC no pipeline).
- Se recompilar: o `manifest.json` é reconstruído retroativamente a partir da wiki existente, ou se aceita começar do zero com proveniência nova?
- Se arquivar: qual o critério de corte, e ele é reversível?
- O que acontece com `topics/` (3.584 arquivos, 87 MB) e `_summaries/` (1.022) — derivados que acompanham a decisão.

## Answer

<!-- preencher na resolução -->
