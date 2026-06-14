"""Deterministic pytest failure classification."""

from typing import Any, Dict, Optional


BROWSER_AUTOMATION_HINT = (
    "Browser automation is involved. Verify selectors, waits, page load timing, "
    "and whether the element is visible before interaction."
)


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def _with_browser_hint(hint: str, longreprtext: str) -> str:
    browser_terms = (
        "selenium",
        "webdriver",
        "NoSuchElementException",
        "StaleElementReferenceException",
        "playwright",
        "locator",
        "page.",
    )
    if _contains_any(longreprtext, browser_terms):
        return f"{hint} {BROWSER_AUTOMATION_HINT}"
    return hint


def classify_failure(
    nodeid: str,
    phase: str,
    longreprtext: str,
    duration: Optional[float] = None,
) -> Dict[str, Any]:
    """Classify a pytest failure and return its explanation fields."""
    text = longreprtext or ""

    is_fixture_failure = phase == "setup" and (
        "ScopeMismatch" in text
        or "recursive dependency involving fixture" in text
        or "recursive fixture dependency" in text
        or ("fixture" in text.lower() and "not found" in text.lower())
    )

    if is_fixture_failure:
        result = {
            "type": "fixture_error",
            "title": "Fixture error",
            "explanation": (
                "Pytest could not prepare the test because a fixture is missing, "
                "has an incompatible scope, or depends on itself."
            ),
            "hint": (
                "Check the fixture name, where it is defined, its scope, and its "
                "dependency chain."
            ),
        }
    elif _contains_any(
        text,
        ("ImportError", "ModuleNotFoundError", "cannot import name", "No module named"),
    ):
        result = {
            "type": "import_error",
            "title": "Import error",
            "explanation": (
                "Python could not import a module or symbol required while collecting "
                "or running this test."
            ),
            "hint": (
                "Verify the package is installed, the import path is correct, and the "
                "symbol exists without a circular import."
            ),
        }
    elif _contains_any(
        text,
        ("Timeout", "TimeoutError", "timed out", "pytest-timeout", "Failed: Timeout"),
    ):
        result = {
            "type": "timeout",
            "title": "Timeout",
            "explanation": (
                "The test exceeded a time limit or waited too long for an operation "
                "to complete."
            ),
            "hint": (
                "Find the blocked operation, replace fixed sleeps with bounded waits, "
                "and confirm external dependencies respond."
            ),
        }
    elif _contains_any(
        text,
        (
            "AssertionError",
            "E       assert",
            "Differing items",
            "Left contains",
            "Right contains",
        ),
    ):
        result = {
            "type": "assertion_mismatch",
            "title": "Assertion mismatch",
            "explanation": (
                "The code ran, but the observed value or state did not match what the "
                "test expected."
            ),
            "hint": (
                "Compare the expected and actual values near the final assertion, then "
                "trace where they first diverge."
            ),
        }
    else:
        result = {
            "type": "unknown_failure",
            "title": "Unknown failure",
            "explanation": (
                "The failure does not match a known pytest-why pattern, so the "
                "traceback remains the best source of detail."
            ),
            "hint": (
                "Start at the last application frame in the traceback and inspect the "
                "inputs and state immediately before the exception."
            ),
        }

    result["hint"] = _with_browser_hint(result["hint"], text)
    return result
