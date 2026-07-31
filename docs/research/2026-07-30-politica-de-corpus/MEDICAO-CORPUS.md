# Medição factual do corpus compilado

Data da medição: 2026-07-31.

## Método e reprodutibilidade

O instrumento é [`scripts/measure_corpus_quality.py`](../../../scripts/measure_corpus_quality.py). Ele é standalone, recebe o vault literal por `--vault`, abre `kb_state/embeddings.json` apenas para leitura e não importa `kb.config`; portanto, não depende de `.env` nem pode resolver o vault errado por default.

Comando-base de todas as tabelas abaixo:

```bash
python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section <universe|size|structure|compression|duplicates|topics>
```

Definições usadas:

- Universo indexável: a mesma regra de `kb/embeddings.py::_iter_articles`: `.md` cujo caminho relativo não contém parte iniciada por `_` ou `.`. Isso exclui os cinco diretórios solicitados e também `wiki/_index.md`.
- Tamanho: palavras Unicode e caracteres do corpo Markdown, depois do frontmatter. O Markdown, títulos e wikilinks permanecem no corpo; frontmatter não entra.
- Percentis: interpolação linear sobre todos os artigos, inclusive mínimo e máximo quando exibidos.
- Seções: correspondência exata, sem diferenciar maiúsculas/minúsculas, aos sete `##` do template atual: Contexto e motivação, Conceitos centrais, Como funciona, Exemplos, Limitações e trade-offs, Conceitos Relacionados e Referências. A nota padrão gerada após `---` não torna uma seção não-vazia.
- Referência candidata: item de lista sob `## Referências` que não é wikilink interno nem placeholder do template. Isso é uma proxy sintática reproduzível, não validação semântica de autoria/título/capítulo; por isso não afirma que seja uma referência bibliográfica real no sentido do `DOMAIN.md`.
- Near-duplicate: média dos vetores de chunk de cada artigo, normalizada em L2, seguida de cosseno entre todos os pares não ordenados de artigos. Antes do cálculo, o script exige igualdade de caminhos **e** hashes entre wiki e índice; não gera nem atualiza vetores.

`_validate_output` não implementa um mínimo de “três frases”: na revisão atual ele exige somente frontmatter com `title` e `topic`, e corpo não vazio. Evidência:

```bash
nl -ba kb/compile.py | sed -n '64,74p'
```

## Universo medido

Comando:

```bash
python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section universe
```

```text
articles_indexable=1037
markdown_after_named_directory_exclusions=1038
extra_excluded_by_indexer=_index.md
```

Assim, os **1.037** artigos são exatamente o universo do índice. A diferença de um arquivo em relação à exclusão literal dos cinco diretórios é explicada por `_index.md`, que não é indexável pela regra usada na engine.

## 1. Distribuição de tamanho

Comando:

```bash
python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section size
```

| Medida | Mínimo | P10 | P25 | Mediana | P75 | P90 | Máximo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Palavras | 127 | 401,6 | 586 | 872 | 1.286 | 1.680,4 | 4.647 |
| Caracteres | 932 | 2.915 | 4.085 | 6.143 | 9.121 | 12.108,4 | 32.236 |

Cauda curta, pelo mesmo comando: 0 artigos têm até 50 palavras; 0 têm até 100; 6 têm até 150. Portanto, nenhum artigo se aproxima de um piso de três frases por tamanho, embora o mínimo de validação de código seja na prática apenas “corpo não vazio”.

Os 20 menores artigos são:

| Palavras | Caracteres | Caminho |
|---:|---:|---|
| 127 | 957 | `recursos-online.md` |
| 130 | 932 | `algorithms/introducao-a-algoritmos-e-estruturas-de-dados-1.md` |
| 132 | 945 | `dedicatorias.md` |
| 133 | 994 | `python/automate-the-boring-stuff-with-python.md` |
| 138 | 958 | `python/sobre-o-revisor-tecnico.md` |
| 139 | 1.095 | `observability-engineering-2nd-edition.md` |
| 153 | 1.163 | `database-internals-introducao-a-obra.md` |
| 172 | 1.255 | `documento-indeterminado-aviso-de-versao-eletronica.md` |
| 177 | 1.427 | `designing-data-intensive-applications.md` |
| 182 | 1.289 | `python/pagina-de-meio-titulo-half-title-page.md` |
| 184 | 1.440 | `martin-kleppmann.md` |
| 192 | 1.354 | `python/automate-the-boring-stuff-with-python-programacao-pratica-pa.md` |
| 200 | 1.458 | `aprendendo-domain-driven-design.md` |
| 201 | 1.519 | `ai/ai-engineering-livro.md` |
| 203 | 1.485 | `part0000.md` |
| 204 | 1.534 | `download-de-recursos-de-treinamento-e-obtencao-de-ajuda-adic.md` |
| 207 | 1.701 | `ai/fundamentos-de-machine-learning.md` |
| 210 | 1.687 | `resolver-problemas-sistemicos.md` |
| 213 | 1.611 | `python/effective-python-pagina-de-rosto.md` |
| 213 | 1.677 | `bolakale-aremu-perfil-do-autor.md` |

