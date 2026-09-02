# Gan rules-only three-stage Phase B: recall-first provisional producers

Date: 2026-08-29
Protocol: [three-stage protocol](gan_rules_only_three_stage_protocol_2026-08-29.md)
Phase A: [instrumentation result](gan_rules_only_three_stage_phase_a_2026-08-29.md)
Taxonomy audit: [rule taxonomy audit](gan_rules_taxonomy_audit_2026-08-29.md)
Artifacts: `experiments/gan2026_rules_only_three_stage_20260829/`
(`dev750_recall_first_summary.json`, `dev750_recall_first_rows.jsonl`,
`rule_inventory.json`)
Script: `scripts/measure_gan_rules_only_recall_first_dev750.py`

Dataset `dev750` (development, row review permitted); Purist scorer via
`score_label`; zero model calls; `test450` never loaded. Program:
`run_record_three_stage(GanThreeStageConfig(provisional_classes=ALL_PROVISIONAL_CLASSES))`
with comparator `run_record(architecture="rules")`.

Vocabulary note: mid-phase the project renamed the first stage from
"recognise" to "find" repo-wide (user decision, adopted 2026-08-29).
Phase A artifacts retain the old key names; this phase and all code use
"find".

## Gate B: held

With all seven provisional classes enabled, the select stop is label-
and evidence-identical to `run_record` on all 750 records, the
competition pool is unchanged on every record, and the select stop
reproduces the cited rung 669/750. Provisional candidates are dropped
by the Select gate (`select.provisional_unsupported_drop`) before
competition, so this holds by construction; the script asserts it
anyway.

## Result: find ceiling 681 → 709 (+28 of the 69 recall-gap rows)

| Measure | Phase A | Phase B (provisional enabled) |
| --- | --- | --- |
| find stop (Purist) | 600/750 (0.8000) | 622/750 (0.8293) |
| encode stop | 600/750 | 622/750 (still zero delta over find) |
| select stop | 669/750 (0.8920) | 669/750 — unchanged (gated) |
| wide-ledger oracle | 681/750 (0.9080) | **709/750 (0.9453)** |

The find stop rises because provisional candidates compete for the
document-order pick; encode remains fused (provisional builders emit
designed-form labels, like every other producer).

## Per-class ledger (Phase C decision input)

Rescue = row where a class supplies a Purist-correct label that no
non-provisional wide-ledger candidate supplies. Exposure = rows where
the class fires but the select stop is already correct (a naive keep
could regress them, since e.g. `unknown` sits atop the select priority
ladder).

| Class | Fired on rows | Rescues | Exposure | History flag |
| --- | ---: | ---: | ---: | --- |
| `provisional.trigger_conditioned_unknown` | 16 | 8 | 7 | — |
| `provisional.electrographic_hourly_rate` | 5 | 5 | 0 | — |
| `provisional.nightly_narrative_rate` | 5 | 5 | 0 | **G1 Candidate A killed on holdout (−1 test450)** |
| `provisional.non_epileptic_current_free` | 3 | 3 | 0 | G2 Candidate B (+1 dev, holdout inert) |
| `provisional.vague_multiple_rate` | 6 | 3 | 3 | — |
| `provisional.single_dated_event_unknown` | 2 | 2 | 0 | — |
| `provisional.monthly_cluster_unclear_count` | 4 | 2 | 2 | — |

All 28 rescues are unique (no row rescued by two classes). Four classes
are surgical (zero exposure); the other three need evidence gates in
Phase C before any keep.

## Development method and its limits

Producers were derived by reading the 69 permitted recall-gap rows
(development split). One widening iteration was applied after the first
measurement (initial ceiling +17): quantifier/window vocabulary for
vague counts, provoked/triggered-by and catamenial forms for
trigger-conditioned statements, and the bursts/runs-of-events monthly
idiom for clusters. Rows skipped deliberately:

- the ~13 protected benchmark shorthand rows (`sz X7/mo`, `qtwo -
  threewk`, …) — contract rows, never hand-tuned;
- one-off narrative paraphrases with no visible pattern class (e.g.
  buried "reduced significantly on <date>" arithmetic, "no generalised
  seizures since <date> though brief jumps continue" span arithmetic).

Remaining recall gap after Phase B: 41 of 750 rows (69 − 28). This is
dev-fitted recall work by design; the anti-overfitting reckoning is the
frozen-candidate aggregate-only `test450` replay in Phase D.

## Claim boundary

Development ceiling evidence only. The cited five-cell rows (0.71
holdout select, 0.892 dev select) are unchanged; no keep decisions have
been made; nothing here is benchmark or holdout evidence.

## Next (Phase C)

Per-class keep decisions through the Select gate: promote a class from
`provisional_unsupported_drop` to competition only with an evidence
gate that spares its exposure rows, measured one class at a time
against the frozen Phase B baseline. The two history-flagged classes
require an explicit argument for why their prior holdout outcome does
not bind (changed mechanism: gated competition vs. direct extraction).
