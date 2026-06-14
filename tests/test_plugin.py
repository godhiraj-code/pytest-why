def test_why_explains_assertion_and_writes_reports(pytester):
    pytester.makepyfile(
        test_demo="""
        def test_math():
            assert 2 + 2 == 5
        """
    )

    result = pytester.runpytest("--why")

    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-why: failure explanations*",
            "Total failures: 1",
            "Assertion mismatch: test_demo.py::test_math (call)",
            "*Reports: pytest-why-report.md, pytest-why-report.html*",
        ]
    )
    assert (pytester.path / "pytest-why-report.md").is_file()
    assert (pytester.path / "pytest-why-report.html").is_file()


def test_without_why_has_no_summary_or_reports(pytester):
    pytester.makepyfile(
        test_demo="""
        def test_math():
            assert 2 + 2 == 5
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(failed=1)
    assert "pytest-why: failure explanations" not in result.stdout.str()
    assert not (pytester.path / "pytest-why-report.md").exists()
    assert not (pytester.path / "pytest-why-report.html").exists()


def test_fixture_failure_is_classified_during_setup(pytester):
    pytester.makepyfile(
        test_fixture="""
        def test_needs_fixture(missing_fixture):
            pass
        """
    )

    result = pytester.runpytest("--why")

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(
        ["Fixture error: test_fixture.py::test_needs_fixture (setup)"]
    )
    markdown = (pytester.path / "pytest-why-report.md").read_text(encoding="utf-8")
    assert "`fixture_error` - Fixture error" in markdown


def test_collection_import_error_is_explained_and_writes_reports(pytester):
    pytester.makepyfile(
        test_import_error="""
        import package_that_does_not_exist

        def test_unreachable():
            pass
        """
    )

    result = pytester.runpytest("--why")

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(
        [
            "*pytest-why: failure explanations*",
            "Total failures: 1",
            "Import error: test_import_error.py (collect)",
            "*Reports: pytest-why-report.md, pytest-why-report.html*",
        ]
    )
    markdown = (pytester.path / "pytest-why-report.md").read_text(encoding="utf-8")
    html = (pytester.path / "pytest-why-report.html").read_text(encoding="utf-8")
    assert "`import_error` - Import error" in markdown
    assert "**Phase:** `collect`" in markdown
    assert "Import error" in html
    assert "Phase: <code>collect</code>" in html
