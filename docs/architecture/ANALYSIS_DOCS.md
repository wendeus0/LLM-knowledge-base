# Análise de Documentação Arquitetural — kb

## Documentos Existentes

### 1. ✅ Presentes e Adequados

| Documento                          | Status      | Avaliação                                                                    |
| ---------------------------------- | ----------- | ---------------------------------------------------------------------------- |
| `AGENTS.md`                        | ✅ Completo | Documentação principal com domínio, stack, comandos, convenções, arquitetura |
| `docs/architecture/TDD.md`         | ✅ Completo | Convenções de teste, estrutura, fixtures, cobertura                          |
| `docs/architecture/SPEC_FORMAT.md` | ✅ Completo | Template para especificação de features                                      |
| `docs/adr/0001-*.md`               | ✅ Completo | ADR sobre book import e LLM opcional                                         |
| `CLAUDE.md`                        | ✅ Presente | Configurações específicas para Claude Code                                   |

### 2. ⚠️ Documentos Ausentes ou Incompletos

| Gap                     | Prioridade | Justificativa                                                         |
| ----------------------- | ---------- | --------------------------------------------------------------------- |
| **ARCHITECTURE.md**     | P1         | Visão geral da arquitetura (fluxos de dados, componentes, interfaces) |
| **API.md**              | P1         | Documentação da API pública (CLI e módulos Python)                    |
| **DEPLOYMENT.md**       | P2         | Guia de deploy/install em diferentes ambientes                        |
| **CONTRIBUTING.md**     | P2         | Guia para contribuidores (workflow, PR, commits)                      |
| **CHANGELOG.md**        | P2         | Histórico de mudanças versionado                                      |
| **SECURITY.md**         | P2         | Política de segurança, reporte de vulnerabilidades                    |
| **docs/adr/0002-\*.md** | P3         | ADRs pendentes: escolha de Typer vs Click, estratégia de busca        |

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

## Recomendação de Prioridade

```
Fase 1 (Semana 1): ARCHITECTURE.md
Fase 2 (Semana 2): API.md
Fase 3 (Mês 2): CONTRIBUTING.md + CHANGELOG.md
Fase 4 (Backlog): ADRs pendentes + DEPLOYMENT.md + SECURITY.md
```

## Checklist de Documentação

- [x] README.md (público, usuário final)
- [x] AGENTS.md (contexto interno)
- [x] TDD.md (convenções de teste)
- [x] SPEC_FORMAT.md (template de features)
- [x] ADR-0001 (book import/LLM opcional)
- [ ] ARCHITECTURE.md (visão técnica)
- [ ] API.md (referência completa)
- [ ] CONTRIBUTING.md (contribuidores)
- [ ] CHANGELOG.md (histórico)
- [ ] SECURITY.md (segurança)
