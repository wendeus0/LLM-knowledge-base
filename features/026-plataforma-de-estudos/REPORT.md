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

**928 passed** nos dois ambientes (vault real e `KB_DATA_DIR` inexistente) · `ruff` limpo · gate de test-appeasement exit 0.

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

## Riscos e dívida

| Item | Estado |
|---|---|
| **Roadmap não existe** | Fase 2. A sidebar já nasceu no formato que ele vai preencher, mas hoje lista só os artigos do topic |
| **Progresso mostra 0%** | Não há marcação de "li este artigo"; a barra existe sem alimentação |
| **Wikilinks do vault apontam para conceitos sem artigo** | É o gancho funcionando como desenhado, mas significa muitos links cinza numa primeira leitura |
| **Sem auth, só localhost** | Sair disso exige ADR próprio (gatilho registrado no 0019) |
| **`kb_state/` sem locking** | Mitigado: a plataforma só lê. Escrever exigiria locking antes |

## Próximos passos

1. Marcar progresso de leitura — a barra da sidebar precisa de dado.
2. Roadmap (fase 2): trilha importada, ajustada à mão, com cobertura do corpus.
3. Compilar direto pelo gancho: hoje ele lista as fontes; falta o botão que dispara `compile_file`.
