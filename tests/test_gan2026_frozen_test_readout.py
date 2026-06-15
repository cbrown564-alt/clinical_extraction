from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.cli import frozen_test_readout

PINNED_TEST_JSONL = (
    "experiments\\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_"
    "safety_v0_9_2026-06-15.jsonl"
)


def test_frozen_test_readout_accepts_aggregate_only_success_report(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(_report(final_purist="383/450"), encoding="utf-8")

    readout = frozen_test_readout.read_aggregate_report(report_path)

    assert readout.ok is True
    assert readout.failures == ()
    assert readout.metrics["target_reached"] is True
    assert readout.metrics["final_purist_correct"] == 383
    assert readout.metrics["final_purist_rows"] == 450
    assert readout.metrics["final_purist_rate"] == 383 / 450
    assert readout.metrics["final_pragmatic_correct"] == 386
    assert readout.metrics["final_pragmatic_rows"] == 450
    assert readout.metrics["final_pragmatic_rate"] == 386 / 450
    assert readout.metrics["format_only_purist_correct"] == 383
    assert readout.metrics["format_only_purist_rows"] == 450
    assert readout.metrics["format_only_pragmatic_correct"] == 386
    assert readout.metrics["format_only_pragmatic_rows"] == 450
    assert readout.metrics["call_failures"] == 0


def test_frozen_test_readout_reports_below_target_without_failing_contract(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(_report(final_purist="382/450"), encoding="utf-8")

    readout = frozen_test_readout.read_aggregate_report(report_path)

    assert readout.ok is True
    assert readout.metrics["target_reached"] is False
    assert readout.metrics["final_purist_correct"] == 382


def test_frozen_test_readout_rejects_row_level_report(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(
        _report(final_purist="383/450") + "\n## Rows\n\n| Row | Action |\n",
        encoding="utf-8",
    )

    readout = frozen_test_readout.read_aggregate_report(report_path)

    assert readout.ok is False
    assert any(
        "report exposes row-level marker: ## Rows" in failure
        for failure in readout.failures
    )
    assert any(
        "report exposes row-level marker: | Row |" in failure
        for failure in readout.failures
    )


def test_frozen_test_readout_rejects_wrong_denominator(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(_report(final_purist="383/449"), encoding="utf-8")

    readout = frozen_test_readout.read_aggregate_report(report_path)

    assert readout.ok is False
    assert any("Final Purist denominator" in failure for failure in readout.failures)


def test_frozen_test_readout_rejects_wrong_pragmatic_denominator(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(
        _report(final_purist="383/450", final_pragmatic="386/449"),
        encoding="utf-8",
    )

    readout = frozen_test_readout.read_aggregate_report(report_path)

    assert readout.ok is False
    assert any("Final Pragmatic denominator" in failure for failure in readout.failures)


def test_frozen_test_readout_rejects_wrong_format_only_denominator(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(
        _report(final_purist="383/450", format_only_purist="383/449"),
        encoding="utf-8",
    )

    readout = frozen_test_readout.read_aggregate_report(report_path)

    assert readout.ok is False
    assert any("Format-only Purist denominator" in failure for failure in readout.failures)


def test_frozen_test_readout_rejects_unpinned_jsonl_artifact(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(
        _report(
            final_purist="383/450",
            jsonl_artifact="experiments/alternate_test_rows.jsonl",
        ),
        encoding="utf-8",
    )

    readout = frozen_test_readout.read_aggregate_report(report_path)

    assert readout.ok is False
    assert any(
        "report missing aggregate-only marker: - JSONL artifact: "
        "`experiments\\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl`"
        in failure
        for failure in readout.failures
    )


def test_frozen_test_readout_rejects_missing_report(tmp_path: Path) -> None:
    readout = frozen_test_readout.read_aggregate_report(tmp_path / "missing.md")

    assert readout.ok is False
    assert readout.metrics == {}
    assert readout.failures == (f"missing aggregate-only report: {tmp_path / 'missing.md'}",)


def test_frozen_test_readout_cli_rejects_alternate_markdown_path(
    tmp_path: Path,
    capsys,
) -> None:
    report_path = tmp_path / "test.md"
    report_path.write_text(_report(final_purist="383/450"), encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        frozen_test_readout.main(["--markdown", str(report_path), "--json"])

    assert exc_info.value.code == 2
    assert (
        "frozen test readout must use --markdown "
        "experiments\\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.md"
        in capsys.readouterr().err
    )


def _report(
    *,
    final_purist: str,
    format_only_purist: str = "383/450",
    format_only_pragmatic: str = "386/450",
    final_pragmatic: str = "386/450",
    jsonl_artifact: str = PINNED_TEST_JSONL,
) -> str:
    return f"""# Gan 2026 Fresh-Evidence Reasoner

Date: 2026-06-13

This is a frozen aggregate-only V12 fresh-evidence holdout audit artifact.
The model may replace the GPT structured-event final only from exact raw-note evidence.

## Experiment Unit

- Work class: V12 fresh-evidence reasoner over saved structured events.
- Rows: 450
- Split: `test`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1`
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_6`
- JSONL artifact: `{jsonl_artifact}`

## Summary

- Prediction-bearing rows: 450
- Model calls attempted: 450
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 120
- Evidence-gate fallbacks: 2
- Exact evidence substrings: 430
- V0 Purist: 364/450
- V0 Pragmatic: 381/450
- Raw model Purist: 380/450
- Raw model Pragmatic: 384/450
- Format-only Purist: {format_only_purist}
- Format-only Pragmatic: {format_only_pragmatic}
- Final Purist: {final_purist}
- Final Pragmatic: {final_pragmatic}
- Net Purist gain vs V0: 19
- Changed-label precision vs V0: 0.31
- Actions: `{{'keep_original_structured_event_final': 330}}`
- Profiles: omitted from the test report to keep the first readout aggregate-only.

## Gate

- Status: `promote`
- Interpretation: frozen readout

## Claim Boundary

frozen aggregate-only V12 test450 audit

## Aggregate-Only Holdout Readout

Row-level test details are intentionally omitted from this Markdown report.
"""
