# Direção visual — plataforma de estudos

> Referência enviada pelo usuário em 2026-08-02: "Ensina Dev". Duas instruções dele, nesta ordem: **foca no visual, não no conteúdo** — e depois: **não se apega à paleta deles**.
>
> **O que a referência é:** norte de *arquitetura de informação* — onde ficam os temas e o artigo dentro de uma trilha. Não é norte de pele.

## Layout

```
┌──────────────────────────────────────────────────────────┐
│  logo   Início  Roadmaps  Trilhas  Simulados  ...        │  nav superior
├───────────────┬──────────────────────────────────────────┤
│ TRILHA        │   breadcrumb                             │
│ progresso     │                                          │
│ ▓▓▓░░ 29%     │   H1 do artigo                           │
│               │   ──────────                             │
│ MÓDULO 1      │                                          │
│  ✅ aula       │   H2 seção                               │
│  ✅ aula       │   prosa com medida de linha curta        │
│ MÓDULO 2      │                                          │
│  🔵 aula atual │   ┌────────────────────┐                 │
│  ⚪ aula       │   │ ● ● ●  bloco de    │                 │
│               │   │        código      │                 │
└───────────────┴──────────────────────────────────────────┘
```

- **Sidebar de trilha** é a navegação primária, não o grafo. Módulos em caixa-alta pequena e cinza; aulas com estado por círculo (verde concluído, azul preenchido na atual, vazio no não-visto). Item atual ganha pílula de fundo claro.
- **Conteúdo em cartão branco** sobre o fundo, com respiro generoso. Breadcrumb acima do H1; H1 com filete abaixo.
- **Bloco de código com cromo de janela** (três pontos coloridos). Código inline em pílula clara.

## Paleta — direção do usuário, não da referência

**Dois temas, ambos obrigatórios.** O usuário declarou preferência por **dark com laranja**, e que no claro **bege é melhor que branco**.

| | Claro | Escuro |
|---|---|---|
| Fundo | bege — não branco puro | escuro |
| Superfície | um degrau acima do fundo | um degrau acima do fundo |
| Acento | a definir | **laranja** |
| Estado | verde só para "concluído" | idem |

O azul da referência **não se aplica** — era a marca deles. A tipografia (sans arredondada, entrelinha generosa, medida curta) e a sensação de material didático calmo permanecem, porque são sobre legibilidade em leitura longa, não sobre identidade.

O front pode divergir bastante da referência. O que se preserva dela é o **layout**: sidebar de trilha com progresso à esquerda, artigo como superfície de leitura à direita.

## O que isso decide no produto

1. **A trilha é a espinha da tela de leitura, não um extra.** A sidebar da fase 1 (F2) já nasce com o formato que o roadmap da fase 2 vai preencher — mesmo que na fase 1 ela liste só "artigos do topic atual".
2. **Progresso é visível o tempo todo**, não uma tela separada. Reforça a decisão de guardar estado em banco próprio (F3).
3. **O grafo de wikilinks não é a navegação primária.** Continua útil como visão lateral, mas não disputa espaço com a trilha — o que reduz a urgência da ilha de `cytoscape`.
4. **Leitura confortável é requisito, não polimento.** Medida de linha, entrelinha e contraste entram no critério de aceite da F2.

## Antes de codar a F2

Rodar a skill `visual-direction` do harness com esta referência para fechar tokens concretos (escala tipográfica, espaçamento, cores em hex) em vez de adjetivos. E `ui-critique` contra a tela renderizada — afirmação sobre UI exige tela, não leitura de componente.
