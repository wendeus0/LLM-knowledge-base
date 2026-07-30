# Dossiê — Hikari-knowledge

## Identificação (commit lido, tamanho, licença, stack)

Commit lido: `3a6784403a4006188b03b5aee3aa0e503c6bc3ec` (obtido com `git rev-parse HEAD`). A medição estática deste checkout totalizou 228.990 bytes de arquivos rastreados (`git ls-files | wc -c`); portanto, este é o tamanho do conteúdo rastreado nesta revisão, não uma estimativa de distribuição compactada. A licença é MIT e identifica copyright de Hikari em 2026. `LICENSE:1-13`.

O núcleo é um corpus Markdown/YAML em `nodes/`, acompanhado por ferramentas Python sem dependência obrigatória para gerar e verificar o grafo; o adaptador MCP é Python 3.10+ e declara `mcp` e `PyYAML` como dependências. `tools/build_graph.py:1-24`, `mcp/pyproject.toml:1-10`. O vetor é uma capacidade opcional que usa LanceDB e FastEmbed quando esse ambiente e tabela existem; esses pacotes não pertencem às dependências declaradas do adaptador MCP. `mcp/kg_vector_query.py:35-40`, `mcp/pyproject.toml:1-8`.

O repositório se apresenta como corpus em inglês de resultados medidos, relatos condicionados e tombstones para sistemas de LLM local; não como espelho de vault privado. `README.md:1-10`, `AGENTS.md:1-13`.

## Mapa de módulos (tabela: caminho → responsabilidade → evidência)

| Caminho | Responsabilidade | Evidência |
|---|---|---|
| `nodes/**/*.md` | Fonte das notas; cada arquivo contém frontmatter e corpo, e os clusters se organizam por pasta. | `docs/CONVENTIONS.md:7-20`, `docs/CONVENTIONS.md:43-51` |
| `INDEX.md` | Mapa humano curado, agrupado por cluster, com título e resumo de cada nó. | `INDEX.md:1-5`, `INDEX.md:7-70` |
| `graph.json` | Artefato serializado com contagens, metadados dos nós e lista de arestas. | `graph.json:1-5`, `graph.json:1213-1228` |
| `tools/build_graph.py` | Lê todas as notas, valida ids/links e, sem `--check`, reescreve `graph.json`. | `tools/build_graph.py:54-93`, `tools/build_graph.py:96-143` |
| `tools/obsidianize.py` | Deriva a propriedade Obsidian `related:` a partir de `links:`. | `tools/obsidianize.py:1-11`, `tools/obsidianize.py:41-59` |
| `tools/sync_vault.sh` | Executa, em sequência, a geração de `related:` e de `graph.json`; opcionalmente repete a checagem. | `tools/sync_vault.sh:1-11` |
| `mcp/server.py` | Adaptador FastMCP local por stdio, com quatro ferramentas. | `mcp/server.py:1-27`, `mcp/server.py:30-90` |
| `mcp/kg_core.py` | Leitura tolerante a escrita parcial, busca lexical/híbrida, leitura de nó, vizinhança e fallback de índice. | `mcp/kg_core.py:117-228`, `mcp/kg_core.py:255-380`, `mcp/kg_core.py:383-512` |
| `mcp/kg_vector_query.py` | Consulta semântica opcional à tabela LanceDB `knowledge_graph`. | `mcp/kg_vector_query.py:1-13`, `mcp/kg_vector_query.py:21-75` |
| `skills/hikari-knowledge/` | Procedimentos para instalar, ler e atualizar um checkout consumidor. | `skills/hikari-knowledge/SKILL.md:59-168` |
| `skills/hikari-knowledge-curate/` | Gates e procedimento para curar, criar, fundir e tombstonar nós. | `skills/hikari-knowledge-curate/SKILL.md:32-112`, `skills/hikari-knowledge-curate/SKILL.md:265-300` |
| `docs/` e `prompts/` | Contrato editorial, decisões, manual operacional e procedimento de integração Obsidian. | `docs/CONVENTIONS.md:1-58`, `docs/AGENT_GUIDE.md:1-93`, `prompts/obsidian-merge.md:28-100` |

