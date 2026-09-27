import json
import os
from typing import List, Dict, Any, Optional

def load_inbox_data(file_path: str = "data/inbox.json") -> List[Dict[str, Any]]:
    """
    Safely loads messages from the raw inbox JSON file.
    Ensures all messages are sorted chronologically by timestamp.
    """
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: Target mail store file '{file_path}' not found.")
        return []
        
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            messages = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Error: Failed to parse '{file_path}'. Check if JSON layout is malformed.")
            return []
            
    # Sort messages chronologically (oldest first) to preserve conversation logic flow
    try:
        messages.sort(key=lambda x: x.get("timestamp", ""))
    except Exception as e:
        print(f"⚠️ Timestamp sort warning: {e}. Defaulting to default ordering.")
        
    return messages

def build_thread_map(messages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Organizes standalone messages into structural conversation paths grouped by thread_id.
    """
    thread_map = {}
    for msg in messages:
        t_id = msg.get("thread_id")
        if t_id:
            if t_id not in thread_map:
                thread_map[t_id] = []
            thread_map[t_id].append(msg)
    return thread_map

def walk_thread_context(message_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Locates a specific target message, identifies its historical thread, and
    gathers all prior contextual items to ground the generation engine securely.
    """
    target_msg = None
    for msg in messages:
        if msg.get("id") == message_id:
            target_msg = msg
            break
            
    if not target_msg:
        return {"target": None, "history": [], "cited_ids": []}
        
    thread_id = target_msg.get("thread_id")
    thread_map = build_thread_map(messages)
    
    # Isolate messages in this thread that occurred strictly before our target message
    full_thread = thread_map.get(thread_id, [])
    history = []
    cited_ids = []
    
    for msg in full_thread:
        if msg.get("id") == message_id:
            break  # Stop gathering context once we reach the message being replied to
        history.append(msg)
        cited_ids.append(msg.get("id"))
        
    return {
        "target": target_msg,
        "history": history,
        "cited_ids": cited_ids
    }
