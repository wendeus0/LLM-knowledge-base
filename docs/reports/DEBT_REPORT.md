# DEBT_REPORT.md

## Sprint fechado em 2026-04-07

## P0

- Nenhum débito P0 aberto.

## P1

1. **Corrigir 8 testes falhando em `tests/unit/test_web_ingest.py`**
   - `AttributeError: None does not have the attribute 'get'`
   - falha pré-existente no setup de mock
   - impacta a confiabilidade da suíte

2. **Neutralizar documentação histórica restante ainda acoplada ao corpus antigo**
   - `docs/architecture/ARCHITECTURE.md` ainda contém blocos grandes com estrutura temática antiga
   - `docs/API.md` ainda tem exemplos residuais e referências técnicas a `TOPICS`

## P2

1. **Tornar `TOPICS` configurável por corpus**
   - hoje ainda é lista fixa em `kb/config.py`
   - isso mantém acoplamento parcial entre engine e domínios temáticos

2. **Refinar guardrail de credenciais**
   - falso positivo com nomes de variável como `OPENAI_API_KEY` em exemplos de código
   - desejável ignorar blocos de código markdown ou melhorar contexto do detector

3. **Aumentar cobertura em `kb/git.py` e `kb/client.py`**
   - gaps seguem prioritários para estabilização do produto

4. **Decidir a política do repositório externo do corpus**
   - definir se `/home/g0dsssp33d/work/llm-wiki` terá Git próprio, backup automatizado ou será apenas diretório local

5. **Embeddings + RAG híbrido**
   - futuro, condicionado à escala do corpus

## Veredito

- sprint fecha com separação bem-sucedida entre engine e corpus do usuário
- débito principal remanescente é documental/técnico, não bloqueador arquitetural
- postura open source do repositório melhorou significativamente
