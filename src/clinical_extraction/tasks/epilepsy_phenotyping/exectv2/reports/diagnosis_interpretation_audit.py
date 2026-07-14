"""Build the pre-adjudication substrate for the ExECTv2 Diagnosis audit."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Literal

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    annotation_clinical_concepts,
    collapse_concepts_to_most_specific,
    concepts_hierarchically_related,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
)

DIAGNOSIS = "Diagnosis"
SCHEMA_VERSION = "exectv2_diagnosis_interpretation_audit_v1"
PROTOCOL_COMMIT = "6277796a0f4a8ee2afe793e6f1dd33a20c2e5ad2"
DEFAULT_LLM_ONLY = Path(
    "experiments/exectv2_gepa_dedup_gpt41mini_h2mb8_20260628.jsonl"
)
DEFAULT_LLM_WITH_RULES = Path(
    "experiments/exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.jsonl"
)
Direction = Literal["missed", "spurious"]


@dataclass(frozen=True)
class ConceptMatch:
    matched: int
    gold_unmatched: tuple[str, ...]
    predicted_unmatched: tuple[str, ...]


@dataclass(frozen=True)
class ConceptResidual:
    letter_id: str
    direction: Direction
    concept: str


@dataclass(frozen=True)
class MethodDisagreements:
    method: str
    residuals: tuple[ConceptResidual, ...]


@dataclass(frozen=True)
class MethodInput:
    method: str
    predictions: tuple[PredictedLetter, ...]
    input_path: Path | None
    input_sha256: str


def match_diagnosis_concepts(
    gold: Sequence[str],
    predicted: Sequence[str],
) -> ConceptMatch:
    """Match de-duplicated concepts with the scorer's exact-then-hierarchy policy."""

    gold_remaining = list(dict.fromkeys(gold))
    pred_remaining = list(dict.fromkeys(predicted))
    matched = 0

    for concept in tuple(gold_remaining):
        if concept not in pred_remaining:
            continue
        gold_remaining.remove(concept)
        pred_remaining.remove(concept)
        matched += 1

    for gold_concept in tuple(gold_remaining):
        pred_concept = next(
            (
                candidate
                for candidate in pred_remaining
                if concepts_hierarchically_related(gold_concept, candidate)
            ),
            None,
        )
        if pred_concept is None:
            continue
        gold_remaining.remove(gold_concept)
        pred_remaining.remove(pred_concept)
        matched += 1

    return ConceptMatch(
        matched=matched,
        gold_unmatched=tuple(gold_remaining),
        predicted_unmatched=tuple(pred_remaining),
    )


def diagnosis_concepts(annotations: Iterable[ExectAnnotation]) -> tuple[str, ...]:
    concepts = collapse_concepts_to_most_specific(
        concept
        for annotation in annotations
        for concept in annotation_clinical_concepts(
            annotation.entity,
            annotation.text,
            annotation.attributes,
        )
        if concept.entity == DIAGNOSIS
    )
    return tuple(dict.fromkeys(concept.concept for concept in concepts))


def decompose_method(
    method: str,
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
) -> MethodDisagreements:
    pred_by_id = {prediction.letter_id: prediction for prediction in predictions}
    residuals: list[ConceptResidual] = []
    for gold_letter in gold_letters:
        prediction = pred_by_id[gold_letter.letter_id]
        pred_letter = to_exect_letter(prediction, note_text=gold_letter.note_text)
        gold = diagnosis_concepts(gold_letter.entities(DIAGNOSIS))
        recall_pool = diagnosis_concepts(pred_letter.annotations)
        home_predictions = diagnosis_concepts(pred_letter.entities(DIAGNOSIS))

        recall_match = match_diagnosis_concepts(gold, recall_pool)
        precision_match = match_diagnosis_concepts(gold, home_predictions)
        residuals.extend(
            ConceptResidual(gold_letter.letter_id, "missed", concept)
            for concept in recall_match.gold_unmatched
        )
        residuals.extend(
            ConceptResidual(gold_letter.letter_id, "spurious", concept)
            for concept in precision_match.predicted_unmatched
        )
    return MethodDisagreements(method=method, residuals=tuple(residuals))


