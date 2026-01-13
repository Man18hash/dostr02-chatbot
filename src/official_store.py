import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"items": []}
    return json.loads(path.read_text(encoding="utf-8"))

def load_official(official_dir: Path) -> Dict[str, Dict[str, Any]]:
    return {
        "contacts": _load_json(official_dir / "contacts.json"),
        "addresses": _load_json(official_dir / "addresses.json"),
        "fees": _load_json(official_dir / "fees.json"),
        "requirements": _load_json(official_dir / "requirements.json"),
        "procedures": _load_json(official_dir / "procedures.json"),
    }

def _search_items(items: List[Dict[str, Any]], query: str, key: str) -> List[Dict[str, Any]]:
    q = query.lower()
    scored = []
    for it in items:
        text = str(it.get(key, "")).lower()
        if not text:
            continue
        if q in text or any(tok in text for tok in q.split()):
            scored.append(it)
    return scored[:5]

def answer_official(official_db: Dict[str, Dict[str, Any]], query: str) -> Tuple[str, List[Dict[str, Any]]]:
    q = query.lower()

    # Decide which dataset to use based on keywords
    if any(k in q for k in ["contact", "email", "phone", "hotline"]):
        matches = _search_items(official_db["contacts"]["items"], query, "office")
        if matches:
            lines = ["**Official Contacts:**"]
            sources = []
            for m in matches:
                lines.append(f"- **{m.get('office')}**: {m.get('email','')} | {m.get('phone','')}")
                if m.get("source"):
                    sources.append({"source": m["source"]})
            return "\n".join(lines), sources

    if any(k in q for k in ["address", "location", "where"]):
        matches = _search_items(official_db["addresses"]["items"], query, "office")
        if matches:
            lines = ["**Official Office Address:**"]
            sources = []
            for m in matches:
                lines.append(f"- **{m.get('office')}**: {m.get('address','')}")
                if m.get("source"):
                    sources.append({"source": m["source"]})
            return "\n".join(lines), sources

    if any(k in q for k in ["fee", "fees", "cost", "how much", "price", "charge", "rate"]):
        matches = _search_items(official_db["fees"]["items"], query, "service")
        if matches:
            lines = ["**Official Fees:**"]
            sources = []
            for m in matches:
                lines.append(f"- **{m.get('service')}**: ₱{m.get('fee_php')} ({m.get('unit','')})")
                if m.get("notes"):
                    lines.append(f"  - Notes: {m['notes']}")
                if m.get("source"):
                    sources.append({"source": m["source"]})
            return "\n".join(lines), sources

    if any(k in q for k in ["requirement", "requirements", "documents needed", "needed documents"]):
        matches = _search_items(official_db["requirements"]["items"], query, "service")
        if matches:
            lines = ["**Official Requirements:**"]
            sources = []
            for m in matches:
                lines.append(f"- **{m.get('service')}**:")
                for r in m.get("required_docs", []):
                    lines.append(f"  - {r}")
                if m.get("source"):
                    sources.append({"source": m["source"]})
            return "\n".join(lines), sources

    if any(k in q for k in ["procedure", "process", "steps", "how to apply", "apply"]):
        matches = _search_items(official_db["procedures"]["items"], query, "service")
        if matches:
            lines = ["**Official Procedure:**"]
            sources = []
            for m in matches:
                lines.append(f"- **{m.get('service')}**:")
                for i, step in enumerate(m.get("steps", []), start=1):
                    lines.append(f"  {i}. {step}")
                if m.get("source"):
                    sources.append({"source": m["source"]})
            return "\n".join(lines), sources

    return "", []
