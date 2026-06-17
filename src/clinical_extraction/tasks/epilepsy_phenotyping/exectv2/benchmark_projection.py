"""Shared benchmark-format projection helpers for ExECTv2.

This module owns finite CUI/CUIPhrase lookup for the active ExECTv2 entity
engines. The lookup is intentionally benchmark-format projection: it attaches
ontology-shaped attributes after a clinical fact has already been selected, and
it returns no projection for unknown phrases rather than guessing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    ONSET,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import normalize_phrase


@dataclass(frozen=True)
class BenchmarkConcept:
    """Benchmark-facing concept projection for one extracted clinical mention."""

    canonical: str
    cui: str
    cui_phrase: str


_PRESCRIPTION_ENTRIES: tuple[tuple[BenchmarkConcept, tuple[str, ...]], ...] = (
    (BenchmarkConcept("lamotrigine", "C0064636", "lamotrigine"), ("lamotrigine",)),
    (BenchmarkConcept("lamictal", "C0678180", "lamictal"), ("lamictal",)),
    (BenchmarkConcept("levetiracetam", "C0377265", "levetiracetam"), ("levetiracetam",)),
    (BenchmarkConcept("keppra", "C0876060", "keppra"), ("keppra",)),
    (
        BenchmarkConcept("sodium-valproate", "C0037567", "sodium-valproate"),
        (
            "sodium valproate",
            "sodium-valproate",
            "sodiumvalproate",
            "valproate",
            "episenta",
        ),
    ),
    (BenchmarkConcept("epilim", "C0591451", "epilim"), ("epilim", "eplim")),
    (
        BenchmarkConcept("epilim-chrono", "C0591452", "epilim-chrono"),
        ("epilim chrono", "epilim-chrono"),
    ),
    (BenchmarkConcept("carbamazepine", "C0006949", "carbamazepine"), ("carbamazepine",)),
    (BenchmarkConcept("tegretol", "C0700087", "tegretol"), ("tegretol", "tegretaol")),
    (
        BenchmarkConcept("zonisamide", "C0078844", "zonisamide"),
        ("zonisamide", "zobisamide", "zonismaide"),
    ),
    (BenchmarkConcept("clobazam", "C0055891", "clobazam"), ("clobazam",)),
    (
        BenchmarkConcept("brivaracetam", "C1699861", "brivaracetam"),
        ("brivaracetam", "brivitiracetam", "brivetiracetam"),
    ),
    (BenchmarkConcept("topiramate", "C0076829", "topiramate"), ("topiramate",)),
    (BenchmarkConcept("perampanel", "C2698764", "perampanel"), ("perampanel",)),
    (BenchmarkConcept("phenytoin", "C0031507", "phenytoin"), ("phenytoin",)),
    (
        BenchmarkConcept("phenobarbital", "C0031412", "phenobarbitone"),
        ("phenobarbital", "phenobarbitone"),
    ),
    (
        BenchmarkConcept("eslicarbazepine", "C2725260", "eslicarbazepine"),
        ("eslicarbazepine", "eslicarbazepine acetate", "eslicarbazepineacetate"),
    ),
    (BenchmarkConcept("oxcarbazepine", "C0069751", "oxcarbazepine"), ("oxcarbazepine",)),
    (BenchmarkConcept("lacosamide", "C0893761", "lacosamide"), ("lacosamide",)),
    (BenchmarkConcept("midazolam", "C0026056", "midazolam"), ("midazolam",)),
    (BenchmarkConcept("pregabalin", "C0657912", "pregabalin"), ("pregabalin",)),
    (BenchmarkConcept("gabapentin", "C0060926", "gabapentin"), ("gabapentin",)),
    (
        BenchmarkConcept("carbamazepine", "C0006949", "carbamazepine"),
        ("carbamazapine", "carbmazapine"),
    ),
)
PRESCRIPTION_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase(variant): concept
    for concept, variants in _PRESCRIPTION_ENTRIES
    for variant in variants
}
PRESCRIPTION_SURFACE_FORMS: tuple[str, ...] = tuple(
    variant for _concept, variants in _PRESCRIPTION_ENTRIES for variant in variants
)

_DIAGNOSIS_ENTRIES: tuple[tuple[BenchmarkConcept, tuple[str, ...]], ...] = (
    (BenchmarkConcept("Epilepsy", "C0014544", "epilepsy"), ("epilepsy",)),
    (BenchmarkConcept("Epilepsy", "C0014547", "focal epilepsy"), ("focal epilepsy",)),
    (
        BenchmarkConcept("Epilepsy", "C0014547", "focal-onset epilepsy"),
        ("focal-onset epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014556", "temporal lobe epilepsy"),
        ("temporal lobe epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0270853", "juvenile myoclonic epilepsy"),
        ("juvenile myoclonic epilepsy", "jme"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014544", "symptomatic epilepsy"),
        ("symptomatic epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014547", "symptomatic structural focal epilepsy"),
        ("symptomatic structural focal epilepsy",),
    ),
)
_DIAGNOSIS_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase(variant): concept
    for concept, variants in _DIAGNOSIS_ENTRIES
    for variant in variants
}
DIAGNOSIS_SURFACE_FORMS: tuple[str, ...] = tuple(
    variant for _concept, variants in _DIAGNOSIS_ENTRIES for variant in variants
)

_INVESTIGATION_CONCEPT_BY_RESULT: dict[tuple[str, str | None], BenchmarkConcept] = {
    ("EEG", "Abnormal"): BenchmarkConcept("EEG", "C0151611", "eeg abnormal"),
    ("EEG", "Normal"): BenchmarkConcept("EEG", "C0744602", "eeg normal"),
    ("EEG", "Unknown"): BenchmarkConcept("EEG", "C0013819", "EEG"),
    ("MRI", "Normal"): BenchmarkConcept("MRI", "C0436481", "mri normal"),
    ("MRI", "Abnormal"): BenchmarkConcept("MRI", "C1319851", "mri abnormal"),
    ("CT", "Normal"): BenchmarkConcept("CT", "C0560017", "ct normal"),
    ("CT", "Abnormal"): BenchmarkConcept("CT", "C0436539", "ct abnormal"),
    ("CT", "Unknown"): BenchmarkConcept("CT", "C3515741", "ct-unknown"),
    ("EEG", None): BenchmarkConcept("EEG", "C0013819", "EEG"),
    ("MRI", None): BenchmarkConcept("MRI", "C0436539", "MRI"),
    ("CT", None): BenchmarkConcept("CT", "C0040405", "CT"),
}
_ONSET_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase("epilepsy"): BenchmarkConcept("epilepsy", "C0014544", "epilepsy"),
    normalize_phrase("seizures"): BenchmarkConcept("seizures", "C0036572", "seizures"),
    normalize_phrase("seizure"): BenchmarkConcept("seizure", "C0036572", "seizures"),
}


def prescription_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark medication concept for ``phrase`` if known."""

    return PRESCRIPTION_CONCEPT_BY_PHRASE.get(normalize_phrase(phrase))


