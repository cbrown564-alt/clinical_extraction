"""Frozen catalogue records pin the encode/revise frame."""

from __future__ import annotations

from clinical_extraction.paper.rule_records import (
    RULE_BY_NAME,
    RULE_RECORDS,
    SELECT_HIERARCHY,
    SELECT_KINDS,
    records_for,
)

_RETIRED_RULE_NAMES = frozenset(
    {
        "basic_label_repair_format_only",
        "clean_scorer_facing_gold_policy",
        "month_x_typical_preserve",
        "absence_preservation_residual_subsumption",
        "heading_recovery",
        "generic_epilepsy_companion",
        "state.drop_stale_older_zero",
        "state.drop_never_had_or_resemble",
        "state.retarget_seizure_free_span",
        "sf_dictionary_rewrite",
        "sf_dictionary_residual_add",
        "residual_add_current_regimens",
        "delete_planned_historical_general_noise",
        "current_guard_only",
        "residual_explicit_current_only",
        "full_noise_result_binding",
        "residual_investigation_providers",
    }
)


def test_catalogue_keeps_only_live_and_format_replay() -> None:
    pinned = records_for()
    assert pinned
    statuses = {row.status for row in pinned}
    assert statuses == {"live", "format-replay"}
    assert all(row.name for row in RULE_RECORDS)
    assert len(RULE_BY_NAME) == len(RULE_RECORDS)
    assert _RETIRED_RULE_NAMES.isdisjoint(RULE_BY_NAME)


def test_project_cuis_is_encode_at_llm_encode() -> None:
    row = RULE_BY_NAME["project_cuis"]
    assert row.runs_at == "llm_encode"
    assert row.authority == "encode"
    assert row.task == "exectv2"


def test_selected_evidence_renderer_is_llm_encode() -> None:
    row = RULE_BY_NAME["selected_evidence_renderer"]
    assert row.runs_at == "llm_encode"
    assert row.authority == "encode"
    assert row.task == "gan2026"


def test_diagnosis_concept_remap_is_llm_select_rewrite() -> None:
    row = RULE_BY_NAME["diagnosis_concept_remap_from_evidence"]
    assert row.runs_at == "llm_select"
    assert row.authority == "rewrite"


def test_no_live_encode_rule_is_stored_as_select() -> None:
    """CUI leak guard: live encode authority must not be filed under select."""

    for row in RULE_RECORDS:
        if row.status == "live" and row.authority == "encode":
            assert row.runs_at != "llm_select", row.name
        if row.name == "project_cuis":
            assert row.runs_at == "llm_encode"
            assert row.authority == "encode"


def test_gan_resolve_and_normalize_run_at_encode() -> None:
    for name in ("_normalize_event", "_resolve_final_label"):
        row = RULE_BY_NAME[name]
        assert row.runs_at == "llm_encode"
        assert row.authority == "encode"


def test_select_kinds_are_shared_across_tasks() -> None:
    assert SELECT_KINDS == ("gate", "drop", "rewrite", "reselect", "invent")
    assert set(SELECT_HIERARCHY) == set(SELECT_KINDS)
    gan_select = {
        row.authority for row in records_for(task="gan2026") if row.runs_at == "llm_select"
    }
    exect_select = {
        row.authority for row in records_for(task="exectv2") if row.runs_at == "llm_select"
    }
    clinical_other = {"parse", "encode", "dialect"}
    assert gan_select - clinical_other <= set(SELECT_KINDS)
    assert exect_select - clinical_other <= set(SELECT_KINDS)
