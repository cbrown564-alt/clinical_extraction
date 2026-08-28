"""Rules-only recall-first extract plus encode/Select on the inventory scorer."""

from __future__ import annotations

from dataclasses import replace

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    diagnosis as diagnosis_mod,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    extract_deterministic_all9,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as inv,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    extract_seizure_frequency,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.recognise_ledger import (
    DIAGNOSIS_HEADING_DECOMPOSITION,
    DIAGNOSIS_NESTED_ANCESTOR,
    DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
    INV_RESULT_VARIANT,
    RECALL_FIRST_CLASS_TAG,
    RX_RECALL_EXPANSION,
    SF_NAMED_TYPE,
    SF_SEIZURE_FREE,
    SF_STATE_VARIANT,
    build_recognise_ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    CANDIDATE_SELECT_RULE_IDS,
    CROSS_FAMILY,
    INVENTORY_WEAK_EPISODE_DROP,
    INVESTIGATION_RESULTLESS_DROP,
    INVESTIGATION_SAME_RESULT_DEDUPE,
    KEEP_DX_HEADING_DECOMPOSITION,
    KEEP_INV_RESULT_VARIANT,
    KEEP_RX_RECALL_EXPANSION,
    KEEP_SF_STATE_VARIANT,
    RECALL_FIRST_UNSUPPORTED_DROP,
    RULES_ONLY_SELECT_RULE_IDS,
    SF_GENERIC_DUPLICATE_DROP,
    SF_RATELESS_ANCHOR_DROP,
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
    SF_SUPPORTED_STATE_PROMOTION,
    apply_select_rules,
    flatten_family_select_plan,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    ACCEPTED_THREE_STAGE_CONFIG,
    ENCODE_FORMAT_STACK,
    RECALL_FIRST_THREE_STAGE_CONFIG,
    TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG,
    ThreeStageConfig,
    run_letter,
    run_letter_retune_stack,
    run_letter_three_stage,
    three_stage_stop_mentions,
)


def test_investigations_keep_repeated_same_result_at_extract() -> None:
    mentions = inv._extract_investigations(
        "She had a normal MRI in 2016. A later MRI in 2019 was also normal."
    )
    results = [mention.attributes.get("MRI_Results") for mention in mentions]
    assert results == ["Normal", "Normal"]
    prediction = extract_deterministic_all9(
        ExectLetter(
            "INV-REPEAT",
            "She had a normal MRI in 2016. A later MRI in 2019 was also normal.",
        )
    )
    investigations = [
        mention
        for mention in prediction.mentions
        if mention.entity == INVESTIGATIONS.name
    ]
    assert [
        mention.attributes.get("MRI_Results") for mention in investigations
    ] == ["Normal", "Normal"]


