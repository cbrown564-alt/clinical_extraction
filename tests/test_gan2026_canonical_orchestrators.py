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
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.naming import (
    active_pipeline_name,
    retained_pipeline_id,
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


def test_gan_llm_active_name_and_legacy_identity_share_one_boundary() -> None:
    assert active_pipeline_name("llm") == "llm"
    assert active_pipeline_name("llm_only_canonical_pipeline") == "llm"
    assert retained_pipeline_id("llm") == "llm_only_canonical_pipeline"


def test_gan_hybrid_active_name_is_used_by_live_split_configuration() -> None:
    assert active_pipeline_name("llm_with_rules") == "llm_with_rules"
    assert active_pipeline_name("hybrid_structured_events") == "llm_with_rules"
    assert retained_pipeline_id("llm_with_rules") == "hybrid_structured_events"
    assert PipelineConfiguration(architecture="llm_with_rules").architecture == "llm_with_rules"


def test_gan_rules_canonical_record_preserves_stage_order_and_avoids_gold() -> None:
    result = run_record(
        _record("The patient has one seizure per month."),
        PipelineConfiguration(architecture="rules"),
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
        PipelineConfiguration(architecture="llm"),
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


def test_gan_hybrid_runner_active_and_legacy_dispatch_is_strictly_no_call(
    monkeypatch,
) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
    from clinical_extraction.tasks.seizure_frequency.gan2026.runner import (
        Gan2026PipelineRunner,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        hybrid_structured_events,
    )

    seen: list[str] = []
    sentinel = object()

    def fake_run_item(item, config):
        seen.append(config.architecture)
        return sentinel

    def fail_model_builder(*args, **kwargs):
        raise AssertionError("runner dispatch unexpectedly built a model provider")

    monkeypatch.setattr(hybrid_structured_events, "run_item", fake_run_item)
    monkeypatch.setattr(
        "clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.scaffolding.configure_split_lm",
        fail_model_builder,
    )

    base = _record("The patient has one seizure per month.")
    label = label_to_frequency_record("1 per month")
    record = GanFrequencyRecord(
        **base.__dict__,
        gold_normalized_label=label.normalized_label,
        gold_label_kind=label.kind,
        gold_yearly_bounds=label.yearly_bounds,
        gold_monthly_frequency=label.monthly_frequency,
    )
    active = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="llm_with_rules")
    ).run(record)
    legacy = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="hybrid_structured_events")
    ).run(record)

    assert active is sentinel
    assert legacy is sentinel
    assert seen == ["llm_with_rules", "hybrid_structured_events"]
