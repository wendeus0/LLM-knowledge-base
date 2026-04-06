---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F1: Validação operacional com provider real

**Status:** Em aberto

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

**Status:** Adiado

**Objetivo:** Reduzir o acoplamento por path usado hoje no laboratório.

**Recomendação atual:** adiar até o próximo ciclo; solução corrente está funcional e coberta por testes.

---

### F4: Merge de PRs abertos

**Status:** Aguardando aprovação

**Objetivo:** Fechar o ciclo das features desenvolvidas neste sprint.

**O que falta:**
- [ ] Merge PR#14 (`feat/wikilink-traversal`)
- [ ] Merge PR#15 (`feat/rich-book-import-metadata`) — inclui fix de URL-encoding de 2026-04-06

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
