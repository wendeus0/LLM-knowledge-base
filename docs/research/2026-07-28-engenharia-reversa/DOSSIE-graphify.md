# Dossiê — graphify

## Identificação (commit lido, tamanho, licença, stack)

- Commit inspecionado: `0b2bd938c4a48e91d27f0ba09b96409e0a36c78a`; tamanho do checkout no momento da leitura: 19 MiB. O pacote se chama `graphifyy`, requer Python >=3.10, declara licença Apache-2.0 e usa NetworkX, RapidFuzz e tree-sitter como dependências-base. [pyproject.toml:5](pyproject.toml#L5) [pyproject.toml:10](pyproject.toml#L10) [pyproject.toml:14](pyproject.toml#L44)
- O desenho declarado é um pipeline de funções que trocam `dict`s e grafos NetworkX: `detect → extract → build_graph → cluster → analyze → report → export`; os artefatos ficam em `graphify-out/`. [ARCHITECTURE.md:5](ARCHITECTURE.md#L5) [ARCHITECTURE.md:11](ARCHITECTURE.md#L11)

## Mapa de módulos

| Caminho | Responsabilidade | Evidência |
|---|---|---|
| `graphify/detect.py` | Classifica e enumera o corpus, converte Office e extrai texto de PDF. | [graphify/detect.py:490](graphify/detect.py#L490) [graphify/detect.py:527](graphify/detect.py#L527) |
| `graphify/extract.py` + `graphify/extractors/` | Extração estrutural local e resolução entre arquivos. | [graphify/extract.py:4503](graphify/extract.py#L4503) |
| `graphify/build.py` | Converte fragmentos em grafo NetworkX, deduplica e mescla atualizações. | [graphify/build.py:539](graphify/build.py#L539) [graphify/build.py:1019](graphify/build.py#L1019) |
| `graphify/export.py` | Serializa `graph.json`, hiperarcos e exportações derivadas. | [graphify/export.py:232](graphify/export.py#L232) |
| `graphify/cluster.py` | Particiona em comunidades Leiden/Louvain e cria rótulo estrutural. | [graphify/cluster.py:22](graphify/cluster.py#L22) [graphify/cluster.py:86](graphify/cluster.py#L86) |
| `graphify/serve.py` | Servidor MCP e recuperação lexical + travessia. | [graphify/serve.py:951](graphify/serve.py#L951) [graphify/serve.py:1192](graphify/serve.py#L1192) |
| `graphify/llm.py` | Passe semântico opcional, provedores e rotulagem opcional de comunidades. | [graphify/llm.py:450](graphify/llm.py#L450) [graphify/llm.py:1652](graphify/llm.py#L1652) |
| `tools/skillgen/` | Gera, de fragmentos, os artefatos de skill por plataforma. | [tools/skillgen/gen.py:1](tools/skillgen/gen.py#L1) [tools/skillgen/gen.py:423](tools/skillgen/gen.py#L423) |

## 1. Retrieval sem vetores

O caminho de consulta é `graph.json → NetworkX → texto de subgrafo`, não um índice vetorial. O CLI lê o JSON no formato node-link, guarda `_src/_tgt` para não perder a direção original durante a travessia não-direcionada e chama `_query_graph_text` em BFS (padrão) ou DFS; o CLI fixa profundidade 2, enquanto MCP aceita até 6. [graphify/cli.py:906](graphify/cli.py#L906) [graphify/cli.py:944](graphify/cli.py#L944) [graphify/serve.py:1334](graphify/serve.py#L1334) [graphify/serve.py:1339](graphify/serve.py#L1339)

### Da pergunta às sementes

1. A pergunta é dividida em tokens: pontuação é removida; há segmentação de chinês; palavras curtas em inglês e stopwords de pergunta em inglês, alemão, francês, espanhol, português e italiano são removidas, com fallback para os termos originais se todos forem removidos. [graphify/serve.py:84](graphify/serve.py#L84) [graphify/serve.py:165](graphify/serve.py#L165)
2. Para cada termo, o peso é `log(1 + N/(1+df))`, calculado sobre rótulos normalizados de todos os nós; termos raros recebem maior peso. O valor fica em cache no objeto do grafo. [graphify/serve.py:193](graphify/serve.py#L193)
3. A busca considera `label` normalizado, rótulo tokenizado, ID do nó e `source_file`. Um índice invertido de trigramas de caracteres é criado preguiçosamente; só é usado como pré-filtro quando seletivo, caso contrário ocorre varredura completa para preservar o resultado. [graphify/serve.py:225](graphify/serve.py#L225) [graphify/serve.py:248](graphify/serve.py#L248) [graphify/serve.py:272](graphify/serve.py#L272)
4. O ranking mistura: igualdade do rótulo (bônus 1000), prefixo (100), substring (1), trecho em caminho-fonte (0,5), todos multiplicados por IDF; igualdade/prefixo da pergunta inteira recebe multiplicador adicional 10. A contribuição de rótulo por termo é escalada pelo quadrado da cobertura dos termos da pergunta. Empates ficam por rótulo mais curto e ID. [graphify/serve.py:187](graphify/serve.py#L187) [graphify/serve.py:427](graphify/serve.py#L427) [graphify/serve.py:442](graphify/serve.py#L442) [graphify/serve.py:512](graphify/serve.py#L512)
5. Há no máximo três sementes do ranking enquanto a pontuação não cair abaixo de 20% da primeira; rótulos homônimos são deduplicados. Em paralelo, o melhor nó de cada termo é conservado, garantindo uma semente por termo que tenha qualquer acerto — uma defesa contra um identificador exato incidental apagar os outros termos. [graphify/serve.py:545](graphify/serve.py#L545) [graphify/serve.py:600](graphify/serve.py#L600) [graphify/serve.py:614](graphify/serve.py#L614)

### Expansão, filtros e montagem

- A pergunta pode inferir filtros de contexto como `call`, `import`, `field`, `parameter_type`, `return_type` e `generic_arg`; filtro explícito vence inferência. O filtro constrói um grafo com todos os nós, mas somente arestas cujo atributo `context` está na lista. [graphify/serve.py:637](graphify/serve.py#L637) [graphify/serve.py:701](graphify/serve.py#L701) [graphify/serve.py:723](graphify/serve.py#L723)
- BFS/DFS expande vizinhos até a profundidade pedida. Nós no percentil 99 de grau (piso 50) não são usados como trânsito, exceto se forem semente: limita a explosão por hubs. [graphify/serve.py:740](graphify/serve.py#L740) [graphify/serve.py:770](graphify/serve.py#L770)
- A resposta é um subgrafo textual: sementes primeiro; os demais por distância das sementes, grau decrescente e ID. Cada linha de nó traz fonte, linha e comunidade; cada aresta traz relação, confiança, contexto e a linha onde a relação ocorre. O limite é aproximadamente `token_budget * 3` caracteres e anuncia explicitamente truncamento. [graphify/serve.py:796](graphify/serve.py#L796) [graphify/serve.py:809](graphify/serve.py#L809) [graphify/serve.py:859](graphify/serve.py#L859) [graphify/serve.py:895](graphify/serve.py#L895)
- Se nenhum nó recebe pontuação positiva, retorna literalmente `No matching nodes found.`; portanto não há fallback semântico nem geração de resposta. [graphify/serve.py:951](graphify/serve.py#L951) [graphify/serve.py:967](graphify/serve.py#L967)

Outras operações expostas: `get_node`, vizinhança direta (com filtro de relação), comunidade, nós de maior grau e caminho mínimo entre dois endpoints lexicamente resolvidos. O caminho mínimo é calculado em cópia não-direcionada, ordenada para desempate determinístico, e exibe as relações realmente armazenadas. [graphify/serve.py:1215](graphify/serve.py#L1215) [graphify/serve.py:1380](graphify/serve.py#L1380) [graphify/cli.py:1240](graphify/cli.py#L1240)

## 2. Modelo do grafo

Um nó possui, no mínimo, `id`, `label`, `file_type`, `source_file` e `source_location`; uma aresta possui `source`, `target`, `relation`, `confidence`, fonte, linha e peso. A documentação define `EXTRACTED`, `INFERRED` e `AMBIGUOUS`; a serialização preenche `confidence_score` padrão de 1,0, 0,5 e 0,2 respectivamente. [ARCHITECTURE.md:33](ARCHITECTURE.md#L33) [ARCHITECTURE.md:50](ARCHITECTURE.md#L50) [graphify/export.py:301](graphify/export.py#L301)

As relações não são uma enumeração fechada centralizada: extratores emitem, entre outras, `contains`, `calls`, `imports`, `imports_from`, `inherits`, `implements`, `references`, `method`, `re_exports`, `uses`, além das relações semânticas. O contrato semântico do próprio `extract.py` lista `inherits`, `implements`, `mixes_in`, `embeds`, `references`, `calls`, `imports`, `imports_from`, `re_exports`, `contains` e `method`. [graphify/extract.py:259](graphify/extract.py#L259) [graphify/llm.py:477](graphify/llm.py#L477)

`build_from_json` produz `Graph` por padrão ou `DiGraph` quando solicitado; `build()` agrega fragmentos e passa por `deduplicate_entities`. A exportação usa NetworkX node-link JSON, adiciona `community`, `community_name`, `norm_label`, hiperarcos no metadado e `built_at_commit`; a escrita é atômica. [graphify/build.py:539](graphify/build.py#L539) [graphify/build.py:1019](graphify/build.py#L1019) [graphify/export.py:289](graphify/export.py#L289) [graphify/export.py:314](graphify/export.py#L314) [graphify/export.py:318](graphify/export.py#L318)

O rebuild completo recompõe a partir das extrações. No incremental, `merge_raw_extraction` preserva contribuições de fontes inalteradas, substitui tudo de fontes reextraídas e poda fontes removidas/excluídas; `build_merge` também preserva hiperarcos de fontes não tocadas. Há guarda contra encolher silenciosamente o grafo e contra sobrescrever JSON ilegível. [graphify/build.py:1162](graphify/build.py#L1162) [graphify/build.py:1174](graphify/build.py#L1174) [graphify/build.py:1376](graphify/build.py#L1376) [graphify/export.py:232](graphify/export.py#L232)

Comunidades são uma camada derivada: Leiden com seed 42 quando `graspologic` existe, Louvain com seed 42 como fallback; comunidades grandes ou pouco coesas recebem nova partição. Sem backend, o rótulo da comunidade é o nó de maior grau. [graphify/cluster.py:22](graphify/cluster.py#L22) [graphify/cluster.py:70](graphify/cluster.py#L70) [graphify/cluster.py:134](graphify/cluster.py#L134) [graphify/cluster.py:86](graphify/cluster.py#L86)

## 3. Extração determinística

O passe AST tem duas fases: primeiro extrai por arquivo classes, funções e imports; depois resolve imports entre arquivos para formar arestas de nível de símbolo `INFERRED`. O código declara explicitamente paralelismo por `ProcessPoolExecutor` para volume suficiente de arquivos não cacheados. [graphify/extract.py:4503](graphify/extract.py#L4503) [graphify/extract.py:4511](graphify/extract.py#L4511) [graphify/extract.py:4528](graphify/extract.py#L4528)

O núcleo genérico instancia `tree_sitter.Language` e `Parser`, percorre a árvore e especializa resolução de declarações, tipos e chamadas por linguagem. As dependências incluem gramáticas para Python, JS/TS, Go, Rust, Java/Groovy, C/C++, Ruby, C#, Kotlin, Scala, PHP, Swift, Lua, Zig, PowerShell, Elixir, Objective-C, Julia, Verilog, Fortran, Bash e JSON; SQL, Pascal, DreamMaker e HCL/Terraform são extras opcionais. [graphify/extractors/engine.py:2180](graphify/extractors/engine.py#L2180) [pyproject.toml:18](pyproject.toml#L18) [pyproject.toml:36](pyproject.toml#L36) [pyproject.toml:73](pyproject.toml#L73)

Além destas gramáticas, o dispatch cobre extratores específicos/heurísticos para Dart, Razor, Blade, Vue, Svelte, Astro, Apex, PowerShell, Bash, Pascal, formulários Delphi/Lazarus, XAML, soluções/projetos .NET, manifests, MCP config e JSON. A lista de extensões suportadas está em `CODE_EXTENSIONS`; ela inclui SQL e infraestrutura, mas extensão suportada não implica que todo formato use tree-sitter. [graphify/detect.py:31](graphify/detect.py#L31) [graphify/extract.py:4248](graphify/extract.py#L4248)

### Explicabilidade e casos difíceis

A promessa “every edge explained” é sustentada, para arestas persistidas, pelo registro de `relation`, `confidence`, `source_file` e `source_location`; a renderização de consulta mostra a linha do sítio da relação, não a linha de definição. [README.md:27](README.md#L27) [ARCHITECTURE.md:39](ARCHITECTURE.md#L39) [graphify/serve.py:879](graphify/serve.py#L879)

Isto não significa que toda relação seja certeza: `EXTRACTED` denota sintaxe/fonte explícita, enquanto a segunda passada e resolução de símbolos produzem `INFERRED`; o próprio esquema admite `AMBIGUOUS`. Os testes dedicados a `getattr`/dispatch indireto, resolução de símbolo e chamadas de membro mostram que esses casos recebem tratamento específico, mas o dossiê não executou os testes e não afirma sua cobertura empírica. [ARCHITECTURE.md:50](ARCHITECTURE.md#L50) [graphify/extract.py:4513](graphify/extract.py#L4513) [tests/test_indirect_dispatch_getattr.py:1](tests/test_indirect_dispatch_getattr.py#L1) [tests/test_symbol_resolution.py:1](tests/test_symbol_resolution.py#L1)

Em especial, resolução de nomes é conservadora em colisões: o código evita repontar aliases ambíguos de imports Python e deixa o alvo pendente em vez de fabricar uma aresta. [graphify/extract.py:187](graphify/extract.py#L187) [graphify/extract.py:237](graphify/extract.py#L237)

### SQL

`.sql` é classificado como código e `extract_sql` usa `tree_sitter_sql` opcional. Ele gera nós para arquivo, tabelas, views, funções, procedimentos e triggers; conecta arquivo por `contains` e cria `references` para foreign keys, referências `FROM`/`JOIN` e parte de `ALTER TABLE`, com fallback regex apenas quando um erro de parsing impede constraints. [graphify/detect.py:31](graphify/detect.py#L31) [graphify/extractors/sql.py:10](graphify/extractors/sql.py#L10) [graphify/extractors/sql.py:68](graphify/extractors/sql.py#L68) [graphify/extractors/sql.py:111](graphify/extractors/sql.py#L111)

## 4. Corpus não-código (prosa, PDF, SQL)

O detector separa `CODE`, `DOCUMENT`, `PAPER`, `IMAGE` e `VIDEO`. Markdown/MDX/QMD/SKILL/TXT/RST/HTML/YAML são `DOCUMENT`; PDF é `PAPER`; `.docx` e `.xlsx` são convertidos para Markdown em `graphify-out/converted/` antes de entrarem como documento. [graphify/detect.py:31](graphify/detect.py#L31) [graphify/detect.py:490](graphify/detect.py#L490) [graphify/detect.py:527](graphify/detect.py#L527) [graphify/detect.py:1376](graphify/detect.py#L1376)

Há um extrator estrutural de Markdown, sem tree-sitter: cria nó para arquivo e cada heading, `contains` de arquivo/heading-pai para heading-filho e `references` para links locais Markdown, reference-style e wikilinks. Ele ignora URLs externas, âncoras e código cercado. [graphify/extractors/markdown.py:53](graphify/extractors/markdown.py#L53) [graphify/extractors/markdown.py:161](graphify/extractors/markdown.py#L161) [graphify/extractors/markdown.py:172](graphify/extractors/markdown.py#L172)

Mas no fluxo de CLI mostrado, documentos, papers e imagens são encaminhados ao passe semântico, enquanto somente `code_files` vai ao AST. Assim, a prosa não recebe análise sintática comparável a símbolos/chamadas: sua estrutura determinística é limitada a headings/links quando `extract_markdown` é invocado, e sua extração conceitual rica é LLM-dependente. [graphify/cli.py:3026](graphify/cli.py#L3026) [graphify/cli.py:3048](graphify/cli.py#L3048) [graphify/extractors/markdown.py:77](graphify/extractors/markdown.py#L77)

PDF é lido por `pypdf`, página a página, sob limite de tamanho; falha ou PDF escaneado sem camada textual resulta em string vazia. A função semântica encaminha especificamente `.pdf` para esse leitor. [graphify/detect.py:527](graphify/detect.py#L527) [graphify/llm.py:497](graphify/llm.py#L497)

## 5. Onde o LLM entra

O LLM é opcional e não está no retrieval. Ele é chamado para extrair nós/arestas/hiperarcos de documentos, papers e imagens, depois que o AST já processou código; a CLI mistura ambos os resultados. O backend precisa ser configurado, e pode ser OpenAI-compatível, Claude, Bedrock/Azure etc.; o teste citado pelo pedido verifica especificamente overrides de endpoint OpenAI-compatível. [graphify/llm.py:1652](graphify/llm.py#L1652) [graphify/cli.py:3048](graphify/cli.py#L3048) [graphify/cli.py:3250](graphify/cli.py#L3250) [tests/test_openai_custom_endpoint.py:1](tests/test_openai_custom_endpoint.py#L1)

O prompt exige JSON, tipos de nó, relações, confiança e no máximo três hiperarcos por chunk. Em `deep_mode`, admite mais relações inferidas; logo essas relações não são determinísticas. [graphify/llm.py:450](graphify/llm.py#L450) [graphify/llm.py:475](graphify/llm.py#L475) [graphify/llm.py:481](graphify/llm.py#L481)

Há duas salvaguardas observáveis: conteúdo é encapsulado como dado não confiável e sentinelas de prompt injection são neutralizados; símbolos do tipo `code` inventados pelo modelo, sem identificador textual no arquivo enviado, recebem `verification: "unverified"` em vez de ser removidos. [graphify/llm.py:522](graphify/llm.py#L522) [graphify/llm.py:548](graphify/llm.py#L548) [graphify/llm.py:654](graphify/llm.py#L654)

Um segundo uso opcional do LLM é nomear comunidades. Na ausência/falha de backend, o sistema devolve `Community N`; há também rótulo local determinístico pelo hub de maior grau. [graphify/llm.py:3027](graphify/llm.py#L3027) [graphify/cluster.py:86](graphify/cluster.py#L86)

## 6. Escala e limites

Os números publicados: LOCOMO (n=300) dá recall@10 0,497 e QA 45,3%; LongMemEval-S (n=50) dá QA 76%; em ERPNext (~1M LOC), a medição diz 82,0% de cobertura versus 70,8% de grep/read, a ~140k tokens por consulta. São alegações do repositório, não resultados reproduzidos neste dossiê. [BENCHMARKS.md:28](BENCHMARKS.md#L28) [BENCHMARKS.md:142](BENCHMARKS.md#L142)

Para histórico temporal de ERPNext, informa 689 checkpoints AST, de 3.069 nós/2.900 arestas/1.032 arquivos em 2011 a 22.620/48.710/3.758 em 2026. [BENCHMARKS.md:151](BENCHMARKS.md#L151)

Limites operacionais codificados: abaixo de 50 mil palavras o detector avisa que talvez não seja necessário grafo; acima de 500 mil palavras ou 500 arquivos avisa que a extração semântica será cara e sugere subpasta. No retrieval, uma consulta sem match não tem recuperação; expansão de hubs é bloqueada; e a saída é cortada por orçamento. [graphify/detect.py:38](graphify/detect.py#L38) [graphify/detect.py:1400](graphify/detect.py#L1400) [graphify/serve.py:740](graphify/serve.py#L740) [graphify/serve.py:967](graphify/serve.py#L967)

O benchmark afirma construção AST sem créditos de LLM e cerca de 40 linguagens, mas o próprio fluxo torna isso uma afirmação de modo: corpus com documentos/PDF/imagens, se submetido ao passe semântico, consome tokens e pode ser caro. [BENCHMARKS.md:164](BENCHMARKS.md#L164) [graphify/cli.py:3095](graphify/cli.py#L3095)

## 7. Entrega como skill

`tools/skillgen` é ferramenta de build, não código embarcado. Fragmentos são a fonte de verdade; `graphify/skill*.md` e `graphify/skills/<platform>/references/` são artefatos gerados, versionados e verificados contra drift. A renderização é determinística: ordem fixa de slots, referências ordenadas e sem timestamp. [tools/skillgen/gen.py:1](tools/skillgen/gen.py#L1) [tools/skillgen/gen.py:20](tools/skillgen/gen.py#L20)

Para uma plataforma “split”, gera um `SKILL.md` enxuto e referências on-demand; plataformas monolíticas recebem um corpo único. O core recebe frontmatter, instruções de instalação, estratégia de dispatch, stub de query, alvo de hooks e extras por substituição de slots. [tools/skillgen/gen.py:360](tools/skillgen/gen.py#L360) [tools/skillgen/gen.py:423](tools/skillgen/gen.py#L423)

O manifesto de plataformas define destinos para Claude, Codex, Cursor, Gemini, OpenCode e outros; o README lista os comandos de instalação e explicita `graphify install --platform codex` e `--platform agents` para o formato cross-framework. O instalador copia também o diretório de referências. [tools/skillgen/platforms.toml:1](tools/skillgen/platforms.toml#L1) [README.md:206](README.md#L206) [README.md:224](README.md#L224) [graphify/install.py:122](graphify/install.py#L122) [graphify/install.py:175](graphify/install.py#L175)

## Decisões de design identificadas

| Decisão | Evidência | Trade-off aparente |
|---|---|---|
| Recuperar por léxico + grafo, não vetor | [graphify/serve.py:193](graphify/serve.py#L193) [graphify/serve.py:951](graphify/serve.py#L951) | Explicável e local na consulta; depende de termos que acertem rótulos/IDs/caminhos. |
| Expandir somente contexto local e bloquear hubs | [graphify/serve.py:740](graphify/serve.py#L740) | Contém ruído/explosão; pode ocultar um caminho legítimo via hub. |
| Preservar proveniência da relação até o texto final | [graphify/export.py:305](graphify/export.py#L305) [graphify/serve.py:879](graphify/serve.py#L879) | A resposta é auditável por linha; requer que extrator tenha capturado a localização. |
| AST local para código; LLM só para conteúdo | [graphify/llm.py:599](graphify/llm.py#L599) [graphify/cli.py:3026](graphify/cli.py#L3026) | Código é repetível/sem API; prosa rica fica dependente de modelo e custo. |
| Cache e merge incremental por fonte | [graphify/build.py:1162](graphify/build.py#L1162) [graphify/cli.py:3065](graphify/cli.py#L3065) | Evita recomputar; aumenta a complexidade de remoção, cache e consistência. |
| Grafo como JSON portátil, com comunidades derivadas | [graphify/export.py:289](graphify/export.py#L289) [graphify/cluster.py:134](graphify/cluster.py#L134) | Simples de inspecionar/servir; NetworkX em memória não é um banco de grafos remoto. |

## UNVERIFIED

- Não executei CLI, testes, parsing, benchmark ou qualquer chamada de rede; desempenho, recall, custo e comportamento prático são apenas os números/intenções publicados no repositório.
- `graphify-out/GRAPH_REPORT.md` não existe neste clone no momento da leitura, apesar da instrução local mencioná-lo; por isso não há achados de comunidades/god nodes desta instância.
- Não confirmei, por execução, quais combinações de gramáticas opcionais estavam instaladas nem a precisão dos casos `getattr`, dispatch indireto e resolução de símbolo; a descrição limita-se ao código e aos testes estáticos citados.
