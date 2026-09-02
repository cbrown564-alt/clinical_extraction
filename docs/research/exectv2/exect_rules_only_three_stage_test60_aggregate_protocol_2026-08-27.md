# Protocol: ExECT rules-only three-stage `test60` aggregate replay

Date: 2026-08-27
Status: complete; Gate A and Gate B executed 2026-08-27
Development candidate: [three-stage reconstruction](exect_rules_only_three_stage_reconstruction_2026-08-27.md)
Frozen config: `ACCEPTED_THREE_STAGE_CONFIG` in
`orchestration/rules.py`
Report: [test60 aggregate replay](exect_rules_only_three_stage_test60_aggregate_2026-08-27.md)

## Primary question

What is the aggregate 4-family inventory micro F1 of the frozen
rules-only three-stage candidate (`ACCEPTED_THREE_STAGE_CONFIG`) on
locked `test60`, and how do family precision and recall move relative
to the cited comparator row (**0.7725**)?

This is one consumption of the holdout split. Family P/R expectations
below are declared before execution so the result cannot be reframed
after the number is seen.

## Frozen candidate and comparator

| Arm | Program | Identity |
| --- | --- | --- |
| Comparator | `run_letter` | Accepted 2026-08-27 retune stack: recall-first extract, Diagnosis encode, `RULES_ONLY_SELECT_RULE_IDS` Select. Cited five-cell rules row **0.7725** on `test60`. |
| Candidate | `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)` | Recognise ledger (D1 service-context exclusion, D2 secondary-to retention, D3 focal-onset alias), Diagnosis encode, ordered Select including `selection.sf_seizure_free_positive_count_drop` and `selection.inventory_weak_episode_drop`. Accepted on `dev140` at inventory F1 **0.9167** (P 0.926 / R 0.908) vs comparator **0.8949**. |

Zero model calls in both arms. Scorer:
`clinical_inventory_unit_keys`, 4-family micro F1. No
Compact/headline numbers.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Holdout split | `test60` (59 letters, locked) |
| Split loader | `test` via `load_letters_for_split("test")` |
| Row policy | `aggregate_only` |
| Development split | not scored in the public artifact except Gate A parity |
| Runs | Exactly one holdout execution per arm after Gate A |

Do not load, inspect, quote, or tune on `test60` rows before this
protocol executes. Do not change `ACCEPTED_THREE_STAGE_CONFIG` between
Gate A and Gate B.

## Predeclared family precision / recall expectations

These are the binding predictions. They are not pass/fail thresholds;
they constrain how the result may be read afterward.

### Comparator baseline (locked, inventory F1 on current `run_letter`)

| Family | F1 | Role in the gap |
| --- | ---: | --- |
| Diagnosis | 0.8550 | Not the historical weak family on holdout |
| SeizureFrequency | 0.5899 | Binding weakness vs cell 3 **0.8082** |
| Prescription | 0.8395 | Mid band |
| Investigations | 0.8706 | Mid band |
| **Overall** | **0.7725** | Cited five-cell rules row |

Cell 3 reference on the same split (Gemini recognise + inventory
Select, not a ruleset-matched counterfactual): overall **0.8674**;
SeizureFrequency recall **0.7973** vs rules comparator recall in the
**0.54** band (headline-era measurement in the brief).

### Expected direction by family (candidate minus comparator)

