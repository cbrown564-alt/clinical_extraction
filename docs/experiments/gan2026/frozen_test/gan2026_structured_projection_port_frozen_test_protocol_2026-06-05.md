# Gan 2026 Structured Projection Port Frozen Test Protocol

Date: 2026-06-05

## Purpose

This protocol freezes an explicitly user-authorized locked-test audit for
`structured_validation_projection_port_panel_v0`.

The validation port panel remains below the original promotion gates:

| Validation metric | Value |
| --- | ---: |
| rows | 47 |
| hard rows | 23 |
| matched controls | 23 |
| no-regression rows | 1 |
| W->C rows | 23 |
| C->W rows | 0 |
| parse-ok plus exact-evidence rate | 1.0000 |

The user explicitly authorized promotion on 2026-06-05 despite the coverage and
W->C gate failures. This waiver permits one frozen aggregate-only locked-test
audit. It does not authorize benchmark-comparable language, scorer changes,
test row-level tuning, or repeated holdout iteration.

## Frozen Claim Language

Any result under this protocol must be described as:

- a user-authorized frozen holdout audit of a validation-developed structured
  projection-port mechanism;
- a local final-holdout or local replication-proxy readout, depending on the
  exact scoring surface reported;
- a saved-artifact, no-new-call audit over previously materialized test packets;
- not a benchmark-comparable result.

## Frozen Inputs

- Repo commit at protocol freeze: `c3b0216`
- Split manifest: `data/Gan (2026)/splits/gan2026_split_v1.json`
- Split manifest SHA-256:
  `c5f512d8744261916bd6d92562430489a3ba0494b0bf7c6575bfaa9e58680143`
- Locked-test source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`
- Locked-test source artifact SHA-256:
  `98858a823ecfb0b2884cbd0a1adda7c218c4eb16c6c409a31f443509cb999a72`
- Validation port panel:
  `experiments/gan2026_structured_validation_projection_port_panel_v0_2026-06-05.json`
- Validation port panel SHA-256:
  `049b6e0d981d431871c166b639cee32c629067485394df789a754b87ede713f1`

The source test artifact is already materialized. This audit must not make new
LLM calls, inspect locked-test note text, or write locked-test row ids, text,
evidence snippets, gold labels, predictions, or failures.

## Frozen Candidate Policy

Base layer:

- `hybrid_adjudicator_raw` from the saved test artifact.

Candidate source priority:

1. LLM structured candidates with asserted current/recent seizure-frequency
   candidates.
2. Deterministic candidates from the saved component packet.
3. Keep the base label if no eligible structured projection candidate is found.

Eligible structured projection families are frozen from the validation port
panel:

- `cluster_frequency`
- `daily_frequency`
- `other_frequency`
- `seizure_free`
- `unknown_frequency`
- `weekly_frequency`

Family selection priority:

1. `cluster_frequency`: select a cluster label when the base label is not already
   a cluster label.
2. `daily_frequency`: select a per-day label when the base label is not already
   a per-day label.
3. `weekly_frequency`: select a per-week label when the base label is not already
   a per-week label.
4. `seizure_free`: select a seizure-free label when the base label is
   no-reference or unknown.
5. `unknown_frequency`: select `unknown` only when the base label is seizure-free
   or no-reference.
6. `other_frequency`: select a non-sentinel frequency label only when no higher
   priority family fired and the base label is no-reference or unknown.

This is intentionally a promotion of the structured projection-port mechanism,
not a new prompt, model, scorer, repair, or normalization policy.

## Allowed First Readout

The first locked-test readout may include only aggregate metrics:

- row count;
- base correct rows and base Purist proxy;
- final correct rows and final Purist proxy;
- changed rows;
- selected rows by family;
- selected rows by source;
- transition counts: `C_to_C`, `C_to_W`, `W_to_C`, `W_to_W`;
- changed-label precision;
- invalid candidate label count;
- aggregate decision.

The audit must not write a row-level JSONL.

## Stop Rules

Accept the audit as a valid frozen readout only if:

- the audit uses the frozen source artifact and split manifest above;
- no new LLM calls are made;
- no row-level locked-test output is written;
- no scorer, split, normalization, prompt, model, or candidate policy changes
  are needed to interpret the aggregate result.

Reject or mark revise-only if:

- `C_to_W` is nonzero at a material rate;
- changed-label precision is poor;
- aggregate proxy falls below the base layer;
- the candidate needs row-level test inspection to explain or repair the result.

Any future fix starts a new validation-cycle candidate and requires a separate
holdout protocol.
