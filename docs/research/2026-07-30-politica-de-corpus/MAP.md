# Map — Política de corpus do kb

## Destination

Um ADR que trava o fundamento do corpus do kb: de onde vem o conhecimento novo, o que acontece com os artigos que já existem, se a wiki compilada é produto ou insumo, e qual superfície o usuário usa para ler. O map fecha quando essas decisões estão travadas com evidência — sem implementar nada. A execução vai para o `spec-pipeline`.

Este esforço gradua o que o map anterior deixou explicitamente em Out of scope ([Engenharia reversa](../2026-07-28-engenharia-reversa/MAP.md), linha 55): *"Decidir se o kb terá UI própria — decisão de direção de produto, não dossiê. Este map levanta a evidência; a decisão é esforço separado."*

## Notes

- **Domínio:** engine de knowledge base mantida por LLM (`kb`). Corpus real em `~/vault/wiki`: **1.037 artigos indexáveis** / 4,26M palavras. O número 2.781 que circula na documentação conta também `_summaries/` (1.022) e `_sources/` (712) — não são artigos.
- **Regra de casa deste diretório** (herdada do map anterior): toda afirmação estrutural carrega evidência `caminho:linha`. Afirmação sem evidência é marcada `UNVERIFIED` e não entra no ADR.
- **Skills a consultar:** `grill-with-docs` (há ADRs em conflito potencial — 0004 superado, 0013 com fases pendentes), `domain-model` (o `DOMAIN.md` do esforço vive neste diretório), `prototype` no ticket 007, `adr-manager` no fechamento.
- **Checkout canônico:** `~/dev/github.com/wendeus0/LLM-knowledge-base` está à frente, mas **não tem `.env`** — rodar `kb` daqui aponta `KB_DATA_DIR` para o próprio repo (`kb/config.py:10`), a falha silenciosa já registrada em `ERROR_LOG.md:30` e `memory/pitfalls.md:106`. O `.env` real está em `~/dev/personal/LLM-knowledge-base/.env` (`KB_DATA_DIR=/Users/wendeus/vault`).
- **Regra 8 do AGENTS.md** pesa neste map: se a política admitir fonte da web, todo conteúdo ingerido é dado não-confiável e a decisão precisa dizer como ele entra sem virar vetor de injeção.
- **O que motivou o esforço:** a pergunta "posso usar o kb para estudar Google Dorking agora?". A resposta imediata é não — o vault não tem uma linha sobre o assunto — e a investigação disso expôs que a questão real não é a ferramenta, é o fundamento do corpus.

## Decisions so far

