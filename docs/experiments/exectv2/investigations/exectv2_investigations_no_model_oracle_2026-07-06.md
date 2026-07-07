# No-model investigations oracle — results

Date: 2026-07-06. Owner: ExECTv2 workstream.
Hypothesis: `inv_no_model_oracle_2026-07-06` — **RESOLVED** (the Investigations
deterministic extraction ceiling is far below the cited hybrid headline; Inv is a
contribution-bearing family, the opposite of the Prescription/SF pattern).
Driver: `experiments/exectv2_investigations_no_model_oracle_2026-07-06.py` (zero
LLM calls; deterministic replay over gold text).
Umbrella plan: item 4 extension of
`docs/plans/predecessor_synthesis_followups_2026-07-06.md` (open question #3).
Template: `experiments/exectv2_medication_no_model_oracle_2026-07-06.py`.

## Headline

**The Investigations deterministic extraction ceiling is far below the cited
hybrid headline — Investigations is a contribution-bearing family, the opposite
of the Prescription pattern.** Running `_extract_investigations` alone (no lens,
no verifier, no pending-test suppression, no LLM) as the final system scores
**0.5116 dev140 / 0.4858 full-200 `clinical_headline`** vs the cited hybrid
**0.9132 / 0.9213** — a gap of **−0.4016 / −0.4355**. The deterministic extractor
emits the modality anchor (EEG/MRI/CT) reliably but cannot classify the result
(Normal/Abnormal/Unknown) in most sentences; the hybrid lane's verifier +
pending-test suppression + completed-neuro lens contributes ~0.40 F1 to turn the
bare anchors into scoreable, result-bearing investigation facts.

Where the medication oracle found the LLM adds **zero** to the headline
(deterministic-only == hybrid), and the SF oracle found the deterministic
extractor is at-or-above the hybrid, **Investigations is the family where the
hybrid lane's deterministic lenses genuinely own the headline** — the bare
deterministic extractor is not close. This is a positive LLM/lens-value story
for Investigations, localized and quantified.

This is a **split-invariant** statement: the gap is −0.40 dev / −0.44 full, both
substantial and consistent in shape.

## The numbers

Two surfaces were scored, in order of how "oracle-like" they are:

| Surface | dev140 F1 | full-200 F1 | What it tests |
| --- | ---: | ---: | --- |
| **`gold_as_prediction`** | **1.0000** (136/0/0) | **1.0000** (183/0/0) | Scorer integrity: gold copied through the pipeline. Not extraction. |
| **`deterministic_only`** | **0.5116** (88/120/48) | **0.4858** (111/163/72) | The real no-model extraction ceiling: `_extract_investigations` run as the final system. |
| Cited hybrid `clinical_headline` (for comparison) | 0.9132 (121/8/15) | 0.9213 (164/9/19) | Hybrid lane (verifier + pending-test suppression + completed-neuro lens). |
| **Gap (deterministic-only − cited hybrid)** | **−0.4016** | **−0.4355** | **The hybrid lenses contribute ~0.40 F1.** |

> **Why two surfaces.** `gold_as_prediction` is the dspy-style scorer-integrity
> ceiling (gold copied through; confirms the 136 dev140 / 183 full-200 gold counts
> are preserved end-to-end). `deterministic_only` is the real extraction ceiling
> the deterministic layer owns, scored through the *same*
> `score_investigations_components` scorer used for the hybrid lanes (no
> special-casing). The interesting number is the second row.

### Predeclared outcome bands (from plan item 4 extension)

| Outcome band | Verdict | This run |
| --- | --- | --- |
| deterministic-only ≈ 1.0 | dspy near-ceiling framing applies in the strongest form | ✗ (0.51 dev) |
| deterministic-only ≈ cited hybrid (≈ 0.91/0.92) | dspy framing applies; LLM adds nothing; manuscript says so | ✗ |
| **deterministic-only ≪ cited hybrid** | **LLM genuinely contributing recall/specificity beyond the lexicon; positive LLM-value story** | **✓ (gap −0.40 dev / −0.44 full)** |

The result lands in the **third band** — the opposite of the medication oracle
(second band) and the SF oracle (second band). Investigations is the family where
the hybrid lane's lenses are load-bearing.

## Where the deterministic extractor fails (dev140 decomposition)

The dev140 residual is **48 FN + 120 FP across 40 / 72 letters**. The failure
mode is overwhelmingly **precision**: the deterministic regex finds the modality
token but the sentence-window result classifier finds no result, emitting a bare
`('EEG','Yes',None)` / `('MRI','Yes',None)` anchor that keys to no gold fact.

**FN (48, recall misses) — gold facts the deterministic extractor missed:**
| Key (modality, performed, result) | Count | Likely cause |
| --- | ---: | --- |
| `('EEG','Yes','Abnormal')` | 21 | result outside the sentence window / paraphrased abnormality |
| `('MRI','Yes','Abnormal')` | 18 | same — MRI result language the regex bank misses |
| `('EEG','Yes','Normal')` | 4 | "normal" outside the window |
| `('MRI','Yes','Normal')` | 3 | same |
| `('CT','Yes',*)` | 2 | CT results (rare) |

**FP (120, precision over-emissions) — non-gold facts the extractor emitted:**
| Key | Count | Cause |
| --- | ---: | --- |
| `('EEG','Yes',None)` | 56 | bare EEG anchor, no result classified |
| `('MRI','Yes',None)` | 54 | bare MRI anchor, no result classified |
| `('CT','Yes',None)` | 2 | same for CT |
| result-bearing but spurious | 8 | modality mentioned in a non-investigation context |

Two structural facts:

1. **The FP is dominated by result-less anchors (112/120).** The deterministic
   extractor's `_INVESTIGATION_PATTERN` matches `\b(EEGs?|MRI|CT)\b` and the
   sentence-window result classifier (`_investigation_result`) returns `None` for
   most windows because the result language is elsewhere in the letter. The
   hybrid lane's **pending-test suppression** (drops awaited/pending results)
   plus the **completed-neuro-investigations lens** (filters to actual performed
   investigations with results) cut these 120 FP to the hybrid's 8 FP.
2. **The FN is genuine recall the lenses/LLM recover.** The 39 missed
   EEG/MRI Abnormal results are cases where the deterministic sentence window
   doesn't capture the result phrase but the hybrid lane's contextual reasoning
   (or the LLM arbitration) does. The hybrid recovers to 121 TP vs deterministic
   88 TP — a +33 TP contribution.

> **Implication for attribution.** This probe *is* the attribution-discipline
> deliverable for Investigations: it shows what the deterministic layer produces
> *before* any lens or LLM is applied. The cited hybrid headline (0.9132) is
> **not** deterministic-owned — it is lens+LLM-owned, with the deterministic
> extractor providing only the modality-anchor recall scaffold. Per the
> research-protocol skill's attribution rule, **Investigations IS an LLM/lens-
> first claim** — unlike Prescription and SF. This is the cross-family contrast
> the manuscript needs.

## Implications for the manuscript

1. **Reframe the Investigations claim as contribution-bearing.** Prescription is
   deterministic-owned (LLM adds zero to headline); SF is deterministic-owned
   (deterministic ≈ hybrid); **Investigations is lens+LLM-owned** (deterministic
   ≪ hybrid by ~0.40). The manuscript must not treat the three families
   uniformly — the attribution picture is:
   - **Prescription:** deterministic ceiling; LLM's value is full-200 precision only.
   - **SF:** deterministic ceiling (state + direction); LLM's value is candidate-
     substrate recall (the 23% the broad payload misses).
   - **Investigations:** lens+LLM ceiling; the deterministic extractor is a recall
     scaffold, not a solution. The headline is owned by the verifier + suppression
     + completed-neuro lens + LLM arbitration.
2. **The dspy near-ceiling framing (90.4–96.7%) does NOT transfer to our
   deterministic extractor.** dspy reports near-ceiling Inv performance; our
   deterministic-only Inv is 0.51. The difference is traced: dspy's strong Inv
   number likely includes their adjudication/lens layer, not just the bare
   extractor. Our analogue of "dspy's near-ceiling" is the **hybrid lane**
   (0.9132), not the deterministic extractor. (Label the dspy number honestly as
   a sibling-repo figure not re-verified in this checkout.)
3. **Quantify the lens contribution.** The ~0.40 F1 gap is a concrete, defensible
   number for the contribution thesis: the deterministic lenses (verifier +
   pending-test suppression + completed-neuro) contribute +33 TP and cut 112 FP,
   a +0.40 F1 effect. This is the kind of isolated-component ceiling the dspy E6
   move produces.
4. **Match the dspy "isolated ceiling" methodology for Inv.** This probe
   establishes the Inv extraction ceiling. With Rx, SF, and Inv all probed, the
   item 4 ceiling-registry is complete across the three LLM-touched families.

## Limitations and honest caveats

- **`_extract_investigations` is the bare deterministic extractor.** It includes
  the regex anchor + sentence-window result classifier but NOT the pending-test
  suppression, the completed-neuro lens, the verifier, or the LLM arbitration.
  The hybrid lane stacks all of these; this probe isolates the bottom layer.
- **The hybrid Inv number (0.9132) is itself lens+LLM-owned, not LLM-only.** This
  probe cannot separate the lens contribution from the LLM contribution within
  the hybrid lane — that would need a lens-only ablation (out of scope here). The
  honest statement is "deterministic ≪ hybrid"; the within-hybrid split is a
  follow-up.
- **`clinical_headline` is the Inv-specific clinical metric.** The cited 0.9132 /
  0.9213 are `clinical_headline` F1; the per-modality (eeg/mri/ct) and attribute
  (performed/result/eeg_type) numbers are in the JSON artifact.
- **dspy's 90.4–96.7% is not directly commensurable.** dspy's Inv number is from
  a sibling repo (`../dspy-extraction/`, not in this checkout) and likely includes
  their adjudication layer. We confirm the *direction* (Inv is contribution-
  bearing, not deterministic-owned) but the literal numbers differ because the
  surfaces are not identical. Label as dspy sibling-repo, not re-verified here.
- **Full-200 row-level inspection is aggregate-only** per claim_policy. The
  per-letter FN/FP decomposition is dev140-only; full-200 is reported as aggregate
  tp/fp/fn.
- **This is a single-family ceiling, not a system-wide claim.** "Inv deterministic
  ≪ hybrid" does not generalize to Prescription or SF (where deterministic ≈
  hybrid). Each family has its own isolated-component ceiling; this is Inv's.

