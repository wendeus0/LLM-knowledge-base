---
title: Archive — Mover artigos stale/órfãos para archive/
epic: infra
status: draft
---

# Archive — Mover artigos stale/órfãos para archive/

## Objetivo

Quando a wiki cresce, artigos não revisitados ou sem links de entrada acumulam ruído. O comando `kb archive` permite mover esses artigos de `wiki/` para `archive/` de forma reversível, preservando o conteúdo e oferecendo preview antes da ação.

## Requisitos funcionais

- [P1] `kb archive` sem flags move artigos órfãos (zero backlinks na wiki) para `archive/`
- [P1] `kb archive --older-than N` move artigos cujo mtime seja anterior a `N` dias atrás
- [P1] `kb archive --dry-run` exibe tabela de preview com Rich sem mover arquivos
- [P2] `kb archive --stale` move artigos cuja idade em dias (mtime) exceda o valor numérico de `stale_pct` reportado pelo stats (proxy: percentual tratado como dias de inatividade)
- [P1] `--dry-run` mostra colunas: arquivo, motivo (orphan/stale/older-than), destino
- [P1] Movimentação preserva estrutura de diretórios relativa a `wiki/` dentro de `archive/`
- [P1] Nenhum arquivo é deletado; apenas movido de `wiki/` → `archive/`
- [P2] Arquivos já existentes em `archive/` com mesmo path relativo são sobrescritos silenciosamente

## Success criteria

- Comando `kb archive --dry-run` executa em <1s para wiki com até 500 artigos
- 100% dos artigos identificados como órfãos são movidos corretamente para `archive/` preservando path relativo
- Zero perda de conteúdo (nenhum delete, apenas move)
- Cobertura de testes do novo módulo `archive` >= 90%

## Requisitos técnicos

- Diretório `archive/` derivado de `KB_DATA_DIR/archive` (novo path em `config.py`)
- Backlinks calculados a partir de wikilinks `[[Nome]]` encontrados em todos os `.md` de `wiki/`
- Stale threshold lido via `kb.analytics.health.get_health_summary()["stale_pct"]`
- Idade do arquivo medida via `path.stat().st_mtime`
- Preview renderizado com `rich.table.Table`
- Movimentação via `path.rename()` ou `shutil.move()`

## Mudanças de API/CLI

Novo comando:

```
kb archive [--stale] [--older-than N] [--dry-run]
```

- Sem flags: filtra órfãos (zero backlinks)
- `--stale`: filtra artigos com stale_pct acima do threshold global
- `--older-than N`: filtra artigos com mtime > N dias
- Flags podem ser combinadas (OR lógico): artigo é arquivado se atender a qualquer critério ativo
- `--dry-run`: preview sem mover; exit 0
- Sem `--dry-run`: move os arquivos e exibe resumo da operação

## Testes

- Unit: `test_archive_moves_orphans` — wiki com 3 artigos, 1 órfão, confirma movimento
- Unit: `test_archive_stale_uses_threshold` — mock de health summary com stale_pct=30, artigo com stale_pct=35 é movido
- Unit: `test_archive_older_than` — artigo com mtime de 10 dias atrás, `--older-than 5` move
- Unit: `test_archive_dry_run_no_move` — `--dry-run` não altera filesystem
- Unit: `test_archive_preserves_structure` — `wiki/topic/foo.md` → `archive/topic/foo.md`
- Integration: `test_archive_cli_end_to_end` — invoca via Typer, verifica tabela de preview

## Dados de contexto

| Chave      | Valor |
| ---------- | ----- |
| Estimativa | 4h    |
| Bloqueador | não   |
| Risk       | baixa |

## Dependências

- `kb.analytics.health` (get_health_summary)
- `kb.config` (WIKI_DIR + novo ARCHIVE_DIR)
- `rich` (tabelas)

## Casos de erro

- Wiki vazia ou inexistente → exibe mensagem de erro e exit 1
- `--older-than N` com N <= 0 → exibe erro de validação e exit 1
- Falha de permissão ao mover arquivo → loga o arquivo como falha e continua com os demais

## Open questions

- (nenhuma)

## Notas

- Orphan detection reaproveita lógica de wikilink parsing existente se houver; caso contrário, regex simples `\[\[(.*?)\]\]` é suficiente.
- `--stale` usa `stale_pct` como proxy de dias porque o stats não expõe stale por artigo individualmente.
- `kb archive` não possui `--commit` nesta versão; archive/ é operacional e não versionado por padrão.
