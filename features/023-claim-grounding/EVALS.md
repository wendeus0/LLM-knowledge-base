---
feature: 023-claim-grounding
status: draft
created: 2026-08-01
---

# EVALS — QA: verificação de ancoragem por afirmação

**Spec:** features/023-claim-grounding/SPEC.md  
**Plan:** features/023-claim-grounding/PLAN.md  
**Pipeline avaliado:** seleção por embedding das três janelas de contexto e classificação NLI por MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7.

## Objetivo e regra de leitura

Este documento mede somente se o veredito de ancoragem de uma afirmação é compatível com o contexto que foi dado ao QA. O cosseno escolhe as premissas; ele não é o grader nem decide o veredito.

Os números disponíveis são uma linha de base **contaminada para aceite**: a deriva sutil teve 5/6, a fabricação injetada 12/12, a preservação de afirmações legítimas 72% (28% de falso alarme), e a janela de 12 sentenças foi escolhida depois de comparar 1/4/6/8/12/16 nos mesmos dados. Eles demonstram viabilidade, não desempenho a prometer. Não há baseline separado a registrar até que o holdout abaixo seja coletado.

Dimensões cobertas:

- **Correção / invariante de domínio:** 'ancorada', 'contradita' ou 'sem apoio' deve corresponder ao par contexto–afirmação.
- **Preservação:** uma síntese fiel de várias sentenças não deve virar alerta apenas porque a evidência está distribuída.

## Baseline provisório (não elegível para aceite)

| Dimensão | Resultado observado | Limite da evidência |
|---|---:|---|
| deriva sutil: negação, número e comparação | 5/6 | Mesmos dados usados para ajustar; amostra mínima. |
| fabricação injetada | 12/12 | Fabricações deliberadamente fáceis; mesmos dados usados para ajustar. |
| preservação de afirmações legítimas | 72% | Equivale a 28% de falso alarme; somente oito pares artigo→fonte, concentrados em IA/LLM. |
| tamanho da premissa | 12 sentenças escolhido entre 1/4/6/8/12/16 | Escolha feita olhando esses próprios resultados. |

O pipeline anterior à feature não tem veredito de grounding, portanto não há comparação pré/pós equivalente. A primeira linha de base válida será a execução congelada da configuração escolhida contra o holdout privado; mudanças futuras são regressão se caírem abaixo dos limiares por classe deste documento.

## Grader executável

Cada caso abaixo usa o grader 'veredito_exato'. Ele não pede revisão humana: passa apenas se o processo termina com código 0, isto é, se a primeira afirmação elegível recebe exatamente o veredito esperado. O comando roda o mesmo estágio 2 do protótipo, com o modelo real e o servidor local de embeddings exigidos pelo README do protótipo.

~~~bash
EVAL_CONTEXT='...' EVAL_CLAIM='...' EVAL_EXPECTED='...' \
/tmp/venv-nli/bin/python - <<'PY'
import importlib.util
import os
from pathlib import Path

