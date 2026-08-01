# O destino dos 1.037 artigos atuais

Type: grilling
Status: resolved (2026-07-31)
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

**Reagrupar de capítulo para tema, em lote único, pela proveniência.** Decidido no grilling de 2026-07-31; mapa proposto em [`MAPA-DE-TEMAS.md`](../MAPA-DE-TEMAS.md), glossário em [`DOMAIN.md`](../DOMAIN.md).

### A pergunta do ticket mudou

Este ticket perguntava "manter, arquivar ou recompilar". Nenhuma das três: o [ticket 004](004-wiki-produto-ou-insumo.md) decidiu que a wiki é produto e que o artigo passa a costurar várias fontes, o que reposiciona os 1.037 artigos como tendo a **granularidade errada** — são recortes de capítulo, e o produto quer recortes de tema. Não é a mesma coisa mal-feita; é outra coisa.

### O que decidiu

1. **Lote único**, não convergência sob demanda. A wiki fica coerente de imediato; os originais em `_chapters/` tornam a operação reversível.
2. **Todos os 1.037 vão para `_chapters/` agora**, absorvidos ou não. A convenção `_*` já os exclui do índice e da busca (mesmo mecanismo de `_summaries/` e `_sources/`).
3. **Perder retrievability do detalhe absorvido é aceito**, com a contrapartida de que **o gate de qualidade passa a ser "não perdeu informação"**, não só "tem referências". Se o detalhe importa, ele está no artigo de tema.
4. **O critério de agrupamento é a proveniência**, não cosseno nem LLM — ver abaixo.

### Por que proveniência, e não cosseno

A recomendação inicial era "cosseno como esqueleto + LLM para a cauda". A medição derrubou isso, e o motivo é o achado central deste ticket:

**O corpus não é 1.037 artigos sobre temas. São ~40 livros fatiados em 1.037 capítulos.**

O clustering por cosseno a 0,88 agrupa 469 artigos (45%) em 116 grupos — e os grupos **estão reconstruindo os livros**: C1 são 31 capítulos de *Learning DDD* + *Implementing DDD*, C3 são 16 de *PBT with PropEr*, C7 são 11 de *Observability Engineering*. Os 568 sem cluster são o mesmo fenômeno pelo avesso: `circuit-breaker.md`, `fail-fast.md`, `dogpile.md` e `criar-back-pressure.md` são todos do *Release It!*, e o cosseno não os junta porque cada capítulo fala de coisa diferente **dentro** do mesmo livro.

Ou seja: cosseno e LLM são **aproximações de um dado que o sistema já tem**. `raw/books/*/metadata.json` sabe qual capítulo veio de qual livro, e o ticket 001 protegeu essas fontes. Precisamos aproximar só porque o `manifest.json` nunca ligou artigo a fonte — a mesma dívida que bloqueia o recompile e o `kb deepen`.

O cosseno continua útil, mas para outra coisa: **detectar tema que atravessa livros**. DDD é o caso claro — dois livros, um tema.

### Ordem de execução

Da mais barata à mais cara, com verificação em cada etapa:

1. **`kb noise scan` retroativo.** O filtro da 011 nasceu depois do corpus e não pegou o que já estava lá: `dedicatorias.md`, `bolakale-aremu-perfil-do-autor.md`, `beneficios-da-assinatura-packt`, `documento-indeterminado-aviso-de-versao-eletronica`, `guia-para-este-livro.md` e `coruja-de-oma-strix-butleri.md` (exemplo de taxonomia biológica num livro técnico). Reduz o corpus antes de reagrupar.
2. **Reconstruir a ligação artigo → fonte** a partir de `raw/books/*/metadata.json`. Destrava também recompile e `kb deepen`.
3. **Agrupar por livro**, usando os clusters de cosseno para achar os temas que atravessam livros.
4. **LLM nomeia os temas e resolve o que não se encaixa**, com aprovação humana no mapa final.

Isso torna o lote único executável com verificação por etapa, em vez de uma rodada de 1.037 chamadas apostando num limiar — e o limiar é frágil: de 0,88 para 0,85 o maior grupo salta de 31 para 148; em 0,82 vira um caroço de 637 artigos.

### Continua em aberto

**A cardinalidade `Artigo de tema` × `Artigo-de-capítulo`.** Um capítulo sobre autenticação serve a "segurança de APIs" e a "criptografia aplicada". O mapa proposto assume um destino por capítulo, e a medição de sobreposição pode invalidar isso. Fica como primeiro passo da execução, não como decisão deste ticket.

### Fragilidades declaradas do mapa

- A atribuição dos 568 sem cluster é **inferência por título**, não medição.
- A ordem de grandeza por tema é estimativa; só os números de cluster são exatos.
- Livros que alimentam dois temas existem (*DDIA* → sistemas de dados **e** motores de banco).

<!-- preencher na resolução -->
