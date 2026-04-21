# PLAN — Archive: mover artigos stale/órfãos para archive/

**Branch:** feat/006-kb-archive
**Data:** 2026-04-21
**Spec:** features/006-kb-archive/SPEC.md
**MVP scope:** critérios [P1] da SPEC

## Contexto técnico

| Campo                   | Valor                                                               |
| ----------------------- | ------------------------------------------------------------------- |
| Linguagem/versão        | Python 3.11+                                                        |
| Dependências principais | typer, rich, pytest                                                 |
| Storage                 | filesystem (JSON/markdown em KB_DATA_DIR)                           |
| Estratégia de testes    | unitário com tmp_path + monkeypatch; integration via TyperCliRunner |
| Plataforma alvo         | Linux / WSL / macOS                                                 |
| Tipo de projeto         | CLI Python com engine de KB                                         |
| Constraints             | Nunca deletar conteúdo; preservar estrutura relativa; offline       |

## Arquitetura escolhida

Novo módulo `kb/archive.py` expõe funções puras de filtro e movimentação, sem side effects de I/O além de filesystem. A camada de CLI em `kb/cli.py` adiciona comando `archive` que orquestra preview (dry-run) ou execução.

Componentes:

- `kb/config.py` — novo `ARCHIVE_DIR = DATA_DIR / "archive"`
- `kb/archive.py` — funções: `collect_candidates`, `move_to_archive`, `render_preview_table`
- `kb/cli.py` — novo `@app.command() def archive(...)`
- `tests/unit/test_archive.py` — testes de filtro e movimentação
- `tests/integration/test_archive_cli.py` — teste end-to-end do comando Typer

## Decisões técnicas

**Decisão:** Usar `shutil.move` em vez de `Path.rename`. **Motivo:** `rename` falha entre filesystems; `move` é robusto para `KB_DATA_DIR` em mounts distintos.

**Decisão:** Backlinks calculados por regex simples `\[\[(.*?)\]\]` em todos os `.md` de `wiki/`, sem depender de parser de markdown completo. **Motivo:** O projeto já usa wikilinks nesse formato; adicionar dependência de parser aumentaria bundle sem ganho prático.

**Decisão:** `--stale` usa `stale_pct` global como proxy de dias de inatividade. **Motivo:** O stats não expõe stale por artigo; converter o percentual em threshold de dias é aproximação aceitável e desbloqueia o requisito sem alterar o modelo de dados.

**Decisão:** `archive/` não é versionado por padrão; comando não expõe `--commit`. **Motivo:** Operação é puramente de manutenção do corpus; versionar moves de arquivos gera noise no histórico git. Se necessário, o usuário versiona manualmente.

**Decisão:** Preview em dry-run usa `rich.table.Table` com colunas: Arquivo, Motivo, Destino. **Motivo:** Alinhado com padrão de tabelas já usado em `import-book` e `stats`.

## Constitution check

- Separação engine/corpus: `archive.py` opera apenas em `KB_DATA_DIR`, nunca no repo. OK.
- `--commit` omitido: justificado na decisão técnica; não quebra contratos existentes porque é comando novo. OK.
- Nenhuma alteração manual em wiki/: movimentação é via engine. OK.

## Dependências entre componentes

1. `config.py` (ARCHIVE_DIR) deve existir antes de `archive.py`
2. `archive.py` deve existir antes da adição do comando em `cli.py`
3. Testes unitários podem ser escritos paralelamente ao CLI
