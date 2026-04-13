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

# Ou usar o atalho local
make install-dev

# Configurar
cp .env.example .env
# Editar .env com KB_API_KEY
```

## Governança obrigatória (SDD + TDD)

Antes de qualquer mudança não trivial, é obrigatório seguir esta ordem de leitura:

1. `CONTEXT.md`
2. `docs/architecture/SDD.md`
3. `docs/architecture/TDD.md`
4. `docs/architecture/SPEC_FORMAT.md`
5. `features/<feature>/SPEC.md` (quando houver feature em foco)

Regra de precedência em caso de conflito:

- `features/<feature>/SPEC.md` governa comportamento da feature
- `docs/architecture/SDD.md` governa arquitetura e evolução
- `docs/architecture/TDD.md` governa estratégia de testes
- `docs/architecture/SPEC_FORMAT.md` governa formato e completude da SPEC
- `CONTEXT.md` governa contexto macro e limites de escopo

Fluxo obrigatório de execução:

SPEC -> TEST_RED -> CODE_GREEN -> REFACTOR -> VALIDATE -> REPORT

Sem SPEC estável e validável, não prossiga para implementação.

## Workflow de Contribuição

### 1. Issues

- Verifique se já existe uma issue relacionada
- Use os templates em `.github/ISSUE_TEMPLATE/`:
  - `Bug report` para comportamento incorreto reproduzível
  - `Feature request` para mudanças de comportamento/escopo que podem evoluir para SPEC
  - `Operational task` para governança, documentação, hygiene e manutenção operacional
- Não abra issue pública para vulnerabilidades; siga `SECURITY.md`

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

1. **Criar SPEC obrigatoriamente** em `features/<nome>/SPEC.md` (use `features/_template/SPEC.md` como base)
2. **Validar SPEC** seguindo `docs/architecture/SPEC_FORMAT.md`
3. **Executar TEST_RED** antes do código de produção
4. **Implementar mínimo para GREEN**
5. **Refatorar sem alterar comportamento**
6. **Atualizar SPEC e evidências** para refletir o escopo real entregue
7. **Abrir/atualizar ADR** em `docs/adr/` se houver decisão arquitetural durável

#### Para bugs

1. **Reproduzir** com teste
2. **Corrigir** com teste passando
3. **Não quebrar** testes existentes

### 4. Commits

Os comandos do produto que escrevem no corpus do usuário agora operam em modo local por padrão. Use `--commit` apenas quando quiser versionar aquela execução específica.

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

# Atalhos parciais para lint/test
make lint
make test
make check                 # cobre ruff + pytest, mas não substitui kb lint
```

### 6. Pull Request

Use o template obrigatório em `.github/pull_request_template.md`.

Requisitos mínimos de aprovação da PR:

- referência explícita da SPEC (`features/<feature>/SPEC.md`)
- referência de ADR quando aplicável (`docs/adr/...`) ou justificativa de não aplicabilidade
- evidências objetivas de TEST_RED/GREEN, testes e lint
- rastreabilidade documental completa (SPEC/ADR/README/CONTRIBUTING quando impactados)

## Definition of Done (documental obrigatório)

Uma mudança só está pronta quando TODOS os itens abaixo estiverem atendidos:

- [ ] Existe SPEC em `features/<feature>/SPEC.md` para toda mudança não trivial ou que altere comportamento/contrato; exceções apenas para ajustes estritamente triviais (typo/comentário/cosmético sem impacto funcional) com justificativa explícita na PR
- [ ] Quando houver SPEC aplicável, ela contém requisitos testáveis e está alinhada ao código final
- [ ] Quando houver SPEC aplicável, testes (unit/integration quando aplicável) cobrem os requisitos da SPEC
- [ ] Em mudança arquitetural durável, ADR criada/atualizada em `docs/adr/`
- [ ] PR referencia SPEC e ADR (ou justificativa objetiva de não aplicabilidade)
- [ ] Evidências de validação (comandos/saídas) foram registradas no PR
- [ ] README/CONTRIBUTING/docs impactados foram atualizados quando necessário

Qualquer implementação sem lastro documental (SPEC/ADR/evidências) é considerada incompleta e não deve ser aceita.

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