| Family | Predeclared P/R direction | Mechanism | Expected magnitude |
| --- | --- | --- | --- |
| **Diagnosis** | Both P and R rise; precision gain ≥ recall gain | D1 drops administrative generic `epilepsy`; D2 retains secondary-to left side; D3 adds focal-onset aliases. Dev140: F1 **0.8257 → 0.8765**, FN 59→45, FP 55→35. | F1 rise **≥ +0.02**. Remains competitive with cell 3 Diagnosis **0.8432**. |
| **SeizureFrequency** | Remains the binding holdout weakness; at most modest lift | Dev140 gain was **+0.008** only (FP 26→23). Named-type promotion and nested-ancestor promotion were rejected and stay off. Holdout hole is recall-shaped, not fixed by the accepted candidate. | F1 rise **≤ +0.03**; family F1 likely stays **below 0.70** and well below cell 3 **0.8082**. Recall gap vs cell 3 remains the headline story unless this band is exceeded. |
| **Prescription** | Neutral | No candidate component touches Prescription. | \|ΔF1\| **≤ 0.01**. |
| **Investigations** | Neutral | Per-occurrence extract already landed in the retune; three-stage adds no Inv rule. | \|ΔF1\| **≤ 0.01**. |
| **Overall** | F1 rises; recall-biased improvement | Dev140 overall **+0.022** with balanced P/R (+0.027 / +0.017). Historical holdout gap vs cell 3 was recall-heavy (~0.75 R band vs ~0.86). | F1 **> 0.7725** (must beat comparator given dev140 gates). F1 likely **< 0.8674** unless SeizureFrequency exceeds the **+0.03** band above. A Diagnosis-only lift does **not** close the method-comparison gap. |

### Post-hoc framing rules (predeclared)

- If overall F1 rises but SeizureFrequency stays below **0.70**, report
  the reconstruction as partially validated: Diagnosis/Select
  mechanisms transfer; SF holdout weakness remains untested by this
  candidate.
- If overall F1 stays near **0.7725**, do not attribute it to scorer
  mismatch; investigate Gate A parity first.
- If overall F1 approaches cell 3 **0.8674**, require SeizureFrequency
  to exceed the **+0.03** band; otherwise treat the overall move as
  Diagnosis-heavy and not a parity claim.
- Do not inspect holdout rows to explain any family move. Do not start
  a holdout retune from this replay.

## Gate A — development parity (precondition)

`test60` is not touched until Gate A passes on current HEAD.

Re-run `scripts/measure_exect_rules_only_three_stage_dev140.py` and
confirm:

| Target | Value |
| --- | ---: |
| Comparator inventory F1 | 0.8949 |
| Candidate inventory F1 | 0.9167 |
| Comparator-exact regressions | 0 |
| `config_for(CANDIDATE_COMPONENTS) == ACCEPTED_THREE_STAGE_CONFIG` | true |

**Gate A passes** if all four match exactly.

**If Gate A fails**, do not run Gate B. Diagnose on `dev140` only and
write a fresh predeclaration for whatever configuration is then
proposed.

## Gate B — holdout execution

One paired run: comparator `run_letter` and candidate
`run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)` on all 59 test
letters.

Row-level outputs go to
`scratch/holdout/exect_rules_only_three_stage_test60_20260827/` and
are sealed (path, `sha256`, byte count only in the public artifact).
The public artifact contains aggregates only: overall and per-family
P/R/F1 for both arms, deltas, and the predeclared expectation table
above by reference.

Before citing the result:

- `scripts/check_locked_aggregate_safety.py` is extended with the new
  public artifact path and must pass.
- No letter id, note text, prediction, or failure case from `test60`
  appears in committed files or status prose.

## What this result may and may not support

May support:

- An aggregate-only replacement for the cited rules row **0.7725** if
  the project owner promotes it through the five-cell grid owners.
- A descriptive statement that the three-stage reconstruction raised
  or failed to raise holdout inventory F1, with family P/R read
  through the predeclared table.
- Updating `paper_experiments/exect/exect_rules/test60.json` and the
  Gemini five-cell grid rules cell when promoted.

May not support:

- A claim that rules-only matches cell 3 unless overall F1 and the
  SeizureFrequency band both support it.
- Row-level holdout mechanism, holdout retune, or revision of the
  Gemini cell 3 stack.
- Mixing headline/Compact F1 with inventory F1 in the same sentence.

## Claim boundary

Aggregate holdout evidence for one frozen development candidate.
Not clinical validation. Not a six-model roster fill. The comparator
**0.7725** remains cited until this protocol completes and an owner
promotes the new aggregate.
