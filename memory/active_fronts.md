---
name: Active Fronts
description: Frentes ativas + decisões abertas
type: project
---

## Frentes ativas

### F1: Setup completo

**Status:** Em progresso (bloqueador P0)

**O que falta:**
- [ ] `pip install -e .` — instalar pacote
- [ ] Configurar `.env` com `KB_API_KEY` real
- [ ] Teste end-to-end: `kb ingest exemplo.md && kb compile && kb qa "teste?"`

**Bloqueador:** Sem API key válida, nada funciona.

**Next action:** Pedir ao usuário para:
1. Fazer signin em https://opencode.ai/ (ou usar Ollama local)
2. Copiar chave de API
3. `cp .env.example .env && nano .env` (preencher KB_API_KEY)
4. `pip install -e .`

---

### F2: Primeiro documento de teste

**Status:** Pendente

**Objetivo:** Validar fluxo: raw → compile → wiki → qa → file-back

**Documento sugerido:** Um artigo sobre um dos tópicos (cybersecurity, ai, python, typescript)

**Passos:**
1. `kb ingest docs/test.md`
2. `kb compile`
3. Verificar wiki/cybersecurity/ (ou outro topic)
4. `kb qa "O que foi mencionado no artigo?"`
5. `kb qa "Pergunta nova" -f` (file-back)
6. Verificar novo artigo foi criado

---

## Decisões abertas

### Q1: Testes — quando implementar?

**Opção A:** Implementar agora (tests/)
- Cobertura: compile, qa, search, heal, lint
- Benefício: segurança ao refatorar
- Custo: tempo upfront

**Opção B:** Adiar para milestone 2
- Benefício: ir rápido
- Risco: bugs descobe cedo no uso real

**Recomendação:** Opção B — ir rápido com testes manuais (ingest → compile → qa). Adicionar testes quando crescer.

---

### Q2: Obsidian — quando?

**Opção A:** Integração nativa (plugin Obsidian)
- Futura, pós-milestone 1

**Opção B:** Manual (usuário abre wiki/ no Obsidian diretamente)
- Disponível agora
- Wikilinks `[[]]` já funcionam em Obsidian

**Recomendação:** Opção B — usuário pode abrir vault agora. Plugin é futuro.

---

### Q3: Escalabilidade — quando migrar para embeddings?

**Limiar sugerido:** >500 artigos ou >1M palavras

**Quando chegar lá:**
1. Adicionar dependência: `sentence-transformers` ou similar
2. Calcular embeddings no compile + heal
3. Atualizar search com hybrid (TF-IDF + semantic)
4. Manter TF-IDF como fallback

**Prioridade:** P2 (futuro)

---

## Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| LLM gera conflitos git ao file-back | Baixa | Médio | Estratégia Pawel Huryn (append/update, no rewrite) |
| API key exposta em código | Média | Alto | Sempre em .env (gitignored) |
| Wiki fica grande demais (>1M palavras) | Baixa | Médio | Planejar embeddings + RAG para futuro |
| Wikilinks quebrados se deletar artigos | Média | Baixo | Lint detecta, heal remove |