## 1. Método de curadoria

### Unidade editorial e esquema

Uma nota é um arquivo Markdown em `nodes/<cluster>/<id>.md`; o `id` deve ser kebab-case, igual ao stem do arquivo e globalmente único. O esquema definido traz `type`, `title`, `status`, `verified`, `confidence`, `tags`, `sources` e `links`. `docs/CONVENTIONS.md:7-20`. As categorias de `type` são `methodology`, `technique`, `result`, `tombstone` e `paper`; os estados enumerados são `active`, `resolved` e `tombstone`; a confiança é `measured`, `reported` ou `mixed`. `docs/CONVENTIONS.md:8-20`.

O código preserva esses campos no nó serializado, além de derivar `path`, `cluster` e aceitar `superseded_by`; isto explica a presença de um campo de supersessão mesmo ele não constando no esquema mínimo de convenções. `tools/build_graph.py:68-92`. O skill de curadoria explicita `superseded_by: canonical-id` como campo opcional para um tombstone criado por fusão ou reversão. `skills/hikari-knowledge-curate/SKILL.md:115-133`.

Os campos têm estes papéis operacionais observáveis:

- `id` é a chave de arquivo, de links e de busca; divergência entre id e stem é registrada como problema. `tools/build_graph.py:68-73`.
- `type` e `status` classificam a natureza e a vigência; o fluxo de leitura manda preferir `active`/`resolved` e mostrar tombstones quando eles evitam caminhos mortos. `AGENTS.md:34-40`, `skills/hikari-knowledge/SKILL.md:115-134`.
- `verified` registra uma data por nó, mas a semântica exata da verificação não é formalmente definida no material lido. A presença está no esquema e em notas reais. `docs/CONVENTIONS.md:13-20`, `nodes/serving/dsv4-mtp-sm120.md:2-12`.
- `confidence` separa evidência `measured`, `reported` ou `mixed`; para adotar `measured`, o gate exige que o corpo traga `n` e condições. `skills/hikari-knowledge-curate/SKILL.md:69-76`.
- `tags` alimenta a busca lexical; `sources` contém apenas URLs públicas quando é preenchido; `links` é a lista canônica de relações entre ids. `docs/CONVENTIONS.md:15-20`, `mcp/kg_core.py:255-304`, `tools/obsidianize.py:1-7`.
- `related` é uma projeção para Obsidian, não uma relação editorial independente: é regenerada de `links:` como strings `[[id]]`. `tools/obsidianize.py:41-59`.

O corpo recomendado tem as seções `What`, `Key numbers (with conditions)`, `Mechanism`, `Gotchas`, `Current state` e `Verification notes`. `docs/CONVENTIONS.md:23-29`. A amostra `dsv4-mtp-sm120` usa o esquema completo, declara `confidence: mixed`, contém condições explícitas de hardware/configuração/amostragem nos números e separa mecanismo, limitações e notas de verificação. `nodes/serving/dsv4-mtp-sm120.md:1-42`. Uma ponte de paper, em contraste, é curta, usa `type: paper` e `confidence: reported`. `nodes/papers/paper-deepseek-v3-mtp.md:1-25`.

### O que significa “measured” neste corpus

O branding não afirma que todos os nós sejam uma medição nova: define o conjunto como “measured results + conditioned reports + dead-end tombstones”. `docs/DECISIONS.md:3-6`. O gate editorial exige condições para números medidos, que a confiança reflita a evidência, e proíbe misturar medido, relatado e hipótese na mesma afirmação. `skills/hikari-knowledge-curate/SKILL.md:69-76`, `docs/CONVENTIONS.md:31-41`.

Na prática, uma nota pode registrar simultaneamente um resultado medido e números somente relatados, marcando a confiança global como `mixed`: o tombstone de dynamic-K distingue explicitamente o teto “Measured” de taxas “Reported” e declara detalhes ausentes. `nodes/specdec/dspark-confidence-dynamic-k-dead.md:15-24`. Há também um tombstone com `confidence: measured` que mantém o resultado contaminado e o experimento corrigido para documentar a regra de avaliação, não para fazer uma alegação de desempenho atual. `nodes/training/val-oversample-split-leak.md:1-40`.

