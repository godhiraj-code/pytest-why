from pytest_why.reporter import write_html_report, write_markdown_report


def sample_failure():
    return {
        "nodeid": "tests/test_demo.py::test_value",
        "phase": "call",
        "duration": 0.01234,
        "longreprtext": "E       assert 4 == 5\n<script>alert('x')</script>",
        "type": "assertion_mismatch",
        "title": "Assertion mismatch",
        "explanation": "The result differed from the expectation.",
        "hint": "Inspect the values.",
    }


def test_write_markdown_report(tmp_path):
    path = tmp_path / "report.md"

    write_markdown_report([sample_failure()], path)

    content = path.read_text(encoding="utf-8")
    assert "# pytest-why failure explanations" in content
    assert "**Total failures:** 1" in content
    assert "`tests/test_demo.py::test_value`" in content
    assert "**Phase:** `call`" in content
    assert "`assertion_mismatch` - Assertion mismatch" in content
    assert "**Duration:** 0.012s" in content
    assert "**Why:**" in content
    assert "**Hint:**" in content
    assert "<details>" in content
    assert "E       assert 4 == 5" in content


def test_write_html_report_escapes_traceback(tmp_path):
    path = tmp_path / "report.html"

    write_html_report([sample_failure()], path)

    content = path.read_text(encoding="utf-8")
    assert "<style>" in content
    assert "Total failures:</strong> 1" in content
    assert "Assertion mismatch" in content
    assert "<details>" in content
    assert "<pre>" in content
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in content
    assert "<script>alert('x')</script>" not in content


def test_markdown_traceback_uses_a_fence_longer_than_backtick_runs(tmp_path):
    path = tmp_path / "report.md"
    failure = sample_failure()
    failure["longreprtext"] = (
        "Traceback line\n```text\nescaped fence attempt\n```\n"
        "<script>alert('x')</script>"
    )

    write_markdown_report([failure], path)

    content = path.read_text(encoding="utf-8")
    assert "````text\nTraceback line\n```text" in content
    assert "\n<script>alert('x')</script>\n````" in content
    assert content.count("````") == 2


def test_markdown_fence_handles_longer_backtick_runs(tmp_path):
    path = tmp_path / "report.md"
    failure = sample_failure()
    failure["longreprtext"] = "before ````` after"

    write_markdown_report([failure], path)

    content = path.read_text(encoding="utf-8")
    assert "``````text\nbefore ````` after\n``````" in content
