---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F1: Validação operacional com provider real

**Status:** Em progresso

**Objetivo:** Confirmar que a configuração atual com OpenCode Go funciona ponta a ponta em uso real, não apenas com mocks.

**O que falta:**
- [ ] Rodar `kb import-book <arquivo> --compile` com um EPUB real
- [ ] Rodar `kb qa`, `kb heal` e `kb lint` usando a chave já configurada
- [ ] Validar ergonomia de erro quando o extra `.[llm]` não está instalado

**Risco principal:** comportamento real do provider pode divergir do ambiente de teste mockado.

---

### F2: Segurança operacional do conteúdo

**Status:** Em aberto

**Objetivo:** Definir guardrails para evitar envio/commit acidental de conteúdo sensível.

**O que falta:**
- [ ] Documentar o que pode ou não ser enviado ao provider externo
- [ ] Avaliar necessidade de modo sem commit automático para alguns fluxos
- [ ] Transformar recomendações do `SECURITY_AUDIT_REPORT.md` em política operacional

---

### F3: Empacotamento definitivo da relação `book2md` → `kb`

**Status:** Em aberto

**Objetivo:** Reduzir o acoplamento por path usado hoje no laboratório.

**Opções:**
1. Tornar `kb` dependência explícita de `book2md`
2. Extrair pacote compartilhado mínimo
3. Manter compat layer atual enquanto o laboratório seguir no mesmo mono-workspace

**Recomendação atual:** adiar até o próximo ciclo, porque a solução corrente está funcional e coberta por testes.

## Decisões abertas

### Q1: O fluxo de livro importado deve sempre passar por `compile`?

**Trade-off:**
- Sim: maximiza consistência com a wiki assistida por LLM
- Não: preserva capítulos markdown como saída final legível sem custo de provider

**Estado:** parcialmente resolvido com `--compile` opcional; ainda falta decidir o padrão operacional recomendado.

### Q2: Commit automático deve ser sempre obrigatório em writes da wiki?

**Trade-off:**
- Sim: rastreabilidade total
- Não: melhor controle para conteúdo sensível/experimentos

**Estado:** decisão ainda em aberto; sem mudança implementada neste sprint.

### Q3: Quando promover o pacote/laboratório para distribuição formal?

**Limiar sugerido:** quando o fluxo de livro estiver estabilizado e for necessário consumir `book2md` fora do workspace atual.