### Granularidade, entrada e defesas de qualidade

A granularidade desejada é uma nota que responda sozinha a uma pergunta futura de recuperação. O manual define “clean” como: cada nó responde uma pergunta isoladamente; quase-duplicatas são fundidas; tombstones são preservados; números carregam condições; fontes são públicas; e o índice espelha o corpus. `docs/AGENT_GUIDE.md:66-77`.

Antes de criar um id, o procedimento manda buscar por título/mecanismo, atualizar um nó que já responda à mesma pergunta, incorporar gotcha fino no hub, criar apenas para dangling intencional com ao menos duas entradas, e rejeitar diário, log datado ou número isolado sem condições. `skills/hikari-knowledge-curate/SKILL.md:32-42`. Um candidato só permanece se satisfizer pelo menos uma função: evitar relitigação, oferecer runbook, decompor mecanismo, fazer ponte entre notas, ou responder sozinho a uma pergunta futura. `skills/hikari-knowledge-curate/SKILL.md:59-67`.

O gatilho de entrada é um evento de julgamento — experimento terminado/gate PASS·FAIL, dead lever confirmado, mudança de método, dangling recorrente, hub antigo ou achado de sessão — e não crawling contínuo. `skills/hikari-knowledge-curate/SKILL.md:80-91`. `docs/DECISIONS.md` também formula a política como qualidade acima de contagem, permitindo criação quando chega um evento de julgamento real. `docs/DECISIONS.md:8-10`.

As barreiras são: recomposição em inglês, fontes públicas, números condicionados, coerência de confiança, exclusão de impressões privadas, merge-before-create e proibição de commit/push sem autorização. `skills/hikari-knowledge-curate/SKILL.md:69-76`. As convenções excluem caminhos privados, identidade, redes internas, UUIDs e dados de terceiros, e retêm hardware somente como condição experimental. `docs/CONVENTIONS.md:31-41`. Para material derrubado, a regra é tombstonar em vez de apagar; quando dois nós ativos têm o mesmo mecanismo, um é canônico e o outro pode apontar para ele por `superseded_by`. `skills/hikari-knowledge-curate/SKILL.md:44-55`.

O seed inicial reforça o filtro: é subconjunto curado de pesquisa privada, recomposto em inglês, e papers entram apenas se referenciados. `docs/SEED_v0.md:1-5`, `docs/SEED_v0.md:49-64`. O corpus declara que não é sincronizado automaticamente de experimentos locais nem lugar para diário, números únicos ou operações pessoais. `AGENTS.md:163-170`.

## 2. Grafo

### Nó, aresta e autoridade

Um nó de grafo é um arquivo Markdown sob `nodes/**/*.md`, identificado por `id`/stem. Ao carregar, o construtor inclui metadados do frontmatter, cluster derivado da pasta, o corpo e links coletados. `tools/build_graph.py:54-93`. O `graph.json` da revisão lida registra 47 nós e 157 arestas; cada nó serializado contém id, caminho, cluster, classificação, confiança, fontes, links e `superseded_by`. `graph.json:1-31`.

Há dois tipos de aresta implementados:

1. `link`, de cada id em `links:` e também de cada wikilink `[[id]]` encontrado no corpo que ainda não esteja em `links:`. `tools/build_graph.py:74-90`, `tools/build_graph.py:103-109`.
2. `superseded_by`, de um nó para seu sucessor quando o campo existe. `tools/build_graph.py:110-119`.

O artefato atual exemplifica uma aresta `link` com `from`, `to` e `kind`; nesta revisão, todos os campos `superseded_by` serializados são `null`, portanto não há exemplo material de aresta desse segundo tipo no JSON atual. `graph.json:1213-1228`, `graph.json:1-31`. O tipo existe no gerador e no traversal MCP, independentemente de estar instanciado agora. `tools/build_graph.py:110-119`, `mcp/kg_core.py:445-463`.

