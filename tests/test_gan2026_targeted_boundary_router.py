from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    targeted_boundary_router,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli import (
    pipeline_specs,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_targeted_boundary_router_is_registered_on_shared_cli_surface() -> None:
    spec = pipeline_specs()["targeted_boundary_router"]

    assert "router" in spec.description
    assert spec.default_max_tokens == 2000
    assert spec.default_structured_event_jsonl_path is not None


def test_router_prompt_uses_profiles_without_forbidden_labels() -> None:
    record = _record(
        920,
        "Clinic Date: 12 June 2026\nTwo brief collapses occurred in July and September.",
        gold_label="unknown",
        gold_monthly_frequency=1000.0,
    )
    prompt_input_json = targeted_boundary_router.build_prompt_input(
        record,
        _structured_event_row(
            920,
            final_label="2 per 3 month",
            final_kind="frequency",
            purist_correct=False,
        ),
    )
    payload = json.loads(prompt_input_json)
    payload_text = json.dumps(payload, ensure_ascii=False)

    assert "source_row_index" not in payload_text
    assert "gold_label" not in payload_text
    assert "gan2026_split_v1" not in payload_text
    assert "deterministic_top" not in payload_text
    assert "targeted_boundary_router" == payload["variant"]
    assert "sentinel_boundary" in payload["router_profiles"]
    assert "rate_denominator" in payload["router_profiles"]
    assert "cluster_burden" in payload["router_profiles"]
    assert payload["router_hints"]["possible_profiles"][0]["profile"] == (
        "sentinel_boundary"
    )
    assert payload["router_hints"]["possible_profiles"][0]["candidate_event_ids"] == [
        "e2"
    ]
    assert "keep_original_structured_event_final" in payload["required_output_schema"]["action"]
    assert "replace_with_existing_event" in payload["required_output_schema"]["action"]
    assert any(
        "Route first" in instruction
        for instruction in payload["instructions"]
    )
    assert any(
        "Anchored numeric mentions" in instruction
        for instruction in payload["instructions"]
    )


def test_live_router_scores_selected_existing_boundary_event(monkeypatch) -> None:
    def fake_model_call(
        prompt_input_json: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        del model, temperature, max_tokens
        assert "deterministic_top" not in prompt_input_json
        return json.dumps(
            {
                "action": "replace_with_existing_event",
                "final_label": "unknown",
                "final_kind": "unknown",
                "selected_event_ids": ["e2"],
                "rejected_event_ids": ["e1"],
                "evidence": ["spells are uncommon when meals are regular"],
                "contradiction_profile": ["router:sentinel_boundary"],
                "calculation_trace": "anchored count is not a recurring cadence",
                "clinical_rationale": (
                    "The numeric count is anchored to named occasions, while e2 "
                    "states an unquantified current pattern."
                ),
                "uncertainty": "low",
                "tool_calls": [],
                "attribution": "llm_selected_tool_rendered",
            }
        )

    monkeypatch.setattr(targeted_boundary_router, "_run_model_call", fake_model_call)

    rows, metadata = targeted_boundary_router.run_split(
        [
            _record(
                921,
                "Clinic Date: 12 June 2026\nspells are uncommon when meals are regular.",
                gold_label="unknown",
                gold_monthly_frequency=1000.0,
            )
        ],
        structured_event_rows=[
            _structured_event_row(
                921,
                final_label="2 per 3 month",
                final_kind="frequency",
                purist_correct=False,
            )
        ],
        structured_event_source_path=Path("v0.jsonl"),
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=2000,
        mode="live",
        dspy_cache=True,
        api_base=None,
        escalation_reason=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    row = rows[0]

    assert metadata["summary"]["model_calls_attempted"] == 1
    assert metadata["summary"]["wrong_to_correct_vs_v0"] == 1
    assert metadata["summary"]["correct_to_wrong_vs_v0"] == 0
    assert metadata["summary"]["router_profiles"] == {"router:sentinel_boundary": 1}
    assert row["score_layers"]["final"]["final_label"] == "unknown"
    assert row["transition_vs_v0"]["purist_transition"] == "wrong_to_correct"
    assert row["decision_record"]["selected_event_ids"] == ["e2"]
    assert row["evidence_valid"] is True


def _record(
    source_row_index: int,
    note_text: str,
    *,
    gold_label: str = "unknown",
    gold_monthly_frequency: float = 1000.0,
) -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=gold_label,
        gold_label_kind=FrequencyLabelKind.UNKNOWN,
        gold_yearly_bounds=None,
        gold_monthly_frequency=gold_monthly_frequency,
    )


def _structured_event_row(
    source_row_index: int,
    *,
    final_label: str,
    final_kind: str,
    purist_correct: bool,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "two recent occasions (July and September)",
                    "temporality": "recent",
                    "assertion_status": "asserted",
                    "applies_to": "seizures",
                    "evidence": (
                        "brief collapses have occurred on two recent occasions "
                        "(July and September)"
                    ),
                    "time_window": "recent",
                },
                {
                    "event_id": "e2",
                    "kind": "unknown_frequency",
                    "raw_value": "spells are uncommon when meals are regular",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "applies_to": "spells",
                    "evidence": "spells are uncommon when meals are regular",
                    "time_window": "current",
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": final_label,
                "evidence": (
                    "brief collapses have occurred on two recent occasions "
                    "(July and September)"
                ),
                "confidence": "high",
                "rationale": "Original structured-event selection.",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": final_label,
                "semantic_kind": final_kind,
                "monthly_frequency": 0.6666666667,
                "validation_errors": [],
            },
            {
                "event_id": "e2",
                "normalized_label": "unknown",
                "semantic_kind": "unknown",
                "monthly_frequency": 1000.0,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": purist_correct,
            "pragmatic_correct": purist_correct,
        },
        "evidence_valid": True,
    }
