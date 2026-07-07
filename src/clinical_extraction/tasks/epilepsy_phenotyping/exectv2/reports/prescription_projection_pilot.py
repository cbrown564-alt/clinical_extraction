"""Phase 5 Prescription projection pilot for ExECTv2 de-duplicated facts.

The pilot is deliberately an offline report over saved rows. It measures
meaning-preserving Prescription benchmark projection separately from actions
that would add missed facts or filter model overcalls.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from clinical_extraction.core.scoring import PRF1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    canonicalize_attribute_value,
    canonicalize_medication_name,
    score_prescription_benchmark_projection,
    score_prescription_components,
)

PRESCRIPTION_ENTITY = "Prescription"
PIPELINE_FAMILY = "exectv2_phase5_prescription_projection_pilot"
SOURCE_FREQUENCY_RE = re.compile(
    r"\b(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+daily|od|o\.d\.|"
    r"once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|nightly|tds|"
    r"t\.d\.s\.|three\s+times\s+(?:a\s+)?day|prn|p\.r\.n\.|"
    r"as\s+required|when\s+required|as\s+needed|rescue)\b",
    re.IGNORECASE,
)


class ProjectionScoreLine(StrEnum):
    LLM_ONLY_MEANING_PRESERVING_PROJECTION = "llm_only_meaning_preserving_projection"
    HYBRID_RESCUE = "hybrid_rescue"
    VERIFIER_FILTERED = "verifier_filtered"


@dataclass(frozen=True)
class PrescriptionProjectionRule:
    rule_id: str
    score_line: ProjectionScoreLine
    portability_category: str
    description: str
    allowed_in_llm_only: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "score_line": self.score_line.value,
            "portability_category": self.portability_category,
            "allowed_in_llm_only": self.allowed_in_llm_only,
            "description": self.description,
        }


PRESCRIPTION_PROJECTION_RULES: tuple[PrescriptionProjectionRule, ...] = (
    PrescriptionProjectionRule(
        "prescription_drugname_cui_projection",
        ProjectionScoreLine.LLM_ONLY_MEANING_PRESERVING_PROJECTION,
        "benchmark_format",
        "Attach benchmark CUI/CUIPhrase to a model-selected medication identity.",
        True,
    ),
    PrescriptionProjectionRule(
        "prescription_brand_generic_equivalence",
        ProjectionScoreLine.LLM_ONLY_MEANING_PRESERVING_PROJECTION,
        "benchmark_format",
        "Score brand and generic names as the same medication identity.",
        True,
    ),
    PrescriptionProjectionRule(
        "prescription_frequency_abbreviation_rendering",
        ProjectionScoreLine.LLM_ONLY_MEANING_PRESERVING_PROJECTION,
        "general",
        "Render source-stated frequency abbreviations such as BD/OD/TDS as accepted values.",
        True,
    ),
    PrescriptionProjectionRule(
        "prescription_dose_unit_normalization",
        ProjectionScoreLine.LLM_ONLY_MEANING_PRESERVING_PROJECTION,
        "general",
        "Normalize stated dose units without changing the selected medication.",
        True,
    ),
    PrescriptionProjectionRule(
        "prescription_prn_frequency_rendering",
        ProjectionScoreLine.LLM_ONLY_MEANING_PRESERVING_PROJECTION,
        "clinical_epilepsy",
        "Render source-stated PRN/rescue frequency as As_Required.",
        True,
    ),
    PrescriptionProjectionRule(
        "prescription_missing_medication_rescue",
        ProjectionScoreLine.HYBRID_RESCUE,
        "clinical_epilepsy",
        "Add a medication regimen present in gold/source but missed by the model.",
        False,
    ),
    PrescriptionProjectionRule(
        "prescription_missing_dose_or_frequency_completion",
        ProjectionScoreLine.HYBRID_RESCUE,
        "clinical_epilepsy",
        "Complete a model-selected medication with dose or frequency the model omitted.",
        False,
    ),
    PrescriptionProjectionRule(
        "prescription_duplicate_regimen_collapse",
        ProjectionScoreLine.VERIFIER_FILTERED,
        "benchmark_format",
        "Drop duplicate model-emitted regimen rows after the model selected them.",
        False,
    ),
    PrescriptionProjectionRule(
        "prescription_unsupported_medication_rejection",
        ProjectionScoreLine.VERIFIER_FILTERED,
        "clinical_epilepsy",
        "Reject a model-emitted medication not supported by the gold/source target.",
        False,
    ),
)


def build_prescription_projection_pilot(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_artifact: str = "in-memory",
) -> dict[str, Any]:
    """Build the Phase 5 Prescription projection pilot from saved run rows."""

    gold_letters = [_letter_from_row(row, "gold_mentions") for row in rows]
    raw_letters = [_letter_from_row(row, "structured_mentions_final") for row in rows]
    projected_letters = [_letter_from_row(row, "predicted_mentions") for row in rows]
    accepted_examples: list[dict[str, Any]] = []
    boundary_examples: list[dict[str, Any]] = []
    rule_counts: Counter[str] = Counter()
    boundary_counts: Counter[str] = Counter()

    for row, gold, raw, projected in zip(
        rows, gold_letters, raw_letters, projected_letters, strict=True
    ):
        _count_accepted_projection_actions(
            row,
            raw,
            projected,
            rule_counts,
            accepted_examples,
        )
        _count_boundary_actions(
            row,
            gold,
            projected,
            boundary_counts,
            boundary_examples,
        )

    raw_scores = _prescription_scores(gold_letters, raw_letters)
    projected_scores = _prescription_scores(gold_letters, projected_letters)
    return {
        "pipeline_family": PIPELINE_FAMILY,
        "source_artifact": source_artifact,
        "row_count": len(rows),
        "taxonomy": [rule.as_dict() for rule in PRESCRIPTION_PROJECTION_RULES],
        "rule_counts": _complete_rule_counts(rule_counts),
        "boundary_counts": _complete_rule_counts(boundary_counts),
        "score_lines": {
            "raw_model": {
                "status": "measured",
                "scores": raw_scores,
            },
            "llm_only_meaning_preserving_projection": {
                "status": "measured",
                "scores": projected_scores,
                "delta_vs_raw_model": _score_deltas(raw_scores, projected_scores),
            },
            "hybrid_rescue": {
                "status": "not_applied",
                "reason": (
                    "Phase 5 pilot counts rescue-eligible boundaries but does not "
                    "add missed medications to the LLM-only score line."
                ),
                "boundary_rule_counts": _score_line_counts(
                    boundary_counts,
                    ProjectionScoreLine.HYBRID_RESCUE,
                ),
            },
            "verifier_filtered": {
                "status": "not_applied",
                "reason": (
                    "Phase 5 pilot counts verifier-filter candidates but does not "
                    "drop model overcalls from the LLM-only score line."
                ),
                "boundary_rule_counts": _score_line_counts(
                    boundary_counts,
                    ProjectionScoreLine.VERIFIER_FILTERED,
                ),
            },
        },
        "accepted_projection_examples": accepted_examples[:10],
        "boundary_violation_examples": boundary_examples[:10],
        "attribution_note": (
            "LLM-only projection keeps the model-selected Prescription inventory "
            "fixed. Hybrid rescue and verifier-filtered actions are counted as "
            "separate candidate score lines and are not applied here."
        ),
    }


def render_prescription_projection_pilot_markdown(pilot: Mapping[str, Any]) -> str:
    lines = [
        "# ExECTv2 Phase 5 Prescription Projection Pilot",
        "",
        f"- Source artifact: `{pilot.get('source_artifact', 'in-memory')}`",
        f"- Rows: `{pilot.get('row_count', 0)}`",
        f"- Attribution: {pilot['attribution_note']}",
        "",
        "## Projection Taxonomy",
        "",
        "| Rule | Score line | Portability | LLM-only allowed |",
        "| --- | --- | --- | --- |",
    ]
    for rule in pilot["taxonomy"]:
        lines.append(
            f"| `{rule['rule_id']}` | `{rule['score_line']}` | "
            f"`{rule['portability_category']}` | {rule['allowed_in_llm_only']} |"
        )

    lines.extend(
        [
            "",
            "## Score Lines",
            "",
            (
                "| Score line | Status | Clinical headline F1 | Benchmark+CUI F1 | "
                "Drug+CUI F1 | Delta benchmark+CUI |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, score_line in pilot["score_lines"].items():
        scores = score_line.get("scores") or {}
        deltas = score_line.get("delta_vs_raw_model") or {}
        lines.append(
            f"| `{name}` | {score_line['status']} | "
            f"{_score_value(scores, 'clinical_headline', 'f1'):.3f} | "
            f"{_score_value(scores, 'benchmark_with_cui', 'f1'):.3f} | "
            f"{_score_value(scores, 'drugname_cui_projection', 'f1'):.3f} | "
            f"{_delta_value(deltas, 'benchmark_with_cui'):.3f} |"
        )

    lines.extend(["", "## Rule Counts", ""])
    lines.extend(_counts_table("Accepted LLM-only projection rules", pilot["rule_counts"]))
    lines.extend(["", "## Boundary Counts", ""])
    lines.extend(
        _counts_table(
            "Separated hybrid/verifier boundary rules",
            pilot["boundary_counts"],
        )
    )

    lines.extend(["", "## Accepted Projection Examples", ""])
    lines.extend(_examples_lines(pilot.get("accepted_projection_examples") or []))
    lines.extend(["", "## Boundary Violation Examples", ""])
    lines.extend(_examples_lines(pilot.get("boundary_violation_examples") or []))
    lines.append("")
    return "\n".join(lines)


def read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_pilot_json(pilot: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pilot, indent=2, sort_keys=True), encoding="utf-8")


def write_pilot_markdown(pilot: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_prescription_projection_pilot_markdown(pilot), encoding="utf-8")


def _letter_from_row(row: Mapping[str, Any], key: str) -> ExectLetter:
    mentions = row.get(key) or []
    annotations = tuple(
        ExectAnnotation(
            entity=str(mention.get("entity", "")),
            text=str(mention.get("text", "")),
            attributes={
                str(attr_key): str(attr_value)
                for attr_key, attr_value in dict(mention.get("attributes") or {}).items()
            },
            raw_text=str(mention.get("evidence") or ""),
        )
        for mention in mentions
        if str(mention.get("entity", "")) == PRESCRIPTION_ENTITY
    )
    return ExectLetter(
        letter_id=str(row.get("letter_id", "")),
        note_text=_note_text_from_row(row),
        annotations=annotations,
    )


def _note_text_from_row(row: Mapping[str, Any]) -> str:
    prompt_json = str(
        row.get("inventory_prompt_input_json") or row.get("generation_prompt_input_json") or ""
    )
    if not prompt_json:
        return ""
    try:
        prompt = json.loads(prompt_json)
    except json.JSONDecodeError:
        return ""
    letter = prompt.get("letter") if isinstance(prompt, dict) else None
    if isinstance(letter, dict):
        return str(letter.get("note_text") or "")
    return ""


def _prescription_scores(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, dict[str, Any]]:
    components = score_prescription_components(gold_letters, pred_letters)
    projection = score_prescription_benchmark_projection(gold_letters, pred_letters)
    return {
        "clinical_headline": _score_counts(components.clinical_headline),
        "name": _score_counts(components.name),
        "dose": _score_counts(components.dose),
        "frequency": _score_counts(components.frequency),
        "source_stated_frequency": _score_counts(components.source_stated_frequency),
        "guideline_defaulted_frequency": _score_counts(components.guideline_defaulted_frequency),
        "phrase_scope": _score_counts(projection.phrase_scope),
        "semantic_without_cui": _score_counts(projection.semantic_without_cui),
        "benchmark_with_cui": _score_counts(projection.benchmark_with_cui),
        "drugname_cui_projection": _score_counts(projection.drugname_cui_projection),
    }


def _score_counts(score: PRF1) -> dict[str, Any]:
    return {
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
    }


def _score_deltas(
    before: Mapping[str, Mapping[str, Any]],
    after: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, float]]:
    return {
        metric: {
            "precision": round(float(after[metric]["precision"]) - float(values["precision"]), 4),
            "recall": round(float(after[metric]["recall"]) - float(values["recall"]), 4),
            "f1": round(float(after[metric]["f1"]) - float(values["f1"]), 4),
        }
        for metric, values in before.items()
        if metric in after
    }


def _count_accepted_projection_actions(
    row: Mapping[str, Any],
    raw: ExectLetter,
    projected: ExectLetter,
    rule_counts: Counter[str],
    examples: list[dict[str, Any]],
) -> None:
    raw_mentions = list(raw.annotations)
    projected_mentions = list(projected.annotations)
    for index, projected_mention in enumerate(projected_mentions):
        raw_mention = raw_mentions[index] if index < len(raw_mentions) else None
        attrs = dict(projected_mention.attributes)
        raw_attrs = dict(raw_mention.attributes) if raw_mention else {}
        if attrs.get("CUI") and attrs.get("CUI") != raw_attrs.get("CUI"):
            _record_action(
                "prescription_drugname_cui_projection",
                row,
                projected_mention,
                rule_counts,
                examples,
            )
        if _canonical_name(projected_mention) != _surface_name(projected_mention):
            _record_action(
                "prescription_brand_generic_equivalence",
                row,
                projected_mention,
                rule_counts,
                examples,
            )
        if attrs.get("Frequency") and SOURCE_FREQUENCY_RE.search(
            " ".join([projected_mention.text, str(projected_mention.raw_text or "")])
        ):
            rule_id = (
                "prescription_prn_frequency_rendering"
                if attrs.get("Frequency") == "As_Required"
                else "prescription_frequency_abbreviation_rendering"
            )
            _record_action(rule_id, row, projected_mention, rule_counts, examples)
        if attrs.get("DoseUnit") in {"mg", "g"}:
            _record_action(
                "prescription_dose_unit_normalization",
                row,
                projected_mention,
                rule_counts,
                examples,
            )


def _count_boundary_actions(
    row: Mapping[str, Any],
    gold: ExectLetter,
    projected: ExectLetter,
    boundary_counts: Counter[str],
    examples: list[dict[str, Any]],
) -> None:
    gold_keys = {_clinical_regimen_key(annotation) for annotation in gold.annotations}
    gold_keys.discard(None)
    pred_keys = {_clinical_regimen_key(annotation) for annotation in projected.annotations}
    pred_keys.discard(None)
    for key in sorted(gold_keys - pred_keys):
        _record_boundary(
            "prescription_missing_medication_rescue",
            row,
            key,
            boundary_counts,
            examples,
        )

    gold_names = {_canonical_name(annotation) for annotation in gold.annotations}
    pred_names = [_canonical_name(annotation) for annotation in projected.annotations]
    for annotation in projected.annotations:
        attrs = annotation.attributes
        if not _clinical_regimen_key(annotation) and attrs.get("DrugName"):
            _record_boundary(
                "prescription_missing_dose_or_frequency_completion",
                row,
                _name_and_text(annotation),
                boundary_counts,
                examples,
            )
        if _canonical_name(annotation) not in gold_names:
            _record_boundary(
                "prescription_unsupported_medication_rejection",
                row,
                _name_and_text(annotation),
                boundary_counts,
                examples,
            )

    for name, count in Counter(pred_names).items():
        if name and count > 1:
            _record_boundary(
                "prescription_duplicate_regimen_collapse",
                row,
                name,
                boundary_counts,
                examples,
            )


def _record_action(
    rule_id: str,
    row: Mapping[str, Any],
    annotation: ExectAnnotation,
    counts: Counter[str],
    examples: list[dict[str, Any]],
) -> None:
    counts[rule_id] += 1
    if len(examples) < 10:
        examples.append(
            {
                "letter_id": str(row.get("letter_id", "")),
                "rule_id": rule_id,
                "mention_text": annotation.text,
                "attributes": dict(annotation.attributes),
            }
        )


def _record_boundary(
    rule_id: str,
    row: Mapping[str, Any],
    detail: Any,
    counts: Counter[str],
    examples: list[dict[str, Any]],
) -> None:
    counts[rule_id] += 1
    if len(examples) < 10:
        examples.append(
            {
                "letter_id": str(row.get("letter_id", "")),
                "rule_id": rule_id,
                "detail": detail,
            }
        )


def _clinical_regimen_key(annotation: ExectAnnotation) -> tuple[str, ...] | None:
    attrs = annotation.attributes
    name = _canonical_name(annotation)
    if not name:
        return None
    frequency = str(attrs.get("Frequency") or "")
    if frequency == "As_Required":
        return ("rescue", name, frequency)
    dose = attrs.get("DrugDose")
    unit = attrs.get("DoseUnit")
    if dose and unit and frequency:
        return (
            "ordinary",
            name,
            canonicalize_attribute_value("DrugDose", str(dose)),
            canonicalize_attribute_value("DoseUnit", str(unit)),
            canonicalize_attribute_value("Frequency", frequency),
        )
    return None


def _canonical_name(annotation: ExectAnnotation) -> str:
    drug = str(annotation.attributes.get("DrugName") or annotation.text or "")
    return canonicalize_medication_name(drug)


def _surface_name(annotation: ExectAnnotation) -> str:
    return canonicalize_medication_name(annotation.text)


def _name_and_text(annotation: ExectAnnotation) -> dict[str, str]:
    return {
        "drug": str(annotation.attributes.get("DrugName") or ""),
        "text": annotation.text,
    }


def _complete_rule_counts(counts: Counter[str]) -> dict[str, int]:
    known = {rule.rule_id for rule in PRESCRIPTION_PROJECTION_RULES}
    return {rule_id: int(counts.get(rule_id, 0)) for rule_id in sorted(known)}


def _score_line_counts(
    counts: Counter[str],
    score_line: ProjectionScoreLine,
) -> dict[str, int]:
    rule_ids = {
        rule.rule_id for rule in PRESCRIPTION_PROJECTION_RULES if rule.score_line is score_line
    }
    return {rule_id: int(counts.get(rule_id, 0)) for rule_id in sorted(rule_ids)}


def _score_value(
    scores: Mapping[str, Mapping[str, Any]],
    metric: str,
    field: str,
) -> float:
    return float((scores.get(metric) or {}).get(field, 0.0))


def _delta_value(deltas: Mapping[str, Mapping[str, Any]], metric: str) -> float:
    return float((deltas.get(metric) or {}).get("f1", 0.0))


def _counts_table(title: str, counts: Mapping[str, int]) -> list[str]:
    lines = [f"### {title}", "", "| Rule | Count |", "| --- | ---: |"]
    lines.extend(f"| `{rule_id}` | {count} |" for rule_id, count in counts.items())
    return lines


def _examples_lines(examples: Sequence[Mapping[str, Any]]) -> list[str]:
    if not examples:
        return ["No examples observed."]
    return [
        (f"- `{example.get('letter_id', '')}` `{example.get('rule_id', '')}`: {example}")
        for example in examples
    ]
