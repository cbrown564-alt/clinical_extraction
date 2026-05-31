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

