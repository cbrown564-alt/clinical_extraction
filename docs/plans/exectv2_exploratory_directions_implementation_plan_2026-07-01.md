> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# Implementation plan — Exploratory Research Directions (Tier 1 + Phase 0)

Status: **EXECUTED, all phases complete.** Date: 2026-07-01 (planned and executed same day).
Owner: ExECTv2 workstream.

Outcomes: Phase 0 done (`docs/experiments/exectv2/exectv2_test60_split_dedupe_fix_2026-07-01.md`).
Item 2 done (`docs/research/exectv2_registry_survivorship_bias_2026-07-01.md`) — also surfaced
and fixed 3 silently-unregistered GEPA run families plus a pre-existing broken registry row
blocking validation. Item 3 done (`docs/research/exectv2_cost_quality_matched_split_table_2026-07-01.md`)
— corrected the review's own "+0.2 F1, ~5x split-dependent" claim as a conflation of two
comparisons. Item 4 done (`docs/research/exectv2_gold_inflation_mechanical_heuristic_2026-07-01.md`)
— kill-criterion passed cleanly, with an honest non-generalization finding. Phase 2 done
(`docs/research/exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md`) — the review's
credit-assignment hypothesis CONFIRMED qualitatively (0.7235 -> 0.7596, verify instructions
turned filter-shaped), kill-criterion narrowly MISSED (-0.0014). See `PROJECT_STATUS.md`'s
`Next` section for the consolidated summary.

Companions:
- `docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`
  (the multi-agent review this plan implements; correction banner added
  2026-07-01 — see below)
- `PROJECT_STATUS.md` (`Next` section, corrected 2026-07-01)

## Scope

Implements the review's **Tier 1** (items 1-4, "high significance, feasible
now") plus the **Phase 0 fix** the review's actionable finding requires,
re-attributed correctly (see below). **Tier 2 (items 5-8) is explicitly out of
scope** — the review itself flags them as more expensive or narrower (item 5
is a full new adjudication phase; item 7 needs a circularity-safe design not
yet specified). They stay backlog until a Tier-1 result creates a reason to
pull one forward.

Two tracks, run in this order:

1. **Free track** (Phase 0 + items 2-4): pure re-analysis/synthesis of
   artifacts already on disk. No new LLM calls, no guardrail surface. The
   three Tier-1 analysis items (2, 3, 4) are mutually independent and can run
   in parallel.
2. **Costed track** (item 1): one code change + one live GEPA rerun
   (gpt-4.1-mini task model, deepseek-reasoner reflection). Real $ and GEPA
   infra surface. **Gated on explicit go-ahead before launch** — do not start
   without confirming.

## Phase 0 — `test60` split identity-fix (corrected framing)

**Re-attribution (done 2026-07-01):** the review's "actionable finding"
originally framed the 4 duplicate letter-pairs found by md5-hashing
`data/ExECTv2 (2025)/Gold1-200_corrected_spelling/` as an undiscovered corpus
bug. That framing was wrong and has been corrected in both
`PROJECT_STATUS.md` and the review doc (correction banners added). The source
paper (Fonferko-Shadrach et al. 2024, *Annotation of epilepsy clinic letters
for natural language processing*, J Biomed Semantics, DOI
10.1186/s13326-024-00316-z) states directly: **"Four letters were duplicated
within the set to test for consistency in annotations."** That is exactly the
4 pairs / 8 of 200 letters (4%) found — a disclosed, intentional
annotation-QA design by the corpus's original authors, not a defect.