def union_review_rows(
    methods: Sequence[MethodDisagreements],
) -> tuple[dict[str, Any], ...]:
    by_key: dict[tuple[str, Direction, str], set[str]] = {}
    for method in methods:
        for residual in method.residuals:
            key = (residual.letter_id, residual.direction, residual.concept)
            by_key.setdefault(key, set()).add(method.method)
    rows = []
    for (letter_id, direction, concept), method_names in sorted(by_key.items()):
        rows.append(
            {
                "review_key": f"{letter_id}|{direction}|{concept}",
                "letter_id": letter_id,
                "direction": direction,
                "normalized_concept": concept,
                "methods": sorted(method_names),
            }
        )
    return tuple(rows)


def build_audit_artifacts(
    *,
    out_jsonl: Path,
    out_summary: Path,
    llm_only_path: Path = DEFAULT_LLM_ONLY,
    llm_with_rules_path: Path = DEFAULT_LLM_WITH_RULES,
    audit_date: str = "2026-07-14",
) -> tuple[Path, Path]:
    gold_letters = load_letters_for_split("dev")
    gold_by_id = {letter.letter_id: letter for letter in gold_letters}
    method_inputs = _load_method_inputs(
        gold_letters,
        llm_only_path=llm_only_path,
        llm_with_rules_path=llm_with_rules_path,
    )
    disagreements = tuple(
        decompose_method(method.method, gold_letters, method.predictions)
        for method in method_inputs
    )
    base_rows = union_review_rows(disagreements)
    predictions_by_method = {
        method.method: {prediction.letter_id: prediction for prediction in method.predictions}
        for method in method_inputs
    }
    rows = [
        _enrich_review_row(
            row,
            gold=gold_by_id[str(row["letter_id"])],
            predictions_by_method=predictions_by_method,
            audit_date=audit_date,
        )
        for row in base_rows
    ]
    summary = _build_summary(
        gold_letters=gold_letters,
        method_inputs=method_inputs,
        disagreements=disagreements,
        review_rows=rows,
        audit_date=audit_date,
    )

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    out_summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out_jsonl, out_summary


def _load_method_inputs(
    gold_letters: Sequence[ExectLetter],
    *,
    llm_only_path: Path,
    llm_with_rules_path: Path,
) -> tuple[MethodInput, ...]:
    deterministic = tuple(run_all9_on_letters(gold_letters))
    llm_only = _align_predictions(gold_letters, _load_saved_predictions(llm_only_path))
    llm_with_rules = _align_predictions(
        gold_letters,
        _load_saved_predictions(llm_with_rules_path),
    )
    expected_ids = {letter.letter_id for letter in gold_letters}
    for name, predictions in (
        ("rules_only", deterministic),
        ("llm_only", llm_only),
        ("llm_with_rules", llm_with_rules),
    ):
        actual_ids = {prediction.letter_id for prediction in predictions}
        if actual_ids != expected_ids:
            missing = sorted(expected_ids - actual_ids)
            extra = sorted(actual_ids - expected_ids)
            raise ValueError(f"{name} row mismatch: missing={missing}, extra={extra}")

    deterministic_digest = _sha256_text(
        "".join(
            json.dumps(prediction.model_dump(mode="json"), sort_keys=True) + "\n"
            for prediction in deterministic
        )
    )
    return (
        MethodInput("rules_only", deterministic, None, deterministic_digest),
        MethodInput("llm_only", llm_only, llm_only_path, _sha256_file(llm_only_path)),
        MethodInput(
            "llm_with_rules",
            llm_with_rules,
            llm_with_rules_path,
            _sha256_file(llm_with_rules_path),
        ),
    )


