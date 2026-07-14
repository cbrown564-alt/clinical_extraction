#!/usr/bin/env python3
"""Validate the aggregate-only Gan efficiency comparison artifact."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "experiments" / "gan2026_single_vs_multimodel_efficiency_2026-07-14.json"
SINGLE_REPORT = (
    ROOT
    / "experiments"
    / "gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md"
)
V12_REPORT = (
    ROOT
    / "experiments"
    / "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md"
)
ARCHITECTURE_REPORT = (
    ROOT
    / "docs"
    / "research"
    / "gan2026"
    / "architecture"
    / "gan2026_simplest_near_ceiling_architecture_results_2026-06-16.md"
)
REGISTRY = ROOT / "experiments" / "registry.jsonl"


def _method(artifact: dict[str, Any], method_id: str) -> dict[str, Any]:
    return next(row for row in artifact["methods"] if row["method_id"] == method_id)


def _require_match(pattern: str, text: str, source: Path) -> re.Match[str]:
    match = re.search(pattern, text)
    if match is None:
        raise ValueError(f"expected aggregate fact missing from {source.relative_to(ROOT)}")
    return match


def validate() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    single_text = SINGLE_REPORT.read_text(encoding="utf-8")
    v12_text = V12_REPORT.read_text(encoding="utf-8")
    architecture_text = ARCHITECTURE_REPORT.read_text(encoding="utf-8")
    registry_rows = [
        json.loads(line)
        for line in REGISTRY.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    single = _method(artifact, "single_pass_event_extractor")
    v12 = _method(artifact, "v12_multi_model_comparison")

    single_match = _require_match(
        r"\| `hybrid_structured_events` \| 450 \| 448 \| 2 \| N/A \| (\d+) \(0\.812\)",
        single_text,
        SINGLE_REPORT,
    )
    v12_final = _require_match(r"Final Purist: (\d+)/(\d+)", v12_text, V12_REPORT)
    v12_calls = _require_match(r"Model calls attempted: (\d+)", v12_text, V12_REPORT)

    if int(single_match.group(1)) != single["purist_correct"]:
        raise ValueError("single-pass Purist count drift")
    if (int(v12_final.group(1)), int(v12_final.group(2))) != (
        v12["purist_correct"],
        v12["purist_total"],
    ):
        raise ValueError("V12 Purist count drift")
    if int(v12_calls.group(1)) != v12["recorded_live_reasoner_calls"]:
        raise ValueError("V12 reasoner call count drift")

    registry_v12 = next(
        row
        for row in registry_rows
        if row["run_id"]
        == "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13"
    )
    registry_metrics = registry_v12["primary_metrics"]
    cache_source = registry_v12["cache_reuse_source"]
    for phrase in ("GPT structured-event", "Qwen patched"):
        if phrase not in cache_source:
            raise ValueError(f"V12 input-provenance fact missing: {phrase}")
    if "DeepSeek test source unavailable" not in registry_v12["model_role"]:
        raise ValueError("V12 DeepSeek-unavailable provenance fact missing")
    if re.search(r"DeepSeek\s+available on zero rows", architecture_text) is None:
        raise ValueError("selected architecture report is missing the test-input correction")
    if v12["input_availability_rows"] != {"gpt": 450, "qwen": 450, "deepseek": 0}:
        raise ValueError("V12 aggregate input-availability boundary drift")
    if (
        registry_metrics["wrong_to_correct_vs_v0"]
        != v12["wrong_to_correct_vs_single_pass"]
    ):
        raise ValueError("V12 wrong-to-correct count drift")
    if (
        registry_metrics["correct_to_wrong_vs_v0"]
        != v12["correct_to_wrong_vs_single_pass"]
    ):
        raise ValueError("V12 correct-to-wrong count drift")

    comparison = artifact["comparison"]
    expected_delta = v12["purist_correct"] - single["purist_correct"]
    if comparison["purist_correct_delta"] != expected_delta:
        raise ValueError("Purist delta is not reproducible")
    expected_points = 100 * expected_delta / artifact["row_count"]
    if not math.isclose(
        comparison["purist_percentage_point_delta"], expected_points, abs_tol=1e-6
    ):
        raise ValueError("Purist percentage-point delta is not reproducible")
    if comparison["cold_model_pass_ratio"] != (
        v12["cold_model_passes_per_note"] / single["cold_model_passes_per_note"]
    ):
        raise ValueError("cold model-pass ratio is not reproducible")

    statuses = {row["dimension"]: row["status"] for row in artifact["dimension_evidence"]}
    expected_statuses = {
        "quality": "observed",
        "calls": "derived",
        "tokens": "unavailable",
        "cost": "unavailable",
        "latency": "unavailable",
        "hardware": "partial",
        "cache_use": "partial",
    }
    if statuses != expected_statuses:
        raise ValueError("efficiency evidence-status boundary drift")

    if artifact["row_policy"] != "aggregate_only_no_row_inspection":
        raise ValueError("locked-row policy drift")
    if artifact["decision"] != "retain_single_pass_and_reject_matched_efficiency_claim":
        raise ValueError("decision drift")


def main() -> int:
    validate()
    print(f"Gan efficiency comparison valid: {ARTIFACT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
