import importlib


def _reload_config(monkeypatch, raw_topics=None):
    if raw_topics is None:
        monkeypatch.delenv("KB_TOPICS", raising=False)
    else:
        monkeypatch.setenv("KB_TOPICS", raw_topics)
    import kb.config as config

    return importlib.reload(config)


def test_should_use_default_topics_when_env_is_absent(monkeypatch):
    config = _reload_config(monkeypatch)

    assert config.TOPICS == ["cybersecurity", "ai", "python", "typescript"]
    assert (
        config.topic_prompt_options()
        == "cybersecurity, ai, python, typescript, general"
    )


def test_should_normalize_and_deduplicate_topics_from_env(monkeypatch):
    config = _reload_config(monkeypatch, " ML Ops , ai,ml-ops,general,AI ")

    assert config.TOPICS == ["ml-ops", "ai"]
    assert config.is_supported_topic("ml-ops") is True
    assert config.is_supported_topic("ML Ops") is True
    assert config.canonical_topic(" ML Ops ") == "ml-ops"
    assert config.is_supported_topic("general") is False


def test_should_resolve_wiki_dir_with_canonical_topic_name(monkeypatch, tmp_path):
    monkeypatch.setenv("KB_TOPICS", "ML Ops")
    monkeypatch.setenv("KB_WIKI_DIR", str(tmp_path / "wiki"))
    config = _reload_config(monkeypatch, "ML Ops")

    assert config.wiki_topic_dir("ML Ops") == config.WIKI_DIR / "ml-ops"


def test_should_fallback_to_default_topics_when_env_has_no_valid_entries(monkeypatch):
    config = _reload_config(monkeypatch, " , general , !!! ")

    assert config.TOPICS == config.DEFAULT_TOPICS
