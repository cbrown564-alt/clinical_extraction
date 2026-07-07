"""Deterministic projection entry point for the target single call.

Pure relocation from ``llm_target_indicators_single_call``. ``to_predicted_letter``
validates entity/evidence and applies deterministic schema repair/projection,
delegating to the leaf helpers in ``projection_helpers``. The deterministic
projection logic itself lives in ``sf_surface_registry``/``target_projection``
and is only imported here (``apply_all`` etc.).

Import order note: ``sf_surface_registry.adapters.projection`` is imported
before ``deterministic.normalization`` (via ``projection_helpers``) to match the
original module's import order and avoid the deterministic.normalization <->
scoring circular import.
"""

from __future__ import annotations

from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.projection import (
    ProjectionFamilySwitches,
    apply_all,
    audit_only_projection_replay_switches,
    effective_target_projection_family_switches,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    check_evidence,
    repair_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.constants import (  # noqa: E501
    COMPONENT_OWNER,
    PIPELINE_FAMILY,
    PROMPT_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.projection_helpers import (  # noqa: E501
    _deduplicate_scored_mentions,
    _expand_target_mention,
    _is_allowed_diagnosis_core,
    _is_allowed_sf_anchor,
    _is_frequency_phrase_diagnosis_context,
    _is_investigation_only_diagnosis_context,
    _is_planned_investigation,
    _is_planned_prescription,
    _is_unsupported_eeg_confirmation,
    _is_unsupported_inferred_diagnosis,
    _is_unsupported_investigation_evidence,
    _is_zero_since_only_diagnosis_context,
    _normalize_target_attributes,
    _normalize_target_text,
    _sf_state_drop_reason,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
)

__all__ = ["audit_only_projection_replay_switches", "to_predicted_letter"]


def to_predicted_letter(
    letter_id: str,
    mentions: Sequence[MentionRecord],
    *,
    note_text: str,
    projection_family_switches: ProjectionFamilySwitches | None = None,
) -> tuple[PredictedLetter, list[str]]:
    """Validate entity/evidence and apply deterministic schema repair/projection."""

    warnings: list[str] = []
    entity_valid: list[MentionRecord] = []
    for mention in mentions:
        if mention.entity not in TARGET_INDICATORS:
            warnings.append(f"dropped_non_target_entity: {mention.entity!r}")
            continue
        if mention.entity == "SeizureFrequency":
            focal_diagnosis = apply_all.empty_sf_candidate(mention)
            if focal_diagnosis is not None:
                entity_valid.append(focal_diagnosis)
                warnings.append(
                    f"projected_focal_onset_sf_candidate_to_diagnosis: {mention.text!r}"
                )
                continue
            if not mention.attributes:
                warnings.append(f"dropped_empty_sf_attributes: {mention.text!r}")
                continue
            if not _is_allowed_sf_anchor(mention.text):
                warnings.append(f"dropped_non_seizure_frequency_anchor: {mention.text!r}")
                continue
        entity_valid.append(mention)

    evidence_repaired, evidence_repair_warnings = apply_all.repair_evidence(
        entity_valid,
        note_text=note_text,
        projection_family_switches=projection_family_switches,
    )
    warnings.extend(evidence_repair_warnings)

    evidence_valid, evidence_invalid, evidence_warnings = check_evidence(
        evidence_repaired,
        note_text=note_text,
    )
    warnings.extend(evidence_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = ENTITY_REGISTRY[mention.entity]
        normalized_attrs, normalization_warnings = _normalize_target_attributes(
            mention.entity,
            {str(k): str(v) for k, v in dict(mention.attributes).items()},
            text=mention.text,
            evidence=mention.evidence,
            projection_family_switches=projection_family_switches,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in normalization_warnings)
        attrs, attr_warnings = repair_attributes(
            normalized_attrs,
            spec=spec,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in attr_warnings)
        if mention.entity == "Investigations" and not any(
            key.startswith(("CT_", "EEG_", "MRI_")) for key in attrs
        ):
            warnings.append(f"Investigations: dropped_empty_investigation_attrs: {mention.text!r}")
            continue
        text, text_warnings = _normalize_target_text(
            mention.entity,
            mention.text,
            evidence=mention.evidence,
        )
        warnings.extend(f"{mention.entity}: {warning}" for warning in text_warnings)
        if mention.entity == "SeizureFrequency":
            text, attrs, state_warnings = apply_all.project_sf_state(
                text,
                attrs,
                mention.evidence,
                projection_family_switches=projection_family_switches,
            )
            warnings.extend(f"{mention.entity}: {warning}" for warning in state_warnings)
            drop_warning = _sf_state_drop_reason(text, attrs, mention.evidence)
            if drop_warning:
                projected_diagnosis = apply_all.project_dropped_sf(
                    text,
                    mention.evidence,
                    mention,
                    component_owner=COMPONENT_OWNER,
                )
                if projected_diagnosis is not None:
                    predicted_mentions.append(projected_diagnosis)
                    warnings.append(
                        f"SeizureFrequency: projected_dropped_sf_to_diagnosis: {text!r}"
                    )
                warnings.append(f"SeizureFrequency: {drop_warning}: {text!r}")
                continue
        base_mention = PredictedMention(
            entity=mention.entity,
            text=text,
            attributes=attrs,
            evidence=mention.evidence,
            confidence=mention.confidence,
            rationale=mention.rationale,
            component_owner=COMPONENT_OWNER,
        )
        if mention.entity == "Diagnosis" and not _is_allowed_diagnosis_core(text):
            projected_sf = apply_all.project_diagnosis_frequency_header(
                base_mention,
                note_text,
            )
            if projected_sf is not None:
                predicted_mentions.append(projected_sf)
                warnings.append(
                    f"Diagnosis: projected_frequency_header_diagnosis_to_sf_state: {text!r}"
                )
                continue
            warnings.append(f"Diagnosis: dropped_non_epilepsy_core: {text!r}")
            continue
        if mention.entity == "Prescription" and _is_planned_prescription(
            base_mention,
            note_text,
        ):
            warnings.append(f"Prescription: dropped_planned_prescription: {text!r}")
            continue
        if mention.entity == "Diagnosis" and _is_zero_since_only_diagnosis_context(
            base_mention,
            note_text,
        ):
            warnings.append(f"Diagnosis: dropped_zero_since_only_diagnosis_context: {text!r}")
            continue
        if mention.entity == "Diagnosis" and _is_investigation_only_diagnosis_context(base_mention):
            warnings.append(f"Diagnosis: dropped_investigation_only_diagnosis_context: {text!r}")
            continue
        if mention.entity == "Diagnosis" and _is_frequency_phrase_diagnosis_context(base_mention):
            warnings.append(f"Diagnosis: dropped_frequency_phrase_diagnosis_context: {text!r}")
            continue
        if mention.entity == "Diagnosis" and _is_unsupported_inferred_diagnosis(base_mention):
            warnings.append(f"Diagnosis: dropped_unsupported_inferred_diagnosis: {text!r}")
            continue
        if mention.entity == "Investigations" and _is_planned_investigation(
            base_mention,
            note_text,
        ):
            warnings.append(f"Investigations: dropped_planned_investigation: {text!r}")
            continue
        if mention.entity == "Investigations" and _is_unsupported_eeg_confirmation(base_mention):
            warnings.append(f"Investigations: dropped_unsupported_eeg_confirmation: {text!r}")
            continue
        if mention.entity == "Investigations" and _is_unsupported_investigation_evidence(
            base_mention
        ):
            warnings.append(f"Investigations: dropped_unsupported_investigation_evidence: {text!r}")
            continue
        expanded_mentions, expansion_warnings = _expand_target_mention(base_mention)
        warnings.extend(f"{mention.entity}: {warning}" for warning in expansion_warnings)
        expanded_mentions, projection_warnings = apply_all.expand_mention_projections(
            entity=mention.entity,
            base_mention=base_mention,
            expanded_mentions=expanded_mentions,
            note_text=note_text,
            text=text,
            projection_family_switches=projection_family_switches,
        )
        warnings.extend(projection_warnings)
        predicted_mentions.extend(expanded_mentions)
    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(_deduplicate_scored_mentions(predicted_mentions)),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "pipeline_family": PIPELINE_FAMILY,
                    "n_evidence_invalid": len(evidence_invalid),
                    "target_projection_family_switches": (
                        effective_target_projection_family_switches(projection_family_switches)
                    ),
                    "attribute_warnings": warnings,
                },
            )
        ),
        warnings,
    )