def test_investigation_same_result_dedupe_is_select_and_clinical_epilepsy() -> None:
    selected = [
        {
            "entity": INVESTIGATIONS.name,
            "text": "MRI",
            "evidence": "normal MRI in 2016",
            "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        },
        {
            "entity": INVESTIGATIONS.name,
            "text": "MRI",
            "evidence": "MRI in 2019 was also normal",
            "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        },
    ]
    kept, actions = apply_select_rules(
        selected,
        source_mentions=selected,
        note_text="She had a normal MRI in 2016. A later MRI in 2019 was also normal.",
        enabled_rule_ids=frozenset({INVESTIGATION_SAME_RESULT_DEDUPE}),
    )
    assert len(kept) == 1
    assert actions[0]["rule_id"] == INVESTIGATION_SAME_RESULT_DEDUPE
    assert actions[0]["action"] == "drop"
    assert actions[0]["portability"] == "clinical_epilepsy"


def test_diagnosis_recognise_keeps_focal_onset_heading() -> None:
    prediction = extract_deterministic_all9(
        ExectLetter("DX-FOCAL-ONSET", "Diagnosis: focal onset epilepsy (occipital).")
    )
    diagnoses = [
        mention.text.lower()
        for mention in prediction.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert any("focal onset epilepsy" in text or "focal epilepsy" in text for text in diagnoses)


def test_run_letter_encodes_probable_focal_heading_to_focal_epilepsy() -> None:
    result = run_letter(
        ExectLetter(
            "DX-PROBABLE-FOCAL",
            "Diagnosis: epilepsy – probable focal. EEG was abnormal.",
        )
    )
    diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in result.comparison_projection.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert "focal epilepsy" in diagnoses


def test_run_letter_three_stage_matches_comparator_on_synthetic_letters() -> None:
    letters = (
        ExectLetter(
            "DX-PROBABLE-FOCAL",
            "Diagnosis: epilepsy – probable focal. EEG was abnormal.",
        ),
        ExectLetter(
            "INV-REPEAT",
            "She had a normal MRI in 2016. A later MRI in 2019 was also normal.",
        ),
        ExectLetter("DX-FOCAL-ONSET", "Diagnosis: focal onset epilepsy (occipital)."),
    )
    for letter in letters:
        comparator = run_letter_retune_stack(letter)
        three_stage = run_letter_three_stage(letter)
        assert (
            three_stage.comparison_projection.mentions
            == comparator.comparison_projection.mentions
        )


def test_sf_rateless_anchor_is_optional_and_select_can_drop_it() -> None:
    letter = ExectLetter("SF-RATELESS", "She has focal seizures. No rate is given.")
    default = extract_seizure_frequency(letter)
    recall = extract_seizure_frequency(letter, keep_unassociated_anchors=True)
    default_texts = [mention.text.lower() for mention in default.mentions]
    recall_rows = [
        {
            "entity": mention.entity,
            "text": mention.text,
            "evidence": mention.evidence,
            "attributes": dict(mention.attributes),
        }
        for mention in recall.mentions
        if mention.entity == SEIZURE_FREQUENCY.name
    ]
    assert "focal seizures" not in default_texts or all(
        mention.attributes for mention in default.mentions
    )
    assert any(
        mention.text.lower() == "focal seizures" and not _has_frequency_attrs(mention.attributes)
        for mention in recall.mentions
    )
    kept, actions = apply_select_rules(
        recall_rows,
        source_mentions=recall_rows,
        note_text=letter.note_text,
        enabled_rule_ids=frozenset({SF_RATELESS_ANCHOR_DROP}),
    )
    assert not any(
        str(row.get("text") or "").lower() == "focal seizures"
        and not _has_frequency_attrs(row.get("attributes") or {})
        for row in kept
    )
    assert any(action["rule_id"] == SF_RATELESS_ANCHOR_DROP for action in actions)
    assert actions[0]["portability"] == "seizure_frequency"


def _has_frequency_attrs(attributes: dict[str, str]) -> bool:
    semantic = set(attributes) - {"CUI", "CUIPhrase"}
    return bool(semantic)


def test_dx_context_direct_class_widens_recognise_and_preserves_select() -> None:
    letter = ExectLetter(
        "DX-CONTEXT-RELOCATE",
        "Diagnosis: focal epilepsy. She was seen by the epilepsy nurse. "
        "There is a family history of epilepsy.",
    )
    relocated = ThreeStageConfig(
        recognise=ACCEPTED_THREE_STAGE_CONFIG.recognise,
        select_rule_ids=(
            RECALL_FIRST_UNSUPPORTED_DROP,
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
        ),
        direct_classes=frozenset({DIAGNOSIS_NONDIAGNOSTIC_CONTEXT}),
    )
    stops = three_stage_stop_mentions(letter, relocated)
    excluded_context_mentions = [
        mention
        for mention in stops.recognise
        if RECALL_FIRST_CLASS_TAG in mention.component_owner
    ]
    assert excluded_context_mentions, "expected excluded-context mentions as direct"
    assert stops.select == run_letter(letter).comparison_projection.mentions


def test_transferred_recall_first_config_keeps_only_rx_and_sf_state() -> None:
    transferred = TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG
    assert transferred.direct_classes == frozenset(
        {RX_RECALL_EXPANSION, SF_STATE_VARIANT}
    )
    assert KEEP_RX_RECALL_EXPANSION in transferred.select_rule_ids
    assert KEEP_SF_STATE_VARIANT in transferred.select_rule_ids
    assert KEEP_DX_HEADING_DECOMPOSITION not in transferred.select_rule_ids
    assert KEEP_INV_RESULT_VARIANT not in transferred.select_rule_ids
    assert DIAGNOSIS_HEADING_DECOMPOSITION not in transferred.direct_classes
    assert INV_RESULT_VARIANT not in transferred.direct_classes
    frozen = RECALL_FIRST_THREE_STAGE_CONFIG
    assert DIAGNOSIS_HEADING_DECOMPOSITION in frozen.direct_classes
    assert INV_RESULT_VARIANT in frozen.direct_classes


def test_investigation_resultless_emission_and_paired_drop() -> None:
    letter = ExectLetter(
        "INV-RESULTLESS-RELOCATE",
        "An MRI was performed in 2016. The report is filed elsewhere. "
        "Her EEG showed generalised spike and wave discharges.",
    )
    accepted_recognise = ACCEPTED_THREE_STAGE_CONFIG.recognise
    assert accepted_recognise is not None
    relocated = ThreeStageConfig(
        recognise=replace(accepted_recognise, investigations_emit_resultless=True),
        select_rule_ids=(
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
            INVESTIGATION_RESULTLESS_DROP,
        ),
    )
    stops = three_stage_stop_mentions(letter, relocated)
    assert any(
        mention.entity == INVESTIGATIONS.name
        and mention.attributes.get("MRI_Performed") == "Yes"
        and "MRI_Results" not in mention.attributes
        for mention in stops.recognise
    )
    assert stops.select == run_letter(letter).comparison_projection.mentions


def test_sf_rateless_relocation_widens_recognise_and_preserves_select() -> None:
    letter = ExectLetter(
        "SF-RATELESS-RELOCATE",
        "She has focal seizures. No rate is given. Diagnosis: focal epilepsy.",
    )
    accepted_recognise = ACCEPTED_THREE_STAGE_CONFIG.recognise
    assert accepted_recognise is not None
    relocated = ThreeStageConfig(
        recognise=replace(accepted_recognise, sf_keep_unassociated_anchors=True),
        select_rule_ids=(
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
            SF_RATELESS_ANCHOR_DROP,
        ),
    )
    stops = three_stage_stop_mentions(letter, relocated)
    assert any(
        mention.entity == SEIZURE_FREQUENCY.name
        and mention.text.lower() == "focal seizures"
        and not _has_frequency_attrs(dict(mention.attributes))
        for mention in stops.recognise
    )
    assert stops.select == run_letter(letter).comparison_projection.mentions


def test_nested_ancestor_diagnosis_candidate_defers_epilepsy_inside_focal_epilepsy() -> None:
    letter = ExectLetter(
        "DX-NESTED-ANCESTOR",
        "Diagnosis: focal epilepsy with occasional nocturnal events.",
    )
    direct = extract_deterministic_all9(letter)
    direct_diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in direct.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert direct_diagnoses == ["focal epilepsy"]

    nested = diagnosis_mod.nested_ancestor_diagnosis_candidates(letter.note_text)
    assert len(nested) == 1
    assert nested[0].candidate_class == DIAGNOSIS_NESTED_ANCESTOR
    assert nested[0].rule_id == "recognise.diagnosis_nested_ancestor"
    assert canonicalize_diagnosis_concept(nested[0].mention.text) == "epilepsy"


def test_run_letter_three_stage_promotes_nested_ancestor_when_enabled() -> None:
    letter = ExectLetter(
        "DX-NESTED-PROMOTE",
        "Diagnosis: focal epilepsy with occasional nocturnal events.",
    )
    default = run_letter_three_stage(letter)
    m2 = run_letter_three_stage(
        letter,
        ThreeStageConfig(deferred_classes=frozenset({DIAGNOSIS_NESTED_ANCESTOR})),
    )
    default_diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in default.comparison_projection.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    m2_diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in m2.comparison_projection.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert default_diagnoses == ["focal epilepsy"]
    assert sorted(m2_diagnoses) == ["epilepsy", "focal epilepsy"]


def test_nested_ancestor_skips_when_parent_already_direct() -> None:
    letter = ExectLetter(
        "DX-NESTED-SKIP",
        "She has epilepsy. Later imaging confirmed focal epilepsy.",
    )
    direct = extract_deterministic_all9(letter)
    direct_diagnoses = sorted(
        canonicalize_diagnosis_concept(mention.text)
        for mention in direct.mentions
        if mention.entity == DIAGNOSIS.name
    )
    assert direct_diagnoses == ["epilepsy", "focal epilepsy"]

    nested = diagnosis_mod.nested_ancestor_diagnosis_candidates(letter.note_text)
    assert nested == ()
    ledger, _ = build_recognise_ledger(
        letter,
        enabled_deferred_classes=frozenset({DIAGNOSIS_NESTED_ANCESTOR}),
    )
    deferred_diagnoses = [
        canonicalize_diagnosis_concept(candidate.mention.text)
        for candidate in ledger.deferred_candidates()
        if candidate.mention.entity == DIAGNOSIS.name
    ]
    assert deferred_diagnoses == []


def test_sf_seizure_free_arm_promotes_orphan_with_verbatim_evidence() -> None:
    note = "She remains seizure free for six months."
    letter = ExectLetter("SF-ORPHAN-FREE", note)
    assert (
        run_letter_three_stage(letter).comparison_projection.mentions
        == run_letter_retune_stack(letter).comparison_projection.mentions
    )
    source = [
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "seizure",
            "evidence": "remains seizure free for six months",
            "attributes": {
                "NumberOfSeizures": "0",
                "NumberOfTimePeriods": "6",
                "TimePeriod": "Month",
                "CUI": "C1299590",
                "CUIPhrase": "seizure",
            },
            "candidate_class": SF_SEIZURE_FREE,
        }
    ]
    kept, actions = apply_select_rules(
        [],
        source_mentions=source,
        note_text=note,
        enabled_rule_ids=frozenset({SF_SUPPORTED_STATE_PROMOTION}),
    )
    assert len(kept) == 1
    assert kept[0]["evidence"] in note
    assert len(actions) == 1
    assert actions[0]["rule_id"] == SF_SUPPORTED_STATE_PROMOTION
    assert actions[0]["action"] == "add"
    assert actions[0]["portability"] == "seizure_frequency"


def test_sf_named_type_promotion_refuses_duplicate_inventory_unit() -> None:
    note = "Seizure type and frequency: focal seizures"
    selected = [
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "focal seizures",
            "evidence": "focal seizures",
            "attributes": {"CUI": "C0751495", "CUIPhrase": "focal seizures"},
        }
    ]
    source = [
        *selected,
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "focal seizures",
            "evidence": "focal seizures",
            "attributes": {"CUI": "C0751495", "CUIPhrase": "focal seizures"},
            "candidate_class": SF_NAMED_TYPE,
        },
    ]
    kept, actions = apply_select_rules(
        selected,
        source_mentions=source,
        note_text=note,
        enabled_rule_ids=frozenset({SF_SUPPORTED_STATE_PROMOTION}),
    )
    assert kept == selected
    assert actions == []


