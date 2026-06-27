"""Cross-modality investigation projection for target indicators."""

from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

from .shared import local_evidence_context


def project_eeg_context_to_mri_normal(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "Investigations":
        return None
    if normalize_phrase(mention.text) != "eeg":
        return None
    context = local_evidence_context(note_text, mention.evidence, before=96, after=8)
    match = re.search(
        r"\b(?:previous\s+)?MRI\s+has\s+been\s+normal\b",
        context,
        re.IGNORECASE,
    )
    if not match:
        return None
    return mention.model_copy(
        update={
            "text": "MRI",
            "attributes": {
                "MRI_Performed": "Yes",
                "MRI_Results": "Normal",
            },
            "evidence": match.group(0),
        }
    )


def project_mri_context_to_eeg_result(
    mention: PredictedMention,
    note_text: str,
) -> PredictedMention | None:
    if mention.entity != "Investigations":
        return None
    if normalize_phrase(mention.text) != "mri":
        return None
    context = local_evidence_context(note_text, mention.evidence, before=8, after=128)
    match = re.search(
        r"\b(?:An\s+)?EEG\s+(?:in\s+\d{4}\s+)?"
        r"(?:(?:did\s+show|showed|demonstrated)\s+[^.\\n]*|(?:was\s+)?normal)\b",
        context,
        re.IGNORECASE,
    )
    if not match:
        return None
    evidence = match.group(0)
    result = "Normal" if "normal" in normalize_phrase(evidence) else "Abnormal"
    return mention.model_copy(
        update={
            "text": "EEG",
            "attributes": {
                "EEG_Performed": "Yes",
                "EEG_Results": result,
            },
            "evidence": evidence,
        }
    )
