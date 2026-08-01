# O que a tela faz que o Obsidian não faz?

Type: prototype
Status: resolved (2026-07-31)
Blocked by: 004-wiki-produto-ou-insumo

## Question

Qual é o trabalho que uma interface própria faz e o Obsidian sobre `wiki/` não faz?

O map anterior deixou "decidir se o kb terá UI própria" em Out of scope, chamando-a de decisão de direção de produto ([MAP.md:55](../../2026-07-28-engenharia-reversa/MAP.md)). Este ticket é essa decisão, trazida para dentro do escopo a pedido do usuário, que mencionou estar colhendo inspirações visuais.

A resposta depende do 004 e muda de natureza conforme ele:

- **Wiki como produto** → a tela é um leitor de markdown com grafo e busca. O Obsidian já faz isso bem, com plugins e sem custo de manutenção. O ônus da prova é alto: o que justifica construir?
- **Wiki como insumo** → a tela é o front do `qa` e expõe **estado operacional**, não conteúdo. É o padrão que o dossiê do rowboat registrou: topologia, ciclo de vida de jobs, draft/live, reasoning e tool calls tipados. O Obsidian não faz nada disso, e o ônus da prova inverte.

Candidatos de trabalho que o Obsidian não faz, a validar com o usuário:

- ver o que o retrieval trouxe para uma pergunta e por quê — score por canal, o que o rerank moveu, o que o cap de 4k cortou;
- acompanhar compile/heal/index em andamento, que hoje só existem como saída de terminal;
- a lacuna de corpus do ticket 005 como estado visível: o que o vault não cobre e o que está na fila para entrar;
- comparar resposta com e sem rerank, ou entre perfis de retrieval, lado a lado.

**Método:** resolver com artefato barato, não com discussão. Usar a skill `prototype` — um mock estático já basta para separar "quero isso" de "achei bonito". O usuário traz as inspirações; a saída do ticket é a decisão de construir ou não, e se sim, qual é o trabalho que a tela faz.

**Restrição:** decidir, não construir. Implementação sai pelo `spec-pipeline` como qualquer outra coisa deste map.

## Evidência para o grilling

> Compilada em 2026-07-31. Organiza o que a sessão mediu; não decide.

**A lista de "coisas que o Obsidian não faz" ganhou itens concretos e mensuráveis nesta sessão** — todos do ramo "wiki é insumo", em que a tela mostra estado, não conteúdo:

- **Ver o que o retrieval trouxe e por quê.** Agora existe dado para mostrar: `channel_scores` por canal (keyword/densidade/BM25), o que o rerank moveu, e — desde o PR #51 — de qual seção do artigo saiu o trecho que o reranker leu. Antes disso, candidato só-semântico chegava sem texto nenhum, então nem havia o que exibir.
- **Medição degradada é estado visível.** O PR #55 fez o bench marcar `degraded` quando o provider falha no meio do lote. Um painel que mostra "esta medição vale / esta não vale" resolve uma classe de erro que já custou duas medições perdidas (2026-07-29 e 2026-07-30) — e o terminal só avisa quem estava olhando na hora.
- **Conteúdo aguardando revisão.** Com o `discovery` sem auto-commit (PR #54), passa a existir uma fila real de material ingerido e não revisado. Isso é um estado que hoje não tem superfície nenhuma.
- **Avisos de injeção por artigo.** `scan_injection` emite avisos em stderr — que se perdem. São por natureza uma lista que alguém precisa triar.

**Contra construir:** o Obsidian continua sendo um bom leitor, e todo item acima é de operação, não de leitura. Se o 004 decidir "produto", o ônus da prova para uma tela própria fica alto de novo.

**Método continua o mesmo:** resolver com `prototype` (mock estático basta para separar "quero isso" de "achei bonito"), com o usuário trazendo as inspirações. A saída do ticket é decidir, não construir.

## Answer

**A tela é a superfície de autoria e leitura: você pede o tema e lê o artigo ali mesmo. Ela absorve a leitura — o Obsidian sai.** Decidido no grilling de 2026-07-31.

### A pergunta do ticket mudou

Este ticket perguntava "o que a tela faz que o Obsidian não faz", supondo que a resposta dependia de a wiki ser produto ou insumo. O [004](004-wiki-produto-ou-insumo.md) decidiu produto **e** que o app próprio é o destino — então o ônus da prova já não estava em construir.

O que mudou de verdade foi o **trabalho a fazer**: os três grillings criaram operações que não existiam quando o ticket foi escrito.

- **Pedir um tema** (004): o artigo de tema é gerado sob demanda. Isso não é leitura, é autoria — o módulo que a `011/DOMAIN.md` desenhou e nunca foi construído.
- **Aprovar o mapa de reagrupamento** (006): o LLM propõe, o humano aprova. É revisão de ~30 temas contra 1.037 artigos.
- **Ver tema stale** (005): livro novo marca o tema como desatualizado; a fila precisa de superfície.
- **Navegar proveniência** (006): com `_chapters/` fora da busca, "de quais capítulos este tema veio" só existe se a tela mostrar.

Em compensação, a lista original do ticket perdeu força: ver score por canal e acompanhar jobs pressupunha "wiki como insumo".

### O que decidiu

1. **Primeiro trabalho: pedir tema e ver o artigo nascer** — fontes que ele vai costurar, acompanhamento, aprovação.
2. **A tela absorve a leitura.** O Obsidian sai da divisão de trabalho; a decisão 1 da `011/DOMAIN.md` (app próprio como superfície única) volta a valer integralmente.
3. **v1 já lê.** O ciclo fecha no primeiro dia: tema pedido, tema lido. Não há fase em que o produto dependa de outra ferramenta para ser útil.

### Um argumento que apareceu na medição

**O Obsidian não honra a convenção `_*`** — ela exclui do índice do `kb`, não do Obsidian, que mostra todo `.md` do vault. Depois da migração do 006, o Obsidian exibiria os ~30 artigos de tema **misturados com os 1.037 capítulos** de `_chapters/`. Dá para configurar exclusão manual em Options → Files & Links, mas o default piora a experiência em vez de melhorar.

Ou seja: a política do 006 degrada o Obsidian como leitor. Isso não decidiu a questão sozinho, mas remove o argumento "o Obsidian já faz bem" que o ticket usava como ônus da prova.

### O que isso custa, declarado

Absorver a leitura significa competir com um produto maduro em wikilinks, grafo, busca e mobile. A `011/DOMAIN.md` falava em Swift nativo (decisão 1) com engine servida por API HTTP em terceiro servidor (decisões 6 e 9) — é o item mais caro de tudo que este map decidiu, e por larga margem.

O que reduz o custo: **o corpus visível encolhe de 1.037 para ~30**. Ler 30 artigos de tema é problema de outra ordem que navegar mil capítulos.

### Restrição preservada

Decidir, não construir. A implementação sai pelo `spec-pipeline`, e a skill `prototype` continua sendo o caminho certo para separar "quero isso" de "achei bonito" antes de qualquer código de UI — agora com o escopo já definido: pedir tema, acompanhar geração, ler o resultado.

<!-- preencher na resolução -->
