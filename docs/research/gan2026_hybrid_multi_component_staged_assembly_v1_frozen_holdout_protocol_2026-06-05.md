# Gan 2026 Hybrid Multi-Component Staged Assembly V1 Frozen Holdout Protocol

Date: 2026-06-05

Status: frozen protocol addendum before any `test450` execution. This document
does not itself authorize a locked-test run; explicit user authorization is
still required after the validation freeze gate is reviewed.

## Purpose

This addendum freezes the holdout-facing audit protocol for
`hybrid_multi_component_staged_assembly_v1`. It exists to keep the Gan 2026
locked test split as a final holdout surface rather than another development
surface.

The audit, if authorized, is an aggregate-only local holdout generalisation
readout under `gan2026_split_v1`. It is not a benchmark-comparable result and
does not authorize row-level test failure review, prompt/rule tuning, repair
policy changes, projection changes, boundary/renderer changes, action-policy
widening, or threshold edits.

## Frozen Candidate Identity

| Field | Frozen value |
| --- | --- |
| Candidate version | `hybrid_multi_component_staged_assembly_v1` |
| Candidate artifact stem | `gan2026_hybrid_multi_component_staged_assembly_v1` |
| Pipeline family | `hybrid` |
| Mode for validation evidence | saved replay |
| Holdout mode if authorized | frozen aggregate-only audit |
| Split manifest | `gan2026_split_v1` |
| Locked test rows | 450 |
| Comparator | `rules_only_v1` |
| Control candidate | `gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate` |
| Repo commit at protocol freeze | `2989f278e6197b70c588587a4165757089476c80` |
| Working tree at protocol drafting | dirty: `PROJECT_STATUS.md` already contained staged-project status edits before this addendum; this protocol remains uncommitted until the current documentation changes are committed |

If code, prompts, scorer policy, split manifests, or any source artifact below
changes before authorization, this protocol is no longer frozen and must be
reissued with new hashes.

## Frozen Policy Ids

| Policy area | Frozen id |
| --- | --- |
| Repair policy | `h5_repair_policy_v1` |
| Boundary policy | `seizure_free_boundary_event_v0` |
| Renderer policy | `benchmark_convention_renderer_v0` |
| Safety floor | `selective_safety_floor_gate_v0` |
| Release policy | `untagged_nonprediction_release_candidate_v0` only |
| Action policy | `staged_action_policy_v1` |
| Action sidecars | `h9_action_summary_sidecar_v1`, `h9_release_lane_ablation_v1`, `h6_control_replay_v1` |
| Provenance sidecar | `h10_raw_identity_sidecar_v1` for saved replay; Stage 5 runtime expansion remains deferred unless live calls are introduced |
| Rejected behavior | trigger-context release, last-event automatic release, broad structured projection port, broad action-policy widening |

No live model calls are part of this frozen saved-replay protocol. If a future
holdout run introduces live calls, the model id, prompt versions, raw-output
capture policy, H10 runtime provenance, call telemetry, and drift controls must
be frozen in a new protocol before execution.

## Source Artifact Hashes

| Source artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `data/Gan (2026)/splits/gan2026_split_v1.json` | 23621 | `c5f512d8744261916bd6d92562430489a3ba0494b0bf7c6575bfaa9e58680143` |
| `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json` | 2629 | `707565ee53c4b36ba69700ebbbe111cee8d841532c1837314a3c4ed712c681a4` |
| `experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.jsonl` | 59249 | `d77d79b572fbf132591575adaa8e71a7a948c42bfe4b0a057cbadaf5e26dd096` |
| `experiments/gan2026_h10_raw_identity_sidecar_v1_2026-06-05.json` | 5308 | `eb80c025ecaeaa7cd2db55c15bb7fd17b74471e4f51f5adfac0bbed99e643029` |
| `experiments/gan2026_h5_repair_policy_v1_manifest_2026-06-05.json` | 3824 | `03ea85ff4464fdc2562e583a776be7331710ea77e9f215b392dce85e560df4e4` |
| `experiments/gan2026_h6_control_replay_v1_2026-06-05.json` | 2185 | `67e23cc0b164d980a31add1f0399a3a1e5bc2498b98fd22e11ac32194ce96e08` |
| `experiments/gan2026_h9_action_summary_sidecar_v1_2026-06-05.json` | 5096 | `457d2b8ed102a268eafa6d4b76c8367d848089fb136ee953cc9dbb7d32360c70` |
| `experiments/gan2026_h9_release_lane_ablation_v1_2026-06-05.json` | 2208 | `73c309d655913bb65b0cb0949c5b6e16da2f2f44a80e28543356912da6cd38a5` |
| `experiments/gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05.json` | 3515 | `eeb320fea5fc11e0b492683dc260bda8a36fcf648c7d1f17f4d58953dfc31c3e` |
| `experiments/gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05.jsonl` | 1186393 | `e7204ff4d7a3a45c4c5c3fba6a8fc0c07ea1e94f45f92e6c3bd1e2d7775553c6` |
| `experiments/gan2026_hybrid_multi_component_staged_assembly_v1_validation750_component_matrix_2026-06-05.csv` | 210520 | `c9c293a2340ad4997ce42bea9df3becf6187cf3610614b5e334a0b42f4e4252a` |
| `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.json` | 2217 | `b335d7fc89e02a856cc99f030b99de04c01d33c34d90c27cc3599aac1001db87` |
| `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.jsonl` | 1147084 | `c49f1dec64631dbd54789b7d9cb6a20998cea4773a8a2b6d02a5b2cc1de7de00` |

