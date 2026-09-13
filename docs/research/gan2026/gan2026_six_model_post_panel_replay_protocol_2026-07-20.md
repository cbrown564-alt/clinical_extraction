# Gan 2026 six-model post-panel replay and attribution protocol

Date: 2026-07-20  
Status: frozen before no-call replay

## Primary question

After all twelve Gan development conditions completed, can bounded structural
schema repair recover additional valid records without changing an already
selected clinical answer, and which component owns each matched method gain or
regression?

## Data and inspection

- Dataset: Gan 2026.
- Split: `dev750`; the manifest and retained artifacts use the legacy identifier
  `validation750`. Manifest: `gan2026_split_v1`.
- Row policy: development row-level inspection permitted.
- Inputs: the twelve frozen artifacts under
  `scratch/validation/gan2026_six_model_comparison_20260718/`.
- Model calls: none; cache/replay mode is saved raw-output replay.
- Scorers: frozen Gan Purist primary and Pragmatic secondary.
- Rules comparison: retained deterministic canonical dev750 artifact (legacy
  ID: `validation750`).

Gan `test450` is excluded. No locked row may enter the replay or analysis.

## Selected-answer-preserving repair

The replay may:

1. apply existing syntax-only JSON dialect repairs;
2. convert an `events` object whose values are event objects into the same
   ordered list of values;
3. turn null evidence into an empty string only when the model explicitly
   selected `no_reference`; and
4. quarantine a schema-invalid event only when its event ID is not selected
   and the selection plus every selected event validate independently.

It must not change selected event IDs, evidence, kind, final label, rationale,
count, denominator, time window, cluster meaning, assertion, or temporality.
A selected-path defect remains a failure. Each repair is recorded separately
as syntax, container shape, or quarantined unselected event. Clinical semantic
repairs remain a distinct downstream stage.

## Required outputs

The machine artifact records, by condition and permitted development row:

- source ID and artifact hash;
- original and replay parse state;
- selected-answer identity before and after replay;
- syntax, container, quarantine, and semantic events separately;
- Purist/Pragmatic correctness, exact evidence, and method transition;
- first failure owner and clinical subproblem;
- comparison with the fixed rules control; and
- deterministic-correct regressions.

The report summarizes score layers, matched rescues/regressions, evidence
validity, repair effects, first-failure ownership, subproblems, and named hard
families. Representative rows may be inspected because validation is a
development split.

## Stop and claim boundary

Stop if any replay changes an existing final label or selected clinical path,
if any input fails manifest identity, or if the rules comparator cannot be
aligned. A positive result is a development component answer for these six
routes, two prompts, frozen repair policy, and validation distribution. It is
not holdout evidence, clinical validation, universal model ranking, or proof
that deterministic repair is always beneficial.
