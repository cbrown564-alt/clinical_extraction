"""Pytest wrapper for production line-count gates (Wave 3 Sprint 4)."""

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
    check_line_counts,
    is_exectv2_llm_production,
    src_root,
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
    rel = "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_key_entities_generation_selection.py"
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
    ],
)
def test_gate_limits_documented(limit_name: str, limit_value: int) -> None:
    assert limit_value > 0
    assert limit_name in {"exectv2_llm", "src"}
