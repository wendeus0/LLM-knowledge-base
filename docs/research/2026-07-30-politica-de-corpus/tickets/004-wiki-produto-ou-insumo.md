# A wiki é produto ou insumo?

Type: grilling
Status: open
Blocked by: 002-atravessar-google-dorking, 003-medir-qualidade-corpus

## Question

O artigo compilado existe para ser lido por você, ou é matéria-prima que só o `qa` consome?

Esta é a decisão central do map. Todas as outras derivam dela, e o projeto hoje responde as duas coisas ao mesmo tempo sem ter decidido nenhuma: o `CLAUDE.md` diz que o frontend oficial é o Obsidian sobre `wiki/` (a wiki é produto), mas o grilling de abertura deste esforço estabeleceu que o produto esperado é o `kb qa` redigindo na hora (a wiki é insumo).

**Se a wiki é produto** — o artigo é o entregável, lido no Obsidian:

- o compile precisa de gate de profundidade, e a definição de artigo robusto de `011/DOMAIN.md:11` volta à mesa com o min-refs que foi adiado;
- artigo raso é **bug**, e o que o ticket 003 medir vira dívida a pagar;
- `heal` proibido de melhorar conteúdo (`kb/heal.py:17-25`) passa a ser um problema: nada no pipeline aprofunda um artigo raso, nunca;
- o retrieval importa menos — você navega por links, não por busca;
- a interface do 007 é um leitor, e o Obsidian já é um bom leitor.

**Se a wiki é insumo** — o artigo é contexto para o `qa`, e ninguém o lê direto:

- artigo raso é **design**, não bug, desde que preserve os fatos que o `qa` precisa recuperar;
- a métrica que importa deixa de ser densidade do artigo e passa a ser fidelidade da resposta — o grader que nunca foi construído (`PENDING_LOG.md:119`);
- o retrieval é tudo, e o teto de `recall@20` = 0,720 vira o número mais importante do projeto;
- o cap de 4k do perfil `fast` (`kb/config.py:85`) e o perfil `article` órfão (`:88`) deixam de ser detalhe de config e viram decisão de produto;
- a interface do 007 é o front do `qa` e mostra estado, não conteúdo — o padrão que o dossiê do rowboat registrou.

**Terceira possibilidade a não descartar de saída:** produto para alguns topics e insumo para outros. O que o ticket 003 medir sobre distribuição por topic pode sustentar isso — ou torná-lo indefensável.

**Insumos obrigatórios antes de responder:** o atrito real registrado em 002 e os números de 003. Responder isto antes das duas evidências é escolher no escuro.

## Evidência para o grilling

> Compilada em 2026-07-31 após 002 e 003 fecharem, mais o que a sessão de correções mediu. Não decide nada — organiza o que já é fato para a conversa não recomeçar do zero.

**O que 003 provou sobre o corpus:** não é raso (mediana de 10 headings, 93% com ≥5, nenhum sem heading), mas não segue o template (mediana de 1 seção com nome do molde), tem **1.035 de 1.037 artigos sem nenhuma referência** e **59 pares** com cosseno ≥ 0,95.

**O que 002 provou sobre a compilação:** o artigo sai com as 7 seções do template e mesmo assim erra o essencial. A seção "Exemplos" não tem exemplos — num artigo sobre dorking, zero dorks — e repetir com 4× o contexto não mudou nada, o que localiza a causa no prompt/template, não no modelo nem na janela. O título saiu com *Information Leakage* traduzido como "Desconhecimento". Erro de compile chega íntegro ao leitor: `"filetype: Concorda apenas um tipo de arquivo"` apareceu nas duas respostas medidas do `qa`.

**Três coisas mudaram desde o charting e alteram o custo de cada ramo:**

1. **Existe gate de saída no compile** (PR #46): `_validate_output` barra seção declarada e vazia e placeholder do template não substituído. Calibrado no corpus: 1 reprovado em 1.039. Se a wiki for **produto**, este é o lugar onde o gate de profundidade entra — a estrutura já está montada.
2. **Detectar "Exemplos que não são exemplos" foi tentado e falhou** com três heurísticas medidas contra o corpus (Jaccard, concretude condicional, fração de termos novos — registrado no PENDING_LOG). Nenhuma separa. Um gate de qualidade de conteúdo exige **juiz semântico (LLM no gate)**, que é decisão de custo própria. Isso pesa contra o ramo "wiki é produto": o gate que ele pede não é barato.
3. **O retrieval melhorou de novo** (PRs #50/#51): colisão de stem não some mais com artigo, e candidato exclusivamente semântico deixou de chegar ao reranker como slug sem texto. Se a wiki for **insumo**, o teto de `recall@20 = 0,720` é o número a atacar, e estes dois consertos são pré-requisito de qualquer medição confiável dele.

**O que continua sem instrumento:** a fidelidade da resposta. O grader pedido em `PENDING_LOG.md:119` nunca foi construído, e `kb bench` mede ordenação de artigo, não resposta. **Enquanto ele não existir, o ramo "insumo" não tem como provar que está funcionando** — é a assimetria mais importante desta decisão.

**Assimetria de custo, resumida:**

| | Wiki é produto | Wiki é insumo |
|---|---|---|
| Gate que falta | profundidade + min-refs no compile — exige juiz semântico (medido) | grader de fidelidade — não existe |
| O que 003 mede vira | dívida a pagar em 1.037 artigos | característica aceitável |
| Métrica que manda | densidade do artigo | `recall@20` = 0,720 e a fidelidade |
| Interface do 007 | leitor (Obsidian já é bom nisso) | front do `qa`, mostrando estado |

## Answer

<!-- preencher na resolução -->
