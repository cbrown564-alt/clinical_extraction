"""Frozen catalogue records pin the encode/revise frame."""

from __future__ import annotations

from clinical_extraction.paper.rule_records import RULE_BY_NAME, RULE_RECORDS, records_for


def test_catalogue_named_live_format_replay_default_off_have_records() -> None:
    pinned = records_for()
    assert pinned
    statuses = {row.status for row in pinned}
    assert {"live", "format-replay", "default_off"} <= statuses
    assert all(row.name for row in RULE_RECORDS)
    assert len(RULE_BY_NAME) == len(RULE_RECORDS)


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


def test_diagnosis_concept_remap_is_llm_revise_rewrite() -> None:
    row = RULE_BY_NAME["diagnosis_concept_remap_from_evidence"]
    assert row.runs_at == "llm_revise"
    assert row.authority == "rewrite"


def test_no_live_encode_rule_is_stored_as_revise() -> None:
    """CUI leak guard: live encode authority must not be filed under revise.

    Schema render leaks may still be authority=encode at llm_schema.
    """

    for row in RULE_RECORDS:
        if row.status == "live" and row.authority == "encode":
            assert row.runs_at != "llm_revise", row.name
        if row.name == "project_cuis":
            assert row.runs_at == "llm_encode"
            assert row.authority == "encode"


def test_gan_schema_render_leaks_stay_llm_schema_encode() -> None:
    for name in ("_normalize_event", "_resolve_final_label"):
        row = RULE_BY_NAME[name]
        assert row.runs_at == "llm_schema"
        assert row.authority == "encode"
