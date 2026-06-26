"""Pydantic record models for generation-selection responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)


class StructuredGenerationSelectionRecord(BaseModel):
    """Model-emitted inventory and final selection in one response."""

    model_config = ConfigDict(extra="ignore")

    generated_events: list[structured.StructuredClinicalEvent] = []
    final_events: list[structured.StructuredClinicalEvent] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredMentionSelectionRecord(BaseModel):
    """Model-emitted mention inventory and final mention selection."""

    model_config = ConfigDict(extra="ignore")

    generated_mentions: list[structured.MentionForEvidence] = []
    final_mentions: list[structured.MentionForEvidence] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredMentionIdSelectionRecord(BaseModel):
    """Model-emitted generated mentions plus model-selected mention IDs."""

    model_config = ConfigDict(extra="ignore")

    generated_mentions: list[dict[str, Any]] = []
    final_mention_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredPoolAdjudicationRecord(BaseModel):
    """Model-selected final mention IDs over prior Qwen-generated mentions."""

    model_config = ConfigDict(extra="ignore")

    final_mention_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []


class StructuredPoolGroupAdjudicationRecord(BaseModel):
    """Model-emitted duplicate groups plus representative selected IDs."""

    model_config = ConfigDict(extra="ignore")

    fact_groups: list[dict[str, Any]] = []
    final_mention_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []


class DedupClinicalFactRecord(BaseModel):
    """Simplified model-emitted de-duplicated clinical fact."""

    model_config = ConfigDict(extra="ignore")

    family: str
    evidence: str
    concept: str = ""
    negation: str = ""
    seizure_type: str = ""
    state: str = ""
    drug: str = ""
    dose: str = ""
    dose_unit: str = ""
    frequency: str = ""
    modality: str = ""
    performed: str = ""
    result: str = ""
    source_text: str = ""
    attributes: dict[str, str] = {}


class DedupClinicalFactsRecord(BaseModel):
    """Model-emitted de-duplicated clinical-fact inventory."""

    model_config = ConfigDict(extra="ignore")

    clinical_facts: list[DedupClinicalFactRecord] = []