def test_sf_supported_promotion_inactive_without_deferred_class() -> None:
    note = (
        "Seizure type and frequency: focal seizures\n\n"
        "She remains seizure free for six months."
    )
    letter = ExectLetter("SF-NO-DEFER", note)
    without_deferred = run_letter_three_stage(
        letter,
        ThreeStageConfig(
            select_rule_ids=(*RULES_ONLY_SELECT_RULE_IDS, SF_SUPPORTED_STATE_PROMOTION),
        ),
    )
    assert (
        without_deferred.comparison_projection.mentions
        == run_letter_retune_stack(letter).comparison_projection.mentions
    )


def test_diagnosis_service_context_exclusion_skips_epilepsy_nurse() -> None:
    letter = ExectLetter("DX-NURSE", "She was seen by the epilepsy nurse.")
    default = extract_deterministic_all9(letter)
    excluded = extract_deterministic_all9(
        letter,
        diagnosis_service_context_exclusion=True,
    )
    default_diagnoses = [
        mention for mention in default.mentions if mention.entity == DIAGNOSIS.name
    ]
    excluded_diagnoses = [
        mention for mention in excluded.mentions if mention.entity == DIAGNOSIS.name
    ]
    assert default_diagnoses
    assert excluded_diagnoses == []


def test_diagnosis_service_context_exclusion_keeps_diagnostic_epilepsy() -> None:
    note = "Seen by the epilepsy nurse. His epilepsy is stable."
    letter = ExectLetter("DX-NURSE-KEEP", note)
    prediction = extract_deterministic_all9(
        letter,
        diagnosis_service_context_exclusion=True,
    )
    diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in prediction.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert diagnoses == ["epilepsy"]


