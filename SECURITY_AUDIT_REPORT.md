# SECURITY_AUDIT_REPORT.md

## 1. Superfície de ataque mapeada

- CLI local exposta via comandos `ingest`, `import-book`, `compile`, `qa`, `heal`, `lint` e `search`
- Entradas principais:
  - arquivos locais em `raw/` e `raw/books/`
  - perguntas livres para `qa`
  - variáveis de ambiente `KB_API_KEY`, `KB_BASE_URL`, `KB_MODEL`
- Integrações externas:
  - provider LLM OpenAI-compatible (default: OpenCode Go)
  - git local para commits automáticos da wiki
- Saídas persistidas:
  - markdown em `wiki/`
  - capítulos importados em `raw/books/`
  - `metadata.json`

## 2. Achados por severidade

### MEDIUM

#### M1. Conteúdo enviado ao provider externo pode incluir material sensível
- **Onde:** `kb compile`, `kb qa`, `kb heal`, `kb lint`
- **Risco:** qualquer documento em `raw/` ou pergunta/resposta processada por esses comandos pode ser transmitido ao provider configurado em `KB_BASE_URL`
- **Impacto:** vazamento operacional de conteúdo sensível se o usuário usar o sistema com documentos não sanitizados
- **Recomendação:** documentar regra explícita de classificação de conteúdo e criar checklist operacional antes de usar recursos LLM em material sensível

#### M2. Commits automáticos podem persistir conteúdo sensível gerado pela automação
- **Onde:** `compile`, `heal`, `qa --file-back`
- **Risco:** a wiki recebe commits automáticos sem etapa intermediária de revisão humana
- **Impacto:** dificuldade maior para evitar que conteúdo indevido entre no histórico do repositório
- **Recomendação:** avaliar modo opcional sem commit automático ou procedimento operacional obrigatório de revisão antes de sincronizar repositório

### LOW

#### L1. Não há auditoria automatizada de dependências/CVEs no sprint fechado
- **Onde:** baseline do projeto
- **Risco:** vulnerabilidades em dependências Python podem passar despercebidas
- **Recomendação:** adicionar `pip-audit`/processo equivalente em ciclo futuro ou rodar checagem periódica manual

#### L2. Compat layer de `book2md` ainda depende de fallback por path
- **Onde:** repositório `projects/book2md`
- **Risco:** acoplamento operacional pode levar a carregamento inesperado em layouts alternativos
- **Recomendação:** formalizar dependência explícita ou pacote compartilhado quando a distribuição externa passar a importar

## 3. Gestão de secrets

- `.env` está em `.gitignore`, o que reduz o risco de versionamento acidental da chave
- `.env.example` não contém segredo real
- A aplicação depende de `KB_API_KEY` para recursos LLM e usa `python-dotenv` para carregar o ambiente
- **Observação:** a chave precisa continuar fora de logs, commits e documentação operacional

## 4. Deps com vulnerabilidades conhecidas

- Não houve consulta a base de CVEs nem execução de ferramenta dedicada neste fechamento
- **Status:** sem evidência de vulnerabilidade conhecida a partir desta auditoria offline
- **Próximo passo recomendado:** rodar ferramenta específica de auditoria de dependências em ciclo futuro

## 5. CI/CD e automações

- Não há pipeline de CI/CD analisado neste sprint
- Automação principal é o commit automático da wiki via git local
- O comportamento de commit automático é útil para rastreabilidade, mas reforça o achado M2 quando o conteúdo é sensível

## 6. Recomendações priorizadas

1. **Definir política operacional para conteúdo sensível** antes de promover uso real com provider externo
2. **Decidir se commits automáticos precisam de modo opt-out** em cenários sensíveis
3. **Executar smoke test real com OpenCode Go** para validar UX e mensagens de falha do subsistema LLM opcional
4. **Planejar auditoria periódica de dependências** com ferramenta dedicada
5. **Formalizar a integração `book2md` → `kb`** quando a distribuição externa deixar de ser mono-workspace

## 7. Próximos passos

- Abrir item de trabalho para política de segurança operacional do provider externo
- Abrir item de trabalho para avaliar `no-commit`/`dry-run` nos fluxos que escrevem na wiki
- Em ciclo futuro, considerar `upgrade-deps` ou processo equivalente se a auditoria de dependências apontar risco

**Veredito geral:** sem achados CRITICAL/HIGH no escopo auditado, mas com dois pontos MEDIUM que merecem tratamento antes de ampliar uso com dados reais.
