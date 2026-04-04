# SECURITY_AUDIT_REPORT.md

## Sprint fechado em 2026-04-03

## 1. Superfície de ataque mapeada

- CLI local exposta via comandos `ingest`, `import-book`, `compile`, `qa`, `heal`, `lint`, `search` e `jobs`
- Entradas principais:
  - arquivos locais em `raw/` e `raw/books/`
  - perguntas livres para `qa`
  - variáveis de ambiente `KB_API_KEY`, `KB_BASE_URL`, `KB_MODEL`
  - flags operacionais `--allow-sensitive` e `--no-commit`
- Integrações externas:
  - provider LLM OpenAI-compatible (default: OpenCode Go)
  - git local para commits automáticos da wiki
- Saídas persistidas:
  - markdown em `wiki/`
  - summaries em `wiki/summaries/`
  - estado em `kb_state/`
  - capítulos importados em `raw/books/`

## 2. Achados por severidade

### MEDIUM

#### M1. Política de classificação de conteúdo sensível ainda não está fechada
- **Onde:** `compile`, `qa`, `qa --file-back`, `heal`, `lint`
- **Risco:** embora agora exista bloqueio/opt-in explícito, ainda falta regra operacional completa dizendo o que pode ou não pode ser enviado ao provider externo
- **Impacto:** uso inconsistente das flags `--allow-sensitive` pode gerar exposição operacional indevida
- **Mitigação aplicada neste sprint:** guardrails em runtime + `--allow-sensitive` explícito
- **Próximo passo:** formalizar política por tipo de conteúdo e eventualmente por diretório

#### M2. `--no-commit` reduz rastreabilidade quando usado sem disciplina operacional
- **Onde:** `compile`, `qa --file-back`, `heal`, `import-book --compile`
- **Risco:** o conteúdo pode ser escrito localmente e permanecer fora do histórico git por mais tempo do que o desejável
- **Impacto:** auditoria e recuperação ficam menos robustas se a flag virar hábito em vez de exceção
- **Mitigação aplicada neste sprint:** comportamento continua opt-in e por execução
- **Próximo passo:** documentar claramente quando usar a flag e considerar logging local de execuções sensíveis/fuga de commit

### LOW

#### L1. Cobertura percentual formal ainda não é calculada no ambiente atual
- **Onde:** processo de qualidade do repositório
- **Risco:** regressões de cobertura podem passar despercebidas apesar da suíte funcional estar saudável
- **Recomendação:** adicionar `pytest-cov`/`coverage.py` em ciclo futuro

#### L2. Compat layer de `book2md` ainda depende de fallback por path em parte do workspace ampliado
- **Onde:** integração `book2md` → `kb`
- **Risco:** acoplamento operacional e comportamento inesperado em layouts alternativos
- **Recomendação:** formalizar dependência explícita ou pacote compartilhado quando sair do mono-workspace

## 3. Gestão de secrets

- `.env` continua fora do versionamento
- `.env.example` permanece sem segredos reais
- `KB_API_KEY` segue obrigatório apenas para recursos LLM
- a política de guardrails reduziu risco de envio acidental, mas não substitui classificação humana do conteúdo

## 4. Dependências e supply chain

- não houve auditoria automatizada de CVEs neste fechamento
- **Status:** sem evidência de vulnerabilidade conhecida a partir desta auditoria offline
- **Próximo passo recomendado:** rodar `pip-audit` ou equivalente em ciclo futuro

## 5. Veredito

- **Sem achados CRITICAL/HIGH** no escopo do sprint
- o sprint **melhorou a postura de segurança** ao introduzir guardrails explícitos e controle `--no-commit`
- ainda restam **dois pontos MEDIUM** de política operacional, não de falha técnica imediata

## 6. Recomendações priorizadas

1. fechar política operacional de conteúdo sensível
2. documentar padrão de uso de `--no-commit` como exceção operacional
3. executar smoke test real com OpenCode Go
4. adicionar ferramenta de cobertura e auditoria de dependências
5. formalizar a integração `book2md` → `kb` no próximo ciclo apropriado
