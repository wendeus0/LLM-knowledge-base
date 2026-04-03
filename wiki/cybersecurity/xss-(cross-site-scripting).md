```
---
title: XSS (Cross-Site Scripting)
topic: cybersecurity
tags: [xss, vulnerabilidade-web, owasp, segurança-cliente, injeção]
source: test_xss.md
---

# XSS (Cross-Site Scripting)

**XSS** ([[Cross-Site Scripting]]) é uma [[Vulnerabilidade]] de segurança [[Web]] que permite a atacantes injetar scripts maliciosos em páginas visualizadas por outros usuários. O código é executado no navegador da vítima no contexto de confiança do site legítimo, violando a política de mesma origem ([[Same-Origin Policy]]).

A vulnerabilidade ocorre quando aplicações não [[Sanitização de Entrada|sanitizam adequadamente]] dados fornecidos por usuários antes de incluí-los nas páginas HTML retornadas.

## Tipos de XSS

### XSS Refletido (Reflected)
O código malicioso é enviado ao servidor (geralmente via parâmetros [[URL]] ou formulários) e "refletido" imediatamente na resposta [[HTTP]] sem persistência. Requer engenharia social para induzir a vítima a clicar em um link manipulado.

### XSS Armazenado (Stored)
O payload malicioso é persistido permanentemente no [[Banco de Dados]] ou armazenamento do servidor (ex: comentários, posts, perfis de usuário). Executado automaticamente para todos os usuários que acessam a página contaminada, sem necessidade de interação específica.

### XSS Baseado em DOM (DOM-based)
A vulnerabilidade reside inteiramente no código [[JavaScript]] cliente. O aplicativo utiliza dados não confiáveis de `window.location`, `document.referrer` ou outras fontes para manipular o [[DOM]] dinamicamente, sem validação adequada.

## Impactos e Riscos

Um atacante explorando XSS pode:

- **Sequestro de sessão**: Roubar [[Cookies de Sessão]] para impersonificação ([[Session Hijacking]])
- **[[CSRF]] forçado**: Executar ações não autorizadas em nome do usuário autenticado
- **[[Defacement]]**: Modificar conteúdo visível da página
- **Phishing**: Redirecionar para sites maliciosos ou coletar credenciais
- **Keylogging**: Registrar digitações do usuário na página
- **Instalação de malware**: Explorar vulnerabilidades do navegador

## Estratégias de Prevenção

### Sanitização e Validação
- **Escapar output**: Converter caracteres especiais (`<`, `>`, `"`, `'`, `&`) em entidades HTML antes da renderização
- **Validação rigorosa**: Aceitar apenas dados conforme padrões esperados (whitelist)
- **Codificação contextual**: Aplicar escaping apropriado para HTML, JavaScript, CSS ou URL

### Frameworks e Bibliotecas
[[React]], [[Vue.js]], [[Angular]] e frameworks modernos aplicam escaping automático por padrão através de templates seguros, desde que não se use `dangerouslySetInnerHTML` ou equivalentes sem sanitização.

### Content Security Policy (CSP)
Implementar cabeçalho [[Content Security Policy]] para restringir origens de scripts executáveis, bloqueando inline-scripts não autorizados e eval().

### Proteção de Cookies
Marcar cookies sensíveis com flag `HttpOnly` para impedir acesso via JavaScript, mitigando roubo de sessão mesmo em presença de XSS.

### Arquitetura Segura
- Validar todas as entradas no [[Backend]] — nunca confiar em validação client-side
- Adotar arquitetura [[Zero Trust]] para dados externos
- Implementar [[Subresource Integrity]] (SRI) para prevenir manipulação de scripts third-party

## Conceitos Relacionados
- [[OWASP Top 10]]
- [[Sanitização de Entrada]]
- [[Content Security Policy]]
- [[HTTP-only Cookies]]
- [[DOM]]
- [[CSRF]]
- [[Injeção de Código]]
- [[Same-Origin Policy]]
- [[Segurança de Aplicações Web]]
```