As notas são autoritativas, e `graph.json` é derivado. O docstring declara que o gerador reconstrói o arquivo a partir do frontmatter; `--check` apenas reporta problemas e, sem a flag, o código escreve o JSON na raiz. `tools/build_graph.py:1-9`, `tools/build_graph.py:96-143`. A implementação MCP torna a mesma decisão explícita: arquivos são a verdade, toda ferramenta relê `nodes/**/*.md` e não mantém snapshot de grafo. `mcp/server.py:4-14`.

### Sincronização, integridade e custo

`build_graph.py --check` detecta frontmatter ausente ou malformado, id/stem divergente, ids duplicados, destinos ausentes e incoerência de `superseded_by` com o status esperado; retorna código 1 se houver problemas de estrutura. `tools/build_graph.py:57-73`, `tools/build_graph.py:101-143`. Destinos ausentes são reportados como candidatos a nós futuros, não removidos. `tools/build_graph.py:103-129`.

Após uma edição, o protocolo manda: gerar `related:`, rodar a checagem, reconstruir `graph.json` e atualizar o blurb correspondente no índice. `AGENTS.md:122-139`. O procedimento de curadoria adiciona atualização do `CHANGELOG` e uma varredura adversarial à integração. `skills/hikari-knowledge-curate/SKILL.md:94-112`.

Quanto ao custo de rebuild, não há benchmark de tempo no repositório. Pela implementação, o trabalho é uma varredura ordenada de todos os `*.md` sob `nodes/`, leitura integral e parse de cada arquivo, seguida de iteração sobre os links de todos os nós; a memória final contém todos os metadados dos nós e todas as arestas. Isto é uma inferência estática de custo aproximadamente linear no conteúdo lido e no total de links, não uma medição de desempenho. `tools/build_graph.py:54-93`, `tools/build_graph.py:101-140`.

## 3. Acesso via MCP

O servidor é local, por stdio, e não hospedado pelo autor. `mcp/README.md:1-5`, `mcp/server.py:85-90`. A raiz é `KG_ROOT`, ou por padrão o pai de `mcp/`; o servidor instancia um `NodeStore` para essa raiz. `mcp/server.py:20-27`.

As ferramentas expostas, com as assinaturas declaradas, são:

| Ferramenta | Assinatura | Resultado/comportamento |
|---|---|---|
| `kg_search` | `kg_search(query: str, k: int = 8) -> dict` | Busca híbrida e retorna hits com id, título, caminho, cluster, status, tipo, tags, snippet, score e via de match. | `mcp/server.py:30-44`, `mcp/kg_core.py:339-380` |
| `kg_get` | `kg_get(id: str) -> str` | Retorna o Markdown bruto do nó; se não achar, oferece sugestão por título/caminho; prefixa avisos para `stale`/`dead`, `superseded_by` ou frontmatter inválido. | `mcp/server.py:47-57`, `mcp/kg_core.py:383-408` |
| `kg_neighbors` | `kg_neighbors(id: str, depth: int = 1) -> dict` | Percorre links e supersessões em ambos sentidos, limita a profundidade a 1–4 e relata dangling outbound. | `mcp/server.py:60-72`, `mcp/kg_core.py:411-489` |
| `kg_index` | `kg_index() -> str` | Lê `INDEX.md`; se ele faltar, gera listagem de clusters a partir de scan vivo. | `mcp/server.py:75-82`, `mcp/kg_core.py:492-512` |

O armazenamento relê os arquivos a cada request em termos de inventário; reutiliza apenas um cache por arquivo validado por `(mtime, size)`, reparsa arquivos alterados e remove entradas de arquivos apagados. Ele tolera um arquivo no meio de escrita tratando o texto inteiro como corpo se o frontmatter não fechar. `mcp/kg_core.py:117-124`, `mcp/kg_core.py:127-184`, `mcp/kg_core.py:186-216`. Assim, o caminho MCP não lê nem depende de `graph.json`. `mcp/server.py:4-14`, `mcp/kg_core.py:186-216`.

### Busca lexical, vetores e composição do resultado

