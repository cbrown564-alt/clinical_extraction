from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    tool_self_consistency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tool_self_consistency import (
    run_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord


def test_tool_self_consistency_votes_and_scores_against_reference(monkeypatch) -> None:
    labels = iter(("2 per week", "unknown", "2 per week", "2 per week"))

    def fake_model_call(prompt_input_json: str, *, model: str, temperature: float, max_tokens: int):
        del prompt_input_json, model, temperature, max_tokens
        label = next(labels)
        return (
            f'{{"final_label":"{label}","evidence":"2 seizures per week",'
            '"answer_kind":"frequency","selected_seizure_type":"seizure",'
            '"time_window":"current","confidence":"high",'
            '"rationale":"The note states 2 seizures per week."}'
        )

    monkeypatch.setattr(tool_self_consistency, "_run_model_call", fake_model_call)

    rows, metadata = run_split(
        [_record()],
        reference_rows=[_reference_row("unknown")],
        split="validation",
        split_manifest="gan2026_split_v1",
        model="openai/gpt-4.1-mini",
        temperature=0.0,
        max_tokens=900,
        mode="live",
        dspy_cache=True,
        api_base=None,
        progress_every=None,
        checkpoint_jsonl_path=None,
        checkpoint_report_path=None,
    )

    trace = rows[0]["condition_trace"]
    assert trace["final_label"] == "2 per week"
    assert trace["normalized_label_vote"]["vote_counts"] == {
        "2 per week": 3,
        "unknown": 1,
    }
    assert metadata["summary"]["purist_correct"] == 1
    assert metadata["summary"]["wins_vs_reference"] == 1
    assert metadata["summary"]["losses_vs_reference"] == 0
    assert metadata["gate"]["status"] == "reject_tool_self_consistency"


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=301,
        note_text="Clinic Date: 12 June 2026\nShe reports 2 seizures per week.",
        gold_label="2 per week",
        gold_reference="2 seizures per week",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per week",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(104.0, 104.0),
        gold_monthly_frequency=8.690476190476192,
    )


def _reference_row(label: str) -> dict:
    return {
        "source_row_index": 301,
        "condition_traces": {
            "single_self_consistency_temperature": {
                "final_label": label,
            }
        },
    }
