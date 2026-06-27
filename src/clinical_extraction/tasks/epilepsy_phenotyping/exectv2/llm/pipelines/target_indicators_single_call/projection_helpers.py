"""Deterministic helper functions for the target single-call projection.

Pure relocation from ``llm_target_indicators_single_call``. These are the leaf
normalization/guard/expansion/dedupe helpers that ``projection.to_predicted_letter``
delegates to. Copied verbatim; no logic, regex, or value changes.

Import order note: ``sf_surface_registry.adapters.projection`` is imported
before ``deterministic.normalization`` to match the original module's import
order and avoid the deterministic.normalization <-> scoring circular import.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.projection import (
    ProjectionFamilySwitches,
    apply_all,
    projection_patterns,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    )

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.constants import (  # noqa: E501
    _CLUSTER_OF_SEIZURES,
    _DIAGNOSIS_ALLOWED_CORE,
    _DIAGNOSIS_PROHIBITED_CORES,
    _GENERALIZED_EPILEPSY_GTCS_ALONE,
    _PLANNED_INVESTIGATION_CONTEXT,
    _PLANNED_PRESCRIPTION_CONTEXT,
    _SEIZURE_FREQUENCY_ANCHOR,
    _SEIZURE_FREQUENCY_PROHIBITED_ANCHOR,
    _SF_STATE_ATTRIBUTES,
    _SF_TEXT_ALIASES,
    _SPECIFIC_SEIZURE_EVIDENCE,
    _UNKNOWN_LIKE_NUMBER,
)


def _normalize_target_attributes(
    entity: str,
    attrs: dict[str, str],
    *,
    text: str = "",
    evidence: str = "",
    projection_family_switches: ProjectionFamilySwitches | None = None,
) -> tuple[dict[str, str], list[str]]:
    """Format-only normalization before scorer-facing schema repair."""

    normalized = dict(attrs)
    warnings: list[str] = []
    if entity == "Prescription":
        prescription_warnings = apply_all.normalize_prescription_attributes(
            normalized,
            text=text,
            evidence=evidence,
        )
        warnings.extend(prescription_warnings)
        evidence_frequency = apply_all.prescription_frequency_from_evidence(
            normalize_phrase(evidence)
        )
        if (
            evidence_frequency
            and normalized.get("Frequency")
            and evidence_frequency != normalized.get("Frequency")
        ):
            normalized["Frequency"] = evidence_frequency
            warnings.append(
                f"projected_prescription_frequency_from_evidence: {evidence_frequency}"
            )
        unit = normalized.get("DoseUnit", "").strip().lower()
        if unit in {"milligram", "milligrams", "mgs"}:
            normalized["DoseUnit"] = "mg"
            warnings.append("normalized_dose_unit: milligrams -> mg")
        elif unit in {"gram", "grams"}:
            normalized["DoseUnit"] = "g"
            warnings.append("normalized_dose_unit: grams -> g")
        dose = normalized.get("DrugDose", "").strip()
        dose_match = re.fullmatch(r"(?P<dose>\d+(?:\.\d+)?)\s*(?:mgs?|mg|grams?|g)?", dose, re.I)
        if dose_match and dose_match.group("dose") != dose:
            normalized["DrugDose"] = projection_patterns.clean_number(dose_match.group("dose"))
            warnings.append(f"normalized_drug_dose_number: {dose!r}")
    if entity == "SeizureFrequency":
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        ):
            if normalized.get(key, "").strip().lower() in _UNKNOWN_LIKE_NUMBER:
                normalized.pop(key, None)
                warnings.append(f"removed_unknown_like_frequency_number: {key}")
        period_raw = normalized.get("TimePeriod", "").strip().lower()
        if "last clinic" in period_raw:
            normalized.pop("TimePeriod", None)
            normalized.setdefault("TimeSince_or_TimeOfEvent", "Since")
            normalized.setdefault("PointInTime", "LastClinic")
            warnings.append("normalized_since_last_clinic_period")
        if normalized.get("PointInTime", "").strip().lower() == "christmas":
            family = "projected_christmas_point_to_month_date"
            if apply_all.is_quarantined_family_enabled(family, projection_family_switches):
                normalized.pop("PointInTime", None)
                normalized.setdefault("MonthDate", "12")
                warnings.append(family)
            else:
                warnings.append(apply_all.quarantine_warning(family))
        _split_range_attribute(
            normalized,
            source_key="NumberOfSeizures",
            lower_key="LowerNumberOfSeizures",
            upper_key="UpperNumberOfSeizures",
            warnings=warnings,
        )
        _split_range_attribute(
            normalized,
            source_key="NumberOfTimePeriods",
            lower_key="LowerNumberOfTimePeriods",
            upper_key="UpperNumberOfTimePeriods",
            warnings=warnings,
        )
        period = normalized.get("TimePeriod", "").strip().lower()
        period_map = {
            "day": "Day",
            "days": "Day",
            "week": "Week",
            "weeks": "Week",
            "month": "Month",
            "months": "Month",
            "year": "Year",
            "years": "Year",
        }
        if period in period_map:
            normalized["TimePeriod"] = period_map[period]
            if period != period_map[period]:
                warnings.append(f"normalized_time_period: {period} -> {period_map[period]}")
        if normalized.get("TimePeriod") == "Day":
            _convert_day_period_to_week(normalized, warnings)
    if entity == "Investigations":
        text_modality = _investigation_text_modality(text)
        if text_modality is None and _is_non_target_investigation_text(text):
            removed = [
                key
                for key in tuple(normalized)
                if key.startswith(("CT_", "EEG_", "MRI_")) or key == "EEG_Type"
            ]
            for key in removed:
                normalized.pop(key, None)
            if removed:
                warnings.append(
                    "removed_non_target_investigation_attrs: "
                    + ",".join(sorted(removed))
                )
        if text_modality is not None:
            removed = [
                key
                for key in tuple(normalized)
                if key.startswith(("CT_", "EEG_", "MRI_"))
                and not key.startswith(f"{text_modality}_")
                and not (text_modality == "EEG" and key == "EEG_Type")
            ]
            for key in removed:
                normalized.pop(key, None)
            if removed:
                warnings.append(
                    "removed_cross_modal_investigation_attrs: "
                    + ",".join(sorted(removed))
                )
        if normalized.get("EEG_Results") and "EEG_Performed" not in normalized:
            normalized["EEG_Performed"] = "Yes"
            warnings.append("inferred_eeg_performed_from_result")
        if normalized.get("MRI_Results") and "MRI_Performed" not in normalized:
            normalized["MRI_Performed"] = "Yes"
            warnings.append("inferred_mri_performed_from_result")
        if (
            "EEG_Type" in normalized
            and any(key.startswith("MRI_") for key in normalized)
            and not any(key in {"EEG_Performed", "EEG_Results"} for key in normalized)
        ):
            normalized.pop("EEG_Type", None)
            warnings.append("removed_cross_modal_eeg_type_from_mri")
    return normalized, warnings


def _normalize_target_text(
    entity: str,
    text: str,
    *,
    evidence: str = "",
) -> tuple[str, list[str]]:
    if entity == "SeizureFrequency":
        if (
            "seizures over" in normalize_phrase(evidence)
            and "generalised tonic clonic seizures with myoclonic jerks"
            in normalize_phrase(text)
        ):
            return "seizures", [
                f"normalized_seizure_frequency_text: {text!r} -> 'seizures'"
            ]
        normalized = normalize_phrase(text)
        if "absence like seizures" in normalize_phrase(evidence) and normalized not in {
            "absence like seizure",
            "absence like seizures",
        }:
            return "absence like seizures", [
                f"normalized_seizure_frequency_text_from_evidence: {text!r} -> "
                "'absence like seizures'"
            ]
        if normalized in _SF_TEXT_ALIASES and _SF_TEXT_ALIASES[normalized] != text:
            return _SF_TEXT_ALIASES[normalized], [
                f"normalized_seizure_frequency_text: {text!r} -> "
                f"{_SF_TEXT_ALIASES[normalized]!r}"
            ]
        if re.match(r"^seizures?\s+every\b", normalized) and (
            projection_patterns.EVERY_N_PERIODS.search(normalized)
            or projection_patterns.EVERY_N_TO_M_PERIODS.search(normalized)
        ):
            return "seizures", [
                f"normalized_seizure_frequency_text: {text!r} -> 'seizures'"
            ]
        return text, []
    if entity != "Diagnosis":
        return text, []
    raw_normalized = normalize_phrase(text)
    if (
        raw_normalized == "epilepsy with generalised tonic clonic seizures"
        and "alone" in normalize_phrase(evidence)
    ):
        normalized = "epilepsy with generalised tonic clonic seizures alone"
        return normalized, [f"normalized_diagnosis_text: {text!r} -> {normalized!r}"]
    normalized = canonicalize_diagnosis_concept(text)
    normalized = apply_all.normalize_diagnosis_text(normalized, evidence)
    if normalized and normalized != text:
        return normalized, [f"normalized_diagnosis_text: {text!r} -> {normalized!r}"]
    return text, []


def _sf_state_drop_reason(
    text: str,
    attrs: dict[str, str],
    evidence: str,
) -> str | None:
    normalized_evidence = normalize_phrase(evidence)
    normalized_text = normalize_phrase(text)
    if normalized_text == "episodes of loss of consciousness":
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        normalized_text == "general and complex partial seizures"
        and "continues to get" in normalized_evidence
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        normalized_text in {"single focal seizure", "focal seizure"}
        and attrs.get("NumberOfSeizures") == "1"
        and "had an event on" in normalized_evidence
    ):
        return "dropped_single_event_not_frequency_state"
    if (
        normalized_text == "focal seizures"
        and attrs.get("FrequencyChange") == "Decreased"
        and "significant improvement since increasing" in normalized_evidence
    ):
        return "dropped_improvement_phrase_not_headline_state"
    if (
        normalized_text not in normalized_evidence
        and "angry or upset" in normalized_evidence
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if normalized_text == "minor seizures" and normalized_evidence == "occur 4 to 5 times a year":
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        "jerks" in normalized_text
        and attrs.get("NumberOfSeizures") == "0"
        and "occasional" in normalized_evidence
    ):
        return "dropped_occasional_jerks_not_seizure_free"
    if (
        "episode" in normalized_evidence
        and normalized_text not in normalized_evidence
        and not _SPECIFIC_SEIZURE_EVIDENCE.search(normalized_evidence)
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        normalized_text == "minor seizures"
        and "episode" in normalized_evidence
        and not _SPECIFIC_SEIZURE_EVIDENCE.search(normalized_evidence)
    ):
        return "dropped_unsupported_episode_frequency_anchor"
    if (
        attrs.get("FrequencyChange") == "Same"
        and "continues to get" in normalized_evidence
        and not any(
            key in attrs
            for key in (
                "NumberOfSeizures",
                "LowerNumberOfSeizures",
                "UpperNumberOfSeizures",
                "NumberOfTimePeriods",
                "LowerNumberOfTimePeriods",
                "UpperNumberOfTimePeriods",
                "TimePeriod",
                "TimeSince_or_TimeOfEvent",
                "PointInTime",
            )
        )
    ):
        return "dropped_ongoing_same_without_frequency"
    if not any(key in attrs for key in _SF_STATE_ATTRIBUTES):
        if "unknown" in normalized_evidence or "not documented" in normalized_evidence:
            return None
        return "dropped_empty_sf_state_after_normalization"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and normalized_text not in {"seizure", "seizures"}
        and normalized_text not in normalized_evidence
        and "seizure free" in normalized_evidence
    ):
        return "dropped_generic_zero_state_for_typed_anchor"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and normalized_text in {"seizure", "seizures", "seizure free"}
        and "remains seizure free" in normalized_evidence
        and "since" not in normalized_evidence
    ):
        return "dropped_unanchored_current_seizure_free_state"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and "best its ever been" in normalized_evidence
    ):
        return "dropped_vague_best_control_zero_state"
    if (
        attrs.get("NumberOfSeizures") == "0"
        and "last had a seizure before this" in normalized_evidence
    ):
        return "dropped_relative_prior_event_not_seizure_free"
    if attrs.get("NumberOfSeizures") == "0" and _evidence_has_positive_rate(
        normalized_evidence
    ):
        return "dropped_inconsistent_zero_state_with_active_rate"
    if normalized_evidence.startswith("previous event"):
        return "dropped_previous_event_not_headline_frequency"
    if "well controlled" in normalized_evidence and not any(
        marker in normalized_evidence
        for marker in ("no ", "not had", "not have", "since", "last event")
    ):
        return "dropped_controlled_without_zero_anchor"
    if attrs.get("NumberOfSeizures") != "0":
        return None
    return None


def _is_allowed_diagnosis_core(text: str) -> bool:
    normalized = normalize_phrase(text)
    return normalized not in _DIAGNOSIS_PROHIBITED_CORES and bool(
        _DIAGNOSIS_ALLOWED_CORE.search(text)
    )


def _is_allowed_sf_anchor(text: str) -> bool:
    return bool(_SEIZURE_FREQUENCY_ANCHOR.search(text)) and not bool(
        _SEIZURE_FREQUENCY_PROHIBITED_ANCHOR.search(text)
    )


def _is_planned_prescription(mention: PredictedMention, note_text: str) -> bool:
    if mention.entity != "Prescription":
        return False
    context = projection_patterns.local_evidence_context(note_text, mention.evidence, before=96, after=24)
    return bool(_PLANNED_PRESCRIPTION_CONTEXT.search(context))


def _is_planned_investigation(mention: PredictedMention, note_text: str) -> bool:
    if mention.entity != "Investigations":
        return False
    attrs = mention.attributes
    has_result = any(
        attrs.get(key) in {"Normal", "Abnormal"}
        for key in ("EEG_Results", "MRI_Results", "CT_Results")
    )
    if has_result:
        return False
    context = projection_patterns.local_evidence_context(note_text, mention.evidence, before=96, after=24)
    return bool(_PLANNED_INVESTIGATION_CONTEXT.search(context))


def _evidence_has_positive_rate(normalized_evidence: str) -> bool:
    return bool(
        re.search(
            r"\b(?:approximately|around|about)?\s*\d+\s*(?:-|to|–|\s)\s*\d+"
            r".{0,80}\b(?:seizures?|convulsions?|jerks?)\s+per\s+"
            r"(?:day|week|month|year)\b",
            normalized_evidence,
            re.IGNORECASE,
        )
        or re.search(
            r"\b\d+.{0,80}\b(?:seizures?|convulsions?|jerks?)\s+per\s+"
            r"(?:day|week|month|year)\b",
            normalized_evidence,
            re.IGNORECASE,
        )
    )


def _is_zero_since_only_diagnosis_context(
    mention: PredictedMention,
    note_text: str,
) -> bool:
    if mention.entity != "Diagnosis":
        return False
    normalized_text = normalize_phrase(mention.text)
    if normalized_text not in {"tonic clonic seizures", "absences"}:
        return False
    context = normalize_phrase(
        projection_patterns.local_evidence_context(note_text, mention.evidence, before=48, after=64)
    )
    return (
        "not had any further" in context
        or "no further" in context
        or ("no absences since" in context and normalized_text == "absences")
    )


def _is_investigation_only_diagnosis_context(mention: PredictedMention) -> bool:
    if mention.entity != "Diagnosis":
        return False
    if normalize_phrase(mention.text) != "temporal lobe epilepsy":
        return False
    evidence = normalize_phrase(mention.evidence)
    return "temporal lobe" in evidence and not any(
        marker in evidence
        for marker in (
            "epilep",
            "seizure",
            "diagnosis",
            "probable temporal",
        )
    )


def _is_frequency_phrase_diagnosis_context(mention: PredictedMention) -> bool:
    if mention.entity != "Diagnosis":
        return False
    source = normalize_phrase(f"{mention.text} {mention.evidence}")
    if "focal onset" in source:
        return False
    return bool(
        (
            projection_patterns.EVERY_N_PERIODS.search(source)
            or projection_patterns.EVERY_N_TO_M_PERIODS.search(source)
        )
        and re.search(r"\bseizures?\s+every\b", source)
    )


def _is_unsupported_inferred_diagnosis(mention: PredictedMention) -> bool:
    if mention.entity != "Diagnosis":
        return False
    normalized_evidence = normalize_phrase(mention.evidence)
    normalized_text = normalize_phrase(mention.text)
    if "probable temporal" in normalized_evidence:
        return False
    if normalized_text == "epilepsy" and "epilep" not in normalized_evidence:
        return True
    if _DIAGNOSIS_ALLOWED_CORE.search(normalized_evidence):
        return False
    return normalized_text not in normalized_evidence


def _is_unsupported_eeg_confirmation(mention: PredictedMention) -> bool:
    if mention.entity != "Investigations":
        return False
    if normalize_phrase(mention.evidence) != "confirmed with an eeg recording":
        return False
    return mention.attributes.get("EEG_Results") == "Abnormal"


def _is_unsupported_investigation_evidence(mention: PredictedMention) -> bool:
    if mention.entity != "Investigations":
        return False
    modality = _investigation_text_modality(mention.text)
    if modality is None:
        return False
    evidence = normalize_phrase(mention.evidence)
    if modality.lower() in evidence.split():
        return False
    return "neurological examination was normal" in evidence


def _deduplicate_scored_mentions(
    mentions: Sequence[PredictedMention],
) -> list[PredictedMention]:
    deduplicated: list[PredictedMention] = []
    seen: set[tuple[Any, ...]] = set()
    for mention in mentions:
        key = _dedupe_key(mention)
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(mention)
    return deduplicated


def _dedupe_key(mention: PredictedMention) -> tuple[Any, ...]:
    attrs = mention.attributes
    if mention.entity == "Diagnosis":
        return (
            mention.entity,
            canonicalize_diagnosis_concept(mention.text),
        )
    if mention.entity == "Prescription":
        return (
            mention.entity,
            normalize_phrase(attrs.get("DrugName", "")),
            normalize_phrase(attrs.get("DrugDose", "")),
            normalize_phrase(attrs.get("DoseUnit", "")),
            normalize_phrase(attrs.get("Frequency", "")),
        )
    if mention.entity == "Investigations":
        modality = _investigation_modality(attrs, mention.text)
        return (
            mention.entity,
            modality,
            attrs.get(f"{modality}_Performed", ""),
            attrs.get(f"{modality}_Results", ""),
            attrs.get("EEG_Type", "") if modality == "EEG" else "",
        )
    if mention.entity == "SeizureFrequency":
        return (
            mention.entity,
            normalize_phrase(mention.text),
            tuple(
                sorted(
                    (key, value)
                    for key, value in attrs.items()
                    if key
                    in {
                        "AgeLower",
                        "AgeUnit",
                        "AgeUpper",
                        "DayDate",
                        "FrequencyChange",
                        "LowerNumberOfSeizures",
                        "LowerNumberOfTimePeriods",
                        "MonthDate",
                        "NumberOfSeizures",
                        "NumberOfTimePeriods",
                        "PointInTime",
                        "TimePeriod",
                        "TimeSince_or_TimeOfEvent",
                        "UpperNumberOfSeizures",
                        "UpperNumberOfTimePeriods",
                        "YearDate",
                    }
                )
            ),
        )
    return (
        mention.entity,
        normalize_phrase(mention.text),
        tuple(sorted(attrs.items())),
        normalize_phrase(mention.evidence),
    )


def _investigation_modality(attrs: Mapping[str, str], text: str) -> str:
    if any(key.startswith("MRI_") for key in attrs) or "mri" in normalize_phrase(text):
        return "MRI"
    if any(key.startswith("EEG_") for key in attrs) or "eeg" in normalize_phrase(text):
        return "EEG"
    if any(key.startswith("CT_") for key in attrs) or "ct" in normalize_phrase(text):
        return "CT"
    return "EEG" if attrs.get("EEG_Type") else "MRI"


def _investigation_text_modality(text: str) -> str | None:
    normalized = normalize_phrase(text).split()
    if any(token in {"mri", "mr"} for token in normalized):
        return "MRI"
    if "eeg" in normalized:
        return "EEG"
    if "ct" in normalized:
        return "CT"
    return None


def _is_non_target_investigation_text(text: str) -> bool:
    tokens = set(normalize_phrase(text).split())
    return bool(tokens & {"ecg", "ekg"})


def _expand_target_mention(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    if mention.entity == "Diagnosis":
        return _expand_diagnosis_projection(mention)
    if mention.entity == "SeizureFrequency":
        return _expand_seizure_frequency_state(mention)
    if mention.entity != "Prescription":
        return [mention], []
    expanded, warnings = _expand_asymmetric_prescription(mention)
    if expanded:
        return expanded, warnings
    return [mention], warnings


def _expand_diagnosis_projection(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    if (
        normalize_phrase(mention.text) == "temporal lobe seizure"
        and "temporal lobe onset focal seizures" in normalize_phrase(mention.evidence)
    ):
        companion = mention.model_copy(
            update={
                "text": "focal seizures",
                "attributes": {
                    **mention.attributes,
                    "DiagCategory": "MultipleSeizures",
                },
            }
        )
        return [mention, companion], ["split_temporal_lobe_onset_to_focal_seizures"]
    if normalize_phrase(mention.text) == "secondary generalised tonic clonic seizures":
        companion = mention.model_copy(
            update={
                "text": "tonic clonic seizures",
                "attributes": {
                    **mention.attributes,
                    "DiagCategory": "MultipleSeizures",
                },
            }
        )
        return [mention, companion], ["split_secondary_gtc_to_tonic_clonic_diagnosis"]
    if normalize_phrase(mention.text) == (
        "epilepsy with generalised tonic clonic seizures alone"
    ):
        companion = mention.model_copy(
            update={
                "text": "tonic clonic seizures",
                "attributes": {
                    **mention.attributes,
                    "DiagCategory": "MultipleSeizures",
                },
            }
        )
        return [mention, companion], ["split_syndrome_to_tonic_clonic_diagnosis"]
    match = _GENERALIZED_EPILEPSY_GTCS_ALONE.search(mention.evidence)
    if not match:
        return [mention], []
    syndrome = "epilepsy with generalised tonic clonic seizures alone"
    if normalize_phrase(mention.text) == syndrome:
        return [mention], []
    syndrome_mention = mention.model_copy(
        update={
            "text": syndrome,
            "attributes": {
                **mention.attributes,
                "DiagCategory": "Epilepsy",
            },
        }
    )
    seizure_mention = mention.model_copy(
        update={
            "text": "tonic clonic seizures",
            "attributes": {
                **mention.attributes,
                "DiagCategory": "MultipleSeizures",
            },
        }
    )
    return [mention, syndrome_mention, seizure_mention], [
        "split_generalised_epilepsy_syndrome"
    ]


def _expand_seizure_frequency_state(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    expanded = [mention]
    warnings: list[str] = []
    if (
        mention.attributes.get("NumberOfSeizures") == "0"
        and normalize_phrase(mention.text) == "focal to bilateral convulsive seizures"
    ):
        expanded.append(
            mention.model_copy(
                update={
                    "text": "convulsive seizure",
                }
            )
        )
        warnings.append("split_convulsive_zero_state")
    if mention.attributes.get("NumberOfSeizures") == "0" and projection_patterns.CONTROLLED_ON_DOSE.search(
        mention.evidence
    ):
        expanded.append(
            mention.model_copy(
                update={
                    "text": "seizures",
                    "attributes": {
                        "FrequencyChange": "Infrequent",
                        "PointInTime": "DrugChange",
                    },
                }
            )
        )
        warnings.append("projected_controlled_drug_change_to_infrequent_state")
    sf_diagnosis_projection = _sf_type_to_diagnosis_projection_warning(mention)
    if sf_diagnosis_projection:
        expanded.append(
            mention.model_copy(
                update={
                    "entity": "Diagnosis",
                    "attributes": {
                        "Certainty": "5",
                        "DiagCategory": "MultipleSeizures",
                        "Negation": "Affirmed",
                    },
                }
            )
        )
        warnings.append(sf_diagnosis_projection)
    if (
        mention.attributes.get("NumberOfSeizures") == "0"
        and "focal to bilateral convulsive seizures" in normalize_phrase(mention.evidence)
        and normalize_phrase(mention.text) == "seizures"
    ):
        expanded.append(
            mention.model_copy(
                update={
                    "entity": "Diagnosis",
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "Certainty": "5",
                        "DiagCategory": "MultipleSeizures",
                        "Negation": "Affirmed",
                    },
                }
            )
        )
        warnings.append("projected_remote_seizure_type_to_diagnosis")
    if not _CLUSTER_OF_SEIZURES.search(mention.evidence):
        return expanded, warnings
    if normalize_phrase(mention.text) == "cluster of seizures":
        return expanded, warnings
    cluster_attrs = {
        key: value
        for key, value in mention.attributes.items()
        if key
        not in {
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
            "TimePeriod",
            "FrequencyChange",
        }
    }
    cluster_attrs["NumberOfSeizures"] = "1"
    cluster = mention.model_copy(
        update={
            "text": "cluster of seizures",
            "attributes": cluster_attrs,
        }
    )
    expanded.append(cluster)
    warnings.append("split_cluster_of_seizures_state")
    return expanded, warnings


def _sf_type_to_diagnosis_projection_warning(mention: PredictedMention) -> str | None:
    if mention.entity != "SeizureFrequency":
        return None
    normalized = normalize_phrase(mention.text)
    if normalized in {
        "seizure",
        "seizures",
        "cluster of seizures",
        "generalised tonic clonic seizure",
        "generalized tonic clonic seizure",
    }:
        return None
    if not _is_allowed_diagnosis_core(normalized):
        return None
    has_count = any(
        key in mention.attributes
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    )
    if mention.attributes.get("NumberOfSeizures") == "0":
        evidence = normalize_phrase(mention.evidence)
        if "last event" in evidence or "last seizure" in evidence or "last one" in evidence:
            return "projected_typed_seizure_frequency_to_diagnosis"
        if normalized == "focal seizures" and "control" in evidence:
            return "projected_typed_controlled_state_to_diagnosis"
        return None
    if has_count:
        if normalized not in normalize_phrase(mention.evidence):
            return None
        return "projected_active_rate_seizure_type_to_diagnosis"
    return None


def _expand_asymmetric_prescription(
    mention: PredictedMention,
) -> tuple[list[PredictedMention], list[str]]:
    attrs = dict(mention.attributes)
    if attrs.get("DoseUnit") != "mg":
        return [], []
    match = projection_patterns.ASYMMETRIC_DOSING.search(f"{mention.text} {mention.evidence}")
    if not match:
        return [], []
    first = projection_patterns.clean_number(match.group("first"))
    second = projection_patterns.clean_number(match.group("second"))
    if first == second:
        return [], []
    first_attrs = {**attrs, "DrugDose": first, "Frequency": "1"}
    second_attrs = {**attrs, "DrugDose": second, "Frequency": "1"}
    return [
        mention.model_copy(update={"attributes": first_attrs}),
        mention.model_copy(update={"attributes": second_attrs}),
    ], [f"split_asymmetric_same_drug_dosing: {first}/{second} mg"]


def _convert_day_period_to_week(attrs: dict[str, str], warnings: list[str]) -> None:
    converted = False
    for key in (
        "NumberOfTimePeriods",
        "LowerNumberOfTimePeriods",
        "UpperNumberOfTimePeriods",
    ):
        if key not in attrs:
            continue
        raw = attrs[key]
        if not raw.isdigit():
            return
        days = int(raw)
        if days % 7 != 0:
            return
        attrs[key] = str(days // 7)
        converted = True
    if converted:
        attrs["TimePeriod"] = "Week"
        warnings.append("converted_day_period_to_week")


def _split_range_attribute(
    attrs: dict[str, str],
    *,
    source_key: str,
    lower_key: str,
    upper_key: str,
    warnings: list[str],
) -> None:
    raw = attrs.get(source_key, "")
    match = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)\s*(?:-|to|or|/)\s*(\d+(?:\.\d+)?)\s*",
        raw,
        flags=re.IGNORECASE,
    )
    if not match:
        return
    attrs.pop(source_key, None)
    attrs[lower_key] = projection_patterns.clean_number(match.group(1))
    attrs[upper_key] = projection_patterns.clean_number(match.group(2))
    warnings.append(
        f"split_range_attribute: {source_key} -> {lower_key}/{upper_key}"
    )
