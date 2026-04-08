# Integração com Obsidian

O Obsidian é o frontend oficial recomendado para o `kb`, mas deve operar sobre o **vault/corpus do usuário**, não sobre o repositório principal da engine.

## Modelo recomendado

- **Repositório `kb`:** código, documentação, testes e exemplos neutros
- **`KB_DATA_DIR`:** diretório local do usuário contendo `raw/`, `wiki/`, `outputs/` e `kb_state/`
- **Obsidian:** aberto em `<KB_DATA_DIR>/wiki`

## Plugin adotado

A integração operacional recomendada usa o plugin community **obsidian-terminal**:

- Repositório: https://github.com/polyipseity/obsidian-terminal
- Objetivo: abrir um terminal real dentro do Obsidian para executar `kb search`, `kb lint`, `kb qa`, `kb compile` e `kb heal` sem depender de comandos fixos ou prompts artificiais.

## Por que `obsidian-terminal`

A abordagem com terminal integrado é a mais estável para este projeto porque:

- `kb qa` e `kb qa -f` exigem input dinâmico do usuário
- o plugin executa um shell real, evitando fragilidade de PATH e working directory
- a integração reaproveita o fluxo já validado no terminal local
- o vault do usuário continua desacoplado da engine

## Pré-requisitos

Na raiz do projeto:

```bash
cd <raiz-do-repositorio>
source .venv/bin/activate
pip install -e .
pip install -e ".[llm]"
```

Se quiser suporte de desenvolvimento:

```bash
pip install -e ".[dev]"
```

Configure `.env`:

```bash
KB_API_KEY=<sua-api-key>
KB_BASE_URL=https://opencode.ai/zen/go/v1
KB_MODEL=kimi-k2.5
KB_DATA_DIR=<caminho-absoluto-para-seu-llm-wiki>
```

Verifique:

```bash
./.venv/bin/kb --help
```

## Estrutura do vault/corpus

Dentro de `KB_DATA_DIR`, o `kb` usa:

```text
<KB_DATA_DIR>/
  raw/
  wiki/
  outputs/
  kb_state/
```

## Abrir o vault

No Obsidian, abra:

```text
<KB_DATA_DIR>/wiki
```

## Instalar o plugin

1. Settings → Community plugins
2. Procurar por `Terminal` / `obsidian-terminal`
3. Instalar e habilitar

## Configuração recomendada do profile

Criar um profile custom com estes valores:

- **Type:** `Integrated`
- **Executable:** `/bin/zsh` (ou `/bin/bash` se esse for seu shell principal)
- **Arguments:** `--login`
- **Linux:** habilitado
- **Python executable:** `python3`

### Observação sobre shell login

O argumento `--login` é importante para carregar o ambiente do shell corretamente.

## Alias recomendado no shell

Adicionar ao `~/.zshrc` ou `~/.bashrc`:

```bash
alias kb='<raiz-do-repositorio>/.venv/bin/kb'
```

Substitua `<raiz-do-repositorio>` pelo caminho absoluto do seu clone local.

Depois recarregue o shell:

```bash
source ~/.zshrc
```

ou

```bash
source ~/.bashrc
```

## Fluxo de uso no terminal integrado

Abra o terminal do plugin e rode na raiz do projeto:

```bash
cd <raiz-do-repositorio>
```

Validação mínima:

```bash
pwd
echo $KB_DATA_DIR
which kb
kb --help
```

Esperado:

- `pwd` aponta para a raiz do repositório
- `echo $KB_DATA_DIR` aponta para o diretório do seu vault/corpus
- `which kb` aponta para `<raiz-do-repositorio>/.venv/bin/kb`
- `kb --help` funciona

## Comandos principais

### Search

```bash
kb search "agent"
```

### Lint

```bash
kb lint --allow-sensitive
```

### QA

```bash
kb qa "Como implementar um orquestrador em meu workflow?" --allow-sensitive
```

### QA com file-back

```bash
kb qa "Explique multi-agent systems" -f --allow-sensitive --no-commit
```

### Compile

```bash
kb compile --allow-sensitive --no-commit

# Compilar apenas um livro já importado pelo nome
kb compile "Mathematics for Machine Learning" --allow-sensitive --no-commit

# Importar e compilar um PDF escaneado com OCR
kb import-book ~/Downloads/mathematics-for-ml.pdf --ocr --compile --allow-sensitive --no-commit
```

### Heal

```bash
kb heal --n 1 --allow-sensitive --no-commit
```

## Conteúdo sensível

Livros técnicos podem conter exemplos como `OPENAI_API_KEY` ou `api_key=...`, que hoje podem disparar falso positivo no guardrail.

Nesses casos, usar:

```bash
--allow-sensitive
```

Para política operacional completa, ver:

- `docs/SENSITIVE_CONTENT_POLICY.md`

## Resultado esperado da integração

Ao final da configuração:

- `<KB_DATA_DIR>/wiki` funciona como vault Obsidian
- o terminal integrado executa o CLI real do projeto
- `qa` e `qa -f` funcionam de forma interativa
- `qa -f` pode ser usado com `--no-commit` no fluxo recomendado via Obsidian
- não é necessário plugin nativo do `kb` nesta fase

## Status

Integração operacional validada em sessão real com `kb qa` executando dentro do Obsidian via `obsidian-terminal`.
