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

4. **Frontend tier** — any ``*.ts`` / ``*.tsx`` under ``frontend/`` (excluding
   ``node_modules/`` and ``.next/``) must be **≤ 600 lines** unless documented
   in ``FRONTEND_ALLOWLIST`` below.

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
FRONTEND_MAX_LINES = 600

SRC_PACKAGE = "src/clinical_extraction"
TESTS_DIR = "tests"
FRONTEND_DIR = "frontend"
FRONTEND_EXTENSIONS = (".ts", ".tsx")


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
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_clinical_findings.py": AllowlistEntry(
        80,
        "Wave C-S2: thin facade over pipelines/clinical_findings/ 3-stage package",
    ),
    # clinical_findings extract decomposed (Wave C-S6): extract now ~50 LOC;
    # prompt corpus in prompts/clinical_findings/, parsing in parsing.py.
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/clinical_findings/verify.py": AllowlistEntry(
        700,
        "Wave C-S2: clinical_findings stage 2 — verification prompts + decisions",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/clinical_findings/runner.py": AllowlistEntry(
        600,
        "Wave C-S2: clinical_findings run_split orchestration + reporting",
    ),
    # target_indicators_single_call decomposed (Wave C-S5): facade now 80 LOC (no entry).
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/target_indicators_single_call/projection_helpers.py": AllowlistEntry(
        880,
        "Wave C-S5: target_indicators decomposed; projection/repair leaf helpers (DAG) cohesive unit",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/target_indicators_single_call/prompt_builders.py": AllowlistEntry(
        527,
        "Wave C-S5: target_indicators decomposed; prompt builders cohesive unit",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/diagnosis_verification/acceptance_gate.py": AllowlistEntry(
        524,
        "P1-3: diagnosis_verification acceptance gate — prompt corpus externalization pending (P3-2)",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/diagnosis_verification/decomposer.py": AllowlistEntry(
        583,
        "P1-3: diagnosis_verification decomposer — prompt corpus externalization pending (P3-2)",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/diagnosis_verification/phase2_panel.py": AllowlistEntry(
        864,
        "P1-3: diagnosis_verification phase2 panel — prompt corpus externalization pending (P3-2)",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/diagnosis_verification/reconciler.py": AllowlistEntry(
        666,
        "P1-3: diagnosis_verification reconciler — prompt corpus externalization pending (P3-2)",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/entity_verifier/med_inv_content.py": AllowlistEntry(
        541,
        "P3-2: med_inv prompt corpus externalized; runner/orchestration remains",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_family_conditioned_candidate_adjudicator.py": AllowlistEntry(
        877,
        "A1: family-conditioned adjudication — extract shared scaffold",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_family_conditioned_event_ledger.py": AllowlistEntry(
        1292,
        "A1: family-conditioned ledger — split prompt corpus from orchestration",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_family_routed_llm_first.py": AllowlistEntry(
        1145,
        "A1: family-routed llm-first — split routing table from runner",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_all_entities.py": AllowlistEntry(
        790,
        "A1: all-entities orchestrator — pending decomposition",
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
    "tasks/seizure_frequency/gan2026/agentic/boundary_audit_prompt_v2.py": AllowlistEntry(
        1014,
        "Wave3-S3: migrate to AgenticStage scaffold + prompt externalization",
    ),
    "tasks/seizure_frequency/gan2026/agentic/consensus_fresh_agreement_selector.py": AllowlistEntry(
        1348,
        "Wave3-S3: migrate to AgenticStage scaffold",
    ),
    "tasks/seizure_frequency/gan2026/agentic/cross_model_structured_event_adjudicator.py": AllowlistEntry(
        1508,
        "Wave3-S3: migrate to AgenticStage scaffold",
    ),
    "tasks/seizure_frequency/gan2026/agentic/direct_boundary_critic_rescue.py": AllowlistEntry(
        1554,
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
    "tasks/seizure_frequency/gan2026/agentic/temporal_sentinel_specialist.py": AllowlistEntry(
        1114,
        "Wave3-S3: migrate to AgenticStage scaffold",
    ),
    "tasks/seizure_frequency/gan2026/artifact_analysis/reset_stage_component_ablation_v6.py": AllowlistEntry(
        1118,
        "Gan2026 artifact_analysis: ablation harness — move to experiments/",
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
    "tasks/seizure_frequency/gan2026/llm/llm_heavy_clinical_frequency_reasoner.py": AllowlistEntry(
        1270,
        "Gan2026 LLM: heavy frequency reasoner — pending decomposition",
    ),
    "tasks/seizure_frequency/gan2026/llm/llm_heavy_evidence_selection_with_deterministic_adapters.py": AllowlistEntry(
        1453,
        "Gan2026 LLM: heavy evidence selection — pending decomposition",
    ),
    "tasks/seizure_frequency/gan2026/llm/llm_only_direct_labeler.py": AllowlistEntry(
        1098,
        "Gan2026 LLM: direct labeler — pending decomposition",
    ),
    "tasks/seizure_frequency/gan2026/pipeline/stages/evidence_gating.py": AllowlistEntry(
        550,
        "Gan2026 pipeline: projection render evidence gating heuristics",
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
    "test_exectv2_target_indicators_single_call_seizure_frequency.py": AllowlistEntry(
        1723,
        "P0-6/Wave-C-S1: megatest — split SF indicator scenarios",
    ),
    "test_gan2026_hybrid_structured_events.py": AllowlistEntry(
        1607,
        "P0-6/Wave-C-S1: megatest — split hybrid event repair cases",
    ),
    "test_gan2026_llm_candidate_set_clinical_assessment_probe.py": AllowlistEntry(
        1541,
        "P0-6/Wave-C-S1: megatest — split candidate-set probe panels",
    ),
    "test_exectv2_llm_only_key_entities_generation_selection.py": AllowlistEntry(
        1470,
        "P0-6/Wave-C-S1: megatest — split generation/selection strategy cases",
    ),
    "test_gan2026_clinical_assessment_projection_render_repairs.py": AllowlistEntry(
        1449,
        "P0-6/Wave-C-S1: megatest — split projection render repair cases",
    ),
    "test_exectv2_scoring.py": AllowlistEntry(
        1641,
        "P0-6/Wave-C-S1: megatest — split scoring scenario tables",
    ),
    "test_gan2026_fresh_evidence_reasoner.py": AllowlistEntry(
        1302,
        "P0-6/Wave-C-S1: megatest — split fresh-evidence reasoner panels",
    ),
    "test_exectv2_deterministic_sf.py": AllowlistEntry(
        1262,
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
    "test_exectv2_llm_only_clinical_findings.py": AllowlistEntry(
        1159,
        "P0-6/Wave-C-S1: megatest — split clinical findings pipeline cases",
    ),
    "test_gan2026_consensus_fresh_agreement_selector.py": AllowlistEntry(
        1062,
        "P0-6/Wave-C-S1: megatest — split consensus selector panels",
    ),
    "test_gan2026_normalize.py": AllowlistEntry(
        1032,
        "P0-6/Wave-C-S1: megatest — split normalize rule tables",
    ),
    "test_gan2026_clinical_assessment_projection_render_instrumentation.py": AllowlistEntry(
        1013,
        "P0-6/Wave-C-S1: megatest — split projection render instrumentation",
    ),
    "test_exectv2_target_indicators_single_call_diagnosis.py": AllowlistEntry(
        948,
        "P0-6/Wave-C-S1: megatest — split diagnosis indicator scenarios",
    ),
    "test_gan2026_pipeline_v1.py": AllowlistEntry(
        889,
        "P0-6/Wave-C-S1: megatest — split pipeline v1 integration cases",
    ),
    "test_exectv2_clinical_finding_assembly.py": AllowlistEntry(
        833,
        "P0-6/Wave-C-S1: megatest — split clinical finding assembly cases",
    ),
    "test_gan2026_clinical_assessment_projection_render.py": AllowlistEntry(
        824,
        "P0-6/Wave-C-S1: megatest — split projection render cases",
    ),
    "test_exectv2_deterministic_all9.py": AllowlistEntry(
        840,
        "P0-6/Wave-C-S1: megatest — split all9 deterministic rule cases",
    ),
}

# Paths are posix-relative to ``frontend/``.
FRONTEND_ALLOWLIST: dict[str, AllowlistEntry] = {
    "lib/types/shared.ts": AllowlistEntry(
        632,
        "P2-6/Wave-C-S6: types split — shared cross-domain types pending further slice",
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


def frontend_root(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / FRONTEND_DIR


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


def iter_frontend_files(tree_root: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for path in sorted(tree_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in FRONTEND_EXTENSIONS:
            continue
        if "node_modules" in path.parts or ".next" in path.parts:
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


def check_frontend_line_counts(frontend_dir: Path | None = None) -> list[LineCountViolation]:
    """Return violations for the frontend tree (empty list = pass)."""
    root = frontend_root() if frontend_dir is None else frontend_dir
    violations: list[LineCountViolation] = []

    for rel_path, path in iter_frontend_files(root):
        line_count = count_lines(path)
        entry = FRONTEND_ALLOWLIST.get(rel_path)

        if line_count <= FRONTEND_MAX_LINES:
            continue

        if entry is not None and line_count <= entry.max_lines:
            continue

        if entry is None:
            violations.append(
                LineCountViolation(
                    rel_path=rel_path,
                    line_count=line_count,
                    triggered_rules=(f"frontend≤{FRONTEND_MAX_LINES}",),
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
                    triggered_rules=(f"frontend≤{FRONTEND_MAX_LINES}",),
                    kind="growth",
                    ceiling=entry.max_lines,
                    justification=entry.justification,
                )
            )

    return violations


def main() -> int:
    violations = (
        check_line_counts() + check_tests_line_counts() + check_frontend_line_counts()
    )
    if not violations:
        print("line-count gates: OK")
        return 0

    print("line-count gate violations:", file=sys.stderr)
    for violation in violations:
        print(f"  - {violation.format()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
