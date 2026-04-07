# ADR 0010 — Defesa dupla para qualidade de formato do output do LLM em `compile`

- **Status:** Aceito
- **Data:** 2026-04-07

## Contexto

Durante a compilação real do EPUB "Building Applications with AI Agents" (12 capítulos), o LLM retornou todos os artigos envoltos em `` ```markdown `` e `` ``` ``. Isso corrompeu o frontmatter YAML de 25 arquivos em `wiki/ai/` e `wiki/summaries/ai/`, tornando-os inválidos para Obsidian e para o pipeline de search/heal.

A causa raiz foi o SYSTEM prompt do `compile.py`, que usava `` ``` `` para delimitar o exemplo de formato de saída, ensinando implicitamente o modelo a envolver a resposta em fences.

## Decisão

Aplicar defesa dupla (belt-and-suspenders) para garantir que o output do LLM nunca inclua code fences externas ao conteúdo compilado:

1. **Instrução explícita no prompt:** o SYSTEM prompt inclui "apenas o markdown bruto, sem explicações e SEM code fences envolvendo o output" — e o exemplo de formato foi reescrito sem usar `` ``` `` para delimitar o bloco.

2. **Strip defensivo em código:** `_strip_outer_fence(text)` é aplicado após cada chamada ao LLM em `compile_file()`, removendo `` ``` `` de abertura e fechamento se presentes.

```python
def _strip_outer_fence(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip() + "\n"
```

## Consequências

- Output do LLM é limpo mesmo que o modelo ignore a instrução do prompt
- A função é idempotente e não afeta artigos que já chegam sem fences
- Padrão estabelecido: toda geração de conteúdo LLM com formato estrito deve ter defesa defensiva em código, além de instrução no prompt

## Alternativas rejeitadas

### A1: Apenas instrução no prompt
Rejeitada — LLMs podem ignorar instruções de formato, especialmente quando o próprio prompt contém o padrão indesejado como exemplo.

### A2: Apenas strip em código, sem instrução no prompt
Rejeitada — strip é mais frágil para fences parciais ou multi-linguagem (`` ```python ``). A instrução no prompt reduz a frequência de ocorrência.

### A3: Validação e rejeição com retry
Rejeitada — aumenta latência e custo por artigo; defesa passiva é preferível para este caso.
