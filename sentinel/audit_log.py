
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "sentinel_audit.jsonl"


def log_decision(tool, operation, source, decision):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "operation": operation,
        "source": source,
        "decision": decision,
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    return record