## 2. Densidade estrutural

Comando:

```bash
python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section structure
```

| Métrica por artigo | Mínimo | P10 | P25 | Mediana | P75 | P90 | Máximo | Distribuição discreta relevante |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Seções não-vazias do template (0–7) | 0 | 1 | 1 | 1 | 1 | 1 | 2 | 0: 3; 1: 1.022; 2: 12 |
| Wikilinks `[[...]]` | 4 | 14 | 18 | 29 | 46 | 70 | 231 | percentis na tabela |
| Itens em Referências | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0: 1.035; 2: 1; 5: 1 |
| Itens candidatos a bibliográficos | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0: 1.036; 5: 1 |

Pelo critério sintático de referência candidata, **1** artigo alcança pelo menos cinco itens. Esse número não verifica a condição mais forte de “referência bibliográfica real” de [`features/_archived/011-corpus-noise-filter/DOMAIN.md`](../../../features/_archived/011-corpus-noise-filter/DOMAIN.md): o corpus não preserva metadados suficientes para validar automaticamente autor, título e capítulo por item.

## 3. Compressão fonte → artigo

Comando:

```bash
python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section compression
```

O `manifest.json` está ausente e o frontmatter guarda apenas o basename de `source`, não o caminho nem um identificador imutável da fonte. Foram procurados arquivos textuais em `raw/`, `library/` e `wiki/_sources/`:

```text
source_candidates=library:804,raw:0,wiki/_sources:712
paired_articles=857 paired_rate=0.827
unresolved_articles=117 unresolved_rate=0.113
ambiguous_articles=63 ambiguous_rate=0.061
pairing_methods=identical-content-basename:23,unique-basename:834
```

Logo, a razão fonte→artigo global é **UNVERIFIED**: 857/1.037 (82,7%) são junções candidatas por basename único (ou cópias de conteúdo idêntico), mas não há proveniência que prove que esse arquivo é a fonte efetivamente enviada ao compile. Para diagnosticar a cobertura disponível, a distribuição condicional desses 857 pares candidatos é:

| Medida | Mínimo | P10 | P25 | Mediana | P75 | P90 | Máximo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Palavras de entrada | 2 | 191,6 | 758 | 2.812 | 7.560 | 13.946,8 | 173.880 |
| Palavras do artigo | 127 | 416,6 | 609 | 939 | 1.339 | 1.729 | 4.647 |
| Razão entrada/saída | 0,01 | 0,50 | 1,15 | 2,83 | 5,91 | 10,70 | 148,56 |

Os valores abaixo de 1, inclusive 0,01, reforçam por que essa proxy não deve ser promovida a métrica de compressão comprovada: o basename pode apontar para uma página de título/índice que não representa a entrada que originou o artigo.

## 4. Near-duplicates sem regenerar embeddings

Comando:

```bash
python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section duplicates
```

O comando validou `format=2`, modelo `text-embedding-nomic-embed-text-v2-moe`, dimensão 768, **1.037** artigos e **8.685** chunks. Caminhos e hashes do índice correspondem ao wiki atual.

Distribuição, por artigo, da maior similaridade de cosseno com qualquer outro artigo:

| Mínimo | P10 | P25 | Mediana | P75 | P90 | Máximo |
|---:|---:|---:|---:|---:|---:|---:|
| 0,5502 | 0,8056 | 0,8346 | 0,8733 | 0,9102 | 0,9517 | 0,9842 |

Contagens de pares não ordenados (os limiares são cumulativos):

| Similaridade mínima | Pares |
|---:|---:|
| 0,95 | 59 |
| 0,90 | 296 |
| 0,85 | 1.432 |

Exemplos reais por faixa:

