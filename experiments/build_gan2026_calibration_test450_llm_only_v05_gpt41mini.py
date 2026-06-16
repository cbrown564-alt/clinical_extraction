"""USER-AUTHORISED CALIBRATION holdout: llm_only direct labeler v0.5 on test450,
live gpt-4.1-mini.

Purpose: the FIRST-EVER test450 number on gpt-4.1-mini, to calibrate the true
validation->test gap (validation750 v0.5 = 575/750). This is explicitly a
calibration measurement, NOT a robustness-certified promotion: Cycle 1 flagged
this same v0.5 candidate as overfit on the battery. Aggregate-only, full 450-row
coverage, no row-level tuning. Resumable.
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026 import llm_config  # noqa: F401
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import llm_only_direct_labeler

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
RUN_ID = "gan2026_calibration_test450_llm_only_v05_gpt41mini_2026-06-16"
JSONL_PATH = EXPERIMENTS / f"{RUN_ID}.jsonl"
REPORT_PATH = EXPERIMENTS / f"{RUN_ID}.md"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"

MODEL = "openai/gpt-4.1-mini"
VALIDATION_REFERENCE = (575, 750)


def main() -> None:
    llm_only_direct_labeler.set_active_prompt_version(
        llm_only_direct_labeler.PROMPT_VERSION_V0_5
    )
    records = load_records_for_split("test")
    assert len(records) == 450, f"expected 450 test rows, got {len(records)}"
    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))

    reuse: dict[int, str] = {}
    if JSONL_PATH.exists():
        reuse = llm_only_direct_labeler.load_reusable_raw_outputs(JSONL_PATH)
        print(f"resuming: {len(reuse)} cached rows")

    rows, metadata = llm_only_direct_labeler.run_split(
        records,
        split="test",
        split_manifest=split_manifest,
        model=MODEL,
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        reuse_raw_outputs=reuse,
        reuse_source=str(JSONL_PATH) if reuse else None,
        escalation_reason="user_authorised_calibration_test450_gap_measurement",
        progress_every=25,
        checkpoint_jsonl_path=JSONL_PATH,
        checkpoint_report_path=REPORT_PATH,
    )
    llm_only_direct_labeler.write_jsonl(rows, JSONL_PATH)

    row_summary = llm_only_direct_labeler.summarize_records(rows)
    purist_correct = _find_first(row_summary, ("purist_correct", "purist_correct_count"))
    total = len(rows)
    if purist_correct is None:
        # Fallback: recursive search for a per-row purist_correct boolean.
        purist_correct = sum(1 for r in rows if _row_purist_correct(r))
    vref_c, vref_n = VALIDATION_REFERENCE
    val_frac = vref_c / vref_n
    test_frac = purist_correct / total if total else 0.0
    summary = {
        "run_id": RUN_ID,
        "candidate": "llm_only_direct_labeler v0.5",
        "model": MODEL,
        "split": "test",
        "test450_purist_correct": purist_correct,
        "test450_total": total,
        "test450_purist_fraction": round(test_frac, 4),
        "validation750_reference_purist": f"{vref_c}/{vref_n}",
        "validation750_reference_fraction": round(val_frac, 4),
        "val_to_test_gap_pp": round((val_frac - test_frac) * 100, 1),
        "target_test450": 405,
        "target_fraction": 0.9,
        "evidence_validity": (
            "User-authorised CALIBRATION measurement of the validation->test gap on "
            "gpt-4.1-mini. NOT a robustness-certified promotion (Cycle 1 flagged this "
            "v0.5 candidate as overfit on the battery). Aggregate-only, full 450-row "
            "coverage, no row-level tuning."
        ),
    }
    JSON_PATH.write_text(json.dumps({**summary, "metadata_keys": sorted(metadata)}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


def _find_first(obj: object, keys: tuple[str, ...]) -> int | None:
    """Recursively find the first int-valued match for any of `keys`."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys and isinstance(v, int) and not isinstance(v, bool):
                return v
        for v in obj.values():
            found = _find_first(v, keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_first(v, keys)
            if found is not None:
                return found
    return None


def _row_purist_correct(row: dict) -> bool:
    """Recursively locate this row's purist_correct boolean."""

    def search(obj: object) -> bool | None:
        if isinstance(obj, dict):
            if isinstance(obj.get("purist_correct"), bool):
                return obj["purist_correct"]
            for v in obj.values():
                r = search(v)
                if r is not None:
                    return r
        elif isinstance(obj, list):
            for v in obj:
                r = search(v)
                if r is not None:
                    return r
        return None

    return bool(search(row))


if __name__ == "__main__":
    main()
