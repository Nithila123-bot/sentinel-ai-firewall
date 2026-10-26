
from sentinel.executor import execute_action

def test_allowed_action():
    result = execute_action("calculator", "calculate")
    assert result["decision"] == "ALLOW"
    assert result["executed"] is True

def test_denied_action():
    result = execute_action("file", "delete", "untrusted")
    assert result["decision"] == "DENY"
    assert result["executed"] is False

def test_approval_required():
    result = execute_action("email", "send", "trusted")
    assert result["decision"] == "REQUIRE_APPROVAL"
    assert result["executed"] is False

if __name__ == "__main__":
    test_allowed_action()
    test_denied_action()
    test_approval_required()
    print("PASS: All 3 executor security tests passed!")
