import os
import logging
from pathlib import Path
from typing import List

from unstructured.partition.auto import partition
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

def extract_text(file_path: Path) -> str:
    elements = partition(filename=str(file_path))
    return "\n".join([el.text for el in elements if getattr(el, "text", None)])

def build_or_update_index(docs_dir: Path, index_dir: Path) -> None:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, chunk_overlap=150,
        separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", " "],
        is_separator_regex=False
    )

    all_docs = []
    for fname in os.listdir(docs_dir):
        if not fname.lower().endswith((".pdf", ".docx", ".txt")):
            continue
        fp = docs_dir / fname
        logger.info(f"Extracting: {fp}")
        text = extract_text(fp).strip()
        if not text:
            logger.warning(f"No text extracted from: {fp}")
            continue

        # create_documents supports metadatas -> attach source filename
        chunk_docs = splitter.create_documents([text], metadatas=[{"source": fname}])
        all_docs.extend(chunk_docs)

    if not all_docs:
        raise ValueError("No documents were extracted. Add PDFs/DOCX/TXT to data/public_docs.")

    # Build FAISS from Documents (keep metadata)
    vectorstore = FAISS.from_documents(all_docs, embeddings)
    index_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(index_dir))
    logger.info(f"Saved FAISS index to: {index_dir}")
