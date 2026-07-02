"""Replay the ``clinical_headline`` layer for Prescription and Investigations.

Prescription and Investigations both score ``clinical_headline`` as a simple,
symmetric, home-tagged multiset match over
``clinical_headline_unit_keys(entity, annotations, note_text)``
(``scoring/prescription.py::score_prescription_components``,
``scoring/investigations.py::score_investigations_components`` -- see
``_DEDUPING_HEADLINE_ENTITIES`` in ``scoring/match.py``, which excludes both).
Diagnosis (asymmetric recall-pool) and SeizureFrequency (per-letter state-set)
use different, already-canonicalized scoring conventions with their own row
analysis scripts (``exectv2_{dx,sf}_canonical_row_analysis.py``); those are
backfilled into the ledger, not replayed by this module (see
``backfill_dx_sf.py``).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Sequence
from dataclasses import dataclass

from clinical_extraction.core.scoring import PRF1, prf1_from_counts
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import clinical_headline_unit_keys

SUPPORTED_ENTITIES: tuple[str, ...] = ("Prescription", "Investigations")


@dataclass(frozen=True)
class DisagreementCase:
    """One clinical_headline key gold and prediction disagree on, for one letter."""

    letter_id: str
    disagreement_type: str  # "missed" | "spurious"
    match_key: Hashable
    #: The gold mention(s) in this letter that produced ``match_key`` (empty for "spurious").
    gold_mentions: tuple[ExectAnnotation, ...]
    #: The predicted mention(s) in this letter that produced ``match_key`` (empty for "missed").
    pred_mentions: tuple[ExectAnnotation, ...]


def replay_clinical_headline(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
) -> tuple[list[DisagreementCase], PRF1]:
    """Per-letter multiset diff on ``clinical_headline_unit_keys``, decomposed to cases.

    Returns ``(cases, aggregate_prf1)``. Callers MUST self-validate
    ``aggregate_prf1`` against the entity's official scorer
    (``score_prescription_components``/``score_investigations_components``
    ``.clinical_headline``) before trusting the per-case decomposition --
    the same discipline ``exectv2_{dx,sf}_canonical_row_analysis.py`` already
    apply to their own replays.
    """

    if entity not in SUPPORTED_ENTITIES:
        raise ValueError(f"match_replay only supports {SUPPORTED_ENTITIES}, got {entity!r}")

    gold_by_id = {letter.letter_id: letter for letter in gold_letters}
    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())

    cases: list[DisagreementCase] = []
    tp = fp = fn = 0

    for letter_id in all_ids:
        gold_letter = gold_by_id.get(letter_id)
        pred_letter = pred_by_id.get(letter_id)
        gold_anns = gold_letter.entities(entity) if gold_letter else ()
        pred_anns = pred_letter.entities(entity) if pred_letter else ()
        note_text = gold_letter.note_text if gold_letter else ""

        gold_by_key = _group_by_key(entity, gold_anns, note_text)
        pred_by_key = _group_by_key(entity, pred_anns, note_text)

        gold_counter = Counter({key: len(anns) for key, anns in gold_by_key.items()})
        pred_counter = Counter({key: len(anns) for key, anns in pred_by_key.items()})

        tp += sum((gold_counter & pred_counter).values())
        missed_counter = gold_counter - pred_counter
        spurious_counter = pred_counter - gold_counter
        fn += sum(missed_counter.values())
        fp += sum(spurious_counter.values())

        # Expand by multiplicity: a key missing/spurious 2x within one letter (gold or
        # the model asserting the same clinical_headline unit twice) is 2 scoring units
        # and must become 2 cases, or the case list under-counts the fn/fp aggregate.
        for key, count in missed_counter.items():
            for _ in range(count):
                cases.append(
                    DisagreementCase(
                        letter_id=letter_id,
                        disagreement_type="missed",
                        match_key=key,
                        gold_mentions=tuple(gold_by_key.get(key, ())),
                        pred_mentions=(),
                    )
                )
        for key, count in spurious_counter.items():
            for _ in range(count):
                cases.append(
                    DisagreementCase(
                        letter_id=letter_id,
                        disagreement_type="spurious",
                        match_key=key,
                        gold_mentions=(),
                        pred_mentions=tuple(pred_by_key.get(key, ())),
                    )
                )

    return cases, prf1_from_counts(tp, fp, fn)


def _group_by_key(
    entity: str,
    annotations: Sequence[ExectAnnotation],
    note_text: str,
) -> dict[Hashable, list[ExectAnnotation]]:
    """Map each annotation to its (0 or 1) clinical_headline key.

    Mirrors ``scoring/match.py::headline_duplicate_tags``'s per-mention key
    computation (``clinical_headline_unit_keys(entity, [a], note_text)`` for a
    single annotation), the established pattern for going from an aggregate
    key list back to which mention(s) produced each key.
    """

    grouped: dict[Hashable, list[ExectAnnotation]] = {}
    for annotation in annotations:
        keys = clinical_headline_unit_keys(entity, [annotation], note_text)
        for key in keys:
            grouped.setdefault(key, []).append(annotation)
    return grouped
