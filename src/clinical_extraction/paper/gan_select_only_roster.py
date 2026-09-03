"""Six-model rule select without encode (`llm_select_only`) on saved extracts.

Separates encode from decide on the Hybrid stack: select families run on each
model's codebook extract ledger with codebook encode off. Zero model calls;
holdout stays aggregate-only.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.gan_cell_replay import (
    gan_living_extract_rows_path,
    score_label,
)
from clinical_extraction.paper.methods import (
    gan_machine_split,
    gan_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)

ROOT = discover_repo_root(start=Path(__file__))
PROTOCOL = (
    "docs/research/gan2026/gan_select_only_roster_test450_protocol_2026-09-03.md"
)
DEFAULT_ARTIFACT = (
    ROOT / "docs/research/gan2026/gan_select_only_roster_test450_2026-09-03.json"
)
ROSTER_SLUGS: tuple[str, ...] = (
    "gemini37flash",
    "grok46",
    "gpt56luna",
    "deepseek_v4_flash",
    "qwen38_27b",
    "gemma4_26b",
)
CITED_GEMINI_CELL4_TEST450 = 382
REPAIR_MODE = "llm_select_only"

# Living Table 4 / Table H1 companions (read-only; not remeasured here).
TABLE4_STOPS: Mapping[str, Mapping[str, int]] = {
    "gemini37flash": {"find": 355, "encode": 360, "hybrid": 387, "hybrid_pragmatic": 396},
    "grok46": {"find": 355, "encode": 365, "hybrid": 384, "hybrid_pragmatic": 400},
    "gpt56luna": {"find": 312, "encode": 332, "hybrid": 355, "hybrid_pragmatic": 369},
    "deepseek_v4_flash": {
        "find": 334,
        "encode": 341,
        "hybrid": 369,
        "hybrid_pragmatic": 382,
    },
    "qwen38_27b": {"find": 315, "encode": 329, "hybrid": 343, "hybrid_pragmatic": 363},
    "gemma4_26b": {"find": 299, "encode": 307, "hybrid": 326, "hybrid_pragmatic": 348},
}
TABLE_H1_SELECT: Mapping[str, Mapping[str, int]] = {
    "gemini37flash": {"purist": 383, "pragmatic": 391},
    "grok46": {"purist": 378, "pragmatic": 394},
    "gpt56luna": {"purist": 335, "pragmatic": 353},
    "deepseek_v4_flash": {"purist": 345, "pragmatic": 356},
    "qwen38_27b": {"purist": 294, "pragmatic": 312},
    "gemma4_26b": {"purist": 278, "pragmatic": 306},
}


def measure_select_only(
    slug: str,
    split: str = "test450",
) -> dict[str, Any]:
    """Score `llm_select_only` on one model's saved extract ledger."""

    if not holdout_is_aggregate_only(split) and split != "dev750":
        raise ValueError(f"unsupported split: {split}")
    n = gan_row_count(split)
    rows_path = gan_living_extract_rows_path(slug, split)
    if not rows_path.is_file():
        raise FileNotFoundError(f"missing extract rows for {slug}/{split}: {rows_path}")
    records = {
        record.source_row_index: record
        for record in load_records_for_split(gan_machine_split(split))
    }
    rows = load_jsonl_rows(rows_path)
    if len(rows) != n or len(records) != n:
        raise RuntimeError(
            f"{slug}/{split}: expected {n} rows and gold records, "
            f"found {len(rows)} / {len(records)}"
        )
    config = StructuredRepairConfig.for_mode(REPAIR_MODE)
    if config.encode_enabled():
        raise RuntimeError(f"{REPAIR_MODE} must keep encode disabled")
    purist = 0
    pragmatic = 0
    scorable = 0
    for row in rows:
        record = records[int(row["source_row_index"])]
        raw = str(row.get("raw_output") or "")
        extraction, _, _, _ = parse_structured_json_with_trace(
            raw,
            note_text=record.note_text,
            repair_config=config,
        )
        label = None if extraction is None else extraction.selection.final_label
        scored = score_label(record, label)
        purist += int(scored["purist_correct"])
        pragmatic += int(scored["pragmatic_correct"])
        scorable += int(scored["scorable"])
    companions = TABLE4_STOPS[slug]
    llm_select = TABLE_H1_SELECT[slug]
    return {
        "model_slug": slug,
        "split": split,
        "n": n,
        "row_policy": "aggregate_only" if holdout_is_aggregate_only(split) else "review_permitted",
        "repair_mode": REPAIR_MODE,
        "extract_rows": str(rows_path.relative_to(ROOT)),
        "select_only": {
            "purist_correct": purist,
            "purist_micro_f1": round(purist / n, 4),
            "pragmatic_correct": pragmatic,
            "pragmatic_micro_f1": round(pragmatic / n, 4),
            "scorable": scorable,
        },
        "companions": {
            "find_purist": companions["find"],
            "encode_purist": companions["encode"],
            "hybrid_purist": companions["hybrid"],
            "hybrid_pragmatic": companions["hybrid_pragmatic"],
            "llm_select_purist": llm_select["purist"],
            "llm_select_pragmatic": llm_select["pragmatic"],
        },
        "deltas_purist": {
            "select_only_minus_find": purist - companions["find"],
            "hybrid_minus_select_only": companions["hybrid"] - purist,
            "select_only_minus_llm_select": purist - llm_select["purist"],
        },
    }


def measure_roster(
    split: str = "test450",
    *,
    slugs: Sequence[str] = ROSTER_SLUGS,
) -> dict[str, Any]:
    """Score select-only for the living six-model roster."""

    models = [measure_select_only(slug, split) for slug in slugs]
    return {
        "protocol": PROTOCOL,
        "generated_on": datetime.now(UTC).date().isoformat(),
        "claim_boundary": (
            "Gan aggregate-only select-only roster replay. Repository "
            "decomposition of encode versus decide. Do not inspect holdout "
            "rows. Do not retune Table 1 or Table 4."
        ),
        "model_calls": 0,
        "split": split,
        "n": gan_row_count(split),
        "repair_mode": REPAIR_MODE,
        "gemini_cell4_gate_purist": CITED_GEMINI_CELL4_TEST450,
        "models": models,
    }


def measure_and_write(
    split: str = "test450",
    *,
    path: Path | None = None,
    slugs: Sequence[str] = ROSTER_SLUGS,
) -> Path:
    """Measure the roster and write the aggregate JSON artifact."""

    out = path or DEFAULT_ARTIFACT
    payload = measure_roster(split, slugs=slugs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
