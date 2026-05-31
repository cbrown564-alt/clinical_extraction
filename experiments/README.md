# Experiments

Store run outputs, metrics, row-level predictions, and experiment notes here.

Prefer timestamped or named subdirectories. Keep enough metadata to reproduce the run.

Use `data/Gan (2026)/splits/gan2026_split_v1.json` for Gan 2026 work. Ordinary
development runs should report validation metrics. Train is reserved for DSPy GEPA
or another optimizer. Test is a locked final holdout and should not be used for
row-level debugging or tuning.

For LLM-backed runs, include the model role, display name, exact provider/API
identifier when available, hosted versus local execution details, prompt/program
version, deterministic-rule configuration, and whether the output came from a
direct program, repaired output, or optimizer-generated program. See
`docs/design/model_strategy.md`.
