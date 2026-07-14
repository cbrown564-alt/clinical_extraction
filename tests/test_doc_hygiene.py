"""Tests for documentation sprawl hygiene gates."""

from __future__ import annotations

from pathlib import Path

from scripts.check_doc_hygiene import (
    check_doc_hygiene,
    check_experiments_root_allowlist,
    check_forbidden_tool_state,
    check_root_markdown,
    check_root_underscore_dirs,
    load_allowlist,
)


def test_load_allowlist_names_only_retained_root_markdown() -> None:
    assert load_allowlist() == {
        "README.md",
        "exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.md",
        "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md",
        "gan2026_reliability_master_scorecard_2026-06-17.md",
        "gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md",
    }


def test_repo_root_markdown_allowed_only() -> None:
    root = Path(__file__).resolve().parents[1]
    assert check_root_markdown(root) == []


def test_no_underscore_root_directories() -> None:
    root = Path(__file__).resolve().parents[1]
    assert check_root_underscore_dirs(root) == []


def test_no_tool_generated_state_in_repository_root(tmp_path: Path) -> None:
    for name in (".claude", ".playwright-cli", ".zcode"):
        (tmp_path / name).mkdir()

    assert check_forbidden_tool_state(
        tmp_path,
        tracked_paths=[
            ".claude/agent.md",
            ".playwright-cli/page.yml",
            ".zcode/plan.md",
        ],
    ) == [
        "tool-generated state directory: .claude/ "
        "(keep agent configuration outside the repository)",
        "tool-generated state directory: .playwright-cli/ "
        "(keep agent configuration outside the repository)",
        "tool-generated state directory: .zcode/ "
        "(keep agent configuration outside the repository)",
    ]


def test_real_repo_has_no_tool_generated_state() -> None:
    root = Path(__file__).resolve().parents[1]
    assert check_forbidden_tool_state(root) == []


def test_experiments_root_matches_allowlist() -> None:
    root = Path(__file__).resolve().parents[1]
    allowlist = load_allowlist()
    assert check_experiments_root_allowlist(root, allowlist) == []


def test_check_doc_hygiene_passes_on_real_repo() -> None:
    root = Path(__file__).resolve().parents[1]
    assert check_doc_hygiene(root) == []
