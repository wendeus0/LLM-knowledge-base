# ADR 0002 — Typer como framework CLI

- **Status:** Aceito
- **Data:** 2026-04-04

## Contexto

O projeto `kb` é uma CLI tool que precisa oferecer comandos como `ingest`, `import-book`, `compile`, `qa`, `search`, `heal` e `lint`. A experiência do desenvolvedor na CLI é parte essencial do produto — comandos devem ser intuitivos, com help gerado automaticamente, e argumentos/opções bem documentados.

Sem um framework estruturado para CLI, o projeto correria risco de:

- parsing manual de argumentos com comportamento inconsistente
- código boilerplate excessivo para help e validação
- dificuldade de manutenção conforme o número de comandos crescesse

## Decisão

1. Adotar **Typer** como framework CLI principal para o projeto `kb`.
2. Organizar comandos em `kb/cli.py` com definições em funções decoradas.
3. Usar type hints para definir tipos de argumentos e opções.
4. Manter a estrutura modular: cada comando delega para seu módulo especializado (`ingest`, `compile`, `qa`, etc.).
5. Aproveitar a integração com Rich para output formatado no terminal.

## Consequências

### Positivas

- Geração automática de help e documentação de comandos
- Validação de tipos integrada via type hints do Python
- Redução significativa de boilerplate comparado a Click puro ou argparse
- Experiência de desenvolvimento moderna com autocomplete para IDEs
- Saída colorida e formatada automaticamente via Rich
- Comunidade ativa e documentação abrangente

### Negativas

- Dependência adicional no projeto (Typer + Click subjacente)
- Abstração pode limitar customizações avançadas de parsing
- Overhead de import para scripts simples (não aplicável neste projeto)
- Curva de aprendizado para quem conhece apenas Click puro

## Alternativas consideradas

### A1. Click puro

- **Rejeitada.** Typer é construído sobre Click e oferece a mesma funcionalidade com menos código. A produtividade do desenvolvedor é superior com Typer devido ao uso de type hints e menos boilerplate.

### A2. argparse (biblioteca padrão)

- **Rejeitada.** Embora não adicione dependências externas, requer significativamente mais código para atingir a mesma qualidade de CLI (help automático, validação de tipos, subcomandos). O custo de manutenção supera o benefício de zero dependências.

### A3. Python Fire

- **Rejeitada.** Fire converte funções Python em CLI automaticamente, mas oferece menos controle sobre a interface (nomes de opções, help text, validação). A CLI resultante é menos polida e profissional para um produto de linha de comando.

## Justificativa técnica

Typer foi escolhido por equilibrar simplicidade e poder:

1. **Type hints como documentação:** A assinatura da função define tanto a interface Python quanto a CLI, eliminando duplicação.

2. **Ecosistema Click:** Como Typer usa Click internamente, herda estabilidade, extensibilidade e integração com outras ferramentas.

3. **Rich integrado:** O suporte nativo a Rich proporciona UX superior no terminal sem esforço adicional.

4. **Produtividade:** O time de desenvolvimento (neste caso, o mantenedor solo) pode adicionar novos comandos rapidamente sem preocupação com parsing manual.

5. **Escalabilidade:** A estrutura de subcomandos do Typer escala naturalmente conforme o projeto cresce em funcionalidades.