def test_diagnosis_service_context_exclusion_skips_family_history() -> None:
    letter = ExectLetter("DX-FHX", "There is no family history of epilepsy.")
    default = extract_deterministic_all9(letter)
    excluded = extract_deterministic_all9(
        letter,
        diagnosis_service_context_exclusion=True,
    )
    assert [
        mention for mention in default.mentions if mention.entity == DIAGNOSIS.name
    ]
    assert [
        mention for mention in excluded.mentions if mention.entity == DIAGNOSIS.name
    ] == []


def test_diagnosis_secondary_to_retention_keeps_focal_epilepsy_before_cause() -> None:
    note = "He has focal epilepsy secondary to a traumatic brain injury."
    letter = ExectLetter("DX-SECONDARY", note)
    default = extract_deterministic_all9(letter)
    retained = extract_deterministic_all9(
        letter,
        diagnosis_secondary_to_retention=True,
    )
    default_diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in default.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    retained_diagnoses = [
        canonicalize_diagnosis_concept(mention.text)
        for mention in retained.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert "focal epilepsy" not in default_diagnoses
    assert "focal epilepsy" in retained_diagnoses


def test_diagnosis_focal_onset_alias_emits_focal_epilepsy_concept() -> None:
    letter = ExectLetter("DX-FOCAL-ONSET-ALIAS", "Diagnosis: Epilepsy - focal onset")
    default = extract_deterministic_all9(letter)
    aliased = extract_deterministic_all9(letter, diagnosis_focal_onset_alias=True)
    assert not [
        mention
        for mention in default.mentions
        if mention.entity == DIAGNOSIS.name
        and canonicalize_diagnosis_concept(mention.text) == "focal epilepsy"
    ]
    aliased_diagnoses = [
        mention
        for mention in aliased.mentions
        if mention.entity == DIAGNOSIS.name
    ]
    assert len(aliased_diagnoses) == 1
    assert aliased_diagnoses[0].attributes.get("CUI") == "C0014547"
    assert aliased_diagnoses[0].attributes.get("CUIPhrase") == "focal epilepsy"


def test_nondiagnostic_context_deferred_class_records_excluded_occurrence() -> None:
    letter = ExectLetter("DX-NONDX-DEFER", "She was seen by the epilepsy nurse.")
    ledger, _ = build_recognise_ledger(
        letter,
        enabled_deferred_classes=frozenset({DIAGNOSIS_NONDIAGNOSTIC_CONTEXT}),
    )
    deferred = [
        candidate
        for candidate in ledger.deferred_candidates()
        if candidate.candidate_class == DIAGNOSIS_NONDIAGNOSTIC_CONTEXT
    ]
    assert len(deferred) == 1
    assert deferred[0].rule_id == "recognise.diagnosis_nondiagnostic_context"


def test_sf_generic_duplicate_drop_removes_generic_when_named_type_same_rate() -> None:
    selected = [
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "seizures",
            "evidence": "3-4 generalised tonic clonic seizures per week",
            "attributes": {
                "LowerNumberOfSeizures": "3",
                "UpperNumberOfSeizures": "4",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Week",
                "CUI": "C0036572",
                "CUIPhrase": "seizures",
            },
        },
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "generalised tonic clonic seizures",
            "evidence": "3-4 generalised tonic clonic seizures per week",
            "attributes": {
                "LowerNumberOfSeizures": "3",
                "UpperNumberOfSeizures": "4",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Week",
                "During": "During",
                "CUI": "C0234549",
                "CUIPhrase": "generalised tonic clonic seizures",
            },
        },
    ]
    kept, actions = apply_select_rules(
        selected,
        source_mentions=selected,
        note_text=selected[0]["evidence"],
        enabled_rule_ids=frozenset({SF_GENERIC_DUPLICATE_DROP}),
    )
    assert len(kept) == 1
    assert kept[0]["text"] == "generalised tonic clonic seizures"
    assert actions[0]["rule_id"] == SF_GENERIC_DUPLICATE_DROP


