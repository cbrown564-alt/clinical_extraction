"""Always-on contract for the five-rung paper table."""

from __future__ import annotations

import json

from clinical_extraction.paper.answer_states import graph_from_hops, make_hop
from clinical_extraction.paper.rungs import (
    EXECT_HOP_EFFECT_CLASS,
    EXECT_RUNG_SOURCE,
    GAN_REPAIR_MODE_FOR_RUNG,
    GAN_RUNG_SOURCE,
    RESULT_COLUMNS,
    RUNG_IDS,
    gan_method_for_rung,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly import (
    MATERIALIZED_SURFACES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json_with_trace,
)


def _record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text=(
            "the observed frequency is noted as ≤ four per day, with variable clustering"
        ),
        gold_label="4 per day",
        gold_reference="≤ four per day",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="4 per day",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(1460.0, 1460.0),
        gold_monthly_frequency=120.0,
    )


def _bound_raw() -> str:
    return json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "raw_value": "≤ four per day",
                    "applies_to": "observed seizures",
                    "time_window": "current",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": (
                        "the observed frequency is noted as ≤ four per day, "
                        "with variable clustering"
                    ),
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "≤ 4 per day",
                "evidence": (
                    "the observed frequency is noted as ≤ four per day, "
                    "with variable clustering"
                ),
                "confidence": "high",
                "rationale": "Accommodation logs give the current count.",
            },
        }
    )


def test_result_columns_are_the_five_rungs() -> None:
    assert RUNG_IDS == (
        "rules_only",
        "llm_schema",
        "llm_format",
        "llm_post",
        "llm_pre_post",
    )
    assert RESULT_COLUMNS == RUNG_IDS
    assert "gan_llm_only" not in RESULT_COLUMNS
    assert gan_method_for_rung("llm_post") == "gan_llm_with_rules"
    assert gan_method_for_rung("llm_pre_post") == "gan_llm_pre_post"
    assert GAN_REPAIR_MODE_FOR_RUNG["llm_schema"] == "raw_model"
    assert GAN_REPAIR_MODE_FOR_RUNG["llm_format"] == "selected_evidence_derivation"
    assert GAN_REPAIR_MODE_FOR_RUNG["llm_post"] == "hybrid_full_stack"
    assert GAN_RUNG_SOURCE["llm_schema"] == "replay_gan_llm_with_rules"
    assert GAN_RUNG_SOURCE["llm_pre_post"] == "new_request"
    assert EXECT_RUNG_SOURCE["llm_schema"] == "replay_exect_llm_only"
    assert EXECT_RUNG_SOURCE["llm_pre_post"] == "living_exect_llm_with_rules"


def test_selected_evidence_render_keeps_the_same_event() -> None:
    raw = _bound_raw()
    note = _record().note_text
    schema, _, _, schema_trace = parse_structured_json_with_trace(
        raw,
        note_text=note,
        repair_config=StructuredRepairConfig.for_mode("raw_model"),
    )
    rendered, _, _, format_trace = parse_structured_json_with_trace(
        raw,
        note_text=note,
        repair_config=StructuredRepairConfig.for_mode("selected_evidence_derivation"),
    )
    assert schema is not None
    assert rendered is not None
    assert schema.selection.selected_event_ids == ["e1"]
    assert rendered.selection.selected_event_ids == ["e1"]
    assert schema.selection.final_label == "≤ 4 per day"
    assert rendered.selection.final_label == "4 per day"
    hops = format_trace["answer_states"]
    render_hops = [hop for hop in hops if hop["stage_id"] == "gan.render.selected_evidence"]
    assert render_hops
    assert render_hops[0]["effect_class"] == "format"
    assert render_hops[0]["rung"] == 3
    assert render_hops[0]["operands"] == ["e1"]


def test_hop_log_keeps_every_label_version() -> None:
    hops = [
        make_hop(
            stage_id="gan.model.selection",
            owner="model",
            effect_class="semantic",
            before=None,
            after="seizure free since then",
            evidence="She has remained seizure-free since then.",
            operands=["e2"],
            rung=2,
        ),
        make_hop(
            stage_id="gan.render.selected_evidence",
            owner="replay",
            effect_class="format",
            before="seizure free since then",
            after="seizure free for multiple month",
            evidence="She has remained seizure-free since then.",
            operands=["e2"],
            rung=3,
        ),
        make_hop(
            stage_id="gan.select.post_change_burst",
            owner="replay",
            effect_class="semantic",
            before="seizure free for multiple month",
            after="2 to 3 per 1 month",
            evidence="Shortly afterwards, she experienced 2 to 3 seizures",
            operands=["e1"],
            rung=4,
        ),
    ]
    graph = graph_from_hops(
        hops,
        unused_candidates=(
            {
                "id": "e1",
                "label": "2 to 3 seizures",
                "kind": "frequency_rate",
            },
        ),
    )
    labels = [node["label"] for node in graph["nodes"] if node["kind"] == "answer"]
    assert labels == [
        "seizure free since then",
        "seizure free for multiple month",
        "2 to 3 per 1 month",
    ]
    assert len(graph["edges"]) == 2
    unused = [node for node in graph["nodes"] if node["kind"] == "unused_candidate"]
    assert unused[0]["id"] == "e1"


def test_exect_format_stop_is_not_dictionary_rewrite() -> None:
    assert "format_only" in MATERIALIZED_SURFACES
    assert MATERIALIZED_SURFACES.index("format_only") < MATERIALIZED_SURFACES.index(
        "dictionary_normalized"
    )


def test_exect_hops_use_the_same_effect_class_names() -> None:
    assert set(EXECT_HOP_EFFECT_CLASS.values()) <= {
        "schema",
        "format",
        "semantic",
        "validation",
        "projection",
    }
    assert EXECT_HOP_EFFECT_CLASS["exect.format.stop"] == "format"
    assert EXECT_HOP_EFFECT_CLASS["exect.select.dictionary"] == "semantic"
    assert EXECT_HOP_EFFECT_CLASS["exect.select.residual"] == "semantic"