**What is still genuinely ours to fix:** `data/ExECTv2 (2025)/splits/exectv2_split_v1.json`
stratifies only by `has_seizure_frequency_mention`, with no
identity-awareness, so it did not know to keep the paper's known duplicate
pairs on one side of the dev/test boundary. One pair — `EA0159` (test) /
`EA0160` (dev) — landed across it (confirmed byte-identical via diff).
Citation check (done): `EA0159` is not cited as a standalone example anywhere
in this repo; `EA0160` is cited repeatedly in
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`
(lines 127-129, 180-182, 254) but only within dev140-internal SF Phase 7
analysis, so it never crosses the test boundary.

### Steps

1. Write `experiments/exectv2_corpus_dedupe_audit.py` (read-only, zero-LLM):
   md5-hash all 200 letters + `.ann` files, reproduce the 4 pairs
   `(EA0021, EA0183)`, `(EA0149, EA0185)`, `(EA0159, EA0160)`,
   `(EA0169, EA0181)`, confirm which `.ann` pair has the "trivial offset
   typo" difference the review mentions, and confirm all 4 pairs' split
   placement (3 same-side / 1 cross-side) against `exectv2_split_v1.json`.
   Output a small JSON/markdown report under `experiments/`.
2. **Decision point (needs explicit sign-off — touches the frozen `test60`
   guardrail):** how to resolve the cross-split pair. Two options:
   - **Option A (recommended default):** drop `EA0159` from `test`, leaving
     `test59` (59 independent letters) going forward. This makes all 4 pairs
     consistent with the "same-side duplicates are harmless" precedent the
     other 3 pairs already establish, and removes rather than relocates.
   - **Option B:** move `EA0159` into `dev`, making it a 4th same-side
     duplicate pair (dev grows to 141 rows, one of which duplicates
     `EA0160`'s content) and `test` shrinks to 59 unique letters. No real
     benefit over Option A since `EA0159`'s content is already present in
     dev via `EA0160`.
   Do not implement either without confirming the choice — this changes the
   definition of the frozen holdout that "test60 is frozen and untouched"
   claims rest on.
3. Cut a **new versioned split manifest** (`exectv2_split_v2.json`) rather
   than mutating `v1` in place — `v1` is referenced by `evidence_validity`
   language in existing registry rows, so it must remain a stable historical
   record. Register `v2` and update `data.py`'s `DEFAULT_SPLIT_MANIFEST` only
   when the project is ready to cut over; until then, keep both paths valid
   and document which future runs use which.
4. Write a short dated doc (`docs/experiments/exectv2/exectv2_test60_split_dedupe_fix_2026-07-01.md`)
   recording: the paper citation, the dedupe audit output, the decision made
   and why, and the before/after split composition.
5. Update `PROJECT_STATUS.md`'s `Next` entry to reflect the fix is done, once
   landed.

## Phase 1 — free track (parallelizable)

### Item 2 — survivorship-bias write-up (registry chain-tracing)

**Already verified** (review doc, `experiments/registry.jsonl`): 9/244 = 3.7%
`promote`, 146 = 59.8% `revise`, 34 = 13.9% `reject`; `supersedes` populated on
127/244 rows vs. `superseded_by` on only 8/244. What remains: trace the
run_ids the manuscript's claims actually rest on back through their
`supersedes` chains and report a mean chain-length-to-publication.

**Confirmed methodology gap:** the manuscript
(`docs/research/paper_manuscript_2026-06-26.md`) does not cite run_ids
directly (one exception:
`` `exectv2_2call_no_sf_adjudicator` ``). It cites ~16 companion docs instead
(`docs/research/*.md`, `docs/experiments/**/*.md`, 2 raw artifact paths — full
list already extracted). Each of those docs in turn cites the run_ids its own
claims rest on (the same "Runs (dev140, mini): `run_id` (score), ..." pattern
seen in `exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`). So this
is a two-hop extraction, not a direct grep.

Steps:
1. `experiments/registry_survivorship_analysis.py` (zero-LLM):
   - Extract run_ids from each of the 16 manuscript-cited companion docs.
   - Look each up via `clinical_extraction.core.registry.load_run_registry`;
     walk `supersedes` recursively to compute chain-length-to-publication per
     cited run_id, and walk `superseded_by` forward as a sanity check that
     the cited run is indeed the terminal (non-superseded) node.
   - Compute mean/median chain length across the cited set; contrast against
     the registry-wide 244-row picture already verified.
2. Write `docs/research/exectv2_registry_survivorship_bias_2026-07-01.md`:
   state plainly what fraction of registry churn (revise/reject rows) the
   manuscript's prose narrative absorbs silently per citation, using the
   real numbers from step 1 — this is the "literal, structured audit trail"
   version of the preregistration-vs-narrative gap the review flags as
   citable.

No new runs. Near-zero marginal cost per the review; confirmed feasible from
what's on disk.

### Item 3 — matched-split, cross-architecture cost-quality table

**Correction to the review's framing, found during research for this plan:**
not all of the review's cited numbers are already sourced verbatim on disk —
part of this item requires deriving numbers, not just copying them into one
table.

Verified as directly sourced:
- 2-call→3-call delta **+0.007 F1** for 1.5x budget: exact from
  `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md:19-23`
  (full200: 3-call 0.8426 vs 2-call 0.8356).
- Deterministic post-processing stack **+0.062 F1** on the same 2-call base,
  zero marginal model calls: exact from
  `experiments/exectv2_component_off_replay_full200_20260626.md:35-37`
  (`standard_dictionary` +0.0186, `residual_semantic_lens` +0.0117,
  `headline_projection` +0.0317, sum 0.0620).

Verified as **derivable but not yet written down**:
- 1-call→2-call delta: same frontier table gives 2-call 0.8356 vs 1-call
  0.7730 / 0.7571 → deltas +0.0626 / +0.0785, consistent with the review's
  "+0.063-0.083" — needs to be computed and stated explicitly as a delta, not
  re-cited as if already tabulated.

**Not found anywhere on disk** (needs fresh computation, not re-citation):
- The "hybrid is worth +0.2 F1, split-dependent by ~5x (full200 +0.0076 vs.
  dev140 +0.076)" claim. `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`
  does **not** contain these numbers (it covers a different ablation:
  `evidence_validation` gate Δ=0.0000 both tasks, `standard_dictionary`
  Δ=+0.0389 exectv2 / +0.0293 Gan2026). This specific comparison must be
  computed fresh from the registry (full200 hybrid rows already exist under
  `pipeline_family` values like `exectv2_holistic_finding_assembly` /
  `exectv2_hybrid*`; a matched full200 single-pass/GEPA baseline needs to be
  identified for the same split) — zero new LLM calls, but real synthesis
  work, not a copy-paste.

**Known pitfall to build around:** GEPA runs are registered under
`pipeline_family: "gepa_from_scratch"`, not an `exectv2_*`-prefixed value. A
naive substring filter over the registry will silently exclude GEPA from
"every architecture family" — the table-building script must include it
explicitly. Distinct `exectv2`-prefixed `pipeline_family` values already
enumerated (22 of them, from this plan's research pass) plus
`gepa_from_scratch` is the full family set to cover.

Steps:
1. `experiments/exectv2_cost_quality_matched_split_table.py`: query the
   registry for the full family set above; for each family, on each split
   where both `full200` and `dev140` rows exist, pull LLM-call-count
   (annotate per family — not a registry field), primary F1, split,
   row_count.
2. Compute the two derived deltas above explicitly (1→2 call, hybrid
   full200-vs-dev140 premium) with exact run_id citations per cell.
3. Write `docs/research/exectv2_cost_quality_matched_split_table_2026-07-01.md`:
   the unified table, the resolved hybrid-premium split-dependency number
   (correct whatever was previously informally cited), and the F1-per-cost
   ranking (deterministic stack ≈ 9x better than the 3rd LLM call, per the
   review, re-verified here).

### Item 4 — mechanical heuristic for gold-inflation vs. genuine error

**Schema confirmed:** all four family adjudications use the same 3-way
`verdict` enum (`GOLD_RIGHT` / `MODEL_DEFENSIBLE` / `BOTH_DEFENSIBLE`) in a
CSV on disk, plus a separate binary `mechanism` enum
(`H1_CARDINALITY` / `H2_GENUINE_DIVERGENCE`) used specifically in the four
`*_ev_recall_consolidation_check` scripts' adjudication CSVs. **No
orthographic/typo category exists as a labeled field anywhere** — it is only
free text in the `reason` column. H-inflated shares confirmed exactly as the
review states: Diagnosis 93.5% (86/92,
`docs/experiments/exectv2/diagnosis/exectv2_dx_ev_recall_consolidation_check_2026-06-30.md:79-80`),
SF 61.1-83.3% (`.../exectv2_sf_ev_recall_consolidation_check_2026-06-30.md:77-83`),
Prescription 52.2% (12/23,
`docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md:73-77`),
Investigations 25.9-29.6% (same doc, lines 108-114).

Prescription's mechanism (confirmed passage, same doc lines 81-93): of the 12
inflated cases, 4 are `H1_CARDINALITY`; the other 8 are typo/transcription
breaks in `source_near`'s substring match — gold misspells the drug
(`Lamotrigne`, `Lacosmaide`, `Carbmazapine`, `EPlim`, `zobisamide`) or the
source letter does (`lamtorigine`, `oxcarbazine`) and the model normalized to
correct spelling; every case's CUI/dose/frequency matches gold exactly. These
8 are currently mis-tagged `H2_GENUINE_DIVERGENCE`.

Steps:
1. Locate the exact adjudication CSV path for each family's
   `*_ev_recall_consolidation_check` (Glob to confirm all four precisely;
   SF and Rx/Inv paths are known from this plan's research, Dx's needs
   confirming at execution time).
2. `experiments/exectv2_gold_inflation_mechanical_heuristic.py`
   (zero-LLM, pure re-analysis): add a derived `H3_ORTHOGRAPHIC` bucket via a
   mechanical check over already-adjudicated rows — e.g. edit-distance /
   normalized-identity match between the missed evidence span and a
   present-but-differently-spelled span in the same letter — re-tagging
   `H2_GENUINE_DIVERGENCE` rows that qualify.
3. Check the kill-criterion the review specifies: does the 3-way split
   (`H1_CARDINALITY` / `H3_ORTHOGRAPHIC` / residual `H2_GENUINE_DIVERGENCE`)
   recover Prescription's missed precision (correctly reclassify its 8 typo
   cases) **without** falsely reclassifying any of Investigations' genuine
   H2 cases (the clean-negative family, expected near-zero orthographic
   hits)?
4. Write `docs/research/exectv2_gold_inflation_mechanical_heuristic_2026-07-01.md`
   ending in a concrete pre-flight decision rule usable before spending
   adjudication budget on a new family (relevant if Tier-2 item 5 — Onset,
   EpilepsyCause, WhenDiagnosed — is ever pulled forward).

## Phase 2 — item 1: verify-stage credit assignment (GATED — confirm before launch)

**Grounded in code + a prior run that already partially corroborates the
hypothesis**, not a cold-start experiment:

- `exectv2/gepa/metric.py`'s `build_metric()` ignores `pred_name` entirely for
  scoring — every predictor, generate or verify, is scored against the same
  undecomposed end-to-end `clinical_headline` F1. `pred_trace` is currently
  only used to read off token counts for the length penalty
  (`_prompt_lengths` / `_predictor_lengths`), never to construct a
  stage-local signal.
- The prior multi-stage run
  (`exectv2_gepa_multistage_dedup_gpt41mini_20260628`, dev140 0.7235, missed
  the +0.03-over-0.731 kill-criterion by −0.008) already diagnosed the
  mechanism via evolved-instruction inspection
  (`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`
  §3): verify cut recall (805→783 facts) and the most heavily-evolved
  verifier drifted into "output a complete corrected list in
  hyphenated-lowercase canonical representation" — reformatting, not
  filtering. This independently corroborates the review's credit-assignment
  hypothesis before any new run is needed to establish the problem exists.
- **Housekeeping gap found:** that prior run's artifacts exist on disk
  (`.json`/`.md`/`.jsonl`/`.instruction.txt` under `experiments/`) but it was
  never written to `experiments/registry.jsonl` despite `register=True` being
  `run_experiment`'s default — the `_register()` call likely hit its
  try/except registry-load-failure path silently. Register it retroactively
  (Phase 2, step 0) so the new run has a fair on-record comparison.

### Design

1. **Freeze S0.** Warm-start generate predictors from
   `load_evolved_s0_seeds()` (as the existing launcher already does) **and**
   restrict GEPA's `component_selector` (already a supported
   `GepaExperimentConfig` field, used today for single-family-lane runs) to
   only the four `verify_<family>` predictors, so GEPA cannot mutate the
   generator at all.
2. **Stage-local reflection feedback, not a stage-local selection score.**
   Modify `metric.py`'s `build_metric()` (or add a sibling
   `build_verify_stage_metric()`) so that when `pred_name` identifies a
   `verify_<family>` predictor, the **feedback text** becomes a stage-local
   accept/reject diagnostic: for each draft fact (recoverable from
   `pred_trace`'s captured `draft_facts_json` input to that verify call),
   was it correctly kept/dropped against gold-derived unit-key labels (reuse
   `_family_unit_keys`)? Facts the verifier *adds* beyond the draft get
   separate credit, not folded into the primary accept/reject signal, so
   reflection cannot "win" by reverting to full regeneration. The **`score`**
   GEPA uses for Pareto/candidate selection stays the unchanged end-to-end
   `clinical_headline` F1 — selection must remain comparable across the
   whole program; only the reflection-time feedback text becomes
   stage-local. This is the metric-edit-only version of the review's
   proposal and needs no change to GEPA's scoring semantics.
3. **New launcher**, modeled on `experiments/gepa_multistage_exectv2.py`:
   `experiments/gepa_multistage_verifyonly_exectv2.py`, run_id
   `exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701`, frozen S0
   + `component_selector` restricted to verify predictors + the new
   stage-local feedback metric. Instruction token budget can likely shrink
   from the prior run's 4000 (8 evolvable instructions) since only 4 are now
   evolvable.
4. **Kill-criterion:** does this beat the prior multi-stage run (0.7235)?
   More importantly — does it beat the 0.731 single-pass per-family ceiling
   the review doc's underlying claim is actually about?
5. **Post-run mechanism check:** inspect the evolved verify instructions —
   do they become filter-shaped (explicit keep/reject criteria) rather than
   reformat-shaped? Does the recall-loss pattern (805→783 in the prior run)
   shrink?
6. Write `docs/research/exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md`
   regardless of outcome, stating the review's generalizable claim ("a
   verify/critique stage sharing an undecomposed scalar reward with its
   upstream generator learns to regenerate, not verify") as **CONFIRMED** or
   **REFUTED** based on the result.

### Before launching

- Confirm go-ahead: this is a live GEPA `auto=medium` run, gpt-4.1-mini task
  model + deepseek-reasoner reflection, real $ cost (though fewer evolvable
  predictors than the prior 8-predictor joint run should reduce it
  somewhat).
- Register the prior multistage run retroactively first (step 0 above) so
  the comparison is on the record either way.

## Definition of done

- Phase 0: new versioned split manifest cut and decision documented, or an
  explicit decision to defer with reasons recorded; `PROJECT_STATUS.md`
  updated.
- Items 2-4: each has a dated write-up doc under `docs/research/`, backed by
  a small reusable zero-LLM script, no new runs.
- Item 1: either a positive result (beats 0.731, filter-shaped instruction
  confirmed) or a documented negative closing the question, registry entry
  for both the prior and new run.
- Tier 2 (items 5-8) remains untouched backlog; not re-opened by this plan.
