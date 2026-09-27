import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Define file paths matching our initialization structure
PENDING_DIR = "outbox/pending"
SENT_DIR = "outbox/sent"
LOG_FILE = "data/trace.jsonl"

def log_gate_transaction(msg_id: str, proposed_action: str, allowed: bool, user_input: str) -> None:
    """
    Logs every gated decision directly to a trace file as required by the brief.
    Tracks what was proposed, what the human decided, and the final state.
    """
    os.makedirs("data", exist_ok=True)
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "capability": "R3",
        "message_id": msg_id,
        "proposed_action": proposed_action,
        "allowed": allowed,
        "user_input": user_input,
        "status": "executed" if allowed else "blocked"
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def stage_draft(msg_id: str, recipient: str, subject: str, body: str, cited_ids: List[str]) -> str:
    """
    Stages an email draft safely in the pending area. 
    Appends a 'cited' string tag to verify grounding facts.
    """
    os.makedirs(PENDING_DIR, exist_ok=True)
    
    draft_content = {
        "id": msg_id,
        "to": recipient,
        "subject": f"Re: {subject}",
        "body": body,
        "cited": cited_ids
    }
    
    file_path = os.path.join(PENDING_DIR, f"{msg_id}_draft.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(draft_content, f, indent=2)
    
    return file_path

def process_outbox_gate(dry_run: bool = False) -> None:
    """
    Evaluates all staged modifications awaiting execution.
    If dry_run is true, it displays actions without moving files.
    Otherwise, it forces an interactive user prompt before final delivery.
    """
    os.makedirs(PENDING_DIR, exist_ok=True)
    os.makedirs(SENT_DIR, exist_ok=True)
    
    pending_files = [f for f in os.listdir(PENDING_DIR) if f.endswith(".json")]
    
    if not pending_files:
        print("📥 No actions are currently pending in the outbox gate.")
        return

    print(f"\n⚡ Found {len(pending_files)} action(s) awaiting execution approval:")
    
    for filename in pending_files:
        pending_path = os.path.join(PENDING_DIR, filename)
        with open(pending_path, "r", encoding="utf-8") as f:
            draft = json.load(f)
            
        msg_id = draft.get("id")
        proposed_action = f"Send grounded email response to <{draft.get('to')}>"
        
        print("-" * 50)
        print(f"📧 Message ID: {msg_id}")
        print(f"➡️ Proposed Action: {proposed_action}")
        print(f"📌 Grounding Citations: {draft.get('cited')}")
        print(f"📝 Draft Body Preview:\n\"{draft.get('body')}\"")
        print("-" * 50)
        
        if dry_run:
            # Under dry-run constraints, report action details but bypass writing changes
            print(f"🔍 [DRY RUN]: Suppressed sending for message {msg_id}. File remains in pending.")
            log_gate_transaction(msg_id, proposed_action, allowed=False, user_input="--dry-run")
            continue
            
        # Interactive interface execution loop
        while True:
            choice = input(f"❓ Do you want to authorize this irreversible action? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                # Commit transactional operation: move payload to target folder
                sent_path = os.path.join(SENT_DIR, f"{msg_id}_sent.json")
                os.rename(pending_path, sent_path)
                print(f"🚀 Authorized! Outbound message written successfully to: {sent_path}")
                log_gate_transaction(msg_id, proposed_action, allowed=True, user_input="yes")
                break
            elif choice in ['n', 'no']:
                print(f"🛑 Refused. Message {msg_id} was held back and left in place.")
                log_gate_transaction(msg_id, proposed_action, allowed=False, user_input="no")
                break
            else:
                print("❌ Invalid response. Please type exactly 'y' or 'n'.")

    # Final summary check required by capability R3 manifestation criteria
    remaining_pending = len([f for f in os.listdir(PENDING_DIR) if f.endswith(".json")])
    if dry_run:
        print(f"\n📊 outbox/ writes: 0 (Dry-run mode safely bypassed execution paths)")
    else:
        print(f"\n📊 Processing sweep complete. Actions remaining in gate queue: {remaining_pending}")
