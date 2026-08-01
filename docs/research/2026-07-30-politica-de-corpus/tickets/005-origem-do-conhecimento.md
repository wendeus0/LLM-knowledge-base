# De onde vem o conhecimento novo?

Type: grilling
Status: resolved (2026-07-31)
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

**Livros e papers, curados por você. Sem web aberta, sem detecção automática de lacuna.** Decidido no grilling de 2026-07-31.

### Fonte admitida

**Livros e papers**, pelo caminho que já existe (`kb import-book` → `raw/books/` → compile). PDF de paper entra como livro. **Web aberta fica fora da rotina** — página só entra se você salvar e ingerir deliberadamente.

Isso preserva a virtude que o charting identificou: **o que atravessa a fronteira é escolhido por você**, e a curadoria fica no humano, no ponto em que é barata. O gate de conteúdo não-confiável do PR #54 continua valendo como defesa em profundidade, não como licença para abrir a porta.

**Destino do que já existe:**
- `discovery` fica, **só com a fonte arXiv** — paper é fonte legítima; Google News sai.
- `kb ingest <url>` continua existindo para uso deliberado seu, sem job automático.
- **Auto-commit segue desligado** (`KB_DISCOVERY_AUTOCOMMIT`), confirmando o default defensivo tomado durante a sessão em resposta ao F-02 da auditoria.

### Livro novo sobre tema que já existe

**Avisa que o tema ficou desatualizado.** Os capítulos entram em `_chapters/`, o artigo de tema ganha marca de stale, e você decide quando recompilar. Nada reescreve artigo que você já leu sem você mandar.

Depende do mesmo pré-requisito do [ticket 006](006-destino-dos-artigos-atuais.md): saber a que tema um capítulo novo pertence exige a ligação artigo → fonte que o `manifest.json` nunca materializou.

### Detecção de lacuna: **derrubada por medição**

A decisão inicial do grilling foi "limiar de score no retrieval". **Medi antes de fixar, e o score não separa acerto de erro.**

Golden de 152 casos, modo híbrido sem rerank (o limiar precisa valer no caminho barato, antes de gastar chamada de LLM), score do primeiro resultado:

| | n | mín | p25 | mediana | p75 | máx |
|---|---:|---:|---:|---:|---:|---:|
| **acertou** | 63 | 0,0367 | 0,0479 | 0,0532 | 0,0601 | 0,0641 |
| **errou** | 89 | 0,0361 | 0,0447 | 0,0502 | 0,0547 | 0,0636 |

As faixas se sobrepõem quase por inteiro: o erro de maior score (0,0636) empata com o melhor acerto (0,0641). Qualquer limiar paga caro:

| Limiar | Lacunas detectadas | Falso alarme (sabia e disse que não) |
|---:|---:|---:|
| 0,046 | 25 de 89 (28%) | 11 |
| 0,052 | 58 de 89 (65%) | **27** |
| 0,058 | 77 de 89 (87%) | **43** |

Para pegar dois terços das lacunas, o sistema diria "não sei" em 27 perguntas que sabia responder.

**A causa é estrutural, não falta de calibração.** O score é RRF — soma de inversos de posição. Ele mede **concordância entre canais**, não confiança na resposta: um artigo errado que os quatro canais concordam em rankear alto tira score alto. RRF não vira medida de confiança com ajuste de limiar; vira com outra métrica.

**Decisão: detectar lacuna automaticamente é pré-requisito medido, não parte desta política.** Exige uma medida de confiança que o retrieval atual não produz — provavelmente o grader de fidelidade pedido em `PENDING_LOG.md:119`. Fica como trabalho próprio, com esta medição como evidência de que o caminho barato foi tentado e não serve.

**Enquanto isso: você diz quando falta.** O kb não sugere leitura, então também não alucina bibliografia — o modo de falha do item 2 da pergunta deste ticket some junto.

### Consequências para as perguntas do ticket

- **Livros apenas, ou web/papers?** Livros e papers. Web fora da rotina.
- **Aquisição sob demanda ou curada em lote?** Curada por você. Não há aquisição automática na lacuna, porque não há detecção de lacuna.
- **Como se detecta lacuna?** Hoje, você. Automaticamente, só depois do grader.
- **O kb sugere referência sem verificar existência?** Não sugere referência nenhuma. A dívida de "referência bibliográfica real" permanece, mas para o artigo compilado (ticket 004), não para recomendação de leitura.
- **A dependência de LLM grande externa é aceitável?** Não entra. A propriedade offline do ADR-0017 fica preservada — consequência de derrubar a detecção automática, não decisão separada.

### Sobra em aberto

Se algum dia a detecção de lacuna voltar, vale medir dois sinais que esta rodada não testou e que podem separar onde o RRF não separa: **o cosseno do canal semântico puro** e **a margem entre 1º e 2º colocado**. É medição barata com o mesmo golden.

<!-- preencher na resolução -->
