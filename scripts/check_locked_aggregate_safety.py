#!/usr/bin/env python3
"""Validate retained test60/test450 aggregates without loading locked rows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    ROOT / "experiments/gan2026_matched_v05_test450_aggregate_20260716.json",
    ROOT / "experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json",
    ROOT / "experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json",
    ROOT / "experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json",
    ROOT / "experiments/six_model_holdout_category_aggregates_20260806.json",
)
FORBIDDEN_KEYS = {
    "letter_id", "letter_ids", "source_row_index", "source_row_indices",
    "note_text", "raw_output", "predicted_mentions", "gold_mentions",
}


def forbidden_paths(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in FORBIDDEN_KEYS or (
                str(key) == "rows" and isinstance(item, (dict, list))
            ):
                found.append(path)
            found.extend(forbidden_paths(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(forbidden_paths(item, f"{prefix}[{index}]"))
    return found


def main() -> int:
    failures: list[str] = []
    for path in ARTIFACTS:
        if not path.is_file():
            failures.append(f"missing:{path.relative_to(ROOT).as_posix()}")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        forbidden = forbidden_paths(payload)
        if forbidden:
            failures.append(
                f"row-level-content:{path.relative_to(ROOT).as_posix()}:{','.join(forbidden)}"
            )
    if failures:
        print(json.dumps({"passed": False, "failures": failures}, indent=2))
        return 1
    print(json.dumps({
        "passed": True,
        "artifacts": [path.relative_to(ROOT).as_posix() for path in ARTIFACTS],
        "row_level_content_detected": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