| Faixa | Cosseno | Par |
|---|---:|---|
| ≥ 0,95 | 0,984209 | `algorithms/decomposicoes-de-matrizes.md` ↔ `decomposicoes-de-matrizes.md` |
| ≥ 0,95 | 0,982860 | `algebra-linear.md` ↔ `algorithms/algebra-linear.md` |
| ≥ 0,95 | 0,982679 | `algorithms/problema-de-coloracao-de-grafos-com-backtracking.md` ↔ `algorithms/problema-de-coloracao-de-grafos-por-backtracking.md` |
| [0,90, 0,95) | 0,949902 | `algorithms/arvore-binaria-de-busca-otima-busca-bem-sucedida-programacao.md` ↔ `algorithms/arvore-de-busca-binaria-otima-com-probabilidades-de-busca-be.md` |
| [0,90, 0,95) | 0,949743 | `algorithms/arvore-binaria-de-busca-otima-busca-bem-sucedida-programacao.md` ↔ `algorithms/arvore-binaria-de-busca-otima-com-probabilidades-de-sucesso-.md` |
| [0,90, 0,95) | 0,949266 | `python/mais-sobre-type-hints-em-python.md` ↔ `python/type-hints-em-funcoes-em-python.md` |
| [0,85, 0,90) | 0,899993 | `04-part-ii-sorting-and-order-statistics.md` ↔ `algorithms/algoritmos-de-ordenacao-sorting.md` |
| [0,85, 0,90) | 0,899926 | `o-que-e-observabilidade.md` ↔ `parte-i-o-caminho-para-a-observabilidade.md` |
| [0,85, 0,90) | 0,899858 | `encerramento-de-antipadroes-a-padroes-de-estabilidade.md` ↔ `encerramento-falhas-de-producao-e-padroes-de-estabilidade.md` |

## 5. Cobertura por topic

Comando:

```bash
python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section topics
```

O P25 global é 586 palavras. A coluna “curtos” conta artigos com até esse valor; ela permite comparar a cauda curta de cada topic com os 25% globais.

| Topic | Artigos | Mediana de palavras | Curtos ≤ 586 | Taxa curta |
|---|---:|---:|---:|---:|
| general | 461 | 951 | 126 | 27,3% |
| algorithms | 258 | 771 | 55 | 21,3% |
| ai | 90 | 1.137 | 18 | 20,0% |
| learning | 89 | 703 | 31 | 34,8% |
| python | 88 | 1.131,5 | 13 | 14,8% |
| harness | 15 | 973 | 1 | 6,7% |
| cybersecurity | 11 | 453 | 7 | 63,6% |
| software-architecture | 5 | 1.009 | 1 | 20,0% |
| geral | 3 | 574 | 2 | 66,7% |
| observability | 3 | 451 | 2 | 66,7% |
| architecture | 2 | 1.238 | 0 | 0,0% |
| ddd | 2 | 1.119 | 1 | 50,0% |
| mathematics | 2 | 1.072 | 0 | 0,0% |
| api | 1 | 303 | 1 | 100,0% |
| data-engineering | 1 | 1.557 | 0 | 0,0% |
| devops | 1 | 598 | 0 | 0,0% |
| domain-driven-design | 1 | 304 | 1 | 100,0% |
| event-driven-architecture | 1 | 1.142 | 0 | 0,0% |
| hexagonal | 1 | 1.638 | 0 | 0,0% |
| software-design | 1 | 486 | 1 | 100,0% |
| tensorflow | 1 | 1.464 | 0 | 0,0% |

Os topics com menos de 10 artigos não permitem inferência estável. Entre grupos com volume suficiente, `cybersecurity` é a maior concentração observada (7/11 curtos, mediana 453), seguido por `learning` (31/89, mediana 703); `python` é a ponta oposta (13/88, mediana 1.131,5).

## CORREÇÃO — revisão do orquestrador, 2026-07-31

