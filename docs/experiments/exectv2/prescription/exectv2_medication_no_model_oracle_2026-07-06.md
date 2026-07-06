# No-model medication oracle — results

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `rx_no_model_oracle_2026-07-06` — **RESOLVED** (dspy framing
confirmed; sharper than anticipated: deterministic-only *equals* the cited
hybrid `clinical_headline` on both splits, not just approaches it).
Driver: `experiments/exectv2_medication_no_model_oracle_2026-07-06.py` (zero LLM
calls; deterministic replay over gold text).
Umbrella plan: item 4 of `docs/plans/predecessor_synthesis_followups_2026-07-06.md`.

## Headline

**The medication extraction ceiling is deterministic-owned. The LLM lane
contributes zero to the Prescription `clinical_headline` on both splits.** Running
`_extract_prescriptions` alone (no lens, no bridge, no benchmark projection, no
LLM) as the final system reproduces the cited hybrid `clinical_headline` **exactly**
— 0.9615 on dev140 and 0.9278 on full-200, gap +0.0000 on each. This is a direct
confirmation of the dspy predecessor finding in our codebase: dspy reports a
no-model annotation-derived payload at 100% F1 with models sitting *below* the
oracle (S1 GPT 92.8%, S5 GPT 88.7%). Our deterministic extractor does not hit the
literal 100% dspy reports — but the LLM does not clear the deterministic ceiling
either. **The manuscript must frame the medication story as "the deterministic
layer solves it; the LLM's value on this family is elsewhere (full-200 precision),
not on the headline"** rather than "the LLM extracts medications."

This is a **split-invariant, model-independent** ceiling statement: the result
holds on dev140 (gap +0.0000) and on full-200 (gap +0.0000), so it is not a
dev/test artifact.

## The numbers

Two surfaces were scored, in order of how "oracle-like" they are:

| Surface | dev140 F1 | full-200 F1 | What it tests |
| --- | ---: | ---: | --- |
| **`gold_as_prediction`** | **1.0000** (206/0/0) | **1.0000** (293/0/0) | Scorer integrity: gold copied through the pipeline. Not extraction. |
| **`deterministic_only`** | **0.9615** (200/10/6) | **0.9278** (270/19/23) | The real no-model extraction ceiling: `_extract_prescriptions` run as the final system. |
| Cited hybrid `clinical_headline` (for comparison) | 0.9615 | 0.9278 | Hybrid lane (deterministic P7-fixed producer + v08 assembly). |
| **Gap (deterministic-only − cited hybrid)** | **+0.0000** | **+0.0000** | **The LLM adds nothing to the headline.** |

> **Why two surfaces.** `gold_as_prediction` is the dspy-style
> scorer-integrity ceiling: it asks "does the scoring pipeline reproduce gold
> labels when handed gold labels?" A 1.0 here means the scorer is not the source
> of any gap — it confirms the (206 dev140 / 293 full-200) gold counts are
> preserved end-to-end. `deterministic_only` is the real extraction ceiling the
> deterministic layer owns, scored through the *same* `score_prescription_components`
> / `score_prescription_benchmark_projection` scorers used for the hybrid lanes
> (no special-casing). The interesting number is the second row.

Full per-component and benchmark-projection tables are in the JSON artifact;
`clinical_headline` is the headline metric everyone reads.

### Predeclared outcome bands (from plan item 4)

| Outcome band | Verdict | This run |
| --- | --- | --- |
| deterministic-only ≈ 1.0 | dspy framing applies in the strongest form | ✗ (0.9615 dev / 0.9278 full — near-ceiling, not literal ceiling) |
| deterministic-only ≈ cited hybrid (≈ 0.96 / 0.93) | **dspy framing applies; LLM adds nothing to the headline; manuscript says so** | **✓ (gap +0.0000 on both splits)** |
| deterministic-only ≪ cited hybrid | LLM genuinely contributing recall/specificity beyond the lexicon; positive LLM-value story | ✗ |

