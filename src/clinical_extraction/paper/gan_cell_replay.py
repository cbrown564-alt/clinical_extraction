"""Replay Gan rungs 1-4 from saved hybrid raw_output. No new model calls."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.answer_states import graph_from_hops, unused_model_events
from clinical_extraction.paper.cells import GAN_REPAIR_MODE_FOR_RUNG, RUNG_IDS
from clinical_extraction.paper.comparison_contract import gan_stage
from clinical_extraction.paper.methods import (
    gan_machine_split,
    gan_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.three_stage import (
    phase_c_candidate_config,
    run_record_three_stage,
)

ROOT = discover_repo_root(start=Path(__file__))


def gan_living_extract_rows_path(slug: str, split: str) -> Path:
    """Return the living codebook extract replay file."""

    holdout = holdout_is_aggregate_only(split)
    roots = (
        ROOT / "paper_experiments/gan/gan_llm_extract" / slug / split / "rows.jsonl",
        (
            ROOT
            / ("scratch/holdout/paper" if holdout else "experiments/paper")
            / "gan_llm_extract"
            / slug
            / split
            / "rows.jsonl"
        ),
    )
    for path in roots:
        if path.is_file():
            return path
    return roots[0]


def gan_source_near_rows_path(slug: str, split: str) -> Path:
    """Return the source-near ablation replay file."""

    return (
        ROOT
        / "paper_experiments/gan/gan_llm_extract_raw"
        / slug
        / split
        / "rows.jsonl"
    )


def gan_hybrid_rows_path(slug: str, split: str) -> Path:
    """Return the living codebook extract, falling back to source-near."""

    living = gan_living_extract_rows_path(slug, split)
    if living.is_file():
        return living
    return gan_source_near_rows_path(slug, split)


def living_gan_stages(
    rows: Sequence[Mapping[str, Any]],
    records: Mapping[int, GanFrequencyRecord],
    *,
    method: str,
) -> dict[str, dict[str, Any]]:
    """Score extract / encode / select on saved Gan rows without new calls."""

    n = len(rows)
    select_correct = sum(
        1 for row in rows if (row.get("comparison") or {}).get("purist_correct")
    )
    select_prag = sum(
        1 for row in rows if (row.get("comparison") or {}).get("pragmatic_correct")
    )
    select = gan_stage(
        purist_correct=select_correct,
        n=n,
        pragmatic_correct=select_prag,
    )
    if method in {
        "gan_llm_only",
        "gan_llm_encode",
        "gan_llm_select",
        "gan_llm_select_from_extract",
    }:
        return {"extract": dict(select), "encode": dict(select), "select": dict(select)}
    extract_correct = 0
    encode_correct = 0
    extract_prag = 0
    encode_prag = 0
    for row in rows:
        record = records[int(row["source_row_index"])]
        raw = str(row.get("raw_output") or "")
        for mode, bucket in (("raw_model", "extract"), ("llm_encode", "encode")):
            extraction, _, _, _ = parse_structured_json_with_trace(
                raw,
                note_text=record.note_text,
                repair_config=StructuredRepairConfig.for_mode(mode),
            )
            label = extraction.selection.final_label if extraction else None
            scored = score_label(record, label)
            if bucket == "extract":
                extract_correct += int(scored["purist_correct"])
                extract_prag += int(scored["pragmatic_correct"])
            else:
                encode_correct += int(scored["purist_correct"])
                encode_prag += int(scored["pragmatic_correct"])
    return {
        "extract": gan_stage(
            purist_correct=extract_correct, n=n, pragmatic_correct=extract_prag
        ),
        "encode": gan_stage(
            purist_correct=encode_correct, n=n, pragmatic_correct=encode_prag
        ),
        "select": select,
    }


def gan_rung_out_dir(slug: str, split: str) -> Path:
    """Return the rung-replay directory for one model and split."""

    return ROOT / "paper_experiments/gan/rungs" / slug / split


def score_label(record: GanFrequencyRecord, label: str | None) -> dict[str, Any]:
    """Score one submitted Gan label against gold."""

    if not label:
        return {
            "predicted_label": None,
            "scorable": False,
            "purist_correct": False,
            "pragmatic_correct": False,
        }
    try:
        predicted = label_to_frequency_record(label)
    except ValueError:
        return {
            "predicted_label": label,
            "scorable": False,
            "purist_correct": False,
            "pragmatic_correct": False,
        }
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted.monthly_frequency))
    return {
        "predicted_label": predicted.normalized_label,
        "scorable": True,
        "predicted_kind": str(predicted.kind.value),
        "purist_correct": predicted_purist == gold_purist,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


def write_gan_rung_artifacts(
    out_dir: Path,
    summary: Mapping[str, Any],
    *,
    scored: Sequence[Mapping[str, Any]],
    hops: Sequence[Mapping[str, Any]],
    holdout: bool,
) -> Path:
    """Write replay artifacts. Holdout keeps comparison.json only."""

    out_dir.mkdir(parents=True, exist_ok=True)
    comparison = out_dir / "comparison.json"
    comparison.write_text(
        json.dumps(dict(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    scored_path = out_dir / "scored.jsonl"
    hops_path = out_dir / "hops.jsonl"
    if holdout:
        scored_path.unlink(missing_ok=True)
        hops_path.unlink(missing_ok=True)
        return comparison
    write_jsonl_rows(list(scored), scored_path)
    write_jsonl_rows(list(hops), hops_path)
    return comparison


def replay_gan_rungs(
    split: str,
    *,
    slug: str = "grok46",
    source: str = "living",
    rows_path: Path | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Replay saved extract raw_output through rungs 1-4. No new model calls."""

    if split not in {"dev750", "test450"}:
        raise ValueError("Gan rung replay accepts split dev750 or test450")
    if source not in {"living", "ablation"}:
        raise ValueError("Gan replay source must be living or ablation")
    holdout = holdout_is_aggregate_only(split)
    expected_n = gan_row_count(split)
    raw_path = rows_path or (
        gan_source_near_rows_path(slug, split)
        if source == "ablation"
        else gan_living_extract_rows_path(slug, split)
    )
    if not raw_path.is_file():
        raise FileNotFoundError(
            f"missing gan extract replay file for {slug} {split}: {raw_path}"
        )
    records = {
        record.source_row_index: record
        for record in load_records_for_split(gan_machine_split(split))
    }
    raw_rows = {
        int(row["source_row_index"]): str(row["raw_output"])
        for row in load_jsonl_rows(raw_path)
    }
    if len(raw_rows) != expected_n:
        raise RuntimeError(
            f"expected {expected_n} hybrid raw rows for {split}, found {len(raw_rows)}"
        )
    rules_config = phase_c_candidate_config()
    scored: list[dict[str, Any]] = []
    hops_rows: list[dict[str, Any]] = []
    event_id_changes = 0
    kind_changes = 0
    format_rescues = 0
    format_harms = 0
    for source_row_index, raw_output in sorted(raw_rows.items()):
        record = records[source_row_index]
        rules_result = run_record_three_stage(record, rules_config)
        rules_scored = score_label(record, rules_result.stops.select_label)
        competing = [
            entry for entry in rules_result.ledger if entry.drop_reason is None
        ]
        rules_scored["predicted_candidate_count"] = len(competing)
        rules_scored["predicted_candidate_count_by_stage"] = {
            "extract": len(rules_result.ledger),
            "encode": len(competing),
            "select": len(competing),
        }
        by_rung: dict[str, dict[str, Any]] = {
            "rules_only": rules_scored
        }
        schema_ids: list[str] = []
        schema_kind: str | None = None
        full_hops: list[dict[str, Any]] = []
        unused: list[dict[str, Any]] = []
        for rung, mode in GAN_REPAIR_MODE_FOR_RUNG.items():
            if rung == "llm_pre_post":
                continue
            extraction, _, _, trace = parse_structured_json_with_trace(
                raw_output,
                note_text=record.note_text,
                repair_config=StructuredRepairConfig.for_mode(mode),
            )
            label = extraction.selection.final_label if extraction else None
            scored_rung = score_label(record, label)
            selected_ids = (
                list(extraction.selection.selected_event_ids) if extraction else []
            )
            scored_rung["selected_event_ids"] = selected_ids
            scored_rung["predicted_candidate_count"] = (
                len(extraction.events) if extraction else 0
            )
            by_rung[rung] = scored_rung
            if rung == "llm_extract":
                schema_ids = selected_ids
                schema_kind = scored_rung.get("predicted_kind")
            if rung == "llm_encode":
                if selected_ids != schema_ids:
                    event_id_changes += 1
                if scored_rung.get("predicted_kind") != schema_kind:
                    kind_changes += 1
                schema_ok = by_rung["llm_extract"]["purist_correct"]
                format_ok = scored_rung["purist_correct"]
                if format_ok and not schema_ok:
                    format_rescues += 1
                if schema_ok and not format_ok:
                    format_harms += 1
            if rung == "llm_select" and not holdout:
                full_hops = list(trace.get("answer_states") or [])
                events = (
                    [event.model_dump() for event in extraction.events]
                    if extraction
                    else []
                )
                unused = unused_model_events(events, selected_ids)
        scored.append(
            {
                "source_row_index": source_row_index,
                "gold_label": record.gold_label,
                "rungs": by_rung,
            }
        )
        if not holdout:
            hops_rows.append(
                {
                    "source_row_index": source_row_index,
                    "answer_states": full_hops,
                    "graph": graph_from_hops(full_hops, unused),
                }
            )
    summary = _comparison_summary(
        scored,
        slug=slug,
        split=split,
        holdout=holdout,
        event_id_changes=event_id_changes,
        kind_changes=kind_changes,
        format_rescues=format_rescues,
        format_harms=format_harms,
        shared_raw_output=(
            "gan_llm_extract_raw" if source == "ablation" else "gan_llm_extract"
        ),
    )
    write_gan_rung_artifacts(
        out_dir or gan_rung_out_dir(slug, split),
        summary,
        scored=scored,
        hops=hops_rows,
        holdout=holdout,
    )
    return summary