A busca lexical é determinística para um conjunto de arquivos dado: normaliza para minúsculas, soma pesos fixos para correspondência de query/termos em id, título, tags e corpo, e desempata por id após ordenar por score decrescente. `mcp/kg_core.py:255-304`, `mcp/kg_core.py:339-373`. `kg_search` constrói snippets por primeira ocorrência ou resumo/primeiro parágrafo. `mcp/kg_core.py:88-114`, `mcp/kg_core.py:231-253`.

Vetores são reais no código, mas opcionais: `KG_VECTOR` vem desligado por padrão; antes de chamar o helper, o servidor exige diretório da tabela LanceDB, um interpretador auxiliar e o arquivo helper. `mcp/kg_core.py:61-69`, `mcp/kg_core.py:307-335`. O helper importa `lancedb` e `fastembed`, gera embedding com o modelo padrão `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` e faz busca de cosseno na tabela `knowledge_graph`. `mcp/kg_vector_query.py:21-24`, `mcp/kg_vector_query.py:35-75`.

Quando disponível, a lista vetorial recebe bônus de reciprocal-rank fusion `300/(10 + rank)`; a própria implementação declara que os pesos lexicais exatos (por exemplo, 1000 para id integral) devem prevalecer sobre o máximo bônus vetorial de aproximadamente 30. `mcp/kg_core.py:339-350`. O resultado explicita `matched_via` como `lexical`, `vector` ou `vector+lexical` e inclui a nota de estado do vetor. `mcp/kg_core.py:356-380`.

Não há código de geração por LLM nem montagem de resposta discursiva pelo MCP: a interface retorna rankings/snippets, Markdown bruto, subgrafo ou índice. Essa conclusão decorre das quatro funções registradas e de seus retornos. `mcp/server.py:30-82`, `mcp/kg_core.py:339-512`. O componente que depende de modelo é somente a criação do embedding no helper; a disponibilidade e o ranking vetorial também dependem da tabela LanceDB externa. `mcp/kg_vector_query.py:42-60`, `mcp/kg_core.py:312-335`. A parte lexical, parsing, obtenção do documento e travessia de arestas são operações Python sem modelo identificadas neste código. `mcp/kg_core.py:127-216`, `mcp/kg_core.py:255-304`, `mcp/kg_core.py:383-512`.

## 4. Tooling do corpus

`obsidianize.py` trata `links:` como origem canônica e `related:` como espelho para a propriedade Obsidian. Ele aceita listas YAML em formato flow ou block, remove qualquer `related:` existente, recria-o como JSON de wikilinks e só escreve se o texto resultante diferir. `tools/obsidianize.py:21-59`. Logo, para um mesmo conteúdo de `links:`, sua transformação é idempotente; o próprio docstring declara que pode ser regenerada repetidamente. `tools/obsidianize.py:1-11`.

O script oferece `--check`: neste modo percorre as notas e lista as que seriam atualizadas, sem gravar. `tools/obsidianize.py:55-70`. A nota de exemplo revela o resultado material: `links` são ids simples e `related` contém o mesmo conjunto como `[[id]]`. `nodes/serving/dsv4-mtp-sm120.md:9-13`. A razão declarada é que Obsidian 1.4+ reconhece esses valores de frontmatter em graph view/backlinks. `tools/obsidianize.py:1-7`.

`sync_vault.sh` é o invólucro operacional: muda para a raiz, executa `obsidianize.py`, executa o rebuild normal de `build_graph.py`, e, se chamado com `--check`, roda uma checagem adicional de grafo depois do rebuild. `tools/sync_vault.sh:1-11`. A idempotência do espelho `related:` é declarada e sustentada pela comparação antes de escrita; o `graph.json` é reserializado por `build_graph.py` quando não há `--check`, portanto a equivalência de bytes depende também da serialização da versão Python, embora a estrutura seja derivada dos mesmos inputs. `tools/obsidianize.py:54-59`, `tools/build_graph.py:131-141`.

## 5. Skills

O skill `hikari-knowledge` separa quatro papéis: instalação em grafo existente (Mode A), leitura/resposta (Mode B), pull (Mode C) e delegação de curadoria ao skill irmão (Mode D); Mode E descreve porting de fatos privados pelo autor. `skills/hikari-knowledge/SKILL.md:59-182`. Para leitura, a sequência é índice, busca, nó, vizinhos, com preferência por `active`/`resolved` e sinalização explícita de tombstones. `skills/hikari-knowledge/SKILL.md:115-134`.

