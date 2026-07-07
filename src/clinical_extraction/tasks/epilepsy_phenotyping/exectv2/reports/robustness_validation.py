"""Aggregate-only robustness validation audit for ExECTv2.

The frozen reliability protocol permits full-200 validation only as aggregate
outputs. This module applies the preflighted robustness taxonomy once to the
accepted current-code v08-shaped full-200 artifact, reports natural hard-slice
aggregate deltas, and keeps adversarial evidence perturbations scoped to the
frozen fixture preflight. It emits no row identifiers, examples, note text,
evidence spans, rationales, or residual ledgers from the full-200 surface.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from . import cross_model_reliability_analysis as reliability
from . import robustness_panels
from . import validation_audit_scaffold as scaffold

REPO_ROOT = scaffold.REPO_ROOT
REPORT_PATH = Path(
    "docs/experiments/exectv2/reliability/exectv2_robustness_validation_audit_2026-06-25.md"
)

_FULL200_ARTIFACT: dict[str, str] = {
    **scaffold.FULL200_ARTIFACT,
    "reason": (
        "Accepted for aggregate-only validation of the frozen robustness "
        "taxonomy on the current-code v08-shaped rich-schema holistic assembly "
        "surface."
    ),
}

_HISTORICAL_RE = re.compile(
    r"\b(previous|previously|prior|past|historical|used to|since|ago|last year|last month)\b",
    re.IGNORECASE,
)
_FUTURE_RE = re.compile(
    r"\b(if|plan|planned|future|review|next|will|worsen|increase|decrease)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_PLAN_RE = re.compile(
    r"\b(plan|planned|start|commence|increase|reduce|switch|titrate|target|next|future|consider|if)\b",
    re.IGNORECASE,
)
_INVESTIGATION_RESULT_RE = re.compile(
    r"\b(normal|abnormal|unknown|pending|requested|arrange|showed|reported|performed|results?)\b",
    re.IGNORECASE,
)
_DIAGNOSIS_ASSERTION_RE = re.compile(
    (
        r"\b(no evidence|not supported|possible|probable|likely|diagnosis|epilepsy|"
        r"seizure|syndrome|focal|generalised|generalized)\b"
    ),
    re.IGNORECASE,
)


def build_robustness_validation_audit(
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Return the aggregate-only robustness validation package."""

    preflight = robustness_panels.build_robustness_panel_payload(include_case_text=False)
    artifact = scaffold.artifact_inventory_single(repo_root, _FULL200_ARTIFACT)[0]
    validation = _validation_readout(repo_root, artifact) if artifact["eligible"] else None
    promotion_gates = _promotion_gates(preflight, validation)
    promotion_decision = scaffold.promotion_decision_from_gates(promotion_gates)
    return {
        **scaffold.audit_envelope(
            audit_kind="exectv2_robustness_aggregate_validation",
            repo_root=repo_root,
            scorer="headline_target clinical-recovery family cells",
            row_inspection_boundary=(
                "Aggregate hard-slice metrics and artifact inventory only; no row "
                "identifiers, note text, gold labels, predictions, evidence spans, "
                "rationales, or selected failure examples are emitted."
            ),
        ),
        "candidate_definition": {
            "candidate": "exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini",
            "taxonomy_source": (
                "docs/experiments/exectv2/reliability/"
                "exectv2_robustness_panels_preflight_2026-06-25.md"
            ),
            "preflight_split": preflight["split"],
            "preflight_minimum_coverage_met": preflight["panel_coverage"]["minimum_coverage_met"],
            "preflight_by_perturbation_family": preflight["panel_coverage"][
                "by_perturbation_family"
            ],
            "full200_tagging_policy": (
                "Frozen regex/provenance feature tags are computed internally "
                "from saved predicted/gold mention metadata and emitted only as "
                "aggregate counts."
            ),
        },
        "artifact_inventory": [artifact],
        "eligible_validation_artifacts": 1 if artifact["eligible"] else 0,
        "validation_readout": validation,
        "stop_rule_outcome": scaffold.stop_rule_outcome(
            validation=validation,
            promotion_decision=promotion_decision,
            promoted_reason=(
                "The frozen robustness taxonomy and accepted current-code "
                "full-200 artifact pass the aggregate reporting gates. Evidence "
                "paraphrase/deletion remain adversarial fixture stress evidence, "
                "not naturally observed full-200 hard-slice failures."
            ),
        ),
        "promotion_gates": promotion_gates,
        "next_action": (
            "Refresh the reliability scorecard to mark robustness as aggregate "
            "full-200 hard-slice validation evidence while keeping adversarial "
            "evidence-perturbation claims tied to the frozen preflight panel."
        )
        if promotion_decision == "promoted"
        else (
            "Keep robustness at preflight-only status and define a fresh dev-only "
            "candidate before any new validation attempt."
        ),
    }


