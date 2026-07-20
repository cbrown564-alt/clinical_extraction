"""Projection of validated mentions into scorer-facing predicted letters.

Pure relocation from ``llm_only_key_entities_structured``. No logic changes.
"""

from __future__ import annotations

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ENTITY_REGISTRY,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    check_evidence,
    repair_attributes,
)

from .constants import (
    COMPONENT_OWNER,
    KEY_ENTITY_NAMES,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
)
from .records import (
    MentionForEvidence,
)


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionForEvidence],
    *,
    note_text: str,
    prompt_version: str = PROMPT_VERSION,
    component_owner: str = COMPONENT_OWNER,
    pipeline_family: str = PIPELINE_FAMILY,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    entity_valid: list[MentionForEvidence] = []
    for mention in mentions:
        if mention.entity not in KEY_ENTITY_NAMES:
            all_warnings.append(f"dropped_out_of_scope_entity: {mention.entity!r}")
            continue
        repaired = _repair_evidence_from_mention_text(mention, note_text, all_warnings)
        entity_valid.append(repaired)

    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        entity_valid, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = ENTITY_REGISTRY[mention.entity]
        attrs, projection_warnings = _strip_model_supplied_projection_attrs(
            dict(mention.attributes)
        )
        all_warnings.extend(f"{mention.entity}: {warning}" for warning in projection_warnings)
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=mention.entity,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=component_owner,
            )
        )

    predicted_mentions = _apply_render_safety_gates(predicted_mentions, all_warnings)

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": prompt_version,
                    "pipeline_family": pipeline_family,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def _repair_evidence_from_mention_text(
    mention: MentionForEvidence,
    note_text: str,
    warnings: list[str],
) -> MentionForEvidence:
    """Use exact model-selected mention text as evidence for source-near entities."""

    if mention.evidence and evidence_is_substring(note_text, mention.evidence):
        return mention
    if (
        mention.entity in {PRESCRIPTION.name, DIAGNOSIS.name}
        and mention.text
        and evidence_is_substring(note_text, mention.text)
    ):
        warnings.append(f"repaired_evidence_from_mention_text: text={mention.text!r}")
        return mention.model_copy(update={"evidence": mention.text})
    return mention


_SF_STATE_ATTRS = {
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "TimePeriod",
    "TimeSince_or_TimeOfEvent",
    "FrequencyChange",
    "PointInTime",
    "DayDate",
    "MonthDate",
    "YearDate",
    "AgeLower",
    "AgeUpper",
    "AgeUnit",
}


def _apply_render_safety_gates(
    mentions: list[PredictedMention],
    warnings: list[str],
) -> list[PredictedMention]:
    gated: list[PredictedMention] = []
    for mention in mentions:
        if mention.entity == SEIZURE_FREQUENCY.name and not _has_sf_state(mention):
            warnings.append(
                f"SeizureFrequency: dropped_no_frequency_state_rendering: {mention.text!r}"
            )
            continue
        gated.append(mention)
    return _drop_duplicate_modality_only_investigations(gated, warnings)


def _has_sf_state(mention: PredictedMention) -> bool:
    return any(
        key in _SF_STATE_ATTRS and str(value).strip() for key, value in mention.attributes.items()
    )


def _drop_duplicate_modality_only_investigations(
    mentions: list[PredictedMention],
    warnings: list[str],
) -> list[PredictedMention]:
    result_bearing_modalities = {
        modality
        for mention in mentions
        if mention.entity == INVESTIGATIONS.name
        for modality in _investigation_modalities(mention)
        if _has_investigation_result(mention, modality)
    }
    if not result_bearing_modalities:
        return mentions

    kept: list[PredictedMention] = []
    for mention in mentions:
        modalities = _investigation_modalities(mention)
        if (
            mention.entity == INVESTIGATIONS.name
            and modalities
            and not any(_has_investigation_result(mention, modality) for modality in modalities)
            and any(modality in result_bearing_modalities for modality in modalities)
        ):
            warnings.append(
                f"Investigations: dropped_duplicate_modality_only_rendering: {mention.text!r}"
            )
            continue
        kept.append(mention)
    return kept


def _investigation_modalities(mention: PredictedMention) -> set[str]:
    modalities: set[str] = set()
    for key in mention.attributes:
        for modality in ("MRI", "CT", "EEG"):
            if key.startswith(f"{modality}_"):
                modalities.add(modality)
    return modalities


def _has_investigation_result(mention: PredictedMention, modality: str) -> bool:
    return bool(str(mention.attributes.get(f"{modality}_Results", "")).strip())


def _strip_model_supplied_projection_attrs(
    attrs: dict[str, str],
) -> tuple[dict[str, str], list[str]]:
    stripped = dict(attrs)
    warnings: list[str] = []
    for key in ("CUI", "CUIPhrase"):
        if key in stripped:
            stripped.pop(key)
            warnings.append(f"dropped_model_supplied_projection_attribute: {key!r}")
    return stripped, warnings
