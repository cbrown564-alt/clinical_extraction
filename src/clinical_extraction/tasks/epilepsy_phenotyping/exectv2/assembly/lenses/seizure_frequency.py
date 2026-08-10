"""SeizureFrequency entity lenses for ExECTv2 assembly."""

from __future__ import annotations

from collections.abc import Mapping

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    ProvenanceEvent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lens_ops import (
    LensPolicy,
    LensResult,
    evidence_is_grounded,
    finding_with_text_attributes,
    source_for_residual,
    text_counts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

from .base import SeizureFrequencyLens, ThinArtifactLens


class SeizureFrequencyDictionaryLens(ThinArtifactLens):
    """v10 SeizureFrequency: pass-through lens adapter.

    SeizureFrequency extraction and state projection are owned by model sidecars
    and ``sf_state_projection_suppression_v01``. Standard-dictionary rewrites
    and residual additions are not applied in the assembly stage.
    """

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        return super().reconcile(store, policy=policy)


def _sf_recovery_key(finding: ClinicalFinding) -> tuple[str, ...]:
    return _sf_recovery_key_from_parts(finding.text, finding.attributes)


def _sf_recovery_key_from_parts(
    text: str,
    attributes: Mapping[str, object],
) -> tuple[str, ...]:
    attrs = {str(key): str(value) for key, value in attributes.items()}
    concept = attrs.get("CUI") or normalize_phrase(text)
    if attrs.get("NumberOfSeizures") == "0":
        state = "seizure-free"
    elif any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ) and any(
        key in attrs
        for key in (
            "TimePeriod",
            "YearDate",
            "MonthDate",
            "DayDate",
            "PointInTime",
        )
    ):
        state = "active-rate"
    elif attrs.get("FrequencyChange"):
        state = "unknown"
    else:
        state = "unknown"
    if state == "active-rate":
        fingerprint_keys = (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimePeriod",
            "YearDate",
            "MonthDate",
            "DayDate",
            "PointInTime",
            "TimeSince_or_TimeOfEvent",
        )
        fingerprint = "|".join(f"{key}={attrs[key]}" for key in fingerprint_keys if key in attrs)
        if fingerprint:
            return concept, state, fingerprint
    return concept, state


def _sf_added_finding(
    store: ClinicalFindingStore,
    *,
    text: str,
    evidence: str,
    attributes: dict[str, str],
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> ClinicalFinding | None:
    source = source_for_residual(
        store,
        entity=SEIZURE_FREQUENCY.name,
        selected=selected,
        policy=policy,
        ownership_suffix="standard_dictionary_sf_residual",
    )
    if source is None:
        return None
    return ClinicalFinding(
        finding_id=(
            f"{store.letter_id}:{policy.producer_id}:SeizureFrequency:lens:{lens_id}:"
            f"{normalize_phrase(text).replace(' ', '_')}"
        ),
        letter_id=store.letter_id,
        entity=SEIZURE_FREQUENCY.name,
        text=text,
        attributes={str(key): str(value) for key, value in attributes.items()},
        evidence=evidence,
        normalized_concept=attributes.get("CUI") or text,
        assertion=None,
        confidence="high",
        source=source,
        provenance=(
            ProvenanceEvent(
                stage="entity_lens",
                action="added_sf_residual_convention_from_dictionary",
                owner="standard_dictionary",
                portability="seizure_frequency",
                detail={
                    "lens_id": lens_id,
                    "producer_id": policy.producer_id,
                    "source_lane": policy.source_lane,
                    "rule_category": "seizure_frequency",
                    "target_text": text,
                    "evidence": evidence,
                },
            ),
        ),
        rationale="The source phrase matches a bounded dev residual seizure-frequency pattern.",
        evidence_valid=evidence_is_grounded(store.note_text, evidence),
        raw_surface=False,
    )


__all__ = [
    "SeizureFrequencyDictionaryLens",
    "SeizureFrequencyLens",
]
