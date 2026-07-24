"""Deterministic evaluation harness for VibeCompass reliability behavior."""

from src.reliability import audit_recommendations, load_default_catalog


CASES = [
    {
        "name": "happy pop leader",
        "profile": {"genre": "pop", "mood": "happy", "energy": 0.8},
        "expected_title": "Sunrise City",
    },
    {
        "name": "chill lofi leader",
        "profile": {"genre": "lofi", "mood": "chill", "energy": 0.35},
        "expected_title": "Library Rain",
    },
    {
        "name": "intense rock leader",
        "profile": {"genre": "rock", "mood": "intense", "energy": 0.92},
        "expected_title": "Storm Runner",
    },
    {
        "name": "invalid energy guardrail",
        "profile": {"genre": "pop", "mood": "happy", "energy": 4.0},
        "expect_abstention": True,
    },
]


def evaluate() -> int:
    """Run predefined cases and print a concise pass/fail summary."""
    songs = load_default_catalog()
    passed = 0
    for case in CASES:
        result = audit_recommendations(case["profile"], songs)
        if case.get("expect_abstention"):
            success = result.abstained
            observed = result.reason
        else:
            observed = (
                result.recommendations[0][0]["title"]
                if result.recommendations
                else result.reason
            )
            success = not result.abstained and observed == case["expected_title"]
        passed += int(success)
        print(f"{'PASS' if success else 'FAIL'} | {case['name']} | {observed}")

    print(f"\nSummary: {passed}/{len(CASES)} checks passed")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(evaluate())
