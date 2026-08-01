# Handoff — 2026-08-01

## Onde parei

Feature **023-claim-grounding** com a especificação fechada e **nenhuma linha de código de feature escrita**. Gates emitidos: `SPEC_VALID`, `PLAN_READY`, `ANALYZE_PASS`, `CONTRACT_VALID`, `EVAL_DESIGN_PARTIAL`.

Branch `proto/answer-verification`, dois commits além de `main`, PR **#60** aberto. Suíte em 739 passed, intocada.

## O que decide o próximo passo

**Dois PRs abertos esperando você**, e eles não são simétricos:

- **#59** trava as decisões da política de corpus (tickets 004–007 + ADR-0018). Enquanto não mergear, o ADR não existe em `main` — a SPEC da 023 teve que recuperá-lo do histórico git para não inventar.
- **#60** carrega o protótipo medido e toda a especificação da 023.

## Como continuar a 023

Entra por **`test-design`, não `test-red`**. O PLAN marca duas condições binárias de risco: output estrutural estável (`--json` cria schema público) e contrato HTTP entre serviços (`GET /v1/models`, `POST /v1/nli` em `:1235`, porta verificada livre).

`T-001` é a primeira task elegível: `tag: AFK`, sem dependências, worktree próprio.

## Três coisas medidas que mudam o desenho

1. **Falso alarme não é uniforme.** Uma síntese fiel recebeu contradição **0,953** — alarme confiante contra conteúdo correto, com a premissa inteira disponível. Os 28% deixam de ser ruído brando. A apresentação precisa separar `contradita` de `sem apoio`.
2. **Comparação numérica não é detectada.** 70% vs 72% dá 0,377, abaixo do corte. O NLI não faz aritmética; a classe só é pega quando a inversão é lexical.
3. **O holdout tem zero pares.** Os 8 pares automáticos já calibraram os limiares atuais — todo número existente é teto otimista. Mínimo viável: 12 pares novos, congelados antes de recalibrar.

## Delegação

SPEC, PLAN, TASKS e EVALS foram redigidos pelo GPT 5.6 Terra; gates e review zero-trust ficaram comigo. Rendeu bem — a decisão de pôr o NLI atrás de serviço HTTP em vez de extra opcional foi dele e está certa (mantém `torch` e ~2 GB de pesos fora do caminho de todo usuário do `kb`).

O review pegou duas coisas que a leitura sozinha não pegaria: uma promessa de compatibilidade que não tinha task (virou `T-008`, com 5 arquivos de teste dependentes) e um caso de eval que esperava o veredito oposto ao que o próprio documento defendia. O segundo só apareceu ao **executar** o grader.

## Prompt de retomada

```
Retomar o kb. Decidir #59 e #60 primeiro — o #59 trava as decisões da política
de corpus. Se a 023 seguir, entrar por test-design (não test-red) a partir da
T-001; o serviço NLI precisa subir em :1235 antes dos testes de contrato.
```