## Validation Freeze Gate

The following validation750 gate is the evidence basis for requesting holdout
authorization:

| Gate | Frozen validation result |
| --- | ---: |
| Rows assembled exactly once | 750/750 |
| Unique source rows | 750/750 |
| Prediction-bearing rows | 735 |
| Abstain rows | 9 |
| Human-review rows | 6 |
| H6 member rows | 37 |
| H6 regressions | 0 |
| Boundary/renderer selected rows | 28 |
| Boundary/renderer suppressed rows | 2 |
| Release-applied rows | 19 |
| Component-matrix contract issues | 0 |
| Final-row contract issues | 0 |

This gate must be reviewed before authorization. If any reviewer finds that a
gate has failed or that a required source artifact has drifted, do not run
test450.

## Allowed Holdout Command

If explicitly authorized, the holdout audit must use the frozen candidate and
protocol:

```bash
python -m clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.staged_assembly_v1 \
  --split test \
  --mode frozen \
  --candidate-version hybrid_multi_component_staged_assembly_v1 \
  --protocol docs/research/gan2026_hybrid_multi_component_staged_assembly_v1_frozen_holdout_protocol_2026-06-05.md \
  --output-dir experiments/
```

The run must not add a live-call dependency or read a row-level locked-test
failure artifact. Any operational row file required solely for scoring must not
be inspected for development decisions and must not be used as the public report.

## Allowed Public Holdout Outputs

The public holdout report may contain only aggregate or predeclared-slice
summaries:

- overall Purist exact-label aggregate;
- overall Pragmatic aggregate;
- test row count;
- prediction-bearing coverage and action counts;
- aggregate abstain, human-review, monitor, and predict counts;
- component-owner aggregate counts;
- boundary/renderer selected and suppressed aggregate counts;
- release-lane aggregate counts;
- H6 aggregate W->C/C->W/readout counts where computable by the frozen plan;
- evidence-status, source-id validity, schema validity, parse validity, and
  issue-count aggregates;
- predeclared hidden-family aggregate counts using family definitions already
  present in validation artifacts or source metadata before the test run;
- cost, latency, and call telemetry only if a separately frozen live-call
  protocol is created.

Expected public artifacts, if authorized, are:

```text
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_test450_aggregate_2026-06-05.json
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_test450_aggregate_2026-06-05.md
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_test450_component_summary_2026-06-05.csv
```

## Disallowed Holdout Outputs And Actions

The audit must not produce or use any of the following for development:

- row-level locked-test failure review;
- row ids in the public test report;
- clinical note text, gold labels by row, raw model outputs by row, or row-level
  error records in the public test report;
- new test-derived slice definitions;
- prompt, model, scorer, parser, repair, projection, boundary, renderer,
  safety-floor, release, action-policy, or threshold changes from test outcomes;
- revisions to `gan2026_split_v1`;
- benchmark-comparable claims;
- selection among multiple candidate branches based on test450 outcomes.

If the test result is poor, record it as final-evaluation evidence. Any fix
starts a new validation-only development cycle and requires a clearly separated
future holdout protocol.

## Interpretation Language

Allowed language after a compliant authorized run:

- local frozen holdout result;
- aggregate-only test450 generalisation audit;
- component-owner aggregate readout under `gan2026_split_v1`;
- validation-developed candidate evaluated once on locked holdout.

Disallowed language:

- benchmark result;
- replicated Gan 2026 benchmark;
- production-ready model;
- LLM-superior whole-pipeline claim;
- proof that boundary/renderer closes the aggregate validation-test gap.

## Authorization Record

Authorization status: not yet authorized.

Before running test450, record a dated user authorization entry here or in
`PROJECT_STATUS.md` that names this exact protocol path and confirms that the
run is aggregate-only under the prohibitions above.
