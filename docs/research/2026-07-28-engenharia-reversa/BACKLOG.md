# Backlog de portes candidatos — ordenado por valor

Resolve o ticket [Backlog priorizado de portes candidatos](tickets/005-backlog-portes.md).

**Critério de ordenação: valor**, conforme decidido — quanto o item melhora o kb e o quanto ele é útil, independentemente do trabalho que dá. Custo aparece como informação, nunca como critério de ordem.

**Contexto de escala** (medido em 2026-07-28): `wiki/` com 2.781 artigos e 4.26M palavras; `library/` com 869 fontes (800 md, 17 pdf, 6 epub, 1 mobi) e 4.79M palavras. Recompilação total do corpus custaria da ordem de 6M tokens de entrada — qualquer item que a exija carrega esse preço.

**Origem dos itens:** `H` = Hikari-knowledge, `G` = graphify, `R` = rowboat. Itens marcados **[achado]** não são portes: são problemas do kb que a leitura dos três repos revelou.

---

## V1. `kb lint` audita 20 de 2.781 artigos **[achado]**

**Valor: crítico.** O comando existe para dar confiança no corpus e olha 0,7% dele, sem informar isso a quem roda.

`kb/lint.py:37-39` monta o contexto do LLM com `articles[:20]` — os vinte primeiros que o `rglob` devolver, em ordem de sistema de arquivos. A detecção de wikilink quebrado, essa sim, varre tudo (`kb/lint.py:29-35`). O resultado é um relatório que mistura uma checagem completa com uma auditoria de amostra silenciosa, e apresenta as duas como se fossem a mesma coisa.

Referência externa: Hikari roda `build_graph.py --check` sobre o corpus inteiro e retorna código 1 quando há problema estrutural; graphify constrói sobre tudo e reporta o que truncou.

**Direção:** separar o que escala do que não escala. Checagens estruturais (links, frontmatter, órfãos, duplicidade de slug) sobre 100% do corpus, sem LLM. Auditoria semântica por amostragem explícita, declarando no output o tamanho da amostra — ou por lote com custo anunciado.

**Custo:** baixo para a parte estrutural; médio para desenhar a auditoria semântica em escala.

---

## V2. Índice persistente com cache por `(mtime, size)` — H, G

**Valor: muito alto.** Habilita quase todos os itens abaixo e resolve a latência que hoje limita o uso.

Duas leituras completas do corpus por operação:

- `kb/search.py:24-31` (`_iter_docs`) lê e tokeniza os 2.781 arquivos, 36 MB, **a cada busca**.
- `kb/graph.py:17-23` (`resolve_wikilink`) faz um `rglob("*.md")` sobre o diretório inteiro **por wikilink**, chamado dentro do laço de travessia (`kb/graph.py:89`). Um artigo com 30 links dispara 30 varreduras completas.

Referência externa: Hikari mantém `NodeStore` com cache por arquivo validado por `(mtime, size)`, reparsando só o que mudou e removendo entradas de arquivos apagados; graphify constrói índice invertido de trigramas sob demanda e cacheia IDF no próprio grafo.

**Direção:** um store de wiki com mapa `slug → path` e cache invalidado por `(mtime, size)`, compartilhado por `search`, `graph`, `lint` e `archive`. É a "camada derivada" que os três repos têm e o kb não.

**Custo:** médio. Não muda a premissa — markdown continua autoritativo, o índice é descartável e reconstruível.

---

## V3. Peso por campo no ranking — H, G

**Valor: alto.** Em 2.781 artigos, título e tags são o sinal mais forte disponível, e hoje valem o mesmo que uma palavra qualquer no meio do corpo.

`kb/search.py:12-13` tokeniza o texto inteiro do arquivo, frontmatter incluído, sem distinção de campo. Um artigo cujo `title` é exatamente a pergunta compete em pé de igualdade com um que menciona o termo de passagem.

