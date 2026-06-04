import json

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_heavy_clinical_frequency_reasoner,
    llm_heavy_evidence_selection_with_deterministic_adapters,
    llm_only_claim_table_selector,
    llm_only_direct_labeler,
    llm_only_minimal_evidence_selector,
    llm_only_simplified_selected_state_reasoner,
    llm_only_sparse_operands_selected_state_reasoner,
    llm_only_structured_events,
    llm_only_typed_adapter_reasoner,
    llm_only_typed_operations_reasoner,
)

AUDIT_PROMPT_DISCIPLINE_TERMS = (
    "source-near",
    "operands",
    "proxy",
    "denominator",
    "prompt_version",
    "pipeline_family",
    "Gan 2026",
    "benchmark",
    "component",
)

MODEL_FACING_METADATA_KEYS = (
    "prompt_version",
    "pipeline_family",
    "typed_output_schema_version",
)

INTERNAL_MODEL_FACING_PHRASES = (
    "Decision 000",
    "decision 000",
    "deterministic code",
    "downstream deterministic",
    "deterministic selected-evidence",
    "deterministic mechanical",
    "must not choose a different clinical fact",
    "will only render parser-ready labels",
    "architecture gate",
    "deterministic candidates",
    "deterministic rule candidates",
    "gold labels",
    "gold_label",
    "parser-ready",
    "Gan-compatible",
    "Gan-facing",
    "scorer-facing",
    "scoring-facing",
    "benchmark",
    "synthetic",
    "prompt_policy_taxonomy",
    "required_ablations",
    " -> ",
)


def _record() -> GanFrequencyRecord:
    frequency_record = label_to_frequency_record("2 per month")
    return GanFrequencyRecord(
        source_row_index=1,
        note_text="Clinic note: two seizures per month. Last seizure was yesterday.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=frequency_record.normalized_label,
        gold_label_kind=frequency_record.kind,
        gold_yearly_bounds=frequency_record.yearly_bounds,
        gold_monthly_frequency=frequency_record.monthly_frequency,
    )


def _payload_text(payload: str | dict[str, object]) -> str:
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _contains_key(value: object, target_key: str) -> bool:
    if isinstance(value, dict):
        return target_key in value or any(
            _contains_key(item, target_key) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, target_key) for item in value)
    return False


def _instruction_text(payload: dict[str, object]) -> str:
    instructions = payload.get("task_instructions") or payload.get("instructions") or []
    return json.dumps(instructions, ensure_ascii=False, sort_keys=True)


def _assert_field_descriptions_cover(
    payload: dict[str, object],
    field_list_key: str,
    description_key: str,
) -> None:
    output_contract = payload["output_contract"]
    assert isinstance(output_contract, dict)
    field_names = output_contract[field_list_key]
    descriptions = output_contract[description_key]
    assert isinstance(field_names, list)
    assert isinstance(descriptions, dict)
    missing = [
        field_name
        for field_name in field_names
        if field_name not in descriptions or not str(descriptions[field_name]).strip()
    ]
    assert missing == []


@pytest.mark.parametrize(
    ("name", "builder"),
    [
        ("llm_only_direct_labeler", llm_only_direct_labeler.build_prompt_input),
        (
            "llm_only_claim_table_selector",
            llm_only_claim_table_selector.build_prompt_input,
        ),
        ("llm_only_structured_events", llm_only_structured_events.build_prompt_input),
        (
            "llm_only_minimal_evidence_selector",
            llm_only_minimal_evidence_selector.build_prompt_input,
        ),
        (
            "llm_only_sparse_operands_selected_state_reasoner",
            llm_only_sparse_operands_selected_state_reasoner.build_sparse_operands_inputs,
        ),
        (
            "llm_heavy_clinical_frequency_reasoner",
            llm_heavy_clinical_frequency_reasoner.build_prompt_input,
        ),
        (
            "llm_only_typed_adapter_reasoner",
            llm_only_typed_adapter_reasoner.build_typed_adapter_inputs,
        ),
        (
            "llm_only_typed_operations_reasoner",
            llm_only_typed_operations_reasoner.build_typed_operations_inputs,
        ),
        (
            "llm_heavy_evidence_selection_with_deterministic_adapters",
            llm_heavy_evidence_selection_with_deterministic_adapters.build_typed_inputs,
        ),
    ],
)
def test_llm_model_facing_payloads_do_not_expose_internal_protocol_language(
    name: str,
    builder,
) -> None:
    text = _payload_text(builder(_record()))

    leaked_phrases = [
        phrase for phrase in INTERNAL_MODEL_FACING_PHRASES if phrase in text
    ]
    assert leaked_phrases == [], name


