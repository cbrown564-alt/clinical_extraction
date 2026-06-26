"""Shared draft-row IO for entity verifiers."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.entity_verifier.config import (
    VerifierConfig,
)


def _draft_mention_row(
    mention: Mapping[str, Any],
    *,
    include_entity: bool,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "text": str(mention.get("text", "")),
        "attributes": dict(mention.get("attributes") or {}),
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence", "")),
        "rationale": str(mention.get("rationale", "")),
    }
    if include_entity:
        row["entity"] = str(mention.get("entity", ""))
    return row


def draft_mentions_by_letter(
    rows: Sequence[Mapping[str, Any]],
    config: VerifierConfig,
) -> dict[str, list[dict[str, Any]]]:
    """Filter draft mentions to the configured entity or entity set."""

    entity_names = config.draft_entity_names or (config.entity_name,)
    drafts: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        drafts[str(row["letter_id"])] = [
            _draft_mention_row(m, include_entity=config.include_entity_in_draft)
            for m in row.get("predicted_mentions", [])
            if m.get("entity") in entity_names
        ]
    return drafts


def read_draft_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
