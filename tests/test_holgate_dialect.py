"""Holgate-dialect projection is an ablation scorer, not the living parser."""

from __future__ import annotations

import pytest

from clinical_extraction.paper.holgate_dialect import project_holgate_dialect_label
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)


@pytest.mark.parametrize(
    ("label", "kind", "expected"),
    (
        ("I do not know.", None, "unknown"),
        ("I do not know", None, "unknown"),
        ("I don't know", None, "unknown"),
        (None, "unknown", "unknown"),
        ("", "no_reference", "no seizure frequency reference"),
        ("seizure-free", None, "seizure free"),
        ("seizure_free", None, "seizure free"),
        ("seizure-free since August 2023", None, "seizure free"),
        ("0 seizures", None, "seizure free"),
        ("0 seizures per year", None, "seizure free"),
        ("2 seizures per month", None, "2 per month"),
        ("3 to 5 seizures per month", None, "3 to 5 per month"),
        ("1-2 seizures per month", None, "1 to 2 per month"),
        ("9/month", None, "9 per month"),
        ("1/day", None, "1 per day"),
        ("≤ 4/day", None, "4 per day"),
        ("2 per month", None, "2 per month"),
        ("unknown", None, "unknown"),
    ),
)
def test_holgate_dialect_maps_prompted_and_format_aliases(
    label: str | None, kind: str | None, expected: str
) -> None:
    projected = project_holgate_dialect_label(label, final_kind=kind)
    assert projected == expected
    record = label_to_frequency_record(projected)
    assert record.normalized_label in {expected, "seizure free"}


def test_holgate_dialect_leaves_unresolved_narrative_alone() -> None:
    text = (
        "Multiple seizure types: 1 generalized tonic-clonic seizure every 3 "
        "months, weekly absences"
    )
    assert project_holgate_dialect_label(text) == text
