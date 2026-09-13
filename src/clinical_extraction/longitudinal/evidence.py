"""Source loading and exact-offset repair. Clinical fields are never rewritten here."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

Record = dict[str, Any]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_evidence(spans: list[Record]) -> list[Record]:
    return list({(e["letter_id"], e["start"], e["end"]): e for e in spans}.values())


def grounded(span: Record, documents: Record) -> bool:
    doc = documents.get(span.get("letter_id", ""))
    return bool(
        doc
        and isinstance(span.get("start"), int)
        and isinstance(span.get("end"), int)
        and 0 <= span["start"] < span["end"] <= len(doc["text"])
        and doc["text"][span["start"] : span["end"]] == span.get("text")
    )


def overlap(a: Record, b: Record) -> bool:
    return a["letter_id"] == b["letter_id"] and max(a["start"], b["start"]) < min(
        a["end"], b["end"]
    )


def wording(record: Record) -> str:
    return " ".join(e["text"] for e in record["evidence"]).casefold()


def normalize_evidence(raw: Record, documents: Record) -> tuple[Record, list[Record]]:
    """Repair a unique exact quotation's offsets; reject missing/ambiguous quotations."""
    output, changes = deepcopy(raw), []

    def visit(value: Any, path: str) -> None:
        if isinstance(value, list):
            for i, item in enumerate(value):
                visit(item, f"{path}/{i}")
        elif isinstance(value, dict):
            if {"letter_id", "start", "end", "text"} <= value.keys():
                if grounded(value, documents):
                    return
                text = documents.get(value["letter_id"], {}).get("text", "")
                quote = value["text"]
                if not isinstance(quote, str) or not quote or text.count(quote) != 1:
                    raise ValueError(f"Ungrounded or ambiguous evidence at {path}")
                start = text.index(quote)
                changes.append({"path": path, "before": deepcopy(value), "rule": "exact-offset"})
                value.update(start=start, end=start + len(quote))
                changes[-1]["after"] = deepcopy(value)
            else:
                for key, child in value.items():
                    visit(child, f"{path}/{key}")

    visit(output, "")
    for a in output["assertions"]:
        if not a.get("evidence") or a["letter_id"] not in documents:
            raise ValueError("Missing assertion evidence or unavailable source")
    return output, changes


def load_case(path: Path) -> tuple[Record, Record, Record]:
    manifest = json.loads((path / "manifest.json").read_text())
    documents = {}
    for doc in manifest["documents"]:
        source = path / doc["path"]
        if digest(source) != doc["sha256"]:
            raise ValueError(f"Source hash mismatch: {source}")
        documents[doc["letter_id"]] = {**doc, "text": source.read_text()}
    annotations = json.loads((path / "annotations.json").read_text())
    normalized, changes = normalize_evidence(annotations, documents)
    if changes:
        raise ValueError("Reference offsets must already be exact")
    return manifest, documents, normalized


def source_paragraphs(record: Record, documents: Record) -> list[Record]:
    """Select surrounding source context for link evidence; do not alter extraction."""
    spans = []
    for evidence in record["evidence"]:
        text = documents[evidence["letter_id"]]["text"]
        boundary = text.rfind("\n\n", 0, evidence["start"])
        start = boundary + 2 if boundary >= 0 else 0
        end = text.find("\n\n", evidence["end"])
        end = len(text) if end < 0 else end
        spans.append(
            {
                "letter_id": evidence["letter_id"],
                "start": start,
                "end": end,
                "text": text[start:end],
            }
        )
    return unique_evidence(spans)
