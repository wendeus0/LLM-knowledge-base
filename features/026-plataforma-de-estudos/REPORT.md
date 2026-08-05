# REPORT — 026-plataforma-de-estudos (F1–F5)

**Estado:** `DONE_WITH_CONCERNS`
**Branch:** `feat/026-plataforma-estudos`

## Contexto

O usuário passou dois dias corrigindo o `kb` sem conseguir usá-lo para estudar cibersegurança. O grilling mostrou que ele não queria um leitor melhor — queria uma **plataforma de estudos** que substitui o Obsidian e usa o `kb` como motor.

O ciclo que ele definiu como "utilizável" fecha nesta entrega: ler → buscar → perguntar → gerar card → verificar → revisar.

## O que existe agora

| Camada | O quê |
|---|---|
| `kb/api/` | Seis rotas: `/health`, `/articles`, `/search`, `/qa`, `/article/{slug:path}`, `/stats` |
| `study/render.py` | Markdown com wikilinks resolvidos; link sem artigo vira gancho |
| `study/sources.py` | Busca de fontes em três origens, classificadas por capacidade |
| `study/db.py` + `notes` + `highlights` | Estado de estudo em SQLite próprio |
| `study/cards.py` | Geração por LLM com verificação obrigatória por grounding |
| `study/review.py` | Agendamento por `fsrs`, quatro ratings 1:1 |
| `study/web.py` + templates | Leitor com dois temas, sidebar de trilha, htmx |

## Validação

