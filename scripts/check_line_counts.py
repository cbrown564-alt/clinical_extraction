#!/usr/bin/env python3
"""CI line-count gates to prevent monolith regression (Wave 3 Sprint 4 / Wave C Sprint 1).

Gate rules
----------
1. **ExECTv2 LLM tier** — any ``*.py`` under ``src/clinical_extraction/**/exectv2/llm/``
   except paths containing ``/prompts/`` must be **≤ 500 lines** (LOC = physical
   line count including blanks and comments).

2. **Production source tier** — any ``*.py`` under ``src/clinical_extraction/`` must be
   **≤ 1,000 lines** unless documented in ``ALLOWLIST`` below.

3. **Tests tier** (P0-6) — any ``*.py`` under ``tests/`` must be **≤ 800 lines**
   unless documented in ``TESTS_ALLOWLIST`` below.

Allowlist policy (day-1 rollout)
--------------------------------
Known legacy monoliths are allowlisted with a **frozen ceiling** equal to their
current line count. The gate **fails on**:

- **New violations** — a file exceeds a tier limit and is not allowlisted.
- **Growth** — an allowlisted file grows beyond its documented ceiling.

Shrinking an allowlisted file is always permitted. To add a new allowlisted
monolith, extend the relevant allowlist with a justification string referencing
the decomposition plan (see ``docs/plans/thermo_nuclear_code_quality_audit_plan_2026-06-26.md``).

How to run
----------
::

    python scripts/check_line_counts.py
    pytest tests/test_line_count_gates.py

Exit code 0 when clean; 1 when violations are printed to stderr.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

EXECTV2_LLM_MAX_LINES = 500
SRC_MAX_LINES = 1000
TESTS_MAX_LINES = 800
SRC_PACKAGE = "src/clinical_extraction"
TESTS_DIR = "tests"


@dataclass(frozen=True)
class AllowlistEntry:
    """Frozen line ceiling for a known legacy monolith."""

    max_lines: int
    justification: str


# Paths are posix-relative to ``src/clinical_extraction/``.
ALLOWLIST: dict[str, AllowlistEntry] = {
    # --- ExECTv2 LLM top-4 blockers (A1) ---
    # generation_selection decomposed (Wave C-S5): facade now 94 LOC (no entry);
    # cohesive package submodules over the 500 LLM tier are allowlisted below.
    # generation_selection decomposed (Wave C-S5/S7): parsing facade now ~35 LOC (no entry).
    # key_entities_structured decomposed (Wave C-S5/S7): prompt_builders facade now ~23 LOC (no entry).
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/runner.py": AllowlistEntry(
        588,
        "Wave C-S5: structured decomposed; run_split + report assembly cohesive unit",
    ),
    # clinical_findings extract decomposed (Wave C-S6): extract now ~50 LOC;
    # prompt corpus in prompts/clinical_findings/, parsing in parsing.py.
    # target_indicators_single_call decomposed (Wave C-S5): facade now 80 LOC (no entry).
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/diagnosis_verification/decomposer.py": AllowlistEntry(
        583,
        "P1-3: diagnosis_verification decomposer — prompt corpus externalization pending (P3-2)",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_per_entity.py": AllowlistEntry(
        1360,
        "A1: per-entity orchestrator — pending decomposition",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_single_pass.py": AllowlistEntry(
        850,
        "A1: single-pass orchestrator — pending decomposition",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_sf_state_adjudicator.py": AllowlistEntry(
        1222,
        "A1: SF state adjudicator — migrate to entity_verifier/sf pipeline",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_sf_union_arbitration.py": AllowlistEntry(
        515,
        "A1: SF union arbitration — pending decomposition",
    ),
    # --- ExECTv2 non-LLM >1k LOC ---
    # --- Gan2026 >1k LOC ---
    "tasks/seizure_frequency/gan2026/agentic/cross_model_structured_event_adjudicator.py": AllowlistEntry(
        1508,
        "Wave3-S3: migrate to AgenticStage scaffold",
    ),
    "tasks/seizure_frequency/gan2026/agentic/fresh_evidence_reasoner.py": AllowlistEntry(
        2145,
        "Gan2026 agentic: fresh evidence reasoner — legacy agentic monolith",
    ),
    "tasks/seizure_frequency/gan2026/agentic/llm_event_reasoner.py": AllowlistEntry(
        1071,
        "Wave3-S3: migrate to AgenticStage scaffold",
    ),
    "tasks/seizure_frequency/gan2026/agentic/structured_event_verifier.py": AllowlistEntry(
        1149,
        "Wave3-S3: migrate to AgenticStage scaffold",
    ),
    "tasks/seizure_frequency/gan2026/deterministic/rules/cluster.py": AllowlistEntry(
        1321,
        "Gan2026 deterministic rules: cluster — candidate for package split",
    ),
    "tasks/seizure_frequency/gan2026/deterministic/rules/diary.py": AllowlistEntry(
        1259,
        "Gan2026 deterministic rules: diary — candidate for package split",
    ),
    "tasks/seizure_frequency/gan2026/deterministic/rules/rate.py": AllowlistEntry(
        1296,
        "Gan2026 deterministic rules: rate — candidate for package split",
    ),
    "tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py": AllowlistEntry(
        1176,
        "C2: move inline repairs to shared StructuredRepairConfig registry",
    ),
    "tasks/seizure_frequency/gan2026/llm/llm_only_direct_labeler.py": AllowlistEntry(
        1104,
        "Gan2026 LLM: direct labeler — pending decomposition",
    ),
}

# Paths are posix-relative to ``tests/``.
TESTS_ALLOWLIST: dict[str, AllowlistEntry] = {
    "test_gan2026_pipeline_v1_extraction.py": AllowlistEntry(
        2069,
        "P0-6/Wave-C-S1: megatest — split into fixtures + per-stage cases",
    ),
    "test_exectv2_v09_dictionary_lenses.py": AllowlistEntry(
        1749,
        "P0-6/Wave-C-S1: megatest — extract lens table fixtures",
    ),
    "test_gan2026_hybrid_structured_events.py": AllowlistEntry(
        1607,
        "P0-6/Wave-C-S1: megatest — split hybrid event repair cases",
    ),
    "test_exectv2_llm_only_key_entities_generation_selection.py": AllowlistEntry(
        1470,
        "P0-6/Wave-C-S1: megatest — split generation/selection strategy cases",
    ),
    "test_exectv2_scoring.py": AllowlistEntry(
        1962,
        "P0-6/Wave-C-S1: megatest — split scoring scenario tables; SF-3 deconflated "
        "direction/magnitude projection tests (2026-07-08); point/range "
        "shape-equivalence fix tests (2026-07-08)",
    ),
    "test_gan2026_fresh_evidence_reasoner.py": AllowlistEntry(
        1302,
        "P0-6/Wave-C-S1: megatest — split fresh-evidence reasoner panels",
    ),
    "test_exectv2_deterministic_sf.py": AllowlistEntry(
        1296,
        "P0-6/Wave-C-S1: megatest — split deterministic SF rule cases",
    ),
    "test_gan2026_llm_pipeline_cli.py": AllowlistEntry(
        1179,
        "P0-6/Wave-C-S1: megatest — split CLI integration scenarios",
    ),
    "test_exectv2_llm_only_key_entities_structured.py": AllowlistEntry(
        1178,
        "P0-6/Wave-C-S1: megatest — split structured key-entity cases",
    ),
    "test_gan2026_normalize.py": AllowlistEntry(
        1032,
        "P0-6/Wave-C-S1: megatest — split normalize rule tables",
    ),
    "test_gan2026_pipeline_v1.py": AllowlistEntry(
        890,
        "P0-6/Wave-C-S1: megatest — split pipeline v1 integration cases",
    ),
    "test_exectv2_clinical_finding_assembly.py": AllowlistEntry(
        843,
        "P0-6/Wave-C-S1: megatest — split clinical finding assembly cases; "
        "point/range shape-equivalence disclosure comments (2026-07-08)",
    ),
    "test_exectv2_deterministic_all9.py": AllowlistEntry(
        840,
        "P0-6/Wave-C-S1: megatest — split all9 deterministic rule cases",
    ),
}


@dataclass(frozen=True)
class LineCountViolation:
    rel_path: str
    line_count: int
    triggered_rules: tuple[str, ...]
    kind: str  # "new" | "growth"
    ceiling: int | None
    justification: str | None

    def format(self) -> str:
        rules = ", ".join(self.triggered_rules)
        if self.kind == "new":
            return f"{self.rel_path}: {self.line_count} lines exceeds {rules} (not allowlisted)"
        return (
            f"{self.rel_path}: {self.line_count} lines exceeds allowlisted ceiling "
            f"{self.ceiling} ({rules}); {self.justification}"
        )


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def src_root(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "src" / "clinical_extraction"


def tests_root(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / TESTS_DIR


def is_exectv2_llm_production(rel_path: str) -> bool:
    return "exectv2/llm/" in rel_path and "/prompts/" not in rel_path


def count_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def iter_python_files(tree_root: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for path in sorted(tree_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(tree_root).as_posix()
        files.append((rel, path))
    return files


def iter_production_python_files(package_root: Path) -> list[tuple[str, Path]]:
    return iter_python_files(package_root)


def check_line_counts(package_root: Path | None = None) -> list[LineCountViolation]:
    """Return violations for the production tree (empty list = pass)."""
    root = src_root() if package_root is None else package_root
    violations: list[LineCountViolation] = []

    for rel_path, path in iter_production_python_files(root):
        line_count = count_lines(path)
        entry = ALLOWLIST.get(rel_path)

        triggered: list[str] = []
        if is_exectv2_llm_production(rel_path) and line_count > EXECTV2_LLM_MAX_LINES:
            triggered.append(f"exectv2/llm≤{EXECTV2_LLM_MAX_LINES}")
        if line_count > SRC_MAX_LINES:
            triggered.append(f"src≤{SRC_MAX_LINES}")

        if not triggered:
            continue

        if entry is not None and line_count <= entry.max_lines:
            continue

        if entry is None:
            violations.append(
                LineCountViolation(
                    rel_path=rel_path,
                    line_count=line_count,
                    triggered_rules=tuple(triggered),
                    kind="new",
                    ceiling=None,
                    justification=None,
                )
            )
        else:
            violations.append(
                LineCountViolation(
                    rel_path=rel_path,
                    line_count=line_count,
                    triggered_rules=tuple(triggered),
                    kind="growth",
                    ceiling=entry.max_lines,
                    justification=entry.justification,
                )
            )

    return violations


def check_tests_line_counts(tests_dir: Path | None = None) -> list[LineCountViolation]:
    """Return violations for the tests tree (empty list = pass)."""
    root = tests_root() if tests_dir is None else tests_dir
    violations: list[LineCountViolation] = []

    for rel_path, path in iter_python_files(root):
        line_count = count_lines(path)
        entry = TESTS_ALLOWLIST.get(rel_path)

        if line_count <= TESTS_MAX_LINES:
            continue

        if entry is not None and line_count <= entry.max_lines:
            continue

        if entry is None:
            violations.append(
                LineCountViolation(
                    rel_path=rel_path,
                    line_count=line_count,
                    triggered_rules=(f"tests≤{TESTS_MAX_LINES}",),
                    kind="new",
                    ceiling=None,
                    justification=None,
                )
            )
        else:
            violations.append(
                LineCountViolation(
                    rel_path=rel_path,
                    line_count=line_count,
                    triggered_rules=(f"tests≤{TESTS_MAX_LINES}",),
                    kind="growth",
                    ceiling=entry.max_lines,
                    justification=entry.justification,
                )
            )

    return violations


def main() -> int:
    violations = check_line_counts() + check_tests_line_counts()
    if not violations:
        print("line-count gates: OK")
        return 0

    print("line-count gate violations:", file=sys.stderr)
    for violation in violations:
        print(f"  - {violation.format()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
