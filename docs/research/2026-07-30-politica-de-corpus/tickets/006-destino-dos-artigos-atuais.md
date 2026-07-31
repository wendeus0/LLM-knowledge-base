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

## Evidência para o grilling

> Compilada em 2026-07-31. Organiza o que a sessão mediu; não decide.

**A opção "recompilar" ficou mais viável em um ponto e continua bloqueada no outro:**

- **O material bruto está protegido** (ticket 001, resolvido): `~/vault` tem remote privado com `library/` versionada via git-lfs — 863 fontes, 161 MB, restauração provada por clone limpo. A opção de recompilar não pode mais ser perdida por falha de disco.
- **`manifest.json` continua sendo o bloqueio**: nunca foi materializado neste vault, então `find_compiled_entry()` devolve `None` para tudo e um recompile **duplica** em vez de atualizar. Isso agora tem prova empírica, não só teórica: no ticket 002 o mesmo documento OWASP — ingerido uma vez como HTML e outra como markdown — virou **dois artigos** em `wiki/cybersecurity/`, que foi de 11 para 13.

**O custo de recompilar mudou:** o compile agora tem gate de saída (`_validate_output`, PR #46) e container de conteúdo não-confiável (PR #54). Recompilar hoje produz artigos que pelo menos não mentem sobre a própria estrutura. Mas o defeito que 002 achou — seção "Exemplos" sem exemplos, tradução errada no título — **não é pego por nenhum gate**, e as três heurísticas testadas para detectá-lo foram todas descartadas com medição. Recompilar 1.037 artigos hoje reproduziria a mesma classe de defeito em escala.

**A quarta opção (recompilar seletivamente) ganhou um critério concreto:** os **59 pares com cosseno ≥ 0,95** que 003 mediu são um alvo delimitado e verificável — dedup é o V5 do backlog anterior, e o caso OWASP acima é um deles. Recompilar/mesclar 59 pares é outra ordem de grandeza que recompilar tudo.

**Sobre arquivar:** as duas políticas de remoção continuam convivendo (`heal.py` faz `unlink`, `archive.py` move com backup). Nada mudou aqui.

## Answer

<!-- preencher na resolução -->
