# CONTRIBUTING.md — Guia de Contribuição

## Bem-vindo

Obrigado por contribuir com o kb! Este documento orienta o processo de contribuição.

## Pré-requisitos

- Python 3.11+
- Git
- Conta OpenAI ou acesso ao OpenCode Go (para features LLM)

## Setup de Desenvolvimento

```bash
# Clone
git clone <repo-url>
cd kb

# Ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências
pip install -e ".[llm,dev]"

# Configurar
cp .env.example .env
# Editar .env com KB_API_KEY
```

## Workflow de Contribuição

### 1. Issues

- Verifique se já existe uma issue relacionada
- Crie issue com template: `[tipo] descrição breve`
- Tipos: `bug`, `feat`, `docs`, `refactor`

### 2. Branches

```bash
# Sempre a partir de main
git checkout main
git pull origin main

# Nomeação: <tipo>/<descrição-kebab-case>
git checkout -b feat/novo-comando
git checkout -b fix/corrige-lint
git checkout -b docs/atualiza-readme
```

### 3. Desenvolvimento

#### Para features novas

1. **Criar SPEC** em `docs/architecture/SPEC.md` ou `features/<nome>/SPEC.md`
2. **Validar SPEC** seguindo `docs/architecture/SPEC_FORMAT.md`
3. **Testes RED** antes do código
4. **Implementar** (GREEN)
5. **Refatorar**

#### Para bugs

1. **Reproduzir** com teste
2. **Corrigir** com teste passando
3. **Não quebrar** testes existentes

### 4. Commits

Formato: Conventional Commits

```
<type>(<scope>): <descrição>

[corpo opcional]

[footer opcional]
```

Tipos:

- `feat:` nova feature
- `fix:` correção de bug
- `docs:` documentação
- `refactor:` refatoração
- `test:` testes
- `chore:` manutenção

Exemplos:

```
feat(compile): adicionar suporte a múltiplos idiomas
fix(qa): corrigir truncamento de respostas longas
docs(readme): atualizar instruções de instalação
```

### 5. Pre-commit Checks

```bash
# Antes de commitar, rode:
ruff check kb              # Lint
python -m pytest           # Testes
kb lint                    # Health check da wiki (se aplicável)
```

### 6. Pull Request

Template do PR:

```markdown
## Resumo

Breve descrição da mudança

## Tipo

- [ ] Feature
- [ ] Bugfix
- [ ] Documentação
- [ ] Refatoração

## Checklist

- [ ] Testes passam
- [ ] Lint limpo
- [ ] Documentação atualizada (se necessário)
- [ ] SPEC aprovada (para features)

## Como testar

Passos para reproduzir/testar
```

## Convenções de Código

### Python

- **Nomenclatura:** snake_case funções/variáveis, PascalCase classes
- **Type hints:** opcional, exceto em `config.py` e `client.py`
- **Docstrings:** português para funções públicas
- **Comprimento:** max 88-100 caracteres por linha
- **Imports:** agrupar por stdlib, third-party, local

### Estrutura de Módulos

```python
# kb/modulo.py
"""Descrição curta do módulo."""

from __future__ import annotations

# stdlib
import os
from pathlib import Path

# third-party
import typer

# local
from kb.config import WIKI_DIR


def funcao_publica() -> None:
    """Descrição da função."""
    pass


def _funcao_privada() -> None:
    pass
```

## Testes

### Estrutura

```
tests/
├── unit/           # Testes unitários
├── integration/    # Testes de integração
├── fixtures/       # Dados de teste
└── conftest.py     # Fixtures compartilhadas
```

### Escrevendo Testes

```python
# tests/unit/test_modulo.py
def test_deve_comportar_quando_condicao():
    # Arrange
    entrada = "dado"

    # Act
    resultado = funcao(entrada)

    # Assert
    assert resultado == "esperado"
```

### Mock de LLM

```python
from unittest.mock import patch

def test_qa_com_mock(monkeypatch):
    monkeypatch.setattr("kb.qa.chat", lambda **kw: "Resposta mockada")
    resultado = answer("pergunta")
    assert "mockada" in resultado
```

## Documentação

### O que documentar

| Tipo        | Onde                                | Quando                      |
| ----------- | ----------------------------------- | --------------------------- |
| API pública | `docs/API.md`                       | Nova função/comando exposto |
| Arquitetura | `docs/architecture/ARCHITECTURE.md` | Mudança estrutural          |
| ADR         | `docs/adr/ADR-NNN-titulo.md`        | Decisão arquitetural        |
| Feature     | `features/<nome>/SPEC.md`           | Nova feature                |

### Como documentar

- Clareza > completude
- Exemplos de código
- Português para texto, inglês para código
- Atualizar se desatualizar

## Revisão de Código

Critérios de aprovação:

1. Testes passam
2. Lint limpo
3. Código segue convenções
4. Documentação coerente
5. Sem breaking changes não discutidos

## Comunidade

- Respeite o código de conduta
- Discuta grandes mudanças antes de implementar
- Pergunte em issues se tiver dúvidas

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob MIT.
