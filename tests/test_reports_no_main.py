"""Gate (P2-2 / gate #7): ExECTv2 report modules are importable libraries.

Every ``*.py`` directly under
``src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/`` (the
report library tier, NOT the ``reports/cli/`` entry-point package) must contain
no ``def main(`` and no ``if __name__ == "__main__":`` block. CLI plumbing lives
in ``reports/cli/<module>.py``; the report module exposes only pure
builder/render functions for import.

If a module ever has to be skipped (its ``main`` is too entangled to convert
safely), add it to ``ALLOWED_WITH_MAIN`` with a justification and the gate will
tolerate exactly that file. The allowlist is currently empty: all 14 historical
violators were fully converted.
"""

from __future__ import annotations

from pathlib import Path

# Report module filenames that are still permitted to define a CLI ``main`` /
# ``__main__`` block, each with a justification. Empty == zero tolerance.
ALLOWED_WITH_MAIN: dict[str, str] = {}


def _reports_dir() -> Path:
    return (
        Path(__file__).resolve().parent.parent
        / "src"
        / "clinical_extraction"
        / "tasks"
        / "epilepsy_phenotyping"
        / "exectv2"
        / "reports"
    )


def _report_library_modules() -> list[Path]:
    """Python files directly under ``reports/`` (excludes the ``cli/`` package)."""
    reports_dir = _reports_dir()
    return [
        path
        for path in sorted(reports_dir.glob("*.py"))
        if path.name != "__init__.py"
    ]


def test_report_modules_have_no_cli_main() -> None:
    offenders: list[str] = []
    for path in _report_library_modules():
        if path.name in ALLOWED_WITH_MAIN:
            continue
        text = path.read_text(encoding="utf-8")
        problems = []
        if "def main(" in text:
            problems.append("def main(")
        if 'if __name__ == "__main__"' in text or "if __name__ == '__main__'" in text:
            problems.append("if __name__")
        if problems:
            offenders.append(f"{path.name}: {', '.join(problems)}")

    assert offenders == [], (
        "report library modules must not contain CLI entry points "
        "(move them to reports/cli/): " + "; ".join(offenders)
    )


def test_allowlisted_report_modules_exist() -> None:
    # Guard against a stale allowlist referencing a renamed/removed module.
    names = {path.name for path in _report_library_modules()}
    missing = sorted(set(ALLOWED_WITH_MAIN) - names)
    assert missing == [], f"ALLOWED_WITH_MAIN references unknown modules: {missing}"
