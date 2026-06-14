import pytest

from pytest_why.classifier import BROWSER_AUTOMATION_HINT, classify_failure


@pytest.mark.parametrize(
    ("phase", "traceback", "expected_type", "expected_title"),
    [
        (
            "call",
            "E       assert {'a': 1} == {'a': 2}\nDiffering items:",
            "assertion_mismatch",
            "Assertion mismatch",
        ),
        (
            "setup",
            "ModuleNotFoundError: No module named 'missing_package'",
            "import_error",
            "Import error",
        ),
        (
            "setup",
            "fixture 'database' not found",
            "fixture_error",
            "Fixture error",
        ),
        (
            "call",
            "Failed: Timeout (>2.0s) from pytest-timeout",
            "timeout",
            "Timeout",
        ),
        (
            "teardown",
            "RuntimeError: cleanup broke",
            "unknown_failure",
            "Unknown failure",
        ),
    ],
)
def test_classify_failure(phase, traceback, expected_type, expected_title):
    result = classify_failure("tests/test_example.py::test_case", phase, traceback, 0.1)

    assert result["type"] == expected_type
    assert result["title"] == expected_title
    assert result["explanation"]
    assert result["hint"]


def test_fixture_terms_only_classify_as_fixture_error_during_setup():
    result = classify_failure(
        "tests/test_example.py::test_case",
        "call",
        "AssertionError: fixture value was not found",
    )

    assert result["type"] == "assertion_mismatch"


def test_browser_automation_hint_is_added():
    result = classify_failure(
        "tests/test_ui.py::test_login",
        "call",
        "selenium.common.exceptions.NoSuchElementException: missing button",
    )

    assert BROWSER_AUTOMATION_HINT in result["hint"]