> A conclusão original desta seção dizia que **"a rasura é praticamente uniforme"**. Isso está **errado**, e o erro é de interpretação de medida — o mesmo modo de falha que `memory/pitfalls.md:140-142` registra para o golden set por título.
>
> O detector contou **seções com os nomes literais do template** (`Resumo`, `Contexto e motivação`, `Conceitos centrais`, `Como funciona`, `Exemplos`, `Limitações e trade-offs`, `Conceitos Relacionados`). Medido assim, a mediana é de fato 1. Mas contando **headings reais** (`^##`/`^###`, qualquer título):
>
> | Métrica | Seções do template | Headings reais |
> |---|---|---|
> | mediana por artigo | 1 | **10** |
> | média | 1,21 | **11,7** |
> | máximo | 2 | **69** |
> | artigos com ≥5 headings | — | **965 de 1.038 (93,0%)** |
> | artigos com 0 headings | — | **0** |
>
> Comando: ver `scripts/measure_corpus_quality.py` mais a verificação cruzada no transcript da sessão.
>
> Exemplo real — `wiki/cybersecurity/autenticacao-de-requisicoes-por-assinatura-digital.md`, 1.552 palavras, **15 headings**: "Requisitos de uma Autenticação de Requisições", "Prova de Origem", "Integridade", "Não-Repúdio", "Visão Geral do Padrão", "Implementação", "Geração de Credenciais", "Assinatura de um Payload", "Fingerprint de Requisição HTTP", "Verificação e Autenticação no Servidor", "Trade-offs e Considerações", "Proteção contra Replay". Só "Conceitos Relacionados" coincide com o template.
>
> **O que a medição de fato mostra:** os artigos **não são rasos** — são estruturados, com mediana de 10 seções e 926 palavras, usando headings derivados do conteúdo em vez dos nomes fixos do template. O corpus foi compilado sob outra convenção, anterior ao template atual.
>
> **Consequência para o ticket 006:** recompilar o corpus para "consertar rasura" partiria de uma premissa falsa e **destruiria estrutura que existe**. O que a não-aderência ao template de fato impede é o processamento uniforme por seção — o que é um problema diferente e menor.
>
> O achado de **zero referências em 1.035 artigos** permanece válido e não é afetado por esta correção.

## Achados factuais

- Por comprimento, o corpus não é uma coleção de microartigos: mediana de 872 palavras e nenhum artigo com até 100 palavras. A cauda curta existe, mas é pequena sob os limiares de 50/100/150 palavras.
- ~~Por aderência ao template atual, a rasura é praticamente uniforme~~ — **ver CORREÇÃO acima**: 1.022 de 1.037 artigos têm exatamente uma das sete seções *do template* preenchidas, mas a mediana de headings reais é 10. Não é rasura, é convenção divergente. Também há zero itens de Referências em 1.035 artigos, e este ponto se sustenta.
- O problema de tamanho não é uniforme por topic. `cybersecurity` e `learning` concentram mais artigos até o P25 global do que os maiores grupos, enquanto `python` concentra menos; topics muito pequenos são apenas sinais, não evidência de concentração.
- Há near-duplicates materiais: 59 pares chegam a cosseno ≥0,95, com pares de títulos quase idênticos entre os exemplos. A mediana da similaridade máxima por artigo é 0,8733.
- Não há medida factual global de compressão fonte→artigo: a proveniência direta foi perdida. A proxy cobre 82,7% por basename, mas seus valores inconsistentes (inclusive entrada/saída <1) impedem tratá-la como razão de compressão comprovada.

Estes números separam dois fenômenos: a não-conformidade estrutural é ampla no corpus, enquanto a cauda curta de tamanho é desigual por topic. A decisão de destino do corpus permanece fora do escopo deste ticket.

## Verificação final

O relatório e o instrumento foram reexecutados duas vezes por seção. O comando abaixo compara os hashes das duas saídas sem criar arquivo no vault:

```bash
set -e
for section in universe size structure compression duplicates topics; do
  first=$(python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section "$section" | shasum -a 256 | awk '{print $1}')
  second=$(python3 scripts/measure_corpus_quality.py --vault /Users/wendeus/vault --section "$section" | shasum -a 256 | awk '{print $1}')
  test "$first" = "$second"
  printf '%s %s\n' "$section" "$first"
done
```

Saída observada:

```text
universe b58929734243ad9f2978f317d1b67b814a55ccae2f09334a2329e47ea2724234
size e33288072925c4db278edb09efa33d1674edf87c6cbea744d7a4c6555d7d0d09
structure d67da7e42c1dfde6aaa243535e10af75756c8e0f2383e288f77a32937eb9475c
compression 283803a8fc25e10e73e0166b919b39ccda0d3da7165069518113650cf4c87566
duplicates 8ae8aea6dcc6f57b292d510aa8b887bb2b8caff881f849203930e02cd54101bc
topics 3512c746a3fd577310f1065831cbe1ec05ae4f969697f46bc8d590236d7e9cac
```

Estado do vault antes e depois da medição:

```bash
cd /Users/wendeus/vault && git status --porcelain
```

```text
 M kb_state/learnings.json
 M kb_state/rerank.json
```

Não houve arquivo novo, removido ou modificado no vault pela medição.
