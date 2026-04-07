# Política Operacional de Conteúdo Sensível

Última revisão: 2026-04-07

---

## Princípio

Controles de segurança e rastreabilidade são seguros por padrão. Escape hatch só com intenção explícita e local à execução.

Referência arquitetural: D11 (`memory/stable_decisions.md`).

---

## Guardrails automáticos

Antes de enviar qualquer conteúdo ao provider externo, `guardrails.py` verifica os seguintes padrões:

| Label | Padrão detectado |
|-------|-----------------|
| `api_key` | `api_key: <valor>` ou `sk-<token>` |
| `token` | `token: <8+ chars>` |
| `password` | `password: <qualquer>` |
| `secret` | `secret: <qualquer>` |
| `private_key` | `-----BEGIN ... PRIVATE KEY-----` |

Se detectado, o comando aborta com `SensitiveContentError` listando os achados redactados.

### Lacunas conhecidas (L2 do SECURITY_AUDIT_REPORT.md)

Os padrões atuais **não cobrem**:
- AWS access keys (`AKIA[A-Z0-9]{16}`)
- GitHub tokens (`ghp_`, `github_pat_`)
- GitLab tokens (`glpat-`)
- Bearer headers

Se seus documentos puderem conter credenciais desses formatos, não use `--allow-sensitive`.

---

## Flag `--allow-sensitive`

### O que faz

Suprime o `SensitiveContentError` e permite que o conteúdo sinalizado seja enviado ao provider externo.

### Quando é aceitável

- Documento é de domínio público (artigo técnico, paper, manual)
- O "falso positivo" foi confirmado manualmente (ex: `api_key` em contexto de tutorial, não credencial real)
- Você está rodando contra um provider **local** (Ollama, LM Studio) onde o conteúdo não sai da máquina

### Quando **não** usar

- Documento contém credenciais reais (mesmo que pareçam expiradas)
- Documento contém dados pessoais sensíveis (PII, saúde, financeiro)
- Você não inspecionou o conteúdo manualmente antes de rodar

### Comandos que aceitam a flag

```bash
kb compile --allow-sensitive
kb qa "pergunta" --allow-sensitive
kb heal --allow-sensitive
kb lint --allow-sensitive
```

---

## Flag `--no-commit`

### O que faz

Suprime o commit git automático após writes na wiki.

### Quando é aceitável

- Experimento temporário — você vai descartar o resultado
- Modo de inspeção — quer ver o output antes de commitar
- Material sensível que não deve ficar no histórico git

### Quando **não** usar

- Uso rotineiro de produção — commits automáticos são a rastreabilidade do sistema
- Múltiplas execuções seguidas sem commit — cria drift acumulado difícil de revisar

### Não há estado global

`--no-commit` age apenas na execução atual. Não existe configuração global persistente que desative commits. Isso é intencional (D11).

---

## Política por diretório (futura)

Há intenção de avaliar política automática por diretório (`raw/private/`), onde arquivos nesse path seriam tratados como sensíveis por default.

**Estado:** não implementado. Use `--allow-sensitive` com consciência enquanto essa política não existir.

---

## Combinação das duas flags

```bash
kb compile --allow-sensitive --no-commit
```

Caso de uso válido: processar documento com falso positivo de sensibilidade em sessão experimental sem commitar o resultado.

---

## Resumo de decisão rápida

| Situação | Ação |
|----------|------|
| Provider local (Ollama) | `--allow-sensitive` aceitável |
| Documento de domínio público com falso positivo confirmado | `--allow-sensitive` aceitável |
| Credenciais reais no documento | **Não use** — remova as credenciais primeiro |
| Experimento temporário | `--no-commit` aceitável |
| Produção rotineira | Nem uma nem outra flag |
