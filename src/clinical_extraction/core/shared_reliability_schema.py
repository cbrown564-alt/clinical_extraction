"""Shared reliability scorecard schema, record construction, and gap policy."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

CRITERIA = (
    {
        "id": "clinical_correctness_generalization",
        "name": "Clinical correctness and generalization",
        "question": (
            "Does the final system recover the intended clinical result, and what "
            "changes outside development?"
        ),
    },
    {
        "id": "clinical_selection_unsupported_inference",
        "name": "Clinical selection and unsupported inference",
        "question": (
            "Does the system select a warranted current fact rather than an "
            "unsupported, historical, planned, or ambiguous one?"
        ),
    },
    {
        "id": "evidence_support_faithfulness",
        "name": "Evidence support and faithfulness",
        "question": (
            "Is cited text present, and does it semantically support the selected conclusion?"
        ),
    },
    {
        "id": "uncertainty_selective_action",
        "name": "Uncertainty and selective action",
        "question": (
            "Do uncertainty signals identify failures, and can they support abstention "
            "or review at acceptable burden?"
        ),
    },
    {
        "id": "robustness_stability",
        "name": "Robustness and stability",
        "question": (
            "Does the decision persist across relevant data, sampling, wording, prompt, "
            "parser, or runtime changes?"
        ),
    },
    {
        "id": "component_attribution_correction_safety",
        "name": "Component attribution and correction safety",
        "question": (
            "Which component changes the answer, and does deterministic correction help "
            "without damaging correct model output?"
        ),
    },
    {
        "id": "coverage_clinical_slice_behavior",
        "name": "Coverage and clinical-slice behavior",
        "question": (
            "Which clinical families and hard cases are covered, missing, or materially weaker?"
        ),
    },
    {
        "id": "operational_reliability",
        "name": "Operational reliability",
        "question": (
            "Does the named runtime complete predictably, with failures, repairs, "
            "retries, latency, and usage reported at their measured scope?"
        ),
    },
)
REQUIRED_MEASUREMENT_FIELDS = {
    "task",
    "criterion_id",
    "measurement_id",
    "result_state",
    "model_scope",
    "dataset",
    "split",
    "split_manifest",
    "row_scope",
    "denominator",
    "denominator_status",
    "unit",
    "score_stage",
    "scorer",
    "repair_policy",
    "value",
    "evidence_state",
    "comparability",
    "source_artifacts",
    "source_hashes",
    "claim_boundary",
    "not_measured_reason",
    "route_runtime",
    "temperature",
    "token_limit",
    "cache_replay_mode",
    "prompt_program",
    "row_inspection_rule",
    "locked_row_controls",
    "independent_clinical_review",
    "reproducibility_command",
    "pooling_unit",
    "unique_rows",
    "model_row_count",
}
TASK_META = {
    "gan2026": {
        "dataset": "Gan 2026 synthetic clinical letters for seizure frequency",
        "split_manifest": "data/Gan (2026)/splits/gan2026_split_v1.json",
    },
    "exectv2": {
        "dataset": "ExECTv2 2025 broad epilepsy phenotyping corpus",
        "split_manifest": "data/ExECTv2 (2025)/splits/exectv2_split_v1.json",
    },
}
SIX_MODELS = [
    "openai/gpt-4.1-mini",
    "openai/gpt-5.6-luna",
    "openai/gpt-5.6-sol",
    "deepseek/deepseek-v4-flash",
    "ollama_chat/qwen3.6:35b",
    "ollama_chat/gemma4:26b",
]


def source_hashes(
    artifact_index: Mapping[str, Mapping[str, Any]], paths: Sequence[str]
) -> dict[str, str]:
    missing = [path for path in paths if path not in artifact_index]
    if missing:
        raise ValueError(f"unretained scorecard sources: {missing}")
    return {path: str(artifact_index[path]["sha256"]) for path in paths}


def make_record(
    *,
    artifact_index: Mapping[str, Mapping[str, Any]],
    task: str,
    criterion_id: str,
    measurement_id: str,
    model_scope: Sequence[str],
    split: str,
    row_scope: str,
    denominator: Any,
    denominator_status: str,
    unit: str,
    score_stage: str,
    scorer: str,
    repair_policy: str,
    value: Any,
    evidence_state: str,
    comparability: str,
    source_artifacts: Sequence[str],
    claim_boundary: str,
    route_runtime: Any,
    temperature: Any,
    token_limit: Any,
    cache_replay_mode: str,
    prompt_program: str,
    row_inspection_rule: str,
    locked_row_controls: str,
    independent_clinical_review: str,
    reproducibility_command: str,
    pooling_unit: str,
    unique_rows: int | None,
    model_row_count: int | None,
    result_state: str = "measured",
    not_measured_reason: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    paths = list(source_artifacts)
    record = {
        "task": task,
        "criterion_id": criterion_id,
        "measurement_id": measurement_id,
        "result_state": result_state,
        "model_scope": list(model_scope),
        "dataset": TASK_META[task]["dataset"],
        "split": split,
        "split_manifest": TASK_META[task]["split_manifest"],
        "row_scope": row_scope,
        "denominator": denominator,
        "denominator_status": denominator_status,
        "unit": unit,
        "score_stage": score_stage,
        "scorer": scorer,
        "repair_policy": repair_policy,
        "value": value,
        "evidence_state": evidence_state,
        "comparability": comparability,
        "source_artifacts": paths,
        "source_hashes": source_hashes(artifact_index, paths),
        "claim_boundary": claim_boundary,
        "not_measured_reason": not_measured_reason,
        "route_runtime": route_runtime,
        "temperature": temperature,
        "token_limit": token_limit,
        "cache_replay_mode": cache_replay_mode,
        "prompt_program": prompt_program,
        "row_inspection_rule": row_inspection_rule,
        "locked_row_controls": locked_row_controls,
        "independent_clinical_review": independent_clinical_review,
        "reproducibility_command": reproducibility_command,
        "pooling_unit": pooling_unit,
        "unique_rows": unique_rows,
        "model_row_count": model_row_count,
    }
    record.update(extra)
    return record


def task_cells_for_measurements(measurements: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    definitions: dict[tuple[str, str], dict[str, Any]] = {
        ("gan2026", "clinical_correctness_generalization"): {
            "result_state": "measured",
            "completion_status": "complete_for_recorded_scope",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Six-model test450 Purist and Pragmatic accuracy plus the retained "
                "subject validation/test comparison."
            ),
            "gap_ids": [],
        },
        ("exectv2", "clinical_correctness_generalization"): {
            "result_state": "measured",
            "completion_status": "complete_for_recorded_scope",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": "Six-model dev140 and aggregate-only test60 clinical-headline F1.",
            "gap_ids": [],
        },
        ("gan2026", "clinical_selection_unsupported_inference"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Unknown-gold active-rate over-read is retained; selected denominator "
                "counts are absent from the compact source."
            ),
            "gap_ids": ["gan_selection_denominator_metadata"],
        },
        ("exectv2", "clinical_selection_unsupported_inference"): {
            "result_state": "not_measurable_current_data",
            "completion_status": "blocked_by_data",
            "strongest_evidence_state": "diagnostic",
            "summary": (
                "The predeclared unknown-only denominator is zero; empty-gold letters "
                "are not substitutes."
            ),
            "gap_ids": ["exect_unsupported_selection_denominator"],
        },
        ("gan2026", "evidence_support_faithfulness"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Textual grounding is measured; independent semantic-support review is "
                "not selected."
            ),
            "gap_ids": ["gan_semantic_support_review"],
        },
        ("exectv2", "evidence_support_faithfulness"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Final exact evidence is measured; a stratified semantic-support sample "
                "awaits independent review."
            ),
            "gap_ids": ["exect_semantic_support_review"],
        },
        ("gan2026", "uncertainty_selective_action"): {
            "result_state": "measured",
            "completion_status": "complete_for_recorded_scope",
            "strongest_evidence_state": "development_answer",
            "summary": (
                "External-signal calibration and full risk-coverage results are retained "
                "for the named subject."
            ),
            "gap_ids": [],
        },
        ("exectv2", "uncertainty_selective_action"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Internal scoring-rule calibration and a historical three-model negative "
                "routing result are retained."
            ),
            "gap_ids": ["exect_six_model_uncertainty"],
        },
        ("gan2026", "robustness_stability"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "development_answer",
            "summary": (
                "Prompt-version and one-model repeated-temperature results cover named "
                "subdimensions only."
            ),
            "gap_ids": ["gan_broad_robustness"],
        },
        ("exectv2", "robustness_stability"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Six-model development-to-holdout changes are measured; perturbation "
                "robustness is not."
            ),
            "gap_ids": ["exect_broad_robustness"],
        },
        ("gan2026", "component_attribution_correction_safety"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "development_answer",
            "summary": (
                "The shared normalization ablation is measured; the retained compact "
                "package does not reproduce every stage transition count."
            ),
            "gap_ids": ["gan_full_stage_transition_inventory"],
        },
        ("exectv2", "component_attribution_correction_safety"): {
            "result_state": "measured",
            "completion_status": "complete_for_recorded_scope",
            "strongest_evidence_state": "development_answer",
            "summary": (
                "Six-model score stages, historical family regressions, and SF correction "
                "transitions remain separate."
            ),
            "gap_ids": [],
        },
        ("gan2026", "coverage_clinical_slice_behavior"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "development_answer",
            "summary": "Seizure-band variation is measured; demographic fairness is not measured.",
            "gap_ids": ["gan_demographic_fairness"],
        },
        ("exectv2", "coverage_clinical_slice_behavior"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "development_answer",
            "summary": (
                "All four fixed families are reported for six models; demographic "
                "fairness is not measured."
            ),
            "gap_ids": ["exect_demographic_fairness"],
        },
        ("gan2026", "operational_reliability"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Six-model failures and repairs plus a bounded historical cost estimate "
                "are measured; efficiency telemetry is unmatched."
            ),
            "gap_ids": ["gan_matched_efficiency_telemetry"],
        },
        ("exectv2", "operational_reliability"): {
            "result_state": "measured",
            "completion_status": "partial",
            "strongest_evidence_state": "aggregate_holdout_evidence",
            "summary": (
                "Six-model test60 completion and parse/schema behavior are retained with "
                "hosted/local routes separate."
            ),
            "gap_ids": ["exect_matched_efficiency_telemetry"],
        },
    }

    cells: list[dict[str, Any]] = []
    for task in ("gan2026", "exectv2"):
        for criterion in CRITERIA:
            key = (task, criterion["id"])
            cell = {"task": task, "criterion_id": criterion["id"], **definitions[key]}
            cell["measurement_ids"] = [
                item["measurement_id"]
                for item in measurements
                if item["task"] == task and item["criterion_id"] == criterion["id"]
            ]
            cells.append(cell)
    return cells


def reliability_gaps() -> list[dict[str, str]]:
    return [
        {
            "id": "gan_selection_denominator_metadata",
            "class": "documentation_instrumentation_gap",
            "owner": "Gan reliability evidence package",
            "decision": (
                "Keep the retained rates and mark their selected denominator counts unavailable."
            ),
            "unblock_condition": (
                "Select a hash-verified machine artifact containing the original "
                "unknown-gold counts."
            ),
            "claim_effect": (
                "The rate is reportable at its retained scope but the criterion remains incomplete."
            ),
        },
        {
            "id": "exect_unsupported_selection_denominator",
            "class": "independent_clinical_review_dependency",
            "owner": "Future independently governed ExECT annotation review",
            "decision": "Keep the zero-denominator study as a closed diagnostic result.",
            "unblock_condition": (
                "Exhaustive independent review distinguishes unsupported predictions "
                "from omission, multiplicity, and accepted representation differences."
            ),
            "claim_effect": (
                "No ExECT unsupported-selection rate or Gan-to-ExECT over-reading "
                "transfer claim is permitted."
            ),
        },
        {
            "id": "gan_semantic_support_review",
            "class": "independent_clinical_review_dependency",
            "owner": "Independent clinical reviewers",
            "decision": "Do not equate exact source presence with semantic support.",
            "unblock_condition": (
                "A governed representative sample is independently reviewed at the "
                "reported decision stage."
            ),
            "claim_effect": (
                "Gan evidence is described as textual grounding, not externally "
                "validated faithfulness."
            ),
        },
        {
            "id": "exect_semantic_support_review",
            "class": "independent_clinical_review_dependency",
            "owner": "Independent clinical reviewers",
            "decision": "Retain the stratified sample as an unreviewed substrate only.",
            "unblock_condition": (
                "Independent reviewers complete the frozen fields with provenance and adjudication."
            ),
            "claim_effect": (
                "Exact evidence remains separate from semantic support and clinical validation."
            ),
        },
        {
            "id": "exect_six_model_uncertainty",
            "class": "optional_new_experiment",
            "owner": "Future dated clinical research protocol",
            "decision": "Keep the historical three-model negative result bounded.",
            "unblock_condition": (
                "Adopt a named six-model routing claim before writing and running a "
                "separate protocol."
            ),
            "claim_effect": "No six-model or deployment-calibration conclusion is permitted.",
        },
        {
            "id": "gan_broad_robustness",
            "class": "optional_new_experiment",
            "owner": "Future dated clinical research protocol",
            "decision": "Do not commission perturbation calls merely to fill the framework.",
            "unblock_condition": "A named paper claim requires a predeclared perturbation result.",
            "claim_effect": (
                "Robustness wording remains limited to the recorded prompt and sampling "
                "subdimensions."
            ),
        },
        {
            "id": "exect_broad_robustness",
            "class": "optional_new_experiment",
            "owner": "Future dated clinical research protocol",
            "decision": "Treat dev-to-test and parser/runtime behavior as separate subdimensions.",
            "unblock_condition": (
                "A claim-changing protocol predeclares clinically equivalent wording or "
                "prompt perturbations."
            ),
            "claim_effect": (
                "The six-model split change is not called perturbation robustness or "
                "self-consistency."
            ),
        },
        {
            "id": "gan_full_stage_transition_inventory",
            "class": "documentation_instrumentation_gap",
            "owner": "Gan component evidence package",
            "decision": (
                "Report the selected normalization ablation and preserve the stage "
                "boundary without reconstructing missing row transitions."
            ),
            "unblock_condition": (
                "A no-call retained artifact exposes all stage transitions under the "
                "locked-row policy."
            ),
            "claim_effect": "No new stage-specific correction-safety count is claimed.",
        },
        {
            "id": "gan_demographic_fairness",
            "class": "outside_project_boundary",
            "owner": "Future dataset and fairness protocol",
            "decision": "Do not relabel seizure-band variation as demographic fairness.",
            "unblock_condition": (
                "Suitable attributes, sample sizes, and a clinically meaningful fairness "
                "question exist."
            ),
            "claim_effect": "Demographic fairness is not measured.",
        },
        {
            "id": "exect_demographic_fairness",
            "class": "outside_project_boundary",
            "owner": "Future dataset and fairness protocol",
            "decision": "Do not relabel entity-family variation as demographic fairness.",
            "unblock_condition": (
                "Suitable attributes, sample sizes, and a clinically meaningful fairness "
                "question exist."
            ),
            "claim_effect": "Demographic fairness is not measured.",
        },
        {
            "id": "gan_matched_efficiency_telemetry",
            "class": "outside_project_boundary",
            "owner": "Future matched runtime protocol",
            "decision": (
                "Do not reconstruct unmatched token, cost, latency, hardware, or retry values."
            ),
            "unblock_condition": (
                "A matched protocol measures the selected conditions prospectively."
            ),
            "claim_effect": (
                "Only observed failures, repairs, pass counts, and the bounded offline "
                "estimate are reportable."
            ),
        },
        {
            "id": "exect_matched_efficiency_telemetry",
            "class": "outside_project_boundary",
            "owner": "Future matched runtime protocol",
            "decision": (
                "Keep hosted and local runtime conditions separate and do not rank efficiency."
            ),
            "unblock_condition": (
                "A matched protocol records latency, usage, hardware, retries, and cache state."
            ),
            "claim_effect": "No cross-route efficiency ranking is permitted.",
        },
    ]
