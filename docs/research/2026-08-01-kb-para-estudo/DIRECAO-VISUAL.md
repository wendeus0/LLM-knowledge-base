# Direção visual — plataforma de estudos

> Referência enviada pelo usuário em 2026-08-02: "Ensina Dev". Instrução explícita: **foca no visual, não no conteúdo**.

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

## Paleta e tipografia

| Elemento | Direção |
|---|---|
| Fundo | creme/bege quente — leitura longa, não branco puro |
| Superfície | cartão branco, sombra sutil |
| Acento | azul, usado com parcimônia (link, item atual, marca) |
| Estado | verde só para "concluído" |
| Tipografia | sans arredondada, entrelinha generosa, medida curta |

Sem dark mode agressivo. A sensação é de material didático calmo, não de dashboard.

## O que isso decide no produto

1. **A trilha é a espinha da tela de leitura, não um extra.** A sidebar da fase 1 (F2) já nasce com o formato que o roadmap da fase 2 vai preencher — mesmo que na fase 1 ela liste só "artigos do topic atual".
2. **Progresso é visível o tempo todo**, não uma tela separada. Reforça a decisão de guardar estado em banco próprio (F3).
3. **O grafo de wikilinks não é a navegação primária.** Continua útil como visão lateral, mas não disputa espaço com a trilha — o que reduz a urgência da ilha de `cytoscape`.
4. **Leitura confortável é requisito, não polimento.** Medida de linha, entrelinha e contraste entram no critério de aceite da F2.

## Antes de codar a F2

Rodar a skill `visual-direction` do harness com esta referência para fechar tokens concretos (escala tipográfica, espaçamento, cores em hex) em vez de adjetivos. E `ui-critique` contra a tela renderizada — afirmação sobre UI exige tela, não leitura de componente.
