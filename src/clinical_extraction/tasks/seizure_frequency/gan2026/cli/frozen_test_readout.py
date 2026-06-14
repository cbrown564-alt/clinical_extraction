"""Aggregate-only readout helper for the frozen Gan 2026 V12 test audit."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight import (
    DEFAULT_TEST_JSONL_PATH,
    DEFAULT_TEST_REPORT_PATH,
    EXPECTED_TEST_ROW_COUNT,
)

TARGET_PURIST_CORRECT = 383
SUMMARY_LINE_RE = re.compile(r"^- (?P<label>[^:]+): (?P<value>.+?)\s*$")
COUNT_RE = re.compile(r"^(?P<count>\d+)/(?P<rows>\d+)$")


@dataclass(frozen=True)
class FrozenTestReadout:
    """Permitted aggregate-only V12 test readout."""

    ok: bool
    report_path: str
    metrics: dict[str, Any]
    failures: tuple[str, ...]

    def to_json_record(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "report_path": self.report_path,
            "metrics": self.metrics,
            "failures": list(self.failures),
        }


def read_aggregate_report(path: Path = DEFAULT_TEST_REPORT_PATH) -> FrozenTestReadout:
    """Parse only permitted aggregate fields from the frozen V12 Markdown report."""

    failures: list[str] = []
    if not path.exists():
        return FrozenTestReadout(
            ok=False,
            report_path=str(path),
            metrics={},
            failures=(f"missing aggregate-only report: {path}",),
        )
    report_text = path.read_text(encoding="utf-8")
    _check_no_row_level_sections(report_text, failures)
    _check_required_report_markers(report_text, failures)
    summary = _parse_summary(report_text)
    metrics = _build_metrics(summary)
    _check_expected_metrics(metrics, failures)
    return FrozenTestReadout(
        ok=not failures,
        report_path=str(path),
        metrics=metrics,
        failures=tuple(failures),
    )


def _check_no_row_level_sections(report_text: str, failures: list[str]) -> None:
    forbidden_text = (
        "## Rows",
        "| Row |",
        "source_row_index",
        "transition_vs_v0",
        "fresh_evidence_decision_record",
        "score_layers",
    )
    for text in forbidden_text:
        if text in report_text:
            failures.append(f"report exposes row-level marker: {text}")


def _check_required_report_markers(report_text: str, failures: list[str]) -> None:
    required_text = (
        "frozen aggregate-only V12 fresh-evidence holdout audit artifact",
        "- Split: `test`, manifest `gan2026_split_v1`.",
        f"- JSONL artifact: `{DEFAULT_TEST_JSONL_PATH}`",
        "## Aggregate-Only Holdout Readout",
    )
    for text in required_text:
        if text not in report_text:
            failures.append(f"report missing aggregate-only marker: {text}")


def _parse_summary(report_text: str) -> dict[str, str]:
    in_summary = False
    values: dict[str, str] = {}
    for line in report_text.splitlines():
        if line.strip() == "## Summary":
            in_summary = True
            continue
        if in_summary and line.startswith("## "):
            break
        if not in_summary:
            continue
        match = SUMMARY_LINE_RE.match(line)
        if match:
            values[match.group("label")] = match.group("value").strip()
    return values


def _build_metrics(summary: dict[str, str]) -> dict[str, Any]:
    final_purist_correct, final_purist_rows = _parse_count(summary.get("Final Purist"))
    raw_purist_correct, raw_purist_rows = _parse_count(summary.get("Raw model Purist"))
    format_purist_correct, format_purist_rows = _parse_count(
        summary.get("Format-only Purist")
    )
    v0_purist_correct, v0_purist_rows = _parse_count(summary.get("V0 Purist"))
    final_pragmatic_correct, final_pragmatic_rows = _parse_count(
        summary.get("Final Pragmatic")
    )
    raw_pragmatic_correct, raw_pragmatic_rows = _parse_count(
        summary.get("Raw model Pragmatic")
    )
    format_pragmatic_correct, format_pragmatic_rows = _parse_count(
        summary.get("Format-only Pragmatic")
    )
    v0_pragmatic_correct, v0_pragmatic_rows = _parse_count(
        summary.get("V0 Pragmatic")
    )
    rows = final_purist_rows or raw_purist_rows or v0_purist_rows
    final_purist_rate = (
        final_purist_correct / final_purist_rows
        if final_purist_correct is not None and final_purist_rows
        else None
    )
    final_pragmatic_rate = (
        final_pragmatic_correct / final_pragmatic_rows
        if final_pragmatic_correct is not None and final_pragmatic_rows
        else None
    )
    return {
        "rows": rows,
        "target_purist_correct": TARGET_PURIST_CORRECT,
        "target_rows": EXPECTED_TEST_ROW_COUNT,
        "target_rate": TARGET_PURIST_CORRECT / EXPECTED_TEST_ROW_COUNT,
        "target_reached": (
            final_purist_correct is not None
            and final_purist_rows == EXPECTED_TEST_ROW_COUNT
            and final_purist_correct >= TARGET_PURIST_CORRECT
        ),
        "final_purist_correct": final_purist_correct,
        "final_purist_rows": final_purist_rows,
        "final_purist_rate": final_purist_rate,
        "raw_model_purist_correct": raw_purist_correct,
        "raw_model_purist_rows": raw_purist_rows,
        "format_only_purist_correct": format_purist_correct,
        "format_only_purist_rows": format_purist_rows,
        "v0_purist_correct": v0_purist_correct,
        "v0_purist_rows": v0_purist_rows,
        "final_pragmatic_correct": final_pragmatic_correct,
        "final_pragmatic_rows": final_pragmatic_rows,
        "final_pragmatic_rate": final_pragmatic_rate,
        "raw_model_pragmatic_correct": raw_pragmatic_correct,
        "raw_model_pragmatic_rows": raw_pragmatic_rows,
        "format_only_pragmatic_correct": format_pragmatic_correct,
        "format_only_pragmatic_rows": format_pragmatic_rows,
        "v0_pragmatic_correct": v0_pragmatic_correct,
        "v0_pragmatic_rows": v0_pragmatic_rows,
        "prediction_bearing_rows": _parse_int(summary.get("Prediction-bearing rows")),
        "model_calls_attempted": _parse_int(summary.get("Model calls attempted")),
        "call_failures": _parse_int(summary.get("Call failures")),
        "parse_or_validation_failures": _parse_int(
            summary.get("Parse/schema/label failures")
        ),
        "fresh_evidence_replace_actions": _parse_int(
            summary.get("Fresh-evidence replace actions")
        ),
        "fresh_evidence_gate_fallbacks": _parse_int(
            summary.get("Evidence-gate fallbacks")
        ),
        "evidence_exact_substrings": _parse_int(
            summary.get("Exact evidence substrings")
        ),
        "net_purist_gain_vs_v0": _parse_int(summary.get("Net Purist gain vs V0")),
        "changed_label_precision_vs_v0": _parse_float(
            summary.get("Changed-label precision vs V0")
        ),
        "actions": summary.get("Actions"),
    }


def _check_expected_metrics(metrics: dict[str, Any], failures: list[str]) -> None:
    if metrics.get("final_purist_rows") != EXPECTED_TEST_ROW_COUNT:
        failures.append(
            "Final Purist denominator is not the locked test row count: "
            f"{metrics.get('final_purist_rows')}"
        )
    if metrics.get("rows") != EXPECTED_TEST_ROW_COUNT:
        failures.append(
            f"aggregate readout row count is not {EXPECTED_TEST_ROW_COUNT}: "
            f"{metrics.get('rows')}"
        )
    if metrics.get("final_pragmatic_rows") != EXPECTED_TEST_ROW_COUNT:
        failures.append(
            "Final Pragmatic denominator is not the locked test row count: "
            f"{metrics.get('final_pragmatic_rows')}"
        )
    if metrics.get("format_only_purist_rows") != EXPECTED_TEST_ROW_COUNT:
        failures.append(
            "Format-only Purist denominator is not the locked test row count: "
            f"{metrics.get('format_only_purist_rows')}"
        )
    if metrics.get("format_only_pragmatic_rows") != EXPECTED_TEST_ROW_COUNT:
        failures.append(
            "Format-only Pragmatic denominator is not the locked test row count: "
            f"{metrics.get('format_only_pragmatic_rows')}"
        )
    required_numeric_fields = (
        "final_purist_correct",
        "final_pragmatic_correct",
        "format_only_purist_correct",
        "format_only_pragmatic_correct",
        "prediction_bearing_rows",
        "model_calls_attempted",
        "call_failures",
        "parse_or_validation_failures",
        "evidence_exact_substrings",
    )
    for field_name in required_numeric_fields:
        if metrics.get(field_name) is None:
            failures.append(f"missing aggregate metric: {field_name}")


def _parse_count(value: str | None) -> tuple[int | None, int | None]:
    if value is None:
        return None, None
    match = COUNT_RE.match(value.strip())
    if not match:
        return None, None
    return int(match.group("count")), int(match.group("rows"))


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "None":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Read the frozen V12 test Markdown report without row-level details."
    )
    parser.add_argument("--markdown", type=Path, default=DEFAULT_TEST_REPORT_PATH)
    parser.add_argument("--json", action="store_true", help="Emit JSON readout.")
    args = parser.parse_args(argv)

    if not _same_cli_path(args.markdown, DEFAULT_TEST_REPORT_PATH):
        parser.error(
            "frozen test readout must use --markdown "
            f"{DEFAULT_TEST_REPORT_PATH}"
        )

    readout = read_aggregate_report(args.markdown)
    if args.json:
        print(json.dumps(readout.to_json_record(), indent=2, sort_keys=True))
    else:
        for key, value in readout.metrics.items():
            print(f"{key}: {value}")
        for failure in readout.failures:
            print(f"FAIL: {failure}")
    raise SystemExit(0 if readout.ok else 1)


def _same_cli_path(path: Path, expected_path: Path) -> bool:
    return path.resolve(strict=False) == expected_path.resolve(strict=False)


if __name__ == "__main__":
    main()