def diagnosis_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark diagnosis concept for ``phrase`` if known."""

    return _DIAGNOSIS_CONCEPT_BY_PHRASE.get(normalize_phrase(phrase))


def investigation_concept(modality: str, result: str | None) -> BenchmarkConcept | None:
    """Return the benchmark investigation concept for a modality/result pair."""

    return _INVESTIGATION_CONCEPT_BY_RESULT.get((modality.upper(), result))


def onset_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark onset concept for a source-near onset phrase."""

    return _ONSET_CONCEPT_BY_PHRASE.get(normalize_phrase(phrase))


def attach_benchmark_concept(
    attributes: Mapping[str, str],
    concept: BenchmarkConcept,
    *,
    canonical_key: str | None = None,
) -> dict[str, str]:
    """Attach CUI attributes and, optionally, the concept canonical value."""

    projected = dict(attributes)
    if canonical_key is not None:
        projected[canonical_key] = concept.canonical
    projected.update({"CUI": concept.cui, "CUIPhrase": concept.cui_phrase})
    return projected


def project_cuis(prediction: PredictedLetter) -> PredictedLetter:
    """Attach known active-entity CUIs to a prediction without changing phrases."""

    mentions = tuple(_project_mention_cui(mention) for mention in prediction.mentions)
    projected_count = sum(
        1
        for before, after in zip(prediction.mentions, mentions, strict=True)
        if "CUI" not in before.attributes and "CUI" in after.attributes
    )
    diagnostics = dict(prediction.diagnostics)
    diagnostics["cui_projected_mentions"] = projected_count
    return PredictedLetter(
        letter_id=prediction.letter_id,
        mentions=mentions,
        diagnostics=diagnostics,
    )


def _project_mention_cui(mention: PredictedMention) -> PredictedMention:
    if "CUI" in mention.attributes:
        return mention

    concept = _concept_for_mention(mention)
    if concept is None:
        return mention

    canonical_key = _canonical_key_for_entity(mention.entity)
    return PredictedMention(
        entity=mention.entity,
        text=mention.text,
        attributes=attach_benchmark_concept(
            mention.attributes,
            concept,
            canonical_key=canonical_key,
        ),
        evidence=mention.evidence,
        evidence_span=mention.evidence_span,
        rationale=mention.rationale,
        confidence=mention.confidence,
        uncertainty_flags=mention.uncertainty_flags,
        component_owner=mention.component_owner,
    )


def _concept_for_mention(mention: PredictedMention) -> BenchmarkConcept | None:
    if mention.entity == PRESCRIPTION.name:
        drug_name = mention.attributes.get("DrugName")
        return prescription_concept(drug_name or mention.text)
    if mention.entity == DIAGNOSIS.name:
        return diagnosis_concept(mention.text)
    if mention.entity == INVESTIGATIONS.name:
        modality = _investigation_modality_from_attributes(mention.attributes) or mention.text
        result = _investigation_result_from_attributes(mention.attributes, modality)
        return investigation_concept(modality, result)
    if mention.entity == ONSET.name:
        return onset_concept(mention.text)
    return None


def _canonical_key_for_entity(entity: str) -> str | None:
    if entity == PRESCRIPTION.name:
        return "DrugName"
    if entity == DIAGNOSIS.name:
        return "DiagCategory"
    return None


def _investigation_modality_from_attributes(attributes: Mapping[str, str]) -> str | None:
    for modality in ("EEG", "MRI", "CT"):
        if attributes.get(f"{modality}_Performed") == "Yes" or f"{modality}_Results" in attributes:
            return modality
    return None


def _investigation_result_from_attributes(
    attributes: Mapping[str, str],
    modality: str,
) -> str | None:
    canonical = modality.upper()
    result = attributes.get(f"{canonical}_Results")
    return result if result in {"Normal", "Abnormal", "Unknown"} else None