def test_sf_generic_duplicate_drop_keeps_generic_with_different_rate() -> None:
    selected = [
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "seizures",
            "evidence": "two seizures per month",
            "attributes": {
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
                "CUI": "C0036572",
            },
        },
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "generalised tonic clonic seizures",
            "evidence": "3-4 generalised tonic clonic seizures per week",
            "attributes": {
                "LowerNumberOfSeizures": "3",
                "UpperNumberOfSeizures": "4",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Week",
                "CUI": "C0234549",
            },
        },
    ]
    kept, actions = apply_select_rules(
        selected,
        source_mentions=selected,
        note_text="two seizures per month; 3-4 generalised tonic clonic seizures per week",
        enabled_rule_ids=frozenset({SF_GENERIC_DUPLICATE_DROP}),
    )
    assert len(kept) == 2
    assert actions == []


def test_sf_seizure_free_positive_count_drop() -> None:
    selected = [
        {
            "entity": SEIZURE_FREQUENCY.name,
            "text": "seizure free",
            "evidence": "seizure free for 3 weeks after 4 seizures",
            "attributes": {
                "NumberOfSeizures": "4",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Week",
                "CUI": "C1299590",
                "CUIPhrase": "seizure free",
            },
        }
    ]
    kept, actions = apply_select_rules(
        selected,
        source_mentions=selected,
        note_text=selected[0]["evidence"],
        enabled_rule_ids=frozenset({SF_SEIZURE_FREE_POSITIVE_COUNT_DROP}),
    )
    assert kept == []
    assert actions[0]["rule_id"] == SF_SEIZURE_FREE_POSITIVE_COUNT_DROP


