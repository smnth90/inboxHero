import json
import os
from typing import Dict, Any, List

MEMORY_FILE = "data/memory_store.json"

def load_preferences() -> Dict[str, Any]:
    """
    Loads standing preferences from disk. Returns an empty dict if no preferences exist.
    """
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_preference(key: str, value: Any) -> None:
    """
    Permanently writes a standing preference rule to disk.
    """
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    prefs = load_preferences()
    prefs[key] = value
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)
    print(f"💾 Stored standing preference: [{key} -> {value}]")

def apply_standing_preferences(msg: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intercepts the LLM triage output and dynamically alters behavior 
    based on recorded user preferences.
    """
    prefs = load_preferences()
    sender = msg.get("from", "").lower()
    subject = msg.get("subject", "").lower()

    # Apply Demo Rule: If the user specified a custom legal preference rule
    # and the email sender or subject contains "legal", enforce a CC modification
    if "legal_cc_co_founder" in prefs and prefs["legal_cc_co_founder"]:
        if "legal" in sender or "legal" in subject:
            decision["reason"] += " [Enforced Standing Preference: Auto-CC Co-Founder on Legal mail]"
            decision["cc_recipient"] = "co-founder@aerowing.com"
            
    return decision
