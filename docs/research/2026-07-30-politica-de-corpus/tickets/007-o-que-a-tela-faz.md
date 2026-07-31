# O que a tela faz que o Obsidian não faz?

Type: prototype
Status: open
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

<!-- preencher na resolução -->
