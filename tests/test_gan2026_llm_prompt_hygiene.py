import json

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as exectv2_structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events,
    llm,
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


def _exect_letter() -> ExectLetter:
    return ExectLetter(
        letter_id="TEST001",
        note_text="Clinic note: two seizures per month. Last seizure was yesterday.",
    )


def _payload_text(payload: str | dict[str, object]) -> str:
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


@pytest.mark.parametrize(
    ("name", "builder", "arg"),
    [
        ("hybrid_structured_events", hybrid_structured_events.build_prompt_input, "_record"),
        ("llm", llm.build_prompt_input, "_record"),
        ("exectv2_structured", exectv2_structured.build_prompt_input, "_letter"),
    ],
)
def test_llm_model_facing_payloads_do_not_expose_internal_protocol_language(
    name: str,
    builder,
    arg: str,
) -> None:
    input_obj = _record() if arg == "_record" else _exect_letter()
    text = _payload_text(builder(input_obj))

    leaked_phrases = [phrase for phrase in INTERNAL_MODEL_FACING_PHRASES if phrase in text]
    assert leaked_phrases == [], name
