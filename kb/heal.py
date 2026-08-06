"""Stochastic heal — pega N arquivos aleatórios, encontra conexões, corrige, stampa."""

import random
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from kb.client import chat
from kb.config import WIKI_DIR
from kb.frontmatter import parse
from kb.fsutil import atomic_write_text
from kb.git import commit
from kb.guardrails import assert_safe_for_provider
from kb.sampling import params

SYSTEM = """Você é um editor de knowledge base. Dado um artigo em markdown:
1. Encontre conceitos mencionados sem [[wikilink]] e adicione-os
2. Remova seções vazias ou placeholders ("TODO", "Em breve", etc.)
3. Sugira 1-2 novos artigos que deveriam existir mas não existem (como comentário no final)
4. NÃO altere o conteúdo substantivo — apenas links e limpeza

Responda APENAS com o markdown corrigido, sem explicações.
Se não houver nada a corrigir, responda exatamente: NO_CHANGES
"""


def _is_stub(text: str) -> bool:
    """Artigo vazio ou só com frontmatter."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Remove frontmatter
    content_lines = []
    in_front = False
    for line in lines:
        if line == "---":
            in_front = not in_front
            continue
        if not in_front:
            content_lines.append(line)
    meaningful = [
        line for line in content_lines if not line.startswith("#") and len(line) > 10
    ]
    return len(meaningful) == 0


def _stamp_reviewed(text: str) -> str:
    """Adiciona ou atualiza reviewed_at no frontmatter."""
    now = datetime.now().strftime("%Y-%m-%d")
    if "reviewed_at:" in text:
        return re.sub(r"reviewed_at: .*", f"reviewed_at: {now}", text)
    return text.replace("---\n", f"---\nreviewed_at: {now}\n", 1)


def _backup(path):
    backup_dir = WIKI_DIR / ".heal_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_path = backup_dir / f"{path.parent.name}.{path.stem}.{ts}.md"
    shutil.copy2(path, backup_path)


def _is_valid_heal_output(original, response):
    original_meta, _ = parse(original)
    response_meta, _ = parse(response)

    if original_meta and not response_meta:
        return False
    if original_meta.get("title") and response_meta.get("title") != original_meta["title"]:
        return False
    if any(key != "reviewed_at" and key not in response_meta for key in original_meta):
        return False
    if len(response) < 0.5 * len(original):
        return False
    return True


def heal(
    n: int = 10,
    allow_sensitive: bool = False,
    no_commit: bool = True,
    index_refresh_enabled: bool = True,
) -> list[dict]:
    """Processa N arquivos aleatórios da wiki. Retorna log de ações."""
    from kb.fsutil import iter_articles

    candidates = list(iter_articles(WIKI_DIR))
    if not candidates:
        return []

    sample = random.sample(candidates, min(n, len(candidates)))
    log: list[dict] = []
    changed: list[Path] = []

    for path in sample:
        text = path.read_text(encoding="utf-8", errors="replace")

        if _is_stub(text):
            # V7 mínimo (029 C2): stub vai para archive/ com backup versionado,
            # nunca unlink — e o manifest deixa de apontar para o path movido.
            from kb.archive import move_to_archive
            from kb.config import ARCHIVE_DIR
            from kb.state import mark_archived

            dest = ARCHIVE_DIR / path.relative_to(WIKI_DIR)
            resultado = move_to_archive([{"source": path, "dest": dest}], ARCHIVE_DIR)
            if resultado and resultado[0]["action"] == "moved":
                try:
                    mark_archived(path)
                except Exception as exc:  # arquivo já se moveu; avisar > abortar
                    print(f"aviso: manifest não atualizado para {path.name} — {exc}", file=sys.stderr)
                log.append({"file": path.name, "action": "archived_stub"})
                # o --commit precisa versionar o move e o manifest, não só heals de texto
                changed.append(path)
                changed.append(dest)
                if "backup" in resultado[0]:
                    changed.append(Path(resultado[0]["backup"]))
                from kb.config import MANIFEST_PATH

                if MANIFEST_PATH.exists():
                    changed.append(MANIFEST_PATH)
            else:
                log.append({"file": path.name, "action": "archive_error"})
            continue

        assert_safe_for_provider(
            text, source=f"heal:{path.name}", allow_sensitive=allow_sensitive
        )

        response = chat(
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": text},
            ],
            # Editar sem inventar: o prompt proíbe alterar conteúdo substantivo.
            **params("analytical"),
        )

        if response.strip() == "NO_CHANGES":
            stamped = _stamp_reviewed(text)
            if stamped != text:
                _backup(path)
                atomic_write_text(path, stamped)
                changed.append(path)
            log.append({"file": path.name, "action": "reviewed_no_changes"})
        else:
            if not _is_valid_heal_output(text, response):
                log.append({"file": path.name, "action": "skipped_invalid_output"})
                continue
            stamped = _stamp_reviewed(response)
            _backup(path)
            atomic_write_text(path, stamped)
            changed.append(path)
            log.append({"file": path.name, "action": "healed"})

    if changed and not no_commit:
        commit(f"chore(heal): stochastic heal ({len(changed)} files)", changed)

    if log:
        from kb.embeddings import refresh_embeddings_index

        refresh_embeddings_index(enabled=index_refresh_enabled)

    return log