def replay_gan_dev750(*, slug: str = "grok46") -> dict[str, Any]:
    """Replay hybrid raw_output through rungs 1-4 on development letters."""

    return replay_gan_rungs("dev750", slug=slug)


def _comparison_summary(
    scored: Sequence[Mapping[str, Any]],
    *,
    slug: str,
    split: str,
    holdout: bool,
    event_id_changes: int,
    kind_changes: int,
    format_rescues: int,
    format_harms: int,
    shared_raw_output: str = "gan_llm_extract",
) -> dict[str, Any]:
    return {
        "claim_boundary": (
            "Gan aggregate-only test450 replay. Do not inspect holdout rows."
            if holdout
            else "Gan development replay. Not holdout."
        ),
        "format_only_check": {
            "repair_mode": GAN_REPAIR_MODE_FOR_RUNG["llm_encode"],
            "select_repair_mode": GAN_REPAIR_MODE_FOR_RUNG["llm_select"],
            "selected_event_id_changes": event_id_changes,
            "predicted_kind_changes": kind_changes,
            "purist_rescues": format_rescues,
            "purist_harms": format_harms,
            "used_as_rung_3": event_id_changes == 0,
            "note": (
                "Living cell 3 is codebook encode then rule select "
                "(gan_rules_encode, llm_select_after_codebook). "
                "selected_event_id_changes still records whether encode "
                "kept the extract pick. Historical llm_encode is the "
                "five-cell encode ablation, not this roster."
            ),
        },
        "generated_on": datetime.now(UTC).date().isoformat(),
        "model_slug": slug,
        "row_count": len(scored),
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "rungs": {
            rung: _rung_summary(scored, rung) for rung in RUNG_IDS if rung != "llm_pre_post"
        },
        "shared_raw_output": shared_raw_output,
        "split": split,
    }


def _rung_summary(rows: Sequence[Mapping[str, Any]], rung: str) -> dict[str, Any]:
    n = len(rows)
    purist = sum(1 for row in rows if row["rungs"][rung]["purist_correct"])
    pragmatic = sum(1 for row in rows if row["rungs"][rung]["pragmatic_correct"])
    scorable = sum(1 for row in rows if row["rungs"][rung].get("scorable"))
    kinds = Counter(
        str(row["rungs"][rung].get("predicted_kind") or "unscorable") for row in rows
    )
    purist_rate = round(purist / n, 4) if n else 0.0
    pragmatic_rate = round(pragmatic / n, 4) if n else 0.0
    return {
        "purist_correct": purist,
        "micro_f1": purist_rate,
        "purist_accuracy": purist_rate,
        "pragmatic_correct": pragmatic,
        "pragmatic_micro_f1": pragmatic_rate,
        "pragmatic_accuracy": pragmatic_rate,
        "scorable": scorable,
        "predicted_kinds": dict(kinds),
        "predicted_candidate_count": sum(
            int(row["rungs"][rung].get("predicted_candidate_count") or 0) for row in rows
        ),
    }
