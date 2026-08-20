"""Fact-keyed lineage for the Assembly Line teaching surface.

One predicted fact, the transforms that touched it, gold only at the end.
"""

from __future__ import annotations

from clinical_extraction.architecture.fact_lineage import _render_unit
from clinical_extraction.architecture.paper_teaching_cases import (
    build_paper_teaching_letters,
)


def _case(letter_id: str):
    return next(
        case
        for case in build_paper_teaching_letters()
        if case.letter_id == letter_id
    )


def _run(letter_id: str, method_id: str):
    case = _case(letter_id)
    return case, next(run for run in case.runs if run.method_id == method_id)


def test_paper_hybrid_runs_publish_fact_ids_spans_and_gold() -> None:
    _, e2 = _run("EA0057", "exectv2_llm_pre_post")
    assert e2.facts, "EA0057 hybrid must expose predicted facts"
    for fact in e2.facts:
        assert fact.fact_id
        payload = fact.to_dict()
        assert "span" in payload
        assert payload["gold"]["label"]
        assert payload["transforms"][-1]["stage_id"] != "gold"
        assert fact.gold.label


def test_ea0057_hybrid_structural_epilepsy_shows_diagnosis_lens_only() -> None:
    _, run = _run("EA0057", "exectv2_llm_pre_post")
    fact = next(
        item
        for item in run.facts
        if item.span is not None and "structural" in item.span.text.lower()
    )
    stage_ids = [step.stage_id for step in fact.transforms]
    assert any(step.stage_id.endswith("lens.diagnosis") for step in fact.transforms)
    diagnosis = next(
        step for step in fact.transforms if step.stage_id.endswith("lens.diagnosis")
    )
    assert diagnosis.idle is False
    assert "symptomatic structural" in diagnosis.entered.lower()
    assert "symptomatic structural focal epilepsy" in diagnosis.left.lower()
    assert not any(".lens.seizure_frequency" in stage_id for stage_id in stage_ids)
    assert not any(".lens.prescription" in stage_id for stage_id in stage_ids)
    assert not any(".lens.investigations" in stage_id for stage_id in stage_ids)
    assert fact.gold.has_counterpart is True
    assert "structural" in fact.gold.label.lower()
    propose = next(
        step for step in fact.transforms if step.stage_id.endswith("model_call")
    )
    assert "CUI" not in propose.left
    assert "CUIPhrase" not in propose.left
    assert "DiagCategory" in propose.left
    assert propose.note != "Model proposed this mention."


def test_gan15431_hybrid_cluster_span_shows_selected_evidence_only() -> None:
    case, run = _run("GAN-15431", "gan2026_llm_with_rules")
    fact = next(
        item
        for item in run.facts
        if item.span is not None
        and "seizure-free" in item.span.text.lower()
        and "cluster" in item.span.text.lower()
    )
    repair_ids = [
        step.stage_id
        for step in fact.transforms
        if ".repair." in step.stage_id
    ]
    assert repair_ids == ["gan.llm_with_rules.repair.selected_evidence"]
    rewrite = fact.transforms[-2] if fact.transforms[-1].band == "leave" else None
    selected = next(
        step
        for step in fact.transforms
        if step.stage_id.endswith("repair.selected_evidence")
    )
    assert selected.idle is False
    assert selected.entered != selected.left
    assert fact.gold.label == case.gold
    assert rewrite is not None or selected in fact.transforms


def test_unattributed_letter_stages_are_not_copied_onto_every_fact() -> None:
    _, run = _run("GAN-15431", "gan2026_llm_with_rules")
    for fact in run.facts:
        stage_ids = [step.stage_id for step in fact.transforms]
        assert "gan.llm_with_rules.build_prompt" not in stage_ids
        assert "gan.llm_with_rules.format_only_retry" not in stage_ids
        assert not any(
            stage_id.endswith("repair.monthly_diary") for stage_id in stage_ids
        )


def test_lineage_render_drops_event_state_scratchpad() -> None:
    rendered = _render_unit(
        {
            "family": "seizure_frequency",
            "anchor_text": "focal to bilateral convulsive seizures",
            "event_state": {
                "attributes": {},
                "frequency": "Last focal to bilateral convulsive seizure was on Christmas day 2009",
            },
            "mentions": [
                {
                    "entity": "SeizureFrequency",
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "YearDate": "2009",
                    },
                }
            ],
        }
    )
    assert "event_state" not in rendered
    assert "NumberOfSeizures" in rendered


def test_ea0057_parse_does_not_surface_event_state_copy() -> None:
    _, run = _run("EA0057", "exectv2_llm_pre_post")
    fact = next(
        item
        for item in run.facts
        if item.span is not None and "christmas" in item.span.text.lower()
    )
    propose = next(
        step for step in fact.transforms if step.stage_id.endswith("model_call")
    )
    parse = next(step for step in fact.transforms if "parse" in step.stage_id)
    assert "event_state" not in propose.left
    assert "event_state" not in parse.left
    assert "confidence" not in parse.left
    assert "mentions" not in parse.left


def test_exect_frequency_fact_keeps_attributes_through_parse_and_leave() -> None:
    _, run = _run("EA0057", "exectv2_llm_pre_post")
    fact = next(
        item
        for item in run.facts
        if item.span is not None
        and "two years" in item.span.text.lower()
        and "focal motor" in item.label.lower()
    )
    parse = next(step for step in fact.transforms if "parse" in step.stage_id)
    leave = next(step for step in fact.transforms if step.band == "leave")
    assert "NumberOfSeizures" in parse.left
    assert "NumberOfSeizures" in leave.left
    lens = next(
        step
        for step in fact.transforms
        if step.stage_id.endswith("lens.seizure_frequency")
    )
    assert "NumberOfSeizures" in lens.entered
    assert "NumberOfSeizures" in lens.left


def test_g3_rules_has_no_clickable_span_and_still_shows_gold() -> None:
    case, run = _run("GAN-2166", "gan2026_rules_only")
    clickable = [fact for fact in run.facts if fact.span is not None]
    assert clickable == []
    assert run.gold_unit.label == case.gold
