"""One-call contract: prompt identity, strict parsing and the lenient findings score."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.one_call import (
    analysis,
    findings_score,
    parse,
    prompts,
)

# Rendered r4 answer-only request scored 658/750 Purist on dev750 (September 2026).
R4_MINIMAL_SHA256 = "902bf3e2523420990f95871ccdccd18d971048ead265d5ab34b57b2621bd99a4"


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    ).hexdigest()


def _wrap(payload: Any) -> str:
    body = payload if isinstance(payload, str) else json.dumps(payload)
    return f"[[ ## structured_json ## ]]\n{body}\n[[ ## completed ## ]]"


def _finding(evidence: str, measurement: dict[str, Any], **extra: Any) -> dict[str, Any]:
    kind = measurement["kind"]
    unit = (
        "not_applicable"
        if kind in ("seizure_free", "last_event", "median_interval")
        else ("cluster" if kind == "cluster" else "individual_seizure")
    )
    return {
        "event": {"scope": "unspecified", "label": "seizures"},
        "counted_unit": unit,
        "status": "stated",
        "measurement": measurement,
        "time": {"phase": "ongoing"},
        "evidence": [evidence],
        **extra,
    }


def _rate(count: int, per: float, unit: str) -> dict[str, Any]:
    return {
        "kind": "rate",
        "quantity": {"kind": "number", "value": count},
        "per": {"kind": "number", "value": per, "unit": unit},
    }


def test_minimal_is_the_scored_r4_request() -> None:
    assert _sha(prompts.messages("<NOTE_TEXT>", "minimal")) == R4_MINIMAL_SHA256


def test_conditions_differ_only_in_output_contract() -> None:
    minimal = prompts.payload("A note.", "minimal")
    expanded = prompts.payload("A note.", "expanded")
    differing = {k for k in minimal.keys() | expanded.keys() if minimal.get(k) != expanded.get(k)}
    assert differing == {"output_schema", "schema_instructions"}
    shared = len(prompts.SHARED_SCHEMA_INSTRUCTIONS)
    assert minimal["schema_instructions"][:shared] == expanded["schema_instructions"][:shared]
    assert expanded["output_schema"] == prompts.EXPANDED_SCHEMA


def test_expanded_response_with_current_and_historical_findings_is_usable() -> None:
    note = (
        "Previously she had one seizure per day. Now she has two focal seizures per month. "
        "No tonic-clonic seizures since March 2019."
    )
    response = {
        "answer": {
            "label": "2 per month",
            "evidence": "Now she has two focal seizures per month.",
            "claim_indices": [1],
        },
        "findings": [
            {
                **_finding("Previously she had one seizure per day.", _rate(1, 1, "day")),
                "time": {"phase": "superseded", "source": "Previously"},
            },
            {
                **_finding("two focal seizures per month", _rate(2, 1, "month")),
                "event": {"scope": "named", "label": "focal seizures"},
            },
            {
                **_finding(
                    "No tonic-clonic seizures since March 2019",
                    {"kind": "seizure_free", "since": "March 2019"},
                ),
                "event": {"scope": "named", "label": "tonic-clonic seizures"},
            },
        ],
    }
    result = parse.inspect(_wrap(response), "stop", note, "expanded")
    assert result["failure"] is None
    assert result["exact_quotes"] == result["quote_slots"] == 4
    assert len(result["findings"]) == 3


@pytest.mark.parametrize(
    ("content", "finish", "failure"),
    [
        (None, "stop", "no_response"),
        ("partial", "length", "truncation"),
        ('{"answer": {}}', "stop", "invalid_envelope"),
        (_wrap("{not json"), "stop", "invalid_syntax"),
        (
            _wrap({"answer": {"label": "4 per fortnight", "evidence": "x"}}),
            "stop",
            "invalid_target_label",
        ),
        (
            _wrap({"answer": {"label": "unknown", "evidence": None}}),
            "stop",
            "absent_required_evidence",
        ),
        (
            _wrap({"answer": {"label": "unknown", "evidence": "x"}, "findings": []}),
            "stop",
            "invalid_schema",
        ),
    ],
)
def test_minimal_failures_are_classified_without_repair(
    content: str | None, finish: str, failure: str
) -> None:
    assert parse.inspect(content, finish, "x", "minimal")["failure"] == failure


def test_invalid_findings_fail_the_record_but_not_the_declared_answer() -> None:
    note = "She has two seizures per month."
    answer = {"label": "2 per month", "evidence": note, "claim_indices": [3]}
    finding = _finding(note, _rate(2, 1, "month"))
    result = parse.inspect(
        _wrap({"answer": answer, "findings": [finding]}), "stop", note, "expanded"
    )
    assert result["failure"] == "invalid_schema"
    assert result["answer_failure"] is None
    no_reference = {
        "label": "no seizure frequency reference",
        "evidence": None,
        "claim_indices": [],
    }
    result = parse.inspect(
        _wrap({"answer": no_reference, "findings": [finding]}), "stop", note, "expanded"
    )
    assert result["failure"] == "invalid_schema"


NOTE = (
    "Seizures occur every 6 days over the past two months. "
    "Seizure-free for about 5 months last year. "
    "Seizures happen about 4 times a week at present."
)


def _reference(*findings: dict[str, Any], tier: str = "core") -> list[dict[str, Any]]:
    return [{"tier": tier, "origin": f"f{i}", **f} for i, f in enumerate(findings)]


def _score(reference: list[dict[str, Any]], predicted: list[dict[str, Any]] | None) -> Any:
    letters = [
        {"source_row_index": 1, "note": NOTE, "reference": reference, "predicted": predicted}
    ]
    return findings_score.score(letters)[0]


def test_lenient_match_ignores_wording_window_and_label() -> None:
    reference = _reference(
        {
            **_finding("Seizures occur every 6 days over the past two months.", _rate(1, 6, "day")),
            "time": {"phase": "ongoing", "source": "over the past two months"},
        }
    )
    predicted = [
        {
            **_finding("every 6 days", _rate(1, 1, "week")),
            "event": {"scope": "named", "label": "focal aware seizures"},
        }
    ]
    summary = _score(reference, predicted)
    assert summary["precision"] == summary["recall_core"] == 1.0
    assert summary["matched_pair_attribute_agreement"]["scope"] == 0.0


def test_lenient_match_requires_same_band_and_measurement_family() -> None:
    reference = _reference(_finding("every 6 days", _rate(1, 6, "day")))
    assert _score(reference, [_finding("every 6 days", _rate(1, 2, "month"))])["precision"] == 0.0
    qualitative = _finding("every 6 days", {"kind": "qualitative", "level": "frequent"})
    assert _score(reference, [qualitative])["precision"] == 0.0


def test_seizure_free_durations_are_not_compared() -> None:
    free = {"kind": "seizure_free", "duration": {"kind": "number", "value": 5, "unit": "month"}}
    other = {"kind": "seizure_free", "duration": {"kind": "number", "value": 1, "unit": "year"}}
    reference = _reference(_finding("Seizure-free for about 5 months", free))
    assert _score(reference, [_finding("about 5 months last year", other)])["recall_core"] == 1.0


def test_matching_is_one_to_one_and_fills_core_first() -> None:
    evidence = "Seizures happen about 4 times a week at present."
    core = _reference(_finding(evidence, _rate(4, 1, "week")))
    supporting = _reference(_finding(evidence, _rate(4, 1, "week")), tier="supporting")
    summary = _score(core + supporting, [_finding(evidence, _rate(4, 1, "week"))])
    assert summary["recall_core"] == 1.0
    assert summary["recall_all"] == 0.5
    duplicate = [_finding(evidence, _rate(4, 1, "week"))] * 2
    assert _score(core, duplicate)["precision"] == 0.5


def test_unusable_response_counts_every_reference_finding_as_missed() -> None:
    summary = _score(_reference(_finding("every 6 days", _rate(1, 6, "day"))), None)
    assert summary["usable_responses"] == 0
    assert summary["recall_core"] == 0.0
    assert summary["precision"] is None


def test_paired_difference_keeps_every_letter() -> None:
    result = analysis.paired([True, True, False, True], [True, False, False, True])
    assert result["expanded_minus_minimal"] == 0.25
    assert (result["expanded_wins"], result["minimal_wins"], result["ties"]) == (1, 0, 3)
