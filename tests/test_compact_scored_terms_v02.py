"""Source-review regressions for scored populations, not literal wording."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    compact_scored_terms_v02 as terms,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v06 as scorer,
)


def finding(label: str, restriction: str | None, kind: str = "seizure_free") -> dict:
    return {"event": {"scope": "named", "label": label},
            "measurement": {"kind": kind}, "restriction": restriction}


def test_distinct_broad_event_populations_and_standard_aliases() -> None:
    assert terms.event_types("convulsion") == terms.event_types("convulsive seizure")
    assert terms.event_types("collapses with limb-jerking") == terms.event_types(
        "convulsive events"
    )
    assert terms.event_types("jerks") != terms.event_types("staring spells")
    assert terms.event_types("status events") == ("status_epilepticus",)
    assert terms.event_types("brief nocturnal episodes") == ()


def test_absence_scope_cannot_be_broadened() -> None:
    assert terms.restriction_key(finding("myoclonic jerks", "on waking")) == ("on_waking",)
    assert terms.restriction_key(finding("myoclonic jerks on waking", None)) == (
        "on_waking",
    )
    assert terms.restriction_key(finding("myoclonic jerks", None)) == ()
    assert terms.restriction_key(finding("myoclonic jerks", "on waking", "rate")) == ()
    assert terms.restriction_key(finding("clear-cut events", None)) == (
        "definite_events_only",
    )
    assert terms.restriction_key(finding("clusters", "requiring emergency care")) == (
        "requiring_emergency_care",
    )
    assert terms.restriction_key(finding("seizures", "off ASMs")) == ()


def test_rate_condition_and_event_context_are_separate() -> None:
    assert terms.restriction_key(finding("seizures", "on workdays", "rate")) == (
        "workdays_only",
    )
    assert terms.restriction_key(finding("seizures", "on the hot line", "rate")) == (
        "during_high_heat_work",
    )
    assert terms.restriction_key(finding("seizures", "brief periods", "rate")) == (
        "intermittent_peak",
    )
    assert terms.restriction_key(
        finding("seizure", "after a night shift", "last_event")
    ) == ()


def test_whole_claim_keeps_conditional_rate_and_waking_absence() -> None:
    def claim(label: str, kind: str, restriction: str | None) -> dict:
        measurement = (
            {"kind": "rate", "quantity": {"kind": "number", "value": 2},
             "per": {"kind": "number", "value": 1, "unit": "day"}}
            if kind == "rate"
            else {"kind": "seizure_free", "duration": {"kind": "number", "value": 1,
                                                      "unit": "month"}}
        )
        return {"event": {"scope": "named", "label": label},
                "measurement": measurement,
                "counted_unit": "individual_seizure" if kind == "rate" else "not_applicable",
                "status": "stated", "time": {"phase": "ongoing", "source": "this month"},
                "restriction": restriction, "evidence": ["source quotation"]}

    note = "source quotation"
    work_rate = claim("seizures", "rate", "on the hot line")
    generic_rate = claim("seizures", "rate", None)
    assert "restriction" in scorer.attribute_diffs(generic_rate, work_rate, note)
    waking_absence = claim("myoclonic jerks", "seizure_free", "on waking")
    generic_absence = claim("myoclonic jerks", "seizure_free", None)
    assert "restriction" in scorer.attribute_diffs(generic_absence, waking_absence, note)
    labelled_absence = claim("myoclonic jerks on waking", "seizure_free", None)
    assert scorer.attribute_diffs(labelled_absence, waking_absence, note) == []
