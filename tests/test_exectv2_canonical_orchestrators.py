from __future__ import annotations

import hashlib
import json
from copy import deepcopy

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)

LETTER = ExectLetter(
    letter_id="synthetic-0047",
    note_text=(
        "Diagnosis: focal epilepsy. MRI brain normal. "
        "Levetiracetam 500 mg twice daily."
    ),
)


def _raw() -> str:
    return json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": "focal epilepsy",
                    "evidence": "Diagnosis: focal epilepsy",
                    "event_state": {},
                    "mentions": [
                        {"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {}}
                    ],
                    "confidence": "high",
                    "rationale": "The diagnosis is explicit.",
                },
                {
                    "family": "investigation",
                    "anchor_text": "MRI brain normal",
                    "evidence": "MRI brain normal",
                    "event_state": {},
                    "mentions": [
                        {"entity": "Investigations", "text": "MRI", "attributes": {}}
                    ],
                    "confidence": "high",
                    "rationale": "The investigation is explicit.",
                },
                {
                    "family": "medication",
                    "anchor_text": "Levetiracetam 500 mg twice daily",
                    "evidence": "Levetiracetam 500 mg twice daily",
                    "event_state": {},
                    "mentions": [
                        {
                            "entity": "Prescription",
                            "text": "Levetiracetam",
                            "attributes": {"DoseUnit": "mg", "Frequency": "2"},
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The prescription is explicit.",
                },
            ]
        }
    )


def test_structured_producer_is_replayable_and_policy_is_explicit() -> None:
    producer = structured_one_call.produce_structured_letter(
        LETTER,
        raw_output=_raw(),
        config=StructuredMethodConfig.selected(),
    )

    assert producer.raw_output == _raw()
    assert producer.call_error is None
    assert producer.row["prompt_profile"] == "full"
    assert producer.row["n_mentions_raw"] == 3
    assert producer.row["n_mentions_scored"] == 3


def test_primary_pair_reuses_one_immutable_producer(monkeypatch: pytest.MonkeyPatch) -> None:
    producer = structured_one_call.produce_structured_letter(LETTER, raw_output=_raw())
    calls = 0

    def fake_produce(*_args: object, **_kwargs: object):
        nonlocal calls
        calls += 1
        return producer

    monkeypatch.setattr(structured_one_call, "produce_structured_letter", fake_produce)
    llm_only, hybrid = structured_one_call.run_primary_pair(LETTER)

    assert calls == 1
    assert llm_only.producer is producer
    assert hybrid.producer is producer
    assert llm_only.row["method_id"] == "llm"
    assert llm_only.row["source_method_id"] == "exectv2_llm_only"
    assert hybrid.row["method_id"] == "llm_with_rules"
    assert hybrid.row["source_method_id"] == "exectv2_llm_with_rules"


def test_projection_order_preserves_deep_producer_and_requested_provenance() -> None:
    projections = {
        "hybrid": structured_one_call.run_llm_with_rules_letter,
        "llm": structured_one_call.run_llm_only_letter,
    }
    for order in (("hybrid", "llm"), ("llm", "hybrid")):
        producer = structured_one_call.produce_structured_letter(
            LETTER,
            raw_output=_raw(),
            mode="replay",
            split="dev140",
            model="fixture/model",
        )
        before_row = deepcopy(dict(producer.row))
        before_stages = tuple(event.to_dict() for event in producer.stage_events)
        before_fingerprint = hashlib.sha256(
            json.dumps(
                {"row": before_row, "stages": before_stages},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        results = [projections[name](LETTER, producer) for name in order]
        assert producer.row == before_row
        assert tuple(event.to_dict() for event in producer.stage_events) == before_stages
        after_fingerprint = hashlib.sha256(
            json.dumps(
                {"row": dict(producer.row), "stages": before_stages},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        assert after_fingerprint == before_fingerprint
        for result in results:
            assert result.producer is producer
            assert result.row["split"] == "dev140"
            assert result.row["producer_row"] == before_row
            assert result.row["producer_row"]["model"] == "fixture/model"
        assert {result.row["method_id"] for result in results} == {"llm", "llm_with_rules"}


def test_combined_policy_requires_an_archived_replay_opt_in() -> None:
    with pytest.raises(ValueError, match="archived_replay"):
        StructuredMethodConfig(diagnosis_policy_variant="combined")

    archived = StructuredMethodConfig.archived_combined()
    assert archived.diagnosis_policy_variant == "combined"
    assert archived.prescription_policy_variant == "combined"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"sf_projection_ablation": "none"},
        {"diagnosis_resolution_candidate": True},
        {"model_preserving_policy_candidate": True},
        {"prescription_rescue_scope_candidate": True},
    ],
)
def test_non_selected_policy_requires_archived_replay(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError, match="archived_replay"):
        StructuredMethodConfig(**kwargs)


def test_selected_hybrid_rejects_archived_policy() -> None:
    producer = structured_one_call.produce_structured_letter(LETTER, raw_output=_raw())

    with pytest.raises(ValueError, match="selected ExECT method"):
        structured_one_call.run_llm_with_rules_letter(
            LETTER,
            producer,
            config=StructuredMethodConfig.archived_combined(),
        )


def test_archived_hybrid_has_a_named_opt_in_entry_point() -> None:
    producer = structured_one_call.produce_structured_letter(LETTER, raw_output=_raw())

    result = structured_one_call.run_archived_llm_with_rules_letter(
        LETTER,
        producer,
        config=StructuredMethodConfig.archived_combined(),
    )

    assert result.row["policy"]["diagnosis_policy_variant"] == "combined"
    assert result.row["policy"]["prescription_policy_variant"] == "combined"


@pytest.mark.parametrize(
    "projection",
    [
        structured_one_call.run_llm_only_letter,
        structured_one_call.run_llm_with_rules_letter,
    ],
)
def test_method_projection_rejects_a_producer_for_another_letter(projection) -> None:
    producer = structured_one_call.produce_structured_letter(LETTER, raw_output=_raw())
    other = ExectLetter(letter_id="other-letter", note_text=LETTER.note_text)

    with pytest.raises(ValueError, match="producer letter_id"):
        projection(other, producer)


def test_terminal_provider_error_stops_before_placeholder_row() -> None:
    class TerminalFailureProgram:
        def __call__(self, **_kwargs: object) -> object:
            raise RuntimeError("AuthenticationError: invalid_api_key")

    with pytest.raises(RuntimeError, match="Terminal model-provider error"):
        structured_one_call.produce_structured_letter(
            LETTER,
            model="provider/model",
            mode="live",
            program=TerminalFailureProgram(),
        )


def test_split_runner_preserves_the_requested_split_identity() -> None:
    rows, _ = structured_one_call.run_split(
        [LETTER],
        split="synthetic-dev",
        model="fixture",
        temperature=0.0,
        max_tokens=1,
        mode="prompt-only",
    )

    assert rows[0]["split"] == "synthetic-dev"
