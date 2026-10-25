
from sentinel.policy_engine import check_action

def test_policy():
    cases = [
        ("calculator", "calculate", "trusted", "ALLOW"),
        ("email", "send", "trusted", "REQUIRE_APPROVAL"),
        ("file", "delete", "untrusted", "DENY"),
        ("file", "read", "trusted", "ALLOW"),
        ("unknown", "read", "trusted", "DENY"),
        ("email", "send", "untrusted", "DENY"),
        ("file", "execute", "untrusted", "DENY"),
    ]

    failures = 0

    for tool, operation, source, expected in cases:
        actual = check_action(tool, operation, source)

        if actual == expected:
            print(f"PASS: {tool}/{operation}/{source} -> {actual}")
        else:
            print(
                f"FAIL: {tool}/{operation}/{source} "
                f"expected {expected}, got {actual}"
            )
            failures += 1

    print(f"\nPassed: {len(cases) - failures}/{len(cases)}")
    return failures == 0


if __name__ == "__main__":
    if not test_policy():
        raise SystemExit(1)
    print("All security policy tests passed!")
