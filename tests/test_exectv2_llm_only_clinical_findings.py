"""Tests for the ExECTv2 llm_only clinical-findings SF extractor."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_clinical_findings,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_clinical_findings import (
    ClinicalFindingRecord,
    EventFrameRecord,
    ExECTv2ClinicalFindingsFinalizerSignature,
    ExECTv2ClinicalFindingsSFSignature,
    ExECTv2ClinicalFindingsVerifierSignature,
    VerificationDecisionList,
    VerificationDecisionRecord,
    apply_verification_decisions,
    build_finalization_prompt_input,
    build_plan11_event_state_route,
    build_verification_prompt_input,
    parse_clinical_findings_json,
    parse_verification_decisions_json,
    project_finding_to_attributes,
    to_predicted_letters,
)
from tests.helpers.prompt_hygiene import FORBIDDEN_PHRASES, collect_signature_text

_NOTE = (
    "She has focal seizures with impaired awareness 2 to 3 times per month "
    "since her medication change. She has also been seizure free for 6 months "
    "following surgery. At her last clinic she reported a cluster of seizures."
)

_LETTER = ExectLetter(letter_id="CF001", note_text=_NOTE)


def test_clinical_findings_prompt_hygiene_no_internal_vocabulary() -> None:
    payload = llm_only_clinical_findings.build_prompt_input(_LETTER)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload]
    assert leaked == []


def test_clinical_findings_signature_hygiene_no_internal_vocabulary() -> None:
    text = collect_signature_text(ExECTv2ClinicalFindingsSFSignature)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
    assert leaked == []


def test_verifier_prompt_hygiene_no_internal_vocabulary() -> None:
    raw_findings = [
        ClinicalFindingRecord(
            text="events",
            evidence="events have been going on now for around 9 months",
            clinical_kind="other_frequency",
            frequency_statement_type="other_frequency",
            count="10",
            confidence="medium",
        )
    ]

    payload = build_verification_prompt_input(_LETTER, raw_findings)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload]
    assert leaked == []

    parsed = json.loads(payload)
    assert parsed["raw_findings"][0]["text"] == "events"
    assert parsed["letter_text"] == _NOTE
    assert "Optional clinical category" in parsed["decision_schema"]["target_status"]
    assert any("Several seizures since last clinic" in rule for rule in parsed["review_checks"])
    assert any("absence like seizures" in rule for rule in parsed["review_checks"])
    assert parsed["decision_examples"][0]["decision"]["action"] == "keep"
    assert parsed["decision_examples"][2]["decision"]["action"] == "remove"
    assert any("historical dated counts" in rule for rule in parsed["review_checks"])
    assert any("action should usually be remove" in rule for rule in parsed["review_checks"])
    assert any("epilepsy seems under control" in rule for rule in parsed["review_checks"])
    assert any("continues to get" in rule for rule in parsed["review_checks"])
    assert any("minor seizures" in rule for rule in parsed["review_checks"])
    assert any(
        "Last-event dates are target" in str(example) for example in parsed["decision_examples"]
    )
    assert any("Vague epilepsy control" in str(example) for example in parsed["decision_examples"])
    assert any(
        "approximately 15 seizures over 4 months" in str(example)
        for example in parsed["decision_examples"]
    )


def test_prompt_keeps_compact_historical_facts_distinct_from_current_control() -> None:
    payload = llm_only_clinical_findings.build_prompt_input(_LETTER)
    parsed = json.loads(payload)

    assert "event_frame_schema" in parsed
    assert any("Fill event_frames before findings" in rule for rule in parsed["clinical_rules"])
    assert any(
        "Every finding should correspond to one target event_frame" in rule
        for rule in parsed["clinical_rules"]
    )
    assert any(
        "Generalised tonic clonic seizure-last event July 2016" in str(example)
        for example in parsed["event_frame_examples"]
    )
    assert any(
        "He remains seizure free" in str(example)
        and '"include_as_finding": false' in json.dumps(example)
        for example in parsed["event_frame_examples"]
    )
    assert any(
        "without change in awareness" in str(example)
        and '"seizure_phrase": "focal seizures"' in json.dumps(example)
        for example in parsed["event_frame_examples"]
    )
    assert any(
        "does not replace historical compact-section" in rule for rule in parsed["clinical_rules"]
    )
    assert any("every week for 3 weeks" in rule for rule in parsed["clinical_rules"])
    assert any("older previous event" in rule for rule in parsed["clinical_rules"])
    assert any("frequency_change infrequent" in rule for rule in parsed["clinical_rules"])
    assert any("diagnostic episode description" in rule for rule in parsed["clinical_rules"])
    assert any("epilepsy seems under control" in rule for rule in parsed["clinical_rules"])
    assert any("bare current statement" in rule for rule in parsed["clinical_rules"])
    assert any("text seizures and count 0" in rule for rule in parsed["clinical_rules"])
    assert any("continues to get seizures" in rule for rule in parsed["clinical_rules"])
    assert any("minor seizures" in rule for rule in parsed["clinical_rules"])
    assert any(
        "2 generalised tonic clonic seizures 2018" in str(example)
        and "He remains seizure free" in str(example)
        for example in parsed["worked_examples"]
    )
    assert any(
        "cluster of seizures in August 2017" in str(example)
        for example in parsed["worked_examples"]
    )
    assert any(
        "The epilepsy seems to be under control" in str(example)
        for example in parsed["worked_examples"]
    )
    assert any(
        "has not had any further seizures" in str(example) for example in parsed["worked_examples"]
    )
    assert any(
        "He developed some minor seizures" in str(example) for example in parsed["worked_examples"]
    )


def test_verifier_signature_hygiene_no_internal_vocabulary() -> None:
    text = collect_signature_text(ExECTv2ClinicalFindingsVerifierSignature)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
    assert leaked == []


def test_verifier_prompt_includes_model_owned_event_frames() -> None:
    raw_findings = [
        ClinicalFindingRecord(
            text="seizures",
            evidence="two seizures per year",
            clinical_kind="frequency_rate",
            frequency_statement_type="background_rate",
            count="2",
            period_unit="year",
            confidence="high",
        )
    ]
    event_frames = [
        EventFrameRecord(
            event_id="e1",
            evidence="two seizures per year",
            seizure_phrase="seizures",
            target_status="target_epileptic_seizure_frequency",
            statement_family="background_rate",
            source_role="narrative",
            count="2",
            period_count="1",
            period_unit="year",
            finding_text="seizures",
            include_as_finding=True,
            rationale="Target seizure rate.",
        ),
        EventFrameRecord(
            event_id="e2",
            evidence="dizzy episodes twice a week",
            seizure_phrase="dizzy episodes",
            target_status="non_target_episode",
            statement_family="non_target",
            source_role="narrative",
            count="2",
            period_count="1",
            period_unit="week",
            include_as_finding=False,
            rationale="Non-target episodes.",
        ),
    ]

    payload = build_verification_prompt_input(_LETTER, raw_findings, event_frames)
    parsed = json.loads(payload)

    assert parsed["event_frames"][0]["event_id"] == "e1"
    assert parsed["event_frames"][1]["target_status"] == "non_target_episode"
    assert any(
        "Use event_frames as the model's first-pass clinical map" in rule
        for rule in parsed["review_checks"]
    )


def test_finalizer_prompt_hygiene_and_contract() -> None:
    raw_findings = [
        ClinicalFindingRecord(
            text="seizure free",
            evidence="The epilepsy seems to be under control on medication.",
            clinical_kind="frequency_change",
            frequency_statement_type="change_only",
            confidence="medium",
        )
    ]

    payload = build_finalization_prompt_input(_LETTER, raw_findings)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload]
    assert leaked == []

    parsed = json.loads(payload)
    assert parsed["raw_findings"][0]["text"] == "seizure free"
    assert "complete final model-owned findings list" in parsed["task"]
    assert any("not a list of decisions" in rule for rule in parsed["finalization_checks"])
    assert any("copy the entire raw finding" in rule for rule in parsed["finalization_checks"])
    assert any("Do not drop fields" in rule for rule in parsed["finalization_checks"])
    assert any(
        "has not had any further seizures" in str(example) for example in parsed["worked_examples"]
    )
    no_further = parsed["worked_examples"][0]["final_findings"][0]
    assert no_further["count_low"] is None
    assert no_further["time_relation"] is None
    assert no_further["frequency_change"] is None
    assert any(
        "approximately 15 seizures over 4 months" in str(example)
        for example in parsed["worked_examples"]
    )


def test_finalizer_signature_hygiene_no_internal_vocabulary() -> None:
    text = collect_signature_text(ExECTv2ClinicalFindingsFinalizerSignature)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
    assert leaked == []


def test_parse_clinical_findings_json_accepts_structured_fields() -> None:
    raw = json.dumps(
        {
            "event_frames": [
                {
                    "event_id": "e1",
                    "evidence": "focal seizures with impaired awareness 2 to 3 times per month",
                    "seizure_phrase": "focal seizures with impaired awareness",
                    "target_status": "target_epileptic_seizure_frequency",
                    "statement_family": "background_rate",
                    "source_role": "narrative",
                    "count_low": 2,
                    "count_high": 3,
                    "period_count": 1,
                    "period_unit": "month",
                    "finding_text": "focal seizures with impaired awareness",
                    "include_as_finding": True,
                    "rationale": "A current focal seizure rate is present.",
                }
            ],
            "findings": [
                {
                    "text": "focal seizures with impaired awareness",
                    "evidence": "focal seizures with impaired awareness 2 to 3 times per month",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "source_role": "narrative",
                    "count_low": "2",
                    "count_high": 3,
                    "period_count": 1,
                    "period_unit": "month",
                    "confidence": "high",
                }
            ],
        }
    )

    record, errors = parse_clinical_findings_json(raw)

    assert record is not None
    assert record.event_frames[0].event_id == "e1"
    assert record.event_frames[0].count_low == "2"
    assert record.event_frames[0].period_count == "1"
    assert record.findings[0].count_high == "3"
    assert record.findings[0].period_count == "1"
    assert record.findings[0].frequency_statement_type == "background_rate"
    assert record.findings[0].source_role == "narrative"
    assert any("coerced_field_value" in e for e in errors)


def test_parse_reports_and_ignores_model_supplied_projection_fields() -> None:
    raw = json.dumps(
        {
            "event_frames": [
                {
                    "event_id": "e1",
                    "evidence": "2 focal seizures per month",
                    "seizure_phrase": "focal seizures",
                    "CUI": "C999",
                    "Certainty": "5",
                }
            ],
            "findings": [
                {
                    "text": "focal seizures",
                    "evidence": "2 focal seizures per month",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "count": "2",
                    "period_count": "1",
                    "period_unit": "month",
                    "CUI": "C999",
                    "CUIPhrase": "wrong",
                    "Negation": "Affirmed",
                }
            ],
        }
    )

    record, errors = parse_clinical_findings_json(raw)

    assert record is not None
    assert not hasattr(record.findings[0], "CUI")
    assert any("event_frames[0] 'CUI'" in e for e in errors)
    assert any("findings[0] 'CUIPhrase'" in e for e in errors)


def test_parse_moves_statement_type_from_clinical_kind_when_misplaced() -> None:
    raw = json.dumps(
        {
            "findings": [
                {
                    "text": "absence like seizures",
                    "evidence": "absence like seizures 2018",
                    "clinical_kind": "calendar_occurrence_no_count",
                    "year": "2018",
                    "confidence": "medium",
                }
            ]
        }
    )

    record, errors = parse_clinical_findings_json(raw)

    assert record is not None
    finding = record.findings[0]
    assert finding.clinical_kind == "dated_count"
    assert finding.frequency_statement_type == "calendar_occurrence_no_count"
    assert any("coerced_statement_type_from_clinical_kind" in e for e in errors)


def test_parse_verification_decisions_json() -> None:
    raw = json.dumps(
        {
            "decisions": [
                {
                    "raw_index": 0,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": "target finding",
                },
                {
                    "raw_index": 1,
                    "target_status": "non_target_episode",
                    "action": "remove",
                    "rationale": "not epileptic",
                },
            ],
            "findings_to_add": [],
        }
    )

    record, errors = parse_verification_decisions_json(raw)

    assert record is not None
    assert errors == []
    assert record.decisions[0].action == "keep"
    assert record.decisions[0].target_status == "target_epileptic_seizure_frequency"
    assert record.decisions[1].action == "remove"
    assert record.decisions[1].target_status == "non_target_episode"


def test_parse_verification_decisions_accepts_python_literal_quote_drift() -> None:
    raw = (
        "{'decisions': [{'raw_index': 0, "
        "'target_status': 'target_epileptic_seizure_frequency', "
        "'action': 'keep', 'rationale': 'target finding'}], "
        "'findings_to_add': []}"
    )

    record, errors = parse_verification_decisions_json(raw)

    assert record is not None
    assert errors == ["coerced_python_literal_to_json"]
    assert record.decisions[0].action == "keep"


def test_parse_verification_decisions_drops_event_frame_shaped_additions() -> None:
    raw = json.dumps(
        {
            "decisions": [
                {
                    "raw_index": 0,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": "target finding",
                }
            ],
            "findings_to_add": [
                {
                    "evidence": "She has had seizures since the age of 13.",
                    "seizure_phrase": "seizures",
                    "target_status": "history_context_only",
                    "statement_family": "calendar_count",
                    "include_as_finding": True,
                    "rationale": "Event-frame shaped object, not a finding.",
                }
            ],
        }
    )

    record, errors = parse_verification_decisions_json(raw)

    assert record is not None
    assert record.findings_to_add == []
    assert errors == ["dropped_invalid_findings_to_add_record: index=0 missing text/clinical_kind"]


def test_parse_clinical_findings_accepts_python_literal_quote_drift() -> None:
    raw = (
        "{'findings': [{'text': 'seizures', "
        "'evidence': 'two seizures per year', "
        "'clinical_kind': 'frequency_rate', "
        "'frequency_statement_type': 'background_rate', "
        "'count': '2', 'period_unit': 'year', "
        "'confidence': 'high'}]}"
    )

    record, errors = parse_clinical_findings_json(raw)

    assert record is not None
    assert errors == ["coerced_python_literal_to_json"]
    assert record.findings[0].text == "seizures"


def test_parse_clinical_findings_tolerates_audit_only_event_family_names() -> None:
    raw = json.dumps(
        {
            "event_frames": [
                {
                    "event_id": "e1",
                    "evidence": "both his sons are well and have not had seizures",
                    "seizure_phrase": "seizures",
                    "target_status": "non_target_episode",
                    "statement_family": "family_history",
                    "source_role": "narrative",
                    "include_as_finding": False,
                    "rationale": "Family history is not scored.",
                }
            ],
            "findings": [],
        }
    )

    record, errors = parse_clinical_findings_json(raw)

    assert record is not None
    assert errors == []
    assert record.event_frames[0].statement_family == "family_history"


def test_apply_verification_revise_preserves_raw_numeric_fields() -> None:
    raw_findings = [
        ClinicalFindingRecord(
            text="focal seizures without change in awareness",
            evidence="In March she had 2 to 3 of her focal seizures without change in awareness",
            clinical_kind="dated_count",
            frequency_statement_type="calendar_count",
            count_low="2",
            count_high="3",
            month="March",
            time_relation="during",
            confidence="high",
        )
    ]
    decisions = VerificationDecisionList(
        decisions=[
            VerificationDecisionRecord(
                raw_index=0,
                target_status="target_epileptic_seizure_frequency",
                action="revise",
                text="focal seizures",
                rationale="The phrase without awareness describes this event subtype.",
            )
        ]
    )

    final, warnings = apply_verification_decisions(raw_findings, decisions)

    assert warnings == []
    assert final[0].text == "focal seizures"
    assert final[0].count_low == "2"
    assert final[0].count_high == "3"
    assert final[0].month == "March"
    assert final[0].time_relation == "during"


def test_apply_verification_revise_applies_explicit_model_field_corrections() -> None:
    raw_findings = [
        ClinicalFindingRecord(
            text="generalised tonic clonic seizure",
            evidence="had a generalised tonic clonic seizure",
            clinical_kind="dated_count",
            frequency_statement_type="calendar_count",
            count="1",
            confidence="high",
        )
    ]
    decisions = VerificationDecisionList(
        decisions=[
            VerificationDecisionRecord(
                raw_index=0,
                target_status="target_epileptic_seizure_frequency",
                action="revise",
                evidence="last week and had a generalised tonic clonic seizure",
                time_relation="during",
                point_in_time="last week",
                rationale="The event happened last week.",
            )
        ]
    )

    final, warnings = apply_verification_decisions(raw_findings, decisions)

    assert warnings == []
    assert final[0].evidence == "last week and had a generalised tonic clonic seizure"
    assert final[0].time_relation == "during"
    assert final[0].point_in_time == "last week"
    assert final[0].count == "1"


def test_apply_verification_remove_and_add() -> None:
    raw_findings = [
        ClinicalFindingRecord(
            text="events",
            evidence="events have been going on now for around 9 months",
            clinical_kind="other_frequency",
            frequency_statement_type="other_frequency",
            count="10",
            confidence="medium",
        )
    ]
    decisions = VerificationDecisionList(
        decisions=[
            VerificationDecisionRecord(
                raw_index=0,
                target_status="non_target_episode",
                action="remove",
                rationale="Blackout events are not epileptic seizure frequency.",
            )
        ],
        findings_to_add=[
            ClinicalFindingRecord(
                text="seizures",
                evidence="She has not had any further seizures",
                clinical_kind="seizure_free",
                frequency_statement_type="current_zero_no_duration",
                count="0",
                confidence="high",
            )
        ],
    )

    final, warnings = apply_verification_decisions(raw_findings, decisions)

    assert [finding.text for finding in final] == ["seizures"]
    assert any("verification_removed" in w for w in warnings)
    assert any("verification_added" in w for w in warnings)


def test_apply_verification_does_not_remove_from_status_without_action() -> None:
    raw_findings = [
        ClinicalFindingRecord(
            text="events",
            evidence="events have been going on now for around 9 months",
            clinical_kind="other_frequency",
            frequency_statement_type="other_frequency",
            count="10",
            confidence="medium",
        )
    ]
    decisions = VerificationDecisionList(
        decisions=[
            VerificationDecisionRecord(
                raw_index=0,
                target_status="non_target_episode",
                action="keep",
                rationale="This deliberately tests action ownership.",
            )
        ],
    )

    final, warnings = apply_verification_decisions(raw_findings, decisions)

    assert warnings == []
    assert [finding.text for finding in final] == ["events"]


def test_projection_uses_only_model_emitted_fields_not_evidence_mining() -> None:
    finding = ClinicalFindingRecord(
        text="cluster of seizures",
        evidence="At her last clinic she reported a cluster of seizures",
        clinical_kind="dated_count",
        confidence="medium",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {}
    assert warnings == []


def test_projection_formats_model_emitted_rate_and_time_context() -> None:
    finding = ClinicalFindingRecord(
        text="focal seizures with impaired awareness",
        evidence=(
            "focal seizures with impaired awareness 2 to 3 times per month "
            "since her medication change"
        ),
        clinical_kind="frequency_rate",
        count_low="2",
        count_high="3",
        period_count="1",
        period_unit="month",
        time_relation="since",
        point_in_time="medication change",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=True)

    assert attrs == {
        "LowerNumberOfSeizures": "2",
        "UpperNumberOfSeizures": "3",
        "NumberOfTimePeriods": "1",
        "TimePeriod": "Month",
        "TimeSince_or_TimeOfEvent": "Since",
        "PointInTime": "DrugChange",
        "CUI": "C0270834",
        "CUIPhrase": "focal seizures with impaired awareness",
    }
    assert warnings == []


def test_projection_adds_one_period_for_model_emitted_background_rate_unit() -> None:
    finding = ClinicalFindingRecord(
        text="seizures",
        evidence="a few seizures per year",
        clinical_kind="frequency_rate",
        frequency_statement_type="background_rate",
        count="2",
        period_unit="year",
        confidence="medium",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "2",
        "NumberOfTimePeriods": "1",
        "TimePeriod": "Year",
    }
    assert warnings == []


def test_projection_drops_unanchored_since_on_background_rate() -> None:
    finding = ClinicalFindingRecord(
        text="seizures",
        evidence="roughly two seizures per year since then",
        clinical_kind="frequency_rate",
        frequency_statement_type="background_rate",
        count="2",
        period_count="1",
        period_unit="year",
        time_relation="since",
        confidence="medium",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "2",
        "NumberOfTimePeriods": "1",
        "TimePeriod": "Year",
    }
    assert warnings == ["dropped_unanchored_background_rate_since"]


def test_projection_collapses_equal_model_emitted_count_range() -> None:
    finding = ClinicalFindingRecord(
        text="generalised tonic clonic seizures",
        evidence="2 generalised tonic clonic seizures 2014",
        clinical_kind="dated_count",
        frequency_statement_type="calendar_count",
        count_low="2",
        count_high="2",
        year="2014",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "2",
        "YearDate": "2014",
        "TimeSince_or_TimeOfEvent": "During",
    }
    assert warnings == []


def test_projection_maps_model_emitted_dated_count_to_during() -> None:
    finding = ClinicalFindingRecord(
        text="focal seizures",
        evidence="In March she had 2 to 3 of her focal seizures",
        clinical_kind="dated_count",
        count_low="2",
        count_high="3",
        month="March",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "LowerNumberOfSeizures": "2",
        "UpperNumberOfSeizures": "3",
        "MonthDate": "3",
        "TimeSince_or_TimeOfEvent": "During",
    }
    assert warnings == []


def test_projection_maps_model_emitted_interval_to_one_event() -> None:
    finding = ClinicalFindingRecord(
        text="seizures",
        evidence="seizures every 3 to 4 weeks",
        clinical_kind="frequency_rate",
        period_low="3",
        period_high="4",
        period_unit="weeks",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "1",
        "LowerNumberOfTimePeriods": "3",
        "UpperNumberOfTimePeriods": "4",
        "TimePeriod": "Week",
    }
    assert warnings == []


def test_projection_period_range_takes_precedence_over_single_period_count() -> None:
    finding = ClinicalFindingRecord(
        text="seizures",
        evidence="seizures every 3 to 4 weeks",
        clinical_kind="frequency_rate",
        frequency_statement_type="recurrence_interval",
        count="1",
        period_count="1",
        period_low="3",
        period_high="4",
        period_unit="weeks",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "1",
        "LowerNumberOfTimePeriods": "3",
        "UpperNumberOfTimePeriods": "4",
        "TimePeriod": "Week",
    }
    assert warnings == []


def test_projection_collapses_equal_period_range() -> None:
    finding = ClinicalFindingRecord(
        text="focal seizures with altered awareness",
        evidence="one focal seizure with altered awareness per fortnight",
        clinical_kind="frequency_rate",
        frequency_statement_type="background_rate",
        count="1",
        period_low="2",
        period_high="2",
        period_unit="weeks",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "1",
        "NumberOfTimePeriods": "2",
        "TimePeriod": "Week",
    }
    assert warnings == []


def test_projection_single_period_bound_becomes_period_count() -> None:
    finding = ClinicalFindingRecord(
        text="focal seizures with altered awareness",
        evidence="focal seizures with altered awareness every 3 weeks",
        clinical_kind="frequency_rate",
        frequency_statement_type="recurrence_interval",
        count="1",
        period_low="3",
        period_unit="weeks",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "1",
        "NumberOfTimePeriods": "3",
        "TimePeriod": "Week",
    }
    assert warnings == []


def test_projection_fortnight_unit_becomes_two_weeks() -> None:
    finding = ClinicalFindingRecord(
        text="focal seizures with altered awareness",
        evidence="one focal seizure with altered awareness per fortnight",
        clinical_kind="frequency_rate",
        frequency_statement_type="background_rate",
        count="1",
        period_count="1",
        period_unit="fortnight",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "1",
        "NumberOfTimePeriods": "2",
        "TimePeriod": "Week",
    }
    assert warnings == []


def test_projection_maps_model_emitted_last_event_date_to_since_zero() -> None:
    finding = ClinicalFindingRecord(
        text="generalised tonic clonic seizure",
        evidence="Generalised tonic clonic seizure-last event July 2016",
        clinical_kind="last_event",
        month="July",
        year="2016",
        confidence="high",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "0",
        "MonthDate": "7",
        "YearDate": "2016",
        "TimeSince_or_TimeOfEvent": "Since",
    }
    assert warnings == []


def test_projection_maps_model_emitted_age_range() -> None:
    finding = ClinicalFindingRecord(
        text="seizures",
        evidence="His last seizures were in his teenage years",
        clinical_kind="last_event",
        frequency_statement_type="last_event_date",
        count="0",
        time_relation="since",
        age_low="13",
        age_high="19",
        age_unit="year",
        confidence="medium",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "0",
        "TimeSince_or_TimeOfEvent": "Since",
        "AgeLower": "13",
        "AgeUpper": "19",
        "AgeUnit": "Year",
    }
    assert warnings == []


def test_projection_maps_model_emitted_calendar_occurrence_to_one() -> None:
    finding = ClinicalFindingRecord(
        text="absence like seizures",
        evidence="absence like seizures 2018",
        clinical_kind="dated_count",
        frequency_statement_type="calendar_occurrence_no_count",
        year="2018",
        confidence="medium",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "1",
        "YearDate": "2018",
        "TimeSince_or_TimeOfEvent": "During",
    }
    assert warnings == []


def test_projection_maps_model_emitted_header_count_anchor() -> None:
    finding = ClinicalFindingRecord(
        text="seizures",
        evidence="several seizures since clinic review",
        clinical_kind="dated_count",
        frequency_statement_type="header_count_since_anchor",
        count="3",
        confidence="medium",
    )

    attrs, warnings = project_finding_to_attributes(finding, include_cui=False)

    assert attrs == {
        "NumberOfSeizures": "3",
        "TimeSince_or_TimeOfEvent": "Since",
        "PointInTime": "LastClinic",
    }
    assert warnings == []


def test_projection_can_project_seizure_free_kind_without_evidence_rules() -> None:
    finding = ClinicalFindingRecord(
        text="seizure free",
        evidence="seizure free for 6 months following surgery",
        clinical_kind="seizure_free",
        period_count="6",
        period_unit="months",
        time_relation="since",
        point_in_time="surgery",
        confidence="high",
    )

    attrs, _ = project_finding_to_attributes(finding, include_cui=True)

    assert attrs["NumberOfSeizures"] == "0"
    assert attrs["NumberOfTimePeriods"] == "6"
    assert attrs["TimePeriod"] == "Month"
    assert attrs["PointInTime"] == "Surgery"
    assert attrs["CUI"] == "C1299590"


def test_to_predicted_letters_exposes_format_and_cui_projection_layers() -> None:
    findings = [
        ClinicalFindingRecord(
            text="focal seizures with impaired awareness",
            evidence="focal seizures with impaired awareness 2 to 3 times per month",
            clinical_kind="frequency_rate",
            count_low="2",
            count_high="3",
            period_count="1",
            period_unit="month",
            confidence="high",
        ),
        ClinicalFindingRecord(
            text="ghost seizures",
            evidence="not in the note",
            clinical_kind="frequency_rate",
            count="2",
            period_unit="month",
            confidence="low",
        ),
    ]

    layers, warnings = to_predicted_letters("CF001", findings, note_text=_NOTE)

    assert set(layers) == {"format_projected", "cui_projected"}
    assert len(layers["format_projected"].mentions) == 1
    assert len(layers["cui_projected"].mentions) == 1
    fmt_attrs = dict(layers["format_projected"].mentions[0].attributes)
    cui_attrs = dict(layers["cui_projected"].mentions[0].attributes)
    assert "CUI" not in fmt_attrs
    assert cui_attrs["CUI"] == "C0270834"
    assert layers["cui_projected"].mentions[0].entity == SEIZURE_FREQUENCY.name
    assert any("dropped_evidence_not_substring" in w for w in warnings)


def test_model_excluded_current_control_no_duration_is_not_scored() -> None:
    findings = [
        ClinicalFindingRecord(
            text="seizure free",
            evidence="She remains seizure free",
            clinical_kind="seizure_free",
            frequency_statement_type="current_control_no_duration",
            count="0",
            confidence="medium",
        )
    ]

    layers, warnings = to_predicted_letters(
        "CF001",
        findings,
        note_text="She remains seizure free",
    )

    assert layers["format_projected"].mentions == ()
    assert layers["cui_projected"].mentions == ()
    assert any("model_excluded_current_control_no_duration" in w for w in warnings)


def test_current_zero_no_duration_is_scored_when_model_marks_target() -> None:
    findings = [
        ClinicalFindingRecord(
            text="seizures",
            evidence="She has not had any further seizures",
            clinical_kind="seizure_free",
            frequency_statement_type="current_zero_no_duration",
            count="0",
            confidence="high",
        )
    ]

    layers, warnings = to_predicted_letters(
        "CF001",
        findings,
        note_text="She has not had any further seizures",
    )

    assert warnings == []
    assert dict(layers["cui_projected"].mentions[0].attributes)["NumberOfSeizures"] == "0"


def test_plan11_route_does_not_convert_non_target_event_frames_to_findings() -> None:
    record = llm_only_clinical_findings.ClinicalFindingsRecord(
        event_frames=[
            EventFrameRecord(
                event_id="e1",
                evidence="staring episodes happen several times per week",
                seizure_phrase="staring episodes",
                target_status="non_target_episode",
                statement_family="non_target",
                include_as_finding=False,
            )
        ],
        findings=[],
    )

    layers, diagnostics, warnings = build_plan11_event_state_route(
        "CF001",
        record,
        note_text="Her staring episodes happen several times per week.",
    )

    assert warnings == []
    assert layers["format_projected"].mentions == ()
    assert layers["cui_projected"].mentions == ()
    assert diagnostics["deterministic_clinical_selection"] is False
    assert diagnostics["aggregate_ownership"] == "llm_first"
    by_layer = {layer["layer"]: layer for layer in diagnostics["layers"]}
    assert by_layer["raw_event_frames"]["count"] == 1
    assert by_layer["raw_findings"]["count"] == 0
    assert by_layer["format_projected"]["owner"] == "deterministic_adapter"


def test_plan11_route_does_not_infer_missing_operands_from_evidence_text() -> None:
    record = llm_only_clinical_findings.ClinicalFindingsRecord(
        findings=[
            ClinicalFindingRecord(
                text="seizures",
                evidence="2 seizures per month",
                clinical_kind="frequency_rate",
                frequency_statement_type="background_rate",
                confidence="high",
            )
        ]
    )

    layers, diagnostics, warnings = build_plan11_event_state_route(
        "CF001",
        record,
        note_text="She reports 2 seizures per month.",
    )

    assert warnings == []
    attrs = dict(layers["format_projected"].mentions[0].attributes)
    assert "NumberOfSeizures" not in attrs
    assert "NumberOfTimePeriods" not in attrs
    assert "TimePeriod" not in attrs
    assert diagnostics["deterministic_clinical_selection"] is False


def test_plan11_route_keeps_cui_projection_out_of_primary_format_layer() -> None:
    record = llm_only_clinical_findings.ClinicalFindingsRecord(
        findings=[
            ClinicalFindingRecord(
                text="focal seizures with impaired awareness",
                evidence="focal seizures with impaired awareness 2 per month",
                clinical_kind="frequency_rate",
                frequency_statement_type="background_rate",
                count="2",
                period_count="1",
                period_unit="month",
                confidence="high",
            )
        ]
    )

    layers, diagnostics, warnings = build_plan11_event_state_route(
        "CF001",
        record,
        note_text="She has focal seizures with impaired awareness 2 per month.",
    )

    assert warnings == []
    format_attrs = dict(layers["format_projected"].mentions[0].attributes)
    cui_attrs = dict(layers["cui_projected"].mentions[0].attributes)
    assert "CUI" not in format_attrs
    assert "CUIPhrase" not in format_attrs
    assert "Certainty" not in format_attrs
    assert "Negation" not in format_attrs
    assert cui_attrs["CUI"] == "C0270834"
    by_layer = {layer["layer"]: layer for layer in diagnostics["layers"]}
    assert by_layer["cui_projected"]["claim_role"] == "Companion benchmark-format score only."
    assert by_layer["certainty_projected"]["diagnostics"] == {"sf_policy": "no_op"}
