
from sentinel.policy_engine import check_action
from sentinel.audit_log import log_decision

actions = [
    ("calculator", "calculate", "trusted"),
    ("email", "send", "trusted"),
    ("file", "delete", "untrusted"),
    ("file", "read", "trusted"),
]

print("=== SENTINEL SECURITY AUDIT ===")

for tool, operation, source in actions:
    decision = check_action(tool, operation, source)
    log_decision(tool, operation, source, decision)

    print(f"{tool} / {operation} / {source}: {decision}")

print("\nAudit records saved to sentinel_audit.jsonl")
