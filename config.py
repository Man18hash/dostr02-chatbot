from pathlib import Path

ROOT = Path(__file__).resolve().parent

DOCS_DIR = ROOT / "data" / "public_docs"
OFFICIAL_DIR = ROOT / "data" / "official"
INDEX_DIR = ROOT / "storage" / "faiss_index"

OLLAMA_MODEL = "mistral"
LLM_TEMPERATURE = 0.1  # lower = less hallucination

RETRIEVE_K = 6  # Reduced from 8 for faster retrieval (still good quality)
RERANK_TOP_K = 2  # Reduced from 3 for faster reranking (still good quality)

# FAISS "distance" threshold (lower is better). Currently unused in gating.
MAX_FAISS_DIST = 1.0

# If True, run a second-pass verifier (slower + stricter).
# We disable it by default to avoid overly frequent refusals like
# "I don’t have enough information to answer that."
ENABLE_VERIFY = False
