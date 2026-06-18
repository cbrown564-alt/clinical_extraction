"""Tests for the gated Plan 11 family-routed comparison preflight."""

from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.family_routed_preflight import (
    REQUIRED_ROUTE_MODULE,
    build_family_routed_preflight,
    predeclaration_authorizes_dev_ladder,
    render_preflight_markdown,
)


def test_current_worktree_preflight_passes_after_adapter_and_authorization() -> None:
    report = build_family_routed_preflight(Path("."))

    assert report.can_run_dev_ladder is True
    assert report.blockers == ()


def test_preflight_blocks_when_routed_adapter_contract_missing(monkeypatch) -> None:
    monkeypatch.setattr(
        "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports."
        "family_routed_preflight.REQUIRED_ROUTE_MODULE",
        f"{REQUIRED_ROUTE_MODULE}.missing_contract",
    )

    report = build_family_routed_preflight(Path("."))

    assert report.can_run_dev_ladder is False
    blockers = {check.name: check.detail for check in report.blockers}
    assert "plan11_routed_adapter_contract_implemented" in blockers


def test_predeclaration_authorization_requires_status_line_not_general_audit_text() -> None:
    text = "\n".join(
        [
            "# Routed predeclaration",
            "Status: PREDECLARED, not executed",
            "A later audit requires explicit authorization.",
        ]
    )
    assert predeclaration_authorizes_dev_ladder(text) is False

    authorized = "Status: AUTHORIZED for pilot25 -> dev140 dev ladder"
    assert predeclaration_authorizes_dev_ladder(authorized) is True


def test_preflight_markdown_keeps_blocked_surfaces_visible() -> None:
    report = build_family_routed_preflight(Path("."))
    markdown = render_preflight_markdown(report)

    assert "GO" in markdown
    assert "Gan test450" in markdown
    assert "full-200/test" in markdown
    assert "pilot25" in markdown
    assert "dev140" in markdown
