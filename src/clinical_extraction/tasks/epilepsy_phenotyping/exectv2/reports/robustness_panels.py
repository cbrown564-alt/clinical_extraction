"""Deterministic ExECTv2 robustness panels for reliability-scorecard upgrades.

The panel is a preflight fixture bank and scoring harness. It makes no model
calls and uses synthetic/dev-style minimal pairs only; it does not load full-200
or holdout rows. Future frozen candidate runs can replace the prediction arms
with saved model predictions while keeping the same aggregate reporting shape.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.validate import (
    validate_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.final_consolidation import (
    REPO_ROOT,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
)

DEFAULT_GENERATED_ON = "2026-06-25"
DEFAULT_JSON = Path("experiments/exectv2_robustness_panels_preflight_20260625.json")
DEFAULT_MARKDOWN = Path(
    "docs/experiments/exectv2/reliability/exectv2_robustness_panels_preflight_2026-06-25.md"
)
FAMILIES: tuple[str, ...] = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)
MINIMUM_PERTURBATION_FAMILIES: tuple[str, ...] = (
    "sf_current_vs_historical",
    "sf_current_vs_future",
    "prescription_current_vs_plan",
    "investigations_result_state",
    "diagnosis_assertion_hierarchy",
    "evidence_paraphrase",
    "evidence_deletion",
)
EVIDENCE_ISSUE_CODES: frozenset[str] = frozenset({"missing_evidence", "evidence_not_substring"})


@dataclass(frozen=True)
class RobustnessCase:
    case_id: str
    family: str
    perturbation_family: str
    baseline_note: str
    perturbed_note: str
    expected_mentions: tuple[dict[str, Any], ...]
    failure_mode: str
    failure_mentions: tuple[dict[str, Any], ...]
    rationale: str


def build_robustness_panel_payload(
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    cases: Sequence[RobustnessCase] | None = None,
    include_case_text: bool = True,
) -> dict[str, Any]:
    """Build the deterministic robustness preflight payload."""

    panel_cases = tuple(cases or default_robustness_cases())
    arms = [
        _score_prediction_arm(
            "reference_oracle",
            "Reference oracle",
            panel_cases,
            {case.case_id: case.expected_mentions for case in panel_cases},
        ),
        _score_prediction_arm(
            "targeted_failure_control",
            "Targeted failure control",
            panel_cases,
            {case.case_id: case.failure_mentions for case in panel_cases},
        ),
    ]
    oracle = arms[0]
    for arm in arms[1:]:
        arm["delta_vs_reference_oracle"] = {
            "overall_f1": round(
                float(arm["overall"]["f1"]) - float(oracle["overall"]["f1"]),
                4,
            ),
            "schema_validity_rate": round(
                float(arm["schema_validity_rate"]) - float(oracle["schema_validity_rate"]),
                4,
            ),
            "evidence_validity_rate": round(
                float(arm["evidence_validity_rate"]) - float(oracle["evidence_validity_rate"]),
                4,
            ),
        }

    coverage_counts = Counter(case.perturbation_family for case in panel_cases)
    missing = [
        family for family in MINIMUM_PERTURBATION_FAMILIES if coverage_counts.get(family, 0) == 0
    ]
    return {
        "artifact_kind": "exectv2_robustness_panel_preflight",
        "generated_on": generated_on,
        "surface": "rich-schema holistic assembly reliability scorecard",
        "scorer": "headline_target clinical-recovery family cells",
        "split": "deterministic_dev_fixture_panel",
        "result_type": "dev_fixture_preflight_not_validation",
        "allow_model_calls": False,
        "row_inspection_policy": (
            "Synthetic/dev-fixture panel only. No full-200 or holdout row-level "
            "inspection, examples, residual ledgers, or note text are loaded."
        ),
        "claim_boundary": (
            "This artifact freezes the robustness panel schema and proves the "
            "scorer is sensitive to targeted perturbation failures. It is not a "
            "validation result until a frozen candidate is run once under the "
            "2026-06-24 reliability-audit protocol."
        ),
        "panel_coverage": {
            "case_count": len(panel_cases),
            "by_family": dict(sorted(Counter(case.family for case in panel_cases).items())),
            "by_perturbation_family": dict(sorted(coverage_counts.items())),
            "minimum_coverage_met": not missing,
            "missing_minimum_families": missing,
        },
        "promotion_gate": {
            "scorecard_ready_for_frozen_candidate_run": not missing
            and oracle["overall"]["f1"] == 1.0
            and oracle["schema_validity_rate"] == 1.0
            and oracle["evidence_validity_rate"] == 1.0,
            "scorecard_coverage_can_increase": False,
            "reason": (
                "Panel preflight is ready, but scorecard robustness coverage can "
                "increase only after an aggregate-only frozen candidate run passes "
                "the predeclared robustness gate."
            ),
        },
        "prediction_arms": arms,
        "cases": [_case_payload(case, include_case_text=include_case_text) for case in panel_cases],
        "holdout_guardrail": {
            "full_200_or_holdout_rows_loaded": False,
            "blocked_surfaces": ["full-200", "holdout", "test"],
            "policy": (
                "This module constructs synthetic fixture letters only. Full-200 "
                "or holdout use must remain aggregate-only and separately frozen."
            ),
        },
    }


def write_robustness_panel_artifacts(
    *,
    json_path: Path = DEFAULT_JSON,
    markdown_path: Path = DEFAULT_MARKDOWN,
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Path]:
    """Write the robustness preflight JSON and Markdown artifacts."""

    json_path = json_path if json_path.is_absolute() else REPO_ROOT / json_path
    markdown_path = markdown_path if markdown_path.is_absolute() else REPO_ROOT / markdown_path
    payload = build_robustness_panel_payload(generated_on=generated_on)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(
        render_robustness_panel_markdown(payload, json_path=json_path),
        encoding="utf-8",
    )
    return {"json": json_path, "markdown": markdown_path}


def render_robustness_panel_markdown(
    payload: Mapping[str, Any],
    *,
    json_path: Path,
) -> str:
    coverage = payload["panel_coverage"]
    gate = payload["promotion_gate"]
    lines = [
        "# ExECTv2 Robustness Panels Preflight",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `{_relative(json_path)}`",
        f"- Surface: {payload['surface']}",
        f"- Scorer: `{payload['scorer']}`",
        f"- Split: `{payload['split']}`",
        f"- Result type: `{payload['result_type']}`",
        f"- Model calls during build: `{payload['allow_model_calls']}`",
        f"- Row inspection policy: {payload['row_inspection_policy']}",
        "",
        "This is an aggregate-only validation-ready panel preflight. It freezes "
        "the case taxonomy and proves the scorer reacts to targeted failures; it "
        "does not inspect full-200 or holdout row-level inspection surfaces.",
        "",
        "## Coverage",
        "",
        "| Requirement | Count |",
        "| --- | ---: |",
    ]
    for family in MINIMUM_PERTURBATION_FAMILIES:
        lines.append(f"| `{family}` | {coverage['by_perturbation_family'].get(family, 0)} |")
    lines.extend(
        [
            "",
            f"- Minimum coverage met: `{coverage['minimum_coverage_met']}`",
            (
                "- Ready for frozen candidate run: "
                f"`{gate['scorecard_ready_for_frozen_candidate_run']}`"
            ),
            f"- Scorecard coverage can increase now: `{gate['scorecard_coverage_can_increase']}`",
            f"- Gate rationale: {gate['reason']}",
            "",
            "## Aggregate Arms",
            "",
            (
                "| Arm | Overall F1 | Schema validity | Evidence validity | "
                "Call failures | Parse failures |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for arm in payload["prediction_arms"]:
        lines.append(
            f"| {arm['label']} | {arm['overall']['f1']:.4f} | "
            f"{arm['schema_validity_rate']:.4f} | "
            f"{arm['evidence_validity_rate']:.4f} | "
            f"{arm['call_failures']} | {arm['parse_schema_failures']} |"
        )
    lines.extend(
        [
            "",
            "## Family Deltas",
            "",
            "| Arm | Family | F1 | P | R | TP | FP | FN | Companion metrics |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for arm in payload["prediction_arms"]:
        for row in arm["by_family"]:
            companion = ", ".join(
                f"{key}={value:.4f}" for key, value in row["companion_metrics"].items()
            )
            lines.append(
                f"| {arm['label']} | {row['family']} | {row['f1']:.4f} | "
                f"{row['precision']:.4f} | {row['recall']:.4f} | "
                f"{row['tp']} | {row['fp']} | {row['fn']} | {companion} |"
            )
    lines.extend(
        [
            "",
            "## Case Catalog",
            "",
            "| Case | Family | Perturbation | Failure mode |",
            "| --- | --- | --- | --- |",
        ]
    )
    for case in payload["cases"]:
        lines.append(
            f"| `{case['case_id']}` | {case['family']} | "
            f"`{case['perturbation_family']}` | {case['failure_mode']} |"
        )
    lines.append("")
    return "\n".join(lines)


def default_robustness_cases() -> tuple[RobustnessCase, ...]:
    """Return the predeclared deterministic panel cases."""

    return (
        RobustnessCase(
            case_id="sf_current_over_historical",
            family="SeizureFrequency",
            perturbation_family="sf_current_vs_historical",
            baseline_note=(
                "Previously he had focal seizures every week. He is currently seizure free."
            ),
            perturbed_note=(
                "Previously he had focal seizures every week. He is currently seizure free."
            ),
            expected_mentions=(
                _mention(
                    "SeizureFrequency",
                    "focal seizures",
                    "He is currently seizure free",
                    {"NumberOfSeizures": "0"},
                ),
            ),
            failure_mode="selects historical active rate instead of current state",
            failure_mentions=(
                _mention(
                    "SeizureFrequency",
                    "focal seizures",
                    "Previously he had focal seizures every week",
                    {
                        "NumberOfSeizures": "1",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Week",
                    },
                ),
            ),
            rationale="Current state must override older seizure-burden history.",
        ),
        RobustnessCase(
            case_id="sf_current_over_future_plan",
            family="SeizureFrequency",
            perturbation_family="sf_current_vs_future",
            baseline_note=(
                "She currently has focal seizures twice a month. If they worsen, "
                "we will review frequency next year."
            ),
            perturbed_note=(
                "She currently has focal seizures twice a month. If they worsen, "
                "we will review frequency next year."
            ),
            expected_mentions=(
                _mention(
                    "SeizureFrequency",
                    "focal seizures",
                    "currently has focal seizures twice a month",
                    {
                        "NumberOfSeizures": "2",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Month",
                    },
                ),
            ),
            failure_mode="drops the current active-rate state because future review is mentioned",
            failure_mentions=(
                _mention(
                    "SeizureFrequency",
                    "focal seizures",
                    "we will review frequency next year",
                    {},
                ),
            ),
            rationale="Future review language is not the current seizure state.",
        ),
        RobustnessCase(
            case_id="rx_current_over_plan",
            family="Prescription",
            perturbation_family="prescription_current_vs_plan",
            baseline_note=(
                "He takes lamotrigine 100 mg twice daily. The plan is to start "
                "clobazam 5 mg twice daily next month."
            ),
            perturbed_note=(
                "He takes lamotrigine 100 mg twice daily. The plan is to start "
                "clobazam 5 mg twice daily next month."
            ),
            expected_mentions=(
                _mention(
                    "Prescription",
                    "lamotrigine",
                    "lamotrigine 100 mg twice daily",
                    {
                        "DrugName": "lamotrigine",
                        "DrugDose": "100",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                ),
            ),
            failure_mode="extracts planned clobazam as a current regimen",
            failure_mentions=(
                _mention(
                    "Prescription",
                    "clobazam",
                    "clobazam 5 mg twice daily next month",
                    {
                        "DrugName": "clobazam",
                        "DrugDose": "5",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                ),
            ),
            rationale="Medication plans must stay separate from active regimens.",
        ),
        RobustnessCase(
            case_id="inv_pending_vs_result",
            family="Investigations",
            perturbation_family="investigations_result_state",
            baseline_note=("An MRI has been requested and is pending. The EEG was abnormal."),
            perturbed_note=("An MRI has been requested and is pending. The EEG was abnormal."),
            expected_mentions=(
                _mention(
                    "Investigations",
                    "MRI",
                    "MRI has been requested and is pending",
                    {"MRI_Performed": "No"},
                ),
                _mention(
                    "Investigations",
                    "EEG",
                    "EEG was abnormal",
                    {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                ),
            ),
            failure_mode="treats pending MRI as performed with an unknown result",
            failure_mentions=(
                _mention(
                    "Investigations",
                    "MRI",
                    "MRI has been requested and is pending",
                    {"MRI_Performed": "Yes", "MRI_Results": "Unknown"},
                ),
                _mention(
                    "Investigations",
                    "EEG",
                    "EEG was abnormal",
                    {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                ),
            ),
            rationale="Pending tests are not completed investigations with results.",
        ),
        RobustnessCase(
            case_id="dx_specific_over_generic",
            family="Diagnosis",
            perturbation_family="diagnosis_assertion_hierarchy",
            baseline_note=(
                "She has focal epilepsy. Generalised epilepsy was considered but is not supported."
            ),
            perturbed_note=(
                "She has focal epilepsy. Generalised epilepsy was considered but is not supported."
            ),
            expected_mentions=(
                _mention(
                    "Diagnosis",
                    "focal epilepsy",
                    "She has focal epilepsy",
                    {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                ),
            ),
            failure_mode="emits a generic or unsupported hierarchy diagnosis",
            failure_mentions=(
                _mention(
                    "Diagnosis",
                    "epilepsy",
                    "Generalised epilepsy was considered but is not supported",
                    {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                ),
            ),
            rationale="Hierarchy pressure cases must preserve the most specific assertion.",
        ),
        RobustnessCase(
            case_id="dx_negation_assertion",
            family="Diagnosis",
            perturbation_family="diagnosis_assertion_hierarchy",
            baseline_note="There is no evidence of epilepsy.",
            perturbed_note="There is no evidence of epilepsy.",
            expected_mentions=(
                _mention(
                    "Diagnosis",
                    "epilepsy",
                    "no evidence of epilepsy",
                    {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Negated",
                    },
                ),
            ),
            failure_mode="preserves concept identity but flips negation to affirmed",
            failure_mentions=(
                _mention(
                    "Diagnosis",
                    "epilepsy",
                    "no evidence of epilepsy",
                    {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                ),
            ),
            rationale=(
                "Concept-only recovery can hide assertion errors; companion scoring exposes them."
            ),
        ),
        RobustnessCase(
            case_id="evidence_paraphrase_sf",
            family="SeizureFrequency",
            perturbation_family="evidence_paraphrase",
            baseline_note="He has had no attacks since February.",
            perturbed_note="He has had no attacks since February.",
            expected_mentions=(
                _mention(
                    "SeizureFrequency",
                    "attacks",
                    "no attacks since February",
                    {"NumberOfSeizures": "0"},
                ),
            ),
            failure_mode="uses paraphrased non-verbatim evidence for a correct fact",
            failure_mentions=(
                _mention(
                    "SeizureFrequency",
                    "attacks",
                    "seizure free since February",
                    {"NumberOfSeizures": "0"},
                ),
            ),
            rationale="Evidence paraphrase preserves the fact but fails exact-evidence validity.",
        ),
        RobustnessCase(
            case_id="evidence_deletion_rx",
            family="Prescription",
            perturbation_family="evidence_deletion",
            baseline_note="Current medication remains levetiracetam 500 mg twice daily.",
            perturbed_note="Current medication remains levetiracetam 500 mg twice daily.",
            expected_mentions=(
                _mention(
                    "Prescription",
                    "levetiracetam",
                    "levetiracetam 500 mg twice daily",
                    {
                        "DrugName": "levetiracetam",
                        "DrugDose": "500",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                ),
            ),
            failure_mode="deletes evidence while keeping the clinical fact",
            failure_mentions=(
                _mention(
                    "Prescription",
                    "levetiracetam",
                    "",
                    {
                        "DrugName": "levetiracetam",
                        "DrugDose": "500",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                ),
            ),
            rationale=(
                "Evidence deletion should reduce evidence validity even when scoring stays correct."
            ),
        ),
    )


def _score_prediction_arm(
    arm_id: str,
    label: str,
    cases: Sequence[RobustnessCase],
    predictions_by_case: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    gold_letters = [
        _letter_from_mentions(
            case.case_id,
            case.perturbed_note,
            case.expected_mentions,
        )
        for case in cases
    ]
    pred_letters = [
        _letter_from_mentions(
            case.case_id,
            case.perturbed_note,
            predictions_by_case.get(case.case_id, ()),
        )
        for case in cases
    ]
    family_rows = [_family_row(family, gold_letters, pred_letters) for family in FAMILIES]
    validity = _validity_summary(cases, predictions_by_case)
    return {
        "arm_id": arm_id,
        "label": label,
        "overall": _aggregate_family_rows(family_rows),
        "by_family": family_rows,
        **validity,
        "call_failures": 0,
        "parse_schema_failures": 0,
    }


def _family_row(
    family: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    if family == "Diagnosis":
        score = score_concept_identity(gold_letters, pred_letters, "Diagnosis")
        primary = score.concept_only
        companion = {
            "assertion_f1": round(float(score.concept_assertion.f1), 4),
            "negation_f1": round(float(score.concept_negation.f1), 4),
        }
    elif family == "SeizureFrequency":
        score = score_frequency_state(gold_letters, pred_letters)
        primary = score.clinical_headline
        companion = {
            "active_rate_fidelity_f1": round(float(score.active_rate_fidelity.f1), 4),
            "benchmark_with_cui_f1": round(float(score.benchmark_with_cui.f1), 4),
        }
    elif family == "Prescription":
        score = score_prescription_components(gold_letters, pred_letters)
        primary = score.clinical_headline
        companion = {
            "ordinary_complete_f1": round(float(score.ordinary_complete.f1), 4),
            "future_medication_f1": round(float(score.future_medication.f1), 4),
        }
    elif family == "Investigations":
        score = score_investigations_components(gold_letters, pred_letters)
        primary = score.clinical_headline
        companion = {
            "performed_f1": round(float(score.performed.f1), 4),
            "result_f1": round(float(score.result.f1), 4),
        }
    else:
        raise ValueError(f"Unknown robustness family {family!r}")

    row = _score_dict(primary)
    row["family"] = family
    row["companion_metrics"] = companion
    return row


def _score_dict(score: Any) -> dict[str, Any]:
    tp = int(getattr(score, "tp", 0))
    fp = int(getattr(score, "fp", 0))
    fn = int(getattr(score, "fn", 0))
    pred_count = int(getattr(score, "pred_count", tp + fp))
    gold_count = int(getattr(score, "gold_count", tp + fn))
    return {
        "tp": tp,
        "precision_tp": int(getattr(score, "precision_tp", tp)),
        "recall_tp": int(getattr(score, "recall_tp", tp)),
        "fp": fp,
        "fn": fn,
        "pred_count": pred_count,
        "gold_count": gold_count,
        "precision": round(float(getattr(score, "precision", 0.0)), 4),
        "recall": round(float(getattr(score, "recall", 0.0)), 4),
        "f1": round(float(getattr(score, "f1", 0.0)), 4),
    }


def _aggregate_family_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    precision_tp = sum(int(row["precision_tp"]) for row in rows)
    recall_tp = sum(int(row["recall_tp"]) for row in rows)
    pred_count = sum(int(row["pred_count"]) for row in rows)
    gold_count = sum(int(row["gold_count"]) for row in rows)
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "precision_tp": precision_tp,
        "recall_tp": recall_tp,
        "pred_count": pred_count,
        "gold_count": gold_count,
        "fp": max(0, pred_count - precision_tp),
        "fn": max(0, gold_count - recall_tp),
    }


def _validity_summary(
    cases: Sequence[RobustnessCase],
    predictions_by_case: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    mention_count = schema_valid_mentions = evidence_valid_mentions = 0
    issue_counts: Counter[str] = Counter()
    for case in cases:
        mentions = tuple(
            _predicted_mention(mention) for mention in predictions_by_case.get(case.case_id, ())
        )
        predicted = PredictedLetter(letter_id=case.case_id, mentions=mentions)
        for mention in mentions:
            mention_count += 1
            spec = ENTITY_REGISTRY[mention.entity]
            issues = validate_letter(
                PredictedLetter(letter_id=case.case_id, mentions=(mention,)),
                case.perturbed_note,
            ).issues
            issue_counts.update(issue.code for issue in issues)
            if not any(issue.severity == "error" for issue in issues):
                schema_valid_mentions += 1
            if not any(issue.code in EVIDENCE_ISSUE_CODES for issue in issues):
                evidence_valid_mentions += 1
            if spec.name != mention.entity:
                issue_counts["entity_registry_mismatch"] += 1
        validate_letter(predicted, case.perturbed_note)
    return {
        "predicted_mentions": mention_count,
        "schema_valid_mentions": schema_valid_mentions,
        "evidence_valid_mentions": evidence_valid_mentions,
        "schema_validity_rate": _rate(schema_valid_mentions, mention_count),
        "evidence_validity_rate": _rate(evidence_valid_mentions, mention_count),
        "validation_issue_counts": dict(sorted(issue_counts.items())),
    }


def _letter_from_mentions(
    letter_id: str,
    note_text: str,
    mentions: Sequence[Mapping[str, Any]],
) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text=note_text,
        annotations=tuple(
            ExectAnnotation(
                entity=str(mention["entity"]),
                text=str(mention["text"]),
                attributes={
                    str(key): str(value)
                    for key, value in dict(mention.get("attributes") or {}).items()
                },
            )
            for mention in mentions
        ),
    )


def _predicted_mention(mention: Mapping[str, Any]) -> PredictedMention:
    return PredictedMention(
        entity=str(mention["entity"]),
        text=str(mention["text"]),
        attributes={
            str(key): str(value) for key, value in dict(mention.get("attributes") or {}).items()
        },
        evidence=str(mention.get("evidence", "")),
        rationale=str(mention.get("rationale", "")),
        confidence=mention.get("confidence") or "high",
        component_owner=str(mention.get("component_owner", "robustness_fixture")),
    )


def _case_payload(case: RobustnessCase, *, include_case_text: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "case_id": case.case_id,
        "family": case.family,
        "perturbation_family": case.perturbation_family,
        "failure_mode": case.failure_mode,
        "rationale": case.rationale,
    }
    if include_case_text:
        payload.update(
            {
                "baseline_note": case.baseline_note,
                "perturbed_note": case.perturbed_note,
                "expected_mentions": list(case.expected_mentions),
                "failure_mentions": list(case.failure_mentions),
            }
        )
    else:
        payload.update({"expected_mentions": [], "failure_mentions": []})
    return payload


def _mention(
    entity: str,
    text: str,
    evidence: str,
    attributes: Mapping[str, str],
) -> dict[str, Any]:
    return {
        "entity": entity,
        "text": text,
        "attributes": dict(attributes),
        "evidence": evidence,
        "confidence": "high",
        "rationale": "",
        "component_owner": "robustness_fixture",
    }


def _relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 1.0