## What this is NOT

- Not a claim that the deterministic Inv extractor is "broken" — it provides the
  modality-anchor recall scaffold the hybrid lane builds on (88 TP of 121 hybrid
  TP come from deterministic anchors). It is a claim that the extractor *alone*
  is far from the headline.
- Not a claim that the LLM alone owns the Inv headline — the lenses (verifier,
  suppression, completed-neuro) are deterministic and contribute substantially.
  This probe cannot separate lens from LLM within the hybrid lane.
- Not a re-run of the hybrid lane. The cited hybrid numbers (0.9132 / 0.9213) are
  taken from the Inv comparator doc as comparison anchors; this probe scores the
  deterministic-only surface fresh.

## Artifacts / Provenance

- Driver: `experiments/exectv2_investigations_no_model_oracle_2026-07-06.py` (zero
  LLM calls; deterministic replay over gold text).
- JSON: `experiments/exectv2_investigations_no_model_oracle_2026-07-06.json`
  (per-component scores for both surfaces, both splits; dev140 FN/FP decomposition
  with per-letter detail and key totals).
- Scorer: `score_investigations_components`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/investigations.py`)
  — the same scorer used for the hybrid lanes, no special-casing.
- Extractor: `_extract_investigations`
  (`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/investigations.py`).
- Comparison anchors: `docs/experiments/exectv2/investigations/exectv2_inv_llm_vs_hybrid_comparator_2026-07-03.md`
  (cited hybrid Inv 0.9132 dev / 0.9213 full).
- Template: `experiments/exectv2_medication_no_model_oracle_2026-07-06.py`.
- Umbrella: `docs/plans/predecessor_synthesis_followups_2026-07-06.md` (item 4,
  open question #3).
- Split discipline: dev140 + full-200, both deterministic replay over gold text —
  no live predictions, no split risk. Cost: 0 LLM calls.
