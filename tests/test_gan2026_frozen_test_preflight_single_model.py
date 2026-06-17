"""Tests for the first-class single-model reused-subject frozen-test preflight."""

from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight_single_model import (
    DEFAULT_SUBJECT_ARTIFACT,
    SingleModelPreflightConfig,
    run_single_model_preflight,
)

ABSENT = Path("experiments/__nonexistent_single_model_preflight_output__.jsonl")


def test_real_test450_setup_passes_when_outputs_absent() -> None:
    report = run_single_model_preflight(SingleModelPreflightConfig(
        outputs_must_be_absent=(ABSENT,),
    ))
    assert report.ok, report.failures
    # the substantive integrity checks are present
    joined = " | ".join(report.checks)
    assert "records == manifest locked set" in joined
    assert "subject artifact covers the locked set" in joined
    assert "v0_reference on every row" in joined


def test_missing_subject_artifact_fails() -> None:
    report = run_single_model_preflight(SingleModelPreflightConfig(
        subject_artifact_path=Path("experiments/__nope__.jsonl"),
        outputs_must_be_absent=(ABSENT,),
    ))
    assert not report.ok
    assert any("subject artifact missing" in f for f in report.failures)


def test_wrong_row_count_fails() -> None:
    report = run_single_model_preflight(SingleModelPreflightConfig(
        expected_row_count=999,
        outputs_must_be_absent=(ABSENT,),
    ))
    assert not report.ok
    assert any("row count drifted" in f for f in report.failures)


def test_present_output_blocks_launch() -> None:
    existing = DEFAULT_SUBJECT_ARTIFACT  # any path known to exist
    report = run_single_model_preflight(SingleModelPreflightConfig(
        outputs_must_be_absent=(existing,),
    ))
    assert not report.ok
    assert any("already exists before launch" in f for f in report.failures)


def test_hash_pin_mismatch_fails() -> None:
    report = run_single_model_preflight(SingleModelPreflightConfig(
        subject_artifact_sha256="0" * 64,
        outputs_must_be_absent=(ABSENT,),
    ))
    assert not report.ok
    assert any("hash mismatch" in f for f in report.failures)


def test_wrong_manifest_name_fails() -> None:
    report = run_single_model_preflight(SingleModelPreflightConfig(
        expected_split_manifest="not_the_real_manifest",
        outputs_must_be_absent=(ABSENT,),
    ))
    assert not report.ok
    assert any("split manifest drifted" in f for f in report.failures)
