"""No-call reconstruction of Gan paper replay rows from saved raw_output."""

from __future__ import annotations

import json

from clinical_extraction.paper.gan import hydrate_saved_raw_row, reparse_gan_llm_extract_raw
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    ROW_TRACE_SCHEMA_VERSION,
)


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


def _hybrid_raw() -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency",
                    "raw_value": "two seizures per month",
                    "applies_to": "seizures",
                    "time_window": "present",
                    "temporality": "ongoing",
                    "assertion_status": "asserted",
                    "evidence": "two seizures per month",
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "current frequency",
                "final_label": "2 per month",
                "evidence": "two seizures per month",
                "confidence": 0.91,
                "rationale": "The note states the present seizure frequency.",
            },
        }
    )


def test_hydrate_saved_hybrid_row_rebuilds_structured_trace() -> None:
    row = hydrate_saved_raw_row(
        "gan_llm_extract_raw",
        _record(),
        _hybrid_raw(),
    )

    assert row["reused_raw_output"] is True
    assert row["structured_record"]["selection"]["final_label"] == "2 per month"
    assert row["normalized_events"]
    assert row["normalized_events"][0]["event_id"] == "e1"
    assert row["row_trace"]["schema_version"] == ROW_TRACE_SCHEMA_VERSION
    assert row["row_trace"]["method"] == "llm_with_rules"
    assert row["comparison"]["purist_correct"] is True


def test_hydrate_saved_hybrid_row_can_stop_at_encode_rules() -> None:
    row = hydrate_saved_raw_row(
        "gan_llm_extract_raw",
        _record(),
        _hybrid_raw(),
        repair_mode="llm_encode",
    )

    assert row["structured_record"]["selection"]["final_label"] == "2 per month"
    assert row["row_trace"]["method"] == "llm_with_rules"


def test_hydrate_saved_llm_only_row_rebuilds_decision_trace() -> None:
    raw = json.dumps(
        {
            "final_label": "2 per month",
            "evidence": "two seizures per month",
            "answer_kind": "frequency",
            "selected_seizure_type": "seizures",
            "time_window": "current",
            "applied_rule_families": ["concrete_frequency_precedence"],
            "confidence": "high",
            "rationale": "The note explicitly gives the current frequency.",
        }
    )
    row = hydrate_saved_raw_row("gan_llm_only", _record(), raw)

    assert row["decision_record"]["final_label"] == "2 per month"
    assert row["row_trace"]["schema_version"] == ROW_TRACE_SCHEMA_VERSION
    assert row["row_trace"]["method"] == "llm_only"
    assert "structured_record" not in row


def test_reparse_gan_llm_extract_raw_uses_saved_raw_and_no_call(
    tmp_path, monkeypatch
) -> None:
    dest = tmp_path / "paper_experiments/gan/gan_llm_extract_raw/grok46/dev750"
    dest.mkdir(parents=True)
    raw = _hybrid_raw()
    (dest / "rows.jsonl").write_text(
        json.dumps(
            {
                "source_row_index": 10,
                "prompt_version": "gan_llm_extract_raw",
                "raw_output": raw,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (dest / "comparison.json").write_text(
        json.dumps(
            {
                "method": "gan_llm_extract_raw",
                "model_slug": "grok46",
                "model": "x-ai/grok-4.6",
                "split": "dev750",
                "prompt_version": "gan_llm_extract_raw",
                "row_count": 1,
                "row_policy": "development_review_permitted",
                "live": True,
                "model_calls": 1,
                "summary": {"purist_correct": 0, "purist_accuracy": 0.0},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("clinical_extraction.paper.gan.ROOT", tmp_path)
    monkeypatch.setattr(
        "clinical_extraction.paper.gan.load_records_for_split",
        lambda _machine: [_record()],
    )
    monkeypatch.setattr("clinical_extraction.paper.gan.gan_row_count", lambda _split: 1)

    payload = reparse_gan_llm_extract_raw("grok46", "dev750")

    assert payload["replay_mode"] == "no_call"
    assert payload["model_calls"] == 0
    assert payload["reused_raw_outputs"] == 1
    comparison = json.loads((dest / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["replay_mode"] == "no_call"
    assert comparison["live"] is False
    assert comparison["model_calls"] == 0
    assert comparison["summary"]["reused_raw_outputs"] == 1
    assert comparison["summary"]["purist_correct"] == 1
    replay = json.loads((dest / "rows.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert replay["raw_output"] == raw
    scored = json.loads((dest / "scored.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert scored["purist_correct"] is True
