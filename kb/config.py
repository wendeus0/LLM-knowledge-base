import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "raw"
WIKI_DIR = ROOT / "wiki"

API_KEY = os.environ["KB_API_KEY"]
BASE_URL = os.getenv("KB_BASE_URL", "https://opencode.ai/zen/go/v1")
MODEL = os.getenv("KB_MODEL", "kimi-k2.5")

TOPICS = ["cybersecurity", "ai", "python", "typescript"]
