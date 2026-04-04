# Política de Segurança — kb

## Versões Suportadas

| Versão        | Suporte de Segurança |
| ------------- | -------------------- |
| Latest (main) | ✅ Ativa             |
| < 1.0         | ❌ Não suportado     |

Apenas a branch principal (`main`) recebe atualizações de segurança.

---

## Como Reportar Vulnerabilidades

**Não abra issues públicas** para vulnerabilidades de segurança.

Envie um email para **security@kb-project.dev** ou abra uma [GitHub Security Advisory](https://github.com/wendeus0/LLM-knowledge-base/security/advisories/new) com:

- Descrição da vulnerabilidade
- Passos para reproduzir (PoC se possível)
- Impacto estimado
- Versão afetada

Você receberá uma resposta em até 72 horas.

---

## Medidas de Segurança Implementadas

### Parsing de XML Seguro (EPUB)

O projeto usa `defusedxml` para parsing de arquivos EPUB, prevenindo:

- XML External Entity (XXE) attacks
- Billion Laughs / XML bomb attacks
- Entity expansion attacks

### Validação de Modelos OpenCode Go

O cliente LLM valida o modelo solicitado contra a lista de modelos disponíveis na API OpenCode Go, prevenindo:

- Model injection
- Uso de modelos não autorizados
- Custos inesperados

### Execução de Código

- **O LLM nunca executa código** — apenas gera e edita arquivos Markdown
- Não há `exec()`, `eval()` ou `subprocess` com input do LLM
- O código Python do projeto é estático e auditável

### Sanitização de Filenames

Todos os caminhos de arquivo são sanitizados antes de uso:

- Remoção de path traversal (`../`, `..\\`)
- Restrição ao diretório de trabalho do projeto
- Validação de caracteres permitidos

### Gerenciamento de API Keys

- API key **exclusivamente via arquivo `.env`**
- Nunca hardcoded no código
- Nunca committed ao repositório
- `.env` está no `.gitignore`

---

## Dependências Auditáveis

```
defusedxml>=0.7       # XML parsing seguro
typer>=0.12           # CLI framework
rich>=13.0.0          # Terminal UI
python-dotenv>=1.0.0  # Env file loading
openai>=1.0.0         # LLM client (opcional)
```

### Verificação de vulnerabilidades

```bash
pip install safety
safety check
```

---

## Boas Práticas para Usuários

1. **Mantenha o `.env` seguro** — não compartilhe, não commit
2. **Use a API key com permissões mínimas** — apenas para leitura/escrita necessária
3. **Revogue a key se suspeitar de vazamento**
4. **Não execute `kb` com sudo/root** — rode com permissões de usuário normal
5. **Mantenha as dependências atualizadas**: `pip install -e . --upgrade`
6. **Audite o código antes de rodar** — o projeto é pequeno e legível
7. **Não ingestione arquivos de fontes não confiáveis** sem inspeção manual
8. **Use `--allow-sensitive` apenas com consciência** — essa flag autoriza explicitamente o envio do conteúdo sinalizado ao provider externo
9. **Use `--no-commit` em experimentos ou material sensível** quando quiser persistir localmente sem gravar histórico git imediato

---

## Limitações Conhecidas

### Processamento de Conteúdo

- O kb **não valida o conteúdo semântico** dos documentos processados
- Documentos maliciosos em `raw/` podem conter payloads (mas o kb não os executa)
- A sanitização foca em paths e XML — não em conteúdo markdown gerado
- Flags como `--allow-sensitive` reduzem a proteção operacional por execução; devem ser usadas apenas quando o usuário entende o risco

### Dependências Externas

- A API OpenCode Go está fora do controle deste projeto
- Vulnerabilidades nas dependências Python devem ser reportadas aos respectivos projetos

### Escopo de Ameaças

- O kb é uma ferramenta local — não expõe serviços de rede
- O vetor de ataque principal é via arquivos de entrada maliciosos
- Não há proteção contra DoS por arquivos extremamente grandes (limitado por memória disponível)

---

## Atualizações

Esta política é revisada a cada release. Última atualização: 2026-04-04.
