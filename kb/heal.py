"""Stochastic heal — pega N arquivos aleatórios, encontra conexões, corrige, stampa."""

import random
import re
from datetime import datetime
from pathlib import Path
from kb.client import chat
from kb.config import WIKI_DIR
from kb.git import commit
from kb.guardrails import assert_safe_for_provider

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


def heal(
    n: int = 10, allow_sensitive: bool = False, no_commit: bool = True
) -> list[dict]:
    """Processa N arquivos aleatórios da wiki. Retorna log de ações."""
    candidates = [p for p in WIKI_DIR.rglob("*.md") if p.name != "_index.md"]
    if not candidates:
        return []

    sample = random.sample(candidates, min(n, len(candidates)))
    log: list[dict] = []
    changed: list[Path] = []

    for path in sample:
        text = path.read_text(encoding="utf-8", errors="replace")

        if _is_stub(text):
            path.unlink()
            log.append({"file": path.name, "action": "deleted_stub"})
            continue

        assert_safe_for_provider(
            text, source=f"heal:{path.name}", allow_sensitive=allow_sensitive
        )

        response = chat(
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": text},
            ]
        )

        if response.strip() == "NO_CHANGES":
            stamped = _stamp_reviewed(text)
            if stamped != text:
                path.write_text(stamped, encoding="utf-8")
                changed.append(path)
            log.append({"file": path.name, "action": "reviewed_no_changes"})
        else:
            stamped = _stamp_reviewed(response)
            path.write_text(stamped, encoding="utf-8")
            changed.append(path)
            log.append({"file": path.name, "action": "healed"})

    if changed and not no_commit:
        commit(f"chore(heal): stochastic heal ({len(changed)} files)", changed)

    return log
