"""Frozen catalogue records for named extract / encode / select rules.

Pipeline code does not read this registry at runtime. It pins the
extract / encode / select frame against the named-rule catalogue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TaskName = Literal["gan2026", "exectv2"]
RunsAt = Literal["llm_extract", "llm_encode", "llm_select"]
Authority = Literal[
    "parse",
    "dialect",
    "encode",
    "gate",
    "drop",
    "rewrite",
    "reselect",
    "invent",
]

SELECT_KINDS: tuple[Authority, ...] = (
    "gate",
    "drop",
    "rewrite",
    "reselect",
    "invent",
)
SELECT_HIERARCHY: dict[str, str] = {
    "gate": "Withhold a finding, or block a proposed change.",
    "drop": "Remove a submitted fact that was already extracted.",
    "rewrite": "Change the submitted meaning of a kept fact.",
    "reselect": "Change which extracted fact is current.",
    "invent": "Add a residual fact that was not submitted as its own extract item.",
}
RuleStatus = Literal["live", "format-replay"]
Portability = Literal[
    "general",
    "clinical_epilepsy",
    "seizure_frequency",
    "benchmark_format",
    "gan2026_specific",
    "exectv2_specific",
]


@dataclass(frozen=True)
class RuleRecord:
    """One catalogue-named rule, frozen for paper inventory tests."""

    name: str
    task: TaskName
    runs_at: RunsAt
    authority: Authority
    status: RuleStatus
    portability: Portability
    notes: str = ""
    # When a rule honestly has two authorities, list the secondary here.
    authority_alt: Authority | None = None


# Source: docs/research/paper/rule_catalogue_schema_format_post_2026-08-21.md
RULE_RECORDS: tuple[RuleRecord, ...] = (
    # --- Gan extract ---
    RuleRecord(
        'json_dialect_repair',
        'gan2026',
        'llm_extract',
        'parse',
        'live',
        'general',
    ),
    RuleRecord(
        'repair_selected_answer_payload',
        'gan2026',
        'llm_extract',
        'parse',
        'live',
        'general',
        notes="structural + quarantine",
    ),
    RuleRecord(
        'schema_validation_StructuredExtractionRecord',
        'gan2026',
        'llm_extract',
        'parse',
        'live',
        'general',
    ),
    # --- Gan encode ---
    RuleRecord(
        '_normalize_event',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'gan2026_specific',
        notes="attaches Gan-normalized label/kind/rate; encode owns this",
    ),
    RuleRecord(
        '_resolve_final_label',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'gan2026_specific',
        notes="fills a blank model label from selected events; encode owns this",
    ),
    RuleRecord(
        'selected_evidence_renderer',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'gan2026_specific',
        notes="does not change selected_event_ids",
    ),
    RuleRecord(
        'words_to_numbers',
        'gan2026',
        'llm_encode',
        'dialect',
        'live',
        'general',
        notes="inside renderer; includes once_twice_thrice",
    ),
    RuleRecord(
        'format_prediction_rate',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
    ),
    RuleRecord(
        'early_late_prewindow_rate_derivation',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'seizure_frequency',
        notes="inside renderer",
    ),
    RuleRecord(
        'daily_label_from_selected_evidence',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'no_reference_daily',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'cluster_derivation',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'seizure_frequency',
        notes="inside renderer",
    ),
    RuleRecord(
        'window_count',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'seizure_frequency',
        notes="single / range / sum; inside renderer",
    ),
    RuleRecord(
        'diary_dialect_in_renderer',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'seizure_frequency',
        notes="monthly_diary_label_from_text and calendar helpers",
    ),
    RuleRecord(
        'blocks_inexact_span_family_rewrite',
        'gan2026',
        'llm_encode',
        'gate',
        'live',
        'gan2026_specific',
        notes="inside renderer",
    ),
    RuleRecord(
        'basic_label_repair',
        'gan2026',
        'llm_encode',
        'encode',
        'live',
        'gan2026_specific',
        notes="live only when selected-evidence is off",
    ),
    # --- Gan select ---
    RuleRecord(
        'usual_interval',
        'gan2026',
        'llm_select',
        'reselect',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'typical_over_ytd',
        'gan2026',
        'llm_select',
        'reselect',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'breakthrough',
        'gan2026',
        'llm_select',
        'reselect',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'non_epileptic',
        'gan2026',
        'llm_select',
        'rewrite',
        'live',
        'clinical_epilepsy',
    ),
    RuleRecord(
        'post_change_burst',
        'gan2026',
        'llm_select',
        'reselect',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'dated_sequence',
        'gan2026',
        'llm_select',
        'reselect',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'monthly_diary',
        'gan2026',
        'llm_select',
        'reselect',
        'live',
        'seizure_frequency',
        notes="post family",
    ),
    RuleRecord(
        'diary_preserve_label_guard',
        'gan2026',
        'llm_select',
        'gate',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'diary_sum_all_months',
        'gan2026',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'vague_seizure_free_diary',
        'gan2026',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'date_list_span',
        'gan2026',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    # --- ExECT shared ---
    RuleRecord(
        'parse_compact_events_flatten',
        'exectv2',
        'llm_extract',
        'parse',
        'live',
        'general',
        notes="mentions_from_events; attribute name aliases",
    ),
    RuleRecord(
        'format_only_json_retry',
        'exectv2',
        'llm_extract',
        'parse',
        'live',
        'general',
        notes="eligible local calls; not in cells 2–4 replay",
    ),
    RuleRecord(
        'drop_out_of_scope_entity',
        'exectv2',
        'llm_extract',
        'drop',
        'live',
        'exectv2_specific',
    ),
    RuleRecord(
        'evidence_copy_from_mention_text',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
        notes="also format-replay",
    ),
    RuleRecord(
        'exact_substring_evidence_whitespace_repair',
        'exectv2',
        'llm_encode',
        'dialect',
        'live',
        'general',
        notes="also format-replay",
    ),
    RuleRecord(
        'strip_model_cui_cuiphrase',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
        notes="also format-replay",
    ),
    RuleRecord(
        'repair_attributes',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'general',
        notes="closed-vocab / legal-key strip; also format-replay",
    ),
    RuleRecord(
        'project_cuis',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
        notes="encode at llm_encode / format-replay stop; also format-replay",
    ),
    RuleRecord(
        'evidence_reject',
        'exectv2',
        'llm_select',
        'gate',
        'live',
        'general',
        notes="not on format-replay",
    ),
    RuleRecord(
        'sf_no_state_render_drop',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'investigations_modality_only_duplicate_drop',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'exectv2_specific',
    ),
    # --- ExECT Diagnosis ---
    RuleRecord(
        'encoding.diagnosis_standard_name',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'benchmark_format',
        notes=(
            "same extracted diagnosis; closed name and spelling only; no qualifier "
            "overwrite"
        ),
    ),
    RuleRecord(
        'diagnosis_surface_spelling_alias',
        'exectv2',
        'llm_select',
        'dialect',
        'live',
        'clinical_epilepsy',
        notes="dialect when spelling-only; rewrite when concept remap",
        authority_alt='rewrite',
    ),
    RuleRecord(
        'diagnosis_convention_attribute_repairs',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
        notes="format when text already rewritten",
    ),
    RuleRecord(
        'diagnosis_concept_remap_from_evidence',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'clinical_epilepsy',
        notes="epilepsy+intractable; FCD→syndrome; focal onset→focal epilepsy",
    ),
    RuleRecord(
        'selection.diagnosis_specificity_hierarchy',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'clinical_epilepsy',
        notes=(
            "probable lobe modifier or possible laterality may overwrite a less "
            "specific same-branch epilepsy mention; seizure-type generalised and "
            "namely-clauses do not classify epilepsy"
        ),
    ),
    RuleRecord(
        'selection.diagnosis_source_local_specificity',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'clinical_epilepsy',
        notes=(
            "restore the encoded source diagnosis when a later rewrite is broader, an "
            "etiology sibling of a named lobe, or an unauthorized laterality child"
        ),
    ),
    RuleRecord(
        'selection.diagnosis_explicit_heading_phenotype',
        'exectv2',
        'llm_select',
        'reselect',
        'live',
        'benchmark_format',
        notes=(
            "retain a heading-listed phenotype unless a selected named syndrome "
            "already owns that phenotype"
        ),
    ),
    RuleRecord(
        'diagnosis_convention_noise_drop',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'clinical_epilepsy',
    ),
    RuleRecord(
        'jme_covers_phenotype_drop',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'clinical_epilepsy',
    ),
    # --- ExECT SeizureFrequency encode ---
    RuleRecord(
        'encoding.word_number',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'general',
    ),
    RuleRecord(
        'encoding.range_split',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'general',
    ),
    RuleRecord(
        'encoding.interval_completer',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'seizure_frequency',
    ),
    RuleRecord(
        'encoding.last_event_zero',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'seizure_frequency',
    ),
    RuleRecord(
        'encoding.last_clinic_frame',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'seizure_frequency',
    ),
    RuleRecord(
        'encoding.dated_heading_count',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'seizure_frequency',
    ),
    RuleRecord(
        'encoding.mention_text_cleanup',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'general',
    ),
    RuleRecord(
        'encoding.sf_local_evidence',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'seizure_frequency',
        notes=(
            "explicit seizure-free closed name only; no type retarget or invented "
            "bound"
        ),
    ),
    RuleRecord(
        'selection.sf_named_type_from_evidence',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
        notes=(
            "generic seizure/episode or parent absence may take one unambiguous named "
            "type from local evidence"
        ),
    ),
    RuleRecord(
        'selection.sf_explicit_recurrence_lower_bound',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
        notes=(
            "explicit further-seizures wording writes LowerNumberOfSeizures=1 when no "
            "count is present"
        ),
    ),
    RuleRecord(
        'selection.sf_named_type_identity',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
        notes=(
            "reconcile shared-evidence groups so one named SF row cannot be "
            "reassigned to a sibling type"
        ),
    ),
    RuleRecord(
        'selection.sf_to_diagnosis_explicit_type',
        'exectv2',
        'llm_select',
        'invent',
        'live',
        'benchmark_format',
        notes=(
            "ledger-only cross-family projection of an already selected named SF fact "
            "into Diagnosis; no unused-note scan"
        ),
    ),
    RuleRecord(
        'encoding.sf_standard_name',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'benchmark_format',
        notes="same seizure type; write the closed-head standard name",
    ),
    RuleRecord(
        'sf_count_unit_month_normalize',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'general',
    ),
    RuleRecord(
        'cuiphrase_preserve_bundle',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
    ),
    RuleRecord(
        'exact_mention_dedupe',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
    ),
    # --- ExECT SF revise ---
    RuleRecord(
        'state.drop_unlabelled_active_rate',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'state.drop_historical_active_rate',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'state.drop_preceded_by_current_seizure_free',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'state.drop_historical_or_advice_seizure_free',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'state.last_event_date_to_seizure_free',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'state.last_event_active_to_seizure_free',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'state.temporal_direction',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.generic_active_to_named',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.generic_surface_to_named',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.drop_umbrella_clone',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.drop_bare_count_active_rate',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.drop_lifetime_oneoff_active_rate',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.drop_dated_cluster_next_to_free',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.retarget_last_week_named_to_generic',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.drop_drugchange_before_if_other_active_rate',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'ownership.drop_scope_residue',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'unknown_suppression.drug_response_scope',
        'exectv2',
        'llm_select',
        'gate',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'unknown_suppression.contextual_or_historical_change',
        'exectv2',
        'llm_select',
        'gate',
        'live',
        'seizure_frequency',
    ),
    RuleRecord(
        'candidate_span_residual_add',
        'exectv2',
        'llm_select',
        'invent',
        'live',
        'seizure_frequency',
        notes="live if spans exist",
    ),
    # --- ExECT Prescription ---
    RuleRecord(
        'encoding.prescription_local_slots',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'clinical_epilepsy',
        notes="local cadence and single explicit dose beat malformed/shared fields",
    ),
    RuleRecord(
        'encoding.prescription_standard_name',
        'exectv2',
        'llm_encode',
        'dialect',
        'format-replay',
        'benchmark_format',
        notes=(
            "write ordinary mention text as generic DrugName; preserve contextual "
            "cues"
        ),
    ),
    RuleRecord(
        'encoding.prescription_formulation_name',
        'exectv2',
        'llm_encode',
        'dialect',
        'format-replay',
        'general',
        notes="strip a dosage-form suffix when the base drug is known",
    ),
    RuleRecord(
        'brand_to_generic',
        'exectv2',
        'llm_encode',
        'dialect',
        'format-replay',
        'benchmark_format',
        notes="resolve_drug_surface then normalize_drug_name",
    ),
    RuleRecord(
        'dose_unit_respell',
        'exectv2',
        'llm_encode',
        'dialect',
        'live',
        'general',
    ),
    RuleRecord(
        'drug_dose_value_normalize',
        'exectv2',
        'llm_encode',
        'dialect',
        'live',
        'general',
    ),
    RuleRecord(
        'fill_frequency_if_missing',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'general',
    ),
    RuleRecord(
        'prefer_current_dose_over_range',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'general',
    ),
    RuleRecord(
        'split_fused_am_pm_drug_dose',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'general',
    ),
    RuleRecord(
        'split_slash_delimited_daily_doses',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'general',
    ),
    RuleRecord(
        'split_explicit_uneven_once_daily',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'general',
    ),
    RuleRecord(
        'drop_non_asm',
        'exectv2',
        'llm_select',
        'gate',
        'live',
        'clinical_epilepsy',
        notes="live leftover",
    ),
    RuleRecord(
        'drop_planned_start_titration_only',
        'exectv2',
        'llm_select',
        'gate',
        'live',
        'clinical_epilepsy',
        notes="live leftover",
    ),
    RuleRecord(
        'selection.prescription_local_regimen_scope',
        'exectv2',
        'llm_select',
        'rewrite',
        'live',
        'clinical_epilepsy',
        notes=(
            "keep a rescue cadence local to its named medicine instead of spreading "
            "it to sibling regimens"
        ),
    ),
    RuleRecord(
        'selection.prescription_active_titration',
        'exectv2',
        'llm_select',
        'reselect',
        'live',
        'clinical_epilepsy',
        notes=(
            "retain the explicit initial current regimen before a future titration; "
            "prescribe/start requests remain suppressed"
        ),
    ),
    RuleRecord(
        'selection.prescription_exact_regimen_dedupe',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'benchmark_format',
        notes=(
            "drop a historical-initiation duplicate only when a current assertion "
            "carries the same exact regimen"
        ),
    ),
    # --- ExECT Investigations ---
    RuleRecord(
        'strip_cross_modality_performed_no',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
        notes="also format-replay",
    ),
    RuleRecord(
        'infer_performed_yes_when_result_present',
        'exectv2',
        'llm_encode',
        'encode',
        'live',
        'benchmark_format',
        notes="also format-replay",
    ),
    RuleRecord(
        'encoding.investigation_local_result',
        'exectv2',
        'llm_encode',
        'encode',
        'format-replay',
        'benchmark_format',
        notes="unnegated abnormal cue in the selected modality's local clause",
    ),
    RuleRecord(
        'pending_cue_drop',
        'exectv2',
        'llm_select',
        'drop',
        'live',
        'exectv2_specific',
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
