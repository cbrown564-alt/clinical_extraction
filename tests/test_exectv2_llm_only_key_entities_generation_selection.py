"""Tests for the attribution-clean Qwen generation-selection key-entity route."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_generation_selection as route,
)
from tests.helpers.prompt_hygiene import FORBIDDEN_PHRASES

_NOTE = (
    "She has focal epilepsy. "
    "Current treatment is lamotrigine 200 mg twice daily. "
    "MRI brain was normal."
)
_LETTER = ExectLetter(
    letter_id="TEST001",
    note_text=_NOTE,
    annotations=(
        ExectAnnotation(
            entity=DIAGNOSIS.name,
            text="focal epilepsy",
            attributes={
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
        ),
    ),
)


def test_generation_prompt_is_note_only_and_attribution_clean() -> None:
    payload_str = route.build_generation_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["prompt_version"] == route.PROMPT_VERSION
    assert payload["architecture"]["pipeline_family"] == route.PIPELINE_FAMILY
    assert payload["architecture"]["generation_owner"] == "target_model"
    assert payload["architecture"]["selection_owner"] == "target_model"
    assert payload["stage"] == "generation"
    assert payload["letter"]["note_text"] == _NOTE
    example_text = " ".join(example["note_fragment"] for example in payload["worked_examples"])
    assert "Current treatment is lamotrigine" in example_text
    assert "MRI brain was normal" in example_text
    assert "repeat MRI scan next year" in example_text
    assert "SeizureFrequency" in payload["mention_attribute_contract"]
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "first_pass_model_events" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_selection_prompt_uses_only_letter_and_first_pass_model_events() -> None:
    first_pass = {
        "clinical_events": [
            {
                "family": "medication",
                "anchor_text": "lamotrigine",
                "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                "mentions": [
                    {
                        "entity": PRESCRIPTION.name,
                        "text": "lamotrigine 200 mg twice daily",
                        "attributes": {
                            "DrugName": "lamotrigine",
                            "DrugDose": "200",
                            "DoseUnit": "mg",
                            "Frequency": "2",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "Current treatment is stated.",
            }
        ]
    }

    payload_str = route.build_selection_prompt_input(_LETTER, first_pass)
    payload = json.loads(payload_str)

    assert payload["stage"] == "selection"
    assert payload["letter"]["note_text"] == _NOTE
    assert payload["first_pass_model_events"][0]["anchor_text"] == "lamotrigine"
    selection_text = " ".join(payload["selection_instructions"])
    assert "Preserve a supported first-pass event" in selection_text
    assert "event_state is transparency only" in selection_text
    assert "revise" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str


def test_single_call_inventory_prompt_has_generated_and_final_surfaces() -> None:
    payload_str = route.build_single_call_inventory_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_inventory_selection"
    assert payload["architecture"]["name"] == "llm_only_single_call_inventory_selection"
    assert "generated_events" in payload["output_schema"]
    assert "final_events" in payload["output_schema"]
    assert payload["forbidden_attribute_combinations"][0]["entity"] == "SeizureFrequency"
    assert "NumberOfTimePeriods" in payload["forbidden_attribute_combinations"][0]["forbid"]
    assert payload["letter"]["note_text"] == _NOTE
    clinical_rules = " ".join(payload["clinical_rules"])
    assert "MonthDate must be numeric" in clinical_rules
    assert "temporal lobe epilepsy" in clinical_rules
    assert "Do not de-duplicate repeated source-supported facts" in clinical_rules
    assert "emit both a Diagnosis mention" in clinical_rules
    assert "LowerNumberOfSeizures and UpperNumberOfSeizures" in clinical_rules
    assert "Retain prior completed MRI" in clinical_rules
    assert "Keep the repeated mentions instead of merging them" in clinical_rules
    assert "include the modality plus test word" in clinical_rules
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str


def test_single_call_mentions_prompt_has_generated_and_final_surfaces() -> None:
    payload_str = route.build_single_call_mentions_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_mention_selection"
    assert payload["architecture"]["name"] == "llm_only_single_call_mention_selection"
    assert "generated_mentions" in payload["output_schema"]
    assert "final_mentions" in payload["output_schema"]
    assert payload["letter"]["note_text"] == _NOTE
    selection_text = " ".join(payload["selection_instructions"])
    assert "Generate broadly" in selection_text
    assert "attributes object" in selection_text
    assert "different sections" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_single_call_per_entity_mentions_prompt_is_entity_scoped() -> None:
    payload_str = route.build_single_call_per_entity_mentions_prompt_input(
        _LETTER,
        target_entity=DIAGNOSIS.name,
    )
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_per_entity_mention_selection"
    assert payload["architecture"]["name"] == (
        "llm_only_single_call_per_entity_mention_selection"
    )
    assert payload["target_entity"] == DIAGNOSIS.name
    assert payload["target_entities"] == [DIAGNOSIS.name]
    assert "generated_mentions" in payload["output_schema"]
    assert "final_mentions" in payload["output_schema"]
    contract_text = " ".join(payload["model_origin_contract"])
    assert "Diagnosis mention" in contract_text
    assert "Do not emit mentions for other entities" in contract_text
    selection_text = " ".join(payload["selection_instructions"])
    assert "entity Diagnosis" in selection_text
    assert "Generate broadly for Diagnosis" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_single_call_typed_mentions_prompt_has_typed_surfaces() -> None:
    payload_str = route.build_single_call_typed_mentions_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_typed_mention_selection"
    assert payload["architecture"]["name"] == "llm_only_single_call_typed_mention_selection"
    assert "generated_typed_mentions" in payload["output_schema"]
    assert "final_typed_mentions" in payload["output_schema"]
    generated_schema = payload["output_schema"]["generated_typed_mentions"][0]
    assert "DrugName" in generated_schema
    assert "LowerNumberOfSeizures" in generated_schema
    selection_text = " ".join(payload["selection_instructions"])
    assert "Use the typed fields directly" in selection_text
    assert "LowerNumberOfSeizures" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_single_call_mention_ids_prompt_selects_generated_ids() -> None:
    payload_str = route.build_single_call_mention_ids_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_mention_id_selection"
    assert payload["architecture"]["name"] == "llm_only_single_call_mention_id_selection"
    assert "generated_mentions" in payload["output_schema"]
    assert "final_mention_ids" in payload["output_schema"]
    assert payload["output_schema"]["generated_mentions"][0]["mention_id"]
    assert payload["letter"]["note_text"] == _NOTE
    selection_text = " ".join(payload["selection_instructions"])
    assert "select conservatively by mention_id" in selection_text
    assert "Keep repeated source-supported mentions" in selection_text
    contract_text = " ".join(payload["model_origin_contract"])
    assert "Do not rewrite selected mentions" in contract_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_single_call_render_ids_prompt_has_model_render_policy() -> None:
    payload_str = route.build_single_call_render_ids_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_render_id_selection"
    assert payload["architecture"]["name"] == "llm_only_single_call_render_id_selection"
    assert "generated_mentions" in payload["output_schema"]
    assert "final_mention_ids" in payload["output_schema"]
    generated_schema = payload["output_schema"]["generated_mentions"][0]
    assert "source_text" in generated_schema
    assert generated_schema["text"] == "final rendered mention text for this clinical fact"
    render_policy = " ".join(payload["render_text_policy"])
    assert "final rendered mention text" in render_policy
    assert "does not need to be an exact source substring" in render_policy
    assert "Split compound diagnosis headings" in render_policy
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_single_call_clean_render_ids_prompt_has_source_and_clean_text() -> None:
    payload_str = route.build_single_call_clean_render_ids_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_clean_render_id_selection"
    assert payload["architecture"]["name"] == (
        "llm_only_single_call_clean_render_id_selection"
    )
    assert "generated_mentions" in payload["output_schema"]
    assert "final_mention_ids" in payload["output_schema"]
    generated_schema = payload["output_schema"]["generated_mentions"][0]
    assert generated_schema["source_text"] == "short exact source span naming the fact"
    assert generated_schema["clean_text"] == "compact final mention text for this clinical fact"
    clean_policy = " ".join(payload["clean_text_policy"])
    assert "source_text must be copied from the letter" in clean_policy
    assert "clean_text should be a compact clinical label" in clean_policy
    assert "separate mention_id values" in clean_policy
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_single_call_per_entity_clean_render_ids_prompt_is_entity_scoped() -> None:
    payload_str = route.build_single_call_per_entity_clean_render_ids_prompt_input(
        _LETTER,
        target_entity=DIAGNOSIS.name,
    )
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_per_entity_clean_render_id_selection"
    assert payload["architecture"]["name"] == (
        "llm_only_single_call_per_entity_clean_render_id_selection"
    )
    assert payload["target_entity"] == DIAGNOSIS.name
    assert payload["target_entities"] == [DIAGNOSIS.name]
    assert "generated_mentions" in payload["output_schema"]
    assert "final_mention_ids" in payload["output_schema"]
    contract_text = " ".join(payload["model_origin_contract"])
    assert "Diagnosis fact" in contract_text
    assert "Do not emit mentions for other entities" in contract_text
    selection_text = " ".join(payload["selection_instructions"])
    assert "Generate broadly for Diagnosis" in selection_text
    assert "Every generated_mentions item must have entity Diagnosis" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_qwen_pool_adjudication_prompt_uses_prior_qwen_mentions_only() -> None:
    pool = [
        {
            "mention_id": "run1_structured_mentions_generation_1",
            "source_run": "run1",
            "source_surface": "structured_mentions_generation",
            "entity": DIAGNOSIS.name,
            "text": "focal epilepsy",
            "attributes": {
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
            "evidence": "She has focal epilepsy.",
            "confidence": "high",
            "rationale": "Directly stated.",
        }
    ]

    payload_str = route.build_qwen_pool_adjudication_prompt_input(_LETTER, pool)
    payload = json.loads(payload_str)

    assert payload["stage"] == "qwen_pool_adjudication"
    assert payload["architecture"]["name"] == "llm_only_qwen_pool_self_adjudication"
    assert payload["model_generated_mentions"][0]["mention_id"] == pool[0]["mention_id"]
    assert payload["model_generated_mentions"][0]["source_run"] == "run1"
    assert "final_mention_ids" in payload["output_schema"]
    contract_text = " ".join(payload["model_origin_contract"])
    assert "prior Qwen model-emitted mentions" in contract_text
    assert "Do not emit new mention objects" in contract_text
    selection_text = " ".join(payload["selection_instructions"])
    assert "Do not select every valid row" in selection_text
    assert "source_run or source_surface values are provenance only" in selection_text
    assert "select exactly one ID for that fact" in selection_text
    assert "structured_mentions_final" in selection_text
    assert "under 18 words" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_qwen_pool_entity_adjudication_prompt_is_entity_scoped() -> None:
    pool = [
        {
            "mention_id": "run1_mg_1",
            "source_run": "run1",
            "source_surface": "structured_mentions_generation",
            "entity": DIAGNOSIS.name,
            "text": "focal epilepsy",
            "attributes": {
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
            "evidence": "She has focal epilepsy.",
            "confidence": "high",
            "rationale": "Directly stated.",
        }
    ]

    payload_str = route.build_qwen_pool_entity_adjudication_prompt_input(
        _LETTER,
        pool,
        target_entity=DIAGNOSIS.name,
    )
    payload = json.loads(payload_str)

    assert payload["stage"] == "qwen_pool_entity_adjudication"
    assert payload["architecture"]["name"] == (
        "llm_only_qwen_pool_entity_self_adjudication"
    )
    assert payload["target_entity"] == DIAGNOSIS.name
    assert payload["target_entities"] == [DIAGNOSIS.name]
    assert payload["model_generated_mentions"][0]["entity"] == DIAGNOSIS.name
    contract_text = " ".join(payload["model_origin_contract"])
    assert "prior Qwen model-emitted Diagnosis mentions" in contract_text
    assert "same fact across source_run values are duplicates" in contract_text
    selection_text = " ".join(payload["selection_instructions"])
    assert "Select only final Diagnosis IDs" in selection_text
    assert "Reject rows for other entities" in selection_text
    assert "source_run or source_surface values are provenance only" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_qwen_pool_group_adjudication_prompt_requires_fact_groups() -> None:
    pool = [
        {
            "mention_id": "run1_mg_1",
            "source_run": "run1",
            "source_surface": "structured_mentions_generation",
            "entity": DIAGNOSIS.name,
            "text": "focal epilepsy",
            "attributes": {
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
            "evidence": "She has focal epilepsy.",
            "confidence": "high",
            "rationale": "Directly stated.",
        }
    ]

    payload_str = route.build_qwen_pool_group_adjudication_prompt_input(
        _LETTER,
        pool,
    )
    payload = json.loads(payload_str)

    assert payload["stage"] == "qwen_pool_group_adjudication"
    assert payload["architecture"]["name"] == "llm_only_qwen_pool_group_self_adjudication"
    assert "fact_groups" in payload["output_schema"]
    assert payload["model_generated_mentions"][0]["mention_id"] == "run1_mg_1"
    contract_text = " ".join(payload["model_origin_contract"])
    assert "group rows that describe the same clinical fact" in contract_text
    assert "representative_mention_id" in contract_text
    selection_text = " ".join(payload["selection_instructions"])
    assert "Return fact_groups, not a flat list" in selection_text
    assert "one included group per source run" in selection_text
    assert "candidate_evidence_ledger" not in payload
    assert "high_priority_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []


def test_parse_single_call_inventory_preserves_generated_and_final_events() -> None:
    raw = json.dumps(
        {
            "generated_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": "focal epilepsy",
                    "evidence": "She has focal epilepsy.",
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "focal epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": 5,
                                "Negation": "Affirmed",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "Directly stated.",
                }
            ],
            "final_events": [],
            "selection_summary": [
                {
                    "final_anchor_text": "focal epilepsy",
                    "source": "rejected",
                    "reason": "unit-test selection omission",
                }
            ],
        }
    )

    record, errors = route.parse_generation_selection_json(raw)

    assert record is not None
    assert errors == [
        "generated_events:coerced_attribute_value: "
        "event[0].mentions[0].attributes.Certainty 5 -> '5'"
    ]
    assert record.generated_events[0].mentions[0].attributes["Certainty"] == "5"
    assert route.final_record_from_generation_selection(record).clinical_events == []


def test_parse_single_call_mentions_preserves_generated_and_final_mentions() -> None:
    raw = json.dumps(
        {
            "generated_mentions": [
                {
                    "entity": DIAGNOSIS.name,
                    "text": "focal epilepsy",
                    "evidence": "She has focal epilepsy.",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": 5,
                        "Negation": "Affirmed",
                    },
                    "confidence": "high",
                    "rationale": "Directly stated.",
                }
            ],
            "final_mentions": [],
            "selection_summary": [
                {
                    "final_text": "focal epilepsy",
                    "source": "rejected",
                    "reason": "unit-test selection omission",
                }
            ],
        }
    )

    record, errors = route.parse_generation_selection_mentions_json(raw)

    assert record is not None
    assert errors == [
        "coerced_attribute_value: "
        "generated_mentions.mention[0].attributes.Certainty 5 -> '5'"
    ]
    assert record.generated_mentions[0].attributes["Certainty"] == "5"
    assert route.final_mentions_from_generation_selection(record) == []


def test_parse_single_call_typed_mentions_maps_fields_to_attributes() -> None:
    raw = json.dumps(
        {
            "generated_typed_mentions": [
                {
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 200 mg twice daily",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                    "DrugName": "lamotrigine",
                    "DrugDose": 200,
                    "DoseUnit": "mg",
                    "Frequency": 2,
                    "confidence": "high",
                    "rationale": "Current treatment is stated.",
                }
            ],
            "final_typed_mentions": [
                {
                    "entity": DIAGNOSIS.name,
                    "text": "focal epilepsy",
                    "evidence": "She has focal epilepsy.",
                    "DiagCategory": "Epilepsy",
                    "Certainty": 5,
                    "Negation": "Affirmed",
                    "confidence": "high",
                    "rationale": "Directly stated.",
                }
            ],
            "selection_summary": [
                {
                    "final_text": "focal epilepsy",
                    "source": "kept",
                    "reason": "supported",
                }
            ],
        }
    )

    record, errors = route.parse_generation_selection_typed_mentions_json(raw)

    assert record is not None
    assert record.generated_mentions[0].attributes["DrugDose"] == "200"
    assert record.generated_mentions[0].attributes["Frequency"] == "2"
    assert record.final_mentions[0].attributes["Certainty"] == "5"
    assert record.selection_summary[0]["source"] == "kept"
    assert any("DrugDose 200 -> '200'" in error for error in errors)


def test_parse_single_call_mention_ids_preserves_generated_mentions_and_ids() -> None:
    raw = json.dumps(
        {
            "generated_mentions": [
                {
                    "mention_id": "m1",
                    "entity": DIAGNOSIS.name,
                    "source_text": "focal epilepsy",
                    "text": "focal epilepsy",
                    "evidence": "She has focal epilepsy.",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": 5,
                        "Negation": "Affirmed",
                    },
                    "confidence": "high",
                    "rationale": "Directly stated.",
                },
                {
                    "mention_id": "m2",
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 200 mg twice daily",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "200",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                    "confidence": "high",
                    "rationale": "Current treatment is stated.",
                },
            ],
            "final_mention_ids": ["m2", "m1"],
            "selection_summary": [
                {"mention_id": "m1", "decision": "keep", "reason": "supported"}
            ],
        }
    )

    record, errors = route.parse_generation_selection_mention_ids_json(raw)

    assert record is not None
    assert errors == [
        "coerced_attribute_value: "
        "generated_mentions.mention[0].attributes.Certainty 5 -> '5'"
    ]
    assert record.generated_mentions[0]["mention_id"] == "m1"
    assert record.generated_mentions[0]["source_text"] == "focal epilepsy"
    assert record.generated_mentions[0]["attributes"]["Certainty"] == "5"
    assert record.final_mention_ids == ["m2", "m1"]

    selected, selection_errors = route.final_mentions_from_mention_id_selection(record)
    assert selection_errors == []
    assert [mention.text for mention in selected] == [
        "lamotrigine 200 mg twice daily",
        "focal epilepsy",
    ]


def test_parse_clean_render_ids_uses_model_clean_text_alias() -> None:
    raw = json.dumps(
        {
            "generated_mentions": [
                {
                    "mention_id": "m1",
                    "entity": DIAGNOSIS.name,
                    "source_text": "focal epilepsy",
                    "clean_text": "focal epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "confidence": "high",
                    "rationale": "Directly stated.",
                }
            ],
            "final_mention_ids": ["m1"],
        }
    )

    record, errors = route.parse_generation_selection_clean_render_ids_json(raw)

    assert record is not None
    assert record.generated_mentions[0]["text"] == "focal epilepsy"
    assert record.generated_mentions[0]["evidence"] == "focal epilepsy"
    assert record.final_mention_ids == ["m1"]
    assert "generated_mentions.mention[0].clean_text:used_as_text" in errors
    assert "generated_mentions.mention[0].source_text:used_as_evidence" in errors


def test_mention_id_selection_drops_unknown_ids_without_fallback() -> None:
    record = route.StructuredMentionIdSelectionRecord(
        generated_mentions=[
            {
                "mention_id": "m1",
                "entity": DIAGNOSIS.name,
                "text": "focal epilepsy",
                "evidence": "She has focal epilepsy.",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
            }
        ],
        final_mention_ids=["missing"],
    )

    selected, selection_errors = route.final_mentions_from_mention_id_selection(record)

    assert selected == []
    assert selection_errors == ["unknown_final_mention_id: missing"]


def test_parse_qwen_pool_adjudication_preserves_selected_ids_only() -> None:
    raw = json.dumps(
        {
            "final_mention_ids": ["pool_m2", "pool_m1"],
            "selection_summary": [
                {
                    "mention_id": "pool_m2",
                    "decision": "keep",
                    "reason": "Complete current prescription attributes.",
                }
            ],
        }
    )

    record, errors = route.parse_qwen_pool_adjudication_json(raw)

    assert record is not None
    assert errors == []
    assert record.final_mention_ids == ["pool_m2", "pool_m1"]
    assert record.selection_summary[0]["decision"] == "keep"


def test_parse_qwen_pool_group_adjudication_uses_included_representatives() -> None:
    raw = json.dumps(
        {
            "fact_groups": [
                {
                    "group_id": "g1",
                    "decision": "include",
                    "representative_mention_id": "pool_m2",
                    "equivalent_mention_ids": ["pool_m1", "pool_m2"],
                    "reason": "Best complete attributes.",
                },
                {
                    "group_id": "g2",
                    "decision": "exclude",
                    "representative_mention_id": "pool_m3",
                    "equivalent_mention_ids": "pool_m3",
                    "reason": "Future-only mention.",
                },
                {
                    "group_id": "g3",
                    "decision": "include",
                    "equivalent_mention_ids": ["pool_m4"],
                    "reason": "Missing representative should not fallback.",
                },
            ]
        }
    )

    record, errors = route.parse_qwen_pool_group_adjudication_json(raw)

    assert record is not None
    assert record.final_mention_ids == ["pool_m2"]
    assert record.fact_groups[1]["equivalent_mention_ids"] == ["pool_m3"]
    assert record.selection_summary[0]["mention_id"] == "pool_m2"
    assert (
        "fact_groups.group[1].equivalent_mention_ids:coerced_string_to_list"
        in errors
    )
    assert (
        "fact_groups:included_group_missing_representative_id: group[2]"
        in errors
    )


def test_parse_qwen_pool_group_adjudication_accepts_model_final_id_alias() -> None:
    raw = json.dumps(
        {
            "final_mention_ids": ["pool_m1", "pool_m2"],
            "selection_summary": ["Selected the best supported rows."],
        }
    )

    record, errors = route.parse_qwen_pool_group_adjudication_json(raw)

    assert record is not None
    assert record.fact_groups == []
    assert record.final_mention_ids == ["pool_m1", "pool_m2"]
    assert record.selection_summary == [{"reason": "Selected the best supported rows."}]
    assert "fact_groups:used_model_emitted_final_mention_ids_alias" in errors


def test_model_generated_mentions_from_row_uses_raw_qwen_surfaces() -> None:
    row = {
        "letter_id": "TEST001",
        "structured_mentions_generation": [
            {
                "mention_id": "m1",
                "entity": DIAGNOSIS.name,
                "text": "focal epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": 5,
                    "Negation": "Affirmed",
                    "CUI": "C001",
                },
                "evidence": "She has focal epilepsy.",
                "confidence": "high",
                "rationale": "Directly stated.",
            }
        ],
        "structured_mentions_final": [
            {
                "entity": PRESCRIPTION.name,
                "text": "lamotrigine 200 mg twice daily",
                "attributes": {
                    "DrugName": "lamotrigine",
                    "DrugDose": "200",
                    "DoseUnit": "mg",
                    "Frequency": 2,
                },
                "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
            }
        ],
        "predicted_mentions": [
            {
                "entity": DIAGNOSIS.name,
                "text": "projected scorer row",
                "attributes": {"CUI": "projected"},
                "evidence": "She has focal epilepsy.",
            }
        ],
        "structured_events_final": [
            {
                "family": "diagnosis",
                "anchor_text": "temporal lobe epilepsy",
                "evidence": "She has focal epilepsy.",
                "mentions": [
                    {
                        "entity": DIAGNOSIS.name,
                        "text": "event-flattened diagnosis",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "4",
                            "Negation": "Affirmed",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "Event surface.",
            }
        ],
    }

    pool = route.model_generated_mentions_from_row(
        row,
        source_run="prior_qwen_run",
        source_row=7,
    )

    assert len(pool) == 3
    assert pool[0]["mention_id"] == "prior_qwen_run_mg_1"
    assert pool[0]["original_mention_id"] == "m1"
    assert pool[0]["source_surface"] == "structured_mentions_generation"
    assert pool[0]["source_row"] == 7
    assert pool[0]["attributes"]["Certainty"] == "5"
    assert "CUI" not in pool[0]["attributes"]
    assert all(mention["text"] != "projected scorer row" for mention in pool)
    assert pool[2]["source_surface"] == "structured_events_final"

    mention_only_pool = route.model_generated_mentions_from_row(
        row,
        source_run="prior_qwen_run",
        source_row=7,
        include_event_surfaces=False,
    )
    assert len(mention_only_pool) == 2
    assert all(
        mention["source_surface"] != "structured_events_final"
        for mention in mention_only_pool
    )


def test_final_record_projection_marks_target_model_origin() -> None:
    final_record = {
        "clinical_events": [
            {
                "family": "diagnosis",
                "anchor_text": "focal epilepsy",
                "evidence": "She has focal epilepsy.",
                "mentions": [
                    {
                        "entity": DIAGNOSIS.name,
                        "text": "focal epilepsy",
                        "attributes": {
                            "DiagCategory": "Epilepsy",
                            "Certainty": "5",
                            "Negation": "Affirmed",
                        },
                    }
                ],
                "confidence": "high",
                "rationale": "The diagnosis is directly stated.",
            }
        ]
    }

    predicted, warnings = route.to_predicted_letter(_LETTER, final_record)
    row = route.row_from_final_record(
        _LETTER,
        final_record,
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        mode="unit",
    )

    assert warnings == []
    assert predicted.diagnostics["pipeline_family"] == route.PIPELINE_FAMILY
    assert predicted.mentions[0].component_owner == route.COMPONENT_OWNER
    assert row["pipeline_family"] == route.PIPELINE_FAMILY
    assert row["fact_origin"] == route.FACT_ORIGIN
    assert row["predicted_mentions"][0]["component_owner"] == route.COMPONENT_OWNER
    assert row["predicted_mentions"][0]["entity"] == DIAGNOSIS.name


def test_final_mentions_projection_marks_target_model_origin() -> None:
    final_mentions = [
        {
            "entity": DIAGNOSIS.name,
            "text": "focal epilepsy",
            "evidence": "She has focal epilepsy.",
            "attributes": {
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
            "confidence": "high",
            "rationale": "The diagnosis is directly stated.",
        }
    ]

    predicted, warnings = route.to_predicted_letter_from_mentions(_LETTER, final_mentions)
    row = route.row_from_final_mentions(
        _LETTER,
        final_mentions,
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        mode="unit",
    )

    assert warnings == []
    assert predicted.diagnostics["pipeline_family"] == route.PIPELINE_FAMILY
    assert predicted.mentions[0].component_owner == route.COMPONENT_OWNER
    assert row["fact_origin"] == route.FACT_ORIGIN
    assert row["structured_events_final"] == []
    assert row["structured_mentions_final"][0]["entity"] == DIAGNOSIS.name
    assert row["predicted_mentions"][0]["component_owner"] == route.COMPONENT_OWNER


def test_final_selection_record_is_authoritative_for_projection() -> None:
    final_record = {"clinical_events": []}

    row = route.row_from_final_record(
        _LETTER,
        final_record,
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        mode="unit",
    )

    assert row["n_events_final"] == 0
    assert row["predicted_mentions"] == []
    assert row["fact_origin"] == route.FACT_ORIGIN


def test_prompt_only_run_split_records_generation_selection_prompts(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="two_stage",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    generation_prompt = json.loads(row["generation_prompt_input_json"])
    selection_prompt = json.loads(row["selection_prompt_input_json"])
    assert generation_prompt["stage"] == "generation"
    assert selection_prompt["stage"] == "selection"
    assert selection_prompt["first_pass_model_events"] == []
    assert row["pipeline_family"] == route.PIPELINE_FAMILY
    assert row["fact_origin"] == route.FACT_ORIGIN
    assert metadata["summary"]["generation_parse_failures"] == 0
    assert metadata["summary"]["selection_parse_failures"] == 0
    assert "model_preserving_canonical" in report_path.read_text(encoding="utf-8")


def test_prompt_only_single_call_inventory_records_inventory_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_inventory",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    inventory_prompt = json.loads(row["inventory_prompt_input_json"])
    assert inventory_prompt["stage"] == "single_call_inventory_selection"
    assert row["call_strategy"] == "single_call_inventory"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_events_generation"] == []
    assert row["structured_events_final"] == []
    assert metadata["call_strategy"] == "single_call_inventory"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_inventory`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_single_call_mentions_records_mention_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_mentions",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    mention_prompt = json.loads(row["inventory_prompt_input_json"])
    assert mention_prompt["stage"] == "single_call_mention_selection"
    assert row["call_strategy"] == "single_call_mentions"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_events_final"] == []
    assert row["structured_mentions_generation"] == []
    assert row["structured_mentions_final"] == []
    assert metadata["call_strategy"] == "single_call_mentions"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_mentions`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_single_call_per_entity_mentions_records_entity_prompts(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_per_entity_mentions",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    prompt_bundle = json.loads(row["inventory_prompt_input_json"])
    assert prompt_bundle["stage"] == "single_call_per_entity_mention_selection"
    entity_prompts = prompt_bundle["entity_prompt_inputs"]
    assert entity_prompts[DIAGNOSIS.name]["target_entity"] == DIAGNOSIS.name
    assert entity_prompts[PRESCRIPTION.name]["target_entity"] == PRESCRIPTION.name
    assert row["call_strategy"] == "single_call_per_entity_mentions"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_mentions_generation"] == []
    assert row["structured_mentions_final"] == []
    assert row["n_entity_calls"] == len(route.structured.KEY_ENTITY_NAMES)
    assert metadata["call_strategy"] == "single_call_per_entity_mentions"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_per_entity_mentions`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_single_call_typed_mentions_records_typed_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_typed_mentions",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    typed_prompt = json.loads(row["inventory_prompt_input_json"])
    assert typed_prompt["stage"] == "single_call_typed_mention_selection"
    assert "generated_typed_mentions" in typed_prompt["output_schema"]
    assert row["call_strategy"] == "single_call_typed_mentions"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_mentions_generation"] == []
    assert row["structured_mentions_final"] == []
    assert metadata["call_strategy"] == "single_call_typed_mentions"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_typed_mentions`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_single_call_mention_ids_records_id_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_mention_ids",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    mention_prompt = json.loads(row["inventory_prompt_input_json"])
    assert mention_prompt["stage"] == "single_call_mention_id_selection"
    assert row["call_strategy"] == "single_call_mention_ids"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_events_final"] == []
    assert row["structured_mentions_generation"] == []
    assert row["structured_mentions_final"] == []
    assert row["final_mention_ids"] == []
    assert metadata["call_strategy"] == "single_call_mention_ids"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_mention_ids`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_single_call_render_ids_records_render_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_render_ids",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    render_prompt = json.loads(row["inventory_prompt_input_json"])
    assert render_prompt["stage"] == "single_call_render_id_selection"
    assert "render_text_policy" in render_prompt
    assert row["call_strategy"] == "single_call_render_ids"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_events_final"] == []
    assert row["structured_mentions_generation"] == []
    assert row["structured_mentions_final"] == []
    assert row["final_mention_ids"] == []
    assert metadata["call_strategy"] == "single_call_render_ids"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_render_ids`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_single_call_clean_render_ids_records_clean_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_clean_render_ids",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    clean_prompt = json.loads(row["inventory_prompt_input_json"])
    assert clean_prompt["stage"] == "single_call_clean_render_id_selection"
    assert "clean_text_policy" in clean_prompt
    assert row["call_strategy"] == "single_call_clean_render_ids"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_events_final"] == []
    assert row["structured_mentions_generation"] == []
    assert row["structured_mentions_final"] == []
    assert row["final_mention_ids"] == []
    assert metadata["call_strategy"] == "single_call_clean_render_ids"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_clean_render_ids`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_single_call_per_entity_clean_render_ids_records_entity_prompts(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_per_entity_clean_render_ids",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    prompt_bundle = json.loads(row["inventory_prompt_input_json"])
    assert prompt_bundle["stage"] == "single_call_per_entity_clean_render_id_selection"
    entity_prompts = prompt_bundle["entity_prompt_inputs"]
    assert entity_prompts[DIAGNOSIS.name]["target_entity"] == DIAGNOSIS.name
    assert entity_prompts[PRESCRIPTION.name]["target_entity"] == PRESCRIPTION.name
    assert row["call_strategy"] == "single_call_per_entity_clean_render_ids"
    assert row["selection_prompt_input_json"] == ""
    assert row["structured_mentions_generation"] == []
    assert row["structured_mentions_final"] == []
    assert row["final_mention_ids_by_entity"][DIAGNOSIS.name] == []
    assert row["n_entity_calls"] == len(route.structured.KEY_ENTITY_NAMES)
    assert metadata["call_strategy"] == "single_call_per_entity_clean_render_ids"
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_per_entity_clean_render_ids`" in (
        report_path.read_text(encoding="utf-8")
    )


def test_prompt_only_qwen_pool_adjudication_records_pool_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"
    pool_mentions = {
        "TEST001": [
            {
                "mention_id": "pool_m1",
                "source_run": "prior_qwen_run",
                "source_surface": "structured_mentions_generation",
                "entity": DIAGNOSIS.name,
                "text": "focal epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "She has focal epilepsy.",
                "confidence": "high",
                "rationale": "Directly stated.",
            }
        ]
    }

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="qwen_pool_adjudication",
        pool_mentions_by_letter=pool_mentions,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    pool_prompt = json.loads(row["inventory_prompt_input_json"])
    assert pool_prompt["stage"] == "qwen_pool_adjudication"
    assert pool_prompt["model_generated_mentions"][0]["mention_id"] == "pool_m1"
    assert row["call_strategy"] == "qwen_pool_adjudication"
    assert row["generation_prompt_input_json"] == ""
    assert json.loads(row["selection_prompt_input_json"]) == pool_prompt
    assert row["structured_mentions_generation"][0]["mention_id"] == "pool_m1"
    assert row["structured_mentions_final"] == []
    assert row["final_mention_ids"] == []
    assert row["pool_size"] == 1
    assert metadata["pool_letters"] == 1
    assert metadata["pool_mentions_total"] == 1
    assert metadata["summary"]["selection_parse_failures"] == 0
    assert "Call strategy: `qwen_pool_adjudication`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_qwen_pool_entity_adjudication_records_entity_prompts(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"
    pool_mentions = {
        "TEST001": [
            {
                "mention_id": "pool_dx_1",
                "source_run": "prior_qwen_run",
                "source_surface": "structured_mentions_generation",
                "entity": DIAGNOSIS.name,
                "text": "focal epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "She has focal epilepsy.",
                "confidence": "high",
                "rationale": "Directly stated.",
            },
            {
                "mention_id": "pool_rx_1",
                "source_run": "prior_qwen_run",
                "source_surface": "structured_mentions_generation",
                "entity": PRESCRIPTION.name,
                "text": "lamotrigine 200 mg twice daily",
                "attributes": {
                    "DrugName": "lamotrigine",
                    "DrugDose": "200",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                "confidence": "high",
                "rationale": "Current treatment is stated.",
            },
        ]
    }

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="qwen_pool_entity_adjudication",
        pool_mentions_by_letter=pool_mentions,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    prompt_bundle = json.loads(row["inventory_prompt_input_json"])
    assert prompt_bundle["stage"] == "qwen_pool_entity_adjudication"
    entity_prompts = prompt_bundle["entity_prompt_inputs"]
    assert entity_prompts[DIAGNOSIS.name]["target_entity"] == DIAGNOSIS.name
    assert entity_prompts[PRESCRIPTION.name]["target_entity"] == PRESCRIPTION.name
    assert entity_prompts[DIAGNOSIS.name]["model_generated_mentions"][0][
        "mention_id"
    ] == "pool_dx_1"
    assert entity_prompts[PRESCRIPTION.name]["model_generated_mentions"][0][
        "mention_id"
    ] == "pool_rx_1"
    assert row["call_strategy"] == "qwen_pool_entity_adjudication"
    assert row["structured_mentions_generation"][0]["mention_id"] == "pool_dx_1"
    assert row["structured_mentions_final"] == []
    assert row["final_mention_ids"] == []
    assert row["final_mention_ids_by_entity"][DIAGNOSIS.name] == []
    assert row["entity_pool_sizes"][DIAGNOSIS.name] == 1
    assert row["entity_pool_sizes"][PRESCRIPTION.name] == 1
    assert row["pool_size"] == 2
    assert metadata["summary"]["selection_parse_failures"] == 0
    assert "Call strategy: `qwen_pool_entity_adjudication`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_qwen_pool_group_adjudication_records_group_prompt(
    tmp_path: Path,
) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"
    pool_mentions = {
        "TEST001": [
            {
                "mention_id": "pool_dx_1",
                "source_run": "prior_qwen_run",
                "source_surface": "structured_mentions_generation",
                "entity": DIAGNOSIS.name,
                "text": "focal epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "She has focal epilepsy.",
                "confidence": "high",
                "rationale": "Directly stated.",
            }
        ]
    }

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="qwen_pool_group_adjudication",
        pool_mentions_by_letter=pool_mentions,
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    group_prompt = json.loads(row["inventory_prompt_input_json"])
    assert group_prompt["stage"] == "qwen_pool_group_adjudication"
    assert group_prompt["model_generated_mentions"][0]["mention_id"] == "pool_dx_1"
    assert row["call_strategy"] == "qwen_pool_group_adjudication"
    assert row["structured_mentions_generation"][0]["mention_id"] == "pool_dx_1"
    assert row["structured_mentions_final"] == []
    assert row["final_mention_ids"] == []
    assert row["fact_groups"] == []
    assert row["n_fact_groups"] == 0
    assert row["pool_size"] == 1
    assert metadata["summary"]["selection_parse_failures"] == 0
    assert "Call strategy: `qwen_pool_group_adjudication`" in report_path.read_text(
        encoding="utf-8"
    )


def test_call_strategy_registry_covers_all_literals() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection import (
        CALL_STRATEGIES,
        STRATEGY_REGISTRY,
    )

    assert frozenset(STRATEGY_REGISTRY) == frozenset(CALL_STRATEGIES)
