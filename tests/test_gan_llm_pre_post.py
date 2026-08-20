"""Always-on contract for the Gan candidate-suggestion prompt."""

from __future__ import annotations

import json

from clinical_extraction.paper.methods import LIVE_METHODS, split_for
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages import (
    extract_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_pre_post import (
    GAN_LLM_PRE_POST,
    LLM_PRE_POST_AUTHORED_KEYS,
    build_llm_pre_post_prompt_input,
    suggested_evidence_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_with_rules import (
    EVENT_SCHEMA,
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


def test_gan_llm_pre_post_is_a_live_paper_method() -> None:
    assert "gan_llm_pre_post" in LIVE_METHODS
    split_for("gan_llm_pre_post", "dev750")


def test_suggested_rows_reuse_deterministic_candidates() -> None:
    record = _record()
    rows = suggested_evidence_rows(record)
    _, _, events = extract_stage(
        record.note_text, source_row_index=record.source_row_index
    )
    assert rows
    assert {row["evidence"] for row in rows} == {event.evidence for event in events}
    assert {row["kind"] for row in rows} == {str(event.kind) for event in events}
    for row in rows:
        assert set(row) == {"kind", "evidence", "name_hint"}
        assert row["evidence"] in record.note_text


def test_pre_post_payload_asks_keep_reject_then_scan() -> None:
    payload = json.loads(build_llm_pre_post_prompt_input(_record()))
    blob = json.dumps(payload)
    assert set(payload) == set(LLM_PRE_POST_AUTHORED_KEYS)
    assert payload["event_schema"] == EVENT_SCHEMA
    assert "suggested_evidence" in payload
    assert payload["suggested_evidence"]
    assert "keep, reject, split, or merge" in blob
    assert "scan the rest of the letter" in blob.lower() or "scan the rest" in blob.lower()
    assert "Gan 2026" not in blob
    assert "prompt_version" not in payload
    assert "source_row_index" not in payload
    assert "gold" not in blob.lower()


def test_hybrid_dispatch_keeps_with_rules_default() -> None:
    before = hybrid_structured_events.PROMPT_VERSION
    payload = json.loads(
        hybrid_structured_events.build_prompt_input(
            _record(),
            prompt_version=GAN_LLM_PRE_POST,
        )
    )
    assert "suggested_evidence" in payload
    assert hybrid_structured_events.PROMPT_VERSION == before
    assert before == hybrid_structured_events.GAN_LLM_WITH_RULES
