# Test-appeasement: produção moldada pelo mock

## Summary

Código de produção ganhou forma para satisfazer testes acoplados à implementação — não para servir usuário nenhum. O mecanismo é sempre o mesmo: um teste mocka um colaborador interno com uma forma errada (tupla crua, env var, path fake), o código quebra, e a "correção" acomoda o mock em vez de corrigir o teste. O resultado é código fantasma em produção: caminhos inalcançáveis, estado contrabandeado, globals mutadas por chamada — cada um capaz de esconder um bug real atrás de um default silencioso.

## Root Cause

Teste que asserta **fiação** (qual função interna é chamada, com qual assinatura, devolvendo qual estrutura) em vez de **comportamento observável**. Quando a implementação evolui, o teste vermelho tem três saídas: corrigir o código, corrigir o teste — ou a terceira, sempre barata e sempre disponível, **mudar o código de um jeito que satisfaz o teste sem consertar nada**. Sem gate mecânico, a terceira vence sob pressão, porque é a única que não exige entender o que o teste deveria provar.

Sinais recorrentes: `getattr(x, "attr", default)` cujo default é inalcançável no call path real; subclasse de builtin pendurando atributos; produção relendo env em tempo de chamada num módulo que resolve config no import; global mutada dentro de fluxo de request.

## Prevention

Gate mecânico bloqueante no CI, com ratchet — `.github/workflows/tests.yml` roda após o ruff:

```bash
python -B scripts/appeasement_report.py --src kb --tests tests --baseline .appeasement-baseline.json
```

O detector (`scripts/appeasement_report.py`, vendorizado da skill `test-appeasement-audit` do harness) cruza a AST da produção com o índice de patches dos testes: `getattr` sobre retorno de função interna patcheada é finding `high` e **quebra o CI** se não estiver no baseline. Entradas do baseline só saem, nunca entram — adição em PR é negada em review. Provado em 2026-08-01: finding sintético → exit 1; limpo → exit 0.

A camada de julgamento (banda ambígua, vereditos, cross-model) vive na skill `test-appeasement-audit` em `~/.claude/core/skills/`.

## Evidence

1. **2026-08-01 — `kb/cli.py:493`** (detectado pelo gate, corrigido): `getattr(result, "grounding", GroundingResult())` com default inalcançável — `execute_qa_command` sempre devolve `QaResult` em produção. Existia porque 6 testes em `test_cli.py`/`test_qa_cmds.py` mockavam o produtor devolvendo tupla crua. Correção: os mocks passaram a devolver o contrato real; o default morreu. O experimento de remoção expôs mais 3 mocks acoplados que a leitura não tinha achado.
2. **2026-08-01 — `_AnswerText(str)`** (removido no mesmo dia em que entrou): subclasse de `str` contrabandeando `grounding` como atributo, para que o teste que assertava `patch("kb.qa.answer")` continuasse verde. Substituído por `QaResult`. O remanescente `QaResult(tuple)` foi julgado **LEGÍTIMO** por juiz cross-model (GPT 5.6 Terra): a forma-tupla é contrato público documentado de `answer_and_file()` com consumidor real de produção desempacotando — os testes confirmam o requisito, não o criam. Exceção auditável via pragma `# appease: allow(TA-2) ...` na própria classe; deixa de valer se a API depreciar o retorno `tuple[str, Path | None]`.
3. **2026-08-01 — `kb/qa.py` relendo `KB_STATE_DIR`/`KB_OUTPUTS_DIR` por env a cada chamada** (removido): existia só para `monkeypatch.setenv` de teste funcionar num módulo que resolve config no import. Os testes passaram a patchar `kb.config` direto — o mesmo padrão que o incidente de 2026-07-29 (índice de embeddings real destruído por `STATE_DIR` não isolado) já tinha ensinado.
4. **2026-07-30 — `kb/git.py` (histórico, ERROR_LOG)**: 11 testes patcheavam `kb.git.ROOT` e "asseguravam o comportamento defeituoso" — o bug de `--commit` nunca versionar nada era mantido verde pela suíte.
