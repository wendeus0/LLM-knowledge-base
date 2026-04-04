# Guia de Deploy — kb

Documento de instalação e configuração do projeto kb.

---

## 1. Requisitos de Sistema

| Componente                | Versão | Obrigatório              |
| ------------------------- | ------ | ------------------------ |
| Python                    | 3.11+  | Sim                      |
| Git                       | 2.30+  | Sim                      |
| API Key (OpenAI/OpenCode) | —      | Apenas para LLM features |

### Verificação rápida

```bash
python --version   # Deve ser 3.11 ou superior
git --version      # Deve ser 2.30 ou superior
```

---

## 2. Instalação Local

### Clone do repositório

```bash
git clone <repositorio>
cd kb
```

### Instalação base (sem LLM)

```bash
pip install -e .
```

Isso instala:

- CLI `kb` com comandos: `ingest`, `import-book`, `compile`, `search`
- Dependências: Typer, Rich

---

## 3. Instalação com Features LLM

Para usar Q&A, heal e lint (que requerem chamadas a LLM):

```bash
pip install -e ".[llm]"
```

Isso instala adicionalmente:

- OpenAI SDK
- Comandos extras: `qa`, `heal`, `lint`

---

## 4. Configuração do Ambiente

Crie o arquivo `.env` na raiz do projeto:

```bash
# .env
KB_API_KEY=sua-api-key-aqui
```

A API key é necessária apenas para comandos LLM:

- `kb qa`
- `kb heal`
- `kb lint`

Comandos não-LLM funcionam sem a key.

---

## 5. Verificação da Instalação

### Teste base

```bash
kb --help
```

Deve exibir a lista de comandos disponíveis.

### Teste com feature LLM

```bash
kb qa "teste" --help
```

Deve exibir o help do comando `qa`.

### Teste funcional

```bash
# Crie um arquivo de teste
echo "Teste de documento" > /tmp/teste.md

# Ingest
kb ingest /tmp/teste.md

# Compile
kb compile

# Search
kb search "teste"
```

---

## 6. Troubleshooting

### Erro: `command not found: kb`

**Causa:** Script não está no PATH ou instalação falhou.

**Solução:**

```bash
# Verifique se instalou
pip list | grep kb

# Reinstale
pip install -e .

# Ou execute via python
python -m kb --help
```

### Erro: `No module named 'openai'`

**Causa:** Tentando usar comandos LLM sem instalar as dependências extras.

**Solução:**

```bash
pip install -e ".[llm]"
```

### Erro: `KB_API_KEY not found`

**Causa:** Variável de ambiente não configurada.

**Solução:**

```bash
# Verifique se .env existe
cat .env

# Ou exporte diretamente
export KB_API_KEY=sua-api-key
```

### Erro: `Permission denied` no Git

**Causa:** Usuário não tem permissão para fazer commits.

**Solução:**

```bash
# Configure git
git config user.email "seu@email.com"
git config user.name "Seu Nome"
```

### Erro: Python version

**Causa:** Python < 3.11

**Solução:** Use pyenv ou atualize o Python:

```bash
# Com pyenv
pyenv install 3.11
pyenv local 3.11
```

---

## 7. Atualização

### Atualização do código

```bash
git pull origin main
pip install -e .  # ou ".[llm]" se usar features LLM
```

### Limpeza e reinstalação

```bash
pip uninstall kb
pip cache purge
pip install -e ".[llm]"
```

---

## Resumo Rápido

```bash
# 1. Clone e entre no diretório
git clone <repo> && cd kb

# 2. Instale com LLM
pip install -e ".[llm]"

# 3. Configure API key
echo "KB_API_KEY=sua-key" > .env

# 4. Verifique
kb --help
kb qa "teste de instalação"
```
