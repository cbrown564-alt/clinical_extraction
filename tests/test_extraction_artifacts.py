"""Always-on checks for the staged source/request/artifact reconstruction.

Admission: these cover new replay identity, raw-event preservation, evidence
ambiguity, and cross-policy immutability obligations that legacy benchmark tests
cannot express.  They use fictional or authored development fixtures only.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from clinical_extraction.core.artifacts import (
    ExecutionConfiguration,
    SourceDocument,
    lifecycle_manifest_from_artifact,
    locate_text_evidence,
)
from clinical_extraction.longitudinal.artifacts import (
    build_longitudinal_artifact,
    evaluate_artifact_query,
)
from clinical_extraction.longitudinal.evidence import load_case
from clinical_extraction.operational.gan import run_gan_artifact_notes
from clinical_extraction.operational.io import InputNote
from clinical_extraction.operational.runtime import RuntimeConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.extraction import (
    exect_extraction_profile,
    family_inventory,
    prepare_exect_request,
    project_exect_artifact,
    project_exect_artifact_with_trace,
    replay_exect_response,
    score_exect_artifact,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as legacy_exect,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events as legacy_gan,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.extraction import (
    event_inventory,
    execute_gan_request,
    gan_extraction_profile,
    prepare_gan_request,
    replay_gan_response,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    GAN_LLM_EXTRACT,
)
from clinical_extraction.tasks.shared.epilepsy.normalization import (
    FrequencyLabelKind,
)


def _gan_record(text: str) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text=text,
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


def _gan_raw() -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "two seizures per month",
                    "applies_to": "seizures",
                    "time_window": "current",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "two seizures per month",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "2 per month",
                "evidence": "two seizures per month",
                "confidence": "high",
                "rationale": "The note states the current rate.",
            },
        },
        separators=(",", ":"),
    )


def _exect_raw() -> str:
    return json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "evidence": "Diagnosis: focal epilepsy",
                    "fact": "focal epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy", "ignored_extra": 7},
                    "model_only_field": "preserved only in raw_event",
                },
                {
                    "family": "outside_scope",
                    "evidence": "EEG normal",
                    "fact": "EEG",
                    "attributes": {"confidence": 0.7},
                },
            ]
        },
        separators=(",", ":"),
    )


def test_source_versions_and_repeated_evidence_are_explicit() -> None:
    source = SourceDocument.from_text(source_id="note-1", text="same quote; same quote")

    ambiguous = locate_text_evidence(source, "same quote")
    exact = locate_text_evidence(source, "same quote", start_char=12, end_char=22)
    changed = SourceDocument.from_text(
        source_id="note-1", text="same quote; changed", version_id="revision-2"
    )

    assert ambiguous.location_status == "ambiguous"
    assert not ambiguous.location_valid
    assert exact.location_status == "exact"
    assert exact.location_valid
    assert changed.ref() != source.ref()
    assert locate_text_evidence(changed, "same quote").source == changed.ref()


def test_gan_request_matches_legacy_bytes_without_gold_or_source_metadata() -> None:
    text = "Present seizure frequency: two seizures per month."
    first_source = SourceDocument.from_text(source_id="ordinary-a", text=text)
    second_source = SourceDocument.from_text(source_id="ordinary-b", text=text)

    first = prepare_gan_request(first_source)
    second = prepare_gan_request(second_source)
    legacy_payload = legacy_gan.build_prompt_input(
        _gan_record(text), prompt_version=GAN_LLM_EXTRACT
    )
    legacy_messages = legacy_gan.DspyStructuredExtractor().render_messages(
        prompt_input_json=legacy_payload
    )

    assert first.prompt_input_json == legacy_payload
    assert list(first.rendered_messages) == legacy_messages
    assert second.prompt_input_json == first.prompt_input_json
    assert second.rendered_messages == first.rendered_messages
    assert second.request_id != first.request_id
    assert "ordinary-a" not in first.prompt_input_json
    assert "gold" not in first.prompt_input_json.casefold()
    assert [component.component_id for component in first.prompt_components] == [
        "task_definition",
        "instructions",
        "examples",
        "allowed_label_presentation",
        "evidence_requirements",
        "schema_presentation",
    ]

    baseline_profile = gan_extraction_profile()
    changed_components = tuple(
        replace(
            component,
            content=[*component.content, "Unique component-composition check."],
            content_sha256="",
        )
        if component.component_id == "instructions"
        else component
        for component in baseline_profile.prompt_components
    )
    changed_profile = replace(
        baseline_profile,
        profile_version="gan2026.gan_llm_extract.profile.test",
        prompt_components=changed_components,
    )
    changed_request = prepare_gan_request(first_source, profile=changed_profile)
    assert "Unique component-composition check." in changed_request.prompt_input_json
    assert changed_request.rendered_messages != first.rendered_messages
    assert changed_request.request_id != first.request_id

    with pytest.raises(ValueError, match="supports only"):
        gan_extraction_profile(legacy_gan.GAN_LLM_EXTRACT_HOLGATE_LABEL)


def test_gan_replay_preserves_raw_events_and_legacy_projection() -> None:
    source = SourceDocument.from_text(
        source_id="ordinary-note",
        text="Present seizure frequency: two seizures per month.",
    )
    request = prepare_gan_request(source)
    artifact = replay_gan_response(
        request,
        source=source,
        saved_request_id=request.request_id,
        response_text=_gan_raw(),
    )
    legacy_record, legacy_events, legacy_errors = legacy_gan.parse_structured_json(
        _gan_raw(), note_text=source.text
    )

    assert artifact.status == "ready"
    assert artifact.attempts[0].kind == "replay"
    assert artifact.attempts[0].response_text == _gan_raw()
    assert [event.event_id for event in event_inventory(artifact)] == ["e1"]
    assert artifact.assertions[0].raw_position == 0
    assert artifact.assertions[0].evidence[0].location_valid
    assert artifact.compatibility_output["structured_record"] == legacy_record.model_dump(
        mode="json"
    )
    serialized = artifact.to_dict()
    assert serialized["compatibility_output"]["normalized_events"] == [
        event.model_dump(mode="json") for event in legacy_events
    ]
    assert list(artifact.diagnostics["compatibility_notes"]) == legacy_errors
    with pytest.raises(ValueError, match="request identity"):
        replay_gan_response(
            request,
            source=source,
            saved_request_id="request:different",
            response_text=_gan_raw(),
        )


def test_gan_operational_artifact_path_needs_no_dummy_gold_record() -> None:
    rows = run_gan_artifact_notes(
        [InputNote("ordinary-note", "Two seizures per month.")],
        RuntimeConfig(
            base_url="http://127.0.0.1:8000/v1",
            api_key="EMPTY",
            model="vllm/fixture",
        ),
        completion=lambda request: _gan_raw(),
    )

    assert rows[0]["status"] == "ok"
    request = rows[0]["artifact"]["request"]
    assert request["sources"][0]["source_id"] == "ordinary-note"
    assert "gold" not in request["prompt_input_json"].casefold()
    runtime_metadata = rows[0]["artifact"]["attempts"][0]["provider_metadata"][
        "runtime"
    ]
    assert runtime_metadata["model"] == "vllm/fixture"
    assert runtime_metadata["settings"]["timeout_seconds"] == 300.0
    assert "EMPTY" not in json.dumps(runtime_metadata)


@pytest.mark.local_corpus
def test_gan_saved_development_response_retains_selected_output() -> None:
    rows_path = Path(
        "results/letter-benchmarks/gan/gan_llm_extract/gemini37flash/dev750/rows.jsonl"
    )
    scored_path = Path(
        "results/letter-benchmarks/gan/gan_llm_extract/gemini37flash/dev750/scored.jsonl"
    )
    saved_row = json.loads(rows_path.read_text(encoding="utf-8").splitlines()[0])
    scored_row = json.loads(scored_path.read_text(encoding="utf-8").splitlines()[0])
    records = {
        record.source_row_index: record
        for record in load_records_for_split("validation")
    }
    record = records[int(saved_row["source_row_index"])]
    source = SourceDocument.from_text(
        source_id=str(record.source_row_index),
        text=record.note_text,
    )
    request = prepare_gan_request(source)
    artifact = replay_gan_response(
        request,
        source=source,
        saved_request_id=request.request_id,
        response_text=str(saved_row["raw_output"]),
    )

    assert request.prompt_input_json == legacy_gan.build_prompt_input(
        record,
        prompt_version=GAN_LLM_EXTRACT,
    )
    assert artifact.status == "ready"
    assert artifact.compatibility_output["final_label"] == scored_row["predicted_label"]


def test_exect_profile_is_explicit_and_does_not_mutate_legacy_default() -> None:
    text = "Diagnosis: focal epilepsy."
    source = SourceDocument.from_text(source_id="letter-a", text=text)
    inventory = prepare_exect_request(source)
    alternate = prepare_exect_request(
        source,
        profile=exect_extraction_profile(legacy_exect.EXECT_LLM_EXTRACT_AND_SELECT),
    )
    repeated = prepare_exect_request(source)

    assert inventory.prompt_input_json == legacy_exect.build_prompt_input(
        ExectLetter("letter-a", text), prompt_version="exect_llm_extract"
    )
    assert alternate.prompt_input_json != inventory.prompt_input_json
    assert alternate.prompt_input_json == legacy_exect.build_prompt_input(
        ExectLetter("letter-a", text),
        prompt_version=legacy_exect.EXECT_LLM_EXTRACT_AND_SELECT,
    )
    assert repeated.prompt_input_json == inventory.prompt_input_json
    assert legacy_exect.PROMPT_VERSION == "exect_llm_pre_post"


def test_exect_artifact_preserves_unknown_events_then_projects_and_scores() -> None:
    source = SourceDocument.from_text(
        source_id="letter-a",
        text="Diagnosis: focal epilepsy. EEG normal. EEG normal.",
    )
    request = prepare_exect_request(source)
    artifact = replay_exect_response(
        request,
        source=source,
        saved_request_id=request.request_id,
        response_text=_exect_raw(),
    )
    before = artifact.content_sha256
    inventory = family_inventory(artifact)
    prediction = project_exect_artifact(artifact, source=source)
    projection_trace = project_exect_artifact_with_trace(artifact, source=source)
    reference = to_exect_letter(prediction, note_text=source.text)
    score = score_exect_artifact(
        artifact,
        source=source,
        reference=reference,
    )

    assert artifact.status == "ready"
    assert [assertion.raw_position for assertion in artifact.assertions] == [0, 1]
    assert set(inventory) == {"diagnosis", "outside_scope"}
    assert inventory["diagnosis"][0].raw_event["model_only_field"] == (
        "preserved only in raw_event"
    )
    assert artifact.assertions[1].evidence[0].location_status == "ambiguous"
    assert artifact.diagnostics["compatibility_event_count"] == 1
    assert any(
        "dropped_unknown_event_family: event[1]" in str(note)
        for note in artifact.diagnostics["compatibility_notes"]
    )
    assert len(prediction.mentions) == 1
    assert projection_trace.prediction == prediction
    assert projection_trace.compatibility_raw_positions == (0,)
    assert projection_trace.projected_mention_raw_positions == (0,)
    assert score["per_item"]["f1"] == pytest.approx(1.0)
    assert artifact.content_sha256 == before

    captured_runtime = ExecutionConfiguration(
        runtime_id="captured-runtime",
        provider="saved",
        model="fixture/model",
    )
    runtime_artifact = replay_exect_response(
        request,
        source=source,
        saved_request_id=request.request_id,
        response_text=_exect_raw(),
        provider_metadata={
            "runtime": captured_runtime.to_dict(),
            "latency_ms": 12.5,
            "input_tokens": 100,
            "output_tokens": 20,
            "cost": 0.0,
            "cost_currency": "GBP",
        },
    )
    runtime_manifest = lifecycle_manifest_from_artifact(
        runtime_artifact,
        runtime=captured_runtime,
        program_version="exect-artifact.v1",
        replay_mode="saved_output_replay",
    )
    assert runtime_manifest.total_latency_ms == 12.5
    assert runtime_manifest.input_tokens == 100
    assert runtime_manifest.output_tokens == 20
    assert runtime_manifest.cost == 0.0
    assert runtime_manifest.cost_currency == "GBP"
    with pytest.raises(ValueError, match="runtime does not match"):
        lifecycle_manifest_from_artifact(
            runtime_artifact,
            runtime=replace(captured_runtime, model="different/model"),
            program_version="exect-artifact.v1",
            replay_mode="saved_output_replay",
        )

    manifest = lifecycle_manifest_from_artifact(
        artifact,
        runtime=ExecutionConfiguration(
            runtime_id="fixture-runtime",
            provider="saved",
            model="fixture/model",
        ),
        program_version="exect-artifact.v1",
        replay_mode="saved_output_replay",
        scorer_version="exectv2.benchmark",
        dataset_id="fictional-test",
        split="development",
        row_policy="development_review_permitted",
    )
    assert manifest.call_count == 0
    assert manifest.failure_count == 0
    assert manifest.source_hashes == {source.source_id: source.text_sha256}
    assert manifest.output_hashes["artifact"] == artifact.content_sha256

    exported = artifact.to_dict()
    exported["raw_payload"]["clinical_events"][0]["fact"] = "changed"
    assert family_inventory(artifact)["diagnosis"][0].fact == "focal epilepsy"
    assert artifact.content_sha256 == before


@pytest.mark.parametrize(
    "response",
    [
        "{}",
        '{"unrelated":true}',
        '{"clinical_events":["not an event"]}',
    ],
)
def test_exect_unsupported_shapes_are_failed_not_valid_empty(response: str) -> None:
    source = SourceDocument.from_text(source_id="letter-a", text="No findings here.")
    request = prepare_exect_request(source)

    invalid = replay_exect_response(
        request,
        source=source,
        saved_request_id=request.request_id,
        response_text=response,
    )
    valid_empty = replay_exect_response(
        request,
        source=source,
        saved_request_id=request.request_id,
        response_text='{"clinical_events":[]}',
    )
    manifest = lifecycle_manifest_from_artifact(
        invalid,
        runtime=ExecutionConfiguration(
            runtime_id="fixture-runtime",
            provider="saved",
            model="fixture/model",
        ),
        program_version="exect-artifact.v1",
        replay_mode="saved_output_replay",
    )

    assert invalid.status == "failed"
    assert invalid.diagnostics["raw_schema_errors"]
    assert manifest.failure_count == 1
    assert valid_empty.status == "ready"


def test_exect_projection_trace_does_not_guess_between_duplicate_names() -> None:
    source = SourceDocument.from_text(
        source_id="letter-a",
        text="Confirmed focal epilepsy.",
    )
    request = prepare_exect_request(source)
    response = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "evidence": "absent quotation",
                    "fact": "known epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
                {
                    "family": "diagnosis",
                    "evidence": "Confirmed focal epilepsy.",
                    "fact": "known epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
            ]
        }
    )
    artifact = replay_exect_response(
        request,
        source=source,
        saved_request_id=request.request_id,
        response_text=response,
    )

    projection = project_exect_artifact_with_trace(artifact, source=source)

    assert len(projection.prediction.mentions) == 1
    assert projection.projected_mention_raw_positions == (1,)


def test_provider_exception_without_message_is_retained_as_failed_attempt() -> None:
    source = SourceDocument.from_text(source_id="ordinary-note", text="Two per month.")
    request = prepare_gan_request(source)

    def timeout(_request):
        raise TimeoutError

    artifact = execute_gan_request(request, source=source, completion=timeout)

    assert artifact.status == "failed"
    assert artifact.attempts[0].status == "provider_error"
    assert artifact.attempts[0].error_type == "TimeoutError"
    assert artifact.attempts[0].error_message == "TimeoutError"


def test_longitudinal_artifact_serves_two_policies_and_both_cutoffs_immutably() -> None:
    case = Path("examples/longitudinal/authored_patient_001")
    manifest, documents, annotations = load_case(case)
    artifact = build_longitudinal_artifact(
        documents,
        annotations,
        artifact_kind="provisional_reference",
        query_independent_capture=True,
    )
    requests = {item["request_id"]: item for item in manifest["requests"]}
    before = artifact.content_sha256

    visit_q2 = evaluate_artifact_query(
        artifact,
        documents,
        requests["T1_visit_Q2"],
    )
    retrospective_q2 = evaluate_artifact_query(
        artifact,
        documents,
        requests["T1_retrospective_Q2"],
    )
    retrospective_q3 = evaluate_artifact_query(
        artifact,
        documents,
        requests["T1_retrospective_Q3"],
    )

    assert artifact.status == "ready"
    assert visit_q2.status == retrospective_q2.status == retrospective_q3.status == "ready"
    assert visit_q2.result["status"] == "eligible"
    assert retrospective_q2.result["status"] == "ineligible"
    assert retrospective_q3.result["status"] == "ineligible"
    assert visit_q2.policy_id != retrospective_q3.policy_id
    assert artifact.content_sha256 == before

    conditioned = build_longitudinal_artifact(
        documents,
        annotations,
        artifact_kind="saved_query_conditioned_prediction",
        query_independent_capture=False,
        input_cutoff=requests["T1_visit_Q2"]["information_cutoff"],
    )
    refused = evaluate_artifact_query(
        conditioned,
        documents,
        requests["T1_retrospective_Q3"],
    )
    assert refused.status == "unsupported"
    assert "query_conditioned_capture_not_reusable" in refused.unresolved_requirements

    changed_documents = deepcopy(documents)
    for document in changed_documents.values():
        document["available_date"] = "1900-01-01"
    changed_decision = evaluate_artifact_query(
        artifact,
        changed_documents,
        requests["T1_visit_Q2"],
    )
    changed_artifact = build_longitudinal_artifact(
        changed_documents,
        annotations,
        artifact_kind="provisional_reference",
        query_independent_capture=True,
    )
    assert changed_decision.status == "unsupported"
    assert any(
        item.startswith("source_document_mismatch:")
        for item in changed_decision.unresolved_requirements
    )
    assert changed_artifact.artifact_id != artifact.artifact_id

    no_medication = {
        **annotations,
        "assertions": [
            row
            for row in annotations["assertions"]
            if row["content"]["family"] != "medication"
        ],
    }
    no_medication_artifact = build_longitudinal_artifact(
        documents,
        no_medication,
        artifact_kind="provisional_reference_without_medication_facts",
        query_independent_capture=True,
    )
    no_medication_decision = evaluate_artifact_query(
        no_medication_artifact,
        documents,
        requests["T1_visit_Q3"],
    )
    assert "medication" in no_medication_artifact.coverage.capture_families
    assert no_medication_decision.status == "ready"
