# ADR 0012 — Compatibilidade provider/model e fallback para resource limit no client

- **Status:** Aceito
- **Data:** 2026-04-12

## Contexto

O módulo `kb/client.py` centraliza chamadas ao provider LLM. Na prática já existem duas decisões duráveis em produção:

1. validação explícita de compatibilidade entre `BASE_URL` OpenCode Go e nomes de modelo permitidos
2. detecção padronizada de erros de limite de recurso (`error 1102`, `worker_exceeded_resources`) para permitir fallback nos fluxos de compilação

Essas decisões estavam implementadas e testadas, mas sem ADR própria, gerando `GAP_ADR` na matriz de conformidade.

## Decisão

1. Manter validação de compatibilidade provider/model no boundary do client:
   - se `BASE_URL` contém `opencode.ai/zen/go`, o modelo deve ser nome simples (sem prefixo)
   - modelos permitidos nesta integração: `kimi-k2.5`, `minimax-2.7`, `glm-5`
2. Tratar incompatibilidade como erro explícito de configuração (falha rápida com mensagem orientativa)
3. Padronizar detecção de erro de resource limit em helper único (`is_provider_resource_limit_error`) via:
   - match por texto da exceção
   - match por campos semânticos em `exc.body` quando presentes
4. Delegar fallback/retry para camadas de domínio (`compile`, `qa`, etc.), mantendo o client como camada de detecção e contrato

## Consequências

### Positivas

- reduz chamadas inválidas ao provider por configuração incorreta
- melhora previsibilidade operacional em ambientes OpenCode Go
- centraliza lógica de detecção de erro transitório/retriável
- mantém cobertura de testes local/offline para decisões críticas

### Negativas

- lista de modelos permitidos exige manutenção explícita quando o provider evoluir
- validação específica por provider aumenta acoplamento contextual no client

## Alternativas consideradas

### A1. Não validar compatibilidade em runtime
- **Rejeitada.** Erros apareceriam tarde e com mensagens menos acionáveis.

### A2. Colocar lista de modelos permitidos em configuração dinâmica
- **Diferida.** Pode ser útil no futuro, mas aumenta superfície de configuração nesta fase.

### A3. Fazer retry/fallback totalmente dentro do client
- **Rejeitada.** Mistura responsabilidades do boundary com regras de domínio.

## Implementação atual vinculada

- `kb/client.py`
  - `validate_provider_model_compatibility()`
  - `is_provider_resource_limit_error()`
- `kb/compile.py`
  - `compile_to_artifact()` (fallback para retry com prompt pré-processado ao detectar resource limit)
- Testes:
  - `tests/unit/test_client.py`
  - `tests/unit/test_compile.py` (`test_should_retry_with_preprocessed_prompt_after_provider_resource_limit_error`)

## Quando revisitar

- inclusão de novos providers com regras específicas
- expansão da whitelist de modelos OpenCode Go
- necessidade de política unificada de retry/backoff cross-comando
