#!/usr/bin/env python3
"""Write the exhaustive post-candidate ExECT dev140 residual ownership ledger."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Literal

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
OUT_DIR = ROOT / "experiments/exectv2_encode_rule_development_20260821"
SOURCE = OUT_DIR / "residual_family_errors.jsonl"
Owner = Literal["encode", "extract", "select_revision", "scorer_gold", "unresolved"]

# Per-row judgments were made after inspecting every residual raw mention,
# exact evidence span, candidate key, and gold key. Key-specific sets below are
# the cases where one row contains residuals owned by different components.
_RX_OWNER: dict[tuple[str, str], Owner] = {
    ("EA0026", "missing"): "extract",
    ("EA0038", "missing"): "select_revision",
    ("EA0047", "missing"): "scorer_gold",
    ("EA0068", "excess"): "select_revision",
    ("EA0075", "excess"): "select_revision",
    ("EA0102", "missing"): "scorer_gold",
    ("EA0104", "missing"): "scorer_gold",
    ("EA0117", "missing"): "extract",
    ("EA0121", "missing"): "scorer_gold",
    ("EA0146", "missing"): "scorer_gold",
    ("EA0146", "excess"): "scorer_gold",
    ("EA0149", "missing"): "extract",
    ("EA0158", "missing"): "select_revision",
    ("EA0182", "missing"): "scorer_gold",
}

_INV_OWNER: dict[tuple[str, str], Owner] = {
    ("EA0015", "excess"): "select_revision",
    ("EA0044", "missing"): "scorer_gold",
    ("EA0046", "missing"): "scorer_gold",
    ("EA0061", "missing"): "scorer_gold",
    ("EA0102", "missing"): "select_revision",
    ("EA0102", "excess"): "select_revision",
    ("EA0120", "excess"): "select_revision",
    ("EA0132", "missing"): "scorer_gold",
    ("EA0143", "excess"): "select_revision",
    ("EA0146", "missing"): "scorer_gold",
    ("EA0179", "missing"): "extract",
    ("EA0200", "missing"): "scorer_gold",
}

_SF_EXTRACT_MISSING = frozenset(
    {
        "EA0022",
        "EA0025",
        "EA0028",
        "EA0049",
        "EA0050",
        "EA0068",
        "EA0102",
        "EA0120",
        "EA0176",
        "EA0195",
    }
)
_SF_SCORER_UNITS = frozenset(
    {
        ("EA0008", "missing", "seizure'), 'unknown"),
        ("EA0011", "missing", "convulsive seizure"),
        ("EA0011", "missing", "focal to bilateral convulsive seizure"),
        ("EA0059", "missing", "seizure'), 'unknown"),
        ("EA0082", "missing", "absence'), 'unknown"),
        ("EA0087", "missing", "generalised tonic clonic seizure'), 'unknown"),
        ("EA0108", "missing", "seizure'), 'unknown"),
        ("EA0127", "missing", "seizure free"),
        ("EA0136", "missing", "seizure'), 'unknown"),
        ("EA0161", "missing", "generalised tonic clonic seizure'), 'unknown"),
        ("EA0168", "missing", "seizure free"),
        ("EA0178", "missing", "seizure'), 'unknown"),
        ("EA0182", "missing", "seizure'), 'seizure-free"),
        ("EA0182", "excess", "seizure'), 'active-rate"),
        ("EA0190", "missing", "seizure'), 'seizure-free"),
        ("EA0190", "excess", "seizure free"),
    }
)

_DX_SELECT_MISSING = frozenset(
    {
        ("EA0005", "tonic clonic"),
        ("EA0007", "focal epilepsy"),
        ("EA0018", "temporal lobe seizure"),
        ("EA0021", "tonic clonic"),
        ("EA0034", "occipital lobe epilepsy"),
        ("EA0035", "tonic clonic"),
        ("EA0038", "tonic clonic"),
        ("EA0054", ""),
        ("EA0057", "epileptic seizure"),
        ("EA0061", "parietal lobe epilepsy"),
        ("EA0079", ""),
        ("EA0107", "generalised seizure"),
        ("EA0108", ""),
        ("EA0109", "temporal lobe seizure"),
        ("EA0110", "focal seizure"),
        ("EA0111", "focal epilepsy"),
        ("EA0114", "temporal lobe onset seizure"),
        ("EA0116", ""),
        ("EA0121", "focal epilepsy"),
        ("EA0126", "focal seizure"),
        ("EA0135", "epileptic seizure"),
        ("EA0136", "generalised seizure"),
        ("EA0137", "epilepsy"),
        ("EA0141", "epileptic seizure"),
        ("EA0156", "absence seizure"),
        ("EA0164", "epileptic seizure"),
        ("EA0172", "focal epilepsy"),
        ("EA0175", "drug refractory"),
        ("EA0179", "epilepsy"),
        ("EA0183", "epilepsy"),
        ("EA0198", "epilepsy"),
    }
)
_DX_SCORER_UNITS = frozenset(
    {
        ("EA0123", "missing", "generalised"),
        ("EA0128", "missing", "generalised"),
        ("EA0143", "missing", "focal"),
        ("EA0143", "excess", "focal seizures with altered awareness"),
        ("EA0150", "missing", "secondary"),
        ("EA0182", "missing", "temporal"),
        ("EA0182", "excess", "temporal lobe epilepsy"),
        ("EA0183", "missing", "generalised"),
        ("EA0189", "missing", "epileptic"),
        ("EA0189", "excess", "single seizure"),
        ("EA0190", "missing", "focal')"),
        ("EA0195", "missing", "generalised"),
        ("EA0195", "missing", "symptomatic"),
        ("EA0195", "excess", "symptomatic epilepsy"),
        ("EA0195", "excess", "tonic clonic"),
    }
)
_DX_SCORER_ALL = frozenset({"EA0188"})


def _contains(key: str, needle: str) -> bool:
    return not needle or needle in key


def _owner(
    letter_id: str,
    family: str,
    direction: Literal["missing", "excess"],
    key: str,
) -> Owner:
    if family == "Prescription":
        return _RX_OWNER[(letter_id, direction)]
    if family == "Investigations":
        return _INV_OWNER[(letter_id, direction)]
    if family == "SeizureFrequency":
        if any(
            row_id == letter_id and row_direction == direction and needle in key
            for row_id, row_direction, needle in _SF_SCORER_UNITS
        ):
            return "scorer_gold"
        if direction == "missing" and letter_id in _SF_EXTRACT_MISSING:
            return "extract"
        return "select_revision"
    if family == "Diagnosis":
        if letter_id in _DX_SCORER_ALL or any(
            row_id == letter_id and row_direction == direction and needle in key
            for row_id, row_direction, needle in _DX_SCORER_UNITS
        ):
            return "scorer_gold"
        if direction == "excess":
            return "select_revision"
        if any(
            row_id == letter_id and _contains(key, needle)
            for row_id, needle in _DX_SELECT_MISSING
        ):
            return "select_revision"
        return "extract"
    raise KeyError(f"unexpected family: {family}")


def _reason(owner: Owner, family: str, direction: str) -> str:
    if owner == "extract":
        return "Required fact or attribute is absent from the saved raw extracted mentions."
    if owner == "select_revision":
        return (
            "Needs add/split/dedupe, temporal or ownership resolution, or a semantic "
            f"{direction} decision; same-fact encode must not perform it."
        )
    if owner == "scorer_gold":
        return (
            "Residual is driven by scorer behavior, gold multiplicity, a fragment/altitude "
            f"convention, or a source-gold conflict in {family}."
        )
    if owner == "encode":
        return "A safe same-fact rendering repair remains."
    return "Evidence does not support a stable ownership decision."


def main() -> None:
    residuals = load_jsonl_rows(SOURCE)
    ledger: list[dict[str, object]] = []
    owner_counts: Counter[str] = Counter()
    family_owner_counts: Counter[str] = Counter()
    accounted_units = 0
    residual_directions: tuple[
        tuple[Literal["missing", "excess"], str], ...
    ] = (("missing", "missing_keys"), ("excess", "excess_keys"))
    for row in residuals:
        family = str(row["family"])
        letter_id = str(row["letter_id"])
        for direction, field in residual_directions:
            for unit in row.get(field, []):
                key = str(unit["key"])
                count = int(unit["count"])
                owner = _owner(letter_id, family, direction, key)
                accounted_units += count
                owner_counts[owner] += count
                family_owner_counts[f"{family}:{owner}"] += count
                ledger.append(
                    {
                        "schema_version": "exectv2.encode_residual_unit.dev140.v1",
                        "dataset": "ExECTv2",
                        "split": "dev140",
                        "row_policy": "development_review_permitted",
                        "letter_id": letter_id,
                        "family": family,
                        "direction": direction,
                        "key": key,
                        "count": count,
                        "first_failure_owner": owner,
                        "reason": _reason(owner, family, direction),
                        "candidate_mentions": row.get("candidate_mentions", []),
                        "candidate_evidence_status": row.get(
                            "candidate_evidence_status", {}
                        ),
                    }
                )

    expected_units = sum(
        int(row["candidate_counts"]["fn"]) + int(row["candidate_counts"]["fp"])
        for row in residuals
    )
    if accounted_units != expected_units:
        raise RuntimeError(
            f"residual accounting mismatch: {accounted_units=} {expected_units=}"
        )
    summary = {
        "schema_version": "exectv2.encode_residual_classification.dev140.v1",
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "development_review_permitted",
        "holdout_policy": "test60_not_loaded_or_inspected",
        "residual_letter_family_pairs": len(residuals),
        "residual_units": expected_units,
        "accounted_units": accounted_units,
        "owner_counts": dict(owner_counts),
        "family_owner_counts": dict(family_owner_counts),
        "remaining_safe_encode_units": owner_counts["encode"],
        "unresolved_units": owner_counts["unresolved"],
        "classification_policy": (
            "Row-level inspection of saved raw mentions, exact evidence, candidate "
            "keys, and gold keys after freezing the portable encode candidate."
        ),
    }
    write_jsonl_rows(ledger, OUT_DIR / "residual_classifications.jsonl")
    (OUT_DIR / "residual_classification_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
