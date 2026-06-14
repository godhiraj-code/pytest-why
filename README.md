# pytest-why

> A pytest plugin that explains failing tests like a senior engineer.

`pytest-why` turns common pytest failures into concise explanations and practical
next steps. It runs locally, adds no noise to normal test runs, and creates
shareable Markdown and HTML reports when you ask for them.

## Install

```bash
python -m pip install pytest-why
```

For local development:

```bash
python -m pip install -e .[dev]
```

## Usage

Run pytest with one extra flag:

```bash
python -m pytest --why
```

Without `--why`, the plugin does nothing and creates no report files.

## Viral demo

Given:

```python
def test_math():
    assert 2 + 2 == 5
```

Run:

```bash
pytest --why
```

Sample output:

```text
================ pytest-why: failure explanations ================
Total failures: 1
Assertion mismatch: test_math.py::test_math (call)
  Why: The code ran, but the observed value or state did not match what the test expected.
  Hint: Compare the expected and actual values near the final assertion, then trace where they first diverge.
Reports: pytest-why-report.md, pytest-why-report.html
```

## Reports

Each `--why` run writes:

- `pytest-why-report.md` for pull requests, issue trackers, and terminals
- `pytest-why-report.html` for a styled, standalone browser view

Both reports include the failing test, pytest phase, classification, duration,
explanation, hint, and the complete raw traceback.

## Supported classifications

- **Assertion mismatch**: expected and actual values differ
- **Import error**: a module or symbol could not be imported
- **Fixture error**: missing fixtures, scope mismatches, or recursive dependencies
- **Timeout**: a test or operation exceeded its time limit
- **Unknown failure**: deterministic fallback with traceback-first guidance

Selenium and Playwright tracebacks also receive a focused browser automation
hint covering selectors, waits, page timing, and element visibility.

The MVP is deterministic and local. No LLM or network connection is required.

**Stop doomscrolling tracebacks. Run pytest --why.**
