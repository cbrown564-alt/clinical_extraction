"""Deterministic mention repair utilities for ExECTv2 (schema + evidence gates)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.evidence import (
    evidence_is_substring,
    repair_evidence_text_if_source_exact,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import EntitySpec
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    canonicalize_attribute_value,
)


class MentionRecord(BaseModel):
    """One entity mention emitted by an LLM extraction call."""

    model_config = ConfigDict(extra="ignore")

    text: str
    attributes: dict[str, Any] = {}
    evidence: str
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class ExtractionRecord(BaseModel):
    """Full LLM output for one letter."""

    model_config = ConfigDict(extra="ignore")

    mentions: list[MentionRecord] = []


def repair_attributes(
    attrs: dict[str, str],
    *,
    spec: EntitySpec,
) -> tuple[dict[str, str], list[str]]:
    """Strip illegal attribute keys and illegal closed-vocab values.

    Semantically-neutral: the LLM clinical fact is never altered, only
    schema-invalid keys are dropped. Both actions are logged.
    """
    repaired: dict[str, str] = {}
    warnings: list[str] = []
    for key, value in attrs.items():
        if key in spec.noise_attributes:
            continue
        if key not in spec.legal_attributes:
            warnings.append(f"dropped_illegal_attribute: {key!r}")
            continue
        normalized_value = canonicalize_attribute_value(key, value)
        if normalized_value != value:
            warnings.append(
                f"normalized_attribute_value: {key!r}={value!r} -> {normalized_value!r}"
            )
        if key in spec.closed_vocab and normalized_value not in spec.closed_vocab[key]:
            warnings.append(
                f"dropped_illegal_value: {key!r}={normalized_value!r} not in "
                f"{sorted(spec.closed_vocab[key])}"
            )
            continue
        repaired[key] = normalized_value
    return repaired, warnings


def check_evidence(
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[list[MentionRecord], list[MentionRecord], list[str]]:
    """Partition mentions into (evidence_valid, evidence_invalid).

    Per policy: mentions whose evidence is not an exact substring of the note
    are dropped from the scored set and logged. They are never silently kept.
    """
    valid: list[MentionRecord] = []
    invalid: list[MentionRecord] = []
    warnings: list[str] = []
    for mention in mentions:
        repaired_evidence = repair_evidence_text_if_source_exact(mention.evidence, note_text)
        if repaired_evidence and evidence_is_substring(note_text, repaired_evidence):
            if repaired_evidence != mention.evidence:
                warnings.append(f"repaired_evidence_exact_copy: text={mention.text!r}")
                mention = mention.model_copy(update={"evidence": repaired_evidence})
            valid.append(mention)
            continue
        invalid.append(mention)
        reason = "empty_evidence" if not mention.evidence else "evidence_not_substring"
        warnings.append(f"dropped_{reason}: text={mention.text!r}")
    return valid, invalid, warnings
