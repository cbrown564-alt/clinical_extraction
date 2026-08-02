"""Delegation and selected-entry structural gates for decision 0047."""

from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

from clinical_extraction.architecture.stage_manifest import METHOD_IDS, load_manifest


def test_selected_entry_points_all_resolve_to_task_local_orchestration() -> None:
    for method_id in METHOD_IDS:
        symbol = load_manifest(method_id).entry_point.symbol
        assert ".orchestration." in symbol, method_id


def test_gan_rules_compatibility_adapter_delegates(monkeypatch) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        deterministic_canonical,
    )

    sentinel = SimpleNamespace(to_pipeline_result=lambda: "delegated")
    seen = {}

    def spy(item, config):
        seen.update(item=item, config=config)
        return sentinel

    monkeypatch.setattr(deterministic_canonical, "run_record", spy)
    item = object()
    config = object()
    assert deterministic_canonical.run_item(item, config) == "delegated"
    assert seen == {"item": item, "config": config}


def test_exect_rules_batch_adapter_delegates(monkeypatch) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
        orchestrator,
    )

    seen = {}

    def spy(letters, **kwargs):
        seen.update(letters=letters, kwargs=kwargs)
        return ["delegated"]

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        rules,
    )

    monkeypatch.setattr(rules, "run_all9_on_letters", spy)
    letters = [object()]
    assert orchestrator.run_all9_on_letters(
        letters, include_diagnosis_resolution_candidate=True
    ) == ["delegated"]
    assert seen["letters"] is letters
    assert seen["kwargs"]["include_diagnosis_resolution_candidate"] is True


def test_exect_structured_runner_delegates(monkeypatch) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
        key_entities_structured,
    )

    runner = import_module(f"{key_entities_structured.__name__}.runner")
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )

    seen = {}

    def spy(letters, **kwargs):
        seen.update(letters=letters, kwargs=kwargs)
        return ["delegated"], {"canonical": True}

    monkeypatch.setattr(structured_one_call, "run_split", spy)
    letters = [object()]
    result = runner.run_split(
        letters,
        split="dev",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
    )
    assert result == (["delegated"], {"canonical": True})
    assert seen["letters"] is letters
    assert seen["kwargs"]["split"] == "dev"


def test_operational_assembly_delegates(monkeypatch) -> None:
    from clinical_extraction.operational import exect
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        letter_assembly,
    )

    seen = {}

    def spy(letters, rows, *, config):
        seen.update(letters=letters, rows=rows, config=config)
        return {"delegated": True}

    monkeypatch.setattr(letter_assembly, "assemble_structured_rows", spy)
    letters = [object()]
    rows = [object()]
    assert exect._assemble(letters, rows) == {"delegated": True}
    assert seen["letters"] is letters
    assert seen["rows"] is rows
    assert seen["config"].diagnosis_policy_variant == "default"
    assert seen["config"].prescription_policy_variant == "default"


def test_operational_gan_delegates_to_canonical_record(monkeypatch) -> None:
    from clinical_extraction.operational import gan
    from clinical_extraction.operational.io import InputNote
    from clinical_extraction.operational.runtime import RuntimeConfig
    from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
        llm_with_rules,
    )

    seen = {}
    sentinel = SimpleNamespace(
        output=SimpleNamespace(final_value="1 per month", evidence="source", rationale="why"),
        diagnostics={"parse_errors": [], "structured_record": {}},
    )

    def spy(record, config, **kwargs):
        seen.update(record=record, config=config, kwargs=kwargs)
        return sentinel

    monkeypatch.setattr(llm_with_rules, "run_record", spy)
    runtime = RuntimeConfig(
        base_url="http://fixture.invalid", api_key="fixture", model="openai/test"
    )
    result = gan.run_gan_notes([InputNote(note_id="n1", text="source")], runtime)

    assert result[0]["prediction"]["seizure_frequency"] == "1 per month"
    assert seen["config"].prompt_version == "gan2026_hybrid_structured_events_v0.5"
