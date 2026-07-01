# Registry survivorship bias: what the manuscript's citations actually touch

Status: complete. Date: 2026-07-01. Zero-LLM, read-only. Implements Item 2 of
`docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`
(Tier-1 item 2 of `docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`).
Script: `experiments/registry_survivorship_analysis.py`.

Already established (not re-derived here): `experiments/registry.jsonl` has 244
rows — 9 `promote` (3.7%), 146 `revise` (59.8%), 34 `reject` (13.9%); `supersedes`
is populated on 127/244 rows (52.0%) vs. `superseded_by` on only 8/244 (3.3%) —
most lineage is recorded forward-only, if at all.

## Extraction method

`docs/research/paper_manuscript_2026-06-26.md` does not cite run_ids directly
(one exception: `exectv2_2call_no_sf_adjudicator`, a `pipeline_family` prefix,
not a literal run_id). It cites 16 companion docs instead. Each was read for
backtick-quoted run_id-shaped tokens and "Runs / Artifacts / Sources" blocks;
candidates were resolved against the registry three ways, in order: (1) exact
`run_id` match; (2) exact `artifact_paths` basename match; (3) for two
Table-6 row labels in `exectv2_results_section_draft_2026-06-26.md` matching
no registry `run_id` (`..._deepseek_full200`, `..._gpt41mini_full200`), a
metrics cross-check — their cited numbers (0.8566, 0.8356 `clinical_headline_f1`)
match `exectv2_same_core_model_swap_full200_20260625`'s `primary_metrics`
exactly. Unresolved tokens are reported below, not dropped. This is a two-hop
trace (manuscript → doc → run_id); citations the 16 docs make to *other* docs
are a third hop not chased here. Three of the 16
(`reliability_thesis.md`, `closing_stage_research_critique_2026-06-27.md`,
`benchmark_surface_reconciliation_subsection_2026-06-27.md`) cite zero run_ids
or artifacts directly — pure synthesis over the other 13.

## Cited run_id set and chain lengths

16 distinct run_ids resolve to a registry row. `chain_length_to_publication` is
the count of distinct ancestor run_ids reached by recursively walking
`supersedes`. All 16 are terminal (`superseded_by` is `null` on every one) —
the manuscript does not cite a stale predecessor anywhere in this set.

