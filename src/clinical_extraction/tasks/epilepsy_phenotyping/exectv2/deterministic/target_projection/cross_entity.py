"""Cross-entity mention projection for target indicators."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    normalize_phrase,
)

from .constants import (
    CONTROLLED_ON_DOSE,
    EVERY_N_TO_M_PERIODS,
    REMOTE_LAST_SEIZURES_IN_TEENS,
    SF_STATE_ATTRIBUTES,
    YEAR_IN_TEXT,
)
from .policy import (
    ProjectionFamilySwitches,
    is_projection_family_enabled,
    quarantined_projection_family_warning,
)
from .shared import local_evidence_context, period_to_canonical
from .types import MentionLike

def project_dropped_sf_to_diagnosis(
    text: str,
    evidence: str,
    mention: MentionLike,
    *,
    component_owner: str,
) -> PredictedMention | None:
    normalized_text = normalize_phrase(text)
    if normalized_text != "general and complex partial seizures":
        return None
    if "continues to get" not in normalize_phrase(evidence):
        return None
    return PredictedMention(
        entity="Diagnosis",
        text="complex partial seizures",
        attributes={
            "Certainty": "5",
            "DiagCategory": "MultipleSeizures",
            "Negation": "Affirmed",
        },
        evidence=evidence,
        confidence=mention.confidence,
        rationale=mention.rationale,
        component_owner=component_owner,
    )

def project_empty_sf_candidate_to_diagnosis(
    mention: MentionLike,
) -> MentionLike | None:
    if any(key in mention.attributes for key in SF_STATE_ATTRIBUTES):
        return None
    source = normalize_phrase(f"{mention.text} {mention.evidence}")
    if "focal onset" not in source:
        return None
    attrs = {str(k): str(v) for k, v in dict(mention.attributes).items()}
    certainty = attrs.get("Certainty", "3")
    return mention.model_copy(
        update={
            "entity": "Diagnosis",
            "text": "focal epilepsy",
            "attributes": {
                "Certainty": certainty,
                "DiagCategory": "Epilepsy",
                "Negation": "Affirmed",
            },
        }
    )

def project_diagnosis_frequency_header_to_sf(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    normalized_text = normalize_phrase(mention.text)
    if normalized_text not in {"absence like seizures", "absence-like seizures"}:
        return None
    year_match = YEAR_IN_TEXT.search(mention.evidence)
    context = normalize_phrase(
        local_evidence_context(note_text, mention.evidence, before=64, after=32)
    )
    if not year_match:
        year_match = re.search(
            r"\babsence\s+like\s+seizures?\s+(?P<year>\d{4})\b",
            context,
            re.IGNORECASE,
        )
    if not year_match:
        return None
    if "seizure type and frequency" not in context:
        return None
    return mention.model_copy(
        update={
            "entity": "SeizureFrequency",
            "text": "absence like seizures",
            "attributes": {
                "NumberOfSeizures": "1",
                "TimeSince_or_TimeOfEvent": "During",
                "YearDate": year_match.group("year"),
            },
        }
    )

def project_focal_diagnosis_context_to_sf(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "Diagnosis":
        return None
    if normalize_phrase(mention.text) != "focal epilepsy":
        return None
    if "focal onset" not in normalize_phrase(mention.evidence):
        return None
    context = local_evidence_context(note_text, mention.evidence, before=96, after=16)
    range_match = re.search(
        r"\bseizures?\s+every\s+(?P<lower>\d+)\s*(?:-|to)\s*(?P<upper>\d+)\s+"
        r"(?P<period>days?|weeks?|months?|years?)\b",
        context,
        re.IGNORECASE,
    )
    if range_match:
        return mention.model_copy(
            update={
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": range_match.group("lower"),
                    "UpperNumberOfTimePeriods": range_match.group("upper"),
                    "TimePeriod": period_to_canonical(range_match.group("period")),
                },
                "evidence": range_match.group(0),
            }
        )
    single_match = re.search(
        r"\bseizures?\s+every\s+(?P<n>\d+)\s+(?P<period>days?|weeks?|months?|years?)\b",
        context,
        re.IGNORECASE,
    )
    if not single_match:
        return None
    return mention.model_copy(
        update={
            "entity": "SeizureFrequency",
            "text": "seizures",
            "attributes": {
                "NumberOfSeizures": "1",
                "NumberOfTimePeriods": single_match.group("n"),
                "TimePeriod": period_to_canonical(single_match.group("period")),
            },
            "evidence": single_match.group(0),
        }
    )

def project_sf_context_to_focal_diagnosis(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "SeizureFrequency":
        return None
    if normalize_phrase(mention.text) not in {"seizure", "seizures"}:
        return None
    if not any(
        key in mention.attributes
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        return None
    context = local_evidence_context(note_text, mention.evidence, before=40, after=80)
    match = re.search(r"\b(?:possibly\s+)?focal\s+onset\b", context, re.IGNORECASE)
    if not match and EVERY_N_TO_M_PERIODS.search(mention.evidence):
        header_match = re.search(
            r"\bseizures?\s+every\s+\d+\s*(?:-|to)\s*\d+\s+"
            r"(?:days?|weeks?|months?|years?)\s*,\s*"
            r"(?P<focal>(?:possibly\s+)?focal\s+onset)\b",
            note_text,
            re.IGNORECASE,
        )
        if header_match:
            match = re.search(
                r"\b(?:possibly\s+)?focal\s+onset\b",
                header_match.group("focal"),
                re.IGNORECASE,
            )
    if not match:
        return None
    certainty = "3" if "possibly" in match.group(0).lower() else "5"
    return mention.model_copy(
        update={
            "entity": "Diagnosis",
            "text": "focal epilepsy",
            "attributes": {
                "Certainty": certainty,
                "DiagCategory": "Epilepsy",
                "Negation": "Affirmed",
            },
            "evidence": match.group(0),
        }
    )

def project_controlled_context_to_infrequent_state(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "SeizureFrequency":
        return None
    if mention.attributes.get("NumberOfSeizures") != "0":
        return None
    context = normalize_phrase(
        local_evidence_context(note_text, mention.evidence, before=16, after=96)
    )
    if not re.search(r"\bunder control\b.+\bon the dose\b", context):
        return None
    return mention.model_copy(
        update={
            "text": "seizures",
            "attributes": {
                "FrequencyChange": "Infrequent",
                "PointInTime": "DrugChange",
            },
        }
    )

def project_returned_context_to_increased_state(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "SeizureFrequency":
        return None
    if normalize_phrase(mention.text) != "focal seizures with altered awareness":
        return None
    context = normalize_phrase(
        local_evidence_context(note_text, mention.evidence, before=48, after=320)
    )
    if "seizures have returned" not in context:
        return None
    return mention.model_copy(
        update={
            "text": "seizure",
            "attributes": {
                "FrequencyChange": "Increased",
            },
        }
    )

def project_infrequent_context_state(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "SeizureFrequency":
        return None
    normalized_text = normalize_phrase(mention.text)
    if normalized_text != "focal to bilateral convulsive seizures":
        return None
    context = normalize_phrase(
        local_evidence_context(note_text, mention.evidence, before=320, after=720)
    )
    if "infrequent focal to bilateral convulsive seizures" not in context:
        return None
    return mention.model_copy(
        update={
            "attributes": {
                "FrequencyChange": "Infrequent",
            },
        }
    )

def project_diagnosis_context_to_sf_states(
    mention: PredictedMention,
    note_text: str,
    *,
    projection_family_switches: ProjectionFamilySwitches | None = None,
) -> tuple[list[PredictedMention], list[str]]:
    if mention.entity != "Diagnosis":
        return [], []
    context = normalize_phrase(
        local_evidence_context(note_text, mention.evidence, before=80, after=900)
    )
    normalized_text = normalize_phrase(mention.text)
    states: list[PredictedMention] = []
    warnings: list[str] = []
    if (
        normalized_text == "focal epilepsy"
        and REMOTE_LAST_SEIZURES_IN_TEENS.search(context)
    ):
        family = "projected_diagnosis_context_to_remote_last_seizures_state"
        if is_projection_family_enabled(family, projection_family_switches):
            states.append(
                mention.model_copy(
                    update={
                        "entity": "SeizureFrequency",
                        "text": "seizures",
                        "attributes": {
                            "NumberOfSeizures": "0",
                            "TimeSince_or_TimeOfEvent": "Since",
                            "AgeLower": "13",
                            "AgeUpper": "19",
                            "AgeUnit": "Year",
                        },
                        "evidence": (
                            remote_last_seizures_evidence(note_text)
                            or mention.evidence
                        ),
                    }
                )
            )
            warnings.append(family)
        else:
            warnings.append(quarantined_projection_family_warning(family))
    if (
        normalized_text == "focal epilepsy"
        and "focal seizures" in context
        and CONTROLLED_ON_DOSE.search(context)
    ):
        family = "projected_diagnosis_context_to_controlled_sf_state"
        if is_projection_family_enabled(family, projection_family_switches):
            evidence = controlled_focal_seizures_evidence(note_text) or mention.evidence
            states.append(
                mention.model_copy(
                    update={
                        "entity": "SeizureFrequency",
                        "text": "focal seizures",
                        "attributes": {
                            "NumberOfSeizures": "0",
                            "PointInTime": "DrugChange",
                        },
                        "evidence": evidence,
                    }
                )
            )
            states.append(
                mention.model_copy(
                    update={
                        "entity": "SeizureFrequency",
                        "text": "seizures",
                        "attributes": {
                            "FrequencyChange": "Infrequent",
                            "PointInTime": "DrugChange",
                        },
                        "evidence": evidence,
                    }
                )
            )
            warnings.append(family)
        else:
            warnings.append(quarantined_projection_family_warning(family))
    if (
        "myoclonic jerks" in normalize_phrase(f"{mention.text} {mention.evidence}")
        and "very frequent myoclonic jerks" in context
    ):
        family = "projected_diagnosis_context_to_frequent_myoclonic_jerks"
        if is_projection_family_enabled(family, projection_family_switches):
            states.append(
                mention.model_copy(
                    update={
                        "entity": "SeizureFrequency",
                        "text": "myoclonic jerks",
                        "attributes": {
                            "FrequencyChange": "Frequent",
                        },
                        "evidence": frequent_myoclonic_jerks_evidence(note_text)
                        or "very frequent myoclonic jerks",
                    }
                )
            )
            warnings.append(family)
        else:
            warnings.append(quarantined_projection_family_warning(family))
    return states, list(dict.fromkeys(warnings))

def remote_last_seizures_evidence(note_text: str) -> str | None:
    match = re.search(
        r"\bHis\s+last\s+seizures\s+were\s+in\s+his\s+teenage\s+years\b",
        note_text,
        re.IGNORECASE,
    )
    return match.group(0) if match else None

def controlled_focal_seizures_evidence(note_text: str) -> str | None:
    match = re.search(
        r"\bfocal\s+seizures\s+are\s+completely\s+under\s+control\s+on\s+the\s+dose\b",
        note_text,
        re.IGNORECASE,
    )
    return match.group(0) if match else None

def frequent_myoclonic_jerks_evidence(note_text: str) -> str | None:
    match = re.search(
        r"\bvery\s+frequent\s+myoclonic\s+jerks\b",
        note_text,
        re.IGNORECASE,
    )
    return match.group(0) if match else None

def project_context_parent_epilepsy(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "Diagnosis":
        return None
    if normalize_phrase(mention.text) == "epilepsy":
        return None
    context = local_evidence_context(note_text, mention.evidence, before=160, after=8)
    match = re.search(r"\bwith\s+epilepsy\b", context, re.IGNORECASE)
    if not match:
        return None
    return mention.model_copy(
        update={
            "text": "epilepsy",
            "attributes": {
                "Certainty": "5",
                "DiagCategory": "Epilepsy",
                "Negation": "Affirmed",
            },
            "evidence": match.group(0),
        }
    )

def project_diagnosis_header_parent_epilepsy(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "Diagnosis":
        return None
    if normalize_phrase(mention.text) == "epilepsy":
        return None
    context = local_evidence_context(note_text, mention.evidence, before=48, after=24)
    if not re.search(r"\bDiagnosis:\s*epilepsy\b", context, re.IGNORECASE):
        return None
    if not re.search(
        r"\b(?:unclassified|probable\s+focal|possibly\s+generalised|"
        r"possibly\s+generalized)\b",
        context,
        re.IGNORECASE,
    ):
        return None
    epilepsy_match = re.search(r"\b[Ee]pilepsy\b", context)
    evidence = epilepsy_match.group(0) if epilepsy_match else mention.evidence
    return mention.model_copy(
        update={
            "text": "epilepsy",
            "attributes": {
                "Certainty": "5",
                "DiagCategory": "Epilepsy",
                "Negation": "Affirmed",
            },
            "evidence": evidence,
        }
    )

def project_dated_diagnosis_context_to_sf(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "Diagnosis":
        return None
    if normalize_phrase(mention.text) != "tonic clonic seizures":
        return None
    context = local_evidence_context(note_text, mention.evidence, before=24, after=24)
    match = re.search(
        r"\b(?P<count>\d+)\s+generalised\s+tonic\s+clonic\s+seizures\s+"
        r"(?P<year>\d{4})\b",
        context,
        re.IGNORECASE,
    )
    if not match:
        return None
    return mention.model_copy(
        update={
            "entity": "SeizureFrequency",
            "text": "generalised tonic clonic seizures",
            "attributes": {
                "NumberOfSeizures": match.group("count"),
                "TimeSince_or_TimeOfEvent": "During",
                "YearDate": match.group("year"),
            },
            "evidence": match.group(0),
        }
    )
