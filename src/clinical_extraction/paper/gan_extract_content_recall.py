"""Extract content recall: answer anywhere in the ledger, or gold-reference evidence.

Stage-1 companion to provisional-answer and decide-stop Purist scores. A letter
hits when any extract event (or the provisional final label) is Purist-correct,
or when the annotation gold reference overlaps any collected evidence span.
All events count, not only the selected ones. Zero model calls; holdout stays
aggregate-only.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.gan_cell_replay import (
    gan_living_extract_rows_path,
    score_label,
)
from clinical_extraction.paper.gan_paired_contrasts import (
    codebook_select_correct,
    row_comparison_correct,
)
from clinical_extraction.paper.methods import (
    gan_machine_split,
    gan_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredExtractionRecord,
    StructuredRepairConfig,
    _normalize_event,
    parse_structured_json,
)

ROOT = discover_repo_root(start=Path(__file__))
PROTOCOL = (
    "docs/research/gan2026/gan_candidate_set_recall_test450_protocol_2026-09-03.md"
)
CITED_SLUG = "gemini37flash"
CITED_CELL3_TEST450 = 387
CITED_CELL5_TEST450 = 383
DEFAULT_ARTIFACT = (
    ROOT / "docs/research/gan2026/gan_extract_content_recall_2026-09-03.json"
)
CELL5_SCORED_TEST450 = (
    ROOT
    / "scratch/holdout/paper/gan_llm_select_from_extract"
    / CITED_SLUG
    / "gan_llm_extract"
    / "test450"
    / "rows.jsonl"
)


def fold_surface(text: str | None) -> str:
    """Casefold and normalize light surface variants for reference overlap."""

    if not text:
        return ""
    cleaned = unicodedata.normalize("NFKC", text).casefold()
    cleaned = cleaned.replace("≤", "<=").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", cleaned).strip()


def surfaces_overlap(left: str | None, right: str | None, *, min_len: int = 5) -> bool:
    """True when either folded surface contains the other."""

    folded_left = fold_surface(left)
    folded_right = fold_surface(right)
    if len(folded_left) < min_len or len(folded_right) < min_len:
        return bool(folded_left) and folded_left == folded_right
    return folded_left in folded_right or folded_right in folded_left


def answer_hit(
    record: GanFrequencyRecord,
    extraction: StructuredExtractionRecord,
) -> bool:
    """True when any provisional or event label is Purist-correct vs gold."""

    if score_label(record, extraction.selection.final_label)["purist_correct"]:
        return True
    for event in extraction.events:
        normalized = _normalize_event(event, note_text=record.note_text)
        label = normalized.normalized_label
        if label and score_label(record, label)["purist_correct"]:
            return True
    return False


def evidence_hit(
    record: GanFrequencyRecord,
    extraction: StructuredExtractionRecord,
) -> bool:
    """True when gold_reference overlaps any collected evidence span."""

    gold_reference = record.gold_reference or ""
    if surfaces_overlap(extraction.selection.evidence, gold_reference):
        return True
    return any(
        surfaces_overlap(event.evidence, gold_reference) for event in extraction.events
    )


def content_hits(
    record: GanFrequencyRecord,
    extraction: StructuredExtractionRecord,
) -> dict[str, bool]:
    """Return answer, evidence, and either flags for one extract record."""

    answer = answer_hit(record, extraction)
    evidence = evidence_hit(record, extraction)
    return {
        "answer": answer,
        "evidence": evidence,
        "either": answer or evidence,
    }


def _rate(correct: int, n: int) -> dict[str, float | int]:
    return {"correct": correct, "accuracy": round(correct / n, 4)}


def measure_extract_content_recall(
    split: str,
    *,
    slug: str = CITED_SLUG,
    rows_path: Path | None = None,
    cell5_rows_path: Path | None = None,
) -> dict[str, Any]:
    """Replay saved extract raws; return aggregate-only content-recall counts."""

    if split not in {"dev750", "test450"}:
        raise ValueError("split must be dev750 or test450")
    holdout = holdout_is_aggregate_only(split)
    expected_n = gan_row_count(split)
    extract_path = rows_path or gan_living_extract_rows_path(slug, split)
    if not extract_path.is_file():
        raise FileNotFoundError(f"missing extract replay: {extract_path}")

    records = {
        record.source_row_index: record
        for record in load_records_for_split(gan_machine_split(split))
    }
    if len(records) != expected_n:
        raise RuntimeError(f"expected {expected_n} records for {split}")
    raw_rows = {
        int(row["source_row_index"]): str(row["raw_output"])
        for row in load_jsonl_rows(extract_path)
    }
    if len(raw_rows) != expected_n:
        raise RuntimeError(f"expected {expected_n} extract rows for {split}")

    cell3 = codebook_select_correct(extract_path, records)
    cell5: dict[int, bool] | None = None
    if split == "test450":
        cell5_path = cell5_rows_path or CELL5_SCORED_TEST450
        cell5 = row_comparison_correct(cell5_path)
        if sum(cell3.values()) != CITED_CELL3_TEST450:
            raise RuntimeError(
                f"cell3 gate failed: {sum(cell3.values())} != {CITED_CELL3_TEST450}"
            )
        if sum(cell5.values()) != CITED_CELL5_TEST450:
            raise RuntimeError(
                f"cell5 gate failed: {sum(cell5.values())} != {CITED_CELL5_TEST450}"
            )

    answer = 0
    evidence = 0
    either = 0
    both = 0
    parse_failures = 0
    cell3_ok_extract_miss = 0
    cell5_ok_extract_miss = 0
    for index, raw_output in sorted(raw_rows.items()):
        record = records[index]
        extraction, _, _ = parse_structured_json(
            raw_output,
            note_text=record.note_text,
            repair_config=StructuredRepairConfig.for_mode("raw_model"),
        )
        if extraction is None:
            parse_failures += 1
            continue
        hits = content_hits(record, extraction)
        answer += int(hits["answer"])
        evidence += int(hits["evidence"])
        either += int(hits["either"])
        both += int(hits["answer"] and hits["evidence"])
        if cell3[index] and not hits["either"]:
            cell3_ok_extract_miss += 1
        if cell5 is not None and cell5[index] and not hits["either"]:
            cell5_ok_extract_miss += 1

    if parse_failures:
        raise RuntimeError(f"extract parse failures: {parse_failures}")

    payload: dict[str, Any] = {
        "schema_version": "gan.extract_content_recall.v1",
        "date": datetime.now(UTC).date().isoformat(),
        "protocol": PROTOCOL,
        "split": split,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "holdout_loaded": holdout,
        "model_slug": slug,
        "model_calls": 0,
        "n": expected_n,
        "definition": {
            "answer": (
                "provisional final_label or any event after _normalize_event is "
                "Purist-correct vs gold; all events count"
            ),
            "evidence": (
                "gold_reference overlaps selection evidence or any event evidence "
                "(folded either-contains)"
            ),
            "either": "answer or evidence",
        },
        "extract_source": str(extract_path.relative_to(ROOT)),
        "pools": {
            "answer": _rate(answer, expected_n),
            "evidence": _rate(evidence, expected_n),
            "answer_or_evidence": _rate(either, expected_n),
            "both": both,
        },
        "decide_stops_purist": {
            "cell3_hybrid": _rate(sum(cell3.values()), expected_n),
        },
        "decide_correct_but_extract_miss": {
            "cell3_hybrid": cell3_ok_extract_miss,
        },
        "claim_boundary": (
            "Stage-1 extract content recall on the shared Gemini gan_llm_extract "
            "record. Aggregate-only on test450. Not a new Table 1 score."
        ),
    }
    if cell5 is not None:
        payload["cell5_source"] = str(
            (cell5_rows_path or CELL5_SCORED_TEST450).relative_to(ROOT)
        )
        payload["decide_stops_purist"]["cell5_llm_only"] = _rate(
            sum(cell5.values()), expected_n
        )
        payload["decide_correct_but_extract_miss"]["cell5_llm_only"] = (
            cell5_ok_extract_miss
        )
        payload["gates"] = {
            "cell3_select_reproduces_cited": CITED_CELL3_TEST450,
            "cell5_select_reproduces_cited": CITED_CELL5_TEST450,
            "extract_parse_failures": parse_failures,
        }
    return payload


def write_extract_content_recall_artifact(
    payload: Mapping[str, Any],
    path: Path | None = None,
) -> Path:
    """Write the aggregate JSON artifact (no row identifiers)."""

    out = path or DEFAULT_ARTIFACT
    out.parent.mkdir(parents=True, exist_ok=True)
    if "source_row_index" in json.dumps(payload):
        raise RuntimeError("refusing to write row identifiers into public artifact")
    out.write_text(
        json.dumps(dict(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def measure_and_write(
    splits: Sequence[str] = ("dev750", "test450"),
    *,
    path: Path | None = None,
) -> Path:
    """Measure one or more splits and write a combined aggregate artifact."""

    by_split = {split: measure_extract_content_recall(split) for split in splits}
    combined = {
        "schema_version": "gan.extract_content_recall.combined.v1",
        "date": datetime.now(UTC).date().isoformat(),
        "protocol": PROTOCOL,
        "model_slug": CITED_SLUG,
        "model_calls": 0,
        "splits": by_split,
        "claim_boundary": (
            "Combined extract content-recall aggregates. Holdout split is "
            "aggregate-only. Not a new Table 1 score."
        ),
    }
    return write_extract_content_recall_artifact(combined, path)
