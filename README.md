# pytest-why

[![PyPI version](https://img.shields.io/pypi/v/pytest-why.svg)](https://pypi.org/project/pytest-why/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-why.svg)](https://pypi.org/project/pytest-why/)
[![License: MIT](https://img.shields.io/pypi/l/pytest-why.svg)](https://github.com/godhiraj-code/pytest-why/blob/main/LICENSE)
[![Tests](https://github.com/godhiraj-code/pytest-why/actions/workflows/tests.yml/badge.svg)](https://github.com/godhiraj-code/pytest-why/actions/workflows/tests.yml)

**Your pytest run failed and the traceback doesn't tell you why.** `pytest-why` adds
`--why`: each failure gets a plain-English cause (fixture error, assertion mismatch,
import error, timeout, collection error...) and the next step to try, plus a
shareable Markdown/HTML report.

> A pytest plugin that explains failing tests like a senior engineer.

Before, a plain `pytest` run on a test that uses a missing fixture:

```text
_______________________ ERROR at setup of test_checkout ________________________
file test_checkout.py, line 3
  def test_checkout(db_session):
E       fixture 'db_session' not found
>       available fixtures: capfd, capfdbinary, caplog, capsys, ...
>       use 'pytest --fixtures [testpath]' for help on them.
=========================== short test summary info ============================
ERROR test_checkout.py::test_checkout
```

After, with `pytest --why`:

```text
================ pytest-why: failure explanations ================
Total failures: 1
Fixture error: test_checkout.py::test_checkout (setup)
  Why: Pytest could not prepare the test because a fixture is missing, has an incompatible scope, or depends on itself.
  Hint: Check the fixture name, where it is defined, its scope, and its dependency chain.
Reports: pytest-why-report.md, pytest-why-report.html
```

**Learn more:** [pytest-why: actionable failure guidance](https://www.dhirajdas.dev/blog/pytest-why-actionable-failure-guidance) · [Project page](https://www.dhirajdas.dev/project/pytest-why)

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

## Example

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
- **Syntax/collection error**: parsing or collection failed before a test could run
- **Type error**: an operation received an incompatible object or argument type
- **Connection error**: a dependency connection was refused, reset, or otherwise failed
- **Unknown failure**: deterministic fallback with traceback-first guidance

Selenium and Playwright tracebacks also receive a focused browser automation
hint covering selectors, waits, page timing, and element visibility.

## When to use pytest-why (vs alternatives)

| Tool | What it does | How pytest-why differs |
|---|---|---|
| `pytest -vv` / `--tb=long` | Shows more of the traceback and the full assertion diff | pytest-why keeps the normal output and adds a short, classified cause and a next step per failure, plus a report you can share |
| [pytest-clarity](https://pypi.org/project/pytest-clarity/), [pytest-icdiff](https://pypi.org/project/pytest-icdiff/) | Make assertion diffs easier to read | Those are diff viewers for assertion failures. pytest-why also covers fixture, import, collection, timeout, type and connection failures, and it works alongside them |
| Pasting the traceback into an LLM chat | Free-form explanation | pytest-why runs locally and offline, sends nothing anywhere, and gives the same answer every time (rule-based classification) |

Use it when you want a quick triage of "what kind of failure is this and where do I start", in your terminal or in CI.
It is not a replacement for reading the traceback: the classification is pattern-based, and failures that match no pattern are reported as **Unknown failure**, with the raw traceback kept in the report.

## FAQ

**Does it send my code or tracebacks anywhere?**
No. Classification is deterministic string matching inside the pytest process. There are no network calls, and the reports are written only to your working directory.

**Does it slow down my test runs?**
Without `--why`, the plugin does nothing. With `--why`, it only does work for failed tests (a few substring checks per failure), plus writing the two report files at the end of the session.

**Does it work with pytest-xdist?**
Yes. Failure reports from workers are collected by the main process, so `pytest -n auto --why` prints one combined summary and writes one pair of reports.

**Where are the reports written, and should I commit them?**
`pytest-why-report.md` and `pytest-why-report.html` are written to the current working directory on every `--why` run. Add them to `.gitignore`, or upload them as CI artifacts.

**My failure shows up as "Unknown failure".**
That's the deterministic fallback for tracebacks that don't match a known pattern. The report still contains the full raw traceback. Issues with example tracebacks are welcome: https://github.com/godhiraj-code/pytest-why/issues

## License

MIT. See [LICENSE](https://github.com/godhiraj-code/pytest-why/blob/main/LICENSE).

**Stop doomscrolling tracebacks. Run pytest --why.**
