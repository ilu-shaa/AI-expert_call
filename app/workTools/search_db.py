# app/workTools/search_db.py
import json
import os
from typing import List, Tuple
from difflib import get_close_matches

DB_PATH = "app/static_files/db.json"

def load_db():
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)

def search_db(query: str, top_k: int = 3) -> List[Tuple[str, str]]:
    db = load_db()
    results = []

    for name, entry in db.items():
        summary_parts = [name]
        for section in ["performance", "weights", "dimensions"]:
            section_data = entry.get(section, {})
            for k, v in section_data.items():
                summary_parts.append(f"{k}: {v}")
        summary = "\n".join(summary_parts)
        results.append((name, summary))
    
    # Наивный скоринг по совпадениям слов
    matches = sorted(results, key=lambda x: -sum(w in x[1].lower() for w in query.lower().split()))
    return matches[:top_k]
