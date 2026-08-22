"""Ablatable deterministic Select rules over the emitted fact ledger."""

from __future__ import annotations

import pytest

from clinical_extraction.paper.rule_records import RULE_BY_NAME
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    CANDIDATE_SELECT_RULE_IDS,
    DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE,
    DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY,
    EMITTED_ACTIONS_BY_RULE_ID,
    PRESCRIPTION_ACTIVE_TITRATION,
    PRESCRIPTION_EXACT_REGIMEN_DEDUPE,
    PRESCRIPTION_LOCAL_REGIMEN_SCOPE,
    SF_NAMED_TYPE_IDENTITY,
    SF_RECENT_EVENT_OVER_HISTORICAL_FREE,
    SF_TO_DIAGNOSIS_EXPLICIT_TYPE,
    apply_select_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly import (
    assemble_structured_rows,
)


def _mention(
    entity: str,
    text: str,
    evidence: str,
    attributes: dict[str, str],
) -> dict[str, object]:
    return {
        "entity": entity,
        "text": text,
        "evidence": evidence,
        "attributes": attributes,
        "confidence": "medium",
        "rationale": "",
    }


def _apply(
    selected: list[dict[str, object]],
    source: list[dict[str, object]],
    rule_id: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    return apply_select_rules(
        selected,
        source_mentions=source,
        note_text="\n".join(str(row["evidence"]) for row in source),
        enabled_rule_ids=frozenset({rule_id}),
    )


def test_source_local_specificity_restores_overbroad_diagnosis_rewrites() -> None:
    longstanding = "Diagnosis: longstanding epilepsy with generalised tonic clonic seizures"
    structural = (
        "As you know he has symptomatic structural temporal lobe epilepsy caused "
        "by his previous herpes encephalitis."
    )
    source = [
        _mention("Diagnosis", "epilepsy", longstanding, {"DiagCategory": "Epilepsy"}),
        _mention(
            "Diagnosis",
            "temporal lobe epilepsy",
            structural,
            {
                "DiagCategory": "Epilepsy",
                "CUI": "C0014556",
                "CUIPhrase": "temporal lobe epilepsy",
            },
        ),
    ]
    selected = [
        _mention(
            "Diagnosis",
            "generalised epilepsy",
            longstanding,
            {
                "DiagCategory": "Epilepsy",
                "CUI": "C0014548",
                "CUIPhrase": "generalised-epilepsy",
            },
        ),
        _mention(
            "Diagnosis",
            "symptomatic structural focal epilepsy",
            structural,
            {
                "DiagCategory": "Epilepsy",
                "CUI": "C0472349",
                "CUIPhrase": "symptomatic structural focal epilepsy",
            },
        ),
    ]

    repaired, actions = _apply(selected, source, DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY)

    assert [row["text"] for row in repaired] == ["epilepsy", "temporal lobe epilepsy"]
    assert len(actions) == 2
    assert {action["rule_id"] for action in actions} == {DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY}


def test_source_local_specificity_restores_unauthorized_laterality() -> None:
    evidence = "Diagnosis: longstanding epilepsy with generalised tonic clonic seizures"
    source = [_mention("Diagnosis", "epilepsy", evidence, {"DiagCategory": "Epilepsy"})]
    selected = [
        _mention(
            "Diagnosis",
            "generalised epilepsy",
            evidence,
            {"DiagCategory": "Epilepsy"},
        )
    ]

    repaired, actions = _apply(selected, source, DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY)

    assert [row["text"] for row in repaired] == ["epilepsy"]
    assert len(actions) == 1


def test_source_local_specificity_keeps_explicit_probable_classification() -> None:
    evidence = "Diagnosis: Epilepsy – unclassified, possibly generalised."
    source = [_mention("Diagnosis", "epilepsy", evidence, {"DiagCategory": "Epilepsy"})]
    selected = [
        _mention(
            "Diagnosis",
            "generalised epilepsy",
            evidence,
            {"DiagCategory": "Epilepsy"},
        )
    ]

    repaired, actions = _apply(selected, source, DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY)

    assert repaired == selected
    assert actions == []


def test_explicit_diagnosis_heading_retains_only_the_heading_phenotype() -> None:
    heading = "Medical diagnosis:\tGeneralised epilepsy with absences and GTCS"
    history = "To recap, Rachel started having absence seizures at around the age of 8."
    source = [
        _mention("Diagnosis", "absence seizures", heading, {"DiagCategory": "MultipleSeizures"}),
        _mention("Diagnosis", "absence seizures", history, {"DiagCategory": "MultipleSeizures"}),
    ]

    repaired, actions = _apply([], source, DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE)

    assert len(repaired) == 1
    assert repaired[0]["evidence"] == heading
    assert actions[0]["rule_id"] == DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE


def test_explicit_heading_myoclonus_is_retained_without_an_owning_syndrome() -> None:
    heading = "Medical diagnosis:\tGeneralised epilepsy with myoclonus"
    source = [_mention("Diagnosis", "myoclonus", heading, {"DiagCategory": "MultipleSeizures"})]

    repaired, actions = _apply([], source, DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE)

    assert [row["text"] for row in repaired] == ["myoclonus"]
    assert actions[0]["rule_id"] == DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE


def test_explicit_heading_absence_is_kept_beside_temporal_lobe_epilepsy() -> None:
    heading = "Diagnosis: temporal lobe epilepsy with absences"
    source = [
        _mention(
            "Diagnosis",
            "temporal lobe epilepsy",
            heading,
            {"DiagCategory": "Epilepsy"},
        ),
        _mention("Diagnosis", "absence seizures", heading, {"DiagCategory": "MultipleSeizures"}),
    ]

    repaired, actions = _apply([source[0]], source, DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE)

    assert [row["text"] for row in repaired] == ["temporal lobe epilepsy", "absence seizures"]
    assert len(actions) == 1


def test_explicit_heading_phenotype_stays_suppressed_under_jme() -> None:
    heading = (
        "Diagnosis: Probable Juvenile Myoclonic Epilepsy (JME) "
        "(absences, myoclonus and generalised tonic clonic seizures)"
    )
    source = [
        _mention(
            "Diagnosis",
            "juvenile myoclonic epilepsy",
            heading,
            {"DiagCategory": "Epilepsy"},
        ),
        _mention(
            "Diagnosis",
            "absence seizures",
            heading,
            {"DiagCategory": "MultipleSeizures"},
        ),
    ]
    selected = [source[0]]

    myoclonus = _mention("Diagnosis", "myoclonus", heading, {"DiagCategory": "MultipleSeizures"})
    repaired, actions = _apply(selected, [*source, myoclonus], DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE)

    assert repaired == selected
    assert actions == []


def test_local_regimen_scope_does_not_spread_rescue_frequency_to_siblings() -> None:
    evidence = (
        "He is taking levetiracetam 1500mg bd as well as lamotrigine 200mg bd "
        "and clobazam for seizure clusters (he takes this infrequently)."
    )
    source = [
        _mention(
            "Prescription",
            "levetiracetam 1500mg bd",
            evidence,
            {"DrugName": "levetiracetam", "DrugDose": "1500", "DoseUnit": "mg", "Frequency": "2"},
        ),
        _mention(
            "Prescription",
            "lamotrigine 200mg bd",
            evidence,
            {"DrugName": "lamotrigine", "DrugDose": "200", "DoseUnit": "mg", "Frequency": "2"},
        ),
        _mention(
            "Prescription",
            "clobazam",
            evidence,
            {"DrugName": "clobazam", "Frequency": "As_Required"},
        ),
    ]
    selected = [
        {**row, "attributes": {**row["attributes"], "Frequency": "As_Required"}} for row in source
    ]

    repaired, actions = _apply(selected, source, PRESCRIPTION_LOCAL_REGIMEN_SCOPE)

    assert [row["attributes"]["Frequency"] for row in repaired] == [
        "2",
        "2",
        "As_Required",
    ]
    assert len(actions) == 2


def test_active_titration_keeps_current_regimen_but_not_a_true_future_start() -> None:
    current = "Lamotrigine 50mg bd increasing by 5mg each dose every 2 weeks to 75mg bd"
    future = "Please start levetiracetam 250mg once daily and increase in two weeks."
    source = [
        _mention(
            "Prescription",
            "lamotrigine",
            current,
            {"DrugName": "lamotrigine", "DrugDose": "50", "DoseUnit": "mg", "Frequency": "2"},
        ),
        _mention(
            "Prescription",
            "levetiracetam",
            future,
            {"DrugName": "levetiracetam", "DrugDose": "250", "DoseUnit": "mg", "Frequency": "1"},
        ),
    ]

    repaired, actions = _apply([], source, PRESCRIPTION_ACTIVE_TITRATION)

    assert [row["text"] for row in repaired] == ["lamotrigine"]
    assert actions[0]["rule_id"] == PRESCRIPTION_ACTIVE_TITRATION


def test_active_titration_rejects_a_start_request_without_letter_openers() -> None:
    source = [
        _mention(
            "Prescription",
            "levetiracetam",
            "Start levetiracetam 250mg once daily and increase in two weeks.",
            {"DrugName": "levetiracetam", "DrugDose": "250", "DoseUnit": "mg", "Frequency": "1"},
        )
    ]

    repaired, actions = _apply([], source, PRESCRIPTION_ACTIVE_TITRATION)

    assert repaired == []
    assert actions == []


def test_active_titration_rejects_prescribe_requests_and_target_doses() -> None:
    prescribe = (
        "Please can you prescribe eslicarbazepine 400mg od, increasing to 800mg od after 1 week."
    )
    titration = "Levetiracetam 250mgs once a day, increasing by 250mgs every 2 weeks to 500mgs bd"
    source = [
        _mention(
            "Prescription",
            "eslicarbazepine 400mg od",
            prescribe,
            {
                "DrugName": "eslicarbazepine",
                "DrugDose": "400",
                "DoseUnit": "mg",
                "Frequency": "1",
            },
        ),
        _mention(
            "Prescription",
            "Levetiracetam 500mgs bd",
            titration,
            {
                "DrugName": "levetiracetam",
                "DrugDose": "500",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
    ]

    repaired, actions = _apply([], source, PRESCRIPTION_ACTIVE_TITRATION)

    assert repaired == []
    assert actions == []


def test_exact_regimen_dedupe_keeps_unequal_doses() -> None:
    first = _mention(
        "Prescription",
        "sodium valproate",
        "Continue sodium valproate 400mg twice daily.",
        {"DrugName": "sodium valproate", "DrugDose": "400", "DoseUnit": "mg", "Frequency": "2"},
    )
    duplicate = {**first, "evidence": "Once commenced on sodium valproate 400mg twice daily."}
    unequal = {
        **first,
        "evidence": "Epilim 200mg in the morning and 400mg at night.",
        "attributes": {**first["attributes"], "DrugDose": "200", "Frequency": "1"},
    }

    repaired, actions = _apply([first, duplicate, unequal], [], PRESCRIPTION_EXACT_REGIMEN_DEDUPE)

    assert len(repaired) == 2
    assert {row["attributes"]["DrugDose"] for row in repaired} == {"200", "400"}
    assert len(actions) == 1


def test_exact_regimen_dedupe_keeps_distinct_current_assertions() -> None:
    first = _mention(
        "Prescription",
        "lamotrigine",
        "Current medication: Lamotrigine 150mg bd",
        {
            "DrugName": "lamotrigine",
            "DrugDose": "150",
            "DoseUnit": "mg",
            "Frequency": "2",
        },
    )
    second = {
        **first,
        "evidence": "At present she is taking lamotrigine 150 milligrammes twice a day.",
    }

    repaired, actions = _apply([first, second], [], PRESCRIPTION_EXACT_REGIMEN_DEDUPE)

    assert repaired == [first, second]
    assert actions == []


def test_exact_regimen_dedupe_keeps_incomplete_regimens() -> None:
    current = _mention(
        "Prescription",
        "lamotrigine",
        "Currently taking lamotrigine.",
        {"DrugName": "lamotrigine"},
    )
    historical = {
        **current,
        "evidence": "Once started on lamotrigine she felt dizzy.",
    }

    repaired, actions = _apply(
        [current, historical], [], PRESCRIPTION_EXACT_REGIMEN_DEDUPE
    )

    assert repaired == [current, historical]
    assert actions == []


def test_named_sf_identity_is_not_reassigned_by_a_shared_evidence_window() -> None:
    evidence = (
        "Seizure type and frequency: 2 generalised tonic clonic seizures 2014, "
        "absence like seizures 2014"
    )
    source = [
        _mention(
            "SeizureFrequency",
            "generalised tonic clonic seizures",
            evidence,
            {
                "CUI": "C0494475",
                "CUIPhrase": "generalised tonic clonic seizures",
                "NumberOfSeizures": "2",
            },
        ),
        _mention(
            "SeizureFrequency",
            "absences",
            evidence,
            {"CUI": "C0563606", "CUIPhrase": "absences", "NumberOfSeizures": "1"},
        ),
    ]
    selected = [
        source[0],
        {
            **source[1],
            "text": "generalised tonic clonic seizures",
            "attributes": {
                **source[1]["attributes"],
                "CUI": "C0494475",
                "CUIPhrase": "generalised tonic clonic seizures",
            },
        },
    ]

    repaired, actions = _apply(selected, source, SF_NAMED_TYPE_IDENTITY)

    assert [row["text"] for row in repaired] == [
        "generalised tonic clonic seizures",
        "absences",
    ]
    assert len(actions) == 1


def test_named_sf_identity_keeps_a_more_specific_same_cui_surface() -> None:
    evidence = "His typical absences have become more frequent."
    source = _mention(
        "SeizureFrequency",
        "absences",
        evidence,
        {
            "CUI": "C0563606",
            "CUIPhrase": "absences",
            "FrequencyChange": "Increased",
        },
    )
    selected = {
        **source,
        "text": "typical absences",
        "attributes": {
            **source["attributes"],
            "CUIPhrase": "typical absences",
        },
    }

    repaired, actions = _apply([selected], [source], SF_NAMED_TYPE_IDENTITY)

    assert repaired == [selected]
    assert actions == []


def test_named_sf_identity_keeps_typical_absence_refinement() -> None:
    evidence = "His brother reports more of his typical absences since clinic."
    source = _mention(
        "SeizureFrequency",
        "absences",
        evidence,
        {
            "CUI": "C0563606",
            "CUIPhrase": "absences",
            "FrequencyChange": "Increased",
        },
    )
    selected = {
        **source,
        "text": "typical absences",
        "attributes": {
            **source["attributes"],
            "CUI": "C4316903",
            "CUIPhrase": "typical absences",
        },
    }

    repaired, actions = _apply([selected], [source], SF_NAMED_TYPE_IDENTITY)

    assert repaired == [selected]
    assert actions == []


def test_named_sf_identity_reconciles_the_whole_shared_evidence_group() -> None:
    evidence = "Frequent tonic clonic seizures, drops and absences throughout the day."
    state = {"FrequencyChange": "Frequent", "TimeSince_or_TimeOfEvent": "During"}
    gtc = _mention(
        "SeizureFrequency",
        "generalised tonic clonic seizures",
        evidence,
        {
            **state,
            "CUI": "C0494475",
            "CUIPhrase": "generalised tonic clonic seizures",
        },
    )
    absence = _mention(
        "SeizureFrequency",
        "absences",
        evidence,
        {**state, "CUI": "C0563606", "CUIPhrase": "absences"},
    )

    repaired, actions = _apply([gtc, absence], [gtc, absence], SF_NAMED_TYPE_IDENTITY)

    assert repaired == [gtc, absence]
    assert actions == []


def test_named_sf_identity_records_seizure_frequency_portability() -> None:
    evidence = "Absences and tonic seizures occur daily."
    absence = _mention(
        "SeizureFrequency",
        "absences",
        evidence,
        {
            "CUI": "C0563606",
            "CUIPhrase": "absences",
            "NumberOfSeizures": "1",
            "TimePeriod": "Day",
        },
    )
    misassigned = {
        **absence,
        "text": "tonic seizures",
        "attributes": {**absence["attributes"], "CUI": "C0270844"},
    }

    repaired, actions = _apply([misassigned], [absence], SF_NAMED_TYPE_IDENTITY)

    assert repaired[0]["provenance"][-1]["portability"] == "seizure_frequency"
    assert actions[0]["portability"] == "seizure_frequency"


def test_named_sf_identity_keeps_focal_awareness_refinement() -> None:
    evidence = "Focal seizures with altered awareness approximately once per fortnight."
    source = _mention(
        "SeizureFrequency",
        "focal seizures",
        evidence,
        {
            "CUI": "C0751495",
            "CUIPhrase": "focal seizures",
            "NumberOfSeizures": "1",
            "TimePeriod": "Week",
        },
    )
    selected = {
        **source,
        "text": "focal seizures with altered awareness",
        "attributes": {
            **source["attributes"],
            "CUI": "C0270834",
            "CUIPhrase": "focal seizures with altered awareness",
        },
    }

    repaired, actions = _apply([selected], [source], SF_NAMED_TYPE_IDENTITY)

    assert repaired == [selected]
    assert actions == []


def test_recent_event_is_kept_over_a_historical_seizure_free_sibling() -> None:
    active = _mention(
        "SeizureFrequency",
        "generalised tonic clonic seizures",
        "She has had a recent generalised tonic chronic seizure at home.",
        {
            "CUI": "C0494475",
            "CUIPhrase": "generalised tonic clonic seizures",
            "NumberOfSeizures": "1",
        },
    )
    historical = _mention(
        "SeizureFrequency",
        "seizure",
        "Before the seizure she had been seizure free for 3 years.",
        {
            "CUI": "C0036572",
            "CUIPhrase": "seizure",
            "NumberOfSeizures": "0",
            "NumberOfTimePeriods": "3",
            "TimePeriod": "Year",
        },
    )

    repaired, actions = _apply(
        [historical], [active, historical], SF_RECENT_EVENT_OVER_HISTORICAL_FREE
    )

    assert len(repaired) == 1
    assert repaired[0]["text"] == active["text"]
    assert repaired[0]["evidence"] == active["evidence"]
    assert repaired[0]["attributes"] == active["attributes"]
    assert {action["action"] for action in actions} == {"add", "drop"}


def test_named_sf_to_diagnosis_projects_named_absence_refinements() -> None:
    evidence = "Typical absences continue weekly."
    sf = _mention(
        "SeizureFrequency",
        "typical absences",
        evidence,
        {
            "CUI": "C4316903",
            "CUIPhrase": "typical absences",
            "NumberOfSeizures": "1",
            "TimePeriod": "Week",
        },
    )

    repaired, actions = _apply([sf], [sf], SF_TO_DIAGNOSIS_EXPLICIT_TYPE)

    diagnosis = [row for row in repaired if row["entity"] == "Diagnosis"]
    assert [row["text"] for row in diagnosis] == ["absence seizures"]
    assert actions[0]["rule_id"] == SF_TO_DIAGNOSIS_EXPLICIT_TYPE


def test_named_sf_to_diagnosis_is_ledger_only_and_concept_deduplicated() -> None:
    evidence = "Focal to bilateral convulsive seizures continue monthly."
    sf = _mention(
        "SeizureFrequency",
        "focal to bilateral convulsive seizures",
        evidence,
        {
            "CUI": "C0877017",
            "CUIPhrase": "focal-to-bilateral-convulsive-seizures",
            "NumberOfSeizures": "1",
            "TimePeriod": "Month",
        },
    )
    generic = _mention(
        "SeizureFrequency",
        "seizures",
        "Seizures continue monthly.",
        {
            "CUI": "C0036572",
            "CUIPhrase": "seizures",
            "NumberOfSeizures": "1",
            "TimePeriod": "Month",
        },
    )

    repaired, actions = _apply([sf, generic], [sf, generic], SF_TO_DIAGNOSIS_EXPLICIT_TYPE)

    diagnosis = [row for row in repaired if row["entity"] == "Diagnosis"]
    assert len(diagnosis) == 1
    assert diagnosis[0]["text"] == "focal to bilateral convulsive seizures"
    assert diagnosis[0]["evidence"] == evidence
    assert diagnosis[0]["attributes"]["CUI"] == "C0877017"
    assert actions[0]["rule_id"] == SF_TO_DIAGNOSIS_EXPLICIT_TYPE

    repaired_again, actions_again = _apply(repaired, [sf, generic], SF_TO_DIAGNOSIS_EXPLICIT_TYPE)
    assert repaired_again == repaired
    assert actions_again == []


def test_named_sf_to_diagnosis_recognizes_embedded_motor_synonym() -> None:
    evidence = "Partial motor seizures involving left arm twitching occur monthly."
    diagnosis = _mention(
        "Diagnosis",
        "partial motor seizures involving left arm twitching",
        evidence,
        {"DiagCategory": "MultipleSeizures"},
    )
    sf = _mention(
        "SeizureFrequency",
        "focal motor seizures",
        evidence,
        {
            "CUI": "C0016399",
            "CUIPhrase": "focal motor seizures",
            "NumberOfSeizures": "1",
            "TimePeriod": "Month",
        },
    )

    repaired, actions = _apply([diagnosis, sf], [diagnosis, sf], SF_TO_DIAGNOSIS_EXPLICIT_TYPE)

    assert repaired == [diagnosis, sf]
    assert actions == []


def test_selected_assembly_applies_accepted_select_rules() -> None:
    evidence = (
        "He is taking levetiracetam 1500mg bd as well as lamotrigine 200mg bd "
        "and clobazam for seizure clusters (he takes this infrequently)."
    )
    letter = ExectLetter(letter_id="EA0000", note_text=evidence)
    mentions = [
        _mention(
            "Prescription",
            "levetiracetam 1500mg bd",
            evidence,
            {
                "DrugName": "levetiracetam",
                "DrugDose": "1500",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        _mention(
            "Prescription",
            "lamotrigine 200mg bd",
            evidence,
            {
                "DrugName": "lamotrigine",
                "DrugDose": "200",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        _mention(
            "Prescription",
            "clobazam",
            evidence,
            {"DrugName": "clobazam", "Frequency": "As_Required"},
        ),
    ]
    row = {
        "letter_id": letter.letter_id,
        "predicted_mentions": mentions,
        "raw_output": "",
    }

    selected = assemble_structured_rows([letter], [row])[letter.letter_id]
    baseline = assemble_structured_rows(
        [letter],
        [row],
        config=StructuredMethodConfig(
            archived_replay=True,
            select_rule_ids=frozenset(),
        ),
    )[letter.letter_id]

    assert [mention["attributes"]["Frequency"] for mention in selected["predicted_mentions"]] == [
        "2",
        "2",
        "As_Required",
    ]
    assert [mention["attributes"]["Frequency"] for mention in baseline["predicted_mentions"]] == [
        "As_Required",
        "As_Required",
        "As_Required",
    ]
    assert {action["rule_id"] for action in selected["select_rule_actions"]} == {
        PRESCRIPTION_LOCAL_REGIMEN_SCOPE
    }


def test_select_rule_ablation_requires_archived_replay() -> None:
    with pytest.raises(ValueError, match="non-selected policy"):
        StructuredMethodConfig(select_rule_ids=frozenset())


def test_select_rule_stack_rejects_unknown_rule_ids() -> None:
    with pytest.raises(ValueError, match="unknown deterministic Select rule"):
        apply_select_rules(
            [],
            source_mentions=[],
            note_text="",
            enabled_rule_ids=frozenset({"selection.typo"}),
        )


def test_emitted_actions_by_rule_id_covers_candidate_rules() -> None:
    assert frozenset(EMITTED_ACTIONS_BY_RULE_ID) == frozenset(CANDIDATE_SELECT_RULE_IDS)
    for rule_id, actions in EMITTED_ACTIONS_BY_RULE_ID.items():
        assert actions, f"{rule_id} must declare at least one action kind"
        assert actions <= frozenset({"rewrite", "add", "drop"}), (
            f"{rule_id} declares invalid action kinds: {sorted(actions)}"
        )


def test_accepted_select_rules_have_live_component_records() -> None:
    expected_authority = {
        DIAGNOSIS_SOURCE_LOCAL_SPECIFICITY: "rewrite",
        DIAGNOSIS_EXPLICIT_HEADING_PHENOTYPE: "reselect",
        PRESCRIPTION_LOCAL_REGIMEN_SCOPE: "rewrite",
        PRESCRIPTION_ACTIVE_TITRATION: "reselect",
        PRESCRIPTION_EXACT_REGIMEN_DEDUPE: "drop",
        SF_NAMED_TYPE_IDENTITY: "rewrite",
        SF_TO_DIAGNOSIS_EXPLICIT_TYPE: "invent",
    }

    for rule_id, authority in expected_authority.items():
        record = RULE_BY_NAME[rule_id]
        assert record.task == "exectv2"
        assert record.runs_at == "llm_select"
        assert record.authority == authority
        assert record.status == "live"