Referência externa: Hikari soma pesos fixos por campo (id, título, tags, corpo) e desempata por id; graphify usa igualdade de label 1000, prefixo 100, substring 1, trecho em caminho 0,5, tudo multiplicado por IDF, com multiplicador extra 10 para a pergunta inteira.

**Direção:** casar contra `title`, `tags`, `topic` e nome de arquivo com pesos próprios, mantendo BM25 sobre o corpo como está. Os canais RRF já existentes (`kb/search.py:130`) acomodam um canal novo sem reescrita.

**Custo:** baixo-médio.

---

## V4. Expansão de contexto sem filtro binário, com bloqueio de hub — G

**Valor: alto.** Hoje a travessia descarta vizinhos relevantes e não tem defesa contra artigo-hub.

Dois problemas em `kb/graph.py`:

- `_is_relevant` (`kb/graph.py:54-62`) exige que um termo da pergunta apareça no `title` ou nas `tags` do vizinho. É filtro binário: o artigo vizinho que explica o conceito sem repetir a palavra da pergunta é jogado fora.
- Não há cap de grau. Um artigo com muitos wikilinks enfileira todos os vizinhos (`kb/graph.py:106-107`), e o corte só vem por `token_budget`.

Referência externa: graphify não filtra vizinho por termo — ordena por distância da semente, grau e id, e impede que nós no percentil 99 de grau (piso 50) sirvam de trânsito, embora possam ser semente.

**Direção:** trocar o filtro binário por ordenação (distância, grau, score lexical do vizinho) e adicionar cap de hub. O `token_budget` deixa de ser a única defesa.

**Custo:** baixo-médio. Depende de V2 para ficar barato.

---

## V5. Deduplicação e merge-before-create no compile — H

**Valor: alto, condicionado a medição.** 869 fontes viraram 2.781 artigos. Se houver near-duplicates em volume, eles degradam toda busca — e nenhum dos itens acima corrige isso.

O `compile` não tem etapa de "já existe artigo que responde isto?". O Hikari trata merge-before-create como gate duro: antes de criar id novo, buscar por título e mecanismo, atualizar o que já responde à mesma pergunta, e só criar para dangling intencional com ao menos duas entradas.

**Antes de implementar, medir:** quantos pares de artigos passam de um limiar de similaridade. Sem esse número, o valor é hipótese. A medição é barata (o índice de V2 já dá o material).

**Custo:** médio para detectar; alto para fundir com segurança em 2.781 artigos.

---

## V6. Vigência semântica no `heal` — R

**Valor: médio-alto.** O `reviewed_at` hoje é carimbo de passagem, não julgamento de vigência.

`kb/heal.py:41-46` estampa a data corrente; o prompt manda explicitamente **não** alterar conteúdo substantivo (`kb/heal.py:16`). O artigo é marcado como revisado sem que ninguém avalie se o que ele afirma ainda vale.

Referência externa: o curador do rowboat distingue fato transitório de fato estável — refresca o timestamp do que foi reconfirmado, remove o transitório envelhecido, preserva o estável, sob a regra explícita de que perder observação já registrada é a pior falha possível.

Nota: o kb já tem decay temporal de confiança, mas em `claims`, não em artigos (`kb/claims.py:141-182`). Há uma primitiva a reaproveitar.

**Custo:** médio. Prompt novo e política de vigência; sem mudança estrutural.

---

## V7. Tombstone em vez de apagar — H

**Valor: médio-alto.** Duas políticas de remoção convivem hoje no mesmo produto.

`kb/heal.py:64-67` faz `path.unlink()` no stub. `kb/archive.py:119` move para `archive/` com backup versionado. O mesmo corpus, portanto, ora perde conteúdo, ora o preserva, dependendo de qual comando passou por ali. O git guarda o histórico, mas histórico não é navegável pelo Obsidian nem pelo `qa`.

Referência externa: Hikari nunca apaga. Conteúdo derrubado vira tombstone com `status: tombstone` e `superseded_by: <id-canônico>`, e continua navegável — o valor de um caminho morto é justamente evitar que alguém o repita.

