# Results: Gan rules-only three-stage Phase A (score-neutral instrumentation)

Date: 2026-08-29
Protocol: [three-stage protocol](gan_rules_only_three_stage_protocol_2026-08-29.md)
Brief: [reconstruction brief](gan_rules_only_three_stage_reconstruction_brief_2026-08-29.md)
Artifact: `experiments/gan2026_rules_only_three_stage_20260829/`
(`dev750_summary.json`, `dev750_rows.jsonl`)
Split: `dev750` only; `test450` never loaded. Zero model calls.
Scorer: Purist accuracy via the existing `score_label`; Pragmatic secondary.
Comparator: living `run_record(architecture="rules")`, the promoted
five-cell rules row.

## Gates (all met on 750/750)

- **A1 identity:** three-stage select label AND evidence identical to
  `run_record` on every record; select stop reproduces the cited rung
  exactly (**669/750 = 0.892**).
- **A2 relocation identity:** the surviving competition pool is
  identical to the comparator's post-prune candidate list on every
  record. The relocated drops (duplicate 304, historical-rate 23,
  contained-fragment 4) reproduce extract-time pruning exactly.

Program: `run_record_three_stage` in
`src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/three_stage.py`;
measurement `scripts/measure_gan_rules_only_three_stage_dev750.py`;
tests `tests/test_gan2026_three_stage.py`.

## Stage stops under the predeclared stop policy

Find/encode = document-order-first pick over the wide pre-drop
ledger (raw / normalized label); select = submitted final label.

| Stop | Purist | Pragmatic |
| --- | ---: | ---: |
| find | **0.8000** (600/750) | 0.8373 |
| encode | **0.8000** (600/750) | 0.8373 |
| select | **0.8920** (669/750) | 0.9053 |
| oracle ceiling (pool) | **0.9080** (681/750) | — |
| oracle ceiling (wide, incl. dropped) | 0.9080 (681/750) | — |

The published flat rules row hides a real gradient: selection adds
**+0.092** over a neutral document-order pick. The encode stop adds
exactly zero — label repair never changes a document-order pick's
correctness on `dev750` — which measurably confirms the brief's
diagnosis that encoding is fused into the find builders (labels
are already in designed form at match time). The wide and pool oracles
are identical: the relocated drops discard **zero** Purist-correct
candidates; extract-time pruning is precision-pure on development.

## Residual partition (81 select-wrong rows)

- **12 rows Select headroom** (a Purist-correct candidate survives in
  the pool but loses competition):
  - 4 rows are the G5 mode-1 signature: gold `unknown`, a
    subtype/negation reading wins as `seizure free ...`
    (`current_seizure_free` or `generic_seizure_free`) while an
    `unknown` candidate sits in the pool (rows 11216, 11254, 11259,
    11272). A Select scope gate on seizure-free support is the target.
  - 8 rows are rate competition: `frequency_monthly_rate` tie-break
    prefers the highest monthly rate and picks the wrong statement
    (e.g. row 10386 gold `1 cluster per week, 2 to 3 per cluster`
    loses to `1 per day`; row 13209 gold `1 per 8 month` loses to
    `1 per 4 to 5 week`).
- **69 rows recall gap** (no Purist-correct normalized label anywhere
  in the wide ledger):
  - 23 nothing recognised at all (fallback `no reference` submitted);
  - 11 a candidate overlaps the gold evidence but carries the wrong
    label — encode-shaped failures inside the builders;
  - 35 candidates recognised elsewhere in the letter only — the gold
    statement never matched any rule.
  - Top confusions: gold `unknown` answered as seizure-free (13 rows
    — mode-1 mass that is *not* Select-rescuable because no `unknown`
    candidate was produced), gold `multiple ...` answered as
    no-reference (8 rows).

So the G5 expectation is revised with instrumented numbers: Select
headroom on the living gold is small (12 rows, ceiling 0.908);
**recall is the dominant residual (69 rows, 85%)**, and 13 of the
G5-mode-1 rows actually need a find-side `unknown`/hedge
producer, not a Select gate.

## Compact stage taxonomy (measured, not per-rule)

| Mechanism | Locked-stage role | Phase A status |
| --- | --- | --- |
| Rule builders writing codebook labels at match time | find + encode fused | measured: encode delta zero; split deferred to Phase B |
| `RuleSpec.exclude` predicates (9 rules) | select interleaved in find | recorded as span-level exclusion records (71 suppressions; `seizure_free.generic_duration_or_since` 31, rate rules 40) |
| Inline distractor suppression in `extract_rate_candidates` (non-`RuleSpec` regexes) | select interleaved in find | not yet recorded; Phase B target |
| `dedupe_candidates` / fragment / historical pruning | select | relocated to tagged Select drops, identity-gated |
| Priority ladder + evidence cues (`deterministic_selection.py`) | select | unchanged; now the sole owner of competition |
| `repair_prediction_label` + parse fallback | encode | unchanged; measured no-op on doc-order picks |

A full per-rule taxonomy audit (ExECT-style) remains open and is the
Phase B prerequisite.

## Attribution and claim boundary

Development instrumentation result on `dev750` only. Nothing semantic
changed: both gates hold on all 750 records, so the cited five-cell
rows (`test450` 0.71, `dev750` 0.892) are untouched, and the stage
gradient is a property of the living program, not a new candidate.
The stop policy was predeclared (with one pre-measurement amendment
recorded in the protocol) and implemented as declared.

Known limits: the recall/headroom partition uses normalized labels, so
builder-encode errors count as recall gap by construction (the 11
wrong-label-on-gold-evidence rows bound that conflation); the
gold-evidence overlap check is substring-based and approximate;
pre-existing unrelated test failures in the tree (stage-manifest
`docs/paper/methods.md` owner, stale generated architecture docs,
paper-runner `temperature` keyword) were verified present without
these changes.

## Next actions

1. **Phase B (find recall):** per protocol — start from the 23
   nothing-recognised and 35 recognised-elsewhere rows; add tagged
   provisional producers (narrative rates, hedge/`unknown` surfaces
   for the 13 gold-`unknown` rows) with the select stop held
   mention-identical; the nine protected shorthand rows stay unfixed.
   Requires the per-rule taxonomy audit first.
2. **Phase C (Select):** the 4-row seizure-free scope gate and the
   8-row rate-competition order, under isolated-positive /
   leave-one-out / zero-regression acceptance.
3. Wiring stage stops into `_gan_grid` waits for Phase D promotion;
   the dissertation table is unchanged until then.
