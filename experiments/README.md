# Experiments

Store run outputs, metrics, row-level predictions, and experiment notes here.

Prefer timestamped or named subdirectories. Keep enough metadata to reproduce the run.

For LLM-backed runs, include the model role, display name, exact provider/API
identifier when available, hosted versus local execution details, prompt/program
version, deterministic-rule configuration, and whether the output came from a
direct program, repaired output, or optimizer-generated program. See
`docs/design/model_strategy.md`.
