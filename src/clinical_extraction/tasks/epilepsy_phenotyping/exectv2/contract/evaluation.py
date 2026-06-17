"""Per-entity gold and scoring policy for ExECTv2.

The ExECTv2 gold has entity-specific representation and scoring quirks. Keeping
them here prevents loader, scorer, and extractor de-duplication from growing
separate one-off policy constants.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    ONSET,
    PATIENT_HISTORY,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
    WHEN_DIAGNOSED,
)

PhraseTarget = Literal["raw_text", "cuiphrase"]

DEFAULT_BENCHMARK_IGNORE_ATTRIBUTES: frozenset[str] = frozenset({"CUIPhrase"})
SEIZURE_FREQUENCY_BENCHMARK_IGNORE_ATTRIBUTES: frozenset[str] = frozenset({
    "CUIPhrase",
    "Certainty",
    "Negation",
})
SEMANTIC_EXTRA_IGNORE_ATTRIBUTES: frozenset[str] = frozenset({"CUI"})


@dataclass(frozen=True)
class EntityEvaluationPolicy:
    """How one ExECTv2 entity is loaded, matched, and de-duplicated."""

    entity: str
    phrase_target: PhraseTarget = "raw_text"
    benchmark_ignore_attributes: frozenset[str] = field(
        default=DEFAULT_BENCHMARK_IGNORE_ATTRIBUTES
    )
    preserve_distinct_occurrences: bool = False

    @property
    def uses_cuiphrase_as_gold_text(self) -> bool:
        return self.phrase_target == "cuiphrase"

    @property
    def semantic_ignore_attributes(self) -> frozenset[str]:
        return self.benchmark_ignore_attributes | SEMANTIC_EXTRA_IGNORE_ATTRIBUTES


ENTITY_EVALUATION_POLICIES: dict[str, EntityEvaluationPolicy] = {
    spec.name: EntityEvaluationPolicy(entity=spec.name) for spec in ALL_ENTITIES
}
ENTITY_EVALUATION_POLICIES.update(
    {
        SEIZURE_FREQUENCY.name: EntityEvaluationPolicy(
            entity=SEIZURE_FREQUENCY.name,
            phrase_target="cuiphrase",
            benchmark_ignore_attributes=SEIZURE_FREQUENCY_BENCHMARK_IGNORE_ATTRIBUTES,
        ),
        DIAGNOSIS.name: EntityEvaluationPolicy(
            entity=DIAGNOSIS.name,
            phrase_target="cuiphrase",
        ),
        PATIENT_HISTORY.name: EntityEvaluationPolicy(
            entity=PATIENT_HISTORY.name,
            preserve_distinct_occurrences=True,
        ),
    }
)

_EXPECTED_ENTITY_NAMES = frozenset(
    {
        BIRTH_HISTORY.name,
        DIAGNOSIS.name,
        EPILEPSY_CAUSE.name,
        INVESTIGATIONS.name,
        ONSET.name,
        PATIENT_HISTORY.name,
        PRESCRIPTION.name,
        SEIZURE_FREQUENCY.name,
        WHEN_DIAGNOSED.name,
    }
)
if frozenset(ENTITY_EVALUATION_POLICIES) != _EXPECTED_ENTITY_NAMES:  # pragma: no cover
    raise RuntimeError("ExECTv2 evaluation policy does not cover all entities")


def evaluation_policy_for(entity: str) -> EntityEvaluationPolicy:
    """Return the explicit evaluation policy for ``entity``."""

    try:
        return ENTITY_EVALUATION_POLICIES[entity]
    except KeyError as exc:  # pragma: no cover - protected by registry tests
        raise KeyError(f"unknown ExECTv2 entity policy: {entity}") from exc


def uses_cuiphrase_as_gold_text(entity: str) -> bool:
    return evaluation_policy_for(entity).uses_cuiphrase_as_gold_text


def benchmark_ignore_attributes_for(entity: str) -> frozenset[str]:
    return evaluation_policy_for(entity).benchmark_ignore_attributes


def semantic_ignore_attributes_for(entity: str) -> frozenset[str]:
    return evaluation_policy_for(entity).semantic_ignore_attributes


def preserves_distinct_occurrences(entity: str) -> bool:
    return evaluation_policy_for(entity).preserve_distinct_occurrences
