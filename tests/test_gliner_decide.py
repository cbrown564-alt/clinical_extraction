"""Exploratory GLiNER2.5-Decide adaptation: split barrier and projection contract.

No model, torch or corpus access. Protects what would silently falsify a GLiNER
result: reading test450, a Pragmatic answer that disagrees with the native bands,
findings that the locked schema would reject, and unit conversion in normalisation.
"""

from __future__ import annotations

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.gliner import normalize, project, schema
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from scripts.benchmarks import gliner_decide

NOTE = (
    "Currently she has two to three focal seizures per month. Seizure-free for 14 months in 2019."
)


def test_runner_refuses_the_locked_test_split() -> None:
    for split in ("test", "test450"):
        with pytest.raises(ValueError):
            gliner_decide.records(split)


def test_answer_labels_cover_purist_and_pragmatic_follows_native_bands() -> None:
    assert sorted(schema.LABEL_TO_PURIST.values()) == sorted(project.PURIST_TO_PRAGMATIC)
    for per_month in (0, 0.05, 0.17, 0.5, 1.0, 1.05, 2, 4, 10, 40, 1000):
        assert project.PURIST_TO_PRAGMATIC[str(map_purist(per_month))] == str(
            map_pragmatic(per_month)
        )
    assert schema.schema_sha256("minimal") != schema.schema_sha256("expanded")


def test_projection_yields_schema_valid_findings_and_counts_drops() -> None:
    start = NOTE.index("two to three focal seizures per month")
    raw = {
        schema.ANSWER_TASK: {"label": "more than monthly but less than weekly", "confidence": 0.6},
        "entities": {
            schema.EVIDENCE_ENTITY: {
                "text": "two to three focal seizures per month",
                "start": start,
                "end": start + 37,
            }
        },
        schema.FINDING: [
            {
                "evidence": {"text": "two to three focal seizures per month"},
                "quantity": {"text": "two to three"},
                "per": {"text": "per month"},
                "kind": {"text": "rate"},
                "phase": {"text": "ongoing"},
            },
            {
                "evidence": {"text": "Seizure-free for 14 months"},
                "window": {"text": "14 months"},
                "kind": {"text": "seizure_free"},
            },
            {"evidence": {"text": "not in the note"}, "kind": {"text": "rate"}},
            {"evidence": {"text": "Currently"}, "kind": None},
        ],
    }
    answer = project.answer(raw, NOTE)
    assert answer["failure"] is None and answer["evidence_exact"]
    assert answer["categories"] == {
        "purist": "seizure_freq_more1mon_less1week",
        "pragmatic": "seizure_frequent",
    }
    findings, tally = project.findings(raw, NOTE)
    assert [f["measurement"] for f in findings] == [
        {
            "kind": "rate",
            "quantity": {"kind": "range", "lower": 2, "upper": 3},
            "per": {"kind": "number", "value": 1, "unit": "month"},
        },
        {"kind": "seizure_free", "duration": {"kind": "number", "value": 14, "unit": "month"}},
    ]
    assert findings[1]["counted_unit"] == "not_applicable"
    assert tally["dropped_no_evidence"] == 1 and tally["dropped_no_kind"] == 1
    assert project.claim_indices(answer["evidence_span"], findings, NOTE) == [0]
    missing = project.answer({schema.ANSWER_TASK: {"label": "daily or more"}}, NOTE)
    assert missing["failure"] == "absent_required_evidence"


@pytest.mark.parametrize(
    ("span", "expected"),
    [
        ("≤ four", {"kind": "bound", "relation": "at_most", "value": 4}),
        ("two or three", {"kind": "range", "lower": 2, "upper": 3}),
        ("several", {"kind": "verbatim", "text": "several"}),
    ],
)
def test_quantity_reads_written_values_only(span: str, expected: dict[str, object]) -> None:
    assert normalize.quantity(span) == expected


@pytest.mark.parametrize(
    ("span", "expected"),
    [
        ("per month", {"kind": "number", "value": 1, "unit": "month"}),
        ("every 4-6 weeks", {"kind": "range", "lower": 4, "upper": 6, "unit": "week"}),
        ("18 months", {"kind": "number", "value": 18, "unit": "month"}),
        ("few weeks", {"kind": "verbatim", "text": "few weeks"}),
        ("per day and per week", {"kind": "verbatim", "text": "per day and per week"}),
    ],
)
def test_duration_never_converts_units(span: str, expected: dict[str, object]) -> None:
    assert normalize.duration(span) == expected
