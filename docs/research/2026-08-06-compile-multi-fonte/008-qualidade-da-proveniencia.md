# 008 — Qualidade da proveniência do manifest

Type: research
Status: resolved
Blocked by: nada

## Question
Qual é a taxa de erro da proveniência do manifest? 824 de 856 entradas (96%) foram atribuídas por `backfill-basename` — match de nome de arquivo entre `library/` e wiki — com apenas 19 por conteúdo e 13 por cosseno (E4). A cadeia de desempate (`kb/backfill.py:81-115`) tenta basename primeiro, e o que não desempata vira `unresolved`. A pergunta é empírica: em que proporção o match por nome de arquivo aponta para o livro errado?

O ADR faz da proveniência O critério de agrupamento de fontes em temas. Se o basename erra em taxa relevante — nomes genéricos, edições diferentes, capítulos homônimos entre livros — então uma fatia dos 856 vínculos fonte↔artigo está errada, e qualquer agrupamento construído sobre eles herda o erro.

Há um segundo eixo de erro, mais barato de medir e já visível: o **falso negativo**. Sete artigos ficaram soltos na raiz da wiki, sem diretório de topic, com títulos que os denunciam como capítulos de livro — *API Design Patterns* front matter, "dentro da capa: tópicos de design de APIs", `honeycomb.md` (*Observability Engineering*), "introdução à integração de aplicações com mensageria" (*Enterprise Integration Patterns*) — e continuam na wiki apenas porque o backfill não conseguiu pareá-los (E13). Eles são amostra pronta: para cada um, a fonte existe em `library/` ou `_sources/` e não foi encontrada. Entender por que falharam dá a taxa de falso negativo sem construir amostragem nenhuma.

## Why it matters
Este ticket pode derrubar [medir-sobreposicao-tematica](001-medir-sobreposicao-tematica.md), e por isso o bloqueia: se a proveniência é ruidosa, medir sobreposição sobre vínculos errados produz um ranking de pilotos inválido e um número de gatilho incorreto para [destino-dos-capitulos](005-destino-dos-capitulos.md). A assimetria é desfavorável — o custo de medir a taxa de erro é pequeno; o custo de construir o piloto sobre proveniência podre é o destination inteiro.

## What would settle it
Uma medição (AFK) das duas taxas de erro, separadas:

1. **Falso positivo** — amostra das 824 atribuições por basename, verificada contra os sinais mais fortes disponíveis (conteúdo normalizado, cosseno), com taxa estimada e intervalo de confiança.
2. **Falso negativo** — diagnóstico dos 120 `unresolved`, começando pelos 7 soltos na raiz da wiki, que têm fonte identificável a olho: por que a cadeia falhou em cada um (basename divergente, fonte só em binário, capítulo homônimo, ausência de `metadata.json`).

E um veredito explícito: basename é confiável o suficiente para alimentar o agrupamento de temas, sim ou não — e, se não, qual o tamanho e a localização do estrago.

## Answer

**SIM — a proveniência por basename sustenta o agrupamento por tema.** O ticket
[medir-sobreposicao-tematica](001-medir-sobreposicao-tematica.md) está destravado.

Medição em 2026-08-06, vault @ `ec3fa16`. Artefatos: [veredito completo](008-VEREDITO.md)
(julgamento par a par pelo Kimi K3), [dados](008-data.json), [script de extração](008-extract.py).

**Falso positivo: 0 em 40 pares auditados**, do estrato que responde por 824 das 856
entradas. Limite superior de 7,5% a 95% pela regra do três — a amostra sustenta "erro
baixo", não "erro zero". Três pares conferidos de novo pelo orquestrador (*Naming* →
nomenclatura em APIs, *The Testing Gap* → a lacuna de testes, *Slow Indexes Part II* →
índices lentos): todos corretos.

O que decide o ticket não é a taxa, é a **anatomia da falha**: 1.342 dos 1.416 basenames
são únicos (94,8%), e as 74 colisões são paratexto padronizado de conversão de ebook —
`03-preface.md` (6×), `01-cover.md` (6×), `20-index.md` (4×). Quando a cadeia não
resolve, ela **omite** em vez de atribuir errado. Para agrupamento, errar por omissão é
o lado seguro.

**Os 120 `unresolved` têm três causas, e só seis são falha do algoritmo:**

| Causa | Artigos | Natureza |
|---|---:|---|
| Fonte ausente do acervo | 112 | 88 transcrições de YouTube sem arquivo correspondente, 15 capítulos de *Building Applications with AI Agents* (livro fora do acervo), 9 outros |
| Duplicata de livro no acervo | 2 | `02-honeycomb.md` em duas pastas do mesmo *Observability Engineering* |
| Limitação da cadeia em paratexto ambíguo | 6 | `01-copyright.md`, `08-front-matter.md`, `06-introduction.md` colidindo entre livros; ~4 seriam desempatáveis pelo título do artigo, sinal que a cadeia não usa |

**Ressalvas que o ticket 001 herda:**

1. **Cobertura, não precisão, é o gargalo.** 120 de 345 vivos (35%) ficam fora do
   agrupamento, e o viés é concentrado: quase todo `learning` e um livro inteiro de `ai`.
2. **A amostra validou só `backfill-basename`.** As 32 entradas por conteúdo e cosseno
   (3,7%) entram no agrupamento sem auditoria.
3. **Proveniência agrupa por LIVRO, não por tema.** Event sourcing aparece em pelo menos
   três livros distintos só na amostra. A medição de sobreposição precisa tratar isso, ou
   medirá zero onde há sobreposição real.
4. **O denominador precisa ser decidido.** 856 entradas de manifest contra 345 artigos
   vivos — 631 apontam para `_chapters/`. Agrupar sobre vivos ou sobre o manifest inteiro
   dá resultados diferentes.
