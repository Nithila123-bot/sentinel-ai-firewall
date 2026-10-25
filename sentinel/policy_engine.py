
def check_action(tool, operation, source="trusted"):
    """Evaluate an AI agent action before execution."""

    sensitive = operation in ("send", "delete", "execute")

    if source == "untrusted" and sensitive:
        return "DENY"

    if sensitive:
        return "REQUIRE_APPROVAL"

    if tool == "calculator" and operation == "calculate":
        return "ALLOW"

    if tool == "file" and operation == "read":
        return "ALLOW"

    return "DENY"
