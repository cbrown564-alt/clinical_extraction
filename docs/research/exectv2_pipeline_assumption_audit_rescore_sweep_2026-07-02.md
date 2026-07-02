# Pipeline assumption audit — Phase 4 re-score sweep (all cited runs)

Date: 2026-07-02. Owner: ExECTv2 workstream.
Predecessor: `docs/research/exectv2_pipeline_assumption_audit_phase1_2026-07-02.md`.

Mechanical, zero-new-LLM-call sweep: every registered ExECTv2 run whose
`clinical_headline` metrics were computed under a now-corrected scorer bug had its
cached predictions re-scored with the **finalized** scorer, and every derived
artifact (four ledger dossiers, frontend reliability scorecard) regenerated.
Citation policy: **overwrite-with-disclose** (corrected number becomes the number;
pre-fix value + a dated re-score note recorded in each run's `claim_language_notes`).

## Finalized scorer folded in

Rx clause-scope future/weight fix + valproate/brand drug-lexicon unification (P1–P4);
SF zero-count precedence (SF-1); Investigations text-fallback gate (I1, latent);
Diagnosis D1 hierarchy-aware concept match (`_concept_overlap_count` in
`scoring/match.py`, credits ancestor/descendant gold↔pred pairs as one match).

## Harness self-validation (canonical run)

The re-score harness reproduces the finalized per-family dev140 `clinical_headline`
numbers for `exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628` **exactly**:
Rx **0.9122**, SF **0.5982**, Dx **0.6779**, Inv **0.8583**. Path faithfulness is
guaranteed by reproducing `run_gepa._canonical_headline`'s aggregation over the
four official scorers on the cached `predicted_mentions`.

### Diagnosis convention clarification (important for the headline number)

The finalized Dx `clinical_headline` per-family number **0.6779 is `concept_only`** —
the actual `clinical_headline` unit-key surface (`clinical_headline_unit_keys`
maps Diagnosis → `_concept_keys(..., "concept")`), which the D1 fix moves
0.6617→0.6779 (+5 recall_tp, +5 precision_tp via hierarchy matching). `run_gepa`'s
overall historically used `concept_negation` for its Diagnosis component, on which
D1 is invisible (stays 0.6617). To re-fold D1 and keep the reported overall equal
to the micro-average of the four cited `clinical_headline` surfaces, the finalized
**overall uses `concept_only` for Diagnosis**. Both numbers are disclosed in the
registry note; the `concept_negation`-based overall is 0.7428 for cross-reference.

## Canonical run OVERALL clinical_headline (the manuscript headline number)

**0.7491** (Dx=`concept_only`, D1+lexicon folded).
Ladder: 0.7313 (pre-audit) → 0.7416 (post-Phase1, `concept_negation`) →
**0.7491** (finalized). `concept_negation`-basis cross-reference: 0.7428.

## Step 1 — re-score sweep (registry `primary_metrics` overwritten + disclosed)

`gepa_from_scratch` runs (overall / Dx / SF / Rx / Inv `clinical_headline` F1):

| run_id | overall | Dx | SF | Rx | Inv |
| --- | --- | --- | --- | --- | --- |
| exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628 (canonical) | 0.7416→**0.7491** | 0.6617→0.6779 | 0.5982→0.5982 | 0.9073→0.9122 | 0.8583→0.8583 |
| exectv2_gepa_dedup_gpt41mini_h2mb8_20260628 | 0.7194→0.7393 | 0.6624→0.6861 | 0.5396→0.5455 | 0.8498→0.8838 | 0.8623→0.8623 |
| exectv2_gepa_dedup_qwen3p6_35b_h2mb8_20260629 | 0.6065→0.6316 | 0.5302→0.5639 | 0.3909→0.3966 | 0.7591→0.8019 | 0.7879→0.7879 |
| exectv2_gepa_investigations_lane_deepseekreasoner_20260630 | 0.6252→0.6465 | 0.4479→0.4743 | 0.4488→0.4537 | 0.8856→0.9198 | 0.9254→0.9254 |
| exectv2_gepa_multifamily_dedup_qwen3p6_35b_h2mb8_20260629 | 0.6540→0.6792 | 0.5526→0.5990 | 0.5056→0.5112 | 0.7303→0.7593 | 0.9323→0.9323 |
| exectv2_gepa_multistage_dedup_gpt41mini_20260628 | 0.7235→0.7415 | 0.6500→0.6761 | 0.5500→0.5556 | 0.8514→0.8780 | 0.9160→0.9160 |
| exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701 | 0.7596→0.7785 | 0.7194→0.7463 | 0.6006→0.6068 | 0.8860→0.9123 | 0.8571→0.8571 |

`gepa_sf_verify` runs (SF-only `clinical_headline` / `state_profile` F1):

| run_id | clinical_headline | state_profile |
| --- | --- | --- |
| exectv2_gepa_sf_verify_gpt41mini_20260628 | 0.6029→0.6029 | 0.7483→0.7483 (P/R 0.7067/0.7794→0.7133/0.7868) |
| exectv2_gepa_sf_verify_p5_reasoner_mini_ex_20260629 | 0.6080→0.6136 | 0.7661→0.7729 |
| exectv2_gepa_sf_verify_p5_reasoner_mini_fb_20260629 | 0.5873→0.5928 | 0.7661→0.7729 |
| exectv2_gepa_sf_verify_p5_reasoner_reasoner_ex_20260629 | 0.5861→0.5921 | 0.7839→0.7912 |
| exectv2_gepa_sf_verify_p5_reasoner_reasoner_fb_20260629 | 0.5600→0.5653 | 0.7434→0.7500 |
| exectv2_gepa_sf_verify_v2_deepseekchat_20260629 | 0.5340→0.5388 | 0.7021→0.7080 |

Full-200 holdout (AGGREGATE-ONLY, structural replay over frozen cached lane
artifacts; no row-level inspection; no LLM calls):

| run_id | overall clinical_headline |
| --- | --- |
| exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624 | 0.8502→**0.8616** |

Per-family primary_metrics for the full-200 run were left at pre-fix values per the
aggregate-only mandate. Replay fidelity confirmed by the Investigations aggregate
reproducing unchanged (0.9213, latent I1 fix); the +0.0114 overall is Dx D1 +
Rx clause-scope/lexicon.

Not re-scored — stale-disclosed (see "Discrepancy flags"): the five
`exectv2_2call_no_sf_adjudicator_*` runs (deepseek/gpt41mini/qwen36 dev140,
qwen36_repair_v02 dev140, qwen36_repair_v02 full200).

## Step 2 — derived artifacts regenerated

### Ledger dossiers (`render_dossier.py`, from reconciled `gold_case_ledger_*.jsonl`)

The dossier F1 ladders are live-queried from the (now-corrected) registry. The
mechanism substrate was reconciled to the finalized scorer's disagreement set by
**preserving every surviving adjudication verbatim (matched by
letter_id+type+match_key) and dropping the disagreements the scorer now resolves**;
genuinely-new disagreements are marked `UNADJUDICATED`. Each reconciliation
self-validates: reconciled row count == official `fp+fn`.

- **Diagnosis 209→199.** D1-aware: dropped exactly the 5 hierarchy-recovered
  gold-parent/pred-child pairs (10 rows: 5 missed + 5 spurious) in
  **EA0002, EA0006, EA0007, EA0035, EA0153** — all `gold_multiplicity_consolidation`.
  Genuine-model-error share 31/209 (14.8%) → 31/199 (15.6%), reinforcing the
  gold-artifact finding. 0 unadjudicated.
- **Prescription 48→36.** Reflects clause-scope + lexicon: EA0093's
  `valproate`/`sodium-valproate` pair collapsed (lexicon), plus 12 clause-scope
  FPs resolved. 2 new FNs (EA0038/EA0114 carbamazepine, from clause-scope) marked
  UNADJUDICATED. Self-validates 36 == official fp+fn.
- **Investigations 31→35.** I1 is latent (0 drops). Reconciliation surfaced 4
  pre-existing missing disagreements (EA0044/46/132/200 EEG/MRI missed) — the
  committed ledger predated the scorer's current count; now consistent (35 ==
  official). 4 UNADJUDICATED.
