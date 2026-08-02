from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.llm import (
    run_record as run_llm_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.rules import (
    run_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def _record(note_text: str) -> GanRecord:
    return GanRecord(
        source_row_index=7,
        note_text=note_text,
        gold_label="1 per month",
        gold_reference="synthetic",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )


def test_gan_rules_canonical_record_preserves_stage_order_and_avoids_gold() -> None:
    result = run_record(
        _record("The patient has one seizure per month."),
        PipelineConfiguration(architecture="deterministic_canonical_pipeline"),
    )

    assert result.output.final_value == "1 per month"
    assert [event.stage_id for event in result.stage_events] == [
        "gan.rules.extract",
        "gan.rules.normalize",
        "gan.rules.select_and_render",
        "gan.rules.evidence_trace_check",
        "gan.rules.score",
    ]
    assert result.diagnostics["evidence_valid"] is True
    assert result.scorer_projection["final_label"] == result.output.final_value
    assert "gold" not in repr(result.diagnostics).lower()


def test_gan_rules_compatibility_runner_delegates_to_same_result() -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        deterministic_canonical,
    )

    record = _record("The patient has one seizure per month.")
    config = PipelineConfiguration(architecture="deterministic_canonical_pipeline")

    canonical = run_record(record, config).to_pipeline_result()
    adapted = deterministic_canonical.run_item(record, config)

    assert adapted.model_dump() == canonical.model_dump()


def test_gan_rules_active_method_dispatches_to_the_canonical_orchestrator() -> None:
    record = _record("The patient has one seizure per month.")
    active = run_record(record, PipelineConfiguration(architecture="rules"))
    legacy = run_record(
        record,
        PipelineConfiguration(architecture="deterministic_canonical_pipeline"),
    )

    assert active.to_pipeline_result().model_dump() == legacy.to_pipeline_result().model_dump()


def test_gan_public_runner_rules_path_preserves_full_result_contract() -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.runner import Gan2026PipelineRunner

    record = _record("The patient has one seizure per month.")
    active = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="rules")
    ).run(record)
    legacy = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="deterministic_canonical_pipeline")
    ).run(record)

    assert active.model_dump() == legacy.model_dump()
    assert active.diagnostics["evidence_valid"] is True
    assert active.diagnostics["final_selection"]["final_label"] == "1 per month"


def test_gan_llm_canonical_replay_keeps_model_boundary_and_evidence_gate() -> None:
    record = _record("The patient has one seizure per month.")
    raw = (
        '{"final_label":"1 per month","evidence":"one seizure per month",'
        '"answer_kind":"frequency","selected_seizure_type":null,'
        '"time_window":"current","applied_rule_families":[],'
        '"confidence":"high","rationale":"The current rate is explicit."}'
    )

    result = run_llm_record(
        record,
        PipelineConfiguration(architecture="llm_only_canonical_pipeline"),
        mode="prompt-only",
        raw_output=raw,
    )

    assert result.output.final_value == "1 per month"
    assert result.raw_model_output == raw
    assert result.parsed_model_output is not None
    assert result.diagnostics["evidence_text_contained"] is True
    assert [event.stage_id for event in result.stage_events] == [
        "gan.llm.build_prompt",
        "gan.llm.model_call",
        "gan.llm.json_schema_repair",
        "gan.llm.schema_validation",
        "gan.llm.selected_evidence_repair",
        "gan.llm.scorable_label_check",
        "gan.llm.evidence_containment",
        "gan.llm.score",
    ]
