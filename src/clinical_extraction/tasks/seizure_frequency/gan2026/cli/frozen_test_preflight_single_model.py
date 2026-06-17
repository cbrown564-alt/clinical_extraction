"""First-class frozen-test preflight for SINGLE-MODEL reused-subject holdout runs.

The V12 preflight (`frozen_test_preflight.py`) is hard-wired to the V12
`fresh_evidence_reasoner` + full-`gpt-4.1` + GPT/Qwen/DeepSeek three-source audit:
it certifies a *fresh multi-source label run*. A single-model holdout run that
**reuses an already-certified subject artifact** (e.g. the variant-D confidence
reviewer over the `v0_reference` test450 answers — one extra `gpt-4.1-mini` call per
row, no new label) has a different, narrower integrity surface. Before this module
the freeze warden had to substitute a hand-rolled split-integrity check per run; this
makes that check a reusable, tested instrument.

What it certifies (data/split integrity for a single-model reused-subject run):
  1. the split manifest is the expected version and row count;
  2. ``load_records_for_split(split)`` is exactly the manifest's locked row-id set
     (unique, complete, no extras);
  3. the reused subject artifact covers exactly that locked set (unique ids), carries
     the canonical ``v0_reference`` layer on every row, and — when pinned — matches an
     expected SHA-256 (source-symmetry inherited from the certified upstream artifact);
  4. the candidate run's declared outputs are absent (no cross-run outcome tuning).

It does NOT re-certify the frozen transform (the reviewer prompt) or git cleanliness —
those remain the certifier's checks, recorded as hashes by the candidate driver. This
module is deliberately decoupled from `frozen_test_preflight.py` so editing it never
disturbs the hash-pinned V12 protocol; it reuses only the public ``PreflightReport``.

Usage:
    uv run python -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight_single_model \\
        --subject-artifact experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl \\
        --output-jsonl experiments/gan2026_reliability_d_gating_test450_2026-06-17.jsonl --json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight import (
    PreflightReport,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_SUBJECT_ARTIFACT = Path(
    "experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl"
)
EXPECTED_SPLIT_MANIFEST = "gan2026_split_v1"
EXPECTED_TEST_ROW_COUNT = 450


@dataclass(frozen=True)
class SingleModelPreflightConfig:
    """Inputs for a single-model reused-subject holdout preflight."""

    split: str = "test"
    expected_split_manifest: str = EXPECTED_SPLIT_MANIFEST
    expected_row_count: int = EXPECTED_TEST_ROW_COUNT
    subject_artifact_path: Path = DEFAULT_SUBJECT_ARTIFACT
    require_v0_reference: bool = True
    subject_artifact_sha256: str | None = None
    outputs_must_be_absent: tuple[Path, ...] = field(default_factory=tuple)


def run_single_model_preflight(config: SingleModelPreflightConfig | None = None) -> PreflightReport:
    if config is None:
        config = SingleModelPreflightConfig()
    checks: list[str] = []
    failures: list[str] = []

    manifest = load_split_manifest()
    manifest_indices = _check_manifest(config, manifest, checks, failures)
    if manifest_indices is not None:
        _check_records_match_manifest(config, manifest_indices, checks, failures)
        _check_subject_artifact(config, manifest_indices, checks, failures)
    _check_outputs_absent(config.outputs_must_be_absent, checks, failures)
    return PreflightReport(ok=not failures, checks=tuple(checks), failures=tuple(failures))


def _check_manifest(
    config: SingleModelPreflightConfig,
    manifest: Mapping[str, object],
    checks: list[str],
    failures: list[str],
) -> set[int] | None:
    name = str(manifest.get("manifest_version") or manifest.get("name") or "")
    if name != config.expected_split_manifest:
        failures.append(f"split manifest drifted: expected {config.expected_split_manifest}, got {name}")
    else:
        checks.append(f"split manifest matches {config.expected_split_manifest}")

    split_record = manifest.get("splits", {}).get(config.split) if isinstance(
        manifest.get("splits"), Mapping
    ) else None
    if not isinstance(split_record, Mapping):
        failures.append(f"manifest missing split record for {config.split!r}")
        return None
    source_row_indices = split_record.get("source_row_indices")
    if not isinstance(source_row_indices, Sequence) or isinstance(source_row_indices, (str, bytes)):
        failures.append(f"manifest split {config.split!r} missing source_row_indices")
        return None
    indices = {int(i) for i in source_row_indices}
    if len(indices) != config.expected_row_count:
        failures.append(
            f"{config.split} split row count drifted: expected {config.expected_row_count}, "
            f"got {len(indices)}"
        )
    else:
        checks.append(f"{config.split} split count matches {config.expected_row_count}")
    return indices


def _check_records_match_manifest(
    config: SingleModelPreflightConfig,
    manifest_indices: set[int],
    checks: list[str],
    failures: list[str],
) -> None:
    records = load_records_for_split(config.split)
    idxs = [r.source_row_index for r in records]
    if len(set(idxs)) != len(idxs):
        failures.append(f"{config.split} records contain duplicate source_row_index")
    else:
        checks.append(f"{config.split} records have unique row ids")
    if set(idxs) != manifest_indices:
        failures.append(
            f"{config.split} records do not match manifest: "
            f"missing {len(manifest_indices - set(idxs))}, extra {len(set(idxs) - manifest_indices)}"
        )
    else:
        checks.append(f"{config.split} records == manifest locked set ({len(manifest_indices)} rows)")


def _check_subject_artifact(
    config: SingleModelPreflightConfig,
    manifest_indices: set[int],
    checks: list[str],
    failures: list[str],
) -> None:
    path = config.subject_artifact_path
    if not path.exists():
        failures.append(f"subject artifact missing: {path}")
        return
    checks.append(f"subject artifact exists: {path}")

    if config.subject_artifact_sha256 is not None:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != config.subject_artifact_sha256:
            failures.append(
                f"subject artifact hash mismatch: expected {config.subject_artifact_sha256}, got {actual}"
            )
        else:
            checks.append("subject artifact hash matches pin")

    try:
        rows = load_jsonl_rows(path)
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"subject artifact is not valid JSONL: {exc}")
        return

    rows_with_id = [r for r in rows if isinstance(r, Mapping) and r.get("source_row_index") is not None]
    ids = {int(r["source_row_index"]) for r in rows_with_id}
    if len(ids) != len(rows_with_id):
        failures.append("subject artifact has duplicate row ids")
    else:
        checks.append("subject artifact has unique row ids")
    if ids != manifest_indices:
        failures.append(
            f"subject artifact coverage drifted: missing {len(manifest_indices - ids)}, "
            f"extra {len(ids - manifest_indices)}"
        )
    else:
        checks.append(f"subject artifact covers the locked set ({len(manifest_indices)} rows)")

    if config.require_v0_reference:
        missing_v0 = [r for r in rows_with_id if not r.get("v0_reference")]
        if missing_v0:
            failures.append(f"subject artifact missing v0_reference on {len(missing_v0)} rows")
        else:
            checks.append("subject artifact carries v0_reference on every row")


def _check_outputs_absent(
    paths: Sequence[Path],
    checks: list[str],
    failures: list[str],
) -> None:
    for path in paths:
        if path.exists():
            failures.append(f"candidate output already exists before launch: {path}")
        else:
            checks.append(f"candidate output absent: {path}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Single-model reused-subject frozen-test integrity preflight."
    )
    parser.add_argument("--split", default="test")
    parser.add_argument("--subject-artifact", type=Path, default=DEFAULT_SUBJECT_ARTIFACT)
    parser.add_argument("--subject-sha256", default=None)
    parser.add_argument("--no-require-v0-reference", action="store_true")
    parser.add_argument("--output", type=Path, action="append", default=[],
                        help="candidate output path that must be absent (repeatable).")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    config = SingleModelPreflightConfig(
        split=args.split,
        subject_artifact_path=args.subject_artifact,
        subject_artifact_sha256=args.subject_sha256,
        require_v0_reference=not args.no_require_v0_reference,
        outputs_must_be_absent=tuple(args.output),
    )
    report = run_single_model_preflight(config)
    if args.json:
        print(json.dumps(report.to_json_record(), indent=2, sort_keys=True))
    else:
        for check in report.checks:
            print(f"OK: {check}")
        for failure in report.failures:
            print(f"FAIL: {failure}")
    raise SystemExit(0 if report.ok else 1)


if __name__ == "__main__":
    main()
