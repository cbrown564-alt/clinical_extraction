"""Tests for the Phase 2 de-duplicated clinical-facts LLM-only route."""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_generation_selection as route,
)

_NOTE = (
    "She has focal epilepsy. "
    "She has no absences. "
    "No seizures since last review. "
    "Current treatment is lamotrigine 200 mg twice daily. "
    "MRI brain was normal."
)

_LETTER = ExectLetter(
    letter_id="DEDUP001",
    note_text=_NOTE,
    annotations=(
        ExectAnnotation(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={"Negation": "Affirmed"},
        ),
        ExectAnnotation(
            entity="Diagnosis",
            text="absences",
            attributes={"Negation": "Negated"},
        ),
        ExectAnnotation(
            entity="SeizureFrequency",
            text="seizures",
            attributes={
                "NumberOfSeizures": "0",
                "CUI": "C0036572",
                "CUIPhrase": "seizures",
            },
        ),
        ExectAnnotation(
            entity="Prescription",
            text="lamotrigine",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "200",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        ExectAnnotation(
            entity="Investigations",
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        ),
    ),
)


def _facts() -> list[dict[str, str]]:
    return [
        {
            "family": "diagnosis",
            "concept": "focal epilepsy",
            "negation": "affirmed",
            "evidence": "She has focal epilepsy.",
        },
        {
            "family": "diagnosis",
            "concept": "absences",
            "negation": "negated",
            "evidence": "She has no absences.",
        },
        {
            "family": "seizure_frequency",
            "seizure_type": "seizures",
            "state": "seizure_free",
            "evidence": "No seizures since last review.",
        },
        {
            "family": "prescription",
            "drug": "lamotrigine",
            "dose": "200",
            "dose_unit": "mg",
            "frequency": "twice daily",
            "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
        },
        {
            "family": "investigation",
            "modality": "MRI",
            "result": "normal",
            "evidence": "MRI brain was normal.",
        },
    ]


def test_single_call_dedup_facts_prompt_is_headline_targeted() -> None:
    payload_str = route.build_single_call_dedup_facts_prompt_input(_LETTER)
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_dedup_facts"
    assert payload["architecture"]["name"] == "llm_only_single_call_dedup_facts"
    assert payload["target_surface"]["name"] == "clinical_headline"
    assert payload["target_surface"]["diagnosis_component"] == "concept_negation"
    assert "clinical_facts" in payload["output_schema"]
    contract_text = " ".join(payload["model_origin_contract"])
    guidance_text = " ".join(payload["fact_guidance"])
    assert "De-duplicate at the source" in contract_text
    assert "deterministic code only validates evidence" in contract_text
    assert "Split compound diagnosis headings" in guidance_text
    assert "also emit a diagnosis fact for that named seizure type" in guidance_text
    assert "Do not skip a frequency fact just because it is in past history" in guidance_text
    assert "prior/previous/old dated MRI" in guidance_text
    assert "current anti-seizure/antiepileptic medications only" in guidance_text
    assert "never paraphrase evidence" in guidance_text
    assert "active_rate requires an explicit count" in guidance_text
    assert "last event, last seizure" in guidance_text
    assert "candidate_evidence_ledger" not in payload
    assert "candidate_id" not in payload_str


def test_per_family_dedup_facts_prompt_is_family_gated() -> None:
    payload_str = route.build_single_call_dedup_facts_prompt_input(
        _LETTER,
        target_family="seizure_frequency",
    )
    payload = json.loads(payload_str)

    assert payload["stage"] == "single_call_dedup_facts_per_family"
    assert payload["architecture"]["name"] == "llm_only_single_call_dedup_facts_per_family"
    assert payload["target_family"] == "seizure_frequency"
    assert payload["target_families"] == ["seizure_frequency"]
    assert payload["output_schema"] == {
        "clinical_facts": [
            {
                "family": "seizure_frequency",
                "seizure_type": "named seizure type, or seizures if generic",
                "state": "active_rate|seizure_free|changed|unknown",
                "evidence": "exact substring copied from the letter",
            }
        ]
    }
    assert "emit only family=seizure_frequency" in " ".join(payload["fact_guidance"])
    assert all(
        fact["family"] == "seizure_frequency"
        for example in payload["worked_examples"]
        for fact in example["clinical_facts"]
    )


def test_decision_table_profile_adds_targeted_family_gates() -> None:
    payload_str = route.build_single_call_dedup_facts_prompt_input(
        _LETTER,
        prompt_profile="decision_table",
        target_family="seizure_frequency",
    )
    payload = json.loads(payload_str)

    assert payload["prompt_profile"] == "decision_table"
    assert set(payload["decision_tables"]) == {"seizure_frequency"}
    table_text = json.dumps(payload["decision_tables"], sort_keys=True)
    guidance_text = " ".join(payload["fact_guidance"])
    examples_text = json.dumps(payload["worked_examples"], sort_keys=True)
    assert "apply the decision_tables exactly" in guidance_text
    assert "continues to get" in table_text
    assert "never invent NumberOfSeizures=1" in table_text
    assert "same seizure type has two distinct stated states" in table_text
    assert "Continues to get has no count/rate/window" in examples_text
    assert all(
        fact["family"] == "seizure_frequency"
        for example in payload["worked_examples"]
        for fact in example["clinical_facts"]
    )


def test_parse_and_adapter_map_facts_one_to_one_without_deduplication() -> None:
    raw = json.dumps({"clinical_facts": [*_facts(), _facts()[0]]})
    record, errors = route.parse_dedup_clinical_facts_json(raw)

    assert record is not None
    assert errors == []
    mentions, provenance, adapter_notes = route.clinical_facts_to_mentions(
        record.clinical_facts
    )

    assert adapter_notes == []
    assert len(mentions) == 6
    assert len(provenance) == 6
    assert all(item["added_fact"] is False for item in provenance)
    assert all(item["deduplicated_by_adapter"] is False for item in provenance)
    assert [mention.entity for mention in mentions[:5]] == [
        "Diagnosis",
        "Diagnosis",
        "SeizureFrequency",
        "Prescription",
        "Investigations",
    ]
    assert mentions[1].attributes == {"Negation": "Negated"}
    assert mentions[2].attributes == {"NumberOfSeizures": "0"}
    assert mentions[3].attributes["Frequency"] == "2"
    assert mentions[4].attributes == {"MRI_Performed": "Yes", "MRI_Results": "Normal"}


def test_row_from_final_dedup_facts_scores_with_exact_evidence() -> None:
    record = route.DedupClinicalFactsRecord.model_validate({"clinical_facts": _facts()})
    row = route.row_from_final_dedup_facts(
        _LETTER,
        record,
        split="dev",
        model="unit-test",
        mode="replay",
    )
    summary = route.summarize_rows([row])

    assert row["n_clinical_facts_final"] == 5
    assert row["n_mentions_raw"] == 5
    assert row["n_mentions_scored"] == 5
    assert row["n_evidence_invalid"] == 0
    assert summary["clinical_recovery"]["overall"]["f1"] == 1.0
    assert summary["clinical_recovery"]["diagnosis_component"] == "concept_negation"


def test_prompt_only_run_split_records_dedup_facts_prompt(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="ollama_chat/qwen3.6:35b",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_dedup_facts",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    prompt = json.loads(row["inventory_prompt_input_json"])
    assert prompt["stage"] == "single_call_dedup_facts"
    assert row["call_strategy"] == "single_call_dedup_facts"
    assert row["clinical_facts_final"] == []
    assert row["dedup_adapter_added_facts"] == 0
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_dedup_facts`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_run_split_records_per_family_dedup_prompts(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    report_path = tmp_path / "report.md"

    rows, metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_dedup_facts_per_family",
        checkpoint_jsonl_path=jsonl_path,
        checkpoint_report_path=report_path,
        progress_every=1,
    )
    route.write_report(rows, metadata, report_path, jsonl_path=jsonl_path)

    row = rows[0]
    prompt_bundle = json.loads(row["inventory_prompt_input_json"])
    assert set(prompt_bundle) == {
        "diagnosis",
        "seizure_frequency",
        "prescription",
        "investigation",
    }
    sf_prompt = json.loads(prompt_bundle["seizure_frequency"])
    assert sf_prompt["target_family"] == "seizure_frequency"
    assert row["call_strategy"] == "single_call_dedup_facts_per_family"
    assert row["clinical_facts_final"] == []
    assert row["dedup_adapter_added_facts"] == 0
    assert metadata["summary"]["inventory_parse_failures"] == 0
    assert "Call strategy: `single_call_dedup_facts_per_family`" in report_path.read_text(
        encoding="utf-8"
    )


def test_prompt_only_mixed_decision_table_profile_targets_sf_and_investigation(
    tmp_path: Path,
) -> None:
    rows, _metadata = route.run_split(
        [_LETTER],
        split="dev",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=128,
        mode="prompt-only",
        call_strategy="single_call_dedup_facts_per_family",
        prompt_profile="decision_table_sf_inv",
        checkpoint_jsonl_path=tmp_path / "rows.jsonl",
        checkpoint_report_path=tmp_path / "report.md",
        progress_every=1,
    )

    prompt_bundle = json.loads(rows[0]["inventory_prompt_input_json"])
    diagnosis_prompt = json.loads(prompt_bundle["diagnosis"])
    sf_prompt = json.loads(prompt_bundle["seizure_frequency"])
    investigation_prompt = json.loads(prompt_bundle["investigation"])

    assert diagnosis_prompt["prompt_profile"] == "compact"
    assert "decision_tables" not in diagnosis_prompt
    assert sf_prompt["prompt_profile"] == "decision_table"
    assert set(sf_prompt["decision_tables"]) == {"seizure_frequency"}
    assert investigation_prompt["prompt_profile"] == "decision_table"
    assert set(investigation_prompt["decision_tables"]) == {"investigation"}


def test_no_call_replay_maps_saved_mentions_through_dedup_adapter() -> None:
    source_row = route.row_from_final_dedup_facts(
        _LETTER,
        route.DedupClinicalFactsRecord.model_validate({"clinical_facts": _facts()}),
        split="dev",
        model="source",
        mode="replay",
    )

    replay_rows, metadata = route.replay_dedup_facts_from_rows([source_row])

    replay_facts = replay_rows[0]["clinical_facts_final"]
    assert [(fact["family"], fact["evidence"]) for fact in replay_facts] == [
        (fact["family"], fact["evidence"]) for fact in _facts()
    ]
    assert replay_rows[0]["n_mentions_scored"] == source_row["n_mentions_scored"]
    assert metadata["summary"]["clinical_recovery"]["overall"]["f1"] == 1.0
