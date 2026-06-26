"""Row-level essential-family error ledger."""

from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    ERROR_TYPES,
    ESSENTIAL_ATOMIC_CONCEPT_ONLY,
    ESSENTIAL_CLINICAL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.projection import (
    as_predicted,
    strip_and_project,
    strip_gold_cui,
    strip_prediction_cui,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    MatchConfig,
    benchmark_config_for,
    concept_keys,
    frequency_state_keys,
    investigation_component_keys,
    match_key,
    prescription_component_keys,
    semantic_config_for,
)


def _counter_match_counts(
    gold_keys: Sequence[Hashable],
    pred_keys: Sequence[Hashable],
) -> tuple[int, int, int]:
    gold = Counter(gold_keys)
    pred = Counter(pred_keys)
    tp = sum((gold & pred).values())
    return tp, max(0, sum(gold.values()) - tp), max(0, sum(pred.values()) - tp)


def _limited_counter_examples(keys: Sequence[Hashable], limit: int = 4) -> str:
    examples = []
    for key, count in Counter(keys).most_common(limit):
        suffix = f" x{count}" if count > 1 else ""
        examples.append(f"{key!r}{suffix}")
    return "; ".join(examples)


def _entity_letter(
    letter_id: str,
    note_text: str,
    annotations: Sequence[ExectAnnotation],
) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note_text, annotations=tuple(annotations))


def _pred_to_exect_with_note(pred: PredictedLetter, note_text: str) -> ExectLetter:
    return ExectLetter(
        letter_id=pred.letter_id,
        note_text=note_text,
        annotations=tuple(
            ExectAnnotation(
                entity=m.entity,
                text=m.text,
                attributes=dict(m.attributes),
            )
            for m in pred.mentions
        ),
    )


def _primary_row_key_sets(
    *,
    family: str,
    gold: ExectLetter,
    pred: ExectLetter,
) -> tuple[list[Hashable], list[Hashable], list[Hashable]]:
    if family == PRESCRIPTION.name:
        gold_keys = prescription_component_keys(
            gold.entities(family),
            "clinical_headline",
            gold.note_text,
        )
        pred_keys = prescription_component_keys(
            pred.entities(family),
            "clinical_headline",
            pred.note_text,
        )
        return gold_keys, pred_keys, pred_keys
    if family == SEIZURE_FREQUENCY.name:
        gold_keys = frequency_state_keys(gold.entities(family), "clinical_headline")
        pred_keys = frequency_state_keys(pred.entities(family), "clinical_headline")
        return gold_keys, pred_keys, pred_keys
    if family == INVESTIGATIONS.name:
        gold_keys = investigation_component_keys(gold.entities(family), "clinical_headline")
        pred_keys = investigation_component_keys(pred.entities(family), "clinical_headline")
        return gold_keys, pred_keys, pred_keys
    if family in ESSENTIAL_ATOMIC_CONCEPT_ONLY:
        return (
            concept_keys(gold.entities(family), family, "concept"),
            concept_keys(pred.entities(family), family, "concept"),
            concept_keys(pred.annotations, family, "concept"),
        )
    raise ValueError(f"Unsupported essential family {family!r}")


def _entity_match_tp(
    gold: ExectLetter,
    pred: ExectLetter,
    family: str,
    config: MatchConfig,
) -> int:
    return _counter_match_counts(
        [match_key(a, config) for a in gold.entities(family)],
        [match_key(a, config) for a in pred.entities(family)],
    )[0]


def _exact_evidence_counts(
    gold: ExectLetter,
    pred: PredictedLetter,
    family: str,
) -> tuple[int, int, int, str]:
    note = gold.note_text or ""
    predicted = 0
    exact = 0
    failures: list[str] = []
    for mention in pred.mentions:
        if mention.entity != family:
            continue
        predicted += 1
        evidence = mention.evidence.strip()
        if evidence and note and evidence in note:
            exact += 1
        else:
            failures.append(evidence or "<missing>")
    return predicted, exact, predicted - exact, "; ".join(failures[:4])


def row_level_error_ledger(
    *,
    architecture: str,
    ownership: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[PredictedLetter],
    families: Sequence[str] = ESSENTIAL_CLINICAL_ENTITIES,
) -> list[dict[str, Any]]:
    """Build a dev-row essential-family error ledger from replayed artifacts."""

    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    projected_by_id = {
        letter.letter_id: letter for letter in strip_and_project(as_predicted(pred_letters))
    }
    rows: list[dict[str, Any]] = []
    for gold in gold_letters:
        pred = pred_by_id.get(
            gold.letter_id,
            PredictedLetter(letter_id=gold.letter_id, mentions=()),
        )
        projected = projected_by_id.get(gold.letter_id, pred)

        gold_cui_free = strip_gold_cui([gold])[0]
        pred_cui_free = _pred_to_exect_with_note(strip_prediction_cui([pred])[0], gold.note_text)
        projected_exect = _pred_to_exect_with_note(projected, gold.note_text)
        raw_pred_exect = _pred_to_exect_with_note(pred, gold.note_text)

        for family in families:
            family_gold = _entity_letter(
                gold_cui_free.letter_id,
                gold_cui_free.note_text,
                gold_cui_free.entities(family),
            )
            family_pred = _entity_letter(
                pred_cui_free.letter_id,
                pred_cui_free.note_text,
                pred_cui_free.entities(family),
            )
            gold_keys, home_pred_keys, recall_pred_keys = _primary_row_key_sets(
                family=family,
                gold=gold_cui_free,
                pred=pred_cui_free,
            )
            _, candidate_miss, _ = _counter_match_counts(gold_keys, recall_pred_keys)
            _, _, wrong_detail_selection = _counter_match_counts(
                gold_keys,
                home_pred_keys,
            )
            semantic_tp = _entity_match_tp(
                family_gold,
                family_pred,
                family,
                semantic_config_for(family),
            )
            projected_benchmark_tp = _entity_match_tp(
                gold,
                projected_exect,
                family,
                benchmark_config_for(family),
            )
            projection_gap = max(0, semantic_tp - projected_benchmark_tp)
            evidence_predicted, exact_evidence, evidence_failure, evidence_examples = (
                _exact_evidence_counts(gold, pred, family)
            )
            counts = {
                "candidate_miss": candidate_miss,
                "wrong_detail_selection": wrong_detail_selection,
                "projection_gap": projection_gap,
                "evidence_failure": evidence_failure,
            }
            base = {
                "architecture": architecture,
                "ownership": ownership,
                "letter_id": gold.letter_id,
                "family": family,
                "gold_count": len(gold_keys),
                "pred_count": len(home_pred_keys),
                "primary_tp": _counter_match_counts(gold_keys, recall_pred_keys)[0],
                "candidate_miss": candidate_miss,
                "wrong_detail_selection": wrong_detail_selection,
                "projection_gap": projection_gap,
                "evidence_failure": evidence_failure,
                "semantic_tp": semantic_tp,
                "projected_benchmark_tp": projected_benchmark_tp,
                "raw_benchmark_tp": _entity_match_tp(
                    gold,
                    raw_pred_exect,
                    family,
                    benchmark_config_for(family),
                ),
                "evidence_predicted": evidence_predicted,
                "exact_evidence": exact_evidence,
                "gold_examples": _limited_counter_examples(gold_keys),
                "pred_examples": _limited_counter_examples(home_pred_keys),
                "evidence_examples": evidence_examples,
            }
            for error_type in ERROR_TYPES:
                count = counts[error_type]
                if count <= 0:
                    continue
                rows.append({**base, "error_type": error_type, "count": count})
    return rows
