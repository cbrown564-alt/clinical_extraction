# Experiments

Store run outputs, metrics, row-level predictions, and experiment notes here.

Prefer timestamped or named subdirectories. Keep enough metadata to reproduce the run.

Use `data/Gan (2026)/splits/gan2026_split_v1.json` for Gan 2026 work. Ordinary
development runs should report validation metrics. Train is reserved for DSPy GEPA
or another optimizer. Test is a locked final holdout and should not be used for
row-level debugging or tuning.

For LLM/DSPy and hybrid architecture work, do not default to all 750 validation
rows. Use the standard validation ladder:

1. 25 validation rows for smoke tests.
2. 50 validation rows for meaningful prompt/schema/model signal.
3. 250 validation rows only after the 50-row run passes a decision gate.

The decision gate for moving from 50 to 250 is: no systemic call failures, no
unresolved schema/parse failure family, evidence behavior good enough for
row-level review, and a written reason that the larger slice will decide whether
to promote, revise, or reject the candidate. Full 750-row validation runs should
be rare and must state why 250 rows are insufficient.

For LLM-backed runs, include the model role, display name, exact provider/API
identifier when available, hosted versus local execution details, prompt/program
version, deterministic-rule configuration, and whether the output came from a
direct program, repaired output, or optimizer-generated program. See
`docs/design/model_strategy.md`.
