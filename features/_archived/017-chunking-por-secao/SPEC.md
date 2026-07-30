---
title: Chunking por seção no índice de embeddings
epic: search
status: done
pr:
---

# Chunking por seção no índice de embeddings

## Objetivo

Hoje cada artigo vira **um único vetor**, gerado a partir dos primeiros 8k caracteres. Duas consequências medidas: **368 dos 1.037 artigos (35%) são truncados** — o conteúdo além do corte é invisível ao canal semântico — e mesmo artigos inteiros perdem especificidade, porque um texto de 20 mil caracteres reduzido a um vetor médio não representa bem nenhum dos assuntos que ele cobre.

O sistema deve indexar **por seção**, não por artigo. A estrutura já existe no corpus: todos os 1.037 artigos têm headings `##`, com 7.743 seções de mediana 647 caracteres — cabem folgadamente no limite do modelo, e só 3 excedem 8k.

Baseline a superar (golden curado de 50 casos, `v2-moe`): **recall@5 = 0,420 / MRR = 0,272**, com recall@20 = 0,720 indicando que o gargalo é ordenação.

## Requisitos funcionais

- [x] RF-01: o índice passa a guardar um vetor por seção do artigo, preservando a associação chunk → artigo
- [x] RF-02: nenhum conteúdo de artigo fica fora do índice por truncamento — seção maior que o limite do modelo é dividida, não cortada
- [x] RF-03: o ranking semântico continua devolvendo **artigos**, agregando os chunks pelo melhor score (o artigo vale o que vale sua melhor seção)
- [x] RF-04: cada chunk carrega o título do artigo e o heading da seção no texto embedado — uma seção isolada sem esse contexto perde o assunto
- [x] RF-05: seções muito curtas são agrupadas com a seguinte até um mínimo, evitando vetores de ruído
- [x] RF-06: incrementalidade preservada — artigo cujo conteúdo não mudou não re-embeda nenhum de seus chunks
- [x] RF-07: índice em formato antigo (um vetor por artigo) é detectado e exige rebuild explícito, sem produzir resultado silenciosamente errado
- [x] RF-08: `kb index status` reporta contagem de chunks além da de artigos

## Requisitos técnicos

- Chunk = seção delimitada por heading `##`; preâmbulo antes do primeiro heading é chunk próprio
- Texto embedado por chunk: `search_document: <título do artigo> — <heading>\n<conteúdo>` (prefixo de task do Nomic preservado)
- Agregação chunk → artigo por **máximo** do cosseno; a alternativa (soma) favoreceria artigos longos por terem mais chunks
- Hash de invalidação continua por **artigo**: se o conteúdo mudou, todos os chunks daquele artigo são refeitos. Hash por chunk economizaria embeds em edições pontuais, mas complica a remoção e não vale nesta fatia
- Índice ganha campo de versão de formato; versão divergente → mesmo tratamento de modelo divergente (ignora e orienta rebuild)
- Sem dependência nova; `numpy` continua fora — cosseno em Python puro sobre ~7.7k vetores é aceitável e mensurável

## Mudanças de API/CLI

- `kb index build`: passa a reportar chunks indexados além de artigos
- `kb index status`: linha com total de chunks e média por artigo
- Formato de `kb_state/embeddings.json` muda (breaking) — exige `kb index build` uma vez

## Testes

- Unit: divisão de artigo em seções (com preâmbulo, sem preâmbulo, heading único, headings aninhados `###`); agrupamento de seção curta; split de seção acima do limite; prefixo de contexto no texto embedado; agregação por máximo com chunks de scores diferentes; detecção de índice em formato antigo
- Integration (embedder fake): `index build` gera N chunks para artigo com N seções; artigo inalterado não re-embeda; artigo editado refaz só os seus chunks; busca semântica devolve artigo cujo melhor chunk casou; `index status` reporta chunks
- Manual: rebuild no vault real e `kb bench --mode hybrid` comparando com a baseline 0,420/0,272

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 6–8h |
| Bloqueador | não |
| Risk | média (muda formato do índice e o caminho de ranking; mitigado por baseline medida e rebuild explícito) |

## Dependências

- Feature 012 (índice), 015 (refresh) e 016 (bench, para provar o ganho)

## Notas

**Fora de escopo:**
- Overlap entre chunks (seções são unidades semânticas naturais; medir antes de adicionar)
- Rerank de chunks por modelo dedicado
- Devolver o chunk específico como resposta ao usuário — o contrato continua sendo artigo
- Chunking do corpus `raw/` (só a wiki é indexada)

**Casos de erro:**
- Artigo sem nenhum heading `##` → um único chunk com o corpo inteiro (comportamento atual); a medição mostrou 0 casos no corpus, mas o código não pode assumir
- Seção acima do limite do modelo → dividida em partes, todas indexadas
- Índice em formato antigo → `index status` orienta rebuild; busca degrada para lexical em vez de misturar formatos

**Open questions:**
- (nenhuma)
