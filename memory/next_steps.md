---
name: Next Steps
description: Próximos passos recomendados (atualizado a cada sessão)
type: project
---

## Imediato (sessão próxima)

1. **[P0 Bloqueador]** Configurar .env com API key
   - `cp .env.example .env`
   - Preencher `KB_API_KEY` (OpenCode Go ou Ollama)
   - Testar: `python -c "from kb.config import API_KEY; print('OK')" `

2. **[P0]** Instalar pacote
   - `python -m venv .venv && source .venv/bin/activate` (Linux/Mac)
   - `pip install -e .`
   - Testar: `kb --help`

3. **[P0]** Primeiro teste end-to-end
   - Criar um documento `exemplo.md` com 200-500 palavras sobre um tópico (ex: "O que é XSS?")
   - `kb ingest exemplo.md`
   - `kb compile`
   - Verificar se foi criado em `wiki/` (ex: wiki/cybersecurity/xss.md)
   - `kb qa "O que é XSS?" -f` (pergunta + file-back)
   - Verificar se criou novo artigo com a resposta

---

## Curto prazo (próximas 2 sessões)

4. **[P1]** Adicionar mais documentos
   - Pesquisar/coletar 5-10 artigos sobre os 4 tópicos
   - Compilar todos
   - Verificar wiki/ cresce com qualidade

5. **[P2]** Usar Obsidian
   - Abrir `/home/g0dsssp33d/work/kb` como vault em Obsidian
   - Navegar wiki/ com wikilinks
   - (Opcional) instalar Obsidian Web Clipper para ingest direto da web

6. **[P1]** Testar stochastic heal
   - `kb heal --n 5` (pequeno teste)
   - Verificar logs de ações (deleted_stub, healed, reviewed_no_changes)
   - Checar git commits criados

---

## Médio prazo (próximo mês)

7. **[P2]** Implementar testes (tests/)
   - Unit: compile, qa, search, heal
   - Integration: raw → wiki → qa
   - Target: 70%+ coverage

8. **[P2]** Adicionar linting básico
   - `ruff check kb`
   - Integrar em CI/pre-commit (futuro)

9. **[P2]** Documentação do projeto
   - README.md (como usar)
   - Architecture.md (design decisions)
   - CLI.md (referência de comandos)

---

## Longo prazo (futuro)

10. **[P2]** Obsidian plugin
    - Plugin nativo que chama `kb` via CLI
    - Renderizar outputs em Obsidian diretamente

11. **[P2]** Embeddings + RAG
    - Quando wiki > 500 artigos
    - Adicionar `sentence-transformers`, FAISS
    - Hybrid search (TF-IDF + semantic)

12. **[P2]** Finetuning
    - Treinar modelo local no corpus da wiki
    - Usar com Ollama
    - Full offline capabilities

---

## Bloqueadores atuais

- ❌ KB_API_KEY não configurada → bloqueia tudo
- ✓ Estrutura de código OK
- ✓ CLI OK
- ✓ Git automático OK

**UNBLOCK:** Preencher .env