@pytest.mark.parametrize(
    ("name", "builder"),
    [
        (
            "llm_only_sparse_operands_selected_state_reasoner",
            llm_only_sparse_operands_selected_state_reasoner.build_sparse_operands_inputs,
        ),
        (
            "llm_only_simplified_selected_state_reasoner",
            llm_only_simplified_selected_state_reasoner.build_selected_state_inputs,
        ),
        (
            "llm_only_typed_adapter_reasoner",
            llm_only_typed_adapter_reasoner.build_typed_adapter_inputs,
        ),
        (
            "llm_only_typed_operations_reasoner",
            llm_only_typed_operations_reasoner.build_typed_operations_inputs,
        ),
    ],
)
def test_selected_state_model_instructions_use_plain_language(
    name: str,
    builder,
) -> None:
    payload = builder(_record())

    instruction_text = _instruction_text(payload)
    leaked_terms = [
        term for term in AUDIT_PROMPT_DISCIPLINE_TERMS if term in instruction_text
    ]
    assert leaked_terms == [], name


@pytest.mark.parametrize(
    ("name", "builder"),
    [
        (
            "llm_only_sparse_operands_selected_state_reasoner",
            llm_only_sparse_operands_selected_state_reasoner.build_sparse_operands_inputs,
        ),
        (
            "llm_only_simplified_selected_state_reasoner",
            llm_only_simplified_selected_state_reasoner.build_selected_state_inputs,
        ),
        (
            "llm_only_typed_adapter_reasoner",
            llm_only_typed_adapter_reasoner.build_typed_adapter_inputs,
        ),
        (
            "llm_only_typed_operations_reasoner",
            llm_only_typed_operations_reasoner.build_typed_operations_inputs,
        ),
    ],
)
def test_selected_state_model_payloads_keep_metadata_out_of_instructions(
    name: str,
    builder,
) -> None:
    payload = builder(_record())

    leaked_metadata = [
        key for key in MODEL_FACING_METADATA_KEYS if _contains_key(payload, key)
    ]
    assert leaked_metadata == [], name


def test_selected_state_schema_fields_have_descriptions() -> None:
    simplified = llm_only_simplified_selected_state_reasoner.build_selected_state_inputs(
        _record()
    )
    sparse = llm_only_sparse_operands_selected_state_reasoner.build_sparse_operands_inputs(
        _record()
    )
    typed_adapter = llm_only_typed_adapter_reasoner.build_typed_adapter_inputs(_record())
    typed_operations = llm_only_typed_operations_reasoner.build_typed_operations_inputs(
        _record()
    )

    _assert_field_descriptions_cover(
        simplified,
        "selected_state_fields",
        "field_descriptions",
    )
    _assert_field_descriptions_cover(
        sparse,
        "selected_state_fields",
        "field_descriptions",
    )
    _assert_field_descriptions_cover(
        sparse,
        "numeric_detail_fields",
        "numeric_detail_field_descriptions",
    )
    assert typed_adapter["output_contract"]["field_descriptions"]
    assert typed_operations["output_contract"]["field_descriptions"]
    _assert_field_descriptions_cover(
        typed_operations,
        "operation_operand_fields",
        "operation_operand_field_descriptions",
    )