Para update, o skill exige estado git conhecido, `pull --ff-only` e `build_graph.py --check`; diante de commits locais, instrui parar e perguntar, sem forçar rewrite. `skills/hikari-knowledge/SKILL.md:138-147`. Seu checklist de edição verifica língua, merge prévio, condições, fontes, varredura de fingerprints, grafo, índice/changelog, geração de `related:` e autorização para commit/push. `skills/hikari-knowledge/SKILL.md:185-195`.

O skill `hikari-knowledge-curate` é o contrato editorial mais restritivo. Ele classifica cada candidato em `UPDATE`, `MERGE+TOMBSTONE`, `CREATE` ou `DROP`, e só permite `CREATE` após os hard gates. `skills/hikari-knowledge-curate/SKILL.md:94-112`. Exige fontes primárias públicas ao buscar fatos novos, não aceita o corpo de um nó como única fonte de verdade para uma nova alegação medida e só permite links para ids existentes (ou papers adicionados na mesma mudança). `skills/hikari-knowledge-curate/SKILL.md:96-112`, `skills/hikari-knowledge-curate/SKILL.md:265-275`.

Há também um protocolo explícito de paralelização de curadoria: scouts só leem, writers têm ownership de um id/arquivo não sobreposto, e o parent integra grafo/índice/changelog/varredura; o próprio manual limita a largura útil a independência real, normalmente 2–6. `skills/hikari-knowledge-curate/SKILL.md:148-190`. O gate de parada é o checklist final: cada candidato decidido, dangling ausente ou listado, índice/changelog atualizados, artefatos gerados, sweep limpo e commit somente se autorizado. `skills/hikari-knowledge-curate/SKILL.md:279-300`.

## 6. Ciclo operacional (fim a fim: como uma nota nova entra e chega ao Obsidian)

1. **Surgimento e triagem.** Um evento de julgamento (por exemplo, experimento finalizado, dead lever ou mudança de método) vira candidato; diário e número único sem condições são descartados. `skills/hikari-knowledge-curate/SKILL.md:80-91`, `skills/hikari-knowledge-curate/SKILL.md:32-42`.
2. **Decisão editorial.** O mantenedor pesquisa hubs/quase-duplicatas e decide atualizar, fundir+tombstonar, criar ou descartar. A criação precisa cumprir ao menos um valor de adoção e todos os gates de fonte, condições, confiança e privacidade. `skills/hikari-knowledge-curate/SKILL.md:44-76`, `skills/hikari-knowledge-curate/SKILL.md:94-105`.
3. **Escrita da fonte.** A nota entra em um cluster com id global/filename correspondente, frontmatter do esquema e corpo estruturado em inglês; os links editoriais são ids em `links:`. `docs/CONVENTIONS.md:7-29`, `docs/CONVENTIONS.md:43-57`.
4. **Integração derivada.** `obsidianize.py` espelha `links:` para `related:`; a checagem do grafo encontra referências pendentes; o rebuild materializa `graph.json`; e `INDEX.md`/`CHANGELOG.md` recebem a atualização humana. `AGENTS.md:132-139`, `skills/hikari-knowledge-curate/SKILL.md:106-112`.
5. **Publicação/versionamento.** O workflow não faz commit ou push automaticamente: ambos requerem pedido explícito. `AGENTS.md:122-130`, `skills/hikari-knowledge-curate/SKILL.md:69-76`.
6. **Consumo em Obsidian.** O consumidor clona como subpasta `Hikari-knowledge/`, preserva ids e acrescenta bridges apenas em suas próprias notas; o `related:` gerado alimenta graph/backlinks do Obsidian. `docs/OBSIDIAN_MERGE.md:5-35`, `docs/OBSIDIAN_MERGE.md:66-79`, `docs/OBSIDIAN_MERGE.md:129-136`.
7. **Atualização do consumidor.** O ritual é verificar estado e fazer `git pull --ff-only`; o uso do MCP não requer migração porque ele relê arquivos como verdade. `docs/OBSIDIAN_MERGE.md:83-101`, `docs/AGENT_GUIDE.md:44-54`.

