"""Run direct-labeler coverage smoke on unrecalled assembly failures."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import dspy

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    change_only_det_state_family_experiment as verifier_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    combined_change_only_switch_layer_experiment as combined_experiment,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    change_only_candidate_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm_only_direct_labeler
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

DATE = "2026-06-05"
MODEL = "openai/gpt-4.1"
POLICY_NAME = "gan2026_direct_labeler_unrecalled_failure_slice_v0"
TARGETED_POLICY_NAME = "gan2026_direct_labeler_targeted_switch_v0"
DEFAULT_RECOVERABILITY_CSV_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "failure_recoverability_2026-06-05.csv"
)
DEFAULT_COMPONENT_MATRIX_CSV_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_"
    "component_matrix_2026-06-04.csv"
)
DEFAULT_COMBINED_VALIDATION_JSONL_PATH = Path(
    "experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.jsonl"
)
DEFAULT_TEST_INPUT_PATH = combined_experiment.DEFAULT_TEST_INPUT_PATH
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.md"
)
DEFAULT_TEST_JSON_PATH = Path(
    "experiments/gan2026_direct_labeler_targeted_switch_test450_aggregate_audit_2026-06-05.json"
)
DEFAULT_TEST_REPORT_PATH = Path(
    "experiments/gan2026_direct_labeler_targeted_switch_test450_aggregate_audit_2026-06-05.md"
)
TARGET_RECOVERABILITY_CLASSES = {"no_recalled_candidate", "semantic_state_only"}


def build_failure_slice(
    recoverability_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return the validation failure rows that need new candidate generation."""

    rows = []
    for row in recoverability_rows:
        if row["recoverability_class"] not in TARGET_RECOVERABILITY_CLASSES:
            continue
        rows.append(
            {
                "source_row_index": int(row["source_row_index"]),
                "recoverability_class": row["recoverability_class"],
                "failure_transition": row["failure_transition"],
                "current_label": _normalized_label(row["prediction_label"]),
                "gold_label": _normalized_label(row["gold_label"]),
            }
        )
    return sorted(rows, key=lambda item: int(item["source_row_index"]))


