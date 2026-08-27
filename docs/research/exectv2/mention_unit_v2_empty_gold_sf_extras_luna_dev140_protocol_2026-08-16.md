# ExECT mention-unit v2 empty-gold SF extras — `dev140` protocol

Date: 2026-08-16  
Status: complete; **answer**  
Prior: [mention-unit v2 `dev140`](mention_unit_v2_fork_a_luna_dev140_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)

Fork A stays. Decision 0050 and `test60` are unchanged. This study
does not retune the prompt or the landed encoder. No new model calls.

## Primary question

On the 140 development letters, is the mention-unit v2 empty-gold
SeizureFrequency extras rise (53 versus v4 38 / trust-item 30) more
empty-gold letters, or more frequency statements on letters gold already
left empty?

`dev20` said extras cannot be prompted away. The `dev140` stop counted
mentions. This catalog asks what those mentions are.

## Data and row policy

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Split: `dev140`. Development rows may be inspected. `test60` is not
  authorized.
- Inputs: saved mention-unit v2 `dev140` rows and saved v4 `dev140`
  default projections. No rematerialization that changes those
  predictions. No new calls.

## Candidate and fixed comparators

- Candidate extras: mention-unit v2 `llm` SeizureFrequency mentions on
  letters with zero gold SF units.
- Fixed: default v4 `llm` extras on the same empty-gold letters.
- Trust-item mention counts stay the recorded comparator from the
  transfer study. This catalog does not rematerialize trust-item.

## Classes

Assign one primary class per extra. Overlay `same_evidence_copy` when
the same letter repeats the same normalized evidence.

| Class | Meaning |
| --- | --- |
| `frequency_statement` | Count, rate, last-event, change, or seizure-free duration in attributes or evidence |
| `remote_childhood` | Febrile or childhood-age count. Still a frequency statement; gold often leaves these empty |
| `seizure_story` | Seizure type or story with no frequency frame |
| `other` | None of the above |

An extra is still a scorer false positive. A supported unannotated
statement is not new gold.

## Scoring

Primary: letter count versus mention count versus v4; class counts;
v2-only versus v4-only letters.

Secondary: same-evidence copies; remote-childhood share. Headline F1
is not a decision metric.

## Minimal implementation change

Add a no-call catalog script that reads the saved rows. Do not change
gold, the selected stack, the v2 prompt, or the encoder.

## Required checks and stop rules

- `model_calls` must be 0.
- `answer` if one mechanism owns the mention-count rise: more
  frequency statements on shared empty-gold letters, or more
  empty-gold letters, or seizure-story over-read.
- `revise` if the extras do not partition into the classes above.
- Do not retune. Do not start mention-unit v3 or Fork B from this
  catalog. Do not inspect `test60`.

Stop with `answer`, `revise`, `reject`, or `blocked_by_instrumentation`.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_empty_gold_sf_extras_luna_dev140_20260816/`.

Write `extras_catalog.json`. One object per extra with letter ID,
clinical name, evidence, attributes, class, overlays, and whether
that letter also has a v4 extra.

## Claim boundary

A development catalog of why the predeclared extras stop fired. It is
not clinical validation, holdout evidence, or a Decision 0050 change.
