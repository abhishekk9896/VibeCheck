import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE_PATH = Path("scope_auditor_security.log")

def log_audit_event(event_type: str, details: dict):
    """Writes structured JSON event logs with strict timestamps for compliance auditing."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "details": details
    }
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")