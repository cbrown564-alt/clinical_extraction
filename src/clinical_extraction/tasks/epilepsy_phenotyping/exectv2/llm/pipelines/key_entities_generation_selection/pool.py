"""Loading prior model-generated mention pools from saved JSONL artifacts."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)


def load_model_generated_mention_pool(
    jsonl_paths: Sequence[Path],
    *,
    include_event_surfaces: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Load raw Qwen-generated mention surfaces from prior llm_only JSONL artifacts."""

    pool_by_letter: dict[str, list[dict[str, Any]]] = {}
    for source_index, path in enumerate(jsonl_paths, start=1):
        source_run = path.stem
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    continue
                letter_id = str(row.get("letter_id") or "").strip()
                if not letter_id:
                    continue
                pool_by_letter.setdefault(letter_id, []).extend(
                    model_generated_mentions_from_row(
                        row,
                        source_run=source_run,
                        source_slot=f"s{source_index}",
                        source_row=line_number,
                        include_event_surfaces=include_event_surfaces,
                    )
                )
    return pool_by_letter


def model_generated_mentions_from_row(
    row: Mapping[str, Any],
    *,
    source_run: str,
    source_slot: str | None = None,
    source_row: int | None = None,
    include_event_surfaces: bool = True,
) -> list[dict[str, Any]]:
    """Extract only Qwen-emitted mention surfaces from one saved route row."""

    mentions: list[dict[str, Any]] = []
    for surface in ("structured_mentions_generation", "structured_mentions_final"):
        raw_mentions = row.get(surface) or []
        if not isinstance(raw_mentions, list):
            continue
        for raw_mention in raw_mentions:
            if not isinstance(raw_mention, Mapping):
                continue
            mentions.append(
                _pool_mention_from_mapping(
                    raw_mention,
                    source_run=source_run,
                    source_slot=source_slot,
                    source_surface=surface,
                    source_row=source_row,
                    pool_index=len(mentions) + 1,
                )
            )

    if include_event_surfaces:
        for surface in ("structured_events_generation", "structured_events_final"):
            raw_events = row.get(surface) or []
            if not isinstance(raw_events, list):
                continue
            try:
                record = structured.StructuredExtractionRecord.model_validate(
                    {"clinical_events": raw_events}
                )
            except Exception:
                continue
            for mention in structured.flatten_events(record):
                mentions.append(
                    _pool_mention_from_mapping(
                        mention.model_dump(),
                        source_run=source_run,
                        source_slot=source_slot,
                        source_surface=surface,
                        source_row=source_row,
                        pool_index=len(mentions) + 1,
                    )
                )
    return mentions


def _pool_mention_from_mapping(
    mention: Mapping[str, Any],
    *,
    source_run: str,
    source_slot: str | None,
    source_surface: str,
    source_row: int | None,
    pool_index: int,
) -> dict[str, Any]:
    source_slug = _safe_id_piece(source_slot or source_run)
    surface_slug = _surface_id_piece(source_surface)
    raw_id = str(mention.get("mention_id") or "").strip()
    mention_id = f"{source_slug}_{surface_slug}_{pool_index}"
    attributes = mention.get("attributes") or {}
    if not isinstance(attributes, Mapping):
        attributes = {}
    return {
        "mention_id": mention_id,
        "source_run": source_run,
        "source_surface": source_surface,
        "source_row": source_row,
        "original_mention_id": raw_id,
        "entity": str(mention.get("entity") or ""),
        "text": str(mention.get("text") or mention.get("source_text") or ""),
        "attributes": {
            str(key): str(value)
            for key, value in attributes.items()
            if value is not None and str(key) not in {"CUI", "CUIPhrase"}
        },
        "evidence": str(mention.get("evidence") or ""),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale") or ""),
    }


def _safe_id_piece(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value)
    return cleaned.strip("_") or "source"


def _surface_id_piece(value: str) -> str:
    if value == "structured_mentions_generation":
        return "mg"
    if value == "structured_mentions_final":
        return "mf"
    if value == "structured_events_generation":
        return "eg"
    if value == "structured_events_final":
        return "ef"
    return _safe_id_piece(value)
