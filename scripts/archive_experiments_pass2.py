"""Second archive pass: move superseded experiments/*.md notes to experiments/archive/."""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
ARCHIVE = EXPERIMENTS / "archive"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"
ARCHIVE_INDEX_PATH = ARCHIVE / "ARCHIVE_INDEX.md"

ARCHIVE_DECISIONS = {
    "reject",
    "historical",
    "inform_architecture_loop",
    "inform_phase4",
    "inform_phase7",
    "inform_phase3",
    "phase4_complete",
    "phase3_complete_gpt41mini",
    "calibration_measure_val_to_test_gap",
}
KEEP_DECISIONS = {
    "promote",
    "promote_hybrid_structured_events_direction",
    "promote_to_phase3_report",
    "clinical_recovery_reporting",
    "reliability_scorecard",
    "revise",
}

PROTECT_SUBSTRINGS = (
    "exectv2_component_off_replay_",
    "gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate",
    "gan2026_v07_test450_",
    "gan2026_reliability_",
    "gan2026_test450_phase4_",
    "gan2026_fresh_evidence_reasoner_test450_",
    "gan2026_reset_clinical_assessment_pipeline_test450_",
    "exectv2_same_core_model_swap",
    "exectv2_2call_no_sf_adjudicator_",
    "exectv2_2call_no_sf_model_swap_",
    "exectv2_holistic_finding_assembly_v08_",
    "exectv2_v08_full200_",
    "exectv2_self_consistency_",
    "RUN_INDEX.md",
    "README.md",
)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def load_extra_protect() -> set[str]:
    protected: set[str] = set()
    for rel in (
        "docs/experiments/FROZEN_EVIDENCE_MANIFEST_2026-06-26.md",
        "experiments/README.md",
        "docs/experiments/final_artifact_index_2026-06-22.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for match in re.findall(r"experiments/[A-Za-z0-9_./-]+\.md", text):
            protected.add(match)
    return protected


def classify_bucket(filename: str) -> str:
    if filename.startswith("gan2026_reset_clinical_assessment_pipeline_validation750"):
        return "gan2026_validation750_iterations"
    if filename.startswith("gan2026_reset_clinical_assessment_pipeline_validation"):
        return "gan2026_validation_iterations"
    if filename.startswith("gan2026_llm_structured_validation"):
        return "gan2026_validation_iterations"
    if "validation750" in filename and filename.startswith("gan2026_"):
        return "gan2026_validation750_iterations"
    if filename.startswith("gan2026_section_claim_table_"):
        return "gan2026_validation_iterations"
    if filename.startswith("gan2026_hybrid_") and "validation" in filename:
        return "gan2026_validation_iterations"
    if filename.startswith("gan2026_agentic_") and "validation" in filename:
        return "gan2026_validation_iterations"
    if filename.startswith("gan2026_"):
        return "gan2026_misc_iterations"
    if filename.startswith("exectv2_target_indicators"):
        return "exectv2_target_indicators_iterations"
    if filename.startswith("diagnostic_"):
        return "exectv2_diagnostics"
    if filename.startswith("_tmp_") or filename.startswith("tmp_"):
        return "smoke_tmp"
    if filename.startswith("exectv2_"):
        return "exectv2_misc_iterations"
    return "misc_iterations"


def is_protected(rel: str, path_decision: dict[str, str | None], extra: set[str]) -> bool:
    if rel in extra:
        return True
    name = Path(rel).name
    if any(sub in name for sub in PROTECT_SUBSTRINGS):
        return True
    decision = path_decision.get(rel)
    if decision in KEEP_DECISIONS:
        return True
    return False


def should_archive(rel: str, path_decision: dict[str, str | None], extra: set[str]) -> str | None:
    if is_protected(rel, path_decision, extra):
        return None
    decision = path_decision.get(rel)
    if decision in ARCHIVE_DECISIONS:
        return decision or "registry"
    if decision is None:
        return "unregistered"
    return None


def update_registry_paths(moves: dict[str, str]) -> int:
    if not moves:
        return 0
    lines = REGISTRY_PATH.read_text(encoding="utf-8").splitlines()
    updated = 0
    out: list[str] = []
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        new_line = line
        for old, new in moves.items():
            if old in new_line:
                new_line = new_line.replace(old, new)
                updated += 1
        out.append(new_line)
    REGISTRY_PATH.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")
    return updated


def append_archive_index(bucket_counts: Counter[str], moved: list[tuple[str, str, str]]) -> None:
    existing = ARCHIVE_INDEX_PATH.read_text(encoding="utf-8")
    section = [
        "",
        "## Pass 2 (2026-06-26)",
        "",
        "Registry-filtered and unregistered iteration notes moved from `experiments/`.",
        "JSON/JSONL machine-readable artifacts remain in `experiments/` for reproduction.",
        "",
        "### Buckets",
        "",
    ]
    for bucket, count in sorted(bucket_counts.items()):
        section.append(f"- `{bucket}/` — {count} notes")
    section.extend(["", "<details><summary>File list</summary>", ""])
    for rel_old, rel_new, reason in sorted(moved, key=lambda x: x[1]):
        section.append(f"- `{rel_new}` (from `{Path(rel_old).name}`; {reason})")
    section.append("</details>")
    ARCHIVE_INDEX_PATH.write_text(existing.rstrip() + "\n" + "\n".join(section) + "\n", encoding="utf-8")


def main() -> None:
    extra_protect = load_extra_protect()
    path_decision: dict[str, str | None] = {}
    for line in REGISTRY_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        decision = row.get("decision")
        for raw in row.get("artifact_paths") or []:
            p = normalize_path(raw)
            if p.startswith("experiments/") and p.endswith(".md") and "/archive/" not in p:
                path_decision[p] = decision

    candidates: list[tuple[str, str]] = []
    for path in sorted(EXPERIMENTS.glob("*.md")):
        rel = path.as_posix()
        reason = should_archive(rel, path_decision, extra_protect)
        if reason:
            candidates.append((rel, reason))

    bucket_files: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    moves: dict[str, str] = {}
    for rel, reason in candidates:
        name = Path(rel).name
        bucket = classify_bucket(name)
        dest_rel = f"experiments/archive/{bucket}/{name}"
        dest = ROOT / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(rel, dest)
        moves[rel] = dest_rel
        bucket_files[bucket].append((rel, dest_rel, reason))

    registry_updates = update_registry_paths(moves)

    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
        load_run_registry,
        write_run_registry_markdown,
    )

    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)

    flat = [item for items in bucket_files.values() for item in items]
    append_archive_index(Counter({b: len(v) for b, v in bucket_files.items()}), flat)

    print(f"archived_md={len(candidates)}")
    print(f"buckets={dict(Counter({b: len(v) for b, v in bucket_files.items()}))}")
    print(f"registry_path_updates={registry_updates}")
    print(f"remaining_root_md={len(list(EXPERIMENTS.glob('*.md')))}")


if __name__ == "__main__":
    main()
