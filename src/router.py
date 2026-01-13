from typing import Tuple, List, Dict, Any
from pathlib import Path

from src.official_store import load_official, answer_official
from src.rag_engine import rag_answer
from src.formatters import format_sources
from config import OFFICIAL_DIR

HIGH_RISK_KEYWORDS = [
    "fee", "fees", "cost", "price", "how much", "rate",
    "address", "location", "where",
    "contact", "email", "phone", "hotline",
    "requirement", "requirements", "documents needed",
    "procedure", "process", "steps", "apply"
]

# Cache the official database - load once, reuse forever
_official_db_cache = None

def route_query(query: str) -> str:
    q = query.lower()
    return "official" if any(k in q for k in HIGH_RISK_KEYWORDS) else "rag"

def is_placeholder_data(answer: str) -> bool:
    """
    Check if the answer contains placeholder data that should trigger
    a fallback to RAG instead.
    """
    if not answer:
        return False
    
    placeholder_indicators = [
        "REPLACE_ME",
        "Step 1",
        "Step 2", 
        "Step 3",
        "Doc 1",
        "Doc 2",
        "YYYY-MM-DD",
        "Procedure memo / document title",
        "Requirements memo / document title"
    ]
    
    answer_upper = answer.upper()
    for indicator in placeholder_indicators:
        if indicator.upper() in answer_upper:
            return True
    
    return False

def hybrid_answer(query: str) -> str:
    global _official_db_cache
    # Load official DB only once, cache it (much faster!)
    if _official_db_cache is None:
        _official_db_cache = load_official(OFFICIAL_DIR)
    
    official_db = _official_db_cache

    route = route_query(query)

    # Try official first when high-risk
    if route == "official":
        ans, sources = answer_official(official_db, query)
        # Check if answer contains placeholder data - if so, fall back to RAG
        if ans and is_placeholder_data(ans):
            # Placeholder detected, use RAG instead for better answer
            rag_ans, rag_sources = rag_answer(query)
            return rag_ans + "\n" + format_sources(rag_sources)
        
        if ans:
            return ans + "\n" + format_sources(sources)

        # if not found in official DB, fallback to RAG (still strict)
        rag_ans, rag_sources = rag_answer(query)
        return rag_ans + "\n" + format_sources(rag_sources)

    # non-high-risk -> RAG
    rag_ans, rag_sources = rag_answer(query)
    return rag_ans + "\n" + format_sources(rag_sources)