- **SeizureFrequency 66 (UNCHANGED — flagged).** Not regenerated: this ledger was
  built on a **2026-06-29 live LLM re-run** of the SF-verify program
  (`_sf_canonical`, stage-2 state_profile 0.7724, tp/fp/fn 112/42/24) that
  reproduces the registered stored `.jsonl` only 99/140. It is therefore on a
  different prediction basis than the registered run (stored-jsonl state_profile
  0.7483), a pre-existing inconsistency unrelated to the scorer fixes. Regenerating
  it faithfully requires re-running the SF LLM program (not a zero-LLM mechanical
  operation, and non-reproducing at 99/140). The SF dossier re-renders with the
  corrected F1 ladder (sp 0.7483) but keeps its live-rerun mechanism table.

### Frontend reliability scorecard

`scripts/build_exectv2_reliability_scorecard_data.py` regenerated
`frontend/public/mock-data/exectv2/reliability-scorecard.json`; the Rx correction
ripples into the live-computed reliability cells (e.g. prescription cell F1
0.9059→0.9195). `tests/test_exectv2_final_consolidation.py::
test_static_frontend_scorecard_matches_builder_contract` is now **green** (was
red-by-design). Side-effect: the same sanctioned builder also rewrites
`frontend/public/mock-data/gan2026/reliability-scorecard.json`, which changed only
its `generated_on` date (content byte-identical).

## Discrepancy flags (for the orchestrator)

1. **The five `exectv2_2call_no_sf_adjudicator_*` runs DO have cached predictions
   on disk** — the phase1 doc's premise that their `.jsonl` were absent is
   incorrect (all present). Per the sweep's scoping they were **not** re-scored;
   their disclosure notes truthfully mark the metrics stale/uncorrected and record
   that predictions are available for a future re-score. The phase1 doc said
   "four"; five run_ids match the pattern.
2. **Rx/Inv canonical `_cases.json` were regenerated** under the current scorer
   (36/35 cases) and are now misaligned with the positional-`case_id`-keyed
   `_verdicts_batch*.json` (48/31 old). The ledgers are correct (reconciled by
   match-key, not via `finalize_rx_inv_canonical.py`), but **do not blindly re-run
   `finalize_rx_inv_canonical.py`** — it would need the 2 Rx + 4 Inv new cases
   re-adjudicated first.
3. **Diagnosis overall convention change** (concept_negation→concept_only) is the
   only non-purely-mechanical decision in the sweep; it is required to make D1
   visible in the headline and to keep overall == micro-average of the four cited
   per-family surfaces. Documented in the canonical run's registry note.

## Files changed by this sweep

`experiments/registry.jsonl` (19 records: 13 dev140 re-scores + 1 full-200 aggregate
+ 5 stale-disclosures; 253 rows preserved, validated), the four
`docs/canon/workstreams/*_CANONICAL_LEDGER_CANON.md` dossiers,
`experiments/gold_case_ledger_{diagnosis,prescription,investigations}.jsonl`,
`docs/research/error_analysis/{rx,inv}_canonical/*` substrate,
`frontend/public/mock-data/{exectv2,gan2026}/reliability-scorecard.json`.
Not touched: any scorer/deterministic/contract source, `hypothesis_registry.jsonl`,
`PROJECT_STATUS.md`, the manuscript.
