"""The scored dictionary keeps clinical types separate from source descriptors."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    compact_scored_terms_v01 as terms,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v05 as scorer,
)


def test_event_type_dictionary_on_source_reviewed_cases() -> None:
    assert terms.event_types("brief nocturnal episodes") == ()
    assert terms.event_types("brief absence episode") == ("absence",)
    assert terms.event_types("absence episode") == ("absence",)
    assert terms.event_types("clusters of drop attacks") == ("drop_attack",)
    assert terms.event_types("drop attacks") == ("drop_attack",)
    assert terms.event_types("generalised tonic–clonic seizures") == ("generalised_tonic_clonic",)
    assert terms.event_types("focal aware sensory episodes") == ("focal_preserved",)
    assert terms.event_types("focal impaired-awareness seizures") == ("focal_impaired",)
    assert terms.event_types("complex partial seizure") == ("focal_impaired",)
    assert terms.event_types(
        "focal aware sensory episodes progressing to focal impaired awareness seizures"
    ) == ("focal_preserved_to_impaired",)
    assert terms.event_types("tonic-clonic seizures with focal onset") == (
        "focal_to_bilateral_tonic_clonic",
    )
    assert terms.event_types("focal to bilateral tonic–clonic seizures") == (
        "focal_to_bilateral_tonic_clonic",
    )
    assert terms.event_types("brief absence-like spells") == ()
    assert terms.event_types("focal aware and focal impaired awareness seizures") == (
        "focal_impaired",
        "focal_preserved",
    )
    assert terms.event_types(
        "focal aware, focal impaired awareness, or focal to bilateral tonic-clonic seizures"
    ) == ("focal_impaired", "focal_preserved", "focal_to_bilateral_tonic_clonic")
    assert terms.event_key({"scope": "overall", "label": "focal epilepsy"}) == ("overall", ())


def test_restriction_codes_keep_reporting_scope_and_drop_duplicate_descriptors() -> None:
    finding = {
        "event": {"scope": "named", "label": "nocturnal episodes"},
        "restriction": "at night",
    }
    assert terms.restriction_key(finding) == ("during_sleep",)
    finding["event"]["label"] = "events"
    assert terms.restriction_key(finding) == ("during_sleep",)
    finding["restriction"] = None
    finding["event"]["label"] = "brief nocturnal episodes"
    assert terms.restriction_key(finding) == ("during_sleep",)
    finding["event"]["label"] = "events"
    finding["restriction"] = "after a night shift"
    assert terms.restriction_key(finding) == ()
    finding["restriction"] = (
        "device-detected convulsive activity, corroborated by personal event log"
    )
    assert terms.restriction_key(finding) == ("device_observed", "diary_recorded")
    finding["restriction"] = "witnessed event by manager"
    assert terms.restriction_key(finding) == ("witnessed",)
    finding["restriction"] = "longest seizure-free interval"
    assert terms.restriction_key(finding) == ("longest_seizure_free_gap",)
    finding["restriction"] = "outside the perimenstrual window (days -3 to +3)"
    assert terms.restriction_key(finding) == ("outside_menstrual_window",)
    finding["restriction"] = "within the 3 days prior to menses"
    assert terms.restriction_key(finding) == ("within_menstrual_window",)
    finding["restriction"] = "observed by partner"
    assert terms.restriction_key(finding) == ("witnessed",)
    finding["event"]["label"] = "reported or recognised seizure events"
    finding["restriction"] = (
        "episodes brought to attention by carers or bystanders, or events recognised "
        "as seizures by the patient"
    )
    assert terms.restriction_key(finding) == ("reported_or_recognised", "witnessed")
    finding["event"]["label"] = "events"
    finding["restriction"] = "on ambulatory EEG"
    assert terms.restriction_key(finding) == ("electrographic_only",)


def test_scorer_distinguishes_source_scope_and_material_population() -> None:
    def claim(scope: str, label: str, restriction: str | None = None) -> dict:
        return {
            "event": {"scope": scope, "label": label},
            "counted_unit": "individual_seizure",
            "status": "stated",
            "measurement": {"kind": "observed_count", "quantity": {"kind": "number", "value": 2}},
            "time": {"phase": "ongoing", "source": "this month"},
            "restriction": restriction,
            "evidence": ["two nocturnal events this month"],
        }

    note = "two nocturnal events this month"
    reference = claim("named", "brief nocturnal episodes", "at night")
    equivalent = claim("named", "nocturnal events")
    assert scorer.attribute_diffs(equivalent, reference, note) == []
    assert "restriction" in scorer.attribute_diffs(claim("named", "events"), reference, note)
    assert "event" in scorer.attribute_diffs(claim("overall", "seizures"), reference, note)
    reported = claim("overall", "reported or recognised events", "recognised by the patient")
    assert "restriction" in scorer.attribute_diffs(claim("overall", "seizures"), reported, note)
