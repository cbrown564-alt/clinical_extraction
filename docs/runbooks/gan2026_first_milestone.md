# Gan 2026 First Milestone Runbook

Goal: reproduce the benchmark-facing substrate before optimizing model behavior.

## Checklist

1. Load `synthetic_data_subset_1500.json`.
2. Identify the note text, clinic date, gold label, and author-provided quality flags.
3. Port or wrap the author-provided label parsing and category mapping.
4. Add tests around representative labels, clusters, seizure-free labels, unknowns, and no-reference labels.
5. Produce a simple evaluation table for known labels and intentionally simple baselines.
6. Create the first notebook showing loading, gold-label distribution, evaluation, and failure slices.

## Rule

Do not claim benchmark progress until local scoring matches the author policy on controlled examples.

## LLM/DSPy Development Run Sizes

For prediction-bearing LLM/DSPy or hybrid pipeline experiments, use validation
prefixes rather than the full validation split by default:

1. Smoke test on 25 validation rows.
2. Meaningful test on 50 validation rows.
3. Move to 250 validation rows only after the 50-row run has no systemic
   output-contract failures and the larger slice will decide a concrete
   promote/revise/reject question.

Full 750-row validation runs should be rare and documented in the experiment
artifact.