def render_markdown(audit: Mapping[str, Any]) -> str:
    """Render a paper-facing Markdown audit without row-level details."""

    candidate = audit["candidate_definition"]
    lines = scaffold.render_preflight_section(
        audit,
        title="# ExECTv2 Robustness Validation Audit",
        status_line=("Status: aggregate-only robustness validation and stop-rule readout."),
    )
    lines.extend(
        [
            "",
            "## Frozen Robustness Candidate",
            "",
            f"- Candidate: `{candidate['candidate']}`",
            f"- Taxonomy source: `{candidate['taxonomy_source']}`",
            f"- Preflight split: `{candidate['preflight_split']}`",
            (f"- Preflight minimum coverage met: `{candidate['preflight_minimum_coverage_met']}`"),
            f"- Full-200 tagging policy: {candidate['full200_tagging_policy']}",
            "",
            "### Preflight Taxonomy Coverage",
            "",
            "| Perturbation family | Fixture count |",
            "| --- | ---: |",
        ]
    )
    for family in robustness_panels.MINIMUM_PERTURBATION_FAMILIES:
        lines.append(
            f"| `{family}` | {candidate['preflight_by_perturbation_family'].get(family, 0)} |"
        )

    lines.extend(scaffold.render_artifact_inventory_section(audit["artifact_inventory"]))

    validation = audit.get("validation_readout")
    if validation:
        overall = validation["overall"]
        stress = validation["hard_slice_overall"]
        complement = validation["non_hard_slice_overall"]
        lines.extend(
            [
                "",
                "## Aggregate Validation Readout",
                "",
                f"- Artifact: `{validation['artifact_path']}`",
                f"- Rows: {validation['rows']}",
                f"- Eligible family cells: {validation['eligible_cells']}",
                f"- Hard-slice family cells: {validation['hard_slice_cells']}",
                f"- Overall F1: {overall['f1']:.4f}",
                f"- Hard-slice F1: {stress['f1']:.4f}",
                f"- Non-hard-slice F1: {complement['f1']:.4f}",
                (
                    "- Hard-slice delta vs overall: "
                    f"{validation['hard_slice_delta_vs_overall']['f1']:.4f}"
                ),
                (f"- Schema validity: {validation['schema_validity_rate']:.4f}"),
                (f"- Evidence validity: {validation['evidence_validity_rate']:.4f}"),
                f"- Call failures: {validation['call_failures']}",
                f"- Parse/schema failures: {validation['parse_schema_failures']}",
                "",
                "### Perturbation Family Counts",
                "",
                (
                    "| Perturbation family | Full-200 cells | Primary family | F1 | "
                    "Delta vs overall | Schema validity | Evidence validity |"
                ),
                "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in validation["by_perturbation_family"]:
            f1 = scaffold.format_optional_float(row["score"]["f1"])
            delta = scaffold.format_optional_float(row["delta_vs_overall"]["f1"])
            schema = scaffold.format_optional_float(row["schema_validity_rate"])
            evidence = scaffold.format_optional_float(row["evidence_validity_rate"])
            lines.append(
                f"| `{row['perturbation_family']}` | {row['cells']} | "
                f"{row['primary_family']} | {f1} | {delta} | {schema} | {evidence} |"
            )
        lines.extend(
            [
                "",
                "### Per-Family Deltas",
                "",
                (
                    "| Family | All cells | Overall F1 | Hard-slice cells | "
                    "Hard-slice F1 | Delta vs family overall |"
                ),
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in validation["by_family"]:
            lines.append(
                f"| {row['family']} | {row['all_cells']} | "
                f"{row['overall']['f1']:.4f} | {row['hard_slice_cells']} | "
                f"{row['hard_slice']['f1']:.4f} | "
                f"{row['delta_vs_family_overall']['f1']:.4f} |"
            )

    lines.extend(scaffold.render_stop_rule_outcome_section(audit))
    lines.extend(scaffold.render_promotion_gates_section(audit))
    lines.extend(scaffold.render_report_footer(audit, _result_paragraph(audit)))
    return "\n".join(lines)


def write_report(
    *,
    repo_root: Path = REPO_ROOT,
    report_path: Path = REPORT_PATH,
) -> Path:
    return scaffold.write_validation_report(
        build_audit=build_robustness_validation_audit,
        render_markdown=render_markdown,
        repo_root=repo_root,
        report_path=report_path,
    )


def _validation_readout(repo_root: Path, artifact: Mapping[str, Any]) -> dict[str, Any]:
    rows = reliability._load_jsonl(repo_root / str(artifact["path"]))
    cells = [_cell for row in rows for _cell in _iter_validation_cells(row)]
    hard_slice_cells = [cell for cell in cells if cell["perturbation_families"]]
    non_hard_slice_cells = [cell for cell in cells if not cell["perturbation_families"]]
    overall = _aggregate_cell_scores(cells)
    hard_slice_overall = _aggregate_cell_scores(hard_slice_cells)
    non_hard_slice_overall = _aggregate_cell_scores(non_hard_slice_cells)
    validity = _validity_summary(rows)
    by_family = [_family_validation_row(family, cells) for family in reliability.FAMILIES]
    return {
        "artifact_path": artifact["path"],
        "rows": len(rows),
        "eligible_cells": len(cells),
        "hard_slice_cells": len(hard_slice_cells),
        "non_hard_slice_cells": len(non_hard_slice_cells),
        "overall": overall,
        "hard_slice_overall": hard_slice_overall,
        "non_hard_slice_overall": non_hard_slice_overall,
        "hard_slice_delta_vs_overall": _score_delta(hard_slice_overall, overall),
        "by_perturbation_family": [
            _perturbation_family_row(family, cells, overall)
            for family in robustness_panels.MINIMUM_PERTURBATION_FAMILIES
        ],
        "by_family": by_family,
        **validity,
    }


def _iter_validation_cells(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for family in reliability.FAMILIES:
        score = reliability._row_family_score(dict(row), family)
        if score.pred_count == 0 and score.gold_count == 0:
            continue
        features = reliability._risk_features(dict(row), family)
        tags = _perturbation_tags(row, family, features)
        cells.append(
            {
                "family": family,
                "score": reliability._score_dict(score),
                "features": features,
                "perturbation_families": tags,
                "mention_validity": _mention_validity(row, family),
                "call_failure": reliability._row_has_call_error(dict(row)),
                "parse_schema_failures": reliability._row_parse_error_count(dict(row)),
            }
        )
    return cells


def _perturbation_tags(
    row: Mapping[str, Any],
    family: str,
    features: Mapping[str, Any],
) -> list[str]:
    text = _family_blob(row, family)
    tags: list[str] = []
    if family == "SeizureFrequency":
        if _HISTORICAL_RE.search(text):
            tags.append("sf_current_vs_historical")
        if _FUTURE_RE.search(text):
            tags.append("sf_current_vs_future")
    elif family == "Prescription":
        if bool(features.get("plan_language")) or _PRESCRIPTION_PLAN_RE.search(text):
            tags.append("prescription_current_vs_plan")
    elif family == "Investigations":
        if bool(features.get("result_state")) or _INVESTIGATION_RESULT_RE.search(text):
            tags.append("investigations_result_state")
    elif family == "Diagnosis":
        if int(
            features.get("deterministic_action_count") or 0
        ) > 0 or _DIAGNOSIS_ASSERTION_RE.search(text):
            tags.append("diagnosis_assertion_hierarchy")

    predicted = _family_mentions(row, family, field="predicted_mentions")
    if any(mention.get("evidence_valid") is False for mention in predicted):
        tags.append("evidence_paraphrase")
    if any(str(mention.get("evidence", "")).strip() == "" for mention in predicted):
        tags.append("evidence_deletion")
    return sorted(set(tags))


def _family_blob(row: Mapping[str, Any], family: str) -> str:
    parts: list[str] = []
    for field in ("predicted_mentions", "gold_mentions"):
        for mention in _family_mentions(row, family, field=field):
            parts.append(str(mention.get("text", "")))
            parts.append(str(mention.get("evidence", "")))
            for key, value in (mention.get("attributes") or {}).items():
                parts.append(f"{key} {value}")
            for event in mention.get("provenance") or []:
                parts.append(str(event.get("action", "")))
                parts.append(str(event.get("owner", "")))
                parts.append(json.dumps(event.get("detail", {}), sort_keys=True))
    return " ".join(parts)


def _family_mentions(
    row: Mapping[str, Any],
    family: str,
    *,
    field: str,
) -> list[dict[str, Any]]:
    return [
        dict(mention) for mention in row.get(field, []) if str(mention.get("entity", "")) == family
    ]


def _validity_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    mention_count = evidence_invalid = evidence_empty = 0
    call_failures = parse_schema_failures = schema_invalid_rows = 0
    for row in rows:
        if reliability._row_has_call_error(dict(row)):
            call_failures += 1
        row_parse_failures = reliability._row_parse_error_count(dict(row))
        parse_schema_failures += row_parse_failures
        if row_parse_failures:
            schema_invalid_rows += 1
        for mention in row.get("predicted_mentions", []):
            mention_count += 1
            if mention.get("evidence_valid") is False:
                evidence_invalid += 1
            if str(mention.get("evidence", "")).strip() == "":
                evidence_empty += 1
    return {
        "predicted_mentions": mention_count,
        "schema_validity_rate": scaffold.round_rate(len(rows) - schema_invalid_rows, len(rows)),
        "evidence_validity_rate": scaffold.round_rate(
            mention_count - evidence_invalid - evidence_empty,
            mention_count,
        ),
        "evidence_invalid_mentions": evidence_invalid,
        "evidence_empty_mentions": evidence_empty,
        "call_failures": call_failures,
        "parse_schema_failures": parse_schema_failures,
    }


def _mention_validity(row: Mapping[str, Any], family: str) -> dict[str, int]:
    mentions = _family_mentions(row, family, field="predicted_mentions")
    evidence_invalid = sum(1 for mention in mentions if mention.get("evidence_valid") is False)
    evidence_empty = sum(
        1 for mention in mentions if str(mention.get("evidence", "")).strip() == ""
    )
    return {
        "predicted_mentions": len(mentions),
        "evidence_invalid_mentions": evidence_invalid,
        "evidence_empty_mentions": evidence_empty,
    }


def _perturbation_family_row(
    perturbation_family: str,
    cells: Sequence[Mapping[str, Any]],
    overall: Mapping[str, Any],
) -> dict[str, Any]:
    family_cells = [cell for cell in cells if perturbation_family in cell["perturbation_families"]]
    score = _aggregate_cell_scores(family_cells)
    return {
        "perturbation_family": perturbation_family,
        "cells": len(family_cells),
        "primary_family": _primary_family_for_perturbation(perturbation_family),
        "score": score,
        "delta_vs_overall": _score_delta(score, overall),
        **_cell_validity_rates(family_cells),
    }


def _family_validation_row(family: str, cells: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    family_cells = [cell for cell in cells if cell["family"] == family]
    hard_cells = [cell for cell in family_cells if cell["perturbation_families"]]
    overall = _aggregate_cell_scores(family_cells)
    hard_slice = _aggregate_cell_scores(hard_cells)
    return {
        "family": family,
        "all_cells": len(family_cells),
        "hard_slice_cells": len(hard_cells),
        "overall": overall,
        "hard_slice": hard_slice,
        "delta_vs_family_overall": _score_delta(hard_slice, overall),
    }


def _cell_validity_rates(cells: Sequence[Mapping[str, Any]]) -> dict[str, float | None]:
    if not cells:
        return {
            "schema_validity_rate": None,
            "evidence_validity_rate": None,
        }
    parse_failures = sum(int(cell["parse_schema_failures"]) for cell in cells)
    mentions = sum(int(cell["mention_validity"]["predicted_mentions"]) for cell in cells)
    evidence_issues = sum(
        int(cell["mention_validity"]["evidence_invalid_mentions"])
        + int(cell["mention_validity"]["evidence_empty_mentions"])
        for cell in cells
    )
    return {
        "schema_validity_rate": scaffold.round_rate(len(cells) - parse_failures, len(cells)),
        "evidence_validity_rate": scaffold.round_rate(mentions - evidence_issues, mentions),
    }


def _aggregate_cell_scores(cells: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return reliability._aggregate_scores([cell["score"] for cell in cells])


def _score_delta(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, float]:
    return {
        "precision": round(float(left["precision"]) - float(right["precision"]), 4),
        "recall": round(float(left["recall"]) - float(right["recall"]), 4),
        "f1": round(float(left["f1"]) - float(right["f1"]), 4),
    }


def _promotion_gates(
    preflight: Mapping[str, Any],
    validation: Mapping[str, Any] | None,
) -> list[dict[str, str]]:
    if validation is None:
        return [
            scaffold.gate(
                "Frozen panel run completed once", "not_evaluable", "No eligible artifact."
            ),
            scaffold.gate(
                "Minimum perturbation taxonomy covered",
                "not_evaluable",
                "No eligible artifact.",
            ),
            scaffold.gate(
                "Overall and per-family score deltas reported",
                "not_evaluable",
                "No eligible artifact.",
            ),
            scaffold.gate(
                "Schema and evidence validity reported",
                "not_evaluable",
                "No eligible artifact.",
            ),
            scaffold.gate(
                "Aggregate-only row-inspection boundary preserved",
                "not_evaluable",
                "No eligible artifact.",
            ),
        ]
    preflight_counts = preflight["panel_coverage"]["by_perturbation_family"]
    natural_counts = {
        row["perturbation_family"]: int(row["cells"])
        for row in validation["by_perturbation_family"]
    }
    minimum_preflight = bool(preflight["panel_coverage"]["minimum_coverage_met"])
    natural_core = all(
        natural_counts.get(family, 0) > 0
        for family in (
            "sf_current_vs_historical",
            "sf_current_vs_future",
            "prescription_current_vs_plan",
            "investigations_result_state",
            "diagnosis_assertion_hierarchy",
        )
    )
    evidence_stress_preflight = all(
        int(preflight_counts.get(family, 0)) > 0
        for family in ("evidence_paraphrase", "evidence_deletion")
    )
    return [
        scaffold.gate(
            "Frozen panel run completed once",
            "pass",
            "Accepted current-code full-200 artifact was read once for aggregate metrics.",
        ),
        scaffold.gate(
            "Minimum perturbation taxonomy covered",
            "pass" if minimum_preflight and natural_core and evidence_stress_preflight else "fail",
            (
                "Natural full-200 hard-slice counts cover SF, Prescription, "
                "Investigations, and Diagnosis; evidence paraphrase/deletion "
                "are covered by the frozen adversarial fixture preflight."
            ),
        ),
        scaffold.gate(
            "Overall and per-family score deltas reported",
            "pass" if validation["hard_slice_cells"] > 0 and validation["by_family"] else "fail",
            f"Hard-slice cells reported: {validation['hard_slice_cells']}.",
        ),
        scaffold.gate(
            "Schema and evidence validity reported",
            "pass",
            (
                f"Schema validity {validation['schema_validity_rate']:.4f}; "
                f"evidence validity {validation['evidence_validity_rate']:.4f}."
            ),
        ),
        scaffold.gate(
            "Aggregate-only row-inspection boundary preserved",
            "pass",
            "Report emits counts and scores only, with no row-level examples or identifiers.",
        ),
    ]


def _result_paragraph(audit: Mapping[str, Any]) -> str:
    if audit["stop_rule_outcome"]["promotion_decision"] != "promoted":
        return (
            "The robustness candidate is not promoted. Keep the scorecard claim "
            "at preflight-only robustness status until a fresh candidate passes "
            "aggregate validation."
        )
    validation = audit["validation_readout"]
    return (
        "The frozen robustness taxonomy is promoted as aggregate full-200 "
        "hard-slice validation evidence for the current-code v08-shaped surface. "
        f"Overall F1 is {validation['overall']['f1']:.4f}; hard-slice F1 is "
        f"{validation['hard_slice_overall']['f1']:.4f} across "
        f"{validation['hard_slice_cells']} eligible family cells. The claim does "
        "not convert adversarial evidence paraphrase/deletion fixtures into "
        "naturally observed full-200 failures."
    )


def _primary_family_for_perturbation(perturbation_family: str) -> str:
    if perturbation_family.startswith("sf_"):
        return "SeizureFrequency"
    if perturbation_family.startswith("prescription_"):
        return "Prescription"
    if perturbation_family.startswith("investigations_"):
        return "Investigations"
    if perturbation_family.startswith("diagnosis_"):
        return "Diagnosis"
    return "cross-family evidence stress"
