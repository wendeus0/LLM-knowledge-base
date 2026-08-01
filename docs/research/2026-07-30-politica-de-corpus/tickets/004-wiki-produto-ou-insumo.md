# A wiki é produto ou insumo?

Type: grilling
Status: resolved (2026-07-31)
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

**A wiki é produto.** Decidido no grilling de 2026-07-31 (`grill-with-docs`); glossário, entidades e invariantes em [`DOMAIN.md`](../DOMAIN.md).

O usuário abre a wiki no Obsidian e lê o artigo. Isso fecha a pergunta central do map — mas a conversa expôs que **produto vs insumo não era o eixo mais importante**, e sim a **granularidade**.

### O que decidiu

1. **Artigo raso é bug**, não design. Os achados do 002 (seção "Exemplos" sem exemplos, *Information Leakage* traduzido como "Desconhecimento") são defeitos a pagar.
2. **O min-refs 5 da decisão 10 da 011 vale**, e os 1.035 artigos sem referência são dívida — não isentos.
3. **O compile passa a ser muitos→um.** Isto saiu de uma impossibilidade estrutural que o grilling encontrou: o compile é 1 documento → 1 artigo, então um artigo vindo de um capítulo tem **exatamente uma** fonte bibliográfica. Exigir cinco dele é impossível por construção, não por esforço do modelo. Ou o min-refs cai, ou o artigo costura várias fontes — e a escolha foi costurar.
4. **Os 1.037 artigos atuais têm a granularidade errada**, não só profundidade insuficiente. São recortes de capítulo; o produto quer recortes de tema. Absorvidos por um artigo de tema, vão para `_chapters/` — fora do índice e da busca pela convenção `_*` que o vault já usa, sem sair do disco.
5. **O artigo de tema é gerado sob demanda**, quando o usuário pede o tema. Não é job automático — é o módulo de autoria que a 011 desenhou e nunca construiu.
6. **Melhorar artigo vira comando próprio.** `heal` continua proibido de alterar conteúdo substantivo (`kb/heal.py:17-25`); aprofundar é operação nova e explícita.
7. **A superfície de leitura é o Obsidian hoje, o app próprio é o destino** — reafirma a decisão 1 da 011 e resolve a contradição com o `CLAUDE.md`, que declarava o Obsidian como frontend oficial sem dizer que era provisório.
8. **O retrieval é fundação do app**, não só do `qa`. O ADR-0017 e os consertos de 2026-07-31 (recall@5 0,467 → 0,526) seguem justificados sob "wiki é produto".

### O que ficou em aberto, e para onde vai

**Cardinalidade `Artigo de tema` × `Artigo-de-capítulo`.** Um capítulo sobre autenticação serve a "segurança de APIs" e a "criptografia aplicada". Se a relação é N:N, capítulo nunca é "consumido" e o critério de arquivamento por absorção cai. **Decisão adiada de propósito: medir a sobreposição temática no corpus antes de fechar** → ticket 006.

### Efeito nos outros tickets

- **006** muda de pergunta. Não é mais "manter, arquivar ou recompilar" — é **como reagrupar de capítulo para tema**, com a medição de sobreposição como primeiro passo. Os 59 pares com cosseno ≥ 0,95 deixam de ser só duplicação e viram evidência de que o recorte por capítulo fragmenta temas.
- **005** ganha restrição: o compile multi-fonte precisa de retrieval sobre `library/`, que não existe. A pergunta "de onde vem conhecimento novo" passa a conviver com "como o conhecimento que já está no vault é encontrado para costurar".
- **007** deixa de ser "construir ou não" e vira "o que a tela faz primeiro" — a decisão 7 já assume que ela vem.

### Pré-requisitos que a decisão expõe

Nenhum existe hoje, e todos bloqueiam a execução (detalhe em [`DOMAIN.md`](../DOMAIN.md)): rastreabilidade de origem por trecho, `manifest.json` materializado, retrieval sobre `library/`, e a medição de sobreposição temática.

O mais incômodo é o primeiro: sem proveniência por trecho, o gate de referências consegue contar linhas numa seção e **conta linha inventada igual**. A decisão 3 da 011 previa isso e nunca foi implementada.
