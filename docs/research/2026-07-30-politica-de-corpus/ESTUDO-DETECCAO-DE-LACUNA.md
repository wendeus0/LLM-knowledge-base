# Estudo — detecção automática de lacuna

> 2026-07-31. Insumo para revisitar o item 5 do [ADR-0018](../../adr/0018-corpus-policy-theme-articles-over-chapter-articles.md), que registrou "não há detecção automática de lacuna" com base numa medição que este estudo mostra ter sido **mal desenhada**.

## O erro de método que originou o estudo

A medição que fechou o ticket 005 comparou, dentro do golden set, o score dos casos em que o retrieval **achou** o artigo contra aqueles em que **não achou** no top-5. Concluiu que o score não separa.

A conclusão estava certa; a pergunta, não. **Os 152 casos do golden têm resposta no corpus** — o campo `expected` aponta para um artigo existente. Falhar ali é o retrieval não achando algo que está lá, não lacuna. Medir lacuna exige perguntas cuja resposta **não existe**, e o golden não tem nenhuma.

## Desenho correto

Três conjuntos:

| Conjunto | n | O que é |
|---|---:|---|
| **golden** | 152 | Resposta existe no corpus |
| **distante** | 20 | Domínio inteiramente ausente: culinária, medicina clínica, teoria musical, fotografia, biologia, história, jardinagem |
| **adjacente** | 16 | Mesma família do corpus (engenharia de software, dados, IA) mas assunto ausente: TLS/certificados, compiladores e parsing, operadores Kubernetes, sistemas operacionais |

O conjunto adjacente é o que importa. Lacuna real raramente é sobre risoto; é sobre o tema vizinho que o acervo **quase** cobre.

Cada ausência foi verificada por leitura do que o retrieval devolve, não só por busca de palavra. **`gradient descent` foi descartado do conjunto**: a frase em inglês não aparece, mas o conceito está em 57 artigos como `backpropagation` e 26 como `gradiente`. Ausência de frase não é ausência de conceito — o mesmo modo de falha que este projeto já registrou duas vezes.

## Resultados

Detecção de lacuna **adjacente**, com o custo em falso alarme:

| Sinal | Detecta | Preserva | Custo |
|---|---:|---:|---|
| termo distintivo ausente do corpus | 12% | — | zero |
| score RRF do 1º | 40% | 91% | zero |
| margem cosseno (1º−2º) | 75% | 43% | zero |
| cosseno com o artigo mais próximo | 100% | **67%** | zero |
| **cosseno com o centroide do tema** | **81%** | **84%** | zero |
| juiz por LLM (bonsai local) | **100%** | **17%** | 13s/pergunta |
| dois estágios (centroide + juiz) | ver abaixo | | 27% de chamadas LLM |

O juiz é o caso mais instrutivo: **é o único que pega todas as lacunas adjacentes, e é inutilizável** — rejeita 83% das perguntas que o vault sabe responder. Detectar bem não basta; o custo em falso alarme decide.

### Por que o RRF falha

RRF é soma de inversos de **posição**. Sempre existe um primeiro colocado, por pior que seja — o score do topo é quase constante, informe o corpus o que informar. Ele mede concordância entre canais, não distância ao conteúdo.

### Por que o termo ausente falha no caso adjacente

Funciona bem para lacuna distante (80% de detecção): "fotossíntese" e "diafragma" não existem no vault. Falha para adjacente (12%, contra 14% do próprio golden — separação zero): `kubernetes` aparece em 21 artigos, `compilador` e `escalonador` aparecem. **O vocabulário está lá; a cobertura não.**

### Por que o centroide de tema é melhor que o artigo mais próximo

O artigo mais próximo pode ser vizinho acidental. Pergunta sobre parser descendente recursivo trouxe `introducao-a-arvores-binarias-de-busca` a cosseno 0,525 — árvore sintática **é** parecida com árvore binária. Contra o centroide do tema, a mesma pergunta cai para 0,39.

O centroide representa o que o tema **cobre**; o artigo isolado representa o que ele **parece**.

| | mediana golden | mediana adjacente | distância |
|---|---:|---:|---:|
| artigo mais próximo | 0,554 | 0,471 | 0,083 |
| centroide de tema | 0,492 | 0,389 | 0,103 |

### Juiz por LLM — medido e reprovado

Perguntar ao modelo, com o contexto recuperado na mão: *"estes trechos respondem a pergunta? SIM ou NAO"*. Bonsai 27B 1-bit local, prompt curto, 3 artigos × 400 chars de contexto, 13,1s por chamada, 66 perguntas em 18,8 min.

| Grupo | Disse "SIM" | Acerto |
|---|---:|---:|
| golden (30, **tem** resposta) | **5/30** | **17%** |
| distante (20) | 0/20 | 100% |
| adjacente (16) | 0/16 | 100% |

**Pegou 100% das lacunas — inclusive as adjacentes, que nenhum sinal barato pega — e rejeitou 25 de 30 perguntas legítimas.** Não é um juiz calibrado; é um "não" com passos extras. Com 83% de falso alarme o `qa` fica inutilizável.