**963 passed**, cobertura 93% · `ruff check kb study tests` limpo · gate de test-appeasement exit 0. (Eram 928 na primeira entrega; a rodada de correção do PR #66, abaixo, somou 35 testes.)

**Provado com serviços reais, não só com mock:**

- O leitor renderiza os 1.040 artigos do vault; medido na tela: bege `rgb(239,231,218)` no claro, `rgb(25,23,21)` com laranja `rgb(240,122,50)` no escuro, sem flash de tema.
- O gancho de fontes encontra `raw/xss-attack-explained.md` como "compilar diretamente" e material de `library/` como "importar livro antes".
- Nota e destaque não mudam um byte do markdown (sha256 idêntico).
- Destaque cujo texto some vira órfão com o trecho preservado — não apagado, não reposicionado.
- **O gate de ancoragem bloqueou um card real:** o Codex Luna gerou 5 cards do artigo de GHDB, o NLI aprovou 4 e reprovou "Quem mantém a GHDB?" como `contradita`.

## Defeitos achados no ciclo

**Só a tela renderizada pegaria:** título duplicado em todo artigo (template + `# H1` do markdown); gancho como botão inline separando a pontuação; marcador da sidebar encolhido em item de duas linhas; medida de linha em 57 caracteres contra os 65–75 do desenho.

**Só o fluxo real pegaria:** o gancho de fontes não achava nada em produção nenhuma — `study/sources.py` lia `os.getenv("KB_DATA_DIR")` sem carregar o `.env` e caía no repositório. E o shim do Codex falhava sob launchd, que não herda o `PATH` do shell.

**Só o review de contrato pegaria:** `/article` não expunha `wikilinks` e `/search` não devolvia `title` — o `response_model` do Pydantic filtrava o campo acrescentado ao dict, silenciosamente.

## O Codex bloqueou três vezes, e as três estavam certas

1. `RED_BLOCKED` por falta de SPEC validada — eu tinha pulado o spec-pipeline.
2. A SPEC que ele escreveu exigiu ADR e levantou duas clarificações reais.
3. Recusou implementar a F2 sem rota de listagem, em vez de importar `kb` direto e furar o ADR-0019.

## Rodada de correção do PR #66 (2026-08-05)

Três bots de review (CodeAnt AI, CodeRabbit, cubic) levantaram ~85 apontamentos e três jobs de CI falhavam. O que mudou, por severidade:

**CI e segurança.** `.github/workflows/tests.yml` instalava sem os extras `api`/`study` — os três jobs de teste caíam por falta de `fastapi`/`httpx`. Novo `kb/security.py` com dois middlewares: recusa de requisição fora do loopback (`KB_ALLOW_REMOTE_ACCESS=1` faz o opt-in explícito) e recusa de escrita cross-origin por `Origin`/`Referer`, que é o vetor real de CSRF numa app sem sessão. O `TestClient` do Starlette usa `("testclient", 50000)`, que não é loopback: os 20 call-sites viraram `TestClient(app, client=("127.0.0.1", 51234))`.

**Concorrência e corretude.**

| Onde | O que estava errado |
|---|---|
| `study/web.py` | Rotas `async` chamavam `httpx` síncrono e travavam o event loop — agora via `run_in_threadpool` |
| `study/review.py` | `fsrs_state` era lido fora da transação que o reescrevia: duas revisões simultâneas partiam do mesmo estado e a última vencia. Agora `BEGIN IMMEDIATE` serializa leitura e escrita — reproduzido por teste antes do fix |
| `study/db.py` | Duas conexões migrando ao mesmo tempo estouravam `duplicate column name` (reproduzido com oito conexões sobre um banco legado). WAL e `busy_timeout` também entraram |
| `kb/grounding.py` | Falha crua do servidor de embeddings virava 500 em vez de `degraded` — o `try` só cobria `classify()` |
| `kb/api/articles.py` | O índice de wikilinks era `lru_cache` sem invalidação: artigo novo ou editado não aparecia até reiniciar a API. Agora a chave inclui uma assinatura (`mtime`+tamanho) do corpus, e os backlinks saem de um mapa invertido calculado uma vez — antes cada requisição relia o corpus inteiro |
| `kb/api/articles.py` | `Path.with_suffix(".md")` transformava `ai/gpt-4.5` em `ai/gpt-4.md` |
| `study/highlights.py` + `study/render.py` | A âncora do destaque era procurada no Markdown cru, mas a seleção vem do texto renderizado: todo destaque que passasse por ênfase, link ou wikilink virava órfão. Agora casa contra o texto renderizado, marca através de nós (`**ênfase**` no meio) e reancora só quando a citação é única — antes escolhia a primeira de várias em silêncio |
| `study/cards.py` | `edit_card` aceitava cartão já `aceito` e zerava o progresso FSRS; candidatos fora de 40–240 caracteres não eram descartados; o grounding verificava pergunta + resposta em vez da resposta |
| Templates | Um lote novo de cards escondia os já curados; `POST /revisar/{id}` devolvia a página inteira para um `hx-swap="outerHTML"` de fragmento |

**Fase 4 (mecânica, delegada ao Codex e revisada aqui).** Fixture `api_client` única em `tests/integration/conftest.py` (sete arquivos deduplicados), `card_row` único em `study/db.py`, htmx e Alpine vendorizados em `study/static/vendor/` (o Alpine estava em `3.x.x`, sem pin), data devida em formato legível, e o oráculo do teste de FSRS trocado por data literal — ele recalculava o valor esperado com o mesmo `Scheduler` da implementação.

**Direção de design B.** Paleta fechada (`#efe7da`/`#fffdf9`/`#b4551f`/`#191715`), fonte pixelada de 4,7 KB restrita a título de trilha e números, botão que afunda 4px, toast de conquista que sai sozinho, `0%` substituído por "Artigo N de M na trilha", trilha que recua na leitura e `prefers-reduced-motion` cobrindo tudo isso. Detalhe e justificativa de contraste em `docs/research/2026-08-01-kb-para-estudo/DESIGN.md`.

**Não feito, e por quê.** O `Form(...)` nativo do FastAPI no lugar do `_form_value` exigiria acrescentar `python-multipart` como dependência de runtime para um ganho cosmético — o parser atual está coberto por teste. A subtração visual na trilha (concluído tachado) depende da marcação de leitura, que segue como dívida abaixo.

## Riscos e dívida

| Item | Estado |
|---|---|
| **Roadmap não existe** | Fase 2. A sidebar já nasceu no formato que ele vai preencher, mas hoje lista só os artigos do topic |
| **Progresso é posição, não leitura** | A barra mostra "Artigo N de M na trilha" porque não existe marcação de "li este artigo". Enquanto ela não existir, não há como tachar o concluído na trilha — que é o mecanismo de subtração da direção B |
| **Wikilinks do vault apontam para conceitos sem artigo** | É o gancho funcionando como desenhado, mas significa muitos links cinza numa primeira leitura |
| **Sem auth, só localhost** | Sair disso exige ADR próprio (gatilho registrado no 0019) |
| **`kb_state/` sem locking** | Mitigado: a plataforma só lê. Escrever exigiria locking antes |

## Próximos passos

1. Marcar progresso de leitura — a barra da sidebar precisa de dado.
2. Roadmap (fase 2): trilha importada, ajustada à mão, com cobertura do corpus.
3. Compilar direto pelo gancho: hoje ele lista as fontes; falta o botão que dispara `compile_file`.
