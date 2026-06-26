#!/usr/bin/env python3
"""CI line-count gates to prevent monolith regression (Wave 3 Sprint 4).

Gate rules
----------
1. **ExECTv2 LLM tier** — any ``*.py`` under ``src/clinical_extraction/**/exectv2/llm/``
   except paths containing ``/prompts/`` must be **≤ 500 lines** (LOC = physical
   line count including blanks and comments).

2. **Production source tier** — any ``*.py`` under ``src/clinical_extraction/`` must be
   **≤ 1,000 lines** unless documented in the allowlist below.

Allowlist policy (day-1 rollout)
--------------------------------
Known legacy monoliths are allowlisted with a **frozen ceiling** equal to their
current line count. The gate **fails on**:

- **New violations** — a file exceeds a tier limit and is not allowlisted.
- **Growth** — an allowlisted file grows beyond its documented ceiling.

Shrinking an allowlisted file is always permitted. To add a new allowlisted
monolith, extend ``ALLOWLIST`` with a justification string referencing the
decomposition plan (see ``docs/plans/thermo_nuclear_code_quality_audit_plan_2026-06-26.md``).

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

SRC_PACKAGE = "src/clinical_extraction"


@dataclass(frozen=True)
class AllowlistEntry:
    """Frozen line ceiling for a known legacy monolith."""

    max_lines: int
    justification: str


# Paths are posix-relative to ``src/clinical_extraction/``.
ALLOWLIST: dict[str, AllowlistEntry] = {
    # --- ExECTv2 LLM top-4 blockers (A1) ---
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_key_entities_generation_selection.py": AllowlistEntry(
        4134,
        "A1/Wave3-S1: decompose into llm/pipelines/generation_selection/ strategy registry",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_key_entities_structured.py": AllowlistEntry(
        2606,
        "A1/Wave3-S2: externalize worked examples to prompts/**/*.yaml + thin orchestrator",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_only_clinical_findings.py": AllowlistEntry(
        3295,
        "A1: split into 3-stage pipeline package (extract, verify, finalize)",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_target_indicators_single_call.py": AllowlistEntry(
        2352,
        "A1/Wave3-S1: move _project_* / _repair_* to deterministic/target_projection/",
    ),
    # --- Other ExECTv2 LLM >500 LOC ---
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_diagnosis_acceptance_gate.py": AllowlistEntry(
        524,
        "A1: diagnosis verifier chain — migrate to pipelines/entity_verifier/",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_diagnosis_decomposer.py": AllowlistEntry(
        583,
        "A1: diagnosis verifier chain — migrate to pipelines/entity_verifier/",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_diagnosis_phase2_panel.py": AllowlistEntry(
        864,
        "A1: diagnosis verifier chain — migrate to pipelines/entity_verifier/",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_diagnosis_reconciler.py": AllowlistEntry(
        666,
        "A1: diagnosis verifier chain — migrate to pipelines/entity_verifier/",
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
        1206,
        "A1: SF state adjudicator — migrate to entity_verifier/sf pipeline",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_sf_state_projection.py": AllowlistEntry(
        767,
        "A1: SF state projection — pending decomposition",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/llm_sf_union_arbitration.py": AllowlistEntry(
        515,
        "A1: SF union arbitration — pending decomposition",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/entity_verifier/diagnosis_content.py": AllowlistEntry(
        929,
        "Wave2: entity_verifier diagnosis content — externalize prompts",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/entity_verifier/med_inv_content.py": AllowlistEntry(
        705,
        "Wave2: entity_verifier med_inv content — externalize prompts",
    ),
    "tasks/epilepsy_phenotyping/exectv2/llm/pipelines/entity_verifier/sf_content.py": AllowlistEntry(
        851,
        "Wave2: entity_verifier SF content — externalize prompts",
    ),
    # --- ExECTv2 non-LLM >1k LOC ---
    "tasks/epilepsy_phenotyping/exectv2/assembly/lenses.py": AllowlistEntry(
        1179,
        "Wave1: lens assembly — data-driven lens_from_manifest; further split deferred",
    ),
    "tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities.py": AllowlistEntry(
        1455,
        "ExECTv2 deterministic: all_entities rule cluster — candidate for package split",
    ),
    "tasks/epilepsy_phenotyping/exectv2/deterministic/conventions/seizure_frequency.py": AllowlistEntry(
        1728,
        "B2: externalize to conventions/data/seizure_frequency.yaml",
    ),
    "tasks/epilepsy_phenotyping/exectv2/deterministic/rules/rate.py": AllowlistEntry(
        1203,
        "ExECTv2 deterministic: rate rules — candidate for package split",
    ),
    "tasks/epilepsy_phenotyping/exectv2/reports/component_ablation_replay.py": AllowlistEntry(
        1474,
        "Wave2/B1: externalize experiment catalog to YAML",
    ),
    "tasks/epilepsy_phenotyping/exectv2/reports/cross_model_reliability_analysis.py": AllowlistEntry(
        1554,
        "Wave2/B1: externalize experiment catalog to YAML",
    ),
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
    "tasks/seizure_frequency/gan2026/runner.py": AllowlistEntry(
        1103,
        "Gan2026 runner — extract stage wiring to pipeline package",
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


def is_exectv2_llm_production(rel_path: str) -> bool:
    return "exectv2/llm/" in rel_path and "/prompts/" not in rel_path


def count_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def iter_production_python_files(package_root: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for path in sorted(package_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(package_root).as_posix()
        files.append((rel, path))
    return files


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


def main() -> int:
    violations = check_line_counts()
    if not violations:
        print("line-count gates: OK")
        return 0

    print("line-count gate violations:", file=sys.stderr)
    for violation in violations:
        print(f"  - {violation.format()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
