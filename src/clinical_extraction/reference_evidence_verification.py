"""Executable no-call verification for retained architecture reference cells."""

from __future__ import annotations

import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.evidence_replay import (
    replay_exectv2_deterministic,
    replay_exectv2_finding_assembly,
    replay_exectv2_saved_predictions,
    replay_gan_saved_comparisons,
)


class ReferenceEvidenceMismatch(AssertionError):
    """Raised when current no-call replay differs from a retained expectation."""


def verify_reference_cells(
    manifest: Mapping[str, Any], *, repo_root: Path
) -> dict[str, dict[str, int | float]]:
    """Replay and verify every reference cell without invoking an LLM."""

    cells = manifest.get("reference_cells")
    if not isinstance(cells, list):
        raise ValueError("reference_cells must be an array")
    results: dict[str, dict[str, int | float]] = {}
    for cell in cells:
        if not isinstance(cell, Mapping):
            raise ValueError("reference cell must be an object")
        record_id = str(cell.get("id", ""))
        verification = cell.get("verification")
        if not isinstance(verification, Mapping):
            raise ValueError(f"verification in {record_id} must be an object")
        actual = _run_replay(verification, repo_root=repo_root)
        expected = verification.get("expected")
        if not isinstance(expected, Mapping):
            raise ValueError(f"verification.expected in {record_id} must be an object")
        assert_expected_metrics(record_id, actual=actual, expected=expected)
        results[record_id] = actual
    return results


def assert_expected_metrics(
    record_id: str,
    *,
    actual: Mapping[str, int | float],
    expected: Mapping[str, Any],
) -> None:
    """Raise a readable error for a missing or changed replay metric."""

    mismatches: list[str] = []
    for metric, expected_value in expected.items():
        actual_value = actual.get(metric)
        if actual_value is None or not _equal_number(actual_value, expected_value):
            mismatches.append(f"{metric}: expected {expected_value!r}, observed {actual_value!r}")
    if mismatches:
        raise ReferenceEvidenceMismatch(f"{record_id}: " + "; ".join(mismatches))


def _run_replay(verification: Mapping[str, Any], *, repo_root: Path) -> dict[str, int | float]:
    replay = verification.get("replay")
    inputs = verification.get("inputs")
    if not isinstance(inputs, Mapping):
        raise ValueError("verification.inputs must be an object")
    if replay == "exectv2_deterministic":
        return replay_exectv2_deterministic(split=str(inputs["split"]))
    if replay == "exectv2_saved_predictions":
        return replay_exectv2_saved_predictions(
            repo_root / str(inputs["path"]), split=str(inputs["split"])
        )
    if replay == "exectv2_finding_assembly":
        return replay_exectv2_finding_assembly(repo_root / str(inputs["path"]))
    if replay == "gan_saved_comparisons":
        return replay_gan_saved_comparisons(repo_root / str(inputs["path"]))
    raise ValueError(f"unsupported retained evidence replay: {replay}")


def _equal_number(actual: int | float, expected: Any) -> bool:
    if not isinstance(expected, (int, float)) or isinstance(expected, bool):
        return False
    if isinstance(actual, int) and isinstance(expected, int):
        return actual == expected
    return math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=1e-9)
