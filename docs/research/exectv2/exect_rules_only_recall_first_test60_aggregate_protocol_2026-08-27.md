# Protocol: ExECT rules-only recall-first `test60` aggregate stage-rung replay

Date: 2026-08-27
Status: complete; Gate A and Gate B executed 2026-08-27
Report: [replay results](exect_rules_only_recall_first_test60_aggregate_2026-08-27.md)
Development candidate: [recall-first restructure results](exect_rules_only_recall_first_restructure_2026-08-27.md)
Frozen config: `RECALL_FIRST_THREE_STAGE_CONFIG` in `orchestration/rules.py`
Runner: `scripts/measure_exect_rules_only_recall_first_test60_aggregate.py`

## Primary question

Does the frozen recall-first restructure candidate
(`RECALL_FIRST_THREE_STAGE_CONFIG`) transfer to locked `test60`:
aggregate 4-family inventory micro F1 at the select stop versus the
promoted comparator row (**0.8018**), with recognise/encode/select
stage rungs reported aggregate-only?

This is one consumption of the holdout split. Family expectations
below are declared before execution so the result cannot be reframed
after the number is seen.

## Frozen candidate and comparator

| Arm | Program | dev140 select F1 |
| --- | --- | ---: |
| Comparator | `run_letter` = `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)`; cited `test60` row **0.8018** | 0.9167 |
| Candidate | `run_letter_three_stage(RECALL_FIRST_THREE_STAGE_CONFIG)`: all recall-first classes emitted as tagged direct at recognise; Select keeps heading decomposition unconditionally and SF state variant / Rx recall expansion / Inv result variant conditionally; every other recall-first class dropped by `selection.recall_first_unsupported_drop` | 0.9266 |

Zero model calls in both arms. Scorer: `clinical_inventory_unit_keys`,
4-family micro F1 plus per-family P/R/F1 at the recognise, encode, and
select stops (candidate) and the select stop (comparator).

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Holdout split | `test60` (59 letters, locked) |
| Split loader | `test` via `load_letters_for_split("test")` |
| Row policy | `aggregate_only` |
| Runs | Exactly one holdout execution per arm after Gate A |

Do not load, inspect, quote, or tune on `test60` rows before this
protocol executes. Do not change `RECALL_FIRST_THREE_STAGE_CONFIG`
between Gate A and Gate B.

## Predeclared expectations

Comparator baseline on `test60` (locked, from the three-stage replay):
overall **0.8018** (P 0.8494 / R 0.7593); Diagnosis 0.8478,
SeizureFrequency 0.6131, Prescription 0.8395, Investigations 0.8837.

Dev140 deltas of the candidate vs comparator (select stop): overall
F1 +0.0099 (P −0.0007, R +0.0203); Diagnosis +0.0076, SF +0.0170,
Prescription +0.0074, Investigations +0.0112.

### Expected direction by family (candidate minus comparator, select stop)

| Family | Predeclared direction | Mechanism | Expected band |
| --- | --- | --- | --- |
| **Diagnosis** | Recall up slightly, precision ~flat | Only the heading-decomposition keep reaches Select; it fires on qualified epilepsy heading grammar, which is letter-format-shaped and present on both splits. | ΔF1 in **[0, +0.03]** |
| **SeizureFrequency** | Modest recall lift; remains the binding weakness | Conditional state-variant keep (typo'd GTC anchor, plural "seizures free", reported cluster events). Dev gain +0.017 came from 5 letter-specific surface variants; holdout density of such variants is unknown. | ΔF1 in **[0, +0.04]**; family F1 likely stays **below 0.70** |
| **Prescription** | Recall up or flat; this family is the lexical-vs-distributional test | The conditional Rx keep includes the external ASM lexicon and typo tolerance built blind to holdout. If the holdout 0.80 recall gap is lexical, recall rises more than the dev +0.015; if distributional, it stays flat. | ΔF1 in **[−0.01, +0.05]**; ΔR **≥ −0.01** |
| **Investigations** | Small lift or flat | Conditional result-variant keep (test-event assertions only). | ΔF1 in **[−0.01, +0.03]** |
| **Overall** | F1 rises, recall-biased | Dev +0.0099 F1 with +0.0203 R at flat P. | ΔF1 in **[0, +0.03]**; candidate F1 expected **> 0.8018** |

### Stage-rung expectations (candidate, aggregate-only)

Recognise-stop overall recall expected in **[0.88, 0.97]**
(dev 0.9677; holdout lexical gaps may cut it). Recognise precision
expected low (dev 0.53 band) by design; encode ~= recognise; the
select stop must carry all precision recovery.

### Post-hoc framing rules (predeclared)

- If overall ΔF1 < 0, the recall-first restructure is reported as
  dev-only mechanism evidence; the cited row stays 0.8018 and no
  holdout retune starts from this replay.
- If Prescription recall rises ≥ +0.03, the holdout Rx gap is reported
  as (at least partly) lexical; if it stays within ±0.01, distributional.
- Do not inspect holdout rows to explain any family move.
- SF F1 below 0.70 keeps "SF holdout weakness" as the standing
  limitation regardless of the overall move.

## Gate A — development parity (precondition)

Re-run `scripts/measure_exect_rules_only_recall_first_dev140.py
phase_c_candidate` on current HEAD and confirm:

| Target | Value |
| --- | ---: |
| Candidate select F1 | 0.9266 |
| Comparator-exact regressions | 0 |
| Candidate arm config is `RECALL_FIRST_THREE_STAGE_CONFIG` | true |

If Gate A fails, do not run Gate B.

## Gate B — holdout execution

One paired run on all 59 test letters. Row-level outputs are sealed
under `scratch/holdout/exect_rules_only_recall_first_test60_20260827/`
(path, `sha256`, byte count only in the public artifact). The public
artifact
(`experiments/exect_rules_only_recall_first_test60_aggregate_20260827.json`)
contains aggregates only: candidate stage rungs, comparator select
scores, deltas. `scripts/check_locked_aggregate_safety.py` is extended
with the new artifact path and must pass. No letter id, note text,
prediction, or failure case from `test60` appears in committed files.

## Claim boundary

Aggregate holdout evidence for one frozen development candidate. Not
clinical validation. The comparator **0.8018** remains cited until an
owner promotes the new aggregate.
