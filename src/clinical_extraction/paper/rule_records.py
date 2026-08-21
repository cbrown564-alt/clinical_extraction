"""Frozen catalogue records for named schema / encode / revise rules.

Pipeline code does not read this registry at runtime. It pins the
2026-08-21 encode/revise frame against the named-rule catalogue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TaskName = Literal["gan2026", "exectv2"]
RunsAt = Literal["llm_schema", "llm_encode", "llm_revise"]
Authority = Literal[
    "parse",
    "dialect",
    "encode",
    "gate",
    "rewrite",
    "reselect",
    "invent",
]
RuleStatus = Literal["live", "format-replay", "default_off", "off", "deleted"]


@dataclass(frozen=True)
class RuleRecord:
    """One catalogue-named rule, frozen for paper inventory tests."""

    name: str
    task: TaskName
    runs_at: RunsAt
    authority: Authority
    status: RuleStatus
    notes: str = ""
    # When a rule honestly has two authorities, list the secondary here.
    authority_alt: Authority | None = None


# Source: docs/research/paper/rule_catalogue_schema_format_post_2026-08-21.md
RULE_RECORDS: tuple[RuleRecord, ...] = (
    # --- Gan schema ---
    RuleRecord("json_dialect_repair", "gan2026", "llm_schema", "parse", "live"),
    RuleRecord(
        "repair_selected_answer_payload",
        "gan2026",
        "llm_schema",
        "parse",
        "live",
        notes="structural + quarantine",
    ),
    RuleRecord(
        "schema_validation_StructuredExtractionRecord",
        "gan2026",
        "llm_schema",
        "parse",
        "live",
    ),
    RuleRecord(
        "_normalize_event",
        "gan2026",
        "llm_schema",
        "encode",
        "live",
        notes="render leak: attaches Gan-normalized label/kind/rate",
    ),
    RuleRecord(
        "_resolve_final_label",
        "gan2026",
        "llm_schema",
        "encode",
        "live",
        notes="render leak: selected event ids → submitted string",
    ),
    # --- Gan encode ---
    RuleRecord(
        "selected_evidence_renderer",
        "gan2026",
        "llm_encode",
        "encode",
        "live",
        notes="does not change selected_event_ids",
    ),
    RuleRecord(
        "words_to_numbers",
        "gan2026",
        "llm_encode",
        "dialect",
        "live",
        notes="inside renderer; includes once_twice_thrice",
    ),
    RuleRecord("format_prediction_rate", "gan2026", "llm_encode", "encode", "live"),
    RuleRecord(
        "early_late_prewindow_rate_derivation",
        "gan2026",
        "llm_encode",
        "encode",
        "live",
        notes="inside renderer",
    ),
    RuleRecord(
        "daily_label_from_selected_evidence",
        "gan2026",
        "llm_encode",
        "encode",
        "live",
    ),
    RuleRecord("no_reference_daily", "gan2026", "llm_encode", "encode", "live"),
    RuleRecord(
        "cluster_derivation",
        "gan2026",
        "llm_encode",
        "encode",
        "live",
        notes="inside renderer",
    ),
    RuleRecord(
        "window_count",
        "gan2026",
        "llm_encode",
        "encode",
        "live",
        notes="single / range / sum; inside renderer",
    ),
    RuleRecord(
        "diary_dialect_in_renderer",
        "gan2026",
        "llm_encode",
        "encode",
        "live",
        notes="monthly_diary_label_from_text and calendar helpers",
    ),
    RuleRecord(
        "blocks_inexact_span_family_rewrite",
        "gan2026",
        "llm_encode",
        "gate",
        "live",
        notes="inside renderer",
    ),
    RuleRecord(
        "basic_label_repair",
        "gan2026",
        "llm_encode",
        "encode",
        "live",
        notes="live only when selected-evidence is off",
    ),
    RuleRecord(
        "basic_label_repair_format_only",
        "gan2026",
        "llm_encode",
        "encode",
        "off",
        notes="mode strict_format",
    ),
    RuleRecord(
        "clean_scorer_facing_gold_policy",
        "gan2026",
        "llm_encode",
        "encode",
        "off",
        notes="mode clean_scorer_facing",
    ),
    # --- Gan revise ---
    RuleRecord("usual_interval", "gan2026", "llm_revise", "reselect", "live"),
    RuleRecord("typical_over_ytd", "gan2026", "llm_revise", "reselect", "live"),
    RuleRecord("breakthrough", "gan2026", "llm_revise", "reselect", "live"),
    RuleRecord("non_epileptic", "gan2026", "llm_revise", "rewrite", "live"),
    RuleRecord("residual_jerk", "gan2026", "llm_revise", "reselect", "live"),
    RuleRecord("post_change_burst", "gan2026", "llm_revise", "reselect", "live"),
    RuleRecord("dated_sequence", "gan2026", "llm_revise", "reselect", "live"),
    RuleRecord("elapsed_anchor", "gan2026", "llm_revise", "reselect", "live"),
    RuleRecord(
        "sustained_seizure_free_veto_on_elapsed_anchor",
        "gan2026",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "monthly_diary",
        "gan2026",
        "llm_revise",
        "reselect",
        "live",
        notes="post family",
    ),
    RuleRecord("diary_preserve_label_guard", "gan2026", "llm_revise", "gate", "live"),
    RuleRecord("month_x_typical_preserve", "gan2026", "llm_revise", "gate", "default_off"),
    RuleRecord("diary_sum_all_months", "gan2026", "llm_revise", "rewrite", "live"),
    RuleRecord("vague_seizure_free_diary", "gan2026", "llm_revise", "rewrite", "live"),
    RuleRecord("date_list_span", "gan2026", "llm_revise", "rewrite", "live"),
    # --- ExECT shared ---
    RuleRecord(
        "parse_compact_events_flatten",
        "exectv2",
        "llm_schema",
        "parse",
        "live",
        notes="mentions_from_events; attribute name aliases",
    ),
    RuleRecord(
        "format_only_json_retry",
        "exectv2",
        "llm_schema",
        "parse",
        "live",
        notes="eligible local calls; not in cells 2–4 replay",
    ),
    RuleRecord("drop_out_of_scope_entity", "exectv2", "llm_schema", "gate", "live"),
    RuleRecord(
        "evidence_copy_from_mention_text",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
        notes="also format-replay",
    ),
    RuleRecord(
        "exact_substring_evidence_whitespace_repair",
        "exectv2",
        "llm_encode",
        "dialect",
        "live",
        notes="also format-replay",
    ),
    RuleRecord(
        "strip_model_cui_cuiphrase",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
        notes="also format-replay",
    ),
    RuleRecord(
        "repair_attributes",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
        notes="closed-vocab / legal-key strip; also format-replay",
    ),
    RuleRecord(
        "project_cuis",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
        notes="encode at llm_encode / format-replay stop; also format-replay",
    ),
    RuleRecord(
        "evidence_reject",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
        notes="not on format-replay",
    ),
    RuleRecord("sf_no_state_render_drop", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord(
        "investigations_modality_only_duplicate_drop",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    # --- ExECT Diagnosis ---
    RuleRecord(
        "diagnosis_surface_spelling_alias",
        "exectv2",
        "llm_revise",
        "dialect",
        "live",
        notes="dialect when spelling-only; rewrite when concept remap",
        authority_alt="rewrite",
    ),
    RuleRecord(
        "diagnosis_convention_attribute_repairs",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
        notes="format when text already rewritten",
    ),
    RuleRecord(
        "diagnosis_concept_remap_from_evidence",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
        notes="epilepsy+intractable; FCD→syndrome; focal onset→focal epilepsy",
    ),
    RuleRecord("diagnosis_convention_noise_drop", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord("jme_covers_phenotype_drop", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord("bounded_residual_add", "exectv2", "llm_revise", "invent", "live"),
    RuleRecord("residual_redundancy_skip", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord(
        "absence_preservation_residual_subsumption",
        "exectv2",
        "llm_revise",
        "gate",
        "off",
        notes="default variant default",
    ),
    RuleRecord("heading_recovery", "exectv2", "llm_revise", "invent", "off"),
    RuleRecord(
        "generic_epilepsy_companion",
        "exectv2",
        "llm_revise",
        "invent",
        "off",
        notes="hard False",
    ),
    # --- ExECT SeizureFrequency encode ---
    RuleRecord("encoding.word_number", "exectv2", "llm_encode", "encode", "format-replay"),
    RuleRecord("encoding.range_split", "exectv2", "llm_encode", "encode", "format-replay"),
    RuleRecord(
        "encoding.interval_completer",
        "exectv2",
        "llm_encode",
        "encode",
        "format-replay",
    ),
    RuleRecord(
        "encoding.last_event_zero",
        "exectv2",
        "llm_encode",
        "encode",
        "format-replay",
    ),
    RuleRecord(
        "encoding.last_clinic_frame",
        "exectv2",
        "llm_encode",
        "encode",
        "format-replay",
    ),
    RuleRecord(
        "encoding.dated_heading_count",
        "exectv2",
        "llm_encode",
        "encode",
        "format-replay",
    ),
    RuleRecord(
        "encoding.mention_text_cleanup",
        "exectv2",
        "llm_encode",
        "encode",
        "format-replay",
    ),
    RuleRecord(
        "sf_count_unit_month_normalize",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
    ),
    RuleRecord("cuiphrase_preserve_bundle", "exectv2", "llm_encode", "encode", "live"),
    RuleRecord("exact_mention_dedupe", "exectv2", "llm_encode", "encode", "live"),
    # --- ExECT SF revise ---
    RuleRecord("state.drop_unlabelled_active_rate", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord("state.drop_historical_active_rate", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord(
        "state.drop_preceded_by_current_seizure_free",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "state.drop_historical_or_advice_seizure_free",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "state.last_event_date_to_seizure_free",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
    ),
    RuleRecord(
        "state.last_event_active_to_seizure_free",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
    ),
    RuleRecord("state.temporal_direction", "exectv2", "llm_revise", "rewrite", "live"),
    RuleRecord(
        "ownership.generic_active_to_named",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
    ),
    RuleRecord(
        "ownership.generic_surface_to_named",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
    ),
    RuleRecord("ownership.drop_umbrella_clone", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord(
        "ownership.drop_bare_count_active_rate",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "ownership.drop_lifetime_oneoff_active_rate",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "ownership.drop_dated_cluster_next_to_free",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "ownership.retarget_last_week_named_to_generic",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
    ),
    RuleRecord(
        "ownership.drop_drugchange_before_if_other_active_rate",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord("ownership.drop_scope_residue", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord(
        "unknown_suppression.drug_response_scope",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "unknown_suppression.contextual_or_historical_change",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
    ),
    RuleRecord(
        "candidate_span_residual_add",
        "exectv2",
        "llm_revise",
        "invent",
        "live",
        notes="live if spans exist",
    ),
    RuleRecord(
        "state.drop_stale_older_zero",
        "exectv2",
        "llm_revise",
        "gate",
        "default_off",
        notes="residuals_v020",
    ),
    RuleRecord(
        "state.drop_never_had_or_resemble",
        "exectv2",
        "llm_revise",
        "gate",
        "default_off",
        notes="residuals_v020",
    ),
    RuleRecord(
        "state.retarget_seizure_free_span",
        "exectv2",
        "llm_revise",
        "rewrite",
        "default_off",
        notes="residuals_v020",
    ),
    RuleRecord("sf_dictionary_rewrite", "exectv2", "llm_revise", "rewrite", "off"),
    RuleRecord("sf_dictionary_residual_add", "exectv2", "llm_revise", "invent", "off"),
    # --- ExECT Prescription ---
    RuleRecord(
        "brand_to_generic",
        "exectv2",
        "llm_encode",
        "dialect",
        "format-replay",
        notes="resolve_drug_surface then normalize_drug_name",
    ),
    RuleRecord("dose_unit_respell", "exectv2", "llm_encode", "dialect", "live"),
    RuleRecord("drug_dose_value_normalize", "exectv2", "llm_encode", "dialect", "live"),
    RuleRecord("fill_frequency_if_missing", "exectv2", "llm_encode", "encode", "live"),
    RuleRecord(
        "prefer_current_dose_over_range",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
    ),
    RuleRecord("split_fused_am_pm_drug_dose", "exectv2", "llm_revise", "rewrite", "live"),
    RuleRecord(
        "split_slash_delimited_daily_doses",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
    ),
    RuleRecord(
        "split_explicit_uneven_once_daily",
        "exectv2",
        "llm_revise",
        "rewrite",
        "live",
    ),
    RuleRecord(
        "drop_non_asm",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
        notes="live leftover",
    ),
    RuleRecord(
        "drop_planned_start_titration_only",
        "exectv2",
        "llm_revise",
        "gate",
        "live",
        notes="live leftover",
    ),
    RuleRecord(
        "residual_add_current_regimens",
        "exectv2",
        "llm_revise",
        "invent",
        "off",
    ),
    RuleRecord(
        "delete_planned_historical_general_noise",
        "exectv2",
        "llm_revise",
        "gate",
        "off",
    ),
    RuleRecord("current_guard_only", "exectv2", "llm_revise", "gate", "deleted"),
    RuleRecord(
        "residual_explicit_current_only",
        "exectv2",
        "llm_revise",
        "gate",
        "deleted",
    ),
    # --- ExECT Investigations ---
    RuleRecord(
        "strip_cross_modality_performed_no",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
        notes="also format-replay",
    ),
    RuleRecord(
        "infer_performed_yes_when_result_present",
        "exectv2",
        "llm_encode",
        "encode",
        "live",
        notes="also format-replay",
    ),
    RuleRecord("pending_cue_drop", "exectv2", "llm_revise", "gate", "live"),
    RuleRecord("full_noise_result_binding", "exectv2", "llm_revise", "gate", "off"),
    RuleRecord(
        "residual_investigation_providers",
        "exectv2",
        "llm_revise",
        "invent",
        "off",
        notes="off in assembly; prompt-side only",
    ),
)

RULE_BY_NAME: dict[str, RuleRecord] = {record.name: record for record in RULE_RECORDS}


def records_for(
    *,
    task: TaskName | None = None,
    status: RuleStatus | None = None,
    runs_at: RunsAt | None = None,
) -> tuple[RuleRecord, ...]:
    """Return frozen records filtered by optional fields."""

    rows = RULE_RECORDS
    if task is not None:
        rows = tuple(row for row in rows if row.task == task)
    if status is not None:
        rows = tuple(row for row in rows if row.status == status)
    if runs_at is not None:
        rows = tuple(row for row in rows if row.runs_at == runs_at)
    return rows
