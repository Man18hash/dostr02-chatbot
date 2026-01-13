from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from sentence_transformers import CrossEncoder
from pathlib import Path
from config import INDEX_DIR, OLLAMA_MODEL, LLM_TEMPERATURE

# Global cache for models - loaded once, reused forever
_vectorstore = None
_reranker = None
_llm = None

def get_vectorstore():
    """Get cached FAISS vectorstore. Loads on first call."""
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        _vectorstore = FAISS.load_local(str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True)
    return _vectorstore

def get_reranker():
    """Get cached CrossEncoder reranker. Loads on first call."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

def get_llm():
    """Get cached Ollama LLM. Loads on first call."""
    global _llm
    if _llm is None:
        _llm = OllamaLLM(model=OLLAMA_MODEL, temperature=LLM_TEMPERATURE)
    return _llm


