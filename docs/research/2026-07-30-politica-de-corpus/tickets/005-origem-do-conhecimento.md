# De onde vem o conhecimento novo?

Type: grilling
Status: open
Blocked by: 004-wiki-produto-ou-insumo

## Question

O corpus continua derivado de livros que você escolhe, ou passa a admitir web, papers e docs? E quem dispara a aquisição — você ou o sistema?

O grilling de abertura já travou o comportamento desejado: quando o corpus não cobre o tema, o kb deve **ir buscar a fonte** e então responder, crescendo na direção do que você estuda. Este ticket decide a forma disso.

### A proposta em cima da mesa

Levantada pelo usuário durante o charting: o modelo local, ao detectar que não tem subsídio, consulta uma **LLM grande** (Codex ou Claude Code, já logados via CLI na estação) pedindo **referências** — não conteúdo. Ela devolve sugestões de livros; o usuário traz o livro ao vault; o `import-book` quebra em capítulos e o compile destila.

O desenho tem uma virtude que não é acidental: **o que atravessa a fronteira são ponteiros, não texto.** Uma página web ingerida é dado não-confiável carregando conteúdo arbitrário para dentro do prompt — a superfície de injeção que a regra 8 do AGENTS.md existe para tratar. Um título e um autor têm superfície minúscula, e o conteúdo que de fato entra no vault chega por um livro que o usuário escolheu e obteve. A curadoria fica no humano, no ponto em que ela é barata.

Casa também com o que já existe: `kb import-book` já quebra EPUB/PDF em capítulos dentro de `raw/books/`, e `--compile` já encadeia.

### Onde a proposta é frágil — e o que este ticket precisa resolver

**1. O gargalo não é sugerir; é saber que não sabe.** Hoje o `qa` não tem noção de insuficiência: o retrieval devolve o top-3 sempre, mesmo quando o melhor match tem score irrisório. Não existe limiar de confiança em lugar nenhum do código. Detectar lacuna exige um limiar calibrado, e calibrar exige o instrumento que não existe — o grader de fidelidade pedido em `PENDING_LOG.md:119`. Esta é a parte cara da ideia, e é anterior a ela.

**2. Sugerir bibliografia é onde LLM alucina mais.** Título plausível com autor plausível e ISBN inventado é modo de falha clássico. Se o kb passa a recomendar leitura, ele precisa de verificação de existência — e "referências bibliográficas **reais**" é exatamente o que `011/DOMAIN.md:11` definiu e nunca implementou. A ideia reabre aquela dívida.

**3. Qual modelo local faz esse julgamento.** `bonsai-27b-1bit` é o reranker em `:8081`, quantizado a 1 bit em 3,79 GB. Reordenar 20 candidatos e julgar "isto está fora do meu alcance" são tarefas de natureza diferente. Se o julgamento de insuficiência for feito por retrieval (score abaixo de limiar) em vez de por modelo, o problema fica determinístico e barato — mas precisa da calibração do item 1.

**4. A dependência externa entra na arquitetura.** Hoje o kb roda offline por decisão registrada no ADR-0017 (embeddings locais preservam a propriedade offline). Um caminho que consulta LLM grande via CLI quebra isso — talvez aceitavelmente, já que é opt-in e só na lacuna, mas a decisão precisa ser explícita e não implícita.

### Pontos a fechar

- Livros apenas, ou web/papers/docs também? Se web entrar, sob qual gate de untrusted-output?
- A aquisição é sob demanda (na lacuna) ou curada em lote (você decide o que estudar e alimenta antes)? As duas coisas coexistem?
- Como se detecta lacuna: limiar de score, julgamento de modelo, ou o usuário dizendo?
- O kb sugere referência sem verificar existência? Se não, quem verifica?
- A dependência de LLM grande externa é aceitável na arquitetura, e o que acontece quando ela não está disponível?

## Evidência para o grilling

> Compilada em 2026-07-31. Organiza o que a sessão mediu; não decide.

**A fronteira que este ticket discutia agora tem enforcement.** O charting notou que a proposta "pedir referências, não conteúdo" tem a virtude de fazer atravessar ponteiros em vez de texto. Desde então:

- **O caminho de conteúdo ganhou container** (PR #54): tudo que vem da fonte — corpo, nome de arquivo, título e autor de livro, título de capítulo — entra num delimitador com sentinela aleatória por chamada, e o system prompt proíbe obedecer ao que está lá dentro. Dois reviews adversariais (Codex GPT-5.6 e Opus de contexto fresco) tentaram furar com 15+ payloads; o que passou foi metadado fora do container, corrigido no mesmo ciclo. **Admitir a web deixou de ser a mesma decisão que era**: o vetor principal tem gate.
- **A cadeia desatendida foi desligada** (mesmo PR): o job `discovery` fazia web → LLM → wiki → **commit automático** a cada 6h. Agora o commit exige `KB_DISCOVERY_AUTOCOMMIT=1`. Foi um default defensivo tomado na sessão — **este ticket é quem decide se fica assim, se volta, ou se vira quarentena explícita (`raw/untrusted/`)**.
- **Ingestão de web mente menos** (PR #53): página JS-dinâmica que voltava vazia e reportava sucesso agora é recusada antes de escrever. Era o caso do GHDB, a base canônica de dorks, ingerida com zero dorks.

**O que continua sendo o gargalo real, e é anterior à proposta:** o `qa` não sabe que não sabe. Não existe limiar de confiança em lugar nenhum do código — o retrieval devolve o top-3 sempre, mesmo com o melhor match irrisório. Detectar lacuna exige calibração, e calibrar exige o grader de fidelidade que nunca foi construído. **Nenhuma variante desta proposta funciona sem resolver isso primeiro.**

**Sobre alucinação de bibliografia:** segue válido como risco. Nada mudou — `min_refs` continua não existindo em `kb/`, e 1.035 de 1.037 artigos não têm referência nenhuma.

**Restrição nova a considerar:** o ADR-0017 registra a propriedade offline (embeddings locais). Consultar LLM grande via CLI na lacuna quebra isso. Continua sendo decisão deste ticket — mas agora com um dado a mais: a infra local (`bonsai-27b-1bit` em `:8081`) voltou ao launchd e ressuscita sozinha, então o argumento "o local não é confiável o bastante" ficou mais fraco.

## Answer

<!-- preencher na resolução -->
