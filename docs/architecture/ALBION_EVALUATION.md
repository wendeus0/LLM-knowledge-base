# Avaliação de Documentação Arquitetural

## Comparação: kb vs albion-market-insights

## Resumo Executivo

| Aspecto                   | kb                       | albion-market-insights          | Veredito       |
| ------------------------- | ------------------------ | ------------------------------- | -------------- |
| **Estrutura docs/**       | Minimalista, em evolução | Completa, madura                | albion vence   |
| **Políticas específicas** | Ausentes                 | STORAGE_POLICY, ARTIFACT_POLICY | Precisa no kb  |
| **Features como unidade** | Implícito                | Explícito (features/)           | Adotar no kb   |
| **ADRs**                  | 1 apenas                 | Múltiplos (ADR-004, ADR-007)    | Expandir no kb |
| **Questões abertas**      | PENDING_LOG              | QUESTIONS.md                    | Similar        |
| **Contexto operacional**  | MEMORY.md                | CONTEXT.md                      | Similar        |

---

## 1. Estrutura de Documentação

### albion-market-insights (referência)

```
docs/
├── adr/
│   ├── ADR-004-localstorage-alerts.md
│   ├── ADR-007-market-data-cache.md
│   └── ... (múltiplos ADRs)
├── architecture/
│   ├── ARTIFACT_POLICY.md      ← Política de build
│   ├── STORAGE_POLICY.md       ← Política de localStorage
│   ├── NODE24_PROMOTION_RUNBOOK.md
│   └── ...
├── features/
│   ├── price-alerts/SPEC.md
│   ├── price-alerts/REPORT.md
│   └── ... (1 pasta por feature)
```

### kb (atual)

```
docs/
├── adr/
│   └── 0001-kb-source-of-truth-for-book-import.md
├── architecture/
│   ├── SPEC_FORMAT.md
│   ├── TDD.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── ANALYSIS_DOCS.md
```

### Gap Identificado

**kb não tem:**

1. Políticas específicas de operação
2. Diretório `features/` com specs por feature
3. Runbooks para operações

---

## 2. Documentos Específicos — Análise Detalhada

### 2.1 STORAGE_POLICY.md (albion)

**Propósito:** Define o que pode ser persistido em localStorage, TTL, limites, privacidade.

**Aplicabilidade ao kb:**

- kb é Python CLI, não navegador
- **Equivalente seria:** Política de persistência em disco (raw/, wiki/)
- Cache de LLM calls? Não implementado
- **Decisão:** Não aplicável diretamente, mas bom padrão

### 2.2 ARTIFACT_POLICY.md (albion)

**Propósito:** Define que artefatos de build não devem ser versionados.

**Aplicabilidade ao kb:**

- kb tem `__pycache__/`, `.pytest_cache/`, build artifacts
- `.gitignore` já cobre, mas não há política documentada
- **Recomendação:** Criar ARTIFACT_POLICY.md para Python

### 2.3 features/ (albion)

**Propósito:** Cada feature tem sua própria pasta com SPEC.md e REPORT.md.

**Aplicabilidade ao kb:**

- kb já tem conceito de features no SPEC_FORMAT.md
- Mas não há pasta `features/` com specs versionadas
- **Recomendação:** Adotar estrutura similar

**Exemplo de aplicação ao kb:**

```
features/
├── book-import/
│   ├── SPEC.md
│   └── REPORT.md
├── stochastic-heal/
│   ├── SPEC.md
│   └── REPORT.md
└── qa-file-back/
    ├── SPEC.md
    └── REPORT.md
```

---

## 3. Padrões de Documentação do albion para Adotar no kb

### ✅ Adotar Imediatamente

| Padrão                | Documento kb                           | Justificativa                    |
| --------------------- | -------------------------------------- | -------------------------------- |
| Política de artefatos | `docs/architecture/ARTIFACT_POLICY.md` | Python tem cache/build artifacts |
| Features como pastas  | `features/*/SPEC.md`                   | Já definido em SPEC_FORMAT.md    |
| Runbook de operações  | `docs/architecture/RUNBOOK.md`         | Deploy, troubleshooting          |

### ⚠️ Adaptar ao Contexto

| Padrão albion          | Adaptação kb                       | Motivo                                   |
| ---------------------- | ---------------------------------- | ---------------------------------------- |
| STORAGE_POLICY         | `docs/architecture/DATA_POLICY.md` | Política de dados em disco (raw/, wiki/) |
| ADR-004 (localStorage) | ADR sobre Git como versioning      | Similar: decisão de persistência         |
| ADR-007 (cache)        | ADR sobre LLM caching              | Futuro: cache de chamadas LLM            |

### ❌ Não Aplicável

| Padrão                    | Motivo                |
| ------------------------- | --------------------- |
| NODE24_PROMOTION_RUNBOOK  | kb é Python, não Node |
| Browser-specific policies | kb é CLI, não webapp  |

---

## 4. Checklist de Melhorias para kb

### Fase 1: Políticas (P2)

- [ ] Criar `docs/architecture/ARTIFACT_POLICY.md`
- [ ] Criar `docs/architecture/DATA_POLICY.md`
- [ ] Atualizar `.gitignore` se necessário

### Fase 2: Estrutura de Features (P2)

- [ ] Criar diretório `features/`
- [ ] Mover specs existentes para `features/<nome>/SPEC.md`
- [ ] Criar REPORT.md para features concluídas

### Fase 3: ADRs Adicionais (P3)

- [ ] ADR-002: Escolha de Typer vs Click/argparse
- [ ] ADR-003: Git como sistema de versionamento implícito
- [ ] ADR-004: Estratégia de busca (keywords vs full-text)
- [ ] ADR-005: Stochastic heal vs determinístico

### Fase 4: Runbooks (P3)

- [ ] `docs/architecture/DEPLOYMENT.md`
- [ ] `docs/architecture/TROUBLESHOOTING.md`

---

## 5. Fortalezas do kb a Preservar

| Aspecto              | Por que é bom                     |
| -------------------- | --------------------------------- |
| AGENTS.md enxuto     | Foco em domínio, não processo     |
| SPEC_FORMAT.md claro | Template aprovado e funcional     |
| TDD.md completo      | Convenções de teste bem definidas |
| Memória distribuída  | memory/ com arquivos temáticos    |
| Comentários em PT    | Alinhado com CLAUDE.md global     |

---

## 6. Conclusão

**kb está em transição:** Da documentação mínima (AGENTS.md apenas) para estrutura madura (ARCHITECTURE.md + API.md criados).

**Próximos passos recomendados:**

1. **P2:** Criar ARTIFACT_POLICY.md e DATA_POLICY.md
2. **P2:** Adotar estrutura `features/` para specs
3. **P3:** Expandir ADRs
4. **P3:** Criar runbooks de operação

**Não copiar cegamente:** albion é frontend/Node, kb é CLI/Python. Adaptar padrões ao contexto.