The result lands in the **middle band, not the top band**: dspy's framing is
confirmed (deterministic owns the medication ceiling; LLM sits at-or-below it),
but it is *not* the literal 47/47 / 100% dspy reports. The difference is traced
below (§Why not 100% like dspy's oracle).

## Why the LLM contributes zero to the headline

This is the key question the probe was designed to answer, and the answer is
clean: the cited 0.9615 dev140 / 0.9278 full-200 `clinical_headline` numbers are
**already** the deterministic-only numbers. They were *produced* by the
deterministic P7-fixed Prescription producer and carry through the v08 hybrid
assembly unchanged — the assembly's Prescription lens is a passthrough for this
producer. (See `exectv2_rx_headtohead_feasibility_finding_2026-07-03.md`: "the
deterministic P7-fixed producer carries through the v08 assembly unchanged.")

The separate LLM-vs-deterministic comparator
(`exectv2_rx_llm_vs_deterministic_comparator_2026-07-03.md`) confirms this from the
other direction: on dev140 the LLM-tuned arm scores **0.9526** — *below* the
deterministic 0.9615. The LLM's medication value is **not** on the
`clinical_headline`; it is a **full-200 precision** effect (FP 19→7), where the
LLM's contextual AED judgment beats the deterministic lexicon's over-capture on
non-epilepsy comorbidity drugs concentrated in the 60 test letters. That is a real
but **narrower** contribution than "the LLM extracts medications," and it is
already documented in the comparator doc's split-dependent-inversion finding.

> **Implication for attribution.** This probe *is* the attribution-discipline
> deliverable for Prescription: it shows what the deterministic layer produces
> *before* any LLM or lens is applied. The cited headline is deterministic-owned
> to four decimals. Per the research-protocol skill's attribution rule ("an
> LLM-first claim requires showing what the model selected before deterministic
> semantic repair"), **Prescription is not an LLM-first claim** — it is a
> deterministic claim that the LLM happens to sit at-or-below on the headline.

## Why not 100% like dspy's oracle

dspy's no-model oracle is an **annotation-derived** payload — it is built *from
the gold annotations*, so it reproduces 47/47 by construction. Our
`deterministic_only` surface is a **real extractor run over raw letter text** —
it does not see the annotations. The residual 0.9615/0.9278 gap is therefore
genuine extraction residual, not a scorer artifact (the `gold_as_prediction` = 1.0
row rules that out). dev140 decomposes as **6 FN + 10 FP across 13 letters**:

**FN (6, recall misses) — the deterministic extractor failed to emit these gold facts:**
| Key | Letter | Likely cause |
| --- | --- | --- |
| `('ordinary', 'perampanel', '8', 'mg', '1')` | EA0117 | perampanel not in lexicon / dose-parse |
| `('ordinary', 'sodium-valproate', '400', 'mg', '2')` | EA0131 | context-window / frequency miss |
| `('ordinary', 'lamotrigine', '50', 'mg', '2')` | EA0137 | multi-dose clause split |
| `('ordinary', 'perampanel', '50', 'mg', '2')` | EA0146 | **gold defect — see below** |
| `('rescue', 'midazolam', 'as_required')` | EA0158 | rescue-as-required surface gap |
| `('ordinary', 'lamotrigine', '100', 'mg', '2')` | EA0197 | multi-dose clause split |

**FP (10, precision over-emissions) — the extractor emitted these non-gold facts:**
| Key | Letter |
| --- | --- |
| `('ordinary', 'levetiracetam', '250', 'mg', '2')` | EA0016 |
| `('ordinary', 'sodium-valproate', '300', 'mg', '2')` | EA0047 |
| `('ordinary', 'sodium-valproate', '400', 'mg', '2')` | EA0075 |
| `('ordinary', 'carbamazepine', '100', 'mg', '2')` | EA0109 |
| `('ordinary', 'levetiracetam', '250', 'mg', '1')` | EA0110 |
| `('ordinary', 'eslicarbazepine', '400', 'mg', '1')` | EA0132 |
| `('ordinary', 'brivaracetam', '50', 'mg', '2')` | EA0146 (**gold defect**) |
| `('ordinary', 'lamotrigine', '125'/'150', 'mg', '1'/'1'/'2')` | EA0166 (3 rows) |

Two structural facts about this residual:

1. **One gold defect is irrecoverable.** EA0146's gold annotation has
   `DrugName=Perampanel` but every other field (CUIPhrase, CUI, span text
   "Brivetiracetam-") resolves to brivaracetam (see `experiments/gold_data_issues.jsonl`,
   status `open`, surfaced in the Phase-0 pipeline audit). Under
   `canonicalize_medication_name` the gold key is `perampanel` while any
   defensible span-grounded prediction keys to `brivaracetam` — so this fact is an
   FP+FN *regardless* of extractor correctness. It accounts for 1 of the 6 FN and
   1 of the 10 FP. This is a gold-noise fact (the kind item 1's `/gold-noise` tab
   surfaces), not an extraction failure.

2. **The remaining residual is a deterministic lexicon/context limit, not a model
   gap.** The 5 recoverable FN (perampanel EA0117, sodium-valproate EA0131,
   lamotrigine EA0137/EA0197, midazolam rescue EA0158) and the 9 non-gold-defect
   FP are lexicon-coverage and multi-dose-clause-splitting issues in the
   deterministic rules — *exactly* the surface the LLM could in principle improve.
   The comparator doc shows the LLM-tuned arm *does not* recover these on dev140
   (it scores 0.9526, below deterministic 0.9615), and recovers only precision on
   full-200. **So the deterministic residual is the real ceiling on dev140, and
   the LLM does not clear it.**

## Implications for the manuscript

1. **Reframe the medication claim.** Prescription is a **deterministic-owned
   ceiling** (0.9615 dev / 0.9278 full), not an LLM extraction result. The
   manuscript must state the deterministic-only number alongside the headline and
   attribute the headline to the deterministic layer. Hiding this inherits dspy's
   "benchmark-inflation" critique; surfacing it preempts the critique.
2. **State the LLM's actual contribution precisely.** The LLM's medication value
   is a **full-200 precision effect** (FP 19→7), localized to non-AED comorbidity
   over-capture in the 60 test letters — not a headline contribution. Report it as
   such, not as "the LLM extracts medications."
3. **Match the dspy "isolated ceiling" methodology.** This probe establishes the
   pattern (dspy's E6 move) of separating "stacked baseline" from "isolated
   ceiling" for one family. The same probe shape extends to Investigations (where
   dspy found 90.4–96.7% near-ceiling) and to the SF candidate substrate —
   item 4's stated payoff of "the medication probe is the template; the larger
   ceiling-registry is the payoff."
4. **The gold defect is reportable, not fixable here.** EA0146 is a frozen-corpus
   gold-noise fact (item 1 territory); it bounds the achievable dev140 ceiling at
   ≤ (206−1)/(206−1+k). It should be cited as a known ceiling limit, not silently
   absorbed.

## Limitations and honest caveats

- **This is a single-family ceiling, not a system-wide claim.** "Deterministic
  owns the medication ceiling" does **not** generalize to Diagnosis, SF, or
  Investigations — those families have LLM-first contributions that this probe
  does not test. Each needs its own isolated-component ceiling (item 5's
  raw-vs-projected decomposition is the cross-family analogue).
- **`deterministic_only` is post-P7.** The extractor run here includes the
  2026-07-02 P7 multi-dose weight-context fix. The pre-P7 deterministic ceiling
  was 0.9386 dev / 0.9033 full (see comparator doc); the P7 fix is a deterministic
  rule improvement, not an LLM contribution. The headline statement
  ("deterministic owns the ceiling") holds pre- and post-P7; the *level* moved
  with the rule fix.
- **`clinical_headline` is the medication-specific clinical metric, not overall
  F1.** The cited 0.8680 full-200 *overall* (across all families) is not
  decomposed here — that is item 5's job. This probe is Prescription-only.
- **dspy's 100% is not directly commensurable.** dspy's oracle is
  annotation-derived (built from gold); ours is extractor-derived (run over text).
  We confirm the *framing* (deterministic owns it; LLM sits at-or-below) but not
  the literal 47/47 number — and we explain the difference (§Why not 100%).
- **Full-200 row-level inspection is aggregate-only** per claim_policy. The
  per-letter FN/FP decomposition is therefore dev140-only; full-200 is reported as
  aggregate tp/fp/fn.

## What this is NOT

- Not a claim that medications are "solved" — the deterministic ceiling is 0.96/0.93,
  with a traced residual including one irrecoverable gold defect.
- Not a claim that the LLM is useless for Prescription — it contributes full-200
  precision. It is a claim that the LLM does not contribute to the *headline*.
- Not a re-run of the hybrid lane. The cited hybrid numbers (0.9615 / 0.9278) are
  taken from the comparator doc as comparison anchors; this probe scores the
  deterministic-only surface fresh.

## Artifacts / Provenance

- Driver: `experiments/exectv2_medication_no_model_oracle_2026-07-06.py` (zero LLM
  calls; deterministic replay over gold text).
- JSON: `experiments/exectv2_medication_no_model_oracle_2026-07-06.json`
  (per-component + benchmark-projection scores for both surfaces, both splits;
  dev140 FN/FP decomposition with per-letter detail and key totals).
- Scorer: `score_prescription_components` / `score_prescription_benchmark_projection`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/prescription.py`)
  — the same scorers used for the hybrid lanes, no special-casing.
- Extractor: `_extract_prescriptions`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/prescription.py`).
- Comparison anchors: `docs/experiments/exectv2/prescription/exectv2_rx_llm_vs_deterministic_comparator_2026-07-03.md`
  (cited hybrid + LLM-tuned numbers, split-dependent inversion).
- Gold defect: `experiments/gold_data_issues.jsonl` (EA0146, status `open`).
- Umbrella: `docs/plans/predecessor_synthesis_followups_2026-07-06.md` (item 4).
- Split discipline: dev140 + full-200, both deterministic replay over gold text —
  no live predictions, no split risk. Cost: 0 LLM calls.
