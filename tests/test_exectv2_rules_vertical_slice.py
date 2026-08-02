"""Contract tests for the ExECT rules method's active public identity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

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


def _fingerprint(records: list[dict[str, object]]) -> str:
    payload = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in records
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_exect_rules_active_name_keeps_legacy_method_identity() -> None:
    assert active_method_name("rules") == "rules"
    assert active_method_name("rules_only") == "rules"
    assert active_method_name("exectv2_rules_only") == "rules"
    with pytest.raises(ValueError):
        active_method_name("deterministic_all9")
    with pytest.raises(ValueError):
        active_method_name("exectv2_deterministic_all9")
    assert retained_method_id("rules") == "exectv2_rules_only"


def test_exect_rules_public_runner_routes_aliases_to_canonical_active_runner(monkeypatch) -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import rules
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    letter = _letter()
    calls = 0
    real_run_letter = rules.run_letter

    def spy_run_letter(letter, **kwargs):
        nonlocal calls
        calls += 1
        return real_run_letter(letter, **kwargs)

    monkeypatch.setattr(rules, "run_letter", spy_run_letter)
    aliases = ("rules", "rules_only", "exectv2_rules_only")
    results = [
        Exectv2PipelineRunner(Exectv2PipelineConfiguration(method=alias)).run(letter)
        for alias in aliases
    ]
    assert calls == len(aliases)
    assert all(result.method == "rules" for result in results)
    assert all(
        len(result.result.prediction.diagnostics["active_entities"]) == 9
        for result in results
    )
    assert all(
        len(result.result.comparison_projection.mentions)
        <= len(result.result.prediction.mentions)
        for result in results
    )
    assert all(event.owner and event.action for event in results[0].result.stage_events)


def test_exect_rules_active_runner_matches_governed_independent_dev_base_fingerprint() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
        Exectv2PipelineConfiguration,
        Exectv2PipelineRunner,
    )

    fingerprint_path = Path("tests/fixtures/exectv2_rules_base_264237bd_fingerprint.json")
    expected = json.loads(fingerprint_path.read_text(encoding="utf-8"))
    letters = load_letters_for_split("dev")
    runner = Exectv2PipelineRunner(Exectv2PipelineConfiguration(method="rules"))

    extraction: list[dict[str, object]] = []
    full: list[dict[str, object]] = []
    for letter in letters:
        result = runner.run(letter).result
        prediction = result.prediction.model_dump(mode="json")
        extraction.append({"letter_id": letter.letter_id, "prediction": prediction})
        full.append(
            {
                "letter_id": letter.letter_id,
                "prediction": prediction,
                "comparison_projection": result.comparison_projection.model_dump(mode="json"),
                "stage_events": [event.to_dict() for event in result.stage_events],
            }
        )

    assert expected["source_commit"] == "264237bd"
    assert expected["row_count"] == 140
    assert len(letters) == expected["row_count"]
    assert _fingerprint(extraction) == expected["extraction_sha256"]
    assert _fingerprint(full) == expected["prediction_projection_trace_sha256"]


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
    assert "saved_run_id" not in active_rows[0]
    assert "retained_evidence_id" not in active_rows[0]
    assert "saved_run_id" not in active_metadata
    assert "retained_evidence_id" not in active_metadata


def test_exect_rules_split_allowlist_rejects_forbidden_aliases_before_processing() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.split import (
        DEVELOPMENT_SPLIT_ALIASES,
        run_split,
    )

    assert DEVELOPMENT_SPLIT_ALIASES == frozenset({"dev", "dev140"})

    class MustNotBeConsumed:
        def __iter__(self):
            raise AssertionError("split validation must happen before processing")

    for allowed_split in sorted(DEVELOPMENT_SPLIT_ALIASES):
        rows, metadata = run_split([_letter()], method="rules", split=allowed_split)
        assert rows
        assert metadata["split"] == allowed_split

    for forbidden_split in (
        "test",
        "test60",
        "holdout",
        "locked_test",
        "locked-test",
        "aggregate_only",
        "aggregate-only",
        "full",
        "full200",
        "all",
    ):
        with pytest.raises(ValueError, match="inspectable development split"):
            run_split(MustNotBeConsumed(), method="rules", split=forbidden_split)


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
    assert set(get_cli_specs()) == {
        "rules",
        "rules_only",
        "exectv2_rules_only",
        "llm",
        "llm_only",
        "exectv2_llm_only",
    }


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
    assert rows[0]["run_id"] == "rules"
    assert "saved_run_id" not in rows[0]
    assert "retained_evidence_id" not in rows[0]
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