Duas causas plausíveis, não separadas por esta medição: o bonsai a 1 bit ser fraco para julgamento binário de answerability, e o contexto ser curto demais (400 chars × 3 artigos). Provavelmente ambas.

**Consequência para o desenho de dois estágios:** ele deixa de ser só economia de chamadas e vira **contenção de dano**. Mandar ao juiz apenas a faixa ambígua limita o falso alarme a 27% das perguntas em vez de 100%.

### Dois estágios (BAIXO 0,36 / ALTO 0,46)

O sinal barato decide o óbvio; só a faixa do meio paga LLM.

| Grupo | "tem" | ambíguo → juiz | "lacuna" |
|---|---:|---:|---:|
| golden (152) | 97 | 43 | 12 falso alarme |
| distante (20) | **0** | 1 | 19 |
| adjacente (16) | 3 | 7 | 6 |

Resolve **73% sem chamar o modelo**, com 89% de acerto, e manda 27% para o juiz. Nenhuma lacuna distante é declarada coberta.

Comparação decisiva: um **limiar único** resolve 98% das perguntas, mas deixa **10 das 16 lacunas adjacentes passarem** como se o vault soubesse. A faixa ambígua é o que compra a precisão.

## Verificação de grounding — mede outra coisa, e é a mais forte

Detecção de lacuna pergunta *"tenho material?"* **antes** de responder. Verificação de grounding pergunta *"o que eu escrevi vem do material?"* **depois**. São complementares, não concorrentes.

Protótipo em `scratchpad/grounding.py`: cada afirmação do texto gerado é comparada por embedding contra as sentenças do contexto; o veredito é a maior similaridade.

| | |
|---|---|
| Injeções fabricadas detectadas | **40/40 (100%)** |
| Similaridade das fabricadas | mediana **0,346**, máx 0,413 |
| Similaridade das legítimas (385 afirmações) | mediana **0,594**, p10 0,391 |
| **Limiar 0,416** | **100% de detecção, 87% de preservação** |

As faixas quase não se sobrepõem — a pior fabricada (0,413) fica abaixo da mediana legítima (0,594). É a separação mais limpa de todo este estudo.

**Nota de método que vale mais que o número:** o limiar chutado (0,60) dava 52% de falso positivo; o medido (0,416) dá 13%. Sem o verify de falso positivo, a abordagem teria sido descartada por causa do chute.

**Limitações:** só **12 pares artigo↔fonte** — a proveniência não existe, então o casamento foi pelo campo `source` do frontmatter contra `wiki/_sources/`, e todos os pares caíram no mesmo domínio (IA/LLM). E as afirmações fabricadas são fáceis: frases deliberadamente estranhas ao contexto. Deriva real é mais sutil — parafrasear errado, inverter condição, trocar número — e teria similaridade alta.

## Veredito das quatro abordagens

| # | Abordagem | Mede | Resultado | Aplica |
|---|---|---|---|---|
| 3 | Grounding por claim | deriva | **100% / 87%** | **sim — a mais forte** |
| 4 | Centroide de tema | lacuna | 81% / 84% | **sim — sai de graça do ticket 006** |
| 2 | Dois estágios | lacuna | 73% sem LLM | pronta, esperando juiz que preste |
| 1 | Juiz por LLM | lacuna | 100% / 17% | não, com o modelo local |

Duas aplicam, e cobrem pontas diferentes do problema. Nenhuma das duas depende do juiz que falhou, e ambas usam só embedding — servidor local já no ar.

## O que isso muda no ADR-0018

O item 5 do ADR está **certo no veredito e incompleto na justificativa**. Continua verdade que nenhum sinal barato sozinho resolve o caso adjacente. Mas:

1. O **centroide de tema** é substancialmente melhor que tudo que havia sido testado, e **sai de graça** do reagrupamento do ticket 006 — com ~30 temas nomeados tende a melhorar, porque os centroides ficam mais representativos que os 116 clusters simulados aqui.
2. O desenho de **dois estágios** torna o juiz de LLM economicamente viável: 27% das chamadas em vez de 100%.
3. A conclusão "exige medida de confiança que o retrieval não produz" permanece — mas o caminho para ela ficou mais curto e mais barato do que o ADR supôs.

**Recomendação:** manter a decisão do ADR (não há detecção automática hoje) e registrar que a reabertura tem caminho medido, dependente do reagrupamento por tema. O gatilho de revisão do ADR já cobre isso; este estudo é a evidência que o instrui.

## Fragilidades declaradas

- Os conjuntos negativos são pequenos: 20 distantes e **16 adjacentes**, contra 152 positivos. A estimativa do lado negativo tem incerteza grande.
- Os temas do teste 4 são **clusters de cosseno**, não os ~30 temas nomeados que o ticket 006 vai produzir. A medição precisa ser refeita depois do reagrupamento.
- Todos os limiares foram ajustados **nos mesmos dados em que são avaliados**. Não há conjunto de validação separado; os números são teto otimista.
- O conjunto adjacente cobre quatro assuntos (TLS, compiladores, k8s, SO). Outros vizinhos podem se comportar de outro jeito.
