"""Central settings. Everything can be overridden with environment variables."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DOCQA_DATA_DIR", ROOT / "data"))
PDF_DIR = Path(os.getenv("DOCQA_PDF_DIR", DATA_DIR / "pdfs"))
ACCESS_FILE = Path(os.getenv("DOCQA_ACCESS_FILE", DATA_DIR / "access_control.json"))
LOG_DIR = Path(os.getenv("DOCQA_LOG_DIR", ROOT / "logs"))

# Chunking: chunks are built from whole sentences up to this many words,
# and consecutive chunks share OVERLAP_SENTENCES sentences so context is not lost at a boundary.
CHUNK_WORDS = int(os.getenv("DOCQA_CHUNK_WORDS", "90"))
OVERLAP_SENTENCES = int(os.getenv("DOCQA_OVERLAP_SENTENCES", "1"))

TOP_K = int(os.getenv("DOCQA_TOP_K", "4"))
MAX_HISTORY_TURNS = int(os.getenv("DOCQA_MAX_HISTORY_TURNS", "10"))
