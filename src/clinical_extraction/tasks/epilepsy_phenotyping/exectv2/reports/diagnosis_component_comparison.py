"""Compare reviewed Diagnosis fixes by architecture and owning component."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence, Set
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_interpretation_audit import (  # noqa: E501
    decompose_method,
    diagnosis_concepts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    sha256_file,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
)

COMPARISON_SCHEMA = "exectv2_diagnosis_component_comparison_v1"
ResidualKey = tuple[str, str, str]


def summarize_residual_changes(
    *,
    baseline_keys: Set[ResidualKey],
    candidate_keys: Set[ResidualKey],
    decisions: Mapping[ResidualKey, Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize fixed-review residuals resolved, retained, and newly introduced."""

    resolved = sorted(baseline_keys - candidate_keys)
    remaining = sorted(baseline_keys & candidate_keys)
    new = sorted(candidate_keys - baseline_keys)
    resolved_triage = Counter(str(decisions[key]["triage"]) for key in resolved)
    resolved_mechanisms = Counter(str(decisions[key]["mechanism"]) for key in resolved)
    resolved_directions = Counter(
        f"{decisions[key]['triage']}:{key[1]}" for key in resolved
    )
    return {
        "resolved_review_rows": len(resolved),
        "remaining_review_rows": len(remaining),
        "new_residual_rows": len(new),
        "resolved_triage_counts": dict(sorted(resolved_triage.items())),
        "resolved_mechanism_counts": dict(sorted(resolved_mechanisms.items())),
        "resolved_triage_direction_counts": dict(sorted(resolved_directions.items())),
        "resolved_rows": [_residual_record(key, decisions.get(key)) for key in resolved],
        "new_residuals": [_residual_record(key, None) for key in new],
    }


