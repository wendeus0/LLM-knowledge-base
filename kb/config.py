import math
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
ARCHIVE_DIR = Path(os.getenv("KB_ARCHIVE_DIR", DATA_DIR / "archive")).expanduser()
STATE_DIR = Path(os.getenv("KB_STATE_DIR", DATA_DIR / "kb_state")).expanduser()
KNOWLEDGE_PATH = STATE_DIR / "knowledge.json"
LEARNINGS_PATH = STATE_DIR / "learnings.json"
MANIFEST_PATH = STATE_DIR / "manifest.json"
CLAIMS_PATH = STATE_DIR / "claims.jsonl"
AUDIT_PATH = STATE_DIR / "audit.jsonl"

API_KEY = os.getenv("KB_API_KEY", "local")
BASE_URL = os.getenv("KB_BASE_URL", "http://localhost:8081/v1")
MODEL = os.getenv("KB_MODEL", "bonsai-27b-1bit")

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


QA_DOC_CHARS_DEFAULT = 4000

# Profundidade medida no golden de 152 casos: ordenar 20 candidatos elevou o MRR
# de 0,242 para 0,343. O ganho vem de buscar fundo e entregar poucos — por isso
# vale nos perfis de top_k baixo, não só nos deep.
RERANK_DEPTH_DEFAULT = 20

RETRIEVAL_PROFILES = {
    "fast": {"top_k": 3, "doc_chars": 4000, "traverse": True, "traversal_budget": 1500, "rerank_depth": RERANK_DEPTH_DEFAULT},
    "deep": {"top_k": 5, "doc_chars": 8000, "traverse": True, "traversal_budget": 4000, "rerank_depth": RERANK_DEPTH_DEFAULT},
    "paper": {"top_k": 3, "doc_chars": 4000, "traverse": False, "traversal_budget": 0, "rerank_depth": RERANK_DEPTH_DEFAULT},
    "article": {"top_k": 5, "doc_chars": 8000, "traverse": True, "traversal_budget": 4000, "rerank_depth": RERANK_DEPTH_DEFAULT},
}


def qa_doc_chars(default: int = QA_DOC_CHARS_DEFAULT) -> int:
    return int(os.getenv("KB_QA_DOC_CHARS", default))


def qa_rerank_depth(default: int = RERANK_DEPTH_DEFAULT) -> int:
    """Profundidade do rerank no QA; 0 desliga."""
    return int(os.getenv("KB_RERANK_DEPTH", default))


def get_retrieval_profile(name: str) -> dict:
    """Perfil de retrieval nomeado; KB_QA_DOC_CHARS e KB_RERANK_DEPTH sobrepõem o perfil."""
    if name not in RETRIEVAL_PROFILES:
        valid = ", ".join(sorted(RETRIEVAL_PROFILES))
        raise ValueError(f"Perfil de retrieval desconhecido: {name}. Válidos: {valid}")
    profile = dict(RETRIEVAL_PROFILES[name])
    profile["doc_chars"] = qa_doc_chars(profile["doc_chars"])
    profile["rerank_depth"] = qa_rerank_depth(profile["rerank_depth"])
    return profile


GROUNDING_BASE_URL_DEFAULT = "http://localhost:1235/v1"
GROUNDING_MODEL_DEFAULT = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
GROUNDING_MAX_PAIRS_DEFAULT = 24
GROUNDING_TIMEOUT_DEFAULT = 15.0


def grounding_base_url() -> str:
    return os.getenv("KB_GROUNDING_BASE_URL", GROUNDING_BASE_URL_DEFAULT)


def grounding_model() -> str:
    return os.getenv("KB_GROUNDING_MODEL", GROUNDING_MODEL_DEFAULT)


def grounding_api_key() -> str | None:
    return os.getenv("KB_GROUNDING_API_KEY") or None


def grounding_max_pairs() -> int:
    try:
        value = int(os.getenv("KB_GROUNDING_MAX_PAIRS", GROUNDING_MAX_PAIRS_DEFAULT))
    except ValueError:
        value = GROUNDING_MAX_PAIRS_DEFAULT
    return max(0, value - value % 3)


def grounding_timeout() -> float:
    try:
        value = float(os.getenv("KB_GROUNDING_TIMEOUT", GROUNDING_TIMEOUT_DEFAULT))
    except ValueError:
        return GROUNDING_TIMEOUT_DEFAULT
    if not math.isfinite(value) or value <= 0:
        return GROUNDING_TIMEOUT_DEFAULT
    return value
