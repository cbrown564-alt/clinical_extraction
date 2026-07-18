# ExECTv2 six-model Seizure Frequency over-inference protocol

Date: 2026-07-18  
Status: frozen before the no-call replay

## Question

Do the six fixed decision-0041 model conditions emit an active seizure rate
when the ExECTv2 gold state is unknown-only, and does the deterministic Seizure
Frequency projection and suppression step remove or introduce those errors?

This is the task-specific ExECT counterpart to the Gan unknown-versus-rate
question. It does not assume that the Gan label transform applies unchanged to
ExECT's multi-mention annotations.

## Data and inspection policy

- Dataset: ExECTv2.
- Split: manifest-defined `dev140`, 140 letters.
- Inspection: row-level analysis is permitted on `dev140` only.
- Excluded: `test60` row identifiers, text, predictions, evidence, errors, and
  changed rows. Existing `test60` aggregates may appear only in the separate
  six-model comparison report.
- Models: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, thinking-enabled DeepSeek V4
  Flash, Qwen 3.6:35B, and Gemma 4 26B.
- Call mode: replay committed decision-0041 outputs; no model calls.

## Fixed stages and repair policy

- Comparator: the named model's `predicted_mentions` in its structured
  event-ledger artifact, after schema and exact-evidence validation but before
  the Seizure Frequency projection and unsupported-state suppression path.
- Candidate: the final assembled `predicted_mentions` in the matching
  six-model decision-0041 artifact.
- Prompt: `exectv2_hybrid_key_family_event_ledger_v0.9.24`.
- Final repair policy: the selected joint bounded policy, including
  `exectv2_hybrid_sf_state_projection_v0.6` and
  `exectv2_hybrid_sf_unknown_suppression_v0.7` for Seizure Frequency.
- State transform: the existing change-aware
  `frequency_state_faithful` function. Per-letter state sets may contain
  `active-rate`, `seizure-free`, `changed`, or `unknown`.

## Metrics

The unit is one model-letter pair. Duplicate mentions with the same state are
collapsed within a letter.

Primary:

- **Unknown-only active-rate over-read:** among letters whose gold state set is
  exactly `{unknown}`, the proportion whose candidate state set contains
  `active-rate`.

Secondary:

1. the same primary measure at the comparator stage;
2. rate-absent active-rate emission, stratified into unknown-only,
   seizure-free-containing, changed-only, and empty-gold bands;
3. exact state-set agreement at comparator and candidate stages;
4. deterministic transitions: over-read rescued, over-read introduced,
   persistent over-read, wrong-to-correct, correct-to-wrong, and
   changed-still-wrong;
5. final exact-evidence coverage and call/parse/schema failure counts; and
6. results by model, with pooled counts descriptive only.

Empty-gold letters are diagnostic and never merged into the primary factuality
denominator. A missing ExECT annotation is not automatically proof that a
model's supported clinical fact is false.

## Artifact contract

The machine-readable artifact records:

- dataset, split, manifest, scorer/state transform, prompt, replay and repair
  policy;
- exact source artifact paths and model/runtime identities;
- one row per model and letter with gold, comparator, and candidate state sets,
  the primary-band flag, transition classification, evidence status, and first
  prediction-changing owner; and
- aggregate tables by model and gold band.

Expected outputs:

- `experiments/exectv2_six_model_sf_overinference_dev140_20260718.json`
- `docs/experiments/exectv2/reliability/exectv2_six_model_sf_overinference_2026-07-18.md`

## Stop rule and claim boundary

If the unknown-only denominator contains fewer than ten letters, retain the
primary result as diagnostic and do not make a prevalence or transfer claim.
Otherwise the study may report model-specific development rates and the effect
of the named deterministic stage.

The strongest possible positive conclusion is a bounded ExECT `dev140`
development finding that an analogous unknown-versus-rate failure occurs under
the fixed state transform. It is not Gan-to-ExECT transfer validation, test60
evidence, clinical validation, a deployment estimate, or proof that empty-gold
model predictions are false.
