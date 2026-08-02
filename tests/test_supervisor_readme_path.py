from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_supervisor_path_has_ordered_content_and_current_claims() -> None:
    text = README.read_text(encoding="utf-8")
    sections = [
        "## Supervisor path",
        "### Five-stage orientation",
        "### Six-path teaching walkthrough",
        "### Open the frontend",
        "### Standalone handoff package status",
        "### Canonical results, limits, and exact replay",
        "## Method names",
    ]
    positions = [text.index(section) for section in sections]
    assert positions == sorted(positions)

    for required in (
        "flowchart LR",
        "docs/architecture/teaching_cases/six_paths.md",
        "frontend/README.md",
        "docs/research/six_model_comparison_report_2026-07-18.md",
        "docs/canon/10_paper_provenance.md",
        "scripts\\verify_reference_evidence.py",
        "tests/test_supervisor_source_handoff.py",
        "default`/`default",
        "dev750 coverage\n  is complete",
    ):
        assert required in text, required

    forbidden_stale_claims = (
        "compiled three-page PDF",
        "now the disclosed fallback",
        "dev750 coverage\n  is pending",
        "Current commands use three plain names",
    )
    for stale_claim in forbidden_stale_claims:
        assert stale_claim not in text, stale_claim


def test_readme_supervisor_links_resolve_to_local_files() -> None:
    text = README.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", text)
    local_links = [
        link for link in links if not link.startswith(("http://", "https://", "#"))
    ]
    assert local_links
    for link in local_links:
        # Pathlib accepts POSIX-style markdown links on Windows and Linux.
        target = ROOT / Path(link.split("#", 1)[0])
        assert target.exists(), link
