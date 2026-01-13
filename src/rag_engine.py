import logging
from typing import List, Tuple, Dict, Any

from sentence_transformers import CrossEncoder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from config import INDEX_DIR, OLLAMA_MODEL, LLM_TEMPERATURE, MAX_FAISS_DIST, RERANK_TOP_K, ENABLE_VERIFY
from src.formatters import format_money_and_units
from src.model_cache import get_vectorstore, get_reranker, get_llm

logger = logging.getLogger(__name__)

PROMPT_TEXT = """You are DOST Region II's AI Assistant speaking directly to clients.
Answer questions naturally and conversationally as if you are DOST Region II staff.

IMPORTANT RULES:
1) NEVER mention "according to the FAQs", "according to the context", "based on the documents", 
   or any reference to internal documents or sources. You are speaking directly to the client.
2) Answer naturally and directly. If you have the information, state it confidently.
3) If the context doesn't contain relevant information, simply say you don't have that 
   specific information and suggest contacting DOST Region II directly.
4) Use the context as your knowledge base, but present information as if it's your own knowledge.
5) Be helpful and professional, as if you work for DOST Region II.

Return your answer naturally. Start with "Answer: " followed by your response.
Keep it concise, clear, and client-friendly.

Context:
{context}

Question: {question}
"""
PROMPT = PromptTemplate(template=PROMPT_TEXT, input_variables=["context", "question"])

VERIFY_TEXT = """You are a strict verifier.
If ANY factual claim in ANSWER is NOT explicitly supported by CONTEXT, respond only: UNSUPPORTED
Otherwise respond only: SUPPORTED

CONTEXT:
{context}

ANSWER:
{answer}
"""

# load_vectorstore() is now replaced by get_vectorstore() from model_cache
# Keeping this for backwards compatibility if needed, but using cached version is preferred
def load_vectorstore():
    return get_vectorstore()

def rerank(query: str, docs: List, reranker: CrossEncoder) -> List:
    pairs = [(query, d.page_content) for d in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [d for d, _ in ranked]

def build_context(docs: List) -> Tuple[str, List[Dict[str, Any]]]:
    sources = []
    blocks = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        sources.append({"source": src})
        blocks.append(f"[Source: {src}]\n{d.page_content}")
    return "\n\n".join(blocks), sources

def clean_answer(text: str) -> str:
    """
    Clean up LLM response by:
    - Extracting just the Answer: section
    - Removing Evidence: and Sources: sections (we add sources separately)
    - Removing "Not applicable" sections
    - Removing phrases that reference internal documents (e.g., "according to the FAQs")
    """
    lines = text.split("\n")
    cleaned = []
    in_answer = False
    skip_until_empty = False
    
    for line in lines:
        line_lower = line.strip().lower()
        
        # Start capturing at "Answer:"
        if line_lower.startswith("answer:"):
            in_answer = True
            # Take the rest of the line after "Answer:"
            answer_part = line.split(":", 1)[1].strip()
            if answer_part:
                cleaned.append(answer_part)
            continue
        
        # Stop at Evidence: or Sources: sections
        if in_answer and (line_lower.startswith("evidence:") or 
                         line_lower.startswith("sources:") or
                         line_lower.startswith("source:")):
            break
        
        # Skip "Not applicable" lines
        if "not applicable" in line_lower:
            continue
        
        # Add lines that are part of the answer
        if in_answer:
            cleaned.append(line)
    
    result = "\n".join(cleaned).strip()
    # If cleaning removed everything, return original (fallback)
    if not result:
        # Fallback: just remove Evidence/Sources sections more simply
        result = text
        for marker in ["Evidence:", "Sources:", "Source:"]:
            if marker in result:
                result = result.split(marker)[0].strip()
        result = result.replace("Answer:", "").strip()
    
    # Remove phrases that reference internal documents (post-processing)
    phrases_to_remove = [
        "according to the faqs",
        "according to the faq",
        "according to the context",
        "according to the documents",
        "according to the provided context",
        "based on the faqs",
        "based on the faq",
        "based on the context",
        "based on the documents",
        "from the faqs",
        "from the faq",
        "from the context",
        "from the documents",
        "as mentioned in the faqs",
        "as mentioned in the context",
        "as stated in the faqs",
        "as stated in the context",
    ]
    
    result_lower = result.lower()
    for phrase in phrases_to_remove:
        if phrase in result_lower:
            # Remove the phrase and clean up surrounding punctuation
            import re
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            result = pattern.sub("", result)
            # Clean up extra spaces and punctuation
            result = re.sub(r'\s+', ' ', result)
            result = re.sub(r'\s*,\s*,', ',', result)  # Remove double commas
            result = re.sub(r'\s*\.\s*\.', '.', result)  # Remove double periods
            result = result.strip()
    
    return result if result else text

def rag_answer(query: str) -> Tuple[str, List[Dict[str, Any]]]:
    # Use cached models instead of loading each time (much faster!)
    vectorstore = get_vectorstore()
    reranker_model = get_reranker()
    llm = get_llm()

    # Confidence gate using similarity_search_with_score
    docs_scores = vectorstore.similarity_search_with_score(query, k=8)
    if not docs_scores:
        # If retrieval finds nothing useful, fall back to a general
        # assistant-style reply instead of a hard refusal so that
        # greetings and broad questions still get a helpful answer.
        general_prompt = f"""You are DOST Region II's helpful AI assistant.
Respond conversationally and briefly to the user message below.
- If it is a greeting (like "hi", "hello", or "how are you"), greet the user back naturally without mentioning Evidence or Sources.
- If it asks generally about DOST Region II services or programs,
  describe the types of support DOST offices typically provide in
  the Philippines (e.g., science and technology programs, testing
  and calibration services, scholarships, etc.) and suggest that
  the user contact DOST Region II directly for specific, updated details.

Respond naturally and conversationally. Do NOT include "Answer:", "Evidence:", or "Sources:" sections.

User message: {query}
Assistant:"""
        answer = llm.invoke(general_prompt)
        answer = format_money_and_units(answer)
        return answer, []

    # Rerank and pick top few
    docs = [d for d, _ in docs_scores]
    docs = rerank(query, docs, reranker_model)[:RERANK_TOP_K]

    context, sources = build_context(docs)
    answer = llm.invoke(PROMPT.format(context=context, question=query))
    # Clean up the answer to remove structured sections and "Not applicable" text
    answer = clean_answer(answer)
    answer = format_money_and_units(answer)

    if ENABLE_VERIFY:
        verdict = llm.invoke(VERIFY_TEXT.format(context=context, answer=answer)).strip().upper()
        if "UNSUPPORTED" in verdict:
            return "I don't have enough information to answer that.", sources

    return answer, sources