def _align_predictions(
    gold_letters: Sequence[ExectLetter],
    predictions: Sequence[PredictedLetter],
) -> tuple[PredictedLetter, ...]:
    by_id = {prediction.letter_id: prediction for prediction in predictions}
    return tuple(by_id[gold.letter_id] for gold in gold_letters)


def _load_saved_predictions(path: Path) -> tuple[PredictedLetter, ...]:
    predictions: list[PredictedLetter] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        predictions.append(
            PredictedLetter(
                letter_id=str(row["letter_id"]),
                mentions=tuple(
                    _predicted_mention(mention) for mention in row["predicted_mentions"]
                ),
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


def _enrich_review_row(
    row: Mapping[str, Any],
    *,
    gold: ExectLetter,
    predictions_by_method: Mapping[str, Mapping[str, PredictedLetter]],
    audit_date: str,
) -> dict[str, Any]:
    gold_mentions = [_gold_mention_record(mention) for mention in gold.entities(DIAGNOSIS)]
    _add_gold_overlap_flags(gold_mentions)
    method_records: dict[str, Any] = {}
    for method in row["methods"]:
        prediction = predictions_by_method[str(method)][gold.letter_id]
        candidates = [
            _predicted_mention_record(mention)
            for mention in prediction.mentions
            if diagnosis_concepts((
                ExectAnnotation(
                    entity=mention.entity,
                    text=mention.text,
                    attributes=mention.attributes,
                ),
            ))
        ]
        method_records[str(method)] = {"diagnosis_candidate_mentions": candidates}
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_date": audit_date,
        "dataset": "ExECTv2 2025 broad epilepsy phenotyping corpus",
        "split": "dev140",
        "row_inspection_policy": "dev140_rows_permitted_test60_forbidden",
        **dict(row),
        "note_text": gold.note_text,
        "gold_diagnosis_mentions": gold_mentions,
        "method_records": method_records,
        "adjudication": {
            "status": "unreviewed",
            "concept_supported_by_note": None,
            "same_clinical_concept": None,
            "multiplicity_convention_explains_difference": None,
            "certainty_agrees_with_note": None,
            "negation_agrees_with_note": None,
            "representation_difference": [],
            "error_owner": None,
            "independent_clinical_review_required": None,
        },
    }


def _gold_mention_record(mention: ExectAnnotation) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "raw_text": mention.raw_text,
        "attributes": dict(mention.attributes),
        "start_index": mention.start_index,
        "end_index": mention.end_index,
        "normalized_diagnosis_concepts": list(diagnosis_concepts((mention,))),
        "overlaps_gold_mentions": [],
    }


def _predicted_mention_record(mention: PredictedMention) -> dict[str, Any]:
    annotation = ExectAnnotation(
        entity=mention.entity,
        text=mention.text,
        attributes=mention.attributes,
    )
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "rationale": mention.rationale,
        "confidence": mention.confidence,
        "component_owner": mention.component_owner,
        "normalized_diagnosis_concepts": list(diagnosis_concepts((annotation,))),
    }


def _add_gold_overlap_flags(records: list[dict[str, Any]]) -> None:
    for first_index, first in enumerate(records):
        first_start = first["start_index"]
        first_end = first["end_index"]
        if first_start is None or first_end is None:
            continue
        for second_index, second in enumerate(records):
            if first_index == second_index:
                continue
            second_start = second["start_index"]
            second_end = second["end_index"]
            if second_start is None or second_end is None:
                continue
            if max(first_start, second_start) < min(first_end, second_end):
                first["overlaps_gold_mentions"].append(second_index)


