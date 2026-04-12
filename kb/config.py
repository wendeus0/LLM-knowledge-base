import os
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

TOPICS = ["cybersecurity", "ai", "python", "typescript"]

WIKILINK_TRAVERSAL_DEPTH = 1
MAX_CONTEXT_TOKENS = 8000