- [Destination: a política, não a implementação](#) — o map produz decisões travadas em ADR; qualquer código sai daqui pelo `spec-pipeline`.
- [Produto esperado do kb](#) — `kb qa` redige o artigo na hora e arquiva em `outputs/` para leitura posterior. O alvo de qualidade é o output do QA, não a densidade do arquivo na wiki. (Grilling de abertura, 2026-07-30.)
- [Comportamento em lacuna de corpus](#) — quando o corpus não cobre o tema, o kb deve **ir buscar a fonte** e então responder, crescendo na direção do que o usuário estuda. Não abster-se; não completar com conhecimento paramétrico do modelo. (Grilling de abertura; a forma disso é o ticket 005.)
- [A interface entra no escopo](#) — "tela visual própria" deixa de ser out of scope e vira decisão de primeira classe deste map (ticket 007), revertendo a exclusão do map anterior.

## Fatos medidos

Levantados na sessão de charting (2026-07-30), sem trabalho novo de ticket.

**Retrieval — o que já foi consertado**

- `recall@5`: 0,230 lexical → 0,414 com canal semântico → **0,467** com rerank 20 a temp 0. MRR: 0,127 → 0,242 → **0,343**. Golden de 152 casos (50 curados + 102 gerados). `docs/adr/0017-hybrid-retrieval-with-measured-llm-rerank.md:25-31`.
- Teto de ordenação disponível: `recall@20` = **0,720** (`memory/project_state.md:30`).
- Negativos registrados para não retentar: chunking por seção (017), `--expand terms` (018), `granite4:tiny-h` como reranker (021/022, pior que não reordenar), **rerank restrito a top-N (2026-07-31: zerou índice alucinado e mesmo assim derrubou recall@5 de 0,526 para 0,493 — o modelo devolve menos do que se pede)**.
- **Baseline de retrieval atualizada em 2026-07-31:** `recall@5` 0,467 → **0,526** e MRR 0,343 → **0,352**, após corrigir a colisão de slug (PR #50) e o snippet vazio do candidato só-semântico (PR #51). São +9 acertos em 152.
- A premissa "busca genérica de fase inicial" descreve o estado **anterior** ao ADR-0017. O ADR-0004 (keyword simples) está superado.

**Corpus — o estado real**

- `~/vault` tem 465 MB: `library/` 185 MB (869 fontes, **fora do git** — `.gitignore` do vault exclui), `kb_state/` 141 MB, `topics/` 87 MB, `wiki/` 35 MB, `archive/` 440 KB.
- **`raw/` está vazio** — dois arquivos, ambos `.DS_Store`. `kb compile` tem zero alvos hoje. O `tracking.db` confirma: 111 execuções de `jobs run compile` entre 2026-07-15 e 2026-07-30 somando **6.951 ms**.
- `manifest.json`, `knowledge.json`, `claims.jsonl` e `audit.jsonl` são declarados em `kb/config.py:18-21` e usados por `kb/state.py`, mas **nunca foram materializados neste vault**. A proveniência raw→artigo está perdida.
- Consequência direta: `find_compiled_entry()` (`kb/state.py:87`) devolve `None` para tudo, então `_resolve_output_path` (`kb/compile.py:223-231`) escreveria em caminhos novos derivados de `slugify(title)`. **Um recompile hoje duplicaria a wiki em vez de atualizá-la.**
- Índice de embeddings: 1.037 artigos, 8.685 chunks, 141 MB, `nomic-embed-text-v2-moe`, dim 768, format 2. É a única parte do vault com invalidação incremental por hash (`kb/embeddings.py:71-107`).

**Compile — por que o artigo sai raso**

- Não é incremental: `discover_compile_targets()` (`kb/compile.py:205-211`) devolve todo arquivo de `raw/` sem filtrar já-compilado. O job agendado `0 9 * * *` (`kb/jobs.py:31-38`) recompilaria o corpus inteiro.
- Custo: **N a 2N chamadas LLM para N documentos**, com o documento completo no prompt, sem chunking e sem cache (`kb/compile.py:307,324`).
- O prompt (`kb/compile.py:35-46`) **não tem uma única instrução de profundidade, extensão ou densidade**. O único número no template é "2-4 frases" no Resumo (`kb/templates/article.md:11`). A regra anti-alucinação ("com fidelidade", "omita seções sem material") empurra para o resumitivo.
- `_validate_output` (`kb/compile.py:64-74`) checa apenas frontmatter parseável, `title`, `topic` e corpo não-vazio. **Um artigo de três frases passa.**
- `max_tokens` nunca é enviado ao modelo — `kb/client.py:87-102` repassa só `temperature` e `top_p` (`kb/sampling.py:10-11`).
- "Artigo robusto" foi definido em `features/_archived/011-corpus-noise-filter/DOMAIN.md:11` (mínimo de referências bibliográficas reais, gate fail-closed em 5, rastreabilidade por trecho) e **explicitamente adiado** na SPEC 011:63. Grep confirma: não existe `min_refs` em `kb/`.
- `heal` é proibido de melhorar conteúdo (`kb/heal.py:17-25`): artigo raso compilado uma vez permanece raso — nenhum comando do pipeline o aprofunda.
- `kb lint` audita **20 de 1.037** artigos e não avisa (`kb/lint.py:37-39`) — o V1 do backlog anterior, classificado valor crítico.

**Qualidade de resposta — o buraco**

- `kb bench` mede **ordenação de artigos**, não resposta. O grader de fidelidade foi pedido em `PENDING_LOG.md:119` e a feature entregue implementou só recall/MRR. Grep por `grader|fidelidade|faithfulness` não retorna nada em `kb/`.
- Os perfis `analytical`/`generative`/`diverse` (temp 0,2/0,6/0,9) foram escolhidos por julgamento, não medidos (`022/REPORT.md:52`).
- O default do `qa` é o perfil `fast`: `top_k=3`, artigos capados em 4.000 chars (`kb/config.py:85`). O cap de 4k corta a cauda de 40% dos artigos (`013/REPORT.md:31`) — declarado como risco a validar, e o bench nunca validou porque não mede resposta.
- Os perfis `paper` e `article` (`kb/config.py:87-88`) — este último com `top_k=5`, 8k chars e travessia — **não têm consumidor nenhum**. Foram feitos para módulos de autoria nunca construídos (`013/REPORT.md:30`).

**Cobertura do tema que motivou o esforço**

- Zero resultados para `dorking`, `google hacking`, `ghdb`, `inurl:`, `filetype:`, `osint`, `pentest`, `recon` em todo o `~/vault`.
- `~/vault/library/` cobre quatro áreas: `finance`, `llm`, `psychology`, `software-engineering`. Nenhuma fonte de segurança ofensiva.
- `wiki/cybersecurity/` tem 11 artigos, todos de segurança **defensiva** de aplicação, extraídos de livros de engenharia (OWASP Top 10, assinatura de requisições, menor privilégio).
- `cybersecurity` é topic default da taxonomia (`kb/config.py:26`) e ganha `topic_bonus` de 0,05 (`kb/claims.py:64`) — o topic está preparado e vazio desse tipo de conteúdo.

**Infraestrutura local**

- `:1234` (embed) — LM Studio, serve `text-embedding-nomic-embed-text-v2-moe`. Responde.
- `:8081` (rerank) — `llama-server` com `bonsai-27b-1bit` (26,9 B params, 3,79 GB, `n_ctx` 16384). Responde, **mas roda fora do launchd**: `com.wendeus.kb-rerank` tem `KeepAlive=true` e está sem PID com último exit code 1. Se o processo morrer, não há garantia de que volte.

## Not yet specified

<!-- fog of war: névoa em-escopo que ainda não dá para ticketar -->

- **Como medir que uma resposta do `qa` presta.** O grader de fidelidade nunca entregue (`PENDING_LOG.md:119`). Não dá para ticketar antes de 004 definir o que "prestar" significa — o critério de um insumo é diferente do critério de um produto.
- **Se a definição de artigo robusto de `011/DOMAIN.md:11` sobrevive.** Min-refs 5 e rastreabilidade por trecho foram desenhados para um produto que talvez não seja o que se decidir.
- **Se material de segurança ofensiva exige política de guardrail própria.** O ticket 002 vai expor: `guardrails.py` aborta em padrões `api_key`/`token`/`password`, e um artigo de dorking com `intext:"api_key"` provavelmente dispara falso positivo (pitfall P9).
- **Qual dos dois checkouts é canônico e como reconciliar.** `github.com/wendeus0/` está à frente mas sem `.env`; `personal/` tem `.env` e `.venv` mas está atrás (`ERROR_LOG.md` 15.875 B vs 18.537 B).
- **Se a política reordena os itens V1–V11 do backlog anterior.** V2 (índice persistente) e V5 (dedup no compile) são os mais sensíveis à decisão de 006.
- **Como verificar que uma referência bibliográfica sugerida existe de fato.** Só vira questão se 005 decidir que o kb recomenda leitura — e aí reabre a dívida de "referências bibliográficas reais" de `011/DOMAIN.md:11`, nunca implementada.
- **Onde mora o limiar de insuficiência**, se 005 escolher detectar lacuna por score em vez de por julgamento de modelo. Hoje não existe limiar em lugar nenhum: o `qa` devolve top-3 sempre, mesmo com o melhor match irrisório.

## Out of scope

- **Implementar qualquer coisa decidida aqui.** Sai pelo `spec-pipeline`, com o `DOMAIN.md` deste diretório como insumo.
- **Os portes V1–V11 do [BACKLOG](../2026-07-28-engenharia-reversa/BACKLOG.md)**, exceto onde a política os invalide ou reordene — e aí a nota vai no ADR, não em ticket próprio.
- **Multi-vault** (feature 010, `draft`, dependente de débito em `kb/config.py`).
- **Os dois bugs de retrieval achados no charting** — registrados em `PENDING_LOG.md` e seguidos dali, porque são bugs de busca, não política de corpus:
  1. o reranker recebe **snippet vazio** para candidatos exclusivamente semânticos — `snippets` só é populado para docs com `tf_total > 0` (`kb/search.py:84-87`) e `_apply_rerank` monta o candidato com `item.get("snippet","")` (`:151-154`). Justamente a classe de artigo que o canal semântico existe para resgatar chega ao LLM como slug nu;
  2. `_apply_rerank` chaveia por `path.stem` (`kb/search.py:155-156`) e o vault tem **4 stems duplicados** em topics diferentes — quando dois caem no mesmo head, um sobrescreve o outro e some do resultado. Afeta também a medição, que compara por stem (`kb/bench.py:246`).
- **Restringir a saída do rerank** (top-N em vez de ordenar 20) — próximo passo já decidido em `memory/next_steps.md:18`, com gate próprio. Independe desta política.
