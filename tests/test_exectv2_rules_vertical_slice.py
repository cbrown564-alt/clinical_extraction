"""Contract tests for the ExECT rules method's active public identity."""

from __future__ import annotations

from pathlib import Path

from clinical_extraction.architecture import stage_manifest
from clinical_extraction.architecture.teaching_case import build_exect_case
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.naming import (
    active_method_name,
    retained_method_id,
)


def _letter() -> ExectLetter:
    return ExectLetter(
        letter_id="RULES-VERTICAL-1",
        note_text="Diagnosis: focal epilepsy. She has two seizures per month.",
    )


def test_exect_rules_active_name_keeps_legacy_method_identity() -> None:
    assert active_method_name("rules") == "rules"
    assert active_method_name("rules_only") == "rules"
    assert active_method_name("exectv2_rules_only") == "rules"
    assert active_method_name("deterministic_all9") == "rules"
    assert retained_method_id("rules") == "exectv2_rules_only"


def test_exect_rules_public_runner_has_exact_no_call_legacy_parity(monkeypatch) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
        all_entities,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    monkeypatch.setattr(
        all_entities,
        "run_all9_on_letters",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("compatibility batch adapter must not own runner parity")
        ),
    )
    letter = _letter()
    active = Exectv2PipelineRunner(
        Exectv2PipelineConfiguration(method="rules")
    ).run(letter)
    legacy = Exectv2PipelineRunner(
        Exectv2PipelineConfiguration(method="exectv2_rules_only")
    ).run(letter)

    assert active.result.prediction.letter_id == legacy.result.prediction.letter_id
    assert [m.entity for m in active.result.prediction.mentions] == [
        m.entity for m in legacy.result.prediction.mentions
    ]
    assert [m.attributes for m in active.result.prediction.mentions] == [
        m.attributes for m in legacy.result.prediction.mentions
    ]
    assert [m.evidence for m in active.result.prediction.mentions] == [
        m.evidence for m in legacy.result.prediction.mentions
    ]
    assert active.result.prediction.diagnostics == legacy.result.prediction.diagnostics
    assert active.result.comparison_projection.model_dump(mode="json") == (
        legacy.result.comparison_projection.model_dump(mode="json")
    )
    assert active.model_dump(mode="json") == legacy.model_dump(mode="json")
    assert all(event.owner and event.action for event in active.result.stage_events)
    assert active.method == "rules"
    assert active.result.stage_events


def test_exect_trace_generation_calls_active_rules_boundary(monkeypatch, tmp_path: Path) -> None:
    from clinical_extraction.trace_explorer import exectv2_comparison

    calls = 0
    real_run_letter = exectv2_comparison.rules.run_letter

    def spy_run_letter(letter, **kwargs):
        nonlocal calls
        calls += 1
        return real_run_letter(letter, **kwargs)

    monkeypatch.setattr(exectv2_comparison.rules, "run_letter", spy_run_letter)
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments" / "exectv2_deterministic_all9_dev_20260714.json").write_text(
        "{}\n", encoding="utf-8"
    )
    result = exectv2_comparison._deterministic_run(tmp_path, [_letter()])

    assert calls == 1
    assert result["run_id"] == "rules"
    assert result["saved_run_id"] == "exectv2_deterministic_all9_dev140"
    assert result["retained_evidence_id"] == "exectv2_deterministic_all9_dev_20260714"


def test_exect_rules_split_active_and_legacy_aliases_are_no_call_parity() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import (
        run_split,
    )

    kwargs = dict(
        split="dev",
        model="ignored",
        temperature=0.0,
        max_tokens=0,
        mode="no-call",
    )
    active_rows, active_metadata = run_split([_letter()], method="rules", **kwargs)
    legacy_rows, legacy_metadata = run_split(
        [_letter()], method="exectv2_rules_only", **kwargs
    )

    assert active_rows == legacy_rows
    assert active_metadata == legacy_metadata
    assert active_metadata["pipeline_family"] == "rules"
    assert active_rows[0]["call_error"] is None


def test_exect_rules_cli_spec_dispatches_active_method(monkeypatch) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.cli_specs import (
        get_cli_specs,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners import (
        split as split_runner,
    )

    seen: dict[str, str] = {}

    def fake_run_split(letters, **kwargs):
        seen["method"] = kwargs["method"]
        return [], {}

    monkeypatch.setattr(split_runner, "run_split", fake_run_split)
    get_cli_specs()["rules"].run_split([], split="dev", model="none")

    assert seen["method"] == "rules"


def test_exect_rules_operational_api_is_no_call_and_traceable() -> None:
    from clinical_extraction.operational.exect import run_exect_notes
    from clinical_extraction.operational.io import InputNote
    from clinical_extraction.operational.runtime import RuntimeConfig

    rows = run_exect_notes(
        [InputNote("RULES-API-1", _letter().note_text)],
        RuntimeConfig(base_url="", api_key="", model="(model-independent)"),
        method="rules",
    )

    assert rows[0]["status"] == "ok"
    assert rows[0]["pipeline"] == "rules"
    assert rows[0]["comparison_projection"]["letter_id"] == "RULES-API-1"
    assert rows[0]["trace"][-1]["owner"] == "scorer"


def test_exect_rules_registry_accepts_active_family_without_rewriting_saved_id() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
        deterministic_all9_scorecard,
    )

    entry = deterministic_all9_scorecard._registry_entry(
        {
            "generated_on": "2026-08-02",
            "split": "dev",
            "row_count": 1,
            "call_failures": 0,
            "parse_failures": 0,
            "schema_repairs": 0,
            "mentions_total": 0,
            "mentions_with_cui": 0,
            "cui_attachment_rate": 1.0,
            "routing_count": 0,
            "active_entities": [],
            "validation": {
                "schema_error_count": 0,
                "evidence_not_substring_count": 0,
                "evidence_validity_rate": 1.0,
            },
            "scores": {
                layer: {"per_item": {"f1": 0.0}, "per_letter": {"f1": 0.0}}
                for layer in ("phrase_only", "semantic", "benchmark")
            },
            "prescription_component_scores": {
                "clinical_headline": {"f1": 0.0}
            },
            "prescription_benchmark_projection_scores": {
                "benchmark_with_cui": {"f1": 0.0}
            },
        },
        json_path=Path("experiments/rules.json"),
        md_path=Path("experiments/rules.md"),
    )

    assert entry.run_id == "exectv2_deterministic_all9_dev_20260802"
    assert entry.pipeline_family == "rules"
    assert entry.architecture_family == "rules"


def test_exect_rules_manifest_and_teaching_case_use_active_method_name() -> None:
    manifest = stage_manifest.load_manifest("exectv2_rules_only")
    assert manifest.method == "rules"
    case = build_exect_case()
    assert case.runs[0].manifest.method == "rules"
