# PLAN — Infra alignment phase 1

## Objetivo técnico

Fechar três débitos estruturais com o menor delta possível e sem alterar a superfície de CLI.

## Estratégia

1. Versionamento

- mover a versão canônica para `kb/__init__.py`
- configurar Hatch para ler a versão dinamicamente
- adicionar teste de contrato contra `CHANGELOG.md`

2. Taxonomia configurável

- introduzir `KB_TOPICS` em `kb.config`
- fornecer helpers para validação, prompt e diretório wiki
- trocar usos diretos em `compile.py` e `qa.py`
- atualizar `.env.example` e docs afetadas

3. Desacoplamento do importador

- extrair o pipeline PDF/OCR para `kb/book_import_pdf.py`
- manter `kb.book_import_core` como fachada compatível para helpers já usados pelos testes
- validar mensagens de erro e comportamento com a suíte existente

## Riscos

- drift documental se `docs/API.md` e `docs/architecture/ARCHITECTURE.md` não forem atualizados junto
- regressão silenciosa se `_get_pdf_pages` perder semântica de fechamento de documento

## Fora de escopo

- refatorar parsing EPUB/TOC em módulos dedicados
- adicionar comando `kb version`
- introduzir persistência de tópicos em `kb_state/`
