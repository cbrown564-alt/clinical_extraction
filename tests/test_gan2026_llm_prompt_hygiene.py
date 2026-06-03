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
    llm_only_structured_events,
    llm_only_typed_adapter_reasoner,
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
            "llm_heavy_clinical_frequency_reasoner",
            llm_heavy_clinical_frequency_reasoner.build_prompt_input,
        ),
        (
            "llm_only_typed_adapter_reasoner",
            llm_only_typed_adapter_reasoner.build_typed_adapter_inputs,
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
