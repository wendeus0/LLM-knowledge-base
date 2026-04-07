# DATA_POLICY.md — Política de Dados

## Escopo

Define como dados são persistidos localmente pelo kb (CLI Python).

> **Nota de escopo:** `raw/`, `wiki/`, `outputs/` e `kb_state/` são diretórios do corpus do usuário. No modelo recomendado atual, eles vivem em `KB_DATA_DIR`, fora do repositório principal.

## Diretórios de Dados

### raw/

- **Conteúdo:** Documentos fonte não processados
- **Formato:** Markdown, texto, EPUB, PDF
- **Retenção:** Permanente até remoção explícita
- **Backup:** Versionado via Git

### wiki/

- **Conteúdo:** Markdown compilado, estruturado
- **Formato:** .md com frontmatter YAML
- **Retenção:** Permanente (histórico Git)
- **Backup:** Git é source of truth

### raw/books/

- **Conteúdo:** Livros importados (EPUB/PDF → capítulos)
- **Estrutura:** `raw/books/<livro>/chapters/`, `metadata.json`
- **Retenção:** Permanente
- **Nota:** Compilado para wiki/ via `kb compile`

## Políticas

### Versionamento

| Ação                | Comportamento                        |
| ------------------- | ------------------------------------ |
| `kb compile`        | Commit automático se houver mudanças |
| `kb heal`           | Commit automático após correções     |
| `kb qa --file-back` | Commit automático da resposta, salvo com `--no-commit` |
| Edição manual       | **Proibida** — apenas via CLI        |

### Limpeza

- Não remova arquivos manualmente de wiki/
- Use `kb` commands para operações estruturadas
- Para deleção em massa: discussão prévia necessária

### Espaço em Disco

- vaults grandes: use `kb heal --n 10` (stochastic)
- Limite de tamanho: monitorar wiki/ e raw/books/
- Política de arquivamento: a definir conforme crescimento

## Privacidade e Segurança

### Dados Sensíveis

- **Nunca** armazene em raw/ ou wiki/:
  - Senhas
  - API keys
  - Tokens de autenticação
  - Dados pessoais sensíveis

### .env

- `.env` deve estar em `.gitignore`
- `.env.example` pode ser versionado (sem valores reais)
- Variáveis obrigatórias: `KB_API_KEY`
- Variáveis opcionais: `KB_BASE_URL`, `KB_MODEL`

### LLM Data

- Conteúdo enviado ao LLM pode ser processado pelo provider
- Não envie dados confidenciais para `kb compile` ou `kb qa`
- Use local-only features (`kb import-book`) para dados sensíveis

## Migração e Backup

### Backup

```bash
# Backup completo do corpus do usuário
tar -czf kb-backup-$(date +%Y%m%d).tar.gz "${KB_DATA_DIR:?}"/

# Ou use Git no repositório do corpus, se existir
# git -C "${KB_DATA_DIR:?}" push origin main
```

### Migração

```bash
# Para novo ambiente
git clone <repo>
cd kb
pip install -e ".[llm]"
cp .env.example .env
# Editar .env com KB_API_KEY e KB_DATA_DIR
```

## Revisão

Revisar esta política quando:

- Adicionar backend/cloud sync
- Mudar estratégia de armazenamento
- Novos requisitos de compliance
