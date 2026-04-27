# ARTIFACT_POLICY.md — Política de Artefatos

## Princípio

Artefatos gerados automaticamente (cache, build, test reports) não devem ser versionados no repositório.

## Artefatos Ignorados

### Python

| Padrão           | Descrição                   |
| ---------------- | --------------------------- |
| `__pycache__/`   | Bytecode Python             |
| `*.py[cod]`      | Arquivos compilados         |
| `*$py.class`     | Classes compiladas          |
| `.pytest_cache/` | Cache de testes             |
| `.coverage`      | Cobertura de testes         |
| `htmlcov/`       | Relatório HTML de cobertura |
| `.mypy_cache/`   | Cache do mypy               |
| `.ruff_cache/`   | Cache do ruff               |

### Build/Distribuição

| Padrão        | Descrição           |
| ------------- | ------------------- |
| `build/`      | Build artifacts     |
| `dist/`       | Distribuição        |
| `*.egg-info/` | Metadados de pacote |
| `*.egg`       | Pacote egg          |
| `*.whl`       | Wheel packages      |

### Ambiente

| Padrão   | Descrição                                   |
| -------- | ------------------------------------------- |
| `.venv/` | Virtual environment                         |
| `venv/`  | Virtual environment                         |
| `.env`   | Variáveis de ambiente (exceto .env.example) |

## Regras

1. **Nunca** commite `__pycache__/`, `.pyc`, ou arquivos de cache
2. **Nunca** commite `dist/` ou `build/`
3. **Nunca** commite relatórios de cobertura (use CI artifacts)
4. **Sempre** verifique `git status` antes de commitar
5. **Sempre** mantenha `.gitignore` atualizado

## Checklist Pre-commit

```bash
# Verifique se não há artefatos acidentalmente staged
git status

# Se houver, remova:
git rm -r --cached __pycache__/
git rm -r --cached .pytest_cache/
```

## Exceções

Nenhuma exceção permanente. Em casos excepcionais:

1. Discutir na issue/PR
2. Documentar motivo no commit message
3. Reverter assim que possível

## Verificação

```bash
# Verificar se .gitignore está completo
git check-ignore -v __pycache__/test.cpython-311.pyc

# Deve retornar o arquivo .gitignore e a linha correspondente
```
