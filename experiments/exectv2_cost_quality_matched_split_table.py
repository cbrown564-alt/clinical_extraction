"""Item 3 of
``docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md``:
matched-split, cross-architecture cost-quality table over the ExECTv2 registry.

Zero-LLM, read-only over ``experiments/registry.jsonl`` via
``clinical_extraction.core.registry.load_run_registry``. Does NOT run any model
calls, does NOT edit the registry, does NOT touch git.

## Family set

Every registered ``pipeline_family`` value that belongs to the ExECTv2
architecture-comparison surface: the 22 ``exectv2_*``-prefixed values plus
``gepa_from_scratch`` (GEPA-from-scratch runs are registered under this
task-agnostic family name, NOT an ``exectv2_*``-prefixed one -- a naive
substring filter over ``pipeline_family`` silently drops all 4 GEPA rows; see
the plan's "known pitfall" note). This script hard-codes the full 23-value set
rather than filtering by substring, so it cannot silently miss GEPA again.

## Split normalization

The registry does NOT use the literal strings "dev140" / "dev25" / "full200"
anywhere in the ``split`` field. Observed values across the 64 rows in this
family set are ``"dev"`` (with ``row_count`` 25 or 140) and three full-200
variants -- ``"full200_aggregate"``, ``"full200_audit"``,
``"full200_overall_audit"`` (older Phase 6/7 SF-only / all-entity-only audits
that predate the ``clinical_headline`` scoring convention, on a DIFFERENT
metric surface than the newer aggregate rows). This script normalizes
``split="dev", row_count=140`` -> ``"dev140"`` etc., and ANY ``full200_*``
value -> ``"full200"`` for the purpose of matched-split comparison, while
preserving the raw split string in the per-row table so that surface
difference is not hidden.

## LLM-call-count annotation

Not a registry field. Hand-assigned per ``pipeline_family`` (with per-run_id
overrides for the two families whose rows span more than one call-count
architecture: ``exectv2_hybrid`` and ``gepa_from_scratch``) from that family's
``model_role`` / ``claim_language_notes`` text, quoted inline in
``CALL_COUNT_ANNOTATIONS`` below so the assignment is auditable against the
registry text it was read from, not asserted from memory.

## Primary-metric selection

Rows in this family set are NOT metric-uniform: some use ``clinical_headline_f1``
(the de-dup clinical-recovery surface, decision 0027), some ``overall_f1``, some
bundle two models' metrics in one row under ``<model>_clinical_headline_f1``
prefixes, some predate that convention entirely and only carry
``sf_benchmark_per_item_f1`` / ``benchmark_per_item_f1`` / ``semantic_per_item_f1``.
Rather than hand-picking one "representative" number per row (64 hand-picks,
error-prone and unauditable), this script deterministically selects one key per
row via ``METRIC_PRIORITY`` (first match wins; ties broken by picking the
gpt-4.1-mini variant when a row bundles multiple models, since that is this
project's main closed model) and RECORDS which key it picked. Every ``*_f1``
key actually present is also emitted per row so nothing is hidden by the
auto-pick.

Usage:
    uv run python experiments/exectv2_cost_quality_matched_split_table.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import RunRegistryEntry, load_run_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "experiments" / "registry.jsonl"
OUT_JSON = ROOT / "experiments" / "exectv2_cost_quality_matched_split_table_20260701.json"

# The full 23-value family set (plan-enumerated 22 exectv2_*-prefixed values,
# confirmed exhaustive by a fresh registry scan for this script, plus
# gepa_from_scratch -- the known pitfall).
FAMILIES: tuple[str, ...] = (
    "exectv2_deterministic",
    "exectv2_deterministic_all9",
    "exectv2_diag_sf_verifier_residual_iteration",
    "exectv2_holistic_finding_assembly",
    "exectv2_hybrid",
    "exectv2_hybrid_benchmark_overall",
    "exectv2_hybrid_diagnosis_acceptance_gate",
    "exectv2_hybrid_diagnosis_decomposer",
    "exectv2_hybrid_diagnosis_reconciler",
    "exectv2_hybrid_sf_state_adjudicator",
    "exectv2_key_entities_clinical_error_ledger",
    "exectv2_key_entities_transfer_readout",
    "exectv2_llm_diagnosis_verifier",
    "exectv2_llm_investigations_verifier",
    "exectv2_llm_med_inv_verifier",
    "exectv2_llm_only_all_entities",
    "exectv2_llm_only_key_entities_structured",
    "exectv2_llm_only_per_entity",
    "exectv2_llm_only_single_pass",
    "exectv2_llm_sf_verifier",
    "exectv2_robustness_validation_audit",
    "exectv2_same_core_model_swap",
    "gepa_from_scratch",
)

METRIC_PRIORITY: tuple[str, ...] = (
    "clinical_headline_f1",
    "clinical_headline_overall_f1",
    "overall_f1",
    "gpt41mini_clinical_headline_f1",
    "deepseek_clinical_headline_f1",
    "v08_dev140_comparator_f1",
    "partial_hybrid_clinical_headline_f1",
    "benchmark_per_item_f1",
    "benchmark_cui_overall_f1",
    "sf_benchmark_per_item_f1",
    "semantic_per_item_f1",
    "phrase_only_per_item_f1",
)

# family -> (calls annotation, basis quote). Per-run_id overrides below for
# exectv2_hybrid and gepa_from_scratch, whose rows span more than one
# call-count architecture.
CALL_COUNT_ANNOTATIONS: dict[str, tuple[str, str]] = {
    "exectv2_deterministic": (
        "0 calls (rules only)",
        "model='(model-independent)'; mode='deterministic'.",
    ),
    "exectv2_deterministic_all9": (
        "0 calls (rules only)",
        "model='(model-independent)'; model_role: 'ExECTv2 deterministic all-9 baseline; "
        "active rules for Prescription, Investigations, Diagnosis, ...'.",
    ),
    "exectv2_diag_sf_verifier_residual_iteration": (
        "~3 calls/letter total (1 upstream v0.5 structured draft [produced by a separate "
        "run, not this one] + 1 Diagnosis verifier + 1 SF verifier; this row's own marginal "
        "calls = 2)",
        "model_role: 'Residual-led Diagnosis verifier v0.6 and SeizureFrequency verifier "
        "v0.4 over the v0.5 single structured key-entity draft. The model owns revised "
        "family mentions; deterministic code only gates schema/evidence...'.",
    ),
    "exectv2_holistic_finding_assembly": (
        "hybrid, multi-call (v08: 3 focused LLM lanes -- Diagnosis reconciler, SF union "
        "arbitration, Investigations verifier+arbitration -- plus 1 deterministic-only "
        "Prescription repair lane, assembled via deterministic lenses; not a fixed "
        "per-letter call count. The dev140 row in this family is a *study* bundling several "
        "architecture variants from 4-GPT/0-focused to 0-GPT/4-focused in one registry row.)",
        "model_role + docs/experiments/exectv2/key_entities/"
        "exectv2_holistic_finding_assembly_v08_dev140_20260621.md 'Finding Assembly' "
        "producer table (4 rows, 1 deterministic-only).",
    ),
    "exectv2_hybrid": (
        "1 LLM call/letter marginal to this stage (default: candidate-set + "
        "clinical-assessment -- deterministic candidate generation -> 1 LLM keep/route/"
        "attribute call -> deterministic normalize, SF-only scope). The "
        "'exectv2_arbitration_v02' row is also 1 marginal call/letter but consumes a "
        "9-call/letter upstream per-entity candidate pool built by a separate run.",
        "model_role per row (see per-run_id overrides for the arbitration variant).",
    ),
    "exectv2_hybrid_benchmark_overall": (
        "0 marginal calls (pure aggregation/merge of already-run key-family + "
        "deterministic-all9 outputs)",
        "mode='analysis_only'; replay_status='analysis_only'; model_role: 'Merged hybrid "
        "key-family + deterministic all-9, benchmark surface.'.",
    ),
    "exectv2_hybrid_diagnosis_acceptance_gate": (
        "1 call/letter (Diagnosis-only accept/reject gate over externally-produced "
        "verifier+decomposer candidates)",
        "model_role: 'The model only accepts or rejects candidate IDs; deterministic code "
        "renders accepted candidates.'.",
    ),
    "exectv2_hybrid_diagnosis_decomposer": (
        "1 call/letter (Diagnosis-only decomposer stage over the v0.5 draft)",
        "model_role: 'Diagnosis heading/narrative decomposer ... the model owns final "
        "Diagnosis mentions.'.",
    ),
    "exectv2_hybrid_diagnosis_reconciler": (
        "1 call/letter (Diagnosis-only reconciler stage over verifier+decomposer "
        "candidates)",
        "model_role: 'Diagnosis reconciler ... over Diagnosis verifier v0.6 and Diagnosis "
        "decomposer v0.1 candidates.'.",
    ),
    "exectv2_hybrid_sf_state_adjudicator": (
        "1 call/letter (SF-only candidate-span/state adjudicator stage)",
        "model_role: 'SeizureFrequency candidate-span state adjudicator ... the model owns "
        "keep/reject, state choice, text normalization, and final mentions.'.",
    ),
    "exectv2_key_entities_clinical_error_ledger": (
        "0 calls (analysis-only error ledger over existing dev140 artifacts)",
        "model='none'; mode='analysis-only'.",
    ),
    "exectv2_key_entities_transfer_readout": (
        "0 marginal calls (a readout combining pre-existing dev140 draft + verifier runs; "
        "despite mode='live' the row's own claim_language_notes describe it as a transfer "
        "*readout*, i.e. a re-presentation of other rows' numbers, not a fresh call)",
        "claim_language_notes: 'Transfer readout combining the single structured v0.5 "
        "dev140 draft with Diagnosis verifier v0.5 and SeizureFrequency verifier v0.3 "
        "dev140 runs.'.",
    ),
    "exectv2_llm_diagnosis_verifier": (
        "1 call/letter (Diagnosis-only verifier over the v0.5 draft)",
        "model_role: 'Diagnosis-focused verifier ... The model may keep, delete, edit, or "
        "add Diagnosis mentions.'.",
    ),
    "exectv2_llm_investigations_verifier": (
        "1 call/letter (Investigations-only verifier)",
        "model_role: 'Investigations-focused verifier ... The model owns revised "
        "Investigations mentions.'.",
    ),
    "exectv2_llm_med_inv_verifier": (
        "1 call/letter (combined Prescription+Investigations verifier)",
        "model_role: 'Prescription/Investigations verifier ... The model owns revised "
        "Prescription and Investigations mentions.'.",
    ),
    "exectv2_llm_only_all_entities": (
        "1 call/letter (single pass, all 9 entities)",
        "model_role: 'ExECTv2 LLM-only all-entity single-pass extractor (one call per "
        "letter, all nine entities).'.",
    ),
    "exectv2_llm_only_key_entities_structured": (
        "1 call/letter (single pass, 4 key families)",
        "model_role: 'LLM-only single-prompt structured clinical event extractor over "
        "medication, diagnosis, seizure frequency, and investigations.'.",
    ),
    "exectv2_llm_only_per_entity": (
        "1 call/letter as registered (SF-only or Diagnosis-only scoped runs); "
        "architecturally 'one focused call per entity type per letter', so a full 9-entity "
        "deployment implies up to 9 calls/letter",
        "model_role: 'ExECTv2 LLM-only per-entity extractor (one focused call per entity "
        "type per letter, SF only).' / Diagnosis-scoped variant for the dev25 row.",
    ),
    "exectv2_llm_only_single_pass": (
        "1 call/letter (single pass, SF scope in registered runs)",
        "model_role: 'ExECTv2 LLM-only single-pass extractor (one call per letter, all SF "
        "mentions + attributes + evidence).'.",
    ),
    "exectv2_llm_sf_verifier": (
        "1 call/letter (SF-only verifier)",
        "model_role: 'SeizureFrequency-focused verifier ... The model owns normalized "
        "SeizureFrequency event text.'.",
    ),
    "exectv2_robustness_validation_audit": (
        "0 calls (explicitly no live model calls)",
        "model_role: 'Aggregate robustness hard-slice analysis over the current-code "
        "v08-shaped full-200 artifact; no live model calls.'.",
    ),
    "exectv2_same_core_model_swap": (
        "2 calls/letter (the frozen 'exectv2_2call_no_sf_adjudicator' core: 1 structured "
        "key-family extraction call + 1 Diagnosis call; deterministic code owns SF "
        "projection/union and Prescription repair)",
        "run_id prefix 'exectv2_2call_no_sf_adjudicator_*' + model_role: 'ExECTv2 same-core "
        "structured key-family and Diagnosis extractor; deterministic code owns SF "
        "projection/union and Prescription repair.'.",
    ),
    "gepa_from_scratch": (
        "1 call/letter for 'dedup' (monolith) run_ids; 4 calls/letter for 'multifamily' "
        "run_ids (one evolved GEPA signature per family: Diagnosis/SF/Prescription/"
        "Investigations)",
        "run_id substring 'dedup' vs 'multifamily'; corroborated by the ExECTv2 GEPA "
        "workstream memory note '4 per-family instr' for the multifamily re-run.",
    ),
}

# Per-run_id overrides for the two heterogeneous families.
RUN_CALL_OVERRIDES: dict[str, tuple[str, str]] = {
    "exectv2_arbitration_v02_dev140_gpt41mini_20260618": (
        "1 call/letter marginal (arbitration over a union candidate pool)",
        "model_role: 'one arbitration call per letter over the union per-entity candidate "
        "pool'; that pool itself is built by 9 upstream per-entity calls from a separate "
        "run, not counted here.",
    ),
}
for _run_id, _override in {
    "exectv2_gepa_dedup_gpt41mini_h2mb8_20260628": (
        "1 call/letter (monolith single-prompt program)",
        "run_id contains 'dedup' not 'multifamily'; model_role: 'attribution-clean de-dup "
        "adapter' with a single evolved instruction set.",
    ),
    "exectv2_gepa_dedup_qwen3p6_35b_h2mb8_20260629": (
        "1 call/letter (monolith single-prompt program)",
        "run_id contains 'dedup' not 'multifamily'.",
    ),
    "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628": (
        "4 calls/letter (one evolved GEPA signature per family)",
        "run_id contains 'multifamily'; final_instruction_tokens=1736 vs the monolith's "
        "490 corroborates 4 separately-evolved instructions.",
    ),
    "exectv2_gepa_multifamily_dedup_qwen3p6_35b_h2mb8_20260629": (
        "4 calls/letter (one evolved GEPA signature per family)",
        "run_id contains 'multifamily'.",
    ),
}.items():
    RUN_CALL_OVERRIDES[_run_id] = _override


def normalize_split(split: str, row_count: int) -> str:
    """Map the registry's raw ``split`` + ``row_count`` to a comparable label."""

    if split == "dev":
        return f"dev{row_count}"
    if split.startswith("full200"):
        return "full200"
    return f"{split}{row_count}"