O `INDEX.md` é a porta de entrada humana desse ciclo: lista clusters e resumos, e no checkout lido declara 47 nós, 6 clusters e 4 tombstones. `INDEX.md:1-5`, `INDEX.md:7-70`. O `CHANGELOG` registra adições públicas e diz que a cadência é aproximadamente semanal, sem SLA rígido. `CHANGELOG.md:1-20`.

## Decisões de design identificadas (tabela: decisão → evidência → trade-off aparente)

| Decisão | Evidência | Trade-off aparente |
|---|---|---|
| Arquivos Markdown são a verdade; `graph.json` é projeção. | `tools/build_graph.py:1-9`, `tools/build_graph.py:131-141`, `mcp/server.py:4-14` | Facilita inspeção e edição direta, mas exige varrer/reprocessar notas para derivar o grafo. |
| O corpus é curado por evento de julgamento e merge-before-create. | `skills/hikari-knowledge-curate/SKILL.md:32-76`, `skills/hikari-knowledge-curate/SKILL.md:80-112` | Favorece recuperabilidade e densidade de mecanismo, ao custo de menor cobertura e de triagem humana. |
| Histórico derrubado permanece como tombstone. | `docs/CONVENTIONS.md:39-41`, `skills/hikari-knowledge-curate/SKILL.md:44-55` | Mantém antiexemplos e contexto de reversão, mas deixa conteúdo obsoleto navegável e requer sinalização de status. |
| `links:` é a relação canônica; `related:` é espelho Obsidian gerado. | `tools/obsidianize.py:1-11`, `tools/obsidianize.py:41-59` | Evita duas fontes editoriais para a mesma relação, mas acrescenta uma etapa de geração ao fluxo. |
| Busca lexical é base; vetor é bônus desligado por padrão. | `mcp/kg_core.py:61-69`, `mcp/kg_core.py:255-304`, `mcp/kg_core.py:339-380`, `mcp/README.md:21-22` | O caminho básico funciona sem ingestão/modelo externo, enquanto a semântica extra depende de tabela, ambiente e embedding. |
| MCP é local por stdio e autocontido no checkout. | `mcp/README.md:1-22`, `mcp/server.py:85-90` | Evita serviço hospedado e mantém os dados no clone, mas transfere instalação e operação ao consumidor. |
| Integração Obsidian preserva o upstream em subpasta e usa bridges unidirecionais do vault do usuário. | `docs/OBSIDIAN_MERGE.md:5-35`, `docs/OBSIDIAN_MERGE.md:66-79` | Mantém pulls simples e reduz colisões, mas não faz fusão semântica automática com notas privadas. |

## UNVERIFIED

- A semântica precisa de `verified` (por exemplo, se é data de medição, de revisão ou de publicação) não é definida explicitamente no material lido; só há o campo no esquema e nas amostras. `docs/CONVENTIONS.md:7-20`, `nodes/serving/dsv4-mtp-sm120.md:1-12`.
- Não há, neste checkout, implementação do pipeline que ingere/popula a tabela LanceDB `knowledge_graph`; o helper apenas declara manter-se em lockstep com `ingest/to_swarm_recall.py`. Portanto, a origem, atualização e esquema completo dessa tabela não foram verificados aqui. `mcp/kg_vector_query.py:1-13`.
- Não há medição de tempo, memória ou frequência real de rebuild; a caracterização de custo na seção de grafo é inferida da leitura estática, não um benchmark. `tools/build_graph.py:54-143`.
- A regra “fontes públicas somente” é verificável como restrição de formato, mas não comprova por si que cada URL pública sustente cada alegação, nem que toda nota tenha uma fonte primária pública para seus números. `docs/CONVENTIONS.md:31-41`, `skills/hikari-knowledge-curate/SKILL.md:69-76`, `nodes/specdec/dspark-confidence-dynamic-k-dead.md:40-42`.
