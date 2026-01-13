import logging
from config import DOCS_DIR, INDEX_DIR
from src.ingest import build_or_update_index

logging.basicConfig(level=logging.INFO)

build_or_update_index(DOCS_DIR, INDEX_DIR)
print("Index built successfully.")
