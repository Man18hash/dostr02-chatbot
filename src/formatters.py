import re
from typing import List, Dict, Any

def format_money_and_units(text: str) -> str:
    # Keep this conservative—avoid aggressive number rewriting
    text = re.sub(r"\b(per piece|per hour|per L|per kg|per ton)\b", r"*\1*", text, flags=re.IGNORECASE)
    return text

def format_sources(sources: List[Dict[str, Any]]) -> str:
    if not sources:
        return ""
    lines = ["\n**Sources:**"]
    for s in sources:
        lines.append(f"- {s.get('source','(unknown)')}")
    return "\n".join(lines)
