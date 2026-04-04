# Análise de Documentação Arquitetural — kb

## Documentos Existentes

### 1. ✅ Presentes e Adequados

| Documento                              | Status      | Avaliação                                                                    |
| -------------------------------------- | ----------- | ---------------------------------------------------------------------------- |
| `AGENTS.md`                            | ✅ Completo | Documentação principal com domínio, stack, comandos, convenções, arquitetura |
| `README.md`                            | ✅ Completo | Documentação pública para usuários                                           |
| `docs/architecture/ARCHITECTURE.md`    | ✅ Completo | Visão técnica C4 Model, fluxos, componentes                                  |
| `docs/architecture/API.md`             | ✅ Completo | Referência completa CLI e API Python                                         |
| `CONTRIBUTING.md`                      | ✅ Completo | Guia de contribuição com workflow e convenções                               |
| `docs/architecture/TDD.md`             | ✅ Completo | Convenções de teste, estrutura, fixtures, cobertura                          |
| `docs/architecture/SPEC_FORMAT.md`     | ✅ Completo | Template para especificação de features                                      |
| `docs/architecture/ARTIFACT_POLICY.md` | ✅ Completo | Política de artefatos Python                                                 |
| `docs/architecture/DATA_POLICY.md`     | ✅ Completo | Política de persistência de dados                                            |
| `docs/adr/0001-*.md`                   | ✅ Completo | ADR sobre book import e LLM opcional                                         |
| `CLAUDE.md`                            | ✅ Presente | Configurações específicas para Claude Code                                   |

### 2. ⚠️ Documentos Pendentes (Backlog)

| Gap             | Prioridade | Justificativa                                      |
| --------------- | ---------- | -------------------------------------------------- |
| **SECURITY.md** | P2         | Política de segurança, reporte de vulnerabilidades |

## Análise Detalhada

### ARCHITECTURE.md (AUSENTE — P1)

**Motivo:** AGENTS.md tem seção de arquitetura, mas é um diagrama estático. Falta:

- Fluxos de dados (ingest → compile → wiki)
- Sequência de operações (QA: search → context → LLM → response)
- Diagrama de componentes e dependências
- Contratos entre módulos

**Conteúdo sugerido:**

- Visão geral (C4 Model — Context, Containers)
- Fluxos: ingest, compile, qa, heal, lint
- Interfaces: CLI (Typer), Python API, Git integration
- Decisões arquiteturais consolidadas

### API.md (AUSENTE — P1)

**Motivo:** Comandos documentados em AGENTS.md, mas sem detalhes:

- Parâmetros e opções de cada comando
- Exemplos de uso avançado
- API Python pública (funções dos módulos)
- Códigos de retorno e erros

**Conteúdo sugerido:**

- Referência completa de comandos CLI
- Documentação de funções públicas (docstrings → markdown)
- Exemplos de integração programática

### ADRs Adicionais (P3)

Decisões que merecem ADR formal:

1. **Escolha de Typer** vs Click/argparse — porque Typer foi escolhido
2. **Estratégia de busca** — contagem simples de keywords vs full-text search
3. **Stochastic heal** — por que abordagem aleatória vs determinística
4. **Git como backend** — versionamento implícito via commits automáticos
5. **YAML frontmatter** — escolha de formato de metadata

## Recomendação de Prioridade (Atualizado)

```
✅ CONCLUÍDO:
   - README.md
   - ARCHITECTURE.md
   - API.md
   - CONTRIBUTING.md
   - ARTIFACT_POLICY.md
   - DATA_POLICY.md
   - DEPLOYMENT.md
   - CHANGELOG.md
   - SECURITY.md
   - ADR-0001 a 0005

🔄 PENDENTE:
Fase 1: Estrutura features/ (diretório por feature — opcional)
```

## Checklist de Documentação

### ✅ Concluídos

- [x] README.md (público, usuário final)
- [x] AGENTS.md (contexto interno)
- [x] ARCHITECTURE.md (visão técnica C4 Model)
- [x] API.md (referência CLI e Python)
- [x] CONTRIBUTING.md (guia de contribuição)
- [x] TDD.md (convenções de teste)
- [x] SPEC_FORMAT.md (template de features)
- [x] ARTIFACT_POLICY.md (política de artefatos)
- [x] DATA_POLICY.md (política de dados)
- [x] DEPLOYMENT.md (guia de deploy)
- [x] CHANGELOG.md (histórico versionado)
- [x] SECURITY.md (política de segurança)
- [x] ADR-0001 a 0005 (decisões arquiteturais)

### 🔄 Pendentes

- [ ] Estrutura features/ (diretório por feature — opcional)

---

## Análise Comparativa (Referência Externa)

Esta seção documenta a análise comparativa com o projeto `albion-market-insights` para identificação de padrões de documentação aplicáveis ao kb.

### Resumo Executivo

| Aspecto                   | kb (antes)  | albion-market-insights          | Ação tomada                                    |
| ------------------------- | ----------- | ------------------------------- | ---------------------------------------------- |
| **Estrutura docs/**       | Minimalista | Completa, madura                | ✅ Expandida com políticas                     |
| **Políticas específicas** | Ausentes    | STORAGE_POLICY, ARTIFACT_POLICY | ✅ Criados ARTIFACT_POLICY.md e DATA_POLICY.md |
| **Features como unidade** | Implícito   | Explícito (features/)           | ⚠️ Definido em SPEC_FORMAT.md                  |
| **ADRs**                  | 1 apenas    | Múltiplos                       | ✅ Expandido para 5 ADRs                       |

### Padrões Adotados

1. **Política de artefatos** → `ARTIFACT_POLICY.md` (Python/cache)
2. **Política de dados** → `DATA_POLICY.md` (persistência em disco)
3. **Guia de deploy** → `DEPLOYMENT.md`
4. **Múltiplos ADRs** → 0001-0005

### Padrões Não Aplicáveis (contexto diferente)

| Padrão albion                 | Motivo de não aplicação |
| ----------------------------- | ----------------------- |
| STORAGE_POLICY (localStorage) | kb é CLI, não navegador |
| NODE24_PROMOTION_RUNBOOK      | kb é Python, não Node   |
| Browser-specific policies     | kb não tem frontend web |

### Fortalezas do kb Preservadas

- AGENTS.md enxuto (foco em domínio)
- SPEC_FORMAT.md claro
- TDD.md completo
- Memória distribuída em `memory/`
- Documentação em português
