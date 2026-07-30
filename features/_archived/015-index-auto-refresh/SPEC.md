---
title: Índice de embeddings acompanha as escritas na wiki
epic: search
status: done
pr:
---

# Índice de embeddings acompanha as escritas na wiki

## Objetivo

Hoje o índice de embeddings só muda quando alguém roda `kb index build` à mão. Todo artigo compilado, curado pelo `heal` ou arquivado por `qa --to-wiki` fica **invisível ao canal semântico** até que esse comando seja lembrado — o REPORT de 012 registrou isso como dívida ("rodar `kb index build` manual ou acoplar a um job").

O efeito é silencioso e cumulativo: a busca continua respondendo, com um corpus semântico cada vez mais defasado em relação ao real. Um artigo recém-compilado sobre o assunto exato da pergunta simplesmente não concorre.

O índice deve acompanhar a wiki por padrão, de forma incremental e barata, degradando quando o servidor de embeddings não estiver disponível.

Fatia 2 da Fase 1 do roadmap revisado. Depende da 014, que entregou detecção de servidor e degradação visível.

## Requisitos funcionais

- [x] RF-01: ao fim de `kb compile`, os artigos escritos no lote entram no índice de embeddings sem comando adicional
- [x] RF-02: ao fim de `kb heal`, artigos reescritos são reindexados e artigos removidos saem do índice
- [x] RF-03: `kb qa --to-wiki` reindexa o artigo arquivado
- [x] RF-04: o refresh é incremental — só o que mudou de hash é re-embedado; corpus inalterado não gera nenhuma chamada ao servidor
- [x] RF-05: `--no-index-refresh` desliga o refresh no comando atual; `KB_INDEX_AUTO_REFRESH=0` desliga por padrão no ambiente — **entregue parcialmente:** a flag existe em `compile` e `heal`; em `qa --to-wiki` o controle é apenas pela env var (ver REPORT)
- [x] RF-06: servidor de embeddings indisponível não faz o comando falhar — o refresh é pulado com aviso, e o comando principal conclui normalmente
- [x] RF-07: o refresh reporta o que fez (indexados, removidos) na saída do comando que o disparou

## Requisitos técnicos

- Reusa `build_index` da 012, que já é incremental por hash — nenhuma lógica de diff nova
- Reusa `ensure_server`/`probe` da 014 para decidir se há servidor antes de tentar; sem servidor, pula sem exceção
- Um único ponto de entrada (`refresh_embeddings_index`) chamado pelos comandos; **não** confundir com `update_index` de `kb/compile.py:60`, que regenera `wiki/_index.md` markdown
- Refresh acontece **uma vez ao fim do lote**, não por artigo — compilar 100 capítulos faz uma varredura, não cem
- Nenhuma chamada de rede em teste: `build_index` e o probe já são monkeypatcháveis
- Falha do refresh nunca propaga para o comando principal

## Mudanças de API/CLI

- `kb compile`, `kb heal`, `kb qa --to-wiki`: nova flag `--no-index-refresh`
- Nova env var: `KB_INDEX_AUTO_REFRESH` (default ligado)
- Saída dos comandos ganha uma linha de resultado do refresh quando ele roda

## Testes

- Unit: `refresh_embeddings_index` pulando quando desabilitado por flag e por env; pulando quando servidor inacessível; propagando o relatório de `build_index`; engolindo exceção do build sem quebrar o chamador
- Integration (sem rede, embedder e probe mockados): `compile` reindexando o artigo novo; `heal` removendo do índice o artigo apagado; `qa --to-wiki` reindexando; `--no-index-refresh` não tocando o índice; corpus inalterado gerando zero chamadas ao embedder
- Manual: compilar um documento no vault real e confirmar que ele aparece na busca semântica sem `kb index build`

## Dados de contexto

| Chave | Valor |
|-------|-------|
| Estimativa | 3–5h |
| Bloqueador | não |
| Risk | baixa-média (toca o caminho de escrita de três comandos; mitigado por nunca propagar falha) |

## Dependências

- Feature 012 (índice incremental) e 014 (detecção de servidor)

## Notas

**Fora de escopo:**
- Reindexação disparada por mudança feita fora da CLI (edição direta no Obsidian) — continua exigindo `kb index build`; detecção por watcher é outra feature
- Job agendado de reindexação (candidato a entrada em `kb/jobs.py`, fatia própria)
- Mudar a granularidade do índice (chunking é a 017)

**Casos de erro:**
- Servidor fora → refresh pulado com aviso; o comando principal conclui com sucesso
- Falha inesperada no build → capturada, reportada como aviso, comando principal conclui
- Índice de outro modelo → `build_index` já trata rebuild; o refresh não decide isso sozinho

**Open questions:**
- (nenhuma)