**Direção:** `heal` passa a delegar ao `archive` em vez de `unlink`, e stub vira tombstone quando havia conteúdo antes.

**Custo:** baixo. As duas peças já existem.

---

## V8. Proveniência citável na resposta — G

**Valor: médio.** O `qa` já cita `[[wikilink]]` por instrução de prompt (`kb/qa.py:16`); o que falta é a âncora verificável e a garantia de que a citação corresponde ao que foi lido.

Referência externa: graphify devolve, para cada aresta do subgrafo, a relação, a confiança e a linha onde ela ocorre — a resposta é auditável sem reabrir o corpus. É o que sustenta a promessa "every edge explained".

**Direção:** o contexto montado por `build_context` carregar `arquivo:linha` do trecho usado, e a resposta citar isso em vez de só o nome do artigo.

**Custo:** médio.

---

## V9. Servir a wiki como ferramenta (MCP) — H, G

**Valor: depende do fluxo de trabalho** — mantido como candidato vivo por decisão explícita.

O kb responde como aplicação: `kb qa` chama o modelo por dentro (`kb/qa.py:80-94`). Os três repos servem como ferramenta e deixam a geração no cliente. As quatro ferramentas do Hikari (`kg_search`, `kg_get`, `kg_neighbors`, `kg_index`) são um contrato pequeno o bastante para portar quase literalmente — e o kb já tem as quatro capacidades correspondentes (`search.search`, leitura de arquivo, `graph.traverse`, `_index.md`).

O que isso destrava: qualquer agente — Claude Code, Codex, outro — consulta o vault sem passar pelo `kb qa` e sem carregar 36 MB no contexto.

**Custo:** médio, e cai bastante depois de V2.

---

## V10. Taxonomia editorial de confiança no compile — H

**Valor: médio.** O kb já deriva confiança numérica em `claims.py:61-67`; o Hikari usa uma taxonomia editorial declarada (`measured` / `reported` / `mixed`) com gate de admissão: número só entra com condições (`n`, setup), e é proibido misturar medido, relatado e hipótese na mesma afirmação.

**Ressalva de escala:** no Hikari isso é aplicado por humano em 47 nós. Em 2.781 artigos precisa ser check automático no `lint`, não gate de entrada manual — ver a tensão 2 da síntese.

**Custo:** médio; alto se aplicado retroativamente ao corpus existente.

---

## V11. Índice autoritativo — muda a premissa

**Valor: baixo, registrado por completude.** O teto de ambição acordado permite propor itens que contrariem "markdown é a fonte da verdade", e este é o único da lista que o faz.

Registro para a decisão ficar consciente: **os três repos recusam isso.** Hikari mantém markdown autoritativo e o MCP nem lê o grafo serializado; graphify reconstrói do fonte; rowboat carrega arquivo no prompt. Nenhum promove o índice a verdade.

Não recomendo, e a razão é o próprio V2: um índice derivado e descartável entrega o ganho de desempenho sem o custo de ter uma segunda fonte de verdade para reconciliar.

---

## Fora deste backlog

- **UI própria para o kb** — out of scope do map por decisão de escopo. A evidência levantada está em `DOSSIE-rowboat.md` §2: o que a UI dele mostra é estado operacional (topologia, ciclo de vida de jobs, draft/live, reasoning e tool calls tipados), não conteúdo. Se a decisão for retomada, é esforço próprio.
- **Compatibilidade com multi-vault (feature 010)** — ignorada por decisão explícita; itens avaliados contra o kb de vault único. V2 e V9 são os que mais mudariam de forma sob multi-vault.

## Alerta de documentação

`CLAUDE.md` e `AGENTS.md` descrevem a busca do kb como "contagem simples de palavras-chave" e "TF-IDF simples ... até ~100 artigos/400K palavras". O código faz BM25 + densidade + RRF (`kb/search.py:59-102`) e o corpus real é 28× maior em artigos. A documentação subestima o produto e a escala ao mesmo tempo. Corrigir é barato e evita que a próxima decisão parta de premissa errada.
