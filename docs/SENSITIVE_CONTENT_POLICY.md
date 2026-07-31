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

## Fronteira de confiança do prompt (prompt injection)

Conteúdo de `raw/` e artigos de `wiki/` são dados de terceiro: entram no prompt do LLM em `compile` (raw → wiki) e em `qa` (wiki → resposta). Regra: **dado, nunca instrução**.

### Container delimitado

Todo conteúdo de terceiro vai dentro de um container com sentinela aleatória por chamada (`secrets.token_hex(6)`), gerado por `guardrails.new_sentinel()`:

```
<untrusted_document-9F3A21C0DE44>
...conteúdo do documento...
</untrusted_document-9F3A21C0DE44>
```

- **Por que sentinela aleatória:** um documento hostil não pode escrever a marca de fechamento se não sabe o valor dela. Delimitador fixo (```` ``` ```` ou tag constante) é adivinhável e já vaza no corpus — qualquer artigo sobre o próprio kb citaria a tag literal.
- **Neutralização de fuga:** antes de envolver, `wrap_untrusted()` escapa qualquer `<untrusted_document...>` presente no texto para `&lt;...&gt;` e remove ocorrências literais da sentinela. O container tem exatamente uma abertura e um fechamento.
- **Metadado fica fora:** nome do arquivo, rota de QA e contexto de capítulo ficam **antes** do container; só o texto de terceiro entra nele.
- **System prompt declara a regra:** `guardrails.untrusted_policy(sentinel)` acrescenta ao system prompt a cláusula que nomeia a sentinela e proíbe obedecer ao que estiver dentro; instrução embutida deve ser reportada como conteúdo, nunca executada.

### Detector `scan_injection`

`guardrails.scan_injection(texto)` reporta os padrões abaixo; `warn_on_injection(texto, source)` imprime aviso em stderr e devolve os achados.

| Label | O que pega |
|-------|-----------|
| `instruction_override` | "ignore/disregard/esqueça ... previous/anteriores ... instructions/instruções" |
| `role_hijack` | "you are now", "act as", "a partir de agora você é", "aja como" |
| `system_prompt_probe` | "system prompt", "reveal your instructions", "revele suas instruções" |
| `new_instructions` | "new/updated instructions", "novas instruções" |
| `container_escape` | `</untrusted_document...>`, `<\|im_end\|>`, `[/INST]`, `</system>` |
| `exfiltration` | `curl/wget https://`, "execute o comando", "send ... https://", "revele a api_key" |
| `image_exfiltration` | imagem markdown com URL contendo query string (`![x](https://host/p.png?d=...)`) |

### Por que avisar e não bloquear

Artigo didático sobre prompt injection cita literalmente as mesmas frases do ataque — o corpus real tem material de cybersecurity, então bloquear geraria falso positivo garantido e treinaria o operador a passar `--allow-*` por reflexo. A defesa que morde é estrutural (container + cláusula de system prompt), sempre ligada; o detector é sinal para o humano, não gate. Conteúdo sensível (credencial) continua abortando com `SensitiveContentError` — lá o falso positivo é raro e o dano de vazar é irreversível.

### Cobertura atual

Container e detector estão em `compile` (documento raw), `qa` (contexto recuperado) e no file-back de `qa`. `heal` e `lint` ainda montam prompt sem container.

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

### Job `discovery` — sem commit por padrão

O job `discovery` ingere da web e compila com LLM sem humano no caminho. Versionar isso automaticamente fecharia a cadeia web → raw → wiki → git sem nenhum ponto de revisão. Por isso o job roda com `no_commit=True`: os arquivos ficam locais e o output diz que há conteúdo aguardando revisão.

Para restaurar o commit automático (só faz sentido em vault descartável ou pipeline com revisão a jusante):

```bash
KB_DISCOVERY_AUTOCOMMIT=1 kb jobs run discovery
```

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
