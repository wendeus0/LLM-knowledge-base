---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F1: Validação operacional com provider real

**Status:** Concluído (2026-04-07)

**Resultado:**
- [x] `kb search` — OK
- [x] `kb lint` — OK (auditoria via LLM funcionando)
- [x] `kb qa "pergunta"` — OK (resposta via wiki + provider)
- [x] `kb heal --n 2` — OK (provider lento ~>60s, sem erro)
- [x] `kb import-book <epub> --compile` — OK; 12 capítulos de "Building Applications with AI Agents" compilados para wiki/ai/

**Nota:** `heal` é notavelmente lento com o provider atual (>60s). Não é erro — é latência do OpenCode Go.

---

### F2: Política operacional de sensibilidade

**Status:** Concluído (2026-04-07)

**Entregável:** `docs/SENSITIVE_CONTENT_POLICY.md`
- Padrões detectados pelo guardrail documentados
- Critérios explícitos de quando usar/não usar `--allow-sensitive`
- Critérios de quando usar/não usar `--no-commit`
- Lacunas conhecidas (L2: AWS/GitHub/GitLab tokens) sinalizadas
- Política por diretório (`raw/private/`) identificada como futura

---

### F3: Empacotamento definitivo da relação `book2md` → `kb`

**Status:** Encerrado (2026-04-07)

**Decisão:** A3 rejeitada formalmente em ADR-0001. Núcleo permanece em `kb/book_import_core.py`. Sem demanda concreta de distribuição externa independente.

**Critério de reabertura:** necessidade real de instalar `book2md` fora do workspace como pacote independente.

---

### F4: Merge de PRs abertos

**Status:** Concluído (2026-04-07)

**Resultado:** PR#14 e PR#15 mergeados conforme confirmação do usuário.

---

### F5: Avaliação de incrementos do produto

**Status:** Aguardando subsídios do usuário

**Objetivo:** Analisar material externo fornecido pelo usuário e decidir se o projeto deve ser expandido.

**O que falta:**
- [ ] Receber material (subsídios) do usuário
- [ ] Avaliar alinhamento com a arquitetura atual
- [ ] Decidir escopo de nova feature, se aplicável

---

## Decisões abertas

### Q1: O fluxo de livro importado deve sempre passar por `compile`?

**Trade-off:**
- Sim: maximiza consistência com a wiki assistida por LLM
- Não: preserva capítulos markdown como saída final legível sem custo de provider

**Estado:** parcialmente resolvido com `--compile` opcional; ainda falta decidir o padrão operacional recomendado.

### Q2: `--no-commit` deve permanecer apenas por comando ou ganhar política configurável?

**Trade-off:**
- Por comando: mais explícito e seguro
- Configurável: mais prático para certos ambientes, mas mais arriscado

**Estado:** mantido por comando nesta fase; sem estado global persistente.

### Q3: Quando promover o pacote/laboratório para distribuição formal?

**Limiar sugerido:** quando o fluxo de livro estiver estabilizado e for necessário consumir `book2md` fora do workspace atual.
