import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "raw"
WIKI_DIR = ROOT / "wiki"
STATE_DIR = ROOT / "kb_state"
KNOWLEDGE_PATH = STATE_DIR / "knowledge.json"
LEARNINGS_PATH = STATE_DIR / "learnings.json"
MANIFEST_PATH = STATE_DIR / "manifest.json"

API_KEY = os.getenv("KB_API_KEY")
BASE_URL = os.getenv("KB_BASE_URL", "https://opencode.ai/zen/go/v1")
MODEL = os.getenv("KB_MODEL", "kimi-k2.5")

TOPICS = ["cybersecurity", "ai", "python", "typescript"]

WIKILINK_TRAVERSAL_DEPTH = 1
MAX_CONTEXT_TOKENS = 8000
