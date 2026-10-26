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

    for tool, operation, source, expected in cases:
        actual = check_action(tool, operation, source)

        assert actual == expected, (
            f"{tool}/{operation}/{source}: "
            f"expected {expected}, got {actual}"
        )


if __name__ == "__main__":
    test_policy()
    print("All security policy tests passed!")