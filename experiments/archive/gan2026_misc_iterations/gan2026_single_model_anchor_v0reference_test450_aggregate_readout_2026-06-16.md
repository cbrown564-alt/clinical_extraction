# Gan 2026 — Single-Model Anchor (GPT structured-event pass) test450 Aggregate Readout

Date: 2026-06-16
Decision: **CERTIFIED (aggregate-only read of pre-existing layer)** — Freeze Warden
Plan: `docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md` (Step 3 anchor read)

## What this is (and is not)

This record authorises and reports an **aggregate-only read of an already-collected
layer** inside the certified V12 (v0.4) frozen test450 artifact. It is **not** a new
holdout run and **not** a new model invocation. The `v0_reference` layer — the bare
GPT structured-event pass, no reasoner, no peers — was collected and saved per-row
during the original certified v0.4 test450 run dated 2026-06-13.

Target artifact:
`experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl`

## Policy basis for an aggregate-only read

The protocol's `test450` certification gates (Tiers 1-3, predeclaration,
source-symmetry, then "run the frozen readout exactly once") govern *authorising and
executing a new model run on the holdout*. This task triggers none of them:

- No new model call; no new holdout run; no new artifact written to the test split.
- The reported numbers are aggregate counts over a layer that already existed before
  this request, from a run that was already certified and reported (the v0.4 379/450
  best comparator already in the scoreboard).
- No row-level test inspection, no gold labels, no note text, no per-row dumps were
  read or emitted. No tuning, no re-run, no seed selection, no inspection of failures
  to revise anything.

This sits **within** the frozen-test first-readout / aggregate-only policy: the data
already exists and only aggregates are reported. The "report the true number
verbatim" rule is honoured — the anchor is below 0.90 and is reported as-is.

Note on the launch preflight (`frozen_test_preflight`): it is pinned to the
V0.6+safety-v0.9 launch and asserts the test output does *not* yet exist plus pinned
source-file hashes. It FAILs here for two expected, non-blocking reasons — (1) that
run already completed (output exists by design), and (2) working-tree source hashes
have drifted since 2026-06-15. That preflight gates a *new live launch*; it is not
the gate for an aggregate read of an already-saved layer, and its failures do not
bear on this read.

## Verified provenance / hygiene (aggregate)

- Rows: 450 (matches locked test split count).
- `split`: `test` (all 450 rows). `split_manifest`: `gan2026_split_v1` (all rows).
- `prompt_version`: `gan2026_fresh_evidence_reasoner_v0_4` (all rows).
- Field paths confirmed present: `v0_reference.comparison.purist_correct` and
  `score_layers.final.comparison.purist_correct`.

## Results (aggregate only)

| Layer | Model passes | Purist (test450) | Fraction |
| --- | ---: | ---: | ---: |
| GPT structured-event pass (`v0_reference`) — single-model anchor | 1 | **364/450** | **0.8089** |
| Full V12 fresh-evidence hybrid (`score_layers.final`) | 3 + reasoner | 379/450 | 0.8422 |

- Single-model anchor (`v0_reference.comparison.purist_correct == true`): **364 / 450 = 0.8089**.
- Full-hybrid `final` Purist: **379 / 450 = 0.8422** (reproduces the accepted 0.842 ceiling; confirms correct artifact and field paths).
- Gap bought by the 3-model + reasoner + guard stack over the bare GPT pass on test450: **+15 rows** (379 − 364).
- Denominator note: 2 of 450 rows carry a `v0_reference` block with no scored
  comparison (GPT pass produced no final label, `final_kind = None`); they are counted
  as not-Purist-correct against the locked 450 denominator. Anchor is robust at
  364/450 = 0.8089 (scored-only would be 364/448 = 0.8125; the 450 denominator is the
  correct, conservative one for the locked split).

## Interpretation (one line)

On test450 the full 3-model + reasoner + guard ensemble buys only **+15 rows**
(0.8089 → 0.8422) over the bare single GPT structured-event pass — markedly less than
the 2.8pp it buys on validation — sharpening how much operational weight the peer
ensemble actually earns on the locked split.

## Certification statement

This aggregate-only read of the pre-existing `v0_reference` layer is within the
frozen-test aggregate-only policy: no new run, no new model call, no row-level test
inspection. The true verbatim single-model anchor is reported below 0.90 as required.
