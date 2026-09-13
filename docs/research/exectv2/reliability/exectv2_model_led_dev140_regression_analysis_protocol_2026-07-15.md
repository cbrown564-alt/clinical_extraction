# ExECTv2 model-led dev140 deterministic-regression protocol

Date: 2026-07-15  
Status: predeclared before row-level analysis or implementation

## Question

Which deterministic post-model mechanisms change a model-correct ExECTv2
development answer into a wrong final answer under the decision-0040 family
architecture? For each mechanism, is the development evidence strong enough to
recommend retaining it, removing it, revising it in a separately predeclared
candidate, or rejecting a family-level policy change?

## Data and row policy

- Dataset: ExECTv2.
- Inspected split: the 140 letter identifiers in the repository's `dev140`
  split definition. The user explicitly permitted dev140 analysis on
  2026-07-15.
- Excluded split: test60. No test60 note, prediction, gold annotation, failure,
  or row-level difference may be inspected, quoted, classified, or retained.
- Full200 evidence remains aggregate-only. Saved full200 producer files may be
  rehydrated only to copy rows whose identifiers belong to dev140 into a
  temporary development-only artifact; all other rows must be discarded before
  assembly or scoring.
- Replay mode: saved historical model outputs only. No model calls, prompt
  changes, gold changes, scorer changes, or rule changes are authorized by this
  protocol.

## Candidates and comparator

The three historical saved-output conditions are GPT-4.1-mini, the historical
DeepSeek V4 Flash API run with incomplete runtime metadata, and Qwen 3.6 35B
repair v02.

For each model, letter, and family, compare:

1. the named model-owned family output before deterministic clinical changes;
2. the decision-0040 final family output after permitted attributable changes;
3. the unchanged ExECTv2 gold annotations.

The families and post-model mechanisms are:

- Diagnosis: dictionary normalization plus accepted heading, boundary, and
  residual recovery;
- Seizure Frequency: projection of model-selected operands and unsupported or
  contradictory-state suppression, without independent extractor union;
- Prescription: drug, dose, unit, and schedule normalization; supported regimen
  splitting; unsupported-fact removal; and bounded residual repair;
- Investigations: schema, evidence, normalization, and deduplication only.

## Measures

- Primary comparison: per-letter equality of de-duplicated
  `clinical_headline` keys for the named family.
- Required directions: unchanged, wrong to correct, correct to wrong, and
  changed while still wrong.
- Secondary Seizure Frequency view: `state_profile` where the retained row data
  support it.
- Evidence: exact selected evidence is required for a safety claim. Invalid or
  missing evidence remains diagnostic.
- Attribution: record the first prediction-changing deterministic mechanism
  that makes an incorrect result unrecoverable. If the retained trace cannot
  identify it, record `unresolved` rather than infer ownership.

The analysis must report changed-row counts and direction by model, family,
mechanism, evidence status, and clinically meaningful case tag. Aggregate F1
alone cannot answer the question.

## Machine-readable row record

Retain one record per dev140 model/family row whose clinical keys changed. Each
record must contain:

- dataset, split, letter identifier, model condition, family, and replay mode;
- model-owned, final, and gold clinical keys;
- model-owned and final correctness;
- change direction;
- selected evidence and evidence status;
- recorded deterministic actions and fact provenance;
- first prediction-changing owner or `unresolved`;
- clinical subproblem and case tags;
- source artifact revisions and scorer identifier.

The retained artifact must contain no note text, gold annotations, predictions,
or row identifiers from test60.

## Decision rule and stop rule

A mechanism may be recommended for retention only when the dev140 changed-row
record shows attributable benefit, no unexplained model-correct to final-wrong
cases, and valid selected evidence. A nonzero regression does not automatically
license removal: the analysis must compare benefits and harms and distinguish a
general family policy from a validation-shaped exception.

Stop after producing the machine-readable dev140 record, mechanism summary,
representative permitted development examples, and one of four recommendations
for each mechanism: retain, remove, revise in a new predeclared candidate, or do
not change. Any implementation or frozen rerun requires a separate candidate
protocol.

## Claim boundary

This study is development-only mechanism evidence. It cannot establish test60
or holdout performance, clinical validity, cross-model transfer, or safety on a
new distribution. The historical DeepSeek condition remains audit-only because
its runtime metadata is incomplete.
