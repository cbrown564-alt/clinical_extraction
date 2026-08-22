"""Frozen catalogue records pin the encode/revise frame."""

from __future__ import annotations

from clinical_extraction.paper.rule_records import (
    RULE_BY_NAME,
    RULE_RECORDS,
    SELECT_HIERARCHY,
    SELECT_KINDS,
    Portability,
    records_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    _RULE_PORTABILITY_BY_ID,
    ACCEPTED_SELECT_RULE_IDS,
    EMITTED_ACTIONS_BY_RULE_ID,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    DEFAULT_SEMANTIC_FAMILY_ORDER,
)

DEFAULT_FORMAT_RULES = key_entities_structured.format_stack.DEFAULT_FORMAT_RULES

_PORTABILITY_VALUES = frozenset(
    {
        "general",
        "clinical_epilepsy",
        "seizure_frequency",
        "benchmark_format",
        "gan2026_specific",
        "exectv2_specific",
    }
)

# Default-off Gan families present in order tuple but absent from the catalogue.
_GAN_SEMANTIC_FAMILY_JOIN_EXCLUSIONS = frozenset({"residual_jerk", "elapsed_anchor"})

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
        "residual_jerk",
        "elapsed_anchor",
        "sustained_seizure_free_veto_on_elapsed_anchor",
        "bounded_residual_add",
        "residual_redundancy_skip",
    }
)


def test_catalogue_keeps_only_live_and_format_replay() -> None:
    pinned = records_for()
    assert pinned
    statuses = {row.status for row in pinned}
    assert statuses == {"live", "format-replay"}
    assert all(row.name for row in RULE_RECORDS)
    assert all(row.portability in _PORTABILITY_VALUES for row in RULE_RECORDS)
    assert len(RULE_BY_NAME) == len(RULE_RECORDS)
    assert _RETIRED_RULE_NAMES.isdisjoint(RULE_BY_NAME)


def test_runtime_rule_ids_join_catalogue_by_task() -> None:
    """Default-enabled runtime registries resolve in RULE_BY_NAME with expected task.

    Exclusions:
    - Gan ``DEFAULT_SEMANTIC_FAMILY_ORDER`` lists ``residual_jerk`` and
      ``elapsed_anchor`` for ablation, but both default off and are intentionally
      absent from the frozen catalogue.
    - ExECT select join uses ``ACCEPTED_SELECT_RULE_IDS`` only; rejected candidate
      ``selection.sf_recent_event_over_historical_free`` stays out of scope.
    - Gan post-stack fix ids (``diary_preserve_label_guard``, etc.) are not in
      the semantic-family order tuple and are not part of this join.
    """

    gan_family_ids = {
        family_id
        for family_id in DEFAULT_SEMANTIC_FAMILY_ORDER
        if family_id not in _GAN_SEMANTIC_FAMILY_JOIN_EXCLUSIONS
    }
    runtime_by_task: dict[str, frozenset[str]] = {
        "gan2026": gan_family_ids,
        "exectv2": frozenset(ACCEPTED_SELECT_RULE_IDS) | DEFAULT_FORMAT_RULES,
    }
    for task, rule_ids in runtime_by_task.items():
        for rule_id in rule_ids:
            record = RULE_BY_NAME[rule_id]
            assert record.task == task, rule_id


def test_accepted_select_portability_matches_catalogue() -> None:
    for rule_id in ACCEPTED_SELECT_RULE_IDS:
        assert RULE_BY_NAME[rule_id].portability == _RULE_PORTABILITY_BY_ID[rule_id]


# Mechanical action kinds a Select authority may emit. ``reselect`` changes
# which extracted fact is current, so it may restore (add), remove (drop), or
# replace (rewrite) a row; the other authorities map one-to-one.
_COMPATIBLE_ACTIONS_BY_AUTHORITY = {
    "rewrite": frozenset({"rewrite"}),
    "reselect": frozenset({"add", "drop", "rewrite"}),
    "drop": frozenset({"drop"}),
    "invent": frozenset({"add"}),
    "gate": frozenset({"drop"}),
}


def test_declared_select_actions_match_catalogue_authority() -> None:
    """Each accepted Select rule's declared action kinds fit its authority."""

    for rule_id in ACCEPTED_SELECT_RULE_IDS:
        record = RULE_BY_NAME[rule_id]
        allowed = _COMPATIBLE_ACTIONS_BY_AUTHORITY[record.authority]
        if record.authority_alt is not None:
            allowed = allowed | _COMPATIBLE_ACTIONS_BY_AUTHORITY[record.authority_alt]
        declared = EMITTED_ACTIONS_BY_RULE_ID[rule_id]
        assert declared <= allowed, (
            f"{rule_id}: declared {sorted(declared)} exceeds "
            f"authority {record.authority!r} ({sorted(allowed)})"
        )


def test_rule_record_exposes_portability_literal() -> None:
    row = RULE_BY_NAME["json_dialect_repair"]
    assert row.portability == "general"
    _: Portability = row.portability


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
