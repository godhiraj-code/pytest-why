"""Markdown and HTML report writers."""

from html import escape
from pathlib import Path
from typing import Any, Iterable, Mapping, Union


Failure = Mapping[str, Any]
PathLike = Union[str, Path]


def _duration(failure: Failure) -> str:
    duration = failure.get("duration")
    if duration is None:
        return "n/a"
    return f"{float(duration):.3f}s"


def _backtick_fence(content: str) -> str:
    longest_run = 0
    current_run = 0
    for character in content:
        if character == "`":
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0
    return "`" * max(3, longest_run + 1)


def write_markdown_report(
    failures: Iterable[Failure],
    path: PathLike = "pytest-why-report.md",
) -> None:
    """Write a human-readable Markdown failure report."""
    items = list(failures)
    lines = [
        "# pytest-why failure explanations",
        "",
        f"**Total failures:** {len(items)}",
        "",
    ]

    for index, failure in enumerate(items, start=1):
        traceback = str(failure.get("longreprtext", "")).rstrip()
        fence = _backtick_fence(traceback)
        lines.extend(
            [
                f"## {index}. `{failure['nodeid']}`",
                "",
                f"- **Phase:** `{failure['phase']}`",
                f"- **Type:** `{failure['type']}` - {failure['title']}",
                f"- **Duration:** {_duration(failure)}",
                "",
                f"**Why:** {failure['explanation']}",
                "",
                f"**Hint:** {failure['hint']}",
                "",
                "<details>",
                "<summary>Raw traceback</summary>",
                "",
                f"{fence}text",
                traceback,
                fence,
                "",
                "</details>",
                "",
            ]
        )

    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_html_report(
    failures: Iterable[Failure],
    path: PathLike = "pytest-why-report.html",
) -> None:
    """Write a standalone HTML failure report."""
    items = list(failures)
    cards = []
    for failure in items:
        cards.append(
            """
            <article class="card">
              <h2>{nodeid}</h2>
              <div class="meta">
                <span>Phase: <code>{phase}</code></span>
                <span>Type: <code>{type}</code> - {title}</span>
                <span>Duration: {duration}</span>
              </div>
              <h3>Why</h3>
              <p>{explanation}</p>
              <h3>Hint</h3>
              <p>{hint}</p>
              <details>
                <summary>Raw traceback</summary>
                <pre>{traceback}</pre>
              </details>
            </article>
            """.format(
                nodeid=escape(str(failure["nodeid"])),
                phase=escape(str(failure["phase"])),
                type=escape(str(failure["type"])),
                title=escape(str(failure["title"])),
                duration=escape(_duration(failure)),
                explanation=escape(str(failure["explanation"])),
                hint=escape(str(failure["hint"])),
                traceback=escape(str(failure.get("longreprtext", ""))),
            )
        )

    document = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>pytest-why failure explanations</title>
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 0 auto;
            padding: 2rem; line-height: 1.5; background: #f6f7f9; color: #18202a; }}
    header {{ margin-bottom: 1.5rem; }}
    .card {{ background: white; border: 1px solid #d9dee5; border-radius: 10px;
             padding: 1.25rem; margin: 1rem 0; box-shadow: 0 2px 8px #0000000d; }}
    .card h2 {{ overflow-wrap: anywhere; margin-top: 0; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: .5rem 1.5rem; color: #4b5563; }}
    code, pre {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
    pre {{ overflow: auto; padding: 1rem; border-radius: 6px; background: #111827;
           color: #e5e7eb; white-space: pre-wrap; }}
    summary {{ cursor: pointer; font-weight: 600; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #111827; color: #e5e7eb; }}
      .card {{ background: #1f2937; border-color: #374151; }}
      .meta {{ color: #cbd5e1; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>pytest-why: failure explanations</h1>
    <p><strong>Total failures:</strong> {count}</p>
  </header>
  <main>{cards}</main>
</body>
</html>
""".format(count=len(items), cards="".join(cards))
    Path(path).write_text(document, encoding="utf-8")