path = Path("prototypes/answer-verification/pilha.py")
spec = importlib.util.spec_from_file_location("answer_verification_pilha", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.avaliar_ancoragem(
    os.environ["EVAL_CLAIM"],
    os.environ["EVAL_CONTEXT"],
    module.carregar_nli(),
)
assert len(result) == 1, result
assert result[0]["veredito"] == os.environ["EVAL_EXPECTED"], result[0]
PY
~~~

Para a feature implementada, o mesmo invólucro deve chamar 'kb.grounding.verify()' pelo cliente HTTP local, preservando a regra de saída acima. Até existir esse adaptador, este comando de protótipo é o grader executável de referência; nenhum caso deve ser marcado como executado pela feature. Os testes unitários e de integração da feature continuam necessários para o contrato HTTP, janelas, orçamento e CLI — não são substituídos por esta eval.

## Casos públicos de regressão

Os casos são públicos deliberadamente: ajudam a detectar quebra óbvia da composição embedding → NLI. Eles não entram no cálculo do aceite do holdout. Para executar um caso, copie seu contexto, afirmação e veredito esperado para as três variáveis do comando anterior; o grader é sempre 'veredito_exato'.

### Negação explícita

- **id:** E-NEG-001
- **classe de falha:** negação explícita.
- **entrada:**
  - contexto: Após falhas consecutivas, o circuit breaker abre e interrompe temporariamente novas chamadas. Depois de um intervalo de recuperação, ele permite uma chamada de teste.
  - afirmação: O circuit breaker NÃO abre após falhas consecutivas e mantém novas chamadas ativas.
- **veredito esperado:** 'contradita'.
- **grader:** 'veredito_exato'; executar o comando anterior com EVAL_EXPECTED=contradita. Este é o caso didático: na medição do protótipo, a variante “NÃO abre” teve cosseno 0,786 e contradição NLI 0,998. Portanto, aceitar a afirmação por similaridade é falha.

### Número ou quantidade trocada

- **id:** E-NUM-001
- **classe de falha:** número/quantidade trocada.
- **entrada:**
  - contexto: O orçamento padrão permite no máximo 24 julgamentos NLI por resposta. Como cada afirmação recebe três premissas candidatas, no máximo oito afirmações são verificadas.
  - afirmação: O orçamento padrão permite no máximo 12 julgamentos NLI por resposta.
- **veredito esperado:** 'contradita'.
- **grader:** 'veredito_exato'; executar o comando anterior com EVAL_EXPECTED=contradita.

### Comparação invertida

- **id:** E-CMP-001
- **classe de falha:** comparação invertida.
- **entrada:**
  - contexto: Com janelas de 12 sentenças, a preservação observada foi 72%. Com janelas de 16 sentenças, a preservação observada foi 70%.
  - afirmação: Janelas de 16 sentenças preservaram mais afirmações legítimas do que janelas de 12 sentenças.
- **veredito esperado:** 'contradita'.
- **grader:** 'veredito_exato'; executar o comando anterior com EVAL_EXPECTED=contradita.

### Fabricação sem relação com o contexto

- **id:** E-FAB-001
- **classe de falha:** fabricação sem relação com o contexto.
- **entrada:**
  - contexto: O serviço NLI local aceita pares de premissa e hipótese. O processo deve escutar somente em loopback e a resposta de QA segue disponível quando o serviço falha.
  - afirmação: A migração do banco de dados cria uma tabela de auditoria para cada veredito.
- **veredito esperado:** 'sem apoio'.
- **grader:** 'veredito_exato'; executar o comando anterior com EVAL_EXPECTED='sem apoio'.

### Síntese legítima de várias sentenças

- **id:** E-SIN-001
- **classe de falha:** afirmação legítima que sintetiza várias sentenças.
- **entrada:**
  - contexto: O contexto é dividido em janelas deslizantes de 12 sentenças. Janelas sucessivas avançam seis sentenças para preservar sobreposição. Para cada afirmação, embeddings selecionam as três janelas mais similares antes da classificação NLI.
  - afirmação: A verificação usa três janelas sobrepostas de 12 sentenças para reunir evidência distribuída antes do julgamento NLI.
- **veredito esperado:** 'ancorada'.
- **grader:** 'veredito_exato'; executar o comando anterior com EVAL_EXPECTED=ancorada. Este caso mede exatamente a fonte conhecida de falso alarme; não pode ser reduzido a uma premissa de uma sentença.

### Afirmação legítima que exige conhecimento externo: caso de borda

- **id:** E-EXT-001
- **classe de falha:** afirmação cujo julgamento depende de conhecimento externo ao contexto.
- **entrada:**
  - contexto: Merge sort divide uma sequência em partes menores, ordena as partes e depois as mescla.
  - afirmação: Merge sort tem complexidade O(n²) no caso típico.
- **veredito esperado:** 'sem apoio'.
- **grader:** 'veredito_exato'; executar o comando anterior com EVAL_EXPECTED='sem apoio'.

O contexto não diz nada sobre complexidade, então o veredito correto de **ancoragem** é 'sem apoio': a afirmação não é sustentada pelo que foi dado, independentemente de ser falsa no mundo. Medido: entailment 0,004 e contradição 0,007, ambos quase nulos, com neutro dominante — o comportamento certo.

A redação original esperava 'contradita', citando entailment 0,357 e contradição 0,615 do protótipo. Os dois pontos estavam errados: o número não reproduz com este contexto (veio de outra premissa) e esperar 'contradita' contradizia o princípio declarado na própria frase seguinte — para ancoragem, a correção deve derivar do contexto, não da memória do modelo. Corrigido após execução. Este caso **não conta** para a taxa de aceite.

## Resultado da primeira execução (2026-08-01)

Os seis casos rodaram contra o modelo real antes de este documento sair de `draft`. **Três falharam**, por três motivos distintos:

| Caso | Esperado | Obtido | Entailment | Contradição | Leitura |
|---|---|---|---|---|---|
| E-NEG-001 | contradita | contradita | — | — | passa |
| E-NUM-001 | contradita | contradita | — | — | passa |
| E-CMP-001 | contradita | **sem apoio** | 0,302 | 0,377 | limitação real |
| E-FAB-001 | sem apoio | sem apoio | — | — | passa |
| E-SIN-001 | ancorada | **contradita** | 0,015 | **0,953** | falso alarme confiante |
| E-EXT-001 | ~~contradita~~ sem apoio | sem apoio | 0,004 | 0,007 | expectativa corrigida |

**E-CMP-001 — comparação numérica não é detectada.** A contradição fica em 0,377, abaixo do corte de 0,5, e o caso cai em 'sem apoio'. Decidir que 70% < 72% invalida a afirmação exige aritmética, não inferência textual, e o NLI não faz aritmética. É buraco de cobertura conhecido, não erro de configuração: a classe "comparação invertida" só é pega quando a inversão é lexical ("maior"/"menor" contra texto explícito), não quando depende de comparar dois números. O caso fica no conjunto, falhando e documentado.

**E-SIN-001 — o achado que importa.** Uma síntese fiel de três sentenças recebeu contradição **0,953**. Não é hesitação: é alarme confiante contra conteúdo legítimo, com a premissa inteira disponível (o contexto cabe numa janela só, então não é o erro de premissa picada já corrigido). A medição anterior tratava os 28% de falso alarme como ruído brando; este caso mostra que parte dele chega como contradição de alta confiança — a anotação mais alarmante que a feature pode emitir. Um caso não é estatística, mas muda o desenho: a apresentação precisa separar visualmente 'contradita' de 'sem apoio', e o holdout precisa medir a **distribuição** do falso alarme entre os dois vereditos, não apenas a taxa agregada.

Nenhum dos três interrompe a feature — a anotação não bloqueia (RF-06). São os limites reais entrando na documentação antes do código, que é para isso que este eval existe.

## Threshold de aceite

Os seis casos públicos são de **regressão, não de aceite**: hoje três dos seis passam, e as duas falhas remanescentes estão documentadas acima como limites conhecidos. A regra é não regredir — caso que passa hoje e falha depois é quebra; caso que já falha não pode piorar para o veredito oposto. Eles são poucos e conhecidos; por isso não aprovam o classificador.

O aceite da capacidade depende exclusivamente de exemplos do holdout, separados por par artigo→fonte e calculados por classe, nunca por uma média global:

| Classe no holdout | Aceite proposto | Justificativa |
|---|---:|---|
| negação, número e comparação, em conjunto | ≥ 70% sinalizados como 'contradita' | **Julgamento de calibração, não número medido.** O teto contaminado é 5/6 (cerca de 83%); reservar 13 pontos percentuais evita rebatizá-lo como garantia e ainda exige sinal útil contra deriva sutil. |
| fabricação sem relação | ≥ 80% como 'sem apoio' | **Julgamento de calibração.** O teto contaminado é 12/12, mas as fabricações atuais são reconhecidamente fáceis; a margem de 20 pontos não presume repetição de 100% fora da amostra. |
| síntese legítima de várias sentenças | ≥ 65% como 'ancorada' | **Julgamento de calibração.** Fica sete pontos abaixo dos 72% contaminados e aceita até 35% de falso alarme somente porque a SPEC torna a anotação não bloqueante. Não é nível aceitável para bloquear ou reescrever resposta. |

E-EXT-001 é reportado à parte e não entra em nenhuma taxa. Um resultado inferior ao teto atual no holdout não reprova o processo de avaliação; é a medição mais honesta do desempenho fora dos dados que influenciaram os parâmetros. A feature só fica aprovada se satisfizer os três limiares acima no holdout e se nenhum caso público regredir.

## Holdout: definição, tamanho e viabilidade atual

### Separação exigida

O holdout precisa ter **30 pares artigo→fonte, confirmados manualmente e nunca usados para escolher limiar, tamanho de janela ou exemplos públicos**. Trinta é uma decisão de planejamento, não uma quantidade medida: é o menor alvo que permite distribuir as classes sem avaliar somente dois ou três casos por uma delas. O split é por par, não por afirmação: todas as afirmações, mutações e fabricações derivadas de um artigo e sua fonte ficam no mesmo lado.

Uma calibração completa requer adicionalmente 60 pares novos e confirmados no conjunto de desenvolvimento: 90 pares novos no total, em split 60 desenvolvimento / 30 holdout. A proporção também respeita a regra de manter o holdout em pelo menos 30% do conjunto público. Esses tamanhos são decisões de planejamento, não uma amostra já medida.

Para cada par, um curador deve registrar em um manifest privado e ignorado: o caminho relativo do artigo, o caminho da fonte, o método de confirmação, um trecho de origem e os IDs das afirmações derivadas. O repositório não recebe esse manifest nem os textos do holdout; recebe somente a data da execução, hashes dos pares e as contagens por classe. Assim, quem ajusta os parâmetros não vê antecipadamente os casos de aceite.

O conjunto de 30 pares deve permitir, no mínimo, 10 mutações de negação, 10 de número, 10 de comparação, 15 fabricações não relacionadas e 15 sínteses legítimas. Um par pode render mais de uma afirmação; não pode atravessar o split. Essa composição tem 60 julgamentos de referência e não é uma medição existente — é requisito para a coleta.

### Como obter os pares

1. Enumerar os 1.037 artigos de ~/vault/wiki, excluindo wiki/_sources/, e as candidatas em wiki/_sources/ e library/.
2. Usar o campo source do frontmatter como descoberta inicial, mas não como prova: hoje ele encontra somente oito pares.
3. Para os demais, fazer confirmação humana de proveniência por título, URL/identificador citado, nome do arquivo e leitura do trecho correspondente na fonte. Registrar somente pares cujo trecho de fonte sustenta de forma verificável a afirmação do artigo.
4. Antes de rodar NLI, sortear e congelar o split por **par**: 60 pares vão para desenvolvimento e 30 para holdout privado. Não mover pares depois de ver as pontuações.

### Estado real e mínimo viável

O holdout tem **zero pares construídos hoje**. Há 1.037 artigos no vault, 712 arquivos em _sources/ e 863 fontes em library/, mas a proveniência artigo→fonte não foi materializada (manifest.json não existe). O único casamento automático disponível rendeu oito pares, quase todos de IA/LLM; eles já contaminaram as medições atuais e não podem ser promovidos a holdout.

Portanto, 30 pares não são alcançáveis automaticamente com o vault atual. O **mínimo viável** é coletar manualmente 24 pares novos para desenvolvimento e 12 novos para holdout, congelá-los antes de qualquer nova calibração e extrair ao menos quatro julgamentos por classe no holdout. Ele serve para detectar regressão grosseira, mas não para declarar os limiares estáveis: poucos casos tornam cada erro muito influente e a cobertura de domínio continuará incerta. Sem ao menos esses 12 pares novos de holdout **e** os 24 separados de desenvolvimento, não há holdout e não há aceite de desempenho; apenas os testes de contrato e a evidência exploratória do protótipo.

## Reajuste sem contaminar a validação

1. Coletar e congelar 60 pares de desenvolvimento e 30 de holdout novos; excluir do holdout os oito pares e todos os casos já vistos no protótipo. No mínimo viável, usar 24/12 e declarar o resultado como piloto.
2. Usar somente o conjunto de desenvolvimento para escolher a janela e os limiares. Para a janela, comparar os valores já estudados 1, 4, 6, 8, 12, 16; para a regra de contradição, pré-registrar uma grade antes da execução (por exemplo, 0,4, 0,5, 0,6). Esses valores de grade são **julgamento de calibração**, não resultados medidos. Qualquer valor diferente de 0,5 exige atualização posterior de RT-04; esta eval não altera a SPEC.
3. Escolher uma única configuração no desenvolvimento: primeiro deve atender os limiares por classe; entre as elegíveis, maximiza preservação de síntese; empate escolhe a configuração de menor custo. Congelar a escolha.
4. Rodar uma vez no holdout privado e publicar as taxas, os denominadores e os hashes dos pares. Não escolher nova configuração após observar esse resultado. Uma recalibração posterior exige outro holdout.

Se o holdout ficar materialmente pior que 5/6, 12/12 ou 72%, isso é um resultado válido: revela o viés otimista da medição original. Nesse caso, manter a anotação não bloqueante, reportar as taxas reais e decidir entre aceitar os limiares definidos, coletar mais pares ou revisar a arquitetura. Não se deve alterar o holdout até ele “passar”.

## Integração de execução

- Os casos públicos rodam junto da validação local/CI que toca grounding, com serviço NLI e embeddings reais provisionados explicitamente.
- O holdout privado roda no quality-gate de sistema, antes do merge, pelo mesmo grader e pela configuração congelada. O relatório contém apenas hashes, contagens, vereditos e versão do modelo.
- Nenhum resultado é um gate para exibir a resposta ao usuário: os limiares aprovam a feature, não bloqueiam kb qa, conforme RF-06.

## Anti-goals

Este eval não mede:

- cobertura do corpus, lacunas de assunto ou se o retrieval trouxe os melhores documentos;
- consistência entre múltiplas gerações, confiança verbalizada ou rerank;
- qualidade, completude, utilidade, estilo ou correção geral da resposta de QA, além da relação de uma afirmação com o contexto fornecido.