def _build_summary(
    *,
    gold_letters: Sequence[ExectLetter],
    method_inputs: Sequence[MethodInput],
    disagreements: Sequence[MethodDisagreements],
    review_rows: Sequence[Mapping[str, Any]],
    audit_date: str,
) -> dict[str, Any]:
    method_summaries: dict[str, Any] = {}
    disagreement_by_method = {entry.method: entry for entry in disagreements}
    for method in method_inputs:
        pred_letters = [
            to_exect_letter(prediction, note_text=gold.note_text)
            for gold, prediction in zip(gold_letters, method.predictions, strict=True)
        ]
        scores = score_concept_identity(gold_letters, pred_letters, DIAGNOSIS)
        residuals = disagreement_by_method[method.method].residuals
        direction_counts = Counter(residual.direction for residual in residuals)
        if direction_counts["missed"] != scores.concept_only.fn:
            raise AssertionError(
                f"{method.method} missed decomposition does not reproduce scorer: "
                f"{direction_counts['missed']} != {scores.concept_only.fn}"
            )
        if direction_counts["spurious"] != scores.concept_only.fp:
            raise AssertionError(
                f"{method.method} spurious decomposition does not reproduce scorer: "
                f"{direction_counts['spurious']} != {scores.concept_only.fp}"
            )
        method_summaries[method.method] = {
            "input_path": str(method.input_path).replace("\\", "/")
            if method.input_path
            else None,
            "input_sha256": method.input_sha256,
            "input_sha256_mode": (
                "working_tree_file_bytes" if method.input_path else "canonical_prediction_json"
            ),
            "prediction_source": "saved_jsonl" if method.input_path else "deterministic_no_call",
            "row_count": len(method.predictions),
            "scores": {
                "concept_only": scores.concept_only.model_dump(mode="json"),
                "concept_negation": scores.concept_negation.model_dump(mode="json"),
                "concept_assertion": scores.concept_assertion.model_dump(mode="json"),
            },
            "disagreements": {
                "missed": direction_counts["missed"],
                "spurious": direction_counts["spurious"],
                "total": len(residuals),
                "letters": len({residual.letter_id for residual in residuals}),
            },
        }
    intersections: dict[str, int] = {}
    method_names = sorted(method_summaries)
    row_methods = [set(str(method) for method in row["methods"]) for row in review_rows]
    for size in range(2, len(method_names) + 1):
        for group in combinations(method_names, size):
            intersections["&".join(group)] = sum(
                set(group).issubset(methods) for methods in row_methods
            )
    exclusive_membership = Counter("&".join(sorted(methods)) for methods in row_methods)
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_date": audit_date,
        "protocol_source_commit": PROTOCOL_COMMIT,
        "working_tree_at_predeclaration": "dirty",
        "dataset": "ExECTv2 2025 broad epilepsy phenotyping corpus",
        "split": "dev140",
        "row_count": len(gold_letters),
        "row_inspection_policy": "dev140_rows_permitted_test60_forbidden",
        "call_mode": "no_calls_saved_replay_and_deterministic_generation",
        "gold_sha256": _gold_digest(gold_letters),
        "scorer": (
            "score_concept_identity Diagnosis: entity-agnostic recall, home-tagged precision, "
            "concept de-duplication, specificity collapse, hierarchy reconciliation"
        ),
        "methods": method_summaries,
        "union": {
            "review_row_count": len(review_rows),
            "letter_count": len({str(row["letter_id"]) for row in review_rows}),
            "direction_counts": dict(Counter(str(row["direction"]) for row in review_rows)),
            "inclusive_method_intersections": intersections,
            "exclusive_method_membership": dict(sorted(exclusive_membership.items())),
        },
        "adjudication_status": "unreviewed",
        "claim_boundary": (
            "Pre-adjudication development substrate only; not corrected gold, clinical "
            "validation, test60 evidence, or holdout generalization."
        ),
    }


def _gold_digest(gold_letters: Sequence[ExectLetter]) -> str:
    payload = [
        {
            "letter_id": letter.letter_id,
            "note_text": letter.note_text,
            "annotations": [
                {
                    "entity": mention.entity,
                    "text": mention.text,
                    "raw_text": mention.raw_text,
                    "attributes": dict(mention.attributes),
                    "start_index": mention.start_index,
                    "end_index": mention.end_index,
                }
                for mention in letter.annotations
            ],
        }
        for letter in gold_letters
    ]
    return _sha256_text(json.dumps(payload, sort_keys=True))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
