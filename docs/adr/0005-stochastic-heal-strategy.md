# ADR 0005 — Estratégia de Stochastic Heal

- **Status:** Aceito
- **Data:** 2026-04-04

## Contexto

O projeto `kb` mantém uma wiki em markdown que cresce organicamente conforme novos documentos são ingeridos e compilados. Com o tempo, o vault pode atingir centenas ou milhares de arquivos. Executar operações de manutenção (heal) em todo o vault de forma determinística apresenta desafios:

- **Tempo de execução:** Processar todos os arquivos em cada execução é inviável para vaults grandes
- **Bloqueio:** Operações longas impedem o uso iterativo da ferramenta
- **Custo LLM:** Cada arquivo processado pelo heal pode requerer chamadas ao LLM

A manutenção da wiki envolve verificar links quebrados, identificar stubs (artigos vazios), atualizar timestamps de revisão e corrigir inconsistências de formatação.

## Decisão

1. Adotar **heal estocástico** (amostragem aleatória) como estratégia padrão de manutenção.
2. Implementar parâmetro `--n` para controlar a quantidade de arquivos processados por execução.
3. Selecionar arquivos aleatoriamente do vault a cada invocação do comando `kb heal`.
4. Complementar com comando `kb lint` para verificação completa quando necessário.

## Consequências

### Positivas

- **Escalabilidade:** Funciona eficientemente independentemente do tamanho do vault
- **Não bloqueante:** Execuções rápidas permitem uso iterativo durante o workflow
- **Custo controlado:** Limite explícito de processamento via parâmetro `--n`
- **Cobertura estatística:** Com execuções regulares, todos os arquivos têm chance de serem revisados
- **UX fluida:** Desenvolvedor pode rodar `kb heal` frequentemente sem esperar

### Negativas

- **Não garante 100% de cobertura:** Arquivos específicos podem não ser revisados por longos períodos
- **Risco de artigos não revisados:** Problemas em arquivos podem persistir se a sorte não os selecionar
- **Não-determinístico:** Dificulta reproduzir exatamente a mesma execução
- **Requer disciplina:** Benefícios dependem de execuções regulares do comando

## Alternativas consideradas

### A1. Processar todos os arquivos

- **Rejeitada.** Para vaults grandes, o tempo de execução torna-se proibitivo. Cada execução consumiria recursos excessivos de LLM e tempo de CPU, desencorajando o uso frequente da ferramenta.

### A2. Priorizar por idade (mais antigos primeiro)

- **Rejeitada.** Embora garanta que todos os arquivos sejam eventualmente revisados, cria uma fila rígida que ignora arquivos recentemente modificados que podem ter problemas introduzidos. Também sofre do mesmo problema de escala para o início da fila.

### A3. Priorizar por acesso (menos acessados primeiro)

- **Rejeitada.** Requer tracking de acesso aos arquivos, adicionando complexidade ao sistema. O benefício marginal não justifica a complexidade adicional de manter métricas de acesso.

### A4. Heal estocástico com pesos

- **Considerada e diferida.** Poderíamos usar pesos (ex: arquivos mais antigos têm maior probabilidade) mas isso adiciona complexidade sem resolver o problema fundamental de escala. Mantemos a versão simples (uniforme) até evidência de necessidade.

## Complementaridade com lint

O comando `kb lint` oferece verificação completa do vault sem processamento via LLM:

- **Lint:** Análise sintática rápida (links quebrados, frontmatter inválido, stubs)
- **Heal:** Processamento semântico via LLM (melhorias de conteúdo, correções contextuais)

Esta separação permite:

1. Rodar `kb lint` para verificação completa e barata
2. Rodar `kb heal --n 10` frequentemente para manutenção profunda amostrada
3. Usar `kb heal --n N` maior quando necessário (ex: após migração massiva)

## Justificativa técnica

A estratégia estocástica foi escolhida por equilibrar eficiência e eficácia:

1. **Lei dos grandes números:** Com execuções regulares e vault grande, a cobertura estatística aproxima-se de uniformidade

2. **UX iterativa:** Desenvolvedores podem integrar `kb heal` ao workflow diário sem fricção

3. **Custo previsível:** O parâmetro `--n` torna o custo de LLM constante independente do tamanho do vault

4. **Simplicidade:** Não requer índices complexos, tracking de estado ou heurísticas de priorização

5. **Resiliência:** Falhas em uma execução afetam apenas a amostra atual, não o vault inteiro

## Parâmetros recomendados

- **Uso diário:** `kb heal --n 10` — rápido, barato, mantém o vault saudável
- **Uso semanal:** `kb heal --n 50` — revisão mais profunda
- **Pós-migração:** `kb heal --n 100` — maior amostra após mudanças massivas
- **Verificação completa:** `kb lint` — análise sintática de todo o vault
