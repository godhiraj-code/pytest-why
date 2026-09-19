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
        (
            "collect",
            "SyntaxError: '(' was never closed",
            "collection_error",
            "Syntax/collection error",
        ),
        (
            "call",
            "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "type_error",
            "Type error",
        ),
        (
            "call",
            "requests.exceptions.ConnectionError: service unavailable",
            "connection_error",
            "Connection error",
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


def test_existing_timeout_precedence_wins_over_connection_error():
    result = classify_failure(
        "tests/test_api.py::test_request",
        "call",
        "TimeoutError: request timed out after ConnectionError",
    )

    assert result["type"] == "timeout"


def test_import_precedence_wins_during_collection():
    result = classify_failure(
        "tests/test_import.py",
        "collect",
        "ModuleNotFoundError: No module named 'missing_package'",
    )

    assert result["type"] == "import_error"
