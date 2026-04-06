---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F0: Trabalho não commitado em branch errado

**Status:** Pendente resolução

**Contexto:** Branch `feat/readme-arch-docs` teve PR mergeado (`5520c05`), mas o branch local carrega implementação completa das features `pal-foundation-phase-1` e `sensitive-execution-controls` sem commit: novos módulos (`guardrails.py`, `router.py`, `state.py`, `jobs.py`, testes), 17 arquivos tracked modificados. 85 testes passando.

**O que falta:**
- [ ] Criar branch de feature correto a partir do estado atual
- [ ] Passar pelo workflow: test-red → green-refactor → quality-gate → report-writer → git-flow-manager
- [ ] Commitar e abrir PR para cada feature separadamente

**Risco:** perda de trabalho ou mistura de escopo a cada nova sessão.

---

### F1: Validação operacional com provider real

**Status:** Em progresso

**Objetivo:** Confirmar que a configuração atual com OpenCode Go funciona ponta a ponta em uso real, não apenas com mocks.

**O que falta:**
- [ ] Rodar `kb import-book <arquivo> --compile` com um EPUB real
- [ ] Rodar `kb qa`, `kb heal` e `kb lint` usando a chave já configurada
- [ ] Validar ergonomia de erro quando o extra `.[llm]` não está instalado

**Risco principal:** comportamento real do provider pode divergir do ambiente de teste mockado.

---

### F2: Política operacional de sensibilidade

**Status:** Em aberto

**Objetivo:** Consolidar regras de uso para `--allow-sensitive` e `--no-commit`.

**O que falta:**
- [ ] Documentar o que pode ou não ser enviado ao provider externo
- [ ] Definir quando `--allow-sensitive` é aceitável
- [ ] Definir quando `--no-commit` pode ser usado sem comprometer rastreabilidade
- [ ] Avaliar políticas por diretório (`raw/private/`) como evolução futura

**Risco principal:** uso inconsistente das novas flags por falta de política operacional fechada.

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

### Q2: `--no-commit` deve permanecer apenas por comando ou ganhar política configurável?

**Trade-off:**
- Por comando: mais explícito e seguro
- Configurável: mais prático para certos ambientes, mas mais arriscado

**Estado:** mantido por comando nesta fase; sem estado global persistente.

### Q3: Quando promover o pacote/laboratório para distribuição formal?

**Limiar sugerido:** quando o fluxo de livro estiver estabilizado e for necessário consumir `book2md` fora do workspace atual.
