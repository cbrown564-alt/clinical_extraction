"""Always-on contract for Gan find prompt-component ablations."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.paper.gan import verify_gan
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_examples_only as extract_examples_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_holgate_label as extract_holgate_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_holgate_like as extract_holgate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_no_evidence as extract_no_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_no_examples as extract_no_examples,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    build_prompt_input,
    parse_structured_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_label_forms import (
    LABEL_FORMS,
    label_form_example_strings,
    label_forms_payload,
    label_forms_without_examples_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    GAN_LLM_EXTRACT,
    llm_extract_prompt_template,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract_raw import (
    EVENT_SCHEMA,
    SELECTION_SCHEMA,
)

RESEARCH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "research"
    / "gan2026"
)
NO_EXAMPLES_TEMPLATE = RESEARCH / "gan_llm_extract_no_examples_prompt_template.json"
HOLGATE_TEMPLATE = RESEARCH / "gan_llm_extract_holgate_like_prompt_template.json"
HOLGATE_LABEL_TEMPLATE = RESEARCH / "gan_llm_extract_holgate_label_prompt_template.json"
NO_EVIDENCE_TEMPLATE = RESEARCH / "gan_llm_extract_no_evidence_prompt_template.json"
EXAMPLES_ONLY_TEMPLATE = RESEARCH / "gan_llm_extract_examples_only_prompt_template.json"


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def test_no_examples_keeps_forms_and_drops_example_strings() -> None:
    baseline = llm_extract_prompt_template()
    variant = extract_no_examples.llm_extract_no_examples_prompt_template()
    payload = json.loads(
        extract_no_examples.build_llm_extract_no_examples_prompt_input(_record())
    )
    assert variant["event_schema"] == EVENT_SCHEMA == baseline["event_schema"]
    assert variant["selection_schema"] == SELECTION_SCHEMA == baseline["selection_schema"]
    assert variant["label_forms"] == label_forms_without_examples_payload()
    assert "examples" not in json.dumps(variant["label_forms"])
    assert [row["form"] for row in variant["label_forms"]["forms"]] == [
        row["form"] for row in LABEL_FORMS
    ]
    assert "Copy an example" not in json.dumps(variant)
    assert "allowed forms" in json.dumps(payload).lower()
    assert set(payload) == set(extract_no_examples.LLM_EXTRACT_NO_EXAMPLES_AUTHORED_KEYS)
    assert payload["note_text"] == _record().note_text


def test_no_examples_frozen_template_matches_living_prompt() -> None:
    on_disk = json.loads(NO_EXAMPLES_TEMPLATE.read_text(encoding="utf-8"))
    assert on_disk == extract_no_examples.llm_extract_no_examples_prompt_template()


def test_holgate_like_drops_codebook_and_keeps_schema() -> None:
    baseline = llm_extract_prompt_template()
    variant = extract_holgate.llm_extract_holgate_like_prompt_template()
    payload = json.loads(
        extract_holgate.build_llm_extract_holgate_like_prompt_input(_record())
    )
    assert "label_forms" not in variant
    assert variant["event_schema"] == EVENT_SCHEMA == baseline["event_schema"]
    assert variant["selection_schema"] == SELECTION_SCHEMA == baseline["selection_schema"]
    assert variant["instructions"][1].endswith("'I do not know.'")
    assert "per year, per month, per week, or per day" in variant["instructions"][2]
    assert "label_forms" not in payload
    assert set(payload) == set(extract_holgate.LLM_EXTRACT_HOLGATE_LIKE_AUTHORED_KEYS)
    blob = json.dumps(payload)
    assert "Gan 2026" not in blob
    assert "gold" not in blob.lower()
    assert payload["note_text"] == _record().note_text


def test_holgate_like_frozen_template_matches_living_prompt() -> None:
    on_disk = json.loads(HOLGATE_TEMPLATE.read_text(encoding="utf-8"))
    assert on_disk == extract_holgate.llm_extract_holgate_like_prompt_template()


def test_dispatch_keeps_default_extract_raw() -> None:
    default = json.loads(build_prompt_input(_record()))
    no_examples = json.loads(
        build_prompt_input(
            _record(), prompt_version=extract_no_examples.GAN_LLM_EXTRACT_NO_EXAMPLES
        )
    )
    holgate = json.loads(
        build_prompt_input(
            _record(), prompt_version=extract_holgate.GAN_LLM_EXTRACT_HOLGATE_LIKE
        )
    )
    codebook = json.loads(build_prompt_input(_record(), prompt_version=GAN_LLM_EXTRACT))
    no_evidence = json.loads(
        build_prompt_input(
            _record(), prompt_version=extract_no_evidence.GAN_LLM_EXTRACT_NO_EVIDENCE
        )
    )
    examples_only = json.loads(
        build_prompt_input(
            _record(),
            prompt_version=extract_examples_only.GAN_LLM_EXTRACT_EXAMPLES_ONLY,
        )
    )
    holgate_label = json.loads(
        build_prompt_input(
            _record(),
            prompt_version=extract_holgate_label.GAN_LLM_EXTRACT_HOLGATE_LABEL,
        )
    )
    assert "label_forms" not in default
    assert no_examples["label_forms"] == label_forms_without_examples_payload()
    assert codebook["label_forms"] == label_forms_payload()
    assert "label_forms" not in holgate
    assert "evidence" not in no_evidence["event_schema"]
    assert examples_only["examples"] == label_form_example_strings()
    assert set(holgate_label) == {"task", "instructions", "answer_schema", "note_text"}


def test_component_ablation_verify_accepts_gemini_holdout_identity() -> None:
    for method, prompt in (
        (
            extract_no_examples.GAN_LLM_EXTRACT_NO_EXAMPLES,
            extract_no_examples.GAN_LLM_EXTRACT_NO_EXAMPLES,
        ),
        (
            extract_holgate.GAN_LLM_EXTRACT_HOLGATE_LIKE,
            extract_holgate.GAN_LLM_EXTRACT_HOLGATE_LIKE,
        ),
        (
            extract_holgate_label.GAN_LLM_EXTRACT_HOLGATE_LABEL,
            extract_holgate_label.GAN_LLM_EXTRACT_HOLGATE_LABEL,
        ),
        (
            extract_no_evidence.GAN_LLM_EXTRACT_NO_EVIDENCE,
            extract_no_evidence.GAN_LLM_EXTRACT_NO_EVIDENCE,
        ),
        (
            extract_examples_only.GAN_LLM_EXTRACT_EXAMPLES_ONLY,
            extract_examples_only.GAN_LLM_EXTRACT_EXAMPLES_ONLY,
        ),
    ):
        development = verify_gan(method, "dev750", "gemini37flash")
        holdout = verify_gan(method, "test450", "gemini37flash")
        assert development["ok"] is True
        assert development["prompt_version"] == prompt
        assert development["row_policy"] == "development_review_permitted"
        assert holdout["row_policy"] == "aggregate_only"
        assert holdout["holdout_scratch"].endswith(method)


def test_no_evidence_drops_quote_keys_and_keeps_codebook() -> None:
    baseline = llm_extract_prompt_template()
    variant = extract_no_evidence.llm_extract_no_evidence_prompt_template()
    payload = json.loads(
        extract_no_evidence.build_llm_extract_no_evidence_prompt_input(_record())
    )
    assert variant["label_forms"] == label_forms_payload()
    assert "evidence" not in variant["event_schema"]
    assert "evidence" not in variant["selection_schema"]
    assert variant["event_schema"].keys() == baseline["event_schema"].keys() - {"evidence"}
    assert (
        variant["selection_schema"].keys()
        == baseline["selection_schema"].keys() - {"evidence"}
    )
    blob = json.dumps(payload)
    assert "exact substring" not in blob
    assert "Every evidence value" not in blob
    assert "label_forms" in payload
    assert "examples" in json.dumps(payload["label_forms"])
    assert set(payload) == set(extract_no_evidence.LLM_EXTRACT_NO_EVIDENCE_AUTHORED_KEYS)
    on_disk = json.loads(NO_EVIDENCE_TEMPLATE.read_text(encoding="utf-8"))
    assert on_disk == variant


def test_examples_only_keeps_example_strings_and_drops_forms() -> None:
    variant = extract_examples_only.llm_extract_examples_only_prompt_template()
    payload = json.loads(
        extract_examples_only.build_llm_extract_examples_only_prompt_input(_record())
    )
    assert "label_forms" not in variant
    assert variant["examples"] == label_form_example_strings()
    assert "1 per day" in variant["examples"]
    assert variant["event_schema"] == EVENT_SCHEMA
    assert "allowed forms" not in json.dumps(variant).lower()
    assert "Copy an example" in json.dumps(variant)
    assert "exact substring" in json.dumps(variant)
    assert set(payload) == set(
        extract_examples_only.LLM_EXTRACT_EXAMPLES_ONLY_AUTHORED_KEYS
    )
    on_disk = json.loads(EXAMPLES_ONLY_TEMPLATE.read_text(encoding="utf-8"))
    assert on_disk == variant


def test_holgate_label_is_one_answer_field() -> None:
    variant = extract_holgate_label.llm_extract_holgate_label_prompt_template()
    payload = json.loads(
        extract_holgate_label.build_llm_extract_holgate_label_prompt_input(_record())
    )
    assert "event_schema" not in variant
    assert "selection_schema" not in variant
    assert "label_forms" not in variant
    assert variant["answer_schema"] == {"answer": "the frequency, or I do not know"}
    assert variant["instructions"][1].endswith("'I do not know.'")
    blob = json.dumps(payload)
    assert "exact substring" not in blob
    assert "evidence" not in blob
    assert set(payload) == set(extract_holgate_label.LLM_EXTRACT_HOLGATE_LABEL_AUTHORED_KEYS)
    on_disk = json.loads(HOLGATE_LABEL_TEMPLATE.read_text(encoding="utf-8"))
    assert on_disk == variant


def test_missing_evidence_still_parses_for_no_evidence_cell() -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "two per month",
                    "applies_to": None,
                    "time_window": None,
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "2 per month",
                "confidence": "high",
                "rationale": "stated rate",
            },
        }
    )
    extraction, _, errors = parse_structured_json(
        raw,
        note_text=_record().note_text,
        repair_config=StructuredRepairConfig.for_mode("raw_model"),
    )
    assert errors == []
    assert extraction is not None
    assert extraction.selection.final_label == "2 per month"
    assert extraction.selection.evidence == ""
    assert extraction.events[0].evidence == ""


def test_single_answer_fallback_wraps_holgate_label() -> None:
    config = StructuredRepairConfig.for_mode("raw_model_single_answer")
    from_object, _, object_errors = parse_structured_json(
        '{"answer": "I do not know."}',
        repair_config=config,
    )
    from_text, _, text_errors = parse_structured_json(
        "2 seizures per month",
        repair_config=config,
    )
    assert object_errors == []
    assert text_errors == []
    assert from_object is not None
    assert from_text is not None
    assert from_object.selection.final_label == "I do not know."
    assert from_text.selection.final_label == "2 seizures per month"
    from_nested, _, nested_errors = parse_structured_json(
        json.dumps(
            {
                "events": [{}],
                "selection": {
                    "selected_event_ids": [],
                    "confidence": "low",
                    "answer": "2 seizures per month",
                },
            }
        ),
        repair_config=config,
    )
    assert nested_errors == []
    assert from_nested is not None
    assert from_nested.selection.final_label == "2 seizures per month"
