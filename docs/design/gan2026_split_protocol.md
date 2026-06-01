# Gan 2026 Split Protocol

## Purpose

Gan 2026 development must not use the full 1,500-row synthetic dataset as a single
iteration surface. Candidate rules, prompts, DSPy modules, and reporting should be
developed against a validation split, with a locked test split reserved for final
evaluation.

The split manifest lives at:

```text
data/Gan (2026)/splits/gan2026_split_v1.json
```

Companion one-split manifests live in the same directory as `train_v1.json`,
`validation_v1.json`, and `test_v1.json`; these mirror the master manifest rows
for external scripts and manual inspection.

## Split Roles

### Train

- Count: 300 rows.
- Intended use: DSPy GEPA or another optimizer that needs training examples.
- Do not use it for manual prompt tuning, deterministic-rule tuning, exploratory
  error analysis, or reporting ordinary development results.
- If no optimizer is being trained, leave this split unused.

### Validation

- Count: 750 rows.
- Intended use: the primary development surface.
- Use this split for deterministic-rule iteration, prompt strategy comparisons,
  ablations, row-level error analysis, scorer-facing diagnostics, and model-choice
  decisions.
- Report ordinary progress as validation development results.
- Do not treat all 750 validation rows as the default LLM/DSPy iteration run.
  Hosted or local model experiments should escalate through validation prefixes:
  25 rows for smoke tests, 50 rows for meaningful signal, and 250 rows for a
  stronger development result after a decision gate is met.
- Full 750-row validation runs are rare. Use them only when a candidate, prompt,
  schema, model, and repair policy are stable enough that the result will change
  a project decision or become a durable comparison artifact.

## Validation Run Ladder

Use this ladder for ordinary LLM/DSPy and hybrid architecture iteration:

1. **Smoke test: 25 validation rows.** Run after prompt/schema/code changes to
   catch call failures, JSON/schema failures, evidence-validity problems, and
   obvious scorer-format drift. Do not promote from aggregate F1 alone.
2. **Meaningful signal: 50 validation rows.** Run when the smoke test has no
   blocking output-contract failures and the row-level failures are interpretable.
   Use this stage for prompt/schema comparisons and first model-swap checks.
3. **Decision gate before 250 rows.** Move to 250 only when the 50-row result has:
   no systemic call failures, no unresolved schema/parse failure family, exact
   evidence behavior adequate for row-level review, and a clear reason the larger
   slice will decide whether to promote, revise, or reject the candidate.
4. **Development result: 250 validation rows.** Treat this as the standard
   stronger validation signal for LLM/DSPy candidate comparisons.
5. **Rare full validation: 750 rows.** Run only with a written reason in the
   experiment artifact, such as freezing a development candidate before holdout
   evaluation, producing a paper-facing ablation/comparison table, or resolving a
   high-impact uncertainty that the 250-row slice cannot answer.

### Saturated Prefix Caveat

The 25- and 50-row prefixes are primarily contract and early-signal surfaces.
They are not strong enough to decide small metric deltas for candidates whose
deterministic comparator, prompt family, or hybrid architecture has already been
tuned close to saturation on those prefixes.

For a near-saturated candidate, a clean 50-row run should usually unlock a
250-row validation run rather than trigger small prompt, gate, or rule changes.
Treat one or two regressions on the 50-row prefix as a row-review note unless
they expose a systemic output-contract, evidence-validity, attribution, or
semantic-boundary failure. The written reason for 250-row escalation should name
the uncertainty the larger sample resolves, such as whether apparent
deterministic-correct regressions persist beyond a saturated prefix or whether
the LLM component produces enough corrections to justify its complexity.

### Test

- Count: 450 rows.
- Intended use: locked holdout final evaluation.
- Do not inspect test row-level failures while developing.
- Do not change prompts, rules, normalization, evidence selection, DSPy programs,
  model choice, thresholds, or repair logic based on test performance.
- Run it only after a candidate and its evaluation protocol are frozen.

## Manifest Policy

`gan2026_split_v1` is deterministic and stratified by:

- `gold_label_kind`
- `row_ok`

The manifest records the source dataset SHA-256, seed, row counts, intended split
uses, source row indices, and per-split stratum counts. Source rows remain in the
original JSON; manifests contain only row identifiers and metadata.

Do not regenerate or edit `gan2026_split_v1` to improve a result. If a future
protocol change is necessary, create a new manifest version and document why the
old split is insufficient.

## Reporting Language

- Train-only or train-plus-validation optimizer work is an optimizer development
  result.
- Validation work is a development result.
- Test work is a final holdout result only if the candidate was frozen before the
  test run and no tuning follows from the result.
- Do not call any local result a benchmark result until the data surface, split,
  scorer, and replication policy are explicitly benchmark-comparable.

## Allowed Workflow

1. Develop deterministic rules, prompt strategies, and ablations on validation,
   using the validation run ladder for LLM/DSPy and hybrid runs.
2. Use train only when running DSPy GEPA or another training/optimization procedure.
3. Freeze code, prompts, model identifiers, scorer, and split manifest version.
4. Run the locked test split once for final evaluation.
5. If test reveals a problem, record it as a final-evaluation finding. Any fix starts
   a new development cycle on validation and requires a later, clearly separated
   holdout evaluation.