def test_family_select_plan_flattens_to_canonical_order() -> None:
    plan = {
        SEIZURE_FREQUENCY.name: (SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,),
        DIAGNOSIS.name: RULES_ONLY_SELECT_RULE_IDS,
        CROSS_FAMILY: (INVENTORY_WEAK_EPISODE_DROP,),
    }
    flattened = flatten_family_select_plan(plan)
    expected = set(ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids)
    assert set(flattened) == expected
    assert flattened == tuple(
        rule_id for rule_id in CANDIDATE_SELECT_RULE_IDS if rule_id in expected
    )
    with pytest.raises(ValueError):
        flatten_family_select_plan({DIAGNOSIS.name: (SF_RATELESS_ANCHOR_DROP,)})
    with pytest.raises(ValueError):
        flatten_family_select_plan({"NotAFamily": (SF_RATELESS_ANCHOR_DROP,)})


def test_family_configured_three_stage_matches_accepted_config() -> None:
    letter = ExectLetter(
        "DX-FAMILY-PLAN",
        "Diagnosis: epilepsy – probable focal. She remains seizure free "
        "for six months. A normal MRI in 2016.",
    )
    family_config = ThreeStageConfig(
        recognise=ACCEPTED_THREE_STAGE_CONFIG.recognise,
        family_select=(
            (DIAGNOSIS.name, RULES_ONLY_SELECT_RULE_IDS),
            (SEIZURE_FREQUENCY.name, (SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,)),
            (CROSS_FAMILY, (INVENTORY_WEAK_EPISODE_DROP,)),
        ),
        family_encoders=((DIAGNOSIS.name, (ENCODE_FORMAT_STACK,)),),
    )
    assert (
        run_letter_three_stage(letter, family_config).comparison_projection.mentions
        == run_letter(letter).comparison_projection.mentions
    )


def test_three_stage_stop_reader_select_stop_equals_run_letter() -> None:
    letter = ExectLetter(
        "DX-STOP-READER",
        "Diagnosis: epilepsy – probable focal. EEG was abnormal. "
        "She was seen by the epilepsy nurse.",
    )
    stops = three_stage_stop_mentions(letter, ACCEPTED_THREE_STAGE_CONFIG)
    assert stops.select == run_letter(letter).comparison_projection.mentions
    assert any(mention.entity == DIAGNOSIS.name for mention in stops.recognise)
    non_diagnosis_recognise = tuple(
        mention for mention in stops.recognise if mention.entity != DIAGNOSIS.name
    )
    non_diagnosis_encode = tuple(
        mention for mention in stops.encode if mention.entity != DIAGNOSIS.name
    )
    assert non_diagnosis_recognise == non_diagnosis_encode


def test_run_letter_three_stage_default_recognise_config_matches_comparator() -> None:
    letter = ExectLetter(
        "DX-DEFAULT-PARITY",
        "Diagnosis: epilepsy – probable focal. She was seen by the epilepsy nurse.",
    )
    assert (
        run_letter_three_stage(letter).comparison_projection.mentions
        == run_letter_retune_stack(letter).comparison_projection.mentions
    )
    assert (
        run_letter(letter).comparison_projection.mentions
        == run_letter_three_stage(
            letter, ACCEPTED_THREE_STAGE_CONFIG
        ).comparison_projection.mentions
    )
    assert (
        run_letter(letter).comparison_projection.mentions
        != run_letter_retune_stack(letter).comparison_projection.mentions
    )
