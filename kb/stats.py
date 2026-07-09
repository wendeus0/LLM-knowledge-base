"""Agregação de métricas para o comando stats."""


def _is_ignored_article(path, wiki_dir):
    rel = path.relative_to(wiki_dir)
    if path.name == "_index.md":
        return True
    return "summaries" in rel.parts or ".heal_backup" in rel.parts


def _topic_for(path, wiki_dir):
    rel = path.relative_to(wiki_dir)
    if len(rel.parts) <= 1:
        return "general"
    return rel.parts[0]


def get_article_summary():
    """Conta artigos compilados na wiki por tópico."""
    import kb.config as _config

    wiki_dir = _config.WIKI_DIR
    if not wiki_dir.exists():
        return {"total": 0, "by_topic": {}}

    by_topic = {}
    total = 0
    for path in wiki_dir.rglob("*.md"):
        if _is_ignored_article(path, wiki_dir):
            continue
        topic = _topic_for(path, wiki_dir)
        by_topic[topic] = by_topic.get(topic, 0) + 1
        total += 1

    return {"total": total, "by_topic": dict(sorted(by_topic.items()))}


def collect_stats():
    """Agrega métricas de claims, histórico de comandos e artigos."""
    from kb.analytics.health import get_health_summary
    from kb.analytics.history import get_history_summary

    return {
        "claims": get_health_summary(),
        "history_7d": get_history_summary(days=7),
        "articles": get_article_summary(),
    }