| run_id (suffix after common prefix) | chain len | source doc(s) |
|---|---:|---|
| `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` | 0 | Dx canonical row analysis |
| selector_v0_9\_**frozen_gate1_hard_slice_audit**_2026-06-26 | 1 | consensus/fresh selector fate |
| selector_v0_9\_**frozen_gate2_robustness_stress**_2026-06-26 | 2 | consensus/fresh selector fate |
| selector_v0_9\_**frozen_gate4_constrained_aggregate_audit**_2026-06-26 | 1 | consensus/fresh selector fate |
| selector_v0_9\_**frozen_gate4_exact_aggregate_audit**_2026-06-26 | 5 | consensus/fresh selector fate |
| selector_v0_9\_**frozen_protocol**_2026-06-26 | 0 | consensus/fresh selector fate |
| selector_v0_9\_**validation750_no_call_replay**_2026-06-15 | 8 | consensus/fresh selector fate |
| `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | 0 | results section draft |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | 0 | results section draft |
| `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | 0 | results section draft |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140` | 1 | results section draft |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | 0 | results section draft |
| `exectv2_same_core_model_swap_full200_20260625` (metrics-verified) | 0 | results draft; outline; results section |
| `gan2026_closeoff_report_2026-06-12` (self-registered) | 0 | itself |
| `exectv2_hybrid_benchmark_overall_dev_20260618` (artifact-path match) | 0 | itself |
| `gan2026_reliability_p2_1_semantic_entropy_2026-06-17` (artifact-path match) | 0 | itself; manuscript outline |

(Rows 2-7: `gan2026_consensus_fresh_agreement_selector_v0_9_` + the bolded suffix.)

**Mean chain length: 1.12. Median: 0.00. Range: 0–8.**

The distribution is bimodal, not uniformly shallow: 10 of 16 citations have
chain length 0 or 1, but the Gan consensus/fresh-selector family carries real
depth — `gate4_exact_aggregate_audit`'s chain (5) crosses out of its own
selector-run family into two `agentic_structured_event_consensus_*` test450
runs from 2026-06-13/26, and `validation750_no_call_replay`'s chain (8) is the
full v0.2→v0.8 prompt-iteration ladder for that selector.

**This chain length is a lower bound, not a full iteration count.** Only
127/244 (52.0%) of rows populate `supersedes` at all — a run can have real,
undocumented iteration history with zero `supersedes` edges recording it. A
chain length of 0 means "no *recorded* ancestor," not "first attempt." Given
146/244 rows (59.8%) are `revise`, it is not plausible most 0-length citations
above are literally the first thing tried; the low mean is at least partly an
artifact of the same forward-only-recording gap already established for the
registry as a whole, not evidence that little iteration preceded these
results.

## Registry-wide accounting

| bucket | all 244 rows | `revise` (146) | `reject` (34) | `revise`+`reject` (180) |
|---|---:|---:|---:|---:|
| cited | 16 (6.6%) | 8 | 1 | 9 (5.0%) |
| absorbed (supersedes ancestor) | 12 (4.9%) | 12 | 0 | 12 (6.7%) |
| accounted (cited + absorbed) | 28 (11.5%) | 20 | 1 | 21 (11.7%) |
| untouched | 216 (88.5%) | 126 | 33 | 159 (88.3%) |

**Of the 180 rows that were revised or rejected, only 9 (5.0%) are directly
cited by the manuscript's citation graph, a further 12 (6.7%) are silently
absorbed as a `supersedes` ancestor of something cited, and 159 (88.3%) are
completely untouched by anything the finished manuscript rests a claim on.**
That untouched rate (88.3%) is statistically indistinguishable from the
registry-wide rate (88.5%) — churn rows are not disproportionately hidden
relative to the registry as a whole; they are simply most of the registry,
and the manuscript's visible citation graph is small relative to it either way.

## Not registered: citations the registry cannot see

11 further run-shaped references, cited by the same 16 companion docs, resolve
to **no registry row at all** despite dated artifacts existing on disk. Checked
explicitly rather than silently dropped, per the source review's finding that
unregistered artifacts are themselves worth reporting:

- `exectv2_gepa_sf_verify_gpt41mini_20260628` (+ its whole Phase-5 sibling
  family) — the canonical two-stage GEPA run the SF plateau finding
  (`state_profile` 0.710→0.772) rests on. Same silent-registration-failure the
  implementation plan already flagged for `exectv2_gepa_multistage_dedup_
  gpt41mini_20260628` (Phase 2 step 0) — a second, independent instance.
- `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator` — lean 2-call
  cost-performance frontier row.
- `gan2026_research_closeout_synthesis_2026-06-17` — one of the 16 cited
  companion docs has no registry row of its own; its own "Core Artifacts"
  section is mostly empty backtick placeholders.
- `gan2026_simplest_arch_decomposition_v1_validation750_2026-06-16` and
  `gan2026_single_model_anchor_v0reference_test450_aggregate_readout_2026-06-16`
  — the only two non-empty entries in that same section.
- `exectv2_sf_wall_transfer_probe_2026-06-27` — the wall-transfer verdict
  (`band_unknown` entropy 0.000, H0 not refuted).
- `exectv2_component_off_replay_dev140_20260626` / `..._full200_20260626` —
  one-component-off replay tables (Tables 8, R2, R8); the full200 file is
  also what the implementation plan's own Item 3 cites directly.
- `exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12`.
- `cross_task_shared_component_ablation_2026-06-27` — sole evidentiary basis
  for the manuscript's one cross-task component-transfer claim (N=2,
  `evidence_validation` Δ=0.0000 both tasks).
- `gan2026_component_stage_ladder_validation_20260624`.

**27 distinct references were traced from the 16 companion docs; 11 of them
(40.7%) have no registry row.** The registry is not a complete map of the
manuscript's evidentiary base — it is missing several load-bearing artifacts,
including the SF plateau's canonical run and the sole cross-task-transfer
table. Every number reported above (the 16-citation chain lengths, the 88.5%
registry-wide untouched rate) is computed only over the portion of the
citation graph the registry can see; the true denominator for "how much churn
feeds a published claim" is larger than 244 rows, and unknowable exactly from
`registry.jsonl` alone.

## What this means for reproducibility

A reader of the manuscript sees a small number of final, headline results.
Three separate things sit behind them, not one. (1) A **visible-but-shallow**
lineage where `supersedes` is recorded: most cited results trace back 0-1
registered prior attempts, a minority (the Gan consensus/fresh-selector
chains) trace back 5-8, and none of the 16 is stale. (2) A **much larger
invisible lineage**: of 180 revised/rejected rows, 88.3% never appear in the
manuscript's citation graph in any form the registry can show, either because
the iteration was never `supersedes`-linked (52.0% coverage registry-wide) or
because the negative result was not the direct precursor of any cited run.
(3) **Load-bearing artifacts outside the registry entirely**: 40.7% of the
references the companion docs themselves cite — including the SF plateau's
canonical run and the only cross-task-transfer evidence table — have no
registry row, so `supersedes`-chain tracing cannot see them at all.

None of this means the manuscript's claims are wrong; the row-level
adjudication work already on record (Dx, SF, Rx, Inv consolidation checks)
independently audits the claims themselves, not their audit trail. What it
means is narrower: the registry's `supersedes` mechanism, as currently used,
cannot reconstruct how much iteration preceded a published number — most rows
never record what they replaced, and a real fraction of what the manuscript
cites was never entered into the registry at all. A reader relying on
`registry.jsonl` to audit "how much was tried before this" would see roughly
1/9th of the true picture (28 of 244 rows) at best, and would miss several
artifacts the manuscript's own prose depends on.

## Artifacts

- `experiments/registry_survivorship_analysis.py` — script this doc reports
  (zero-LLM, read-only; `uv run python experiments/registry_survivorship_analysis.py`).
- `experiments/registry.jsonl` — 244 rows, unmodified.
- The 16 companion docs listed in the implementation plan's Item 2 section.
