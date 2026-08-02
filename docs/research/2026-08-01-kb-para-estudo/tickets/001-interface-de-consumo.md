# Qual é a interface de consumo, e de qual projeto OSS ela parte?

Type: grilling
Status: open
Blocks: 003 (o que é "artigo bom" depende de como é lido)

## Question

O usuário quer uma **interface própria** para consumir o material de estudo, reaproveitando front-end de projeto open source com licença permissiva — não codar do zero. Citou `rowboatlabs/rowboat` e pediu uma varredura mais ampla de projetos "que emulem o Obsidian".

### Pontos a fechar

- **O que a interface precisa fazer**, no mínimo, para o estudo dele: ler artigo, navegar wikilink, buscar, ver grafo, fazer pergunta ao kb de dentro dela? Cada um desses muda o candidato.
- **Onde ela roda**: local (o vault está em disco), ou publicada em algum lugar? Isso decide entre SSG e app com backend.
- ~~**Licença aceitável**~~ **RESOLVIDO (2026-08-01): o uso é privado.** Sem distribuição, AGPL/GPL não geram obrigação prática — a trava só aparece ao compartilhar o link. Isso reabre o **Flowershow** (AGPL, Next.js) como candidato técnico, que passa a ser a alternativa ao Quartz no lugar do WebObsidian: troca o risco de "1 contribuidor, auth não auditada" por projeto com comunidade. Não muda o favorito — o Quartz já era MIT e ganha por mérito. Descarte seco continua valendo para Anytype, Outline e MagmaGlass, que não são open source.
- **Fronteira com o kb**: a interface só *lê* a wiki, ou também dispara `kb qa` / `kb ingest`? Se dispara, precisa de um backend HTTP que o kb hoje não tem.
- **O que acontece com o Obsidian** — some, coexiste, ou a interface nova é para outra coisa?

## Evidência

Varredura de candidatos com licença verificada em `../frontends-oss.md` (pesquisa de 2026-08-01).

Restrição técnica conhecida: o vault usa frontmatter YAML (`title`, `topic`, `tags`, `source`) e wikilinks `[[assim]]`. Qualquer candidato que exija importar para banco próprio quebra o modelo "o markdown em disco é a fonte da verdade" que o projeto adotou.

## Answer

<!-- preencher no grilling -->
