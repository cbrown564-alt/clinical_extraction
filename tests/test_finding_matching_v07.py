"""Guide v0.7 finding matching: whole-match rule, one-to-one assignment and accounting."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as fm,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8

NOTE = (
    "She has a generalised tonic-clonic seizure every four to six weeks. "
    "Absences occur most days. She has been seizure-free since March."
)


def finding(
    fid: str, label: str, measurement: dict[str, Any], evidence: str, **extra: Any
) -> dict[str, Any]:
    return {
        "id": fid,
        "event": {"type": label, "scope": r8.derive_scope(label), "seizure_status": "stated"},
        "measurement": measurement,
        "timing": "current",
        "evidence": evidence,
        **extra,
    }


RATE = {
    "type": "rate",
    "count": {"type": "number", "value": 1},
    "per": {"type": "range", "lower": 4, "upper": 6, "unit": "week"},
}
REFERENCE = [
    finding("f1", "generalised tonic-clonic seizure", RATE, NOTE.split(". ")[0] + "."),
    finding(
        "f2",
        "Absences",
        {"type": "qualitative", "frequency": "frequent"},
        "Absences occur most days.",
    ),
    finding(
        "f3",
        "seizure",
        {"type": "seizure_free", "since": {"time": "March", "form": "calendar"}},
        "She has been seizure-free since March.",
    ),
]


def test_equivalent_label_overlapping_evidence_and_condition_ignored_match() -> None:
    pred = [
        finding(
            "p1",
            "generalised tonic–clonic seizures",
            RATE,
            "every four to six weeks",
            condition="x",
        ),
        finding(
            "p2", "absence seizures", {"type": "qualitative", "frequency": "frequent"}, "most days"
        ),
        finding(
            "p3",
            "events",
            {"type": "seizure_free", "since": {"time": "since March", "form": "relative"}},
            "seizure-free since March",
        ),
    ]
    result = fm.score_letter(NOTE, REFERENCE, pred)
    assert (result["tp"], result["fp"], result["fn"]) == (3, 0, 0)


def test_value_timing_and_type_differences_are_fp_and_fn() -> None:
    wrong_rate = {**RATE, "per": {"type": "number", "value": 4, "unit": "week"}}
    pred = [
        finding("p1", "generalised tonic-clonic seizure", wrong_rate, "every four to six weeks"),
        finding(
            "p2",
            "Absences",
            {"type": "qualitative", "frequency": "frequent"},
            "most days",
            timing="historical",
        ),
        finding(
            "p3",
            "seizure",
            {"type": "qualitative", "frequency": "unknown"},
            "seizure-free since March",
        ),
    ]
    result = fm.score_letter(NOTE, REFERENCE, pred)
    assert (result["tp"], result["fp"], result["fn"]) == (0, 3, 3)
    diffs = {d["prediction"]: d["closest_diffs"] for d in result["unmatched_diagnostics"]}
    assert diffs["p1"] == ["measurement_value"]
    assert diffs["p2"] == ["timing"]
    assert diffs["p3"] == ["measurement_type"]

    # Vague absence durations stay source text and cannot match invented numbers.
    vague = {
        "type": "seizure_free",
        "duration": {"type": "qualitative", "quantity": "several months"},
    }
    assert r8.SeizureFree.model_validate(vague).model_dump(exclude_none=True) == vague
    assert fm.measurement_equal(vague, vague)
    for duration in (
        {"type": "number", "value": 3, "unit": "month"},
        {"type": "qualitative", "quantity": "several weeks"},
    ):
        assert not fm.measurement_equal(vague, {"type": "seizure_free", "duration": duration})

    # A verbatim rate interval is not an invented number/range or another time unit.
    rate = {
        "type": "rate",
        "count": {"type": "number", "value": 1},
        "per": {"type": "qualitative", "quantity": "few weeks"},
    }
    cluster = {"type": "cluster", "rate": {k: v for k, v in rate.items() if k != "type"}}
    assert r8.Rate.model_validate(rate).model_dump(exclude_none=True) == rate
    assert r8.Cluster.model_validate(cluster).model_dump(exclude_none=True) == cluster
    assert fm.measurement_equal(rate, rate)
    assert fm.measurement_equal(cluster, cluster)
    for denominator in (
        {"type": "number", "value": 3, "unit": "week"},
        {"type": "range", "lower": 2, "upper": 3, "unit": "week"},
        {"type": "qualitative", "quantity": "few months"},
    ):
        assert not fm.measurement_equal(rate, {**rate, "per": denominator})
        assert not fm.measurement_equal(
            cluster, {"type": "cluster", "rate": {**cluster["rate"], "per": denominator}}
        )


def test_duplicate_prediction_matches_once_and_specific_label_does_not_match_generic() -> None:
    pred = [
        finding("p1", "generalised tonic-clonic seizure", RATE, "every four to six weeks"),
        finding("p2", "generalised tonic-clonic seizure", RATE, "every four to six weeks"),
        finding(
            "p3",
            "focal seizures",
            {"type": "seizure_free", "since": {"time": "March", "form": "calendar"}},
            "seizure-free since March",
        ),
    ]
    result = fm.score_letter(NOTE, REFERENCE, pred)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 2, 2)


def test_unusable_and_empty_accounting() -> None:
    unusable = fm.score_letter(NOTE, REFERENCE, None)
    assert (unusable["usable"], unusable["fn"], unusable["predicted"]) == (False, 3, None)
    empty_ok = fm.score_letter("No relevant text.", [], [])
    empty_fp = fm.score_letter(NOTE, [], [REFERENCE[0]])
    summary = fm.aggregate([unusable, empty_ok, empty_fp])
    assert summary["unusable_letters"] == 1
    assert summary["empty_reference_letters"] == 2
    assert summary["empty_state_correct"] == 1
    assert summary["exact_inventory"] == 1
    assert summary["precision"] == 0.0 and summary["recall"] == 0.0
    assert fm.aggregate([empty_ok])["precision"] == "not estimable"
