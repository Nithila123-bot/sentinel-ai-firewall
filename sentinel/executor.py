
from .policy_engine import check_action
from .audit_log import log_decision


def execute_action(tool, operation, source="trusted"):
    decision = check_action(tool, operation, source)
    log_decision(tool, operation, source, decision)

    if decision == "DENY":
        return {
            "decision": decision,
            "executed": False,
            "message": "Blocked by Sentinel security policy."
        }

    if decision == "REQUIRE_APPROVAL":
        return {
            "decision": decision,
            "executed": False,
            "message": "Waiting for human approval."
        }

    return {
        "decision": decision,
        "executed": True,
        "message": "Simulated action completed successfully."
    }
