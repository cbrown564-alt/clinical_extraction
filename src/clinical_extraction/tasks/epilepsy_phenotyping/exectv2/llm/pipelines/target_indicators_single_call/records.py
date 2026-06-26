"""Pydantic record model for the target-indicators single-call extraction.

Pure relocation from ``llm_target_indicators_single_call``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)


class ExtractionRecord(BaseModel):
    """Four-target extraction output."""

    model_config = ConfigDict(extra="ignore")

    mentions: list[MentionRecord] = []
