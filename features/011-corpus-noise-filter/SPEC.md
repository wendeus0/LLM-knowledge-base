---
title: Corte de ruído de corpus — filtro na importação + limpeza retroativa
epic: infra
status: in_progress
pr:
---

# Corte de ruído de corpus — filtro na importação + limpeza retroativa

## Objetivo

Hoje o `import-book` traz TODOS os capítulos do livro para `raw/` e o compile os transforma em artigos — inclusive agradecimentos, dedicatórias, prefácios, elogios e correlatos, que poluem a base de texto e a busca (prefácios já aparecem com frequência no vault atual). O sistema deve excluir capítulos-ruído na importação por default e oferecer limpeza retroativa do corpus já ingerido, sem nunca deletar conteúdo (arquivar, não apagar).

Fatia 1 do roadmap grillado em `DOMAIN.md` (mesma pasta) — decisões 4 e 12, invariante "nenhum capítulo-ruído entra em raw/ sem override explícito".

## Requisitos funcionais

- [x] RF-01: `import-book` classifica cada capítulo como conteúdo ou ruído e, por default, NÃO escreve capítulos-ruído em `raw/`; ao final, reporta a lista do que foi excluído e por qual categoria
- [x] RF-02: flag de override (`--keep-noise`) importa tudo, preservando o comportamento atual; override é registrado no `metadata.json` do livro
- [x] RF-03: taxonomia de ruído configurável — defaults versionados na engine (agradecimentos, dedicatória, prefácio, prólogo editorial, elogios/praise, encerramento = epílogo/posfácio/"palavras finais" — **Conclusão/Considerações finais NÃO entram**, colofão, sobre o autor, copyright, índice remissivo — PT e EN), com override por vault (`kb.toml`, alinhado ao RF-05 da feature 010)
- [x] RF-04: título ambíguo (não bate com a taxonomia com confiança) → capítulo é MANTIDO e listado no relatório como "não classificado" — na dúvida, nunca descartar conteúdo silenciosamente
- [x] RF-05: comando retroativo em modo dry-run por default: varre `raw/` (e os artigos de `wiki/` derivados desses capítulos, via rastro do `metadata.json`) e lista os candidatos a ruído com categoria e caminho, sem alterar nada
- [x] RF-06: modo apply do comando retroativo move os candidatos para `archive/` (nunca deleta), com escrita atômica, backup consistente com a rede de segurança do healing, e commit controlado por `--commit` (padrão do repo, ADR-0016)
- [x] RF-07: reexecução do retroativo sobre corpus já limpo é no-op (idempotente) — relatório indica "0 candidatos"

## Requisitos técnicos

- Classificação v1 é **heurística por título** (match normalizado contra a taxonomia, case/acento-insensível, PT+EN) — sem LLM no caminho default; classificação assistida por modelo local pequeno fica para iteração futura (ver Notas)
- A taxonomia default vive versionada na engine (constante/arquivo de dados), override por vault em `kb.toml` — nunca hardcoded espalhada
- O retroativo reutiliza o mecanismo existente de `archive` (mover + log), não cria um segundo caminho de arquivamento
- Separação engine × corpus preservada: o comando opera no vault apontado por `KB_DATA_DIR`, nada é gravado no repo da engine
- Capítulos excluídos na importação são registrados no `metadata.json` do livro (título, categoria, motivo) — trilha auditável do que ficou de fora

## Mudanças de API/CLI

- `kb import-book <arquivo>`: novo comportamento default (exclui ruído) — **breaking em relação ao comportamento atual**; `--keep-noise` restaura o comportamento antigo
- Novo comando: `kb noise scan` (dry-run, default) e `kb noise apply [--commit]` (retroativo)
- Nenhuma mudança em `compile`, `qa`, `search`

## Testes

- Unit: classificador de títulos — casos PT (Agradecimentos, Dedicatória, Prefácio, Elogios, Sobre o autor), EN (Acknowledgments, Preface, Foreword, Praise for..., About the Author, Colophon), ambíguos (mantidos), falsos-amigos que NÃO podem ser cortados (ex.: capítulo de conteúdo cujo título contém "preface" no meio de frase)
- Integration: importar EPUB fixture com capítulos-ruído → `raw/` sem os ruídos + relatório correto + `metadata.json` com trilha; reimportar com `--keep-noise` → tudo presente
- Integration: `kb noise scan` em vault fixture sujo → lista correta; `kb noise apply` → movidos para `archive/`, wiki íntegra, segunda execução no-op
- Manual: rodar `kb noise scan` no vault real do dono e revisar a lista antes do primeiro apply

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 8–12h |
| Bloqueador | não |
| Risk | média (breaking default no import-book; mitigado por --keep-noise e por arquivar em vez de deletar) |

## Dependências

- Nenhuma feature bloqueante. Interage com a 010 (multi-vault) apenas no ponto de config por vault (`kb.toml`) — se a 010 não estiver entregue, a taxonomia override cai para env var/default e o RF-03 registra o gap.

## Notas

**Fora de escopo (vão para features seguintes do roadmap, ver DOMAIN.md):**
- Retrieval semântico com embeddings Nomic (Fase 2 do ADR-0013) → feature 012
- Módulos paper/artigo robusto → feature posterior
- API HTTP + app visual → feature posterior
- Classificação de capítulos assistida por LLM local (para títulos criativos que a heurística não pega) — iteração futura desta mesma frente, depois de medir o miss rate da heurística no vault real

**Casos de erro:**
- Livro sem TOC/títulos de capítulo utilizáveis → nada é excluído; warning explica que a classificação não foi possível
- `kb noise apply` com conflito de nome no `archive/` → não sobrescreve; sufixa e registra no log de auditoria
- Falha no meio do apply → escrita atômica garante que nenhum arquivo fica meio-movido; reexecução retoma os restantes

**Open questions:**
- (nenhuma) — resolvida em 2026-07-15: "encerramento" na taxonomia default = epílogo, posfácio, "palavras finais" e elogios de fechamento; **Conclusão/Considerações finais são conteúdo e ficam** (decisão A do dono).
