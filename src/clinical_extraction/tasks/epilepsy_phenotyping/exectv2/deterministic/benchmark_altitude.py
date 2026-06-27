"""Deterministic benchmark-altitude projection for ExECTv2 (satellite 09 Phase F).

The selection/arbitration analysis (``docs/research/exectv2_gpt_first_error_analysis_2026-06-18``)
proved that the LLM clinical layer (the bare-union per-entity hybrid) finds 84% of
gold concepts but lands them at gold's exact phrase altitude only 38% of the time,
and scatters named seizure types across the wrong entity. This module is the
deterministic projection the plan assigns to non-LLM code: it normalizes the LLM
candidates toward the benchmark's representation convention **without adding any
clinical fact and without dropping recall**. It is reported as projection credit,
never as LLM clinical reasoning.

Three principled (non-memorising) transforms, applied to a fixed LLM prediction:

1. **Compound splitting.** Gold decomposes a compound diagnostic clause
   (``complex partial seizures with secondary generalised tonic-clonic seizures``)
   into atomic mentions. Split Diagnosis / SeizureFrequency / PatientHistory
   phrases on ``with`` / ``and`` / comma connectors into atomic concepts, each
   inheriting the parent's attributes.
2. **Seizure-type entity normalization.** A named focal / generalised / partial /
   tonic-clonic / myoclonic / absence seizure type filed as PatientHistory is, by
   the benchmark convention, also a Diagnosis (DiagCategory=MultipleSeizures). Add
   the Diagnosis copy (the PatientHistory copy is kept — recall-preserving).
   Non-epilepsy attack types (febrile / dissociative / non-epileptic / psychogenic)
   are excluded.
3. **Attribute-convention defaults.** Affirmed findings default Certainty=5 /
   Negation=Affirmed when unstated, matching the benchmark's affirmed-default.

CUI projection (``benchmark_projection.project_cuis``) runs after, unchanged.
"""

from __future__ import annotations

from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    COMPOUND_ENTITIES,
    apply_affirmed_defaults,
    diagnosis_copy,
    is_epilepsy_seizure_type,
        split_compound_phrase,
    with_text,
)


def project_altitude(prediction: PredictedLetter) -> PredictedLetter:
    """Apply the three benchmark-altitude transforms, then CUI projection.

    Recall-preserving: every input mention survives (possibly split and/or copied);
    exact within-entity duplicates are collapsed.
    """
    produced: list[PredictedMention] = []
    for mention in prediction.mentions:
        if mention.entity in COMPOUND_ENTITIES:
            parts = split_compound_phrase(mention.text)
        else:
            parts = [mention.text]
        for part in parts:
            base = with_text(mention, part)
            produced.append(base)
            if base.entity == "PatientHistory" and is_epilepsy_seizure_type(normalize_phrase(part)):
                produced.append(diagnosis_copy(base, part))

    produced = [apply_affirmed_defaults(m) for m in produced]

    deduped: list[PredictedMention] = []
    seen: set[tuple] = set()
    for m in produced:
        key = (
            m.entity,
            normalize_phrase(m.text),
            tuple(sorted((k, v) for k, v in m.attributes.items() if k not in {"CUI", "CUIPhrase"})),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(m)

    projected = project_cuis(
        PredictedLetter(
            letter_id=prediction.letter_id,
            mentions=tuple(deduped),
            diagnostics={**dict(prediction.diagnostics), "benchmark_altitude_projected": True},
        )
    )
    return projected


def project_altitude_mentions(
    letter_id: str, mentions: Sequence[PredictedMention]
) -> tuple[PredictedMention, ...]:
    """Convenience wrapper returning just the projected mention tuple."""
    return project_altitude(PredictedLetter(letter_id=letter_id, mentions=tuple(mentions))).mentions