def build_component_comparison(
    *,
    audit_summary_json: Path,
    ledger_jsonl: Path,
    sensitivity_json: Path,
    llm_candidate_jsonl: Path,
    hybrid_candidate_jsonl: Path,
    out_rules_boundary_jsonl: Path,
    out_rules_full_jsonl: Path,
    out_json: Path,
    out_md: Path,
) -> dict[str, Any]:
    """Build the final dev140 component comparison and write reproducible artifacts."""

    audit = json.loads(audit_summary_json.read_text(encoding="utf-8"))
    ledger = [
        json.loads(line)
        for line in ledger_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    sensitivity = json.loads(sensitivity_json.read_text(encoding="utf-8"))
    gold = load_letters_for_split("dev")
    decisions = {
        _row_key(row): row["review_decision"]
        for row in ledger
    }
    review_rows = {_row_key(row): row for row in ledger}
    baseline_keys = {
        method: {_row_key(row) for row in ledger if method in row.get("methods", [])}
        for method in audit["methods"]
    }

    rules_boundary = tuple(
        run_all9_on_letters(
            gold,
            include_diagnosis_resolution_candidate=True,
            include_diagnosis_benchmark_residuals=False,
        )
    )
    rules_full = tuple(
        run_all9_on_letters(
            gold,
            include_diagnosis_resolution_candidate=True,
            include_diagnosis_benchmark_residuals=True,
        )
    )
    llm_candidate = _load_saved_predictions(llm_candidate_jsonl)
    hybrid_candidate = _load_saved_predictions(hybrid_candidate_jsonl)
    _write_prediction_jsonl(out_rules_boundary_jsonl, rules_boundary)
    _write_prediction_jsonl(out_rules_full_jsonl, rules_full)

    candidates = {
        "rules_boundary_only": _candidate_summary(
            name="rules_boundary_only",
            baseline_method="rules_only",
            component="clinical_epilepsy context and surface rules",
            gold=gold,
            predictions=rules_boundary,
            baseline_keys=baseline_keys["rules_only"],
            decisions=decisions,
            review_rows=review_rows,
            input_path=out_rules_boundary_jsonl,
        ),
        "rules_full": _candidate_summary(
            name="rules_full",
            baseline_method="rules_only",
            component="clinical_epilepsy rules plus benchmark-format residual dictionary",
            gold=gold,
            predictions=rules_full,
            baseline_keys=baseline_keys["rules_only"],
            decisions=decisions,
            review_rows=review_rows,
            input_path=out_rules_full_jsonl,
        ),
        "llm_only_v02": _candidate_summary(
            name="llm_only_v02",
            baseline_method="llm_only",
            component="Diagnosis decomposer prompt v0.2; no post-model clinical repair",
            gold=gold,
            predictions=llm_candidate,
            baseline_keys=baseline_keys["llm_only"],
            decisions=decisions,
            review_rows=review_rows,
            input_path=llm_candidate_jsonl,
        ),
        "llm_with_rules_full": _candidate_summary(
            name="llm_with_rules_full",
            baseline_method="llm_with_rules",
            component="shared deterministic Diagnosis dictionary replay",
            gold=gold,
            predictions=hybrid_candidate,
            baseline_keys=baseline_keys["llm_with_rules"],
            decisions=decisions,
            review_rows=review_rows,
            input_path=hybrid_candidate_jsonl,
        ),
    }

    baselines = _baseline_summary(audit, sensitivity)
    rules_baseline_f1 = baselines["rules_only"]["fixed_primary"]["f1"]
    rules_boundary_f1 = candidates["rules_boundary_only"]["scores"]["concept_only"]["f1"]
    rules_full_f1 = candidates["rules_full"]["scores"]["concept_only"]["f1"]
    hybrid_baseline_f1 = baselines["llm_with_rules"]["fixed_primary"]["f1"]
    llm_baseline_f1 = baselines["llm_only"]["fixed_primary"]["f1"]
    report = {
        "schema_version": COMPARISON_SCHEMA,
        "dataset": audit["dataset"],
        "split": "dev140",
        "row_count": 140,
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "fixed_scorer": audit["scorer"],
        "primary_gold_or_scorer_changed": False,
        "baselines": baselines,
        "candidates": candidates,
        "component_ablations": {
            "rules_clinical_boundary_effect": {
                "from": rules_baseline_f1,
                "to": rules_boundary_f1,
                "delta_f1": rules_boundary_f1 - rules_baseline_f1,
            },
            "rules_benchmark_residual_marginal_effect": {
                "from": rules_boundary_f1,
                "to": rules_full_f1,
                "delta_f1": rules_full_f1 - rules_boundary_f1,
            },
            "hybrid_dictionary_effect": {
                "from": hybrid_baseline_f1,
                "to": candidates["llm_with_rules_full"]["scores"]["concept_only"]["f1"],
                "delta_f1": (
                    candidates["llm_with_rules_full"]["scores"]["concept_only"]["f1"]
                    - hybrid_baseline_f1
                ),
            },
            "llm_prompt_v02_effect": {
                "from": llm_baseline_f1,
                "to": candidates["llm_only_v02"]["scores"]["concept_only"]["f1"],
                "delta_f1": (
                    candidates["llm_only_v02"]["scores"]["concept_only"]["f1"]
                    - llm_baseline_f1
                ),
            },
        },
        "decision": {
            "reference": "retain_v08",
            "rules_boundary_candidate": "retain_for_development_only",
            "rules_full_residual_candidate": "reject_30_new_residuals",
            "hybrid_candidate": "retain_for_development_only",
            "llm_only_candidate": "reject_regressed_fixed_primary",
            "promotion": "do_not_promote_without_frozen_holdout_protocol",
            "reason": (
                "The deterministic components improve dev140 with attributable mechanisms, "
                "but the LLM-only candidate regresses and no test60 or independent clinical "
                "validation was used."
            ),
        },
        "inputs": {
            "audit_summary": _path_record(audit_summary_json),
            "ledger": _path_record(ledger_jsonl),
            "sensitivity": _path_record(sensitivity_json),
            "llm_candidate": _path_record(llm_candidate_jsonl),
            "hybrid_candidate": _path_record(hybrid_candidate_jsonl),
            "rules_boundary": _path_record(out_rules_boundary_jsonl),
            "rules_full": _path_record(out_rules_full_jsonl),
        },
        "claim_boundary": (
            "Development evidence on inspected dev140 only. The report does not correct gold, "
            "change the primary scorer, inspect test60, validate clinical correctness, or "
            "promote a reference."
        ),
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(report, json_path=out_json), encoding="utf-8")
    return report


def _candidate_summary(
    *,
    name: str,
    baseline_method: str,
    component: str,
    gold: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
    baseline_keys: Set[ResidualKey],
    decisions: Mapping[ResidualKey, Mapping[str, Any]],
    review_rows: Mapping[ResidualKey, Mapping[str, Any]],
    input_path: Path,
) -> dict[str, Any]:
    aligned = _align_predictions(gold, predictions)
    adapted = [
        to_exect_letter(prediction, note_text=letter.note_text)
        for letter, prediction in zip(gold, aligned, strict=True)
    ]
    scores = score_concept_identity(gold, adapted, "Diagnosis")
    residuals = decompose_method(name, gold, aligned).residuals
    candidate_keys = {(row.letter_id, row.direction, row.concept) for row in residuals}
    changes = summarize_residual_changes(
        baseline_keys=baseline_keys,
        candidate_keys=candidate_keys,
        decisions=decisions,
    )
    changes["resolved_extraction_examples"] = _resolved_extraction_examples(
        changes["resolved_rows"],
        baseline_method=baseline_method,
        review_rows=review_rows,
    )
    changes["new_residuals"] = _enrich_new_residuals(
        changes["new_residuals"], predictions=aligned
    )
    return {
        "baseline_method": baseline_method,
        "component": component,
        "input": _path_record(input_path),
        "scores": {
            "concept_only": scores.concept_only.model_dump(mode="json"),
            "concept_negation": scores.concept_negation.model_dump(mode="json"),
            "concept_assertion": scores.concept_assertion.model_dump(mode="json"),
        },
        "evidence": _evidence_summary(gold, aligned),
        "residual_changes": changes,
    }


def _resolved_extraction_examples(
    resolved_rows: Sequence[Mapping[str, Any]],
    *,
    baseline_method: str,
    review_rows: Mapping[ResidualKey, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for residual in resolved_rows:
        if residual.get("triage") != "extraction_error":
            continue
        key = (
            str(residual["letter_id"]),
            str(residual["direction"]),
            str(residual["concept"]),
        )
        review = review_rows[key]
        if key[1] == "spurious":
            mentions = review["method_records"][baseline_method][
                "diagnosis_candidate_mentions"
            ]
            evidence = [
                str(mention.get("evidence", ""))
                for mention in mentions
                if key[2] in mention.get("normalized_diagnosis_concepts", [])
            ]
        else:
            evidence = [
                str(mention.get("raw_text", ""))
                for mention in review["gold_diagnosis_mentions"]
                if key[2] in mention.get("normalized_diagnosis_concepts", [])
            ]
        examples.append(
            {
                **_residual_record(key, review["review_decision"]),
                "exact_source_evidence": sorted(set(item for item in evidence if item)),
            }
        )
    return examples


def _enrich_new_residuals(
    residuals: Sequence[Mapping[str, Any]], *, predictions: Sequence[PredictedLetter]
) -> list[dict[str, Any]]:
    by_id = {prediction.letter_id: prediction for prediction in predictions}
    enriched: list[dict[str, Any]] = []
    for residual in residuals:
        record = dict(residual)
        evidence: list[str] = []
        if residual["direction"] == "spurious":
            for mention in by_id[str(residual["letter_id"])].mentions:
                if mention.entity != "Diagnosis":
                    continue
                concepts = diagnosis_concepts(
                    (
                        ExectAnnotation(
                            entity=mention.entity,
                            text=mention.text,
                            attributes=mention.attributes,
                        ),
                    )
                )
                if residual["concept"] in concepts and mention.evidence:
                    evidence.append(mention.evidence)
        record["candidate_exact_source_evidence"] = sorted(set(evidence))
        enriched.append(record)
    return enriched


def _baseline_summary(audit: Mapping[str, Any], sensitivity: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for method, entry in sorted(audit["methods"].items()):
        result[method] = {
            "fixed_primary": entry["scores"]["concept_only"],
            "fixed_secondary": {
                "concept_negation": entry["scores"]["concept_negation"],
                "concept_assertion": entry["scores"]["concept_assertion"],
            },
            "multiplicity_and_clinical_granularity_f1": sensitivity["views"][
                "multiplicity_and_clinical_granularity"
            ]["methods"][method]["scores"]["f1"],
            "reviewed_interpretation_f1": sensitivity["views"][
                "reviewed_interpretation"
            ]["methods"][method]["scores"]["f1"],
        }
    return result


def _evidence_summary(
    gold: Sequence[ExectLetter], predictions: Sequence[PredictedLetter]
) -> dict[str, Any]:
    note_by_id = {letter.letter_id: letter.note_text for letter in gold}
    total = 0
    exact = 0
    invalid: list[dict[str, str]] = []
    for prediction in predictions:
        note = note_by_id[prediction.letter_id]
        for mention in prediction.mentions:
            if mention.entity != "Diagnosis":
                continue
            total += 1
            if mention.evidence and mention.evidence in note:
                exact += 1
            else:
                invalid.append(
                    {
                        "letter_id": prediction.letter_id,
                        "text": mention.text,
                        "evidence": mention.evidence,
                    }
                )
    return {
        "diagnosis_mentions": total,
        "exact_evidence_mentions": exact,
        "evidence_validity_rate": exact / total if total else 1.0,
        "invalid_evidence": invalid,
    }


def _load_saved_predictions(path: Path) -> tuple[PredictedLetter, ...]:
    predictions: list[PredictedLetter] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        predictions.append(
            PredictedLetter(
                letter_id=str(row["letter_id"]),
                mentions=tuple(_predicted_mention(raw) for raw in row["predicted_mentions"]),
            )
        )
    return tuple(predictions)


def _predicted_mention(raw: Mapping[str, Any]) -> PredictedMention:
    return PredictedMention(
        entity=str(raw["entity"]),
        text=str(raw.get("text", "")),
        attributes={str(key): str(value) for key, value in raw.get("attributes", {}).items()},
        evidence=str(raw.get("evidence", "")),
        rationale=str(raw.get("rationale", "")),
        confidence=raw.get("confidence"),
        uncertainty_flags=tuple(str(flag) for flag in raw.get("uncertainty_flags", ())),
        component_owner=str(raw.get("component_owner", "")),
    )


def _align_predictions(
    gold: Sequence[ExectLetter], predictions: Sequence[PredictedLetter]
) -> tuple[PredictedLetter, ...]:
    by_id = {prediction.letter_id: prediction for prediction in predictions}
    expected = {letter.letter_id for letter in gold}
    if set(by_id) != expected:
        raise ValueError("candidate prediction rows do not match dev140")
    return tuple(by_id[letter.letter_id] for letter in gold)


def _write_prediction_jsonl(path: Path, predictions: Sequence[PredictedLetter]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "letter_id": prediction.letter_id,
            "predicted_mentions": [
                mention.model_dump(mode="json") for mention in prediction.mentions
            ],
            "diagnostics": dict(prediction.diagnostics),
        }
        for prediction in predictions
    ]
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _row_key(row: Mapping[str, Any]) -> ResidualKey:
    return (str(row["letter_id"]), str(row["direction"]), str(row["normalized_concept"]))


def _residual_record(
    key: ResidualKey, decision: Mapping[str, Any] | None
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "letter_id": key[0],
        "direction": key[1],
        "concept": key[2],
    }
    if decision is not None:
        record["triage"] = decision["triage"]
        record["mechanism"] = decision["mechanism"]
    return record


def _path_record(path: Path) -> dict[str, str]:
    return {"path": str(path).replace("\\", "/"), "sha256": sha256_file(path)}



def _render_markdown(report: Mapping[str, Any], *, json_path: Path) -> str:
    baselines = report["baselines"]
    candidates = report["candidates"]
    candidate_for_method = {
        "rules_only": "rules_boundary_only",
        "llm_only": "llm_only_v02",
        "llm_with_rules": "llm_with_rules_full",
    }
    lines = [
        "# ExECTv2 Diagnosis component comparison",
        "",
        "Date: 2026-07-14  ",
        "Status: dev140 development evidence; do not promote",
        "",
        f"Machine-readable result: `{str(json_path).replace(chr(92), '/')}`",
        "",
        "## Answer",
        "",
        (
            "The completed review separates a large representation effect from a smaller "
            "extraction problem. Shared deterministic fixes improve rules-only and hybrid "
            "Diagnosis recovery on dev140. The fixed LLM-only prompt candidate regresses, "
            "so the retained v08 reference remains the control."
        ),
        "",
        "## Score layers",
        "",
        "| Architecture | Fixed baseline | Conservative sensitivity | Reviewed "
        "interpretation | Candidate fixed F1 | Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in ("rules_only", "llm_only", "llm_with_rules"):
        baseline = baselines[method]
        candidate = candidates[candidate_for_method[method]]["scores"]["concept_only"]
        base_f1 = baseline["fixed_primary"]["f1"]
        lines.append(
            f"| {method} | {base_f1:.4f} | "
            f"{baseline['multiplicity_and_clinical_granularity_f1']:.4f} | "
            f"{baseline['reviewed_interpretation_f1']:.4f} | {candidate['f1']:.4f} | "
            f"{candidate['f1'] - base_f1:+.4f} |"
        )

    lines.extend(
        [
            "",
            "## Component attribution",
            "",
            "| Component | F1 before | F1 after | Delta |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    labels = {
        "rules_clinical_boundary_effect": "Rules: clinical context and surface handling",
        "rules_benchmark_residual_marginal_effect": "Rules: residual dictionary marginal",
        "hybrid_dictionary_effect": "Hybrid: shared deterministic dictionary",
        "llm_prompt_v02_effect": "LLM-only: prompt v0.2",
    }
    for key, label in labels.items():
        row = report["component_ablations"][key]
        lines.append(
            f"| {label} | {row['from']:.4f} | {row['to']:.4f} | "
            f"{row['delta_f1']:+.4f} |"
        )

    lines.extend(["", "## Reviewed-row effects", ""])
    lines.append(
        "| Candidate | Resolved review rows | Extraction errors resolved | New residuals |"
    )
    lines.append("| --- | ---: | ---: | ---: |")
    for name in ("rules_boundary_only", "rules_full", "llm_only_v02", "llm_with_rules_full"):
        changes = candidates[name]["residual_changes"]
        extraction = changes["resolved_triage_counts"].get("extraction_error", 0)
        lines.append(
            f"| {name} | {changes['resolved_review_rows']} | {extraction} | "
            f"{changes['new_residual_rows']} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep v08 as the retained reference.",
            "- Keep the rules boundary and hybrid fixes as development candidates only.",
            (
                "- Reject the broad rules residual dictionary as a default because it adds "
                f"{candidates['rules_full']['residual_changes']['new_residual_rows']} new "
                "residuals."
            ),
            "- Reject the LLM-only v0.2 candidate because its fixed primary score regressed.",
            "- Do not inspect test60 or promote any candidate from this dev140 study.",
            "",
        ]
    )
    return "\n".join(lines)
