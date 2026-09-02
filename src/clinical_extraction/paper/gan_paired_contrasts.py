"""Predeclared paired Purist tests on Gan letters."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.cells import GAN_REPAIR_MODE_FOR_RUNG
from clinical_extraction.paper.gan_cell_replay import (
    gan_living_extract_rows_path,
    score_label,
)
from clinical_extraction.paper.methods import (
    gan_machine_split,
    gan_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.paper.paired_accuracy import (
    PairedAccuracyTest,
    paired_accuracy_test,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
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
CITED_SLUG = "gemini37flash"
SPLIT = "test450"
DEV_SPLIT = "dev750"
SELECT_MODE = GAN_REPAIR_MODE_FOR_RUNG["llm_select"]
CELL5_ROWS = (
    ROOT
    / "scratch/holdout/paper/gan_llm_select_from_extract"
    / CITED_SLUG
    / "gan_llm_extract"
    / SPLIT
    / "rows.jsonl"
)


def gan_extract_segment_rows_path(
    segment: str,
    *,
    split: str,
    slug: str = CITED_SLUG,
) -> Path:
    """Return a non-living Gemini extract replay file."""

    holdout = holdout_is_aggregate_only(split)
    root = ROOT / ("scratch/holdout/paper" if holdout else "experiments/paper")
    return root / "gan_llm_extract" / slug / segment / split / "rows.jsonl"


def aligned_correctness(
    left: Mapping[int, bool],
    right: Mapping[int, bool],
    *,
    expected: int,
    split: str,
) -> tuple[tuple[bool, ...], tuple[bool, ...]]:
    """Align two letter maps on the shared source-row index order."""

    keys = sorted(set(left) & set(right))
    if len(keys) != expected:
        raise RuntimeError(
            f"expected {expected} paired {split} letters, found {len(keys)}"
        )
    return (
        tuple(left[key] for key in keys),
        tuple(right[key] for key in keys),
    )


def rules_select_correct(
    records: Mapping[int, GanFrequencyRecord],
) -> dict[int, bool]:
    """Score the promoted three-stage rules program on each letter."""

    config = phase_c_candidate_config()
    return {
        index: bool(
            score_label(record, run_record_three_stage(record, config).stops.select_label)[
                "purist_correct"
            ]
        )
        for index, record in records.items()
    }


def codebook_select_correct(
    rows_path: Path,
    records: Mapping[int, GanFrequencyRecord],
) -> dict[int, bool]:
    """Replay saved extract raws through living cell-3 rule select."""

    if not rows_path.is_file():
        raise FileNotFoundError(f"missing extract replay: {rows_path}")
    repair = StructuredRepairConfig.for_mode(SELECT_MODE)
    scored: dict[int, bool] = {}
    for row in load_jsonl_rows(rows_path):
        index = int(row["source_row_index"])
        record = records[index]
        extraction, _, _, _ = parse_structured_json_with_trace(
            str(row.get("raw_output") or ""),
            note_text=record.note_text,
            repair_config=repair,
        )
        label = extraction.selection.final_label if extraction else None
        scored[index] = bool(score_label(record, label)["purist_correct"])
    return scored


def rung_select_correct(scored_path: Path) -> dict[int, bool]:
    """Read living-rung Purist select flags. A missing flag counts as incorrect."""

    if not scored_path.is_file():
        raise FileNotFoundError(f"missing rung scored file: {scored_path}")
    scored: dict[int, bool] = {}
    for row in load_jsonl_rows(scored_path):
        index = int(row["source_row_index"])
        select = (row.get("rungs") or {}).get("llm_select") or {}
        scored[index] = bool(select.get("purist_correct"))
    return scored


def row_comparison_correct(rows_path: Path) -> dict[int, bool]:
    """Read stored Purist correctness; a missing flag counts as incorrect."""

    if not rows_path.is_file():
        raise FileNotFoundError(f"missing scored rows: {rows_path}")
    scored: dict[int, bool] = {}
    for row in load_jsonl_rows(rows_path):
        index = int(row["source_row_index"])
        scored[index] = bool((row.get("comparison") or {}).get("purist_correct"))
    return scored


def _payload(result: PairedAccuracyTest, **meta: Any) -> dict[str, Any]:
    return {
        **meta,
        "n": result.n,
        "correct_a": result.correct_a,
        "correct_b": result.correct_b,
        "a_right_b_wrong": result.a_only,
        "a_wrong_b_right": result.b_only,
        "accuracy_a": round(result.correct_a / result.n, 4),
        "accuracy_b": round(result.correct_b / result.n, 4),
        "accuracy_delta": round(result.accuracy_delta, 4),
        "delta_ci95": [round(result.delta_ci_low, 4), round(result.delta_ci_high, 4)],
        "mcnemar_exact_p": result.p_value,
    }


def _pair(
    left: Mapping[int, bool],
    right: Mapping[int, bool],
    *,
    split: str,
) -> PairedAccuracyTest:
    return paired_accuracy_test(
        *aligned_correctness(
            left,
            right,
            expected=gan_row_count(split),
            split=split,
        )
    )


def run_predeclared_contrasts(
    *,
    slug: str = CITED_SLUG,
    records: Mapping[int, GanFrequencyRecord] | None = None,
) -> dict[str, Any]:
    """Score the predeclared Gemini paired contrasts. No new calls."""

    loaded = records or {
        record.source_row_index: record
        for record in load_records_for_split(gan_machine_split(SPLIT))
    }
    living_extract = gan_living_extract_rows_path(slug, SPLIT)
    cell3 = codebook_select_correct(living_extract, loaded)
    rules = rules_select_correct(loaded)
    cell5 = row_comparison_correct(CELL5_ROWS)
    temp1 = codebook_select_correct(
        gan_extract_segment_rows_path("temperature_1", split=SPLIT, slug=slug),
        loaded,
    )
    thinking_high = codebook_select_correct(
        gan_extract_segment_rows_path("reasoning_high", split=SPLIT, slug=slug),
        loaded,
    )
    loaded_dev = {
        record.source_row_index: record
        for record in load_records_for_split(gan_machine_split(DEV_SPLIT))
    }
    living_dev = codebook_select_correct(
        gan_living_extract_rows_path(slug, DEV_SPLIT),
        loaded_dev,
    )
    temp1_dev = codebook_select_correct(
        gan_extract_segment_rows_path("temperature_1", split=DEV_SPLIT, slug=slug),
        loaded_dev,
    )
    contrasts = {
        "cell3_vs_rules": _payload(
            _pair(cell3, rules, split=SPLIT),
            a="cell3_living_codebook_select",
            b="rules_three_stage_select",
            claim="Table 1: model-led find then rules versus standalone rules",
            split=SPLIT,
        ),
        "cell3_vs_cell5": _payload(
            _pair(cell3, cell5, split=SPLIT),
            a="cell3_living_codebook_select",
            b="cell5_llm_select_from_extract",
            claim="Table 1: model-led find then rules versus end-to-end model",
            split=SPLIT,
        ),
        "gemini_temperature_0_vs_1_test450": _payload(
            _pair(cell3, temp1, split=SPLIT),
            a="cell3_temperature_0",
            b="cell3_temperature_1",
            claim="Gemini temperature 0 versus 1 on the living cell-3 stack",
            split=SPLIT,
        ),
        "gemini_temperature_0_vs_1_dev750": _payload(
            _pair(living_dev, temp1_dev, split=DEV_SPLIT),
            a="cell3_temperature_0",
            b="cell3_temperature_1",
            claim="Gemini temperature 0 versus 1 on the living cell-3 stack",
            split=DEV_SPLIT,
        ),
        "gemini_thinking_low_vs_high": _payload(
            _pair(cell3, thinking_high, split=SPLIT),
            a="cell3_thinking_low",
            b="cell3_thinking_high",
            claim=(
                "Gemini living thinking (low) versus high effort at the "
                "cell-3 select stop"
            ),
            split=SPLIT,
        ),
    }
    return {
        "claim_boundary": (
            "Paired Purist tests. Holdout contrasts are aggregate-only "
            "discordant counts; do not inspect test450 rows. The Gemini "
            "temperature contrast is reported on both test450 and dev750."
        ),
        "contrasts": contrasts,
        "generated_on": datetime.now(UTC).date().isoformat(),
        "model_slug": slug,
        "n_dev750": gan_row_count(DEV_SPLIT),
        "n_test450": gan_row_count(SPLIT),
        "row_policy": "aggregate_only_on_test450",
        "scorer": "purist",
        "split": SPLIT,
        "test": "exact_mcnemar_plus_wald_accuracy_delta_ci95",
        "thinking_framing": (
            "One thinking contrast: living low versus high at the cell-3 "
            "select stop on test450. High is the predeclared extra-budget "
            "setting (same 2x token cap as medium). Medium stays a point "
            "estimate. Thinking changes only find; the tested outcome is "
            "select."
        ),
        "temperature_framing": (
            "One temperature question, two splits: Gemini living 0 versus "
            "1 on the cell-3 stack, on test450 and on dev750."
        ),
        "vector_note": (
            "Cell 3 on both splits is the living codebook replay "
            "(llm_select_after_codebook, including last_event_well_since). "
            "Table 1 cites that same test450 total. Rules are "
            "phase_c_candidate_config() (325/450). Cell 5 uses stored "
            "gan_llm_select_from_extract comparison flags (383/450). "
            "dev750 temperature replays saved extracts through the same "
            "living select stack."
        ),
    }


def write_predeclared_contrasts(
    *,
    slug: str = CITED_SLUG,
) -> Path:
    """Write the aggregate-only paired-test artifact."""

    payload = run_predeclared_contrasts(slug=slug)
    out_dir = ROOT / "paper_experiments/gan/paired_significance" / slug / SPLIT
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "comparison.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def contrast_table(payload: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    """Return contrasts in report order."""

    order = (
        "cell3_vs_rules",
        "cell3_vs_cell5",
        "gemini_temperature_0_vs_1_test450",
        "gemini_temperature_0_vs_1_dev750",
        "gemini_thinking_low_vs_high",
    )
    contrasts = payload["contrasts"]
    return [contrasts[name] | {"id": name} for name in order]