def f1_like_fields(primary_metrics: dict[str, Any]) -> dict[str, float]:
    """All ``*_f1``-suffixed numeric fields in a row's primary_metrics."""

    out: dict[str, float] = {}
    for key, value in primary_metrics.items():
        if key.endswith("_f1") and isinstance(value, int | float):
            out[key] = float(value)
    return out


def pick_primary_metric(f1_fields: dict[str, float]) -> tuple[str, float] | tuple[None, None]:
    """Deterministically select one representative metric key, priority-first."""

    for key in METRIC_PRIORITY:
        if key in f1_fields:
            return key, f1_fields[key]
    if f1_fields:
        key = sorted(f1_fields)[0]
        return key, f1_fields[key]
    return None, None


def calls_for_run(entry: RunRegistryEntry) -> tuple[str, str]:
    if entry.run_id in RUN_CALL_OVERRIDES:
        return RUN_CALL_OVERRIDES[entry.run_id]
    return CALL_COUNT_ANNOTATIONS[entry.pipeline_family]


def build_rows(entries: list[RunRegistryEntry]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in entries:
        if entry.pipeline_family not in FAMILIES:
            continue
        f1_fields = f1_like_fields(dict(entry.primary_metrics))
        metric_key, metric_value = pick_primary_metric(f1_fields)
        calls, calls_basis = calls_for_run(entry)
        rows.append(
            {
                "run_id": entry.run_id,
                "pipeline_family": entry.pipeline_family,
                "split_raw": entry.split,
                "split_norm": normalize_split(entry.split, entry.row_count),
                "row_count": entry.row_count,
                "model": entry.model,
                "date": entry.date,
                "decision": entry.decision,
                "calls": calls,
                "calls_basis": calls_basis,
                "primary_metric_key": metric_key,
                "primary_metric_value": metric_value,
                "all_f1_fields": f1_fields,
            }
        )
    rows.sort(key=lambda r: (r["pipeline_family"], r["split_norm"], r["date"], r["run_id"]))
    return rows


def build_pivot(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Best (highest auto-selected metric) row per (family, normalized split)."""

    pivot: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["primary_metric_value"] is None:
            continue
        key = f"{row['pipeline_family']}|{row['split_norm']}"
        current = pivot.get(key)
        if current is None or row["primary_metric_value"] > current["primary_metric_value"]:
            pivot[key] = row
    return pivot


def print_table(rows: list[dict[str, Any]]) -> None:
    header = (
        "pipeline_family | run_id | split(raw) | split(norm) | rows | model | calls | "
        "metric_key=value"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        metric = (
            f"{row['primary_metric_key']}={row['primary_metric_value']}"
            if row["primary_metric_key"]
            else "(no *_f1 field)"
        )
        print(
            f"{row['pipeline_family']} | {row['run_id']} | {row['split_raw']} | "
            f"{row['split_norm']} | {row['row_count']} | {row['model']} | {row['calls']} | "
            f"{metric}"
        )


def print_pivot(pivot: dict[str, dict[str, Any]]) -> None:
    print()
    print("Best/representative primary metric per (family, normalized split):")
    for key in sorted(pivot):
        row = pivot[key]
        print(
            f"  {key}: {row['primary_metric_key']}={row['primary_metric_value']} "
            f"(run_id={row['run_id']}, calls={row['calls']})"
        )


def derived_numbers(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_run = {row["run_id"]: row for row in rows}

    # --- 1-to-2-call delta ---------------------------------------------
    # These three exact figures come from
    # docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md
    # (full200, gpt-4.1-mini): the frontier's own candidate labels are NOT
    # separately registered run_ids (only the underlying JSON artifact is),
    # so this delta is stated from that doc's numbers directly, cross-checked
    # against the one registry row that IS the same architecture as its
    # "2call_no_sf_adjudicator" candidate.
    two_call_full200 = 0.8356
    one_call_structured_only_full200 = 0.7571
    one_call_structured_plus_det_prescription_full200 = 0.7730
    registry_2call_full200 = by_run["exectv2_same_core_model_swap_full200_20260625"][
        "all_f1_fields"
    ]["gpt41mini_clinical_headline_f1"]
    one_to_two_call = {
        "two_call_full200_source": (
            "docs/experiments/exectv2/reliability/"
            "exectv2_gpt41mini_simplification_frontier_2026-06-24.md:19-23, candidate "
            "'exectv2_gpt41mini_simplification_2call_no_sf_adjudicator'"
        ),
        "two_call_full200_value": two_call_full200,
        "registry_corroboration_run_id": "exectv2_same_core_model_swap_full200_20260625",
        "registry_corroboration_field": "gpt41mini_clinical_headline_f1",
        "registry_corroboration_value": registry_2call_full200,
        "registry_matches_frontier_doc": registry_2call_full200 == two_call_full200,
        "delta_vs_structured_only": round(two_call_full200 - one_call_structured_only_full200, 4),
        "delta_vs_structured_plus_det_prescription": round(
            two_call_full200 - one_call_structured_plus_det_prescription_full200, 4
        ),
    }

    # --- hybrid premium by split ----------------------------------------
    hybrid_full200 = by_run["exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624"][
        "all_f1_fields"
    ]["clinical_headline_f1"]
    hybrid_full200_corroboration = by_run["exectv2_robustness_validation_audit_2026-06-25"][
        "all_f1_fields"
    ]["overall_f1"]
    hybrid_dev140 = by_run["exectv2_v09_single_gpt_simplification_study_dev140_20260621"][
        "all_f1_fields"
    ]["v08_dev140_comparator_f1"]

    baseline_gpt41mini_full200 = by_run["exectv2_same_core_model_swap_full200_20260625"][
        "all_f1_fields"
    ]["gpt41mini_clinical_headline_f1"]
    baseline_deepseek_full200 = by_run["exectv2_same_core_model_swap_full200_20260625"][
        "all_f1_fields"
    ]["deepseek_clinical_headline_f1"]
    baseline_gpt41mini_dev140 = by_run["exectv2_2call_no_sf_adjudicator_gpt41mini_dev140"][
        "all_f1_fields"
    ]["clinical_headline_f1"]
    baseline_deepseek_dev140 = by_run["exectv2_2call_no_sf_adjudicator_deepseek_dev140"][
        "all_f1_fields"
    ]["clinical_headline_f1"]

    gepa_full200_rows = [r for r in rows if r["pipeline_family"] == "gepa_from_scratch" and r["split_norm"] == "full200"]
    gepa_dev140_best = max(
        (r for r in rows if r["pipeline_family"] == "gepa_from_scratch" and r["split_norm"] == "dev140"),
        key=lambda r: r["primary_metric_value"],
    )

    premium_gpt41mini_matched_full200 = round(hybrid_full200 - baseline_gpt41mini_full200, 4)
    premium_gpt41mini_matched_dev140 = round(hybrid_dev140 - baseline_gpt41mini_dev140, 4)
    ratio_gpt41mini_matched = (
        round(premium_gpt41mini_matched_dev140 / premium_gpt41mini_matched_full200, 3)
        if premium_gpt41mini_matched_full200
        else None
    )

    premium_best_available_full200 = round(hybrid_full200 - baseline_deepseek_full200, 4)
    premium_best_available_dev140 = round(hybrid_dev140 - baseline_deepseek_dev140, 4)

    hybrid_premium = {
        "hybrid_full200_run_id": (
            "exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624"
        ),
        "hybrid_full200_field": "clinical_headline_f1",
        "hybrid_full200_value": hybrid_full200,
        "hybrid_full200_corroboration_run_id": "exectv2_robustness_validation_audit_2026-06-25",
        "hybrid_full200_corroboration_field": "overall_f1",
        "hybrid_full200_corroboration_value": hybrid_full200_corroboration,
        "hybrid_dev140_run_id": "exectv2_v09_single_gpt_simplification_study_dev140_20260621",
        "hybrid_dev140_field": "v08_dev140_comparator_f1",
        "hybrid_dev140_value": hybrid_dev140,
        "hybrid_dev140_upstream_source": (
            "docs/experiments/exectv2/key_entities/"
            "exectv2_holistic_finding_assembly_v08_dev140_20260621.md (clinical_headline "
            "score view, Overall F1 row) -- NOT independently registered under its own "
            "run_id, only embedded as this field in the v09 study row."
        ),
        "hybrid_dev140_widely_cited_variant": 0.9155,
        "hybrid_dev140_widely_cited_variant_source": (
            "docs/experiments/exectv2/key_entities/"
            "exectv2_dedup_phase1_active_scoreboard_2026-06-23.md:25 -- NOT a registry "
            "primary_metrics value under any run_id; a ~0.0003 rounding-level variant of "
            "the same underlying v08 dev140 artifact, repeated across ~15 other docs."
        ),
        "baseline_family": "exectv2_same_core_model_swap (architecture_family='llm_only' "
        "per registry; the 2-call structured-extractor + deterministic-projection "
        "architecture)",
        "baseline_gpt41mini_full200_run_id": "exectv2_same_core_model_swap_full200_20260625",
        "baseline_gpt41mini_full200_value": baseline_gpt41mini_full200,
        "baseline_gpt41mini_dev140_run_id": "exectv2_2call_no_sf_adjudicator_gpt41mini_dev140",
        "baseline_gpt41mini_dev140_value": baseline_gpt41mini_dev140,
        "baseline_deepseek_full200_run_id": "exectv2_same_core_model_swap_full200_20260625",
        "baseline_deepseek_full200_value": baseline_deepseek_full200,
        "baseline_deepseek_dev140_run_id": "exectv2_2call_no_sf_adjudicator_deepseek_dev140",
        "baseline_deepseek_dev140_value": baseline_deepseek_dev140,
        "framing_A_model_held_constant_gpt41mini": {
            "premium_full200": premium_gpt41mini_matched_full200,
            "premium_dev140": premium_gpt41mini_matched_dev140,
            "ratio_dev140_over_full200": ratio_gpt41mini_matched,
        },
        "framing_B_best_available_baseline_per_split_deepseek": {
            "premium_full200": premium_best_available_full200,
            "premium_dev140": premium_best_available_dev140,
            "note": (
                "DeepSeek is the strongest registered same-core baseline at BOTH splits "
                "(full200 0.8566 > gpt41mini 0.8356; dev140 0.8596 > gpt41mini 0.8396). No "
                "DeepSeek row exists for the hybrid family at either split, so this framing "
                "necessarily compares a gpt-4.1-mini hybrid to a DeepSeek baseline -- a "
                "model-confound, flagged, not hidden."
            ),
        },
        "gepa_full200_rows_found": len(gepa_full200_rows),
        "gepa_dev140_best_run_id": gepa_dev140_best["run_id"],
        "gepa_dev140_best_value": gepa_dev140_best["primary_metric_value"],
        "gepa_full200_available": bool(gepa_full200_rows),
        "gepa_vs_hybrid_dev140_only_delta": round(hybrid_dev140 - gepa_dev140_best["primary_metric_value"], 4),
    }

    return {"one_to_two_call": one_to_two_call, "hybrid_premium": hybrid_premium}


def main() -> None:
    entries = load_run_registry(REGISTRY_PATH)
    rows = build_rows(entries)
    pivot = build_pivot(rows)
    derived = derived_numbers(rows)

    print_table(rows)
    print_pivot(pivot)
    print()
    print("Derived numbers:")
    print(json.dumps(derived, indent=2, sort_keys=True))

    OUT_JSON.write_text(
        json.dumps(
            {
                "rows": rows,
                "pivot": {k: v for k, v in pivot.items()},
                "derived": derived,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"\nWrote {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
