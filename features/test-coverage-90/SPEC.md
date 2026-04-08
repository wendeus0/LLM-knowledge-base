---
title: Aumentar cobertura de testes para 90%
epic: infra
status: approved
pr:
---

# Aumentar Cobertura de Testes para 90%

## Objetivo

A cobertura atual da suíte é 78%, com gaps significativos em `kb/git.py` (31%), `kb/cli.py` (60%), `kb/book_import_core.py` (68%) e `kb/client.py` (68%). Esta feature eleva a cobertura geral para 90%+ cobrindo branches de erro, fallbacks e fluxos pouco exercitados.

## Requisitos funcionais

- [ ] `kb/git.py` atinge ≥90% de cobertura (commits automáticos, tratamento de erro)
- [ ] `kb/cli.py` atinge ≥90% de cobertura (paths de erro, comandos heal/lint/jobs)
- [ ] `kb/book_import_core.py` atinge ≥90% de cobertura (fallbacks de TOC/assets/PDF)
- [ ] `kb/client.py` atinge ≥90% de cobertura (validações e paths de erro do provider)
- [ ] Cobertura total da suíte ≥90%
- [ ] Todos os 140 testes existentes continuam passando

## Requisitos técnicos

- Usar mocks para isolar I/O externo (git, provider LLM, filesystem)
- Manter testes determinísticos — sem randomização ou timing real
- Preservar compatibilidade com pytest-cov para relatórios
- Não alterar comportamento do código de produção — apenas adicionar testes

## Testes

- Unit: Testes para linhas não cobertas em `git.py`, `cli.py`, `book_import_core.py`, `client.py`
- Integration: Validar que comandos CLI completos funcionam com novos testes
- Manual: Executar `python -m pytest --cov=kb` e verificar ≥90% total

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 1 dia |
| Bloqueador | não   |
| Risk       | baixo |

## Dependências

- baseline estável com 140 testes passando

## Notas

### Casos de erro

- Falha em comando git → tratamento de exceção coberto
- Provider retorna erro/resposta inválida → validação coberta
- Arquivo PDF/EPUB corrompido → fallback coberto
- CLI recebe argumentos inválidos → mensagem de erro coberta

### Fora de escopo

- Refatoração de código de produção (apenas adicionar testes)
- Mudanças em comportamento ou API pública
- Testes de performance ou carga

### Prioridade por módulo

1. `kb/git.py` (31% → 90%) — maior gap, testes de integração de commit
2. `kb/cli.py` (60% → 90%) — commands heal, lint, jobs, paths de erro
3. `kb/book_import_core.py` (68% → 90%) — fallbacks PDF/EPUB, TOC, assets
4. `kb/client.py` (68% → 90%) — validações de modelo, tratamento de erro
