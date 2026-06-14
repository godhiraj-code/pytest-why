"""Pytest hooks for pytest-why."""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from .classifier import classify_failure
from .reporter import write_html_report, write_markdown_report


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("pytest-why")
    group.addoption(
        "--why",
        action="store_true",
        default=False,
        help="Explain failures and write pytest-why Markdown and HTML reports.",
    )


def pytest_configure(config: pytest.Config) -> None:
    if config.getoption("--why"):
        config.pluginmanager.register(WhyPlugin(), "pytest-why-runtime")


class WhyPlugin:
    def __init__(self) -> None:
        self.failures: List[Dict[str, Any]] = []

    def _record_failure(self, report: Any, phase: str) -> None:
        if not report.failed:
            return

        duration = getattr(report, "duration", None)
        classification = classify_failure(
            nodeid=report.nodeid,
            phase=phase,
            longreprtext=report.longreprtext,
            duration=duration,
        )
        self.failures.append(
            {
                "nodeid": report.nodeid,
                "phase": phase,
                "duration": duration,
                "longreprtext": report.longreprtext,
                **classification,
            }
        )

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        self._record_failure(report, report.when)

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        self._record_failure(report, "collect")

    def pytest_terminal_summary(
        self,
        terminalreporter: pytest.TerminalReporter,
        exitstatus: int,
        config: pytest.Config,
    ) -> None:
        terminalreporter.section("pytest-why: failure explanations")
        terminalreporter.write_line(f"Total failures: {len(self.failures)}")
        for failure in self.failures:
            terminalreporter.write_line(
                f"{failure['title']}: {failure['nodeid']} ({failure['phase']})"
            )
            terminalreporter.write_line(f"  Why: {failure['explanation']}")
            terminalreporter.write_line(f"  Hint: {failure['hint']}")

        report_dir = Path.cwd()
        write_markdown_report(self.failures, report_dir / "pytest-why-report.md")
        write_html_report(self.failures, report_dir / "pytest-why-report.html")
        terminalreporter.write_line("Reports: pytest-why-report.md, pytest-why-report.html")
