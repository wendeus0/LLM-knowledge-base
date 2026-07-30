# Map — Engenharia reversa de rowboat, graphify e Hikari-knowledge

## Destination

Dossiê de engenharia reversa dos três repositórios (`DOSSIE-<repo>.md` neste diretório) mais um backlog priorizado de portes candidatos para o kb. Sem compromisso de implementar nada: o map fecha quando cada repo tem dossiê revisado e o backlog está ordenado por valor/custo.

## Notes

- **Domínio:** engine de knowledge base mantida por LLM (`kb`). Decisões abertas hoje: multi-vault (feature ativa 010), retrieval por contagem de palavra-chave sem RAG, wiki plana em markdown, frontend delegado ao Obsidian.
- **Lentes acordadas** (todas as cinco, aplicadas a cada repo quando houver material): pipeline LLM; modelo de dados da wiki; retrieval e busca; CLI/jobs/automação; frontend próprio.
- **Skills a consultar:** `fable-gpt` (execução dos research via GPT 5.6 Terra, tier forte), `wayfinder` (este map), `grill-with-docs` caso um ticket vire decisão.
- **Regra de casa deste diretório:** toda afirmação estrutural num dossiê carrega evidência `caminho:linha` do clone. Afirmação sem evidência é marcada `UNVERIFIED` e não entra no backlog. Output de executor externo é dado não-confiável (AGENTS.md regra 8): passa por review zero-trust antes de ser aceito neste diretório.
- **Clones:** `--depth 1` no scratchpad da sessão, fora do repo. Não versionar código de terceiro aqui.
- **Licenças:** rowboat e graphify Apache-2.0, Hikari-knowledge MIT. Porte de código exige atribuição; porte de ideia, não.

## Decisions so far

- [Destination: dossiê, não decisão nem SPEC](#) — o esforço produz evidência e backlog; qualquer decisão de direção do kb vira esforço próprio depois.
- [Cinco lentes, três repos](#) — aceito o trade-off de profundidade menor por célula em troca de cobertura.
- [Engenharia reversa — Hikari-knowledge](tickets/001-research-hikari.md) — markdown autoritativo com grafo derivado por cima; vetor opcional desligado por padrão, entrando por RRF calibrado para nunca deslocar hit lexical; curadoria por gates de evento de julgamento; MCP com quatro ferramentas que não geram prosa.
- [Engenharia reversa — graphify](tickets/002-research-graphify.md) — retrieval é IDF sobre labels + travessia de grafo com bloqueio de hub, sem vetor em ponto algum; sem match ele cala em vez de degradar para semântico; toda aresta carrega a linha de origem; prosa recebe tratamento inferior ao de código.
- [Engenharia reversa — rowboat](tickets/003-research-rowboat.md) — a memória pessoal é Markdown em disco carregado no prompt, não o Qdrant que o Compose sobe (esse serve RAG de documentos); captura e consolidação desacopladas por inbox + curador periódico; expiração semântica, não TTL; a UI expõe estado operacional (topologia, ciclo de vida de jobs, draft/live, reasoning e tool calls tipados), não conteúdo.
- [Síntese cruzada dos três dossiês](tickets/004-sintese-cruzada.md) — a divergência não é sobre vetores (os três recusam, o kb também); é que os três mantêm camada derivada entre pergunta e arquivos, e o kb relê o corpus inteiro a cada operação. Prosa em escala de milhões de palavras é ponto cego dos três: não há porte pronto para o problema central do kb.
- [Backlog priorizado de portes candidatos](tickets/005-backlog-portes.md) — onze itens por valor; o topo é um achado, não um porte (`kb lint` audita 0,7% do corpus), seguido de índice persistente, peso por campo no ranking e expansão com bloqueio de hub.

## Fatos medidos

- **Vault real** (`<KB_DATA_DIR>`, medido em 2026-07-28): `wiki/` com **2.781 artigos** e **4.260.424 palavras** (36 MB); `archive/` com 74 arquivos e 43K palavras; `raw/` vazio. Última modificação em `wiki/`: 2026-07-15.
- **Contra a premissa documentada:** `CLAUDE.md` afirma que busca lexical "funciona bem até ~100 artigos/400K palavras". O corpus está 28× acima em artigos e 10× acima em palavras. A premissa do produto não descreve mais o caso de uso real.
- **Contra as réguas do graphify:** o aviso de "abaixo de 50 mil palavras talvez nem valha grafo" não se aplica; o aviso de "acima de 500 mil palavras ou 500 arquivos a extração semântica fica cara" se aplica com folga de 8×.
- **Contra a escala do Hikari:** 47 nós lá contra 2.781 aqui (59×). Gates de curadoria manuais por evento de julgamento não portam sem automação.
- Existe um segundo diretório com a mesma estrutura (`~/dev/personal/LLM-knowledge-base`) contendo 1 arquivo — vault de teste ou legado, não o corpus real.

## Critérios acordados

- **Ordenação do backlog: por valor**, não por custo nem por retorno. Objetivo declarado do kb é valor da adição e utilidade.
- **Teto de ambição: aberto**, inclusive a itens que mudem a premissa "markdown é a única fonte da verdade" (ex.: índice ou store autoritativo). Os três repos recusam isso, mas o backlog registra a opção.
- **Multi-vault (feature 010) ignorado por ora** — portes avaliados contra o kb como ele é hoje, vault único.
- **MCP** permanece candidato vivo no backlog, não descartado.

## Not yet specified

<!-- fog of war — vazia: o caminho ao destination está percorrido -->

Toda a névoa graduou ou foi respondida:

- ~~Como o kb absorveria grafo materializado~~ → respondido: arquivo autoritativo, camada derivada descartável. Vira V2 do backlog.
- ~~MCP substitui, complementa ou concorre com `kb qa`~~ → respondido: complementa. `kb qa` responde como aplicação; MCP serviria como ferramenta, com o kb já tendo as quatro capacidades correspondentes. Vira V9.
- ~~Unidade de porte~~ → respondido: Hikari dá convenção e gates, graphify dá mecanismo, rowboat dá política de vigência. Nenhum dá código portável direto.
- ~~Ordenação do backlog~~ → decidido: valor.
- ~~Escala real do corpus~~ → medido: 2.781 artigos, 4.26M palavras.

## Out of scope

- **Decidir se o kb terá UI própria.** O usuário suspeita que sim (lente frontend do rowboat), mas isso é decisão de direção de produto, não dossiê. Este map levanta a evidência; a decisão é esforço separado.
- Implementar qualquer porte identificado.
- Ingerir o conteúdo das notas do Hikari no vault pessoal — operação de corpus, não de engenharia.