def build_control_slice(
    component_matrix_rows: Sequence[Mapping[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    """Return deterministic validation controls where the current assembly is correct."""

    rows = []
    for row in component_matrix_rows:
        if row["final_action"] != "predict" or row["final_purist_correct"] != "True":
            continue
        rows.append(
            {
                "source_row_index": int(row["source_row_index"]),
                "recoverability_class": "current_correct_control",
                "failure_transition": "C_to_C",
                "current_label": _normalized_label(row["prediction_label"]),
                "gold_label": _normalized_label(row["gold_label"]),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def build_full_validation_slice(
    combined_validation_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Use the combined switch-layer label as the full-validation current label."""

    rows = []
    for row in combined_validation_rows:
        current_label = _normalized_label(row["final_label"])
        gold_label = _normalized_label(row["gold_label"])
        current_correct = _purist_correct(current_label, gold_label)
        rows.append(
            {
                "source_row_index": int(row["source_row_index"]),
                "recoverability_class": "full_validation_candidate_surface",
                "failure_transition": "C_to_C" if current_correct else "W_to_W",
                "current_label": current_label,
                "gold_label": gold_label,
            }
        )
    return sorted(rows, key=lambda item: int(item["source_row_index"]))


def run_live_slice(
    slice_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    records = [records_by_source[int(row["source_row_index"])] for row in slice_rows]
    direct_rows, direct_metadata = llm_only_direct_labeler.run_split(
        records,
        split="validation",
        split_manifest="gan2026_split_v1",
        model=model,
        temperature=0.0,
        max_tokens=max_tokens,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=(
            "validation-only hard slice over unrecalled/semantic-state assembly failures"
        ),
        progress_every=progress_every,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )
    rows = merge_direct_rows(slice_rows, direct_rows)
    return rows, summarize_rows(rows, direct_metadata, model=model)


def merge_direct_rows(
    slice_rows: Sequence[Mapping[str, Any]],
    direct_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    slice_by_source = {int(row["source_row_index"]): row for row in slice_rows}
    rows = []
    for direct in direct_rows:
        idx = int(direct["source_row_index"])
        slice_row = slice_by_source[idx]
        decision = direct.get("decision_record") or {}
        current_label = _normalized_label(slice_row["current_label"])
        direct_label = _normalized_label(decision.get("final_label"))
        gold_label = _normalized_label(slice_row["gold_label"])
        current_correct = _purist_correct(current_label, gold_label)
        direct_correct = _purist_correct(direct_label, gold_label)
        rows.append(
            {
                "artifact_kind": "gan2026_direct_labeler_unrecalled_failure_slice_row",
                "date": DATE,
                "policy_name": POLICY_NAME,
                "source_row_index": idx,
                "split": "validation",
                "split_manifest": "gan2026_split_v1",
                "recoverability_class": slice_row["recoverability_class"],
                "failure_transition": slice_row["failure_transition"],
                "current_label": current_label,
                "direct_label": direct_label,
                "gold_label": gold_label,
                "current_purist_correct": current_correct,
                "direct_purist_correct": direct_correct,
                "transition": change_only_candidate_verifier.transition(
                    current_correct,
                    direct_correct,
                ),
                "evidence_valid": bool(direct.get("evidence_valid")),
                "parse_errors": direct.get("parse_errors") or [],
                "call_error": direct.get("call_error"),
                "decision_record": decision,
                "raw_output": direct.get("raw_output"),
            }
        )
    return rows


def reparse_saved_rows(
    slice_rows: Sequence[Mapping[str, Any]],
    saved_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Re-score saved raw outputs after parser/schema repairs without new calls."""

    records_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    direct_rows = []
    for row in saved_rows:
        raw_output = str(row.get("raw_output") or "")
        decision, parse_errors = (
            llm_only_direct_labeler.parse_decision_json(raw_output)
            if raw_output
            else (None, ["not_run"])
        )
        record = records_by_source[int(row["source_row_index"])]
        evidence_valid = (
            evidence_is_substring(record.note_text, decision.evidence)
            if decision and decision.evidence
            else False
        )
        direct_rows.append(
            {
                "source_row_index": int(row["source_row_index"]),
                "decision_record": decision.model_dump() if decision else None,
                "evidence_valid": evidence_valid,
                "parse_errors": parse_errors,
                "call_error": row.get("call_error"),
                "raw_output": raw_output,
            }
        )
    return merge_direct_rows(slice_rows, direct_rows)


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    direct_metadata: Mapping[str, Any] | None,
    *,
    model: str,
) -> dict[str, Any]:
    transitions = Counter(str(row["transition"]) for row in rows)
    classes = Counter(str(row["recoverability_class"]) for row in rows)
    base_full_correct = 708
    projected_full_correct = base_full_correct + transitions["W_to_C"] - transitions["C_to_W"]
    return {
        "artifact_kind": "gan2026_direct_labeler_unrecalled_failure_slice_summary",
        "date": DATE,
        "model": model,
        "prompt_version": llm_only_direct_labeler.PROMPT_VERSION,
        "policy_name": POLICY_NAME,
        "claim_boundary": (
            "Validation-development hard-slice smoke over unrecalled and semantic-state "
            "assembly failures. This does not inspect locked test rows or authorize "
            "benchmark-comparable claims."
        ),
        "target_recoverability_classes": sorted(TARGET_RECOVERABILITY_CLASSES),
        "metrics": {
            "row_count": len(rows),
            "call_ok_rows": sum(not row["call_error"] for row in rows),
            "parse_ok_rows": sum(not row["parse_errors"] for row in rows),
            "exact_evidence_rows": sum(bool(row["evidence_valid"]) for row in rows),
            "direct_correct_rows": sum(bool(row["direct_purist_correct"]) for row in rows),
            "direct_slice_purist_proxy": _rate(
                sum(bool(row["direct_purist_correct"]) for row in rows),
                len(rows),
            ),
            "slice_w_to_c_rows": transitions["W_to_C"],
            "slice_c_to_w_rows": transitions["C_to_W"],
            "base_full_correct_rows": base_full_correct,
            "projected_full_correct_rows_if_oracle_switched_slice": projected_full_correct,
            "projected_full_purist_proxy_if_oracle_switched_slice": _rate(
                projected_full_correct,
                750,
            ),
        },
        "transition_counts": dict(sorted(transitions.items())),
        "recoverability_class_counts": dict(sorted(classes.items())),
        "direct_labeler_summary": (direct_metadata or {}).get("summary"),
        "decision": (
            "promising_candidate_generator_needs_gating"
            if transitions["W_to_C"] >= 10 and transitions["C_to_W"] == 0
            else "reject_as_broad_switch_source"
        ),
    }


def build_verifier_panel_rows(
    direct_paths: Sequence[Path],
) -> list[dict[str, Any]]:
    """Build change-only verifier inputs from direct-labeler candidate rows."""

    records_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    panel_rows = []
    for path in direct_paths:
        for row in load_jsonl_rows(path):
            direct_label = _normalized_label(row.get("direct_label"))
            current_label = _normalized_label(row.get("current_label"))
            if (
                not direct_label
                or direct_label == current_label
                or not row.get("evidence_valid")
            ):
                continue
            decision = row.get("decision_record") or {}
            record = records_by_source[int(row["source_row_index"])]
            panel_rows.append(
                {
                    "source_row_index": int(row["source_row_index"]),
                    "split": "validation",
                    "split_manifest": "gan2026_split_v1",
                    "clinical_text": record.note_text,
                    "gold_label": row["gold_label"],
                    "current_label": current_label,
                    "proposed_label": direct_label,
                    "proposed_evidence": str(decision.get("evidence") or ""),
                    "candidate_source": "llm_only_direct_labeler_raw",
                    "candidate_kind": str(decision.get("answer_kind") or ""),
                    "candidate_id": f"direct_labeler:{row['source_row_index']}",
                    "recoverability_class": row.get("recoverability_class"),
                    "direct_transition": row.get("transition"),
                    "whole_validation_base_correct_rows": 708,
                }
            )
    return sorted(panel_rows, key=lambda item: int(item["source_row_index"]))


def run_verifier_panel(
    panel_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    progress_every: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output_rows = []
    for index, row in enumerate(panel_rows, 1):
        output_rows.append(
            verifier_experiment._run_row(
                row,
                model=model,
                max_tokens=max_tokens,
                raw_reuse={},
            )
        )
        if progress_every and index % progress_every == 0:
            summary = change_only_candidate_verifier.summarize_rows(output_rows)
            print(
                f"processed={index}/{len(panel_rows)} "
                f"transitions={summary['transition_counts']}"
            )
    return output_rows, summarize_verifier_rows(output_rows, model=model)


def summarize_verifier_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
) -> dict[str, Any]:
    summary = change_only_candidate_verifier.summarize_rows(rows)
    transitions = Counter(str(row["transition"]) for row in rows)
    base_full_correct = 708
    projected_full_correct = base_full_correct + transitions["W_to_C"] - transitions["C_to_W"]
    return {
        "artifact_kind": "gan2026_direct_labeler_change_only_verifier_panel_summary",
        "date": DATE,
        "model": model,
        "prompt_version": change_only_candidate_verifier.POLICY_NAME,
        "policy_name": "gan2026_direct_labeler_change_only_verifier_panel_v0",
        "claim_boundary": (
            "Validation-development verifier panel over exact-evidence direct-labeler "
            "alternatives from hard failures and current-correct controls. Gold labels are "
            "used only for validation accounting."
        ),
        "metrics": {
            "row_count": len(rows),
            "call_ok_rows": sum(row["call_status"] == "ok" for row in rows),
            "parse_ok_rows": sum(not row["parse_errors"] for row in rows),
            "all_evidence_quotes_exact_rows": sum(
                bool(row["verifier_decision"]["all_evidence_quotes_exact"])
                for row in rows
            ),
            "panel_base_correct_rows": summary["base_correct_rows"],
            "panel_projected_correct_rows": summary["projected_correct_rows"],
            "panel_projected_purist_proxy": summary["projected_purist_proxy"],
            "base_full_correct_rows": base_full_correct,
            "projected_full_correct_rows": projected_full_correct,
            "projected_full_purist_proxy": _rate(projected_full_correct, 750),
            "changed_label_precision": summary["changed_label_precision"],
        },
        "transition_counts": summary["transition_counts"],
        "recommendation_counts": summary["recommendation_counts"],
        "decision": (
            "promote_to_full_validation_candidate"
            if transitions["W_to_C"] > 0 and transitions["C_to_W"] == 0
            else "reject_or_revise_verifier_gate"
        ),
    }


def targeted_policy_family(current_label: Any, proposed_label: Any) -> str:
    """Return the frozen targeted-switch family, or keep_current."""

    current = _normalized_label(current_label) or ""
    proposed = _normalized_label(proposed_label) or ""
    if proposed == "unknown" and current.startswith("seizure free"):
        return "direct_unknown_from_current_seizure_free"
    if "cluster per" in proposed and "per cluster" in proposed:
        return "direct_cluster_per_cluster_completion"
    if proposed == "1 per day" and "per day" not in current:
        return "direct_daily_upgrade_from_non_daily_current"
    return "keep_current"


def run_targeted_switch_test_aggregate_audit(
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    direct_max_tokens: int,
    verifier_max_tokens: int,
    progress_every: int,
) -> dict[str, Any]:
    """Run the frozen targeted switch on locked test and keep only aggregates."""

    dspy.configure(
        lm=build_dspy_lm(
            model,
            temperature=0.0,
            max_tokens=direct_max_tokens,
            cache=True,
            timeout=90,
        )
    )
    direct_program = llm_only_direct_labeler.DspyLlmOnlyDirectLabelerExtractor()
    aggregate_rows = []
    for index, test_row in enumerate(test_rows, 1):
        aggregate_rows.append(
            _run_targeted_switch_test_row(
                test_row,
                direct_program=direct_program,
                model=model,
                direct_max_tokens=direct_max_tokens,
                verifier_max_tokens=verifier_max_tokens,
            )
        )
        if progress_every and index % progress_every == 0:
            partial = _summarize_targeted_aggregate_rows(aggregate_rows)
            print(
                f"processed={index}/{len(test_rows)} "
                f"targeted_transitions={partial['targeted_transition_counts']} "
                f"final_correct={partial['final_correct_rows']}",
                flush=True,
            )
    return summarize_targeted_switch_test_rows(
        aggregate_rows,
        test_rows,
        model=model,
        direct_max_tokens=direct_max_tokens,
        verifier_max_tokens=verifier_max_tokens,
    )


def summarize_targeted_switch_test_rows(
    rows: Sequence[Mapping[str, Any]],
    test_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    direct_max_tokens: int,
    verifier_max_tokens: int,
) -> dict[str, Any]:
    targeted = _summarize_targeted_aggregate_rows(rows)
    raw_base_correct = sum(
        bool(row["score_layers"]["hybrid_adjudicator_raw"]["purist_correct"])
        for row in test_rows
    )
    row_count = len(test_rows)
    return {
        "artifact_kind": "gan2026_direct_labeler_targeted_switch_test450_aggregate_audit",
        "date": DATE,
        "model": model,
        "direct_max_tokens": direct_max_tokens,
        "verifier_max_tokens": verifier_max_tokens,
        "policy_name": TARGETED_POLICY_NAME,
        "source_artifact": str(DEFAULT_TEST_INPUT_PATH),
        "claim_boundary": (
            "Frozen locked-test aggregate-only audit for the direct-labeler targeted "
            "switch over the combined switch-layer current label. This artifact omits "
            "test row ids, clinical text, raw model outputs, and row-level failures."
        ),
        "policy_rules": [
            "direct_unknown_from_current_seizure_free",
            "direct_cluster_per_cluster_completion",
            "direct_daily_upgrade_from_non_daily_current",
        ],
        "metrics": {
            "test_rows": row_count,
            "raw_base_correct_rows": raw_base_correct,
            "combined_current_correct_rows": targeted["combined_correct_rows"],
            "final_correct_rows": targeted["final_correct_rows"],
            "raw_base_purist_proxy": _rate(raw_base_correct, row_count),
            "combined_current_purist_proxy": _rate(
                targeted["combined_correct_rows"],
                row_count,
            ),
            "final_purist_proxy": _rate(targeted["final_correct_rows"], row_count),
            "combined_changed_rows": targeted["combined_changed_rows"],
            "targeted_selected_rows": targeted["targeted_selected_rows"],
            "direct_call_ok_rows": targeted["direct_call_ok_rows"],
            "direct_parse_ok_rows": targeted["direct_parse_ok_rows"],
            "direct_exact_evidence_rows": targeted["direct_exact_evidence_rows"],
            "targeted_verifier_call_ok_rows": targeted["targeted_verifier_call_ok_rows"],
            "targeted_changed_label_precision": _rate(
                targeted["targeted_transition_counts"].get("W_to_C", 0),
                targeted["targeted_transition_counts"].get("W_to_C", 0)
                + targeted["targeted_transition_counts"].get("C_to_W", 0),
            ),
        },
        "combined_transition_counts": targeted["combined_transition_counts"],
        "targeted_transition_counts": targeted["targeted_transition_counts"],
        "combined_family_counts": targeted["combined_family_counts"],
        "targeted_family_counts": targeted["targeted_family_counts"],
        "targeted_verifier_action_counts": targeted["targeted_verifier_action_counts"],
        "decision": (
            "meets_requested_test_threshold"
            if _rate(targeted["final_correct_rows"], row_count) >= 0.9
            else "does_not_meet_goal"
        ),
    }


def write_targeted_test_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Direct Labeler Targeted Switch Test450 Aggregate Audit",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Artifacts",
        "",
        f"- Summary JSON: `{json_path}`",
        f"- Source artifact: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    for title, key in [
        ("Combined Transitions", "combined_transition_counts"),
        ("Targeted Transitions", "targeted_transition_counts"),
        ("Combined Families", "combined_family_counts"),
        ("Targeted Families", "targeted_family_counts"),
        ("Targeted Verifier Actions", "targeted_verifier_action_counts"),
    ]:
        lines.extend(["", f"## {title}", "", "| Value | Rows |", "| --- | ---: |"])
        for item, value in metadata[key].items():
            lines.append(f"| `{item}` | {value} |")
    lines.extend(
        [
            "",
            "## Inspection Boundary",
            "",
            "No test row ids, clinical text, raw model outputs, or row-level failures are "
            "stored in this report.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_targeted_switch_test_row(
    test_row: Mapping[str, Any],
    *,
    direct_program: llm_only_direct_labeler.DspyLlmOnlyDirectLabelerExtractor,
    model: str,
    direct_max_tokens: int,
    verifier_max_tokens: int,
) -> dict[str, Any]:
    raw_current_label = _normalized_label(
        test_row["score_layers"]["hybrid_adjudicator_raw"]["final_label"]
    )
    gold_label = _normalized_label(test_row["reference"]["gold_normalized_label"])
    combined_label, combined_family, combined_call_ok = _combined_test_label(
        test_row,
        raw_current_label,
        gold_label,
        model=model,
        max_tokens=verifier_max_tokens,
    )
    direct = _direct_test_candidate(
        test_row,
        direct_program=direct_program,
        current_label=combined_label,
    )
    targeted_family = targeted_policy_family(combined_label, direct["label"])
    final_label = combined_label
    verifier_call_ok = None
    verifier_action = "not_run"
    if (
        targeted_family != "keep_current"
        and direct["label"]
        and direct["evidence_valid"]
        and direct["label"] != combined_label
    ):
        verifier_row = {
            "source_row_index": int(test_row["source_row_index"]),
            "split": "test",
            "split_manifest": test_row.get("split_manifest", "gan2026_split_v1"),
            "clinical_text": str(test_row["component_inputs"]["note_text"]),
            "gold_label": gold_label,
            "current_label": combined_label,
            "proposed_label": direct["label"],
            "proposed_evidence": direct["evidence"],
            "candidate_source": "llm_only_direct_labeler_raw",
            "candidate_kind": direct["answer_kind"],
            "candidate_id": "direct_labeler:test",
        }
        result = verifier_experiment._run_row(
            verifier_row,
            model=model,
            max_tokens=verifier_max_tokens,
            raw_reuse={},
        )
        verifier_call_ok = result["call_status"] == "ok"
        verifier_action = str(result["verifier_decision"]["action"])
        decision_label = _normalized_label(result["verifier_decision"]["label"])
        if verifier_action == "switch_to_proposed" and decision_label:
            final_label = decision_label
        else:
            targeted_family = "keep_current"
    raw_correct = _purist_correct(raw_current_label, gold_label)
    combined_correct = _purist_correct(combined_label, gold_label)
    final_correct = _purist_correct(final_label, gold_label)
    return {
        "raw_correct": raw_correct,
        "combined_correct": combined_correct,
        "final_correct": final_correct,
        "combined_transition": change_only_candidate_verifier.transition(
            raw_correct,
            combined_correct,
        ),
        "targeted_transition": change_only_candidate_verifier.transition(
            combined_correct,
            final_correct,
        ),
        "combined_family": combined_family,
        "targeted_family": targeted_family,
        "combined_call_ok": combined_call_ok,
        "direct_call_ok": direct["call_ok"],
        "direct_parse_ok": direct["parse_ok"],
        "direct_evidence_valid": direct["evidence_valid"],
        "targeted_verifier_call_ok": verifier_call_ok,
        "targeted_verifier_action": verifier_action,
    }


def _combined_test_label(
    test_row: Mapping[str, Any],
    current_label: str | None,
    gold_label: str | None,
    *,
    model: str,
    max_tokens: int,
) -> tuple[str | None, str, bool]:
    final_label = current_label
    selected_family = "keep_current"
    call_ok = True
    for family_name, candidate in [
        (
            "det_state_exact",
            combined_experiment._test_det_state_candidate(test_row, current_label),
        ),
        (
            "llm_selector_exact",
            combined_experiment._test_llm_candidate(test_row, current_label),
        ),
    ]:
        if not candidate:
            continue
        run_row = {
            "source_row_index": int(test_row["source_row_index"]),
            "split": "test",
            "split_manifest": test_row.get("split_manifest", "gan2026_split_v1"),
            "clinical_text": str(test_row["component_inputs"]["note_text"]),
            "gold_label": gold_label,
            "current_label": current_label,
            "proposed_label": candidate["proposed_label"],
            "proposed_evidence": candidate["proposed_evidence"],
            "candidate_source": candidate["candidate_source"],
            "candidate_kind": candidate["candidate_kind"],
            "candidate_id": candidate["candidate_id"],
        }
        result = verifier_experiment._run_row(
            run_row,
            model=model,
            max_tokens=max_tokens,
            raw_reuse={},
        )
        call_ok = call_ok and result["call_status"] == "ok"
        decision_label = _normalized_label(result["verifier_decision"]["label"])
        if decision_label and decision_label != current_label:
            final_label = decision_label
            selected_family = family_name
            break
    return final_label, selected_family, call_ok


def _direct_test_candidate(
    test_row: Mapping[str, Any],
    *,
    direct_program: llm_only_direct_labeler.DspyLlmOnlyDirectLabelerExtractor,
    current_label: str | None,
) -> dict[str, Any]:
    note_text = str(test_row["component_inputs"]["note_text"])
    record = SimpleNamespace(
        source_row_index=int(test_row["source_row_index"]),
        note_text=note_text,
    )
    raw_output = ""
    call_ok = True
    try:
        prediction = direct_program(
            prompt_input_json=llm_only_direct_labeler.build_prompt_input(record)
        )
        raw_output = str(prediction.decision_json)
    except Exception:
        call_ok = False
    decision, parse_errors = (
        llm_only_direct_labeler.parse_decision_json(raw_output)
        if raw_output
        else (None, ["not_run"])
    )
    label = _normalized_label(decision.final_label) if decision else None
    evidence = str(decision.evidence) if decision else ""
    return {
        "call_ok": call_ok,
        "parse_ok": not parse_errors,
        "label": label if label != current_label else None,
        "evidence": evidence,
        "evidence_valid": evidence_is_substring(note_text, evidence) if evidence else False,
        "answer_kind": str(decision.answer_kind) if decision else "",
    }


def _summarize_targeted_aggregate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "combined_correct_rows": sum(bool(row["combined_correct"]) for row in rows),
        "final_correct_rows": sum(bool(row["final_correct"]) for row in rows),
        "combined_changed_rows": sum(row["combined_family"] != "keep_current" for row in rows),
        "targeted_selected_rows": sum(row["targeted_family"] != "keep_current" for row in rows),
        "direct_call_ok_rows": sum(bool(row["direct_call_ok"]) for row in rows),
        "direct_parse_ok_rows": sum(bool(row["direct_parse_ok"]) for row in rows),
        "direct_exact_evidence_rows": sum(bool(row["direct_evidence_valid"]) for row in rows),
        "targeted_verifier_call_ok_rows": sum(
            row["targeted_verifier_call_ok"] is True for row in rows
        ),
        "combined_transition_counts": dict(
            sorted(Counter(str(row["combined_transition"]) for row in rows).items())
        ),
        "targeted_transition_counts": dict(
            sorted(Counter(str(row["targeted_transition"]) for row in rows).items())
        ),
        "combined_family_counts": dict(
            sorted(Counter(str(row["combined_family"]) for row in rows).items())
        ),
        "targeted_family_counts": dict(
            sorted(Counter(str(row["targeted_family"]) for row in rows).items())
        ),
        "targeted_verifier_action_counts": dict(
            sorted(Counter(str(row["targeted_verifier_action"]) for row in rows).items())
        ),
    }


def write_verifier_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Direct Labeler Change-Only Verifier Panel",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for key, value in metadata["transition_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Recommendations", "", "| Recommendation | Rows |", "| --- | ---: |"])
    for key, value in metadata["recommendation_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Changed Rows",
            "",
            "| Row | Current | Proposed | Transition | Recommendation |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["transition"] in {"C_to_C", "W_to_W"}:
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['current_label']}` | "
            f"`{row['proposed_label']}` | `{row['transition']}` | "
            f"`{row['verifier_decision']['action']}` |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Direct Labeler Unrecalled Failure Slice",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Transitions", "", "| Transition | Rows |", "| --- | ---: |"])
    for key, value in metadata["transition_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Recoverability Classes", "", "| Class | Rows |", "| --- | ---: |"])
    for key, value in metadata["recoverability_class_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Class | Current | Direct | Gold | Transition | Evidence exact |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['recoverability_class']}` | "
            f"`{row['current_label'] or ''}` | `{row['direct_label'] or ''}` | "
            f"`{row['gold_label'] or ''}` | `{row['transition']}` | "
            f"{row['evidence_valid']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "This hard slice is intentionally enriched for current validation failures. Its "
            "slice accuracy is not a full-validation score; it only estimates whether a "
            "direct-label candidate source creates useful alternatives for rows that "
            "saved candidate discovery missed.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_recoverability_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _normalized_label(label: Any) -> str | None:
    if not label:
        return None
    try:
        return label_to_frequency_record(str(label)).normalized_label
    except ValueError:
        return None


def _purist_correct(label: Any, gold_label: Any) -> bool:
    try:
        prediction = label_to_frequency_record(str(label))
        gold = label_to_frequency_record(str(gold_label))
    except ValueError:
        return False
    return map_purist(prediction.monthly_frequency) == map_purist(gold.monthly_frequency)


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["live", "analyze", "verify", "test-aggregate"],
        default="live",
    )
    parser.add_argument(
        "--panel",
        choices=["failure", "control", "full-validation"],
        default="failure",
    )
    parser.add_argument(
        "--recoverability-csv-path",
        type=Path,
        default=DEFAULT_RECOVERABILITY_CSV_PATH,
    )
    parser.add_argument(
        "--component-matrix-csv-path",
        type=Path,
        default=DEFAULT_COMPONENT_MATRIX_CSV_PATH,
    )
    parser.add_argument(
        "--combined-validation-jsonl-path",
        type=Path,
        default=DEFAULT_COMBINED_VALIDATION_JSONL_PATH,
    )
    parser.add_argument("--control-limit", type=int, default=31)
    parser.add_argument("--verifier-input-jsonl-path", type=Path, action="append")
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--test-input-path", type=Path, default=DEFAULT_TEST_INPUT_PATH)
    parser.add_argument("--test-json-path", type=Path, default=DEFAULT_TEST_JSON_PATH)
    parser.add_argument("--test-report-path", type=Path, default=DEFAULT_TEST_REPORT_PATH)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--verifier-max-tokens", type=int, default=500)
    parser.add_argument("--progress-every", type=int, default=5)
    args = parser.parse_args(argv)

    if args.mode == "test-aggregate":
        metadata = run_targeted_switch_test_aggregate_audit(
            load_jsonl_rows(args.test_input_path),
            model=args.model,
            direct_max_tokens=args.max_tokens,
            verifier_max_tokens=args.verifier_max_tokens,
            progress_every=args.progress_every,
        )
        write_summary_json(metadata, args.test_json_path)
        write_targeted_test_report(
            metadata,
            args.test_report_path,
            json_path=args.test_json_path,
        )
        print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
        print(metadata["decision"])
        return

    if args.mode == "verify":
        if not args.verifier_input_jsonl_path:
            raise SystemExit("--mode verify requires --verifier-input-jsonl-path")
        panel_rows = build_verifier_panel_rows(args.verifier_input_jsonl_path)
        rows, metadata = run_verifier_panel(
            panel_rows,
            model=args.model,
            max_tokens=args.max_tokens,
            progress_every=args.progress_every,
        )
        write_jsonl_rows(rows, args.jsonl_path)
        write_summary_json(metadata, args.json_path)
        write_verifier_report(
            rows,
            metadata,
            args.report_path,
            jsonl_path=args.jsonl_path,
            json_path=args.json_path,
        )
        print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
        print(metadata["decision"])
        return

    if args.panel == "full-validation":
        slice_rows = build_full_validation_slice(
            load_jsonl_rows(args.combined_validation_jsonl_path)
        )
    elif args.panel == "control":
        slice_rows = build_control_slice(
            load_csv(args.component_matrix_csv_path),
            limit=args.control_limit,
        )
    else:
        slice_rows = build_failure_slice(load_recoverability_csv(args.recoverability_csv_path))
    if args.mode == "analyze":
        rows = reparse_saved_rows(slice_rows, load_jsonl_rows(args.jsonl_path))
        metadata = summarize_rows(rows, None, model=args.model)
    else:
        rows, metadata = run_live_slice(
            slice_rows,
            model=args.model,
            max_tokens=args.max_tokens,
            progress_every=args.progress_every,
        )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps(metadata["metrics"], indent=2, sort_keys=True))
    print(metadata["decision"])


if __name__ == "__main__":
    main()
