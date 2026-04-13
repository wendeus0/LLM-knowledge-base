import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("KB_DATA_DIR", ROOT)).expanduser()
RAW_DIR = Path(os.getenv("KB_RAW_DIR", DATA_DIR / "raw")).expanduser()
WIKI_DIR = Path(os.getenv("KB_WIKI_DIR", DATA_DIR / "wiki")).expanduser()
OUTPUTS_DIR = Path(os.getenv("KB_OUTPUTS_DIR", DATA_DIR / "outputs")).expanduser()
STATE_DIR = Path(os.getenv("KB_STATE_DIR", DATA_DIR / "kb_state")).expanduser()
KNOWLEDGE_PATH = STATE_DIR / "knowledge.json"
LEARNINGS_PATH = STATE_DIR / "learnings.json"
MANIFEST_PATH = STATE_DIR / "manifest.json"
CLAIMS_PATH = STATE_DIR / "claims.jsonl"

API_KEY = os.getenv("KB_API_KEY")
BASE_URL = os.getenv("KB_BASE_URL", "https://opencode.ai/zen/go/v1")
MODEL = os.getenv("KB_MODEL", "kimi-k2.5")

DEFAULT_TOPICS = ["cybersecurity", "ai", "python", "typescript"]


def normalize_topic(topic: str | None) -> str:
    if not topic:
        return ""
    normalized = re.sub(r"\s+", "-", topic.strip().lower())
    normalized = re.sub(r"[^a-z0-9-]", "", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized


def _parse_topics(raw: str | None) -> list[str]:
    if not raw:
        return DEFAULT_TOPICS.copy()
    topics: list[str] = []
    for candidate in raw.split(","):
        normalized = normalize_topic(candidate)
        if not normalized or normalized == "general" or normalized in topics:
            continue
        topics.append(normalized)
    return topics or DEFAULT_TOPICS.copy()


TOPICS = _parse_topics(os.getenv("KB_TOPICS"))


def is_supported_topic(topic: str) -> bool:
    return normalize_topic(topic) in TOPICS


def canonical_topic(topic: str | None) -> str:
    normalized = normalize_topic(topic)
    if normalized in TOPICS:
        return normalized
    return "general"


def topic_prompt_options() -> str:
    return ", ".join([*TOPICS, "general"])


def wiki_topic_dir(topic: str) -> Path:
    resolved = canonical_topic(topic)
    return WIKI_DIR / resolved if resolved != "general" else WIKI_DIR


WIKILINK_TRAVERSAL_DEPTH = 1
MAX_CONTEXT_TOKENS = 8000
