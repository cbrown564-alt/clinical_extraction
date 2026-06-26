"""Pytest wrapper for production and tests line-count gates (Wave 3 Sprint 4 / Wave C Sprint 1)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from check_line_counts import (  # noqa: E402
    ALLOWLIST,
    EXECTV2_LLM_MAX_LINES,
    SRC_MAX_LINES,
    TESTS_ALLOWLIST,
    TESTS_MAX_LINES,
    check_line_counts,
    check_tests_line_counts,
    is_exectv2_llm_production,
    src_root,
    tests_root as get_tests_root,
)


def test_production_tree_passes_line_count_gates(repo_root: Path) -> None:
    violations = check_line_counts(src_root(repo_root))
    assert violations == [], "\n".join(v.format() for v in violations)


def test_allowlist_paths_exist_under_src(repo_root: Path) -> None:
    package_root = src_root(repo_root)
    missing = [rel for rel in ALLOWLIST if not (package_root / rel).is_file()]
    assert missing == [], f"stale allowlist entries: {missing}"


def test_new_exectv2_llm_file_over_500_is_caught(tmp_path: Path) -> None:
    """A new 600-line module under exectv2/llm/ must fail without allowlisting."""
    package_root = tmp_path / "src" / "clinical_extraction"
    target = (
        package_root
        / "tasks/epilepsy_phenotyping/exectv2/llm/llm_new_monolith_candidate.py"
    )
    target.parent.mkdir(parents=True)
    target.write_text("\n".join(["# stub"] * 600), encoding="utf-8")

    violations = check_line_counts(package_root)
    assert len(violations) == 1
    violation = violations[0]
    assert violation.kind == "new"
    assert violation.line_count == 600
    assert "exectv2/llm" in violation.triggered_rules[0]
    assert is_exectv2_llm_production(violation.rel_path)


def test_prompts_subtree_exempt_from_exectv2_llm_gate(tmp_path: Path) -> None:
    package_root = tmp_path / "src" / "clinical_extraction"
    target = (
        package_root
        / "tasks/epilepsy_phenotyping/exectv2/llm/prompts/key_entities/big_prompt_data.py"
    )
    target.parent.mkdir(parents=True)
    target.write_text("\n".join(["PROMPT = 'x'"] * 700), encoding="utf-8")

    violations = check_line_counts(package_root)
    assert violations == []


def test_allowlisted_monolith_growth_is_caught(tmp_path: Path) -> None:
    # Use any current allowlist entry rather than hardcoding a path (paths churn
    # as monoliths are decomposed and their entries removed).
    rel = next(iter(ALLOWLIST))
    entry = ALLOWLIST[rel]
    package_root = tmp_path / "src" / "clinical_extraction"
    target = package_root / rel
    target.parent.mkdir(parents=True)
    target.write_text("\n".join(["# legacy"] * (entry.max_lines + 1)), encoding="utf-8")

    violations = check_line_counts(package_root)
    assert any(v.kind == "growth" and v.rel_path == rel for v in violations)


@pytest.mark.parametrize(
    ("limit_name", "limit_value"),
    [
        ("exectv2_llm", EXECTV2_LLM_MAX_LINES),
        ("src", SRC_MAX_LINES),
        ("tests", TESTS_MAX_LINES),
    ],
)
def test_gate_limits_documented(limit_name: str, limit_value: int) -> None:
    assert limit_value > 0
    assert limit_name in {"exectv2_llm", "src", "tests"}


def test_tests_tree_passes_line_count_gates(repo_root: Path) -> None:
    violations = check_tests_line_counts(get_tests_root(repo_root))
    assert violations == [], "\n".join(v.format() for v in violations)


def test_tests_allowlist_paths_exist_under_tests(repo_root: Path) -> None:
    tree_root = get_tests_root(repo_root)
    missing = [rel for rel in TESTS_ALLOWLIST if not (tree_root / rel).is_file()]
    assert missing == [], f"stale tests allowlist entries: {missing}"


def test_new_test_file_over_800_is_caught(tmp_path: Path) -> None:
    """A new 900-line module under tests/ must fail without allowlisting."""
    tree_root = tmp_path / "tests"
    target = tree_root / "test_new_megatest_candidate.py"
    target.parent.mkdir(parents=True)
    target.write_text("\n".join(["# stub"] * 900), encoding="utf-8")

    violations = check_tests_line_counts(tree_root)
    assert len(violations) == 1
    violation = violations[0]
    assert violation.kind == "new"
    assert violation.line_count == 900
    assert violation.triggered_rules == (f"tests≤{TESTS_MAX_LINES}",)


def test_allowlisted_megatest_growth_is_caught(tmp_path: Path) -> None:
    rel = "test_gan2026_pipeline_v1_extraction.py"
    entry = TESTS_ALLOWLIST[rel]
    tree_root = tmp_path / "tests"
    target = tree_root / rel
    target.parent.mkdir(parents=True)
    target.write_text("\n".join(["# legacy"] * (entry.max_lines + 1)), encoding="utf-8")

    violations = check_tests_line_counts(tree_root)
    assert any(v.kind == "growth" and v.rel_path == rel for v in violations)